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


def generate_image(prompt: str, api_key: str = '', model: str = '') -> bytes:
    """
    Generate image from prompt. Returns raw image bytes (JPEG or PNG).

    Priority:
    1. If api_key set → try OpenRouter chat completions (for models that output images)
    2. Fallback → Pollinations.ai (free, no key needed, FLUX model)
    """
    import urllib.request
    import urllib.parse

    if api_key:
        try:
            return _generate_via_openrouter_chat(prompt, api_key, model or 'openai/gpt-4o-image')
        except Exception as e:
            print(f"    [openrouter] {e} — falling back to pollinations")

    # Pollinations.ai — free, URL-based, no key needed
    return _generate_via_pollinations(prompt)


def _generate_via_pollinations(prompt: str, width: int = 1024, height: int = 1024) -> bytes:
    """Pollinations.ai free image generation (FLUX model)."""
    import urllib.request
    import urllib.parse

    encoded = urllib.parse.quote(prompt)
    url = (f'https://image.pollinations.ai/prompt/{encoded}'
           f'?model=flux&width={width}&height={height}&nologo=true')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def _generate_via_openrouter_chat(prompt: str, api_key: str, model: str) -> bytes:
    """
    Try OpenRouter chat completions for models that return images in content.
    Works with models like openai/gpt-image-1 if/when OpenRouter supports them.
    """
    import urllib.request
    import base64

    payload = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    content = data['choices'][0]['message']['content']
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get('type') == 'image_url':
                url = part['image_url']['url']
                if url.startswith('data:'):
                    return base64.b64decode(url.split(',', 1)[1])
                with urllib.request.urlopen(url, timeout=60) as r:
                    return r.read()
    elif isinstance(content, str) and 'data:image' in content:
        return base64.b64decode(content.split(',', 1)[1].strip())

    raise ValueError(f"No image in chat response for model {model}")


def handle_transparentor(asset: dict, out_path: Path):
    """
    Transparentor: auto-generate visual asset via OpenRouter → remove contrast bg → clean PNG.

    Flow:
    1. Build prompt instructing AI to render asset on solid contrast bg
    2. Call OpenRouter image gen API
    3. Pipe result through removebg_known_color()
    4. Auto-trim → save as <name>.png

    Falls back to writing prompt file only if OPENROUTER_API_KEY not set and not in asset.
    """
    import io

    prompt = asset.get('prompt', '')
    contrast_bg = asset.get('contrast_bg', '#FF00FF')
    tolerance = asset.get('tolerance', 40)
    softness = asset.get('softness', 1.2)
    model = asset.get('model', 'openai/dall-e-3')

    api_key = asset.get('api_key') or os.environ.get('OPENROUTER_API_KEY', '')

    # Always save prompt file for reference
    prompt_path = out_path.with_name(out_path.stem + '_prompt.txt')
    transparentor_settings = asset.get('transparentor_settings',
                                        f'Color Key → {contrast_bg} — threshold {tolerance}, softness {softness}')
    notes = asset.get('notes', '')
    file_content = f"""ASSET: {asset.get('name', out_path.stem)}
CONTRAST BACKGROUND: {contrast_bg}
TRANSPARENTOR SETTINGS: {transparentor_settings}

== PASTE THIS PROMPT INTO TRANSPARENTOR ==

{prompt}

== STEPS ==
1. Open https://uranus-agency.github.io/Transparentor/
2. Paste the prompt above
3. After generation: Color Key → color {contrast_bg} → threshold 35, softness 1.0
4. Download PNG → save as: {out_path.name}
5. Copy to this folder: {out_path.parent}/
"""
    if notes:
        file_content += f"\n== NOTES ==\n{notes}\n"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    if not api_key:
        print(f"  ✓ transparentor  {prompt_path.name}  (no API key — manual step needed)")
        print(f"    contrast_bg: {contrast_bg}  |  {transparentor_settings}")
        return

    # Auto-generate via OpenRouter
    full_prompt = (
        f"{prompt}\n\n"
        f"IMPORTANT: Render the subject on a perfectly solid flat {contrast_bg} background only. "
        f"No shadows, no ground plane, no gradients, no other colors. "
        f"The background must be exactly {contrast_bg} so it can be keyed out."
    )

    print(f"  [transparentor] generating image (model={model or 'pollinations/flux'}) ...")
    try:
        img_bytes = generate_image(full_prompt, api_key, model)
    except Exception as e:
        print(f"  ✗ image gen failed: {e}")
        print(f"    prompt saved to {prompt_path.name} — manual step needed")
        return

    # Decode → removebg → trim → save
    gen_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    arr = np.array(gen_img)

    # Auto-detect actual bg color from corners (handles JPEG color drift)
    h, w = arr.shape[:2]
    corner_size = max(5, min(20, h // 20, w // 20))
    corners = np.concatenate([
        arr[:corner_size, :corner_size].reshape(-1, 3),
        arr[:corner_size, -corner_size:].reshape(-1, 3),
        arr[-corner_size:, :corner_size].reshape(-1, 3),
        arr[-corner_size:, -corner_size:].reshape(-1, 3),
    ])
    actual_bg_rgb = corners.mean(axis=0).astype(np.uint8)
    print(f"    detected bg: rgb{tuple(actual_bg_rgb)}  (specified: {contrast_bg})")

    result = removebg_known_color(arr, actual_bg_rgb, tolerance=tolerance, softness=softness)
    result = tight_crop(result, padding=0)
    result.save(out_path)
    print(f"  ✓ transparentor  {out_path.name}  {result.size}  (auto-generated + bg removed)")

    # Also save raw generated image for reference
    raw_path = out_path.with_name(out_path.stem + '_raw_generated.png')
    gen_img_pil = Image.open(io.BytesIO(img_bytes))
    gen_img_pil.save(raw_path)
    print(f"    raw saved → {raw_path.name}")


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
            handle_transparentor(asset, out_path)
        else:
            print(f"  ✗ unknown method: {method}")

    print(f"\nDone → {out_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python butcher_auto.py manifest.json")
        sys.exit(1)
    run(sys.argv[1])
