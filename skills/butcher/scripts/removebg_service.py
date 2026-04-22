"""
RemoveBG Local Service
======================
A local remove.bg-like service with drag & drop UI.
Runs on localhost — no internet needed.

Methods:
  1. Smart flood-fill (best for solid/gradient backgrounds)
  2. GrabCut (OpenCV-style foreground extraction)
  3. Color-key (specific color removal)

Usage:
    python removebg_service.py [--port 5555]
    Then open http://localhost:5555
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import io
import base64
import json
import argparse
import numpy as np
from PIL import Image, ImageFilter
from collections import deque
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from scipy import ndimage
from scipy.ndimage import binary_fill_holes, binary_dilation, binary_erosion, gaussian_filter

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "removebg_output")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# PRO ENGINE — LAB Color Segmentation + Alpha Matting
# ============================================================

def rgb_to_lab(rgb_array):
    rgb = rgb_array.astype(np.float64) / 255.0
    mask = rgb > 0.04045
    rgb[mask] = ((rgb[mask] + 0.055) / 1.055) ** 2.4
    rgb[~mask] = rgb[~mask] / 12.92
    x = rgb[:,:,0]*0.4124564 + rgb[:,:,1]*0.3575761 + rgb[:,:,2]*0.1804375
    y = rgb[:,:,0]*0.2126729 + rgb[:,:,1]*0.7151522 + rgb[:,:,2]*0.0721750
    z = rgb[:,:,0]*0.0193339 + rgb[:,:,1]*0.1191920 + rgb[:,:,2]*0.9503041
    x /= 0.95047; y /= 1.00000; z /= 1.08883
    def f(t):
        m = t > 0.008856; r = np.zeros_like(t)
        r[m] = t[m]**(1/3); r[~m] = 7.787*t[~m]+16/116; return r
    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116*fy-16, 500*(fx-fy), 200*(fy-fz)], axis=-1)

def pro_remove_bg(img, tolerance=30, softness=1.5):
    """Professional BG removal using LAB segmentation + alpha matting."""
    rgb = np.array(img.convert('RGB'))
    h, w = rgb.shape[:2]
    lab = rgb_to_lab(rgb)

    # Sample BG from edges
    margin = max(10, min(h,w)//20)
    samples = np.concatenate([
        rgb[:margin,:,:].reshape(-1,3), rgb[-margin:,:,:].reshape(-1,3),
        rgb[:,:margin,:].reshape(-1,3), rgb[:,-margin:,:].reshape(-1,3)
    ], axis=0)
    samples_lab = rgb_to_lab(samples.reshape(1,-1,3)).reshape(-1,3)

    # Cluster BG into centers
    from scipy.cluster.vq import kmeans
    try:
        centers, _ = kmeans(samples_lab.astype(np.float64), min(4, max(2, len(samples_lab)//100)))
    except:
        centers = np.mean(samples_lab, axis=0, keepdims=True)

    # Min distance to any center
    flat = lab.reshape(-1,3)
    min_dist = np.full(flat.shape[0], np.inf)
    for c in centers:
        min_dist = np.minimum(min_dist, np.sqrt(np.sum((flat-c)**2, axis=1)))
    distance = min_dist.reshape(h,w)

    # Alpha matte
    lo, hi = tolerance*0.6, tolerance*1.4
    alpha = np.zeros_like(distance)
    alpha[distance > hi] = 1.0
    trans = (distance >= lo) & (distance <= hi)
    if np.any(trans):
        alpha[trans] = (distance[trans]-lo)/(hi-lo)

    # Morphological cleanup
    binary = alpha > 0.5
    binary = binary_fill_holes(binary)
    labeled, nf = ndimage.label(binary)
    if nf > 1:
        sizes = ndimage.sum(binary, labeled, range(1, nf+1))
        thresh = max(sizes) * 0.01
        for i in range(1, nf+1):
            if sizes[i-1] < thresh: binary[labeled==i] = False
    struct = ndimage.generate_binary_structure(2,1)
    cleaned = binary_dilation(binary_erosion(binary, struct, 1), struct, 1)
    alpha[~cleaned & (alpha < 0.7)] = 0.0

    # Edge refinement
    edge = (alpha > 0.05) & (alpha < 0.95)
    if np.any(edge):
        smoothed = gaussian_filter(alpha, sigma=softness)
        alpha[edge] = smoothed[edge]
    alpha = np.clip(alpha, 0, 1)

    rgba = np.dstack([rgb, (alpha*255).astype(np.uint8)])
    return Image.fromarray(rgba, 'RGBA')


# ============================================================
# BASIC ENGINES (fallback)
# ============================================================

def flood_fill_remove(img: Image.Image, tolerance: int = 25, feather: float = 1.0) -> Image.Image:
    """Smart flood-fill from all edges. Best for solid/gradient BGs."""
    img_rgba = img.convert('RGBA')
    data = np.array(img_rgba)
    h, w = data.shape[:2]
    rgb = data[:, :, :3].astype(np.float32)
    alpha = np.ones((h, w), dtype=np.uint8) * 255
    visited = np.zeros((h, w), dtype=bool)

    # Seed from edges (3px margin)
    seeds = set()
    for margin in range(3):
        for x in range(w):
            seeds.add((margin, x))
            seeds.add((h - 1 - margin, x))
        for y in range(h):
            seeds.add((y, margin))
            seeds.add((y, w - 1 - margin))

    queue = deque()
    for (sy, sx) in seeds:
        if 0 <= sy < h and 0 <= sx < w and not visited[sy, sx]:
            visited[sy, sx] = True
            alpha[sy, sx] = 0
            queue.append((sy, sx))

    tol_sq = tolerance * tolerance * 3

    while queue:
        cy, cx = queue.popleft()
        current_color = rgb[cy, cx]
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                diff = np.sum((current_color - rgb[ny, nx]) ** 2)
                if diff < tol_sq:
                    visited[ny, nx] = True
                    alpha[ny, nx] = 0
                    queue.append((ny, nx))

    if feather > 0:
        from PIL import ImageFilter
        alpha_img = Image.fromarray(alpha, 'L')
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(radius=feather))
        alpha_arr = np.array(alpha_img, dtype=np.float32)
        alpha_arr = np.clip((alpha_arr - 20) * (255 / 235), 0, 255)
        alpha = alpha_arr.astype(np.uint8)

    data[:, :, 3] = alpha
    return Image.fromarray(data, 'RGBA')


def color_key_remove(img: Image.Image, hex_color: str = "#FFFFFF", tolerance: int = 30) -> Image.Image:
    """Remove specific color (like chroma key)."""
    img_rgba = img.convert('RGBA')
    data = np.array(img_rgba, dtype=np.float32)

    hc = hex_color.lstrip('#')
    tr, tg, tb = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)

    dist = np.sqrt(
        (data[:,:,0] - tr)**2 + (data[:,:,1] - tg)**2 + (data[:,:,2] - tb)**2
    )

    alpha = np.ones(data.shape[:2], dtype=np.float32) * 255
    inner = tolerance * 0.7
    outer = tolerance * 1.4
    alpha[dist < inner] = 0
    mask = (dist >= inner) & (dist < outer)
    if np.any(mask):
        alpha[mask] = ((dist[mask] - inner) / (outer - inner)) * 255

    alpha_img = Image.fromarray(alpha.astype(np.uint8), 'L')
    alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(radius=0.8))
    data[:,:,3] = np.array(alpha_img, dtype=np.float32)

    return Image.fromarray(data.astype(np.uint8), 'RGBA')


def auto_trim(img: Image.Image, padding: int = 4) -> Image.Image:
    """Trim transparent borders."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    alpha = np.array(img)[:,:,3]
    rows = np.any(alpha > 20, axis=1)
    cols = np.any(alpha > 20, axis=0)
    if not np.any(rows) or not np.any(cols):
        return img
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin = max(0, rmin - padding)
    rmax = min(img.height - 1, rmax + padding)
    cmin = max(0, cmin - padding)
    cmax = min(img.width - 1, cmax + padding)
    return img.crop((cmin, rmin, cmax + 1, rmax + 1))


# ============================================================
# WEB UI
# ============================================================

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<title>RemoveBG Local</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', IRANSansX, Tahoma, sans-serif;
    background: #0f0f13;
    color: #e0e0e0;
    min-height: 100vh;
    direction: rtl;
  }

  .header {
    text-align: center;
    padding: 30px 20px 10px;
  }
  .header h1 {
    font-size: 28px;
    background: linear-gradient(135deg, #ff6b6b, #ffa500, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
  }
  .header p { color: #888; font-size: 14px; }

  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px;
  }

  /* Controls Bar */
  .controls {
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    margin: 16px 0;
    padding: 16px;
    background: #1a1a24;
    border-radius: 12px;
    border: 1px solid #2a2a3a;
  }
  .control-group { display: flex; align-items: center; gap: 8px; }
  .control-group label { font-size: 13px; color: #aaa; white-space: nowrap; }
  .control-group select, .control-group input[type="range"], .control-group input[type="text"] {
    background: #252535; border: 1px solid #3a3a4a; color: #e0e0e0;
    padding: 6px 10px; border-radius: 6px; font-size: 13px;
  }
  .control-group input[type="range"] { width: 100px; }
  .control-group input[type="text"] { width: 80px; text-align: center; direction: ltr; }

  /* Drop Zone */
  .dropzone {
    border: 2px dashed #3a3a5a;
    border-radius: 16px;
    padding: 50px;
    text-align: center;
    transition: all 0.3s;
    cursor: pointer;
    background: #14141e;
    margin-bottom: 20px;
  }
  .dropzone:hover, .dropzone.dragover {
    border-color: #ff6b6b;
    background: #1a1a28;
  }
  .dropzone .icon { font-size: 48px; margin-bottom: 12px; }
  .dropzone p { color: #888; }
  .dropzone input { display: none; }

  /* Results Grid */
  .results {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .result-card {
    background: #1a1a24;
    border-radius: 12px;
    border: 1px solid #2a2a3a;
    overflow: hidden;
  }
  .result-card .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #2a2a3a;
    background: #15151f;
  }
  .result-card .card-header h3 { font-size: 14px; color: #ccc; }
  .result-card .card-header .size { font-size: 12px; color: #666; direction: ltr; }

  .image-container {
    padding: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
  }
  .image-container.checker {
    background-image:
      linear-gradient(45deg, #1e1e2e 25%, transparent 25%),
      linear-gradient(-45deg, #1e1e2e 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #1e1e2e 75%),
      linear-gradient(-45deg, transparent 75%, #1e1e2e 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    background-color: #2a2a3a;
  }
  .image-container img { max-width: 100%; max-height: 350px; object-fit: contain; }

  .download-btn {
    display: block;
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #ff6b6b, #ff8e53);
    color: white;
    border: none;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    transition: opacity 0.2s;
    font-family: inherit;
  }
  .download-btn:hover { opacity: 0.85; }

  /* Batch Mode */
  .batch-results { margin-top: 20px; }
  .batch-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; background: #1a1a24; border-radius: 8px;
    margin-bottom: 8px; border: 1px solid #2a2a3a;
  }
  .batch-item img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
  .batch-item .info { flex: 1; }
  .batch-item .info .name { font-size: 13px; }
  .batch-item .info .meta { font-size: 11px; color: #666; direction: ltr; }
  .batch-item a {
    background: #ff6b6b; color: white; padding: 6px 16px;
    border-radius: 6px; text-decoration: none; font-size: 12px;
  }

  .loading { text-align: center; padding: 40px; color: #888; }
  .loading .spinner {
    width: 40px; height: 40px; border: 3px solid #333;
    border-top-color: #ff6b6b; border-radius: 50%;
    animation: spin 0.8s linear infinite; margin: 0 auto 12px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 700px) {
    .results { grid-template-columns: 1fr; }
    .controls { flex-direction: column; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>RemoveBG Local</h1>
  <p>drag & drop — background removal — no internet needed</p>
</div>

<div class="container">

  <div class="controls">
    <div class="control-group">
      <label>Method:</label>
      <select id="method">
        <option value="pro" selected>Pro (LAB + Alpha Matte)</option>
        <option value="flood">Flood Fill (Fast)</option>
        <option value="colorkey_white">Color Key (White)</option>
        <option value="colorkey_custom">Color Key (Custom)</option>
      </select>
    </div>
    <div class="control-group">
      <label>Tolerance:</label>
      <input type="range" id="tolerance" min="5" max="60" value="25">
      <span id="tol-val">25</span>
    </div>
    <div class="control-group" id="color-group" style="display:none">
      <label>Color:</label>
      <input type="text" id="hex-color" value="#FFFFFF" placeholder="#FFFFFF">
    </div>
    <div class="control-group">
      <label>Auto-Trim:</label>
      <select id="auto-trim">
        <option value="yes" selected>Yes</option>
        <option value="no">No</option>
      </select>
    </div>
  </div>

  <div class="dropzone" id="dropzone">
    <div class="icon">&#128248;</div>
    <p>Drag & Drop images here or click to browse</p>
    <p style="font-size:12px; margin-top:8px; color:#555">PNG, JPG, WEBP — single or batch</p>
    <input type="file" id="file-input" accept="image/*" multiple>
  </div>

  <div id="single-result" class="results" style="display:none">
    <div class="result-card">
      <div class="card-header">
        <h3>Original <span id="picker-status" style="font-size:11px;color:#ff6b6b;"></span></h3>
        <span class="size" id="orig-size"></span>
      </div>
      <div class="image-container" style="position:relative;">
        <canvas id="orig-canvas" style="max-width:100%;max-height:350px;cursor:crosshair;"></canvas>
        <div id="color-tooltip" style="display:none;position:absolute;background:#1a1a24;border:1px solid #3a3a4a;border-radius:8px;padding:8px 12px;pointer-events:none;z-index:10;font-size:12px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <div id="tt-swatch" style="width:24px;height:24px;border-radius:4px;border:1px solid #555;"></div>
            <span id="tt-hex" style="direction:ltr;font-family:monospace;"></span>
          </div>
        </div>
      </div>
      <div id="picked-colors-bar" style="display:none;padding:8px 16px;border-top:1px solid #2a2a3a;background:#15151f;">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span style="font-size:12px;color:#888;">Picked:</span>
          <div id="picked-colors" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
          <button onclick="reprocessWithPicked()" style="background:#ff6b6b;color:#fff;border:none;padding:4px 14px;border-radius:6px;font-size:12px;cursor:pointer;margin-right:auto;">Re-process</button>
          <button onclick="clearPicked()" style="background:#333;color:#aaa;border:1px solid #444;padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer;">Clear</button>
        </div>
      </div>
    </div>
    <div class="result-card">
      <div class="card-header">
        <h3>Background Removed</h3>
        <span class="size" id="result-size"></span>
      </div>
      <div class="image-container checker">
        <img id="result-img">
      </div>
      <button class="download-btn" id="download-btn">Download PNG</button>
    </div>
  </div>

  <div id="batch-result" class="batch-results" style="display:none">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <h3 style="color:#ccc;"></h3>
      <button onclick="downloadAll()" class="download-btn" style="width:auto; border-radius:8px; padding:8px 24px;">Download All</button>
    </div>
    <div id="batch-list"></div>
  </div>

  <div id="loading" class="loading" style="display:none">
    <div class="spinner"></div>
    <p>Processing...</p>
  </div>

</div>

<script>
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const tolRange = document.getElementById('tolerance');
const tolVal = document.getElementById('tol-val');
const methodSel = document.getElementById('method');
const colorGroup = document.getElementById('color-group');
const origCanvas = document.getElementById('orig-canvas');
const origCtx = origCanvas.getContext('2d', {willReadFrequently: true});
const tooltip = document.getElementById('color-tooltip');
const ttSwatch = document.getElementById('tt-swatch');
const ttHex = document.getElementById('tt-hex');
const pickerStatus = document.getElementById('picker-status');

let currentFile = null;
let pickedColors = [];
let resultBlobs = [];
let origImage = null;

tolRange.oninput = () => tolVal.textContent = tolRange.value;
methodSel.onchange = () => {
  colorGroup.style.display = methodSel.value === 'colorkey_custom' ? 'flex' : 'none';
};

dropzone.onclick = () => fileInput.click();
dropzone.ondragover = e => { e.preventDefault(); dropzone.classList.add('dragover'); };
dropzone.ondragleave = () => dropzone.classList.remove('dragover');
dropzone.ondrop = e => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  handleFiles(e.dataTransfer.files);
};
fileInput.onchange = () => handleFiles(fileInput.files);

// ===== COLOR PICKER ON CANVAS =====
origCanvas.addEventListener('mousemove', (e) => {
  if (!origImage) return;
  const rect = origCanvas.getBoundingClientRect();
  const scaleX = origCanvas.width / rect.width;
  const scaleY = origCanvas.height / rect.height;
  const x = Math.floor((e.clientX - rect.left) * scaleX);
  const y = Math.floor((e.clientY - rect.top) * scaleY);

  if (x < 0 || y < 0 || x >= origCanvas.width || y >= origCanvas.height) {
    tooltip.style.display = 'none';
    return;
  }

  const pixel = origCtx.getImageData(x, y, 1, 1).data;
  const hex = '#' + [pixel[0], pixel[1], pixel[2]].map(c => c.toString(16).padStart(2, '0')).join('');

  ttSwatch.style.background = hex;
  ttHex.textContent = hex.toUpperCase();
  tooltip.style.display = 'block';
  tooltip.style.left = (e.clientX - origCanvas.closest('.image-container').getBoundingClientRect().left + 15) + 'px';
  tooltip.style.top = (e.clientY - origCanvas.closest('.image-container').getBoundingClientRect().top - 10) + 'px';

  pickerStatus.textContent = 'Click to pick color';
});

origCanvas.addEventListener('mouseleave', () => {
  tooltip.style.display = 'none';
  pickerStatus.textContent = '';
});

origCanvas.addEventListener('click', (e) => {
  if (!origImage) return;
  const rect = origCanvas.getBoundingClientRect();
  const scaleX = origCanvas.width / rect.width;
  const scaleY = origCanvas.height / rect.height;
  const x = Math.floor((e.clientX - rect.left) * scaleX);
  const y = Math.floor((e.clientY - rect.top) * scaleY);

  const pixel = origCtx.getImageData(x, y, 1, 1).data;
  const hex = '#' + [pixel[0], pixel[1], pixel[2]].map(c => c.toString(16).padStart(2, '0')).join('');

  // Add to picked colors (avoid duplicates)
  if (!pickedColors.includes(hex)) {
    pickedColors.push(hex);
    renderPickedColors();
  }

  // Auto-update hex input
  document.getElementById('hex-color').value = hex;

  // Auto-switch to colorkey_custom
  methodSel.value = 'colorkey_custom';
  colorGroup.style.display = 'flex';
});

function renderPickedColors() {
  const container = document.getElementById('picked-colors');
  const bar = document.getElementById('picked-colors-bar');
  container.innerHTML = '';

  if (pickedColors.length === 0) {
    bar.style.display = 'none';
    return;
  }
  bar.style.display = 'block';

  pickedColors.forEach((hex, i) => {
    const chip = document.createElement('div');
    chip.style.cssText = 'display:flex;align-items:center;gap:4px;background:#252535;padding:3px 8px;border-radius:6px;cursor:pointer;border:1px solid #3a3a4a;';
    chip.innerHTML = `
      <div style="width:16px;height:16px;border-radius:3px;background:${hex};border:1px solid #555;"></div>
      <span style="font-size:11px;font-family:monospace;color:#ccc;direction:ltr;">${hex}</span>
      <span onclick="event.stopPropagation();removePicked(${i})" style="color:#666;font-size:14px;margin-right:-2px;cursor:pointer;">&times;</span>
    `;
    chip.onclick = () => {
      document.getElementById('hex-color').value = hex;
    };
    container.appendChild(chip);
  });
}

function removePicked(i) {
  pickedColors.splice(i, 1);
  renderPickedColors();
}

function clearPicked() {
  pickedColors = [];
  renderPickedColors();
}

async function reprocessWithPicked() {
  if (!currentFile || pickedColors.length === 0) return;

  document.getElementById('loading').style.display = 'block';

  const formData = new FormData();
  formData.append('image', currentFile);
  formData.append('method', 'colorkey_multi');
  formData.append('tolerance', tolRange.value);
  formData.append('hex_colors', JSON.stringify(pickedColors));
  formData.append('auto_trim', document.getElementById('auto-trim').value);

  const resp = await fetch('/remove', { method: 'POST', body: formData });
  const data = await resp.json();

  document.getElementById('result-img').src = 'data:image/png;base64,' + data.result;
  document.getElementById('result-size').textContent = data.result_size;
  resultBlobs = [{name: data.filename, b64: data.result}];
  document.getElementById('download-btn').onclick = () => downloadB64(data.result, data.filename);

  document.getElementById('loading').style.display = 'none';
}

// ===== MAIN HANDLERS =====

async function handleFiles(files) {
  if (!files.length) return;

  document.getElementById('loading').style.display = 'block';
  document.getElementById('single-result').style.display = 'none';
  document.getElementById('batch-result').style.display = 'none';
  resultBlobs = [];
  pickedColors = [];
  renderPickedColors();

  if (files.length === 1) {
    currentFile = files[0];
    await processSingle(files[0]);
  } else {
    await processBatch(files);
  }
  document.getElementById('loading').style.display = 'none';
}

async function processSingle(file) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('method', getMethod());
  formData.append('tolerance', tolRange.value);
  formData.append('hex_color', document.getElementById('hex-color').value);
  formData.append('auto_trim', document.getElementById('auto-trim').value);

  const resp = await fetch('/remove', { method: 'POST', body: formData });
  const data = await resp.json();

  // Load original into canvas for color picking
  const img = new Image();
  img.onload = () => {
    origImage = img;
    // Scale canvas to fit but maintain aspect ratio
    const maxW = 500, maxH = 350;
    let w = img.width, h = img.height;
    if (w > maxW) { h = h * maxW / w; w = maxW; }
    if (h > maxH) { w = w * maxH / h; h = maxH; }
    origCanvas.width = img.width;  // Full res for accurate picking
    origCanvas.height = img.height;
    origCanvas.style.width = w + 'px';
    origCanvas.style.height = h + 'px';
    origCtx.drawImage(img, 0, 0);
  };
  img.src = 'data:image/png;base64,' + data.original;

  document.getElementById('result-img').src = 'data:image/png;base64,' + data.result;
  document.getElementById('orig-size').textContent = data.orig_size;
  document.getElementById('result-size').textContent = data.result_size;
  document.getElementById('single-result').style.display = 'grid';

  resultBlobs = [{name: data.filename, b64: data.result}];
  document.getElementById('download-btn').onclick = () => downloadB64(data.result, data.filename);
}

async function processBatch(files) {
  const list = document.getElementById('batch-list');
  list.innerHTML = '';
  resultBlobs = [];

  for (const file of files) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('method', getMethod());
    formData.append('tolerance', tolRange.value);
    formData.append('hex_color', document.getElementById('hex-color').value);
    formData.append('auto_trim', document.getElementById('auto-trim').value);

    const resp = await fetch('/remove', { method: 'POST', body: formData });
    const data = await resp.json();
    resultBlobs.push({name: data.filename, b64: data.result});

    list.innerHTML += `
      <div class="batch-item">
        <img src="data:image/png;base64,${data.result}" style="background:repeating-conic-gradient(#2a2a3a 0% 25%, #1e1e2e 0% 50%) 50% / 12px 12px;">
        <div class="info">
          <div class="name">${data.filename}</div>
          <div class="meta">${data.result_size}</div>
        </div>
        <a href="#" onclick="downloadB64('${data.result}','${data.filename}');return false;">Download</a>
      </div>`;
  }
  document.getElementById('batch-result').style.display = 'block';
}

function getMethod() {
  const v = methodSel.value;
  if (v === 'pro') return 'pro';
  if (v === 'colorkey_white') return 'colorkey';
  if (v === 'colorkey_custom') return 'colorkey';
  return 'flood';
}

function downloadB64(b64, filename) {
  const a = document.createElement('a');
  a.href = 'data:image/png;base64,' + b64;
  a.download = filename.replace(/\.[^.]+$/, '') + '_nobg.png';
  a.click();
}

async function downloadAll() {
  for (const r of resultBlobs) {
    downloadB64(r.b64, r.name);
    await new Promise(ok => setTimeout(ok, 300));
  }
}
</script>
</body>
</html>"""


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/')
def index():
    return HTML_PAGE


@app.route('/remove', methods=['POST'])
def remove_bg():
    file = request.files.get('image')
    if not file:
        return jsonify({"error": "No image"}), 400

    method = request.form.get('method', 'flood')
    tolerance = int(request.form.get('tolerance', 25))
    hex_color = request.form.get('hex_color', '#FFFFFF')
    do_trim = request.form.get('auto_trim', 'yes') == 'yes'

    # Load image
    img = Image.open(file.stream).convert('RGB')
    orig_size = f"{img.width}x{img.height}"

    # Process
    if method == 'pro':
        result = pro_remove_bg(img, tolerance=tolerance, softness=1.5)
    elif method == 'flood':
        result = flood_fill_remove(img, tolerance=tolerance, feather=1.0)
    elif method == 'colorkey':
        result = color_key_remove(img, hex_color=hex_color, tolerance=tolerance)
    elif method == 'colorkey_multi':
        # Multi-color removal — picked from color picker
        hex_colors_str = request.form.get('hex_colors', '[]')
        try:
            hex_colors = json.loads(hex_colors_str)
        except:
            hex_colors = [hex_color]
        # Apply color-key for each picked color
        result = img.convert('RGBA')
        data_arr = np.array(result, dtype=np.float32)
        alpha = np.ones(data_arr.shape[:2], dtype=np.float32) * 255
        for hc in hex_colors:
            hc = hc.lstrip('#')
            if len(hc) != 6:
                continue
            tr, tg, tb = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
            dist = np.sqrt(
                (data_arr[:,:,0]-tr)**2 + (data_arr[:,:,1]-tg)**2 + (data_arr[:,:,2]-tb)**2
            )
            inner = tolerance * 0.7
            outer = tolerance * 1.4
            alpha[dist < inner] = 0
            mask = (dist >= inner) & (dist < outer)
            if np.any(mask):
                partial = ((dist[mask]-inner)/(outer-inner))*255
                alpha[mask] = np.minimum(alpha[mask], partial)
        alpha_img = Image.fromarray(alpha.astype(np.uint8), 'L')
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(radius=0.8))
        data_arr[:,:,3] = np.array(alpha_img, dtype=np.float32)
        result = Image.fromarray(data_arr.astype(np.uint8), 'RGBA')
    else:
        result = pro_remove_bg(img, tolerance=tolerance, softness=1.5)

    # Trim
    if do_trim:
        result = auto_trim(result, padding=4)

    result_size = f"{result.width}x{result.height}"

    # Encode original
    buf_orig = io.BytesIO()
    img.save(buf_orig, 'PNG')
    orig_b64 = base64.b64encode(buf_orig.getvalue()).decode()

    # Encode result
    buf_result = io.BytesIO()
    result.save(buf_result, 'PNG', optimize=True)
    result_b64 = base64.b64encode(buf_result.getvalue()).decode()

    # Also save to disk
    safe_name = file.filename or 'image.png'
    save_path = os.path.join(UPLOAD_DIR, safe_name.rsplit('.', 1)[0] + '_nobg.png')
    result.save(save_path, 'PNG', optimize=True)

    return jsonify({
        "original": orig_b64,
        "result": result_b64,
        "orig_size": orig_size,
        "result_size": result_size,
        "filename": safe_name,
        "saved_to": save_path
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RemoveBG Local Service')
    parser.add_argument('--port', type=int, default=5555)
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  RemoveBG Local Service")
    print(f"  http://localhost:{args.port}")
    print(f"  Output dir: {UPLOAD_DIR}")
    print(f"{'='*50}\n")

    import webbrowser
    webbrowser.open(f"http://localhost:{args.port}")

    app.run(host='0.0.0.0', port=args.port, debug=False)
