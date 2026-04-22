"""
Butcher Smart Extractor v3
==========================
Crops assets from original banner + intelligent background removal.
Uses flood-fill from edges (like Photoshop Magic Wand) instead of
global color-key — preserves green text inside cards.

Pipeline:
1. Crop with generous bbox from original banner
2. Flood-fill transparency from edges (only removes connected bg pixels)
3. Auto-trim to content bounds
4. Save as transparent PNG
"""

import json
import sys
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path
from collections import deque

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def crop_asset(source_img: Image.Image, bbox: dict) -> Image.Image:
    src_w, src_h = source_img.size
    if 'x_pct' in bbox:
        x = int(bbox['x_pct'] / 100 * src_w)
        y = int(bbox['y_pct'] / 100 * src_h)
        w = int(bbox['w_pct'] / 100 * src_w)
        h = int(bbox['h_pct'] / 100 * src_h)
    else:
        x, y = bbox.get('x', 0), bbox.get('y', 0)
        w, h = bbox.get('w', src_w), bbox.get('h', src_h)
    x, y = max(0, x), max(0, y)
    w = min(w, src_w - x)
    h = min(h, src_h - y)
    return source_img.crop((x, y, x + w, y + h))


def flood_fill_remove_bg(img: Image.Image, tolerance: int = 30,
                          edge_margin: int = 3, feather: float = 1.0) -> Image.Image:
    """
    Smart background removal using flood-fill from edges.
    Like Photoshop's Magic Wand starting from all edges.
    Only removes pixels CONNECTED to the border — preserves interior colors.
    """
    img_rgba = img.convert('RGBA')
    data = np.array(img_rgba)
    h, w = data.shape[:2]
    rgb = data[:, :, :3].astype(np.float32)

    # Alpha mask: 255 = keep, 0 = remove
    alpha = np.ones((h, w), dtype=np.uint8) * 255
    visited = np.zeros((h, w), dtype=bool)

    # Collect seed pixels from all edges
    seeds = set()
    for margin in range(edge_margin):
        for x in range(w):
            seeds.add((margin, x))           # top
            seeds.add((h - 1 - margin, x))   # bottom
        for y in range(h):
            seeds.add((y, margin))            # left
            seeds.add((y, w - 1 - margin))   # right

    # BFS flood fill from edges
    queue = deque()
    for (sy, sx) in seeds:
        if not visited[sy, sx]:
            visited[sy, sx] = True
            alpha[sy, sx] = 0
            queue.append((sy, sx))

    tol_sq = tolerance * tolerance * 3  # tolerance in 3D color space

    while queue:
        cy, cx = queue.popleft()
        current_color = rgb[cy, cx]

        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                neighbor_color = rgb[ny, nx]
                diff = np.sum((current_color - neighbor_color) ** 2)

                if diff < tol_sq:
                    visited[ny, nx] = True
                    alpha[ny, nx] = 0
                    queue.append((ny, nx))

    # Feather edges for anti-aliasing
    if feather > 0:
        alpha_img = Image.fromarray(alpha, 'L')
        # Dilate slightly then blur for smooth edges
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(radius=feather))
        # Re-threshold to keep crisp but smooth
        alpha_arr = np.array(alpha_img, dtype=np.float32)
        # Remap: 0-127 -> 0, 128-255 -> scale up
        alpha_arr = np.clip((alpha_arr - 30) * (255 / 225), 0, 255)
        alpha = alpha_arr.astype(np.uint8)

    data[:, :, 3] = alpha
    return Image.fromarray(data, 'RGBA')


def auto_trim(img: Image.Image, padding: int = 4) -> Image.Image:
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    alpha = np.array(img)[:, :, 3]
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


def extract_assets(manifest_path: str, source_path: str, output_dir: str):
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    source_img = Image.open(source_path).convert('RGB')
    os.makedirs(output_dir, exist_ok=True)

    assets = manifest.get("assets", [])
    print(f"\n{'='*50}")
    print(f"  BUTCHER v3 - Smart Extract: {len(assets)} assets")
    print(f"  Source: {source_path} ({source_img.size[0]}x{source_img.size[1]})")
    print(f"{'='*50}\n")

    for asset in assets:
        name = asset.get("name", "unnamed")
        bbox = asset.get("bbox", {})
        method = asset.get("bg_removal", "flood")  # flood, ai, none
        tolerance = asset.get("tolerance", 30)
        trim = asset.get("auto_trim", True)
        padding = asset.get("trim_padding", 4)
        feather = asset.get("edge_feather", 1.0)
        scale = asset.get("scale", 1.0)

        print(f"  [CUT] {name}...", end=" ")

        # Step 1: Crop
        cropped = crop_asset(source_img, bbox) if bbox else source_img.copy()

        # Step 2: Remove background
        if method == "flood":
            result = flood_fill_remove_bg(cropped, tolerance, feather=feather)
        elif method == "ai":
            try:
                from rembg import remove
                result = remove(cropped.convert('RGBA'))
            except ImportError:
                print("(rembg unavailable, using flood)...", end=" ")
                result = flood_fill_remove_bg(cropped, tolerance, feather=feather)
        elif method == "none":
            result = cropped.convert('RGBA')
        else:
            result = cropped.convert('RGBA')

        # Step 3: Auto-trim
        if trim:
            result = auto_trim(result, padding)

        # Step 4: Scale
        if scale != 1.0:
            new_w = int(result.width * scale)
            new_h = int(result.height * scale)
            result = result.resize((new_w, new_h), Image.LANCZOS)

        # Step 5: Save
        output_path = os.path.join(output_dir, f"{name}.png")
        result.save(output_path, "PNG", optimize=True)
        print(f"OK -> {name}.png ({result.width}x{result.height})")

    print(f"\n{'='*50}")
    print(f"  DONE! {len(assets)} assets -> {output_dir}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python butcher_smart_extract.py <manifest.json> <source_image> <output_dir>")
        sys.exit(1)
    extract_assets(sys.argv[1], sys.argv[2], sys.argv[3])
