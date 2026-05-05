"""
Butcher Auto — Full Automated Asset Extraction
================================================
Send image → get folder of clean transparent PNGs.

Claude analyzes the image, writes a manifest JSON, then runs this script.
No manual steps needed.

Usage:
    python butcher_auto.py manifest.json

Manifest format:
{
  "source": "path/to/banner.png",
  "output_dir": "butcher_output",   // optional
  "banner_width": 628,              // optional, for text_render sizing
  "banner_height": 314,
  "assets": [
    {
      "name": "background_plate",
      "method": "direct_crop",
      "bbox": {"x_pct": 0, "y_pct": 0, "w_pct": 100, "h_pct": 100}
    },
    {
      "name": "key_visual",
      "method": "removebg",
      "bbox": {"x_pct": 0, "y_pct": 0, "w_pct": 44, "h_pct": 100},
      "tolerance": 35,
      "softness": 1.2
    },
    {
      "name": "copy_headline",
      "method": "text_render",
      "type": "text",
      "text": "۱۰۰ گرم طلا ببر",
      "font_family": "Vazirmatn",
      "font_weight": "ExtraBold",
      "font_size": 52,
      "color": "#FFFFFF",
      "direction": "rtl",
      "width": 280,
      "height": 130
    },
    {
      "name": "cta_button",
      "method": "text_render",
      "type": "cta",
      "text": "شروع کن",
      "bg_color": "#F5C518",
      "text_color": "#1A1F6E",
      "font_family": "Vazirmatn",
      "font_weight": "Bold",
      "font_size": 18,
      "width": 120,
      "height": 44,
      "border_radius": 8
    }
  ]
}

Methods:
  direct_crop   — crop region from source, save as-is (for background plates)
  removebg      — crop region + LAB-based background removal + auto-trim
  text_render   — render text/button via butcher_render.py (Playwright)
  transparentor — for visual assets (KV, logo, product):
                  saves a ready-to-paste AI prompt → paste into Transparentor
                  → AI generates asset on contrast bg → Color Key removes bg
                  → clean transparent PNG. Best quality for complex visuals.
                  Required fields: "prompt" (AI generation prompt), "contrast_bg" (hex color)
"""

import json
import sys
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCRIPTS_DIR = Path(__file__).parent


# ── helpers ──────────────────────────────────────────────────────────────────

def resolve_bbox(bbox: dict, src_w: int, src_h: int) -> tuple[int, int, int, int]:
    """Convert bbox (percent or absolute) → (x, y, x2, y2) pixel coords."""
    if 'x_pct' in bbox:
        x  = int(bbox['x_pct']  / 100 * src_w)
        y  = int(bbox['y_pct']  / 100 * src_h)
        w  = int(bbox['w_pct']  / 100 * src_w)
        h  = int(bbox['h_pct']  / 100 * src_h)
    else:
        x, y = bbox.get('x', 0), bbox.get('y', 0)
        w, h = bbox.get('w', src_w), bbox.get('h', src_h)
    x  = max(0, min(x, src_w - 1))
    y  = max(0, min(y, src_h - 1))
    w  = max(1, min(w, src_w - x))
    h  = max(1, min(h, src_h - y))
    return x, y, x + w, y + h


def tight_crop(img: Image.Image, padding: int = 0) -> Image.Image:
    """Trim transparent borders. Returns original if no transparent channel."""
    if img.mode != 'RGBA':
        return img
    bbox = img.getbbox()
    if bbox is None:
        return img
    if padding > 0:
        w, h = img.size
        bbox = (
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(w, bbox[2] + padding),
            min(h, bbox[3] + padding),
        )
    return img.crop(bbox)


# ── method handlers ───────────────────────────────────────────────────────────

def apply_source_alpha(img_rgba: Image.Image, src_alpha: Image.Image,
                        bbox: tuple) -> Image.Image:
    """Mask out pixels that were transparent in source (e.g. rounded corners)."""
    if src_alpha is None:
        return img_rgba
    region_alpha = src_alpha.crop(bbox)
    arr = np.array(img_rgba)
    sa  = np.array(region_alpha)
    # Pixels transparent in source stay transparent regardless of removebg result
    arr[:, :, 3] = np.minimum(arr[:, :, 3], sa)
    return Image.fromarray(arr, 'RGBA')


def handle_direct_crop(asset: dict, src: Image.Image, out_path: Path,
                        src_alpha: Image.Image = None):
    """Crop region from source, save as PNG (no transparency processing)."""
    src_w, src_h = src.size
    x1, y1, x2, y2 = resolve_bbox(asset['bbox'], src_w, src_h)
    bbox = (x1, y1, x2, y2)
    cropped = src.crop(bbox)
    if src_alpha:
        a = src_alpha.crop(bbox)
        rgba = cropped.convert('RGBA')
        rgba.putalpha(a)
        rgba.save(out_path)
        print(f"  ✓ direct_crop  {out_path.name}  {rgba.size}")
    else:
        cropped.save(out_path)
        print(f"  ✓ direct_crop  {out_path.name}  {cropped.size}")


def hex_to_rgb(hex_color: str) -> np.ndarray:
    """Convert #RRGGBB to numpy array [R, G, B]."""
    h = hex_color.lstrip('#')
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.uint8)


def removebg_known_color(img_rgb: np.ndarray, bg_rgb: np.ndarray,
                          tolerance: int = 30, softness: float = 1.0) -> Image.Image:
    """
    Remove background using a KNOWN bg color (skip edge sampling).
    Safe when the asset is near the crop edges (avoids bg sample contamination).
    """
    sys.path.insert(0, str(SCRIPTS_DIR))
    from removebg_pro import rgb_to_lab, create_alpha_matte, morphological_cleanup, refine_edges

    lab = rgb_to_lab(img_rgb)
    bg_lab = rgb_to_lab(bg_rgb.reshape(1, 1, 3))[0, 0]

    h, w = img_rgb.shape[:2]
    flat = lab.reshape(-1, 3)
    dist = np.sqrt(np.sum((flat - bg_lab) ** 2, axis=1)).reshape(h, w)

    alpha = create_alpha_matte(dist, tolerance * 0.6, tolerance * 1.4)
    alpha = morphological_cleanup(alpha)
    alpha = refine_edges(alpha, img_rgb, radius=softness)

    alpha_uint8 = (alpha * 255).astype(np.uint8)
    rgba = np.dstack([img_rgb, alpha_uint8])
    return Image.fromarray(rgba, 'RGBA')


def handle_removebg(asset: dict, src: Image.Image, out_path: Path,
                     src_alpha: Image.Image = None):
    """Crop + LAB background removal + auto-trim → transparent PNG."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from removebg_pro import remove_background

    src_w, src_h = src.size
    x1, y1, x2, y2 = resolve_bbox(asset['bbox'], src_w, src_h)
    bbox = (x1, y1, x2, y2)
    cropped = src.crop(bbox).convert('RGB')
    arr = np.array(cropped)

    tolerance = asset.get('tolerance', 30)
    softness  = asset.get('softness',  1.2)

    bg_color_hex = asset.get('bg_color')
    if bg_color_hex:
        print(f"  [bg] using known color {bg_color_hex}")
        result = removebg_known_color(arr, hex_to_rgb(bg_color_hex), tolerance, softness)
    else:
        result = remove_background(cropped, tolerance=tolerance, edge_softness=softness)

    # Mask out pixels that were transparent in source (rounded corners, etc.)
    result = apply_source_alpha(result, src_alpha, bbox)
    result = tight_crop(result, padding=0)
    result.save(out_path)
    print(f"  ✓ removebg     {out_path.name}  {result.size}")


def handle_text_render(asset: dict, out_path: Path):
    """Render text/button via butcher_render.py (Playwright headless)."""
    render_script = SCRIPTS_DIR / 'butcher_render.py'
    if not render_script.exists():
        print(f"  ✗ butcher_render.py not found, skipping {asset['name']}")
        return

    # Build a single-asset manifest for butcher_render.py
    # butcher_render.py expects text/style fields nested under "properties"
    flat = {k: v for k, v in asset.items() if k not in ('method', 'bbox', 'tolerance', 'softness')}
    flat['name'] = out_path.stem
    # Move text/style keys into "properties" (butcher_render.py reads from there)
    prop_keys = ('text', 'font_family', 'font_weight', 'font_size', 'color',
                 'text_color', 'direction', 'line_height', 'text_shadow',
                 'text_align', 'bg_color_btn', 'border_radius',
                 'bg_color', 'text_content', 'html')
    properties = {}
    for k in prop_keys:
        if k in flat:
            # map 'color' → 'text_color' for butcher_render compatibility
            dest = 'text_color' if k == 'color' else k
            properties[dest] = flat.pop(k)
    flat['properties'] = properties
    manifest = {
        'assets': [flat],
        'output_dir': str(out_path.parent),
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                     delete=False, encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        tmp_manifest = f.name

    try:
        result = subprocess.run(
            [sys.executable, str(render_script), tmp_manifest, str(out_path.parent)],
            capture_output=True, text=True, encoding='utf-8'
        )
        if result.returncode != 0:
            print(f"  ✗ text_render failed: {result.stderr.strip()[:200]}")
        else:
            # butcher_render saves as <name>.png in output_dir
            rendered = out_path.parent / f"{out_path.stem}.png"
            if rendered.exists():
                # tight crop even rendered text
                img = Image.open(rendered).convert('RGBA')
                img = tight_crop(img)
                img.save(rendered)
                print(f"  ✓ text_render  {rendered.name}  {img.size}")
            else:
                print(f"  ✓ text_render  (check output dir for {out_path.stem}.png)")
    finally:
        os.unlink(tmp_manifest)


def _image_to_b64(img: Image.Image, fmt: str = 'PNG') -> str:
    """Encode PIL image to base64 string."""
    import base64
    import io as _io
    buf = _io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def _extract_image_from_response(data: dict) -> bytes | None:
    """
    Pull image bytes out of an OpenRouter chat response.
    Handles multiple response formats:
    - message['images'] list (gemini-*-image models via OpenRouter)
    - message['content'] list with image_url parts
    - inline base64 data URIs in text content
    Returns None if no image found.
    """
    import base64
    import urllib.request

    msg = data['choices'][0]['message']

    # Format 1: message['images'] — used by gemini-2.5-flash-image via OpenRouter
    images = msg.get('images') or []
    for item in images:
        if isinstance(item, dict) and item.get('type') == 'image_url':
            url = item['image_url']['url']
            if url.startswith('data:'):
                return base64.b64decode(url.split(',', 1)[1])
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()

    # Format 2: message['content'] list with image_url parts
    content = msg.get('content')
    parts = content if isinstance(content, list) else ([{'type': 'text', 'text': str(content)}] if content else [])
    for part in parts:
        if not isinstance(part, dict):
            continue
        if part.get('type') == 'image_url':
            url = part['image_url']['url']
            if url.startswith('data:'):
                return base64.b64decode(url.split(',', 1)[1])
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        if part.get('type') == 'text':
            text = part.get('text', '')
            if 'data:image' in text:
                b64 = text.split('data:image')[1].split(',', 1)[1].split('"')[0].strip()
                return base64.b64decode(b64)

    return None


def gemini_edit_image(source_img: Image.Image, prompt: str,
                       api_key: str, contrast_bg: str = '#FF00FF',
                       model: str = 'google/gemini-2.0-flash-exp:free') -> bytes | None:
    """
    Send source image to Gemini via OpenRouter multimodal chat.
    Ask it to isolate the subject on a solid contrast background.
    Returns image bytes if the model outputs an image, else None.
    """
    import urllib.request
    import urllib.error

    b64 = _image_to_b64(source_img, 'PNG')
    mime = 'image/png'

    edit_instruction = (
        f"{prompt}\n\n"
        f"TASK: Generate a new image containing ONLY the subject described above, "
        f"placed on a perfectly solid flat {contrast_bg} background. "
        f"Remove all text, logos, decorative elements, UI elements, and anything that is not the main subject. "
        f"Do not add shadows or ground reflections. "
        f"Output a clean product-style image ready for background removal. "
        f"The background color must be exactly {contrast_bg}."
    )

    payload = json.dumps({
        'model': model,
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{b64}'}},
                {'type': 'text', 'text': edit_instruction},
            ],
        }],
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://uranus-agency.github.io/Transparentor/',
            'X-Title': 'Butcher Auto',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return _extract_image_from_response(data)
    except urllib.error.HTTPError as e:
        body = e.read()[:300].decode('utf-8', errors='replace')
        raise RuntimeError(f"HTTP {e.code}: {body}")


def _generate_via_pollinations(prompt: str, width: int = 1024, height: int = 1024) -> bytes:
    """Pollinations.ai free image generation (FLUX model). Fallback only."""
    import urllib.request
    import urllib.parse

    encoded = urllib.parse.quote(prompt)
    url = (f'https://image.pollinations.ai/prompt/{encoded}'
           f'?model=flux&width={width}&height={height}&nologo=true')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def _removebg_from_bytes(img_bytes: bytes, contrast_bg: str,
                          tolerance: int, softness: float) -> Image.Image:
    """Decode image bytes → auto-detect bg from corners → remove bg → trim → RGBA."""
    import io as _io
    img = Image.open(_io.BytesIO(img_bytes)).convert('RGB')
    arr = np.array(img)
    h, w = arr.shape[:2]
    cs = max(5, min(20, h // 20, w // 20))
    corners = np.concatenate([
        arr[:cs, :cs].reshape(-1, 3),
        arr[:cs, -cs:].reshape(-1, 3),
        arr[-cs:, :cs].reshape(-1, 3),
        arr[-cs:, -cs:].reshape(-1, 3),
    ])
    actual_bg = corners.mean(axis=0).astype(np.uint8)
    print(f"    detected bg: rgb{tuple(actual_bg)}  (specified: {contrast_bg})")
    result = removebg_known_color(arr, actual_bg, tolerance=tolerance, softness=softness)
    return tight_crop(result, padding=0)


def handle_transparentor(asset: dict, out_path: Path,
                          src: Image.Image = None, src_w: int = 0, src_h: int = 0):
    """
    Transparentor — extract key visual using image-to-image AI editing.

    Flow (preferred):
      1. Crop the key visual region from the source banner
      2. Send crop to Gemini (multimodal) via OpenRouter
      3. Gemini outputs the subject isolated on a solid contrast background
      4. Auto-detect actual bg color from corners
      5. removebg_known_color → tight_crop → save clean transparent PNG

    Fallback (no image output from model):
      → Pollinations FLUX text-to-image using the prompt field

    Falls back to writing prompt file only if no api_key.
    """
    import io

    prompt = asset.get('prompt', '')
    contrast_bg = asset.get('contrast_bg', '#FF00FF')
    tolerance = asset.get('tolerance', 40)
    softness = asset.get('softness', 1.2)
    model = asset.get('model', 'google/gemini-2.5-flash-image')
    api_key = asset.get('api_key') or os.environ.get('OPENROUTER_API_KEY', '')

    # Always save prompt file for reference / manual fallback
    prompt_path = out_path.with_name(out_path.stem + '_prompt.txt')
    transparentor_settings = asset.get(
        'transparentor_settings',
        f'Color Key → {contrast_bg} — threshold {tolerance}, softness {softness}')
    notes = asset.get('notes', '')
    file_content = (
        f"ASSET: {asset.get('name', out_path.stem)}\n"
        f"CONTRAST BACKGROUND: {contrast_bg}\n"
        f"TRANSPARENTOR SETTINGS: {transparentor_settings}\n\n"
        f"== PASTE THIS PROMPT INTO TRANSPARENTOR ==\n\n{prompt}\n\n"
        f"== STEPS ==\n"
        f"1. Open https://uranus-agency.github.io/Transparentor/\n"
        f"2. Upload source banner as reference image\n"
        f"3. Paste the prompt above\n"
        f"4. After generation: Color Key → color {contrast_bg} → threshold 35, softness 1.0\n"
        f"5. Download PNG → save as: {out_path.name}\n"
        f"6. Copy to this folder: {out_path.parent}/\n"
    )
    if notes:
        file_content += f"\n== NOTES ==\n{notes}\n"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    if not api_key:
        print(f"  ✓ transparentor  {prompt_path.name}  (no API key — manual step needed)")
        return

    # ── Crop source region to use as reference image ──────────────────────────
    source_crop = None
    if src is not None and 'bbox' in asset:
        x1, y1, x2, y2 = resolve_bbox(asset['bbox'], src_w, src_h)
        source_crop = src.crop((x1, y1, x2, y2))
        print(f"  [transparentor] sending source crop {source_crop.size} to {model} ...")
    elif src is not None:
        source_crop = src
        print(f"  [transparentor] sending full source {src.size} to {model} ...")

    img_bytes = None

    # ── Step 1: Gemini image-to-image editing ─────────────────────────────────
    if source_crop is not None:
        try:
            img_bytes = gemini_edit_image(source_crop, prompt, api_key, contrast_bg, model)
            if img_bytes:
                print(f"    ✓ got image from {model}")
            else:
                print(f"    model returned text only — falling back to Pollinations")
        except Exception as e:
            print(f"    [{model}] {e} — falling back to Pollinations")

    # ── Step 2: Fallback — Pollinations text-to-image ─────────────────────────
    if not img_bytes:
        flux_prompt = (
            f"{prompt} "
            f"Solid flat {contrast_bg} background only. No shadows, no ground plane. "
            f"Clean product render, centered."
        )
        print(f"    [fallback] Pollinations FLUX ...")
        try:
            img_bytes = _generate_via_pollinations(flux_prompt)
        except Exception as e:
            print(f"  ✗ all image gen failed: {e}")
            print(f"    prompt saved to {prompt_path.name} — manual step needed")
            return

    # ── Remove bg → trim → save ───────────────────────────────────────────────
    result = _removebg_from_bytes(img_bytes, contrast_bg, tolerance, softness)
    result.save(out_path)
    print(f"  ✓ transparentor  {out_path.name}  {result.size}  (bg removed)")

    raw_path = out_path.with_name(out_path.stem + '_raw_generated.png')
    Image.open(io.BytesIO(img_bytes)).save(raw_path)
    print(f"    raw → {raw_path.name}")


# ── main ──────────────────────────────────────────────────────────────────────

def run(manifest_path: str):
    manifest_path = Path(manifest_path).resolve()
    with open(manifest_path, encoding='utf-8') as f:
        manifest = json.load(f)

    source_path = Path(manifest['source']).resolve()
    if not source_path.exists():
        # Try relative to manifest location
        source_path = (manifest_path.parent / manifest['source']).resolve()
    if not source_path.exists():
        print(f"ERROR: source image not found: {manifest['source']}")
        sys.exit(1)

    # Output folder: next to source image, named butcher_<name|stem>
    if 'output_dir' in manifest:
        out_dir = Path(manifest['output_dir']).resolve()
    elif 'name' in manifest:
        out_dir = source_path.parent / f"butcher_{manifest['name']}"
    else:
        out_dir = source_path.parent / f"butcher_{source_path.stem}"
    out_dir.mkdir(parents=True, exist_ok=True)

    src_rgba = Image.open(source_path)
    has_alpha = src_rgba.mode == 'RGBA'
    src = src_rgba.convert('RGB')
    src_alpha = src_rgba.split()[3] if has_alpha else None
    src_w, src_h = src.size
    print(f"\nButcher Auto")
    print(f"  Source : {source_path.name}  ({src_w}×{src_h})")
    print(f"  Output : {out_dir}")
    print(f"  Assets : {len(manifest['assets'])}\n")

    for asset in manifest['assets']:
        name   = asset['name']
        method = asset.get('method', 'direct_crop')
        out_path = out_dir / f"{name}.png"

        print(f"[{name}]")
        if method == 'direct_crop':
            handle_direct_crop(asset, src, out_path, src_alpha)
        elif method == 'removebg':
            handle_removebg(asset, src, out_path, src_alpha)
        elif method == 'text_render':
            handle_text_render(asset, out_path)
        elif method == 'transparentor':
            handle_transparentor(asset, out_path, src=src, src_w=src_w, src_h=src_h)
        else:
            print(f"  ✗ unknown method: {method}")

    print(f"\nDone → {out_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python butcher_auto.py manifest.json")
        sys.exit(1)
    run(sys.argv[1])
