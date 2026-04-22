"""
PSD Butcher v1.0
================
Surgical asset extractor for layered PSD files.
Opens any .psd file, walks every layer (including nested groups),
and exports each one as a clean transparent PNG — production-ready
for Figma, Photoshop, or ad banners.

Usage:
    python psd_butcher.py <input.psd> [output_dir]
    python psd_butcher.py <input.psd> [output_dir] --merge-groups
    python psd_butcher.py <input.psd> [output_dir] --visible-only
    python psd_butcher.py <input.psd> [output_dir] --composite

Output:
    output_dir/
        01_LayerName.png
        02_GroupName__SubLayer.png
        ...
        _manifest.json      ← full layer metadata
        _report.xml         ← butcher report
        _composite.png      ← flattened preview
"""

import sys
import os
import json
import re
import colorsys
import numpy as np
from pathlib import Path
from PIL import Image, ImageChops
from collections import Counter

# ── stdout encoding fix for Windows ───────────────────────────────────────────
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from psd_tools import PSDImage
    from psd_tools.constants import Tag
except ImportError:
    print("ERROR: psd-tools not installed.")
    print("Install: pip install psd-tools")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def sanitize_name(name: str) -> str:
    """Convert layer name to safe filename."""
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name[:60] or "unnamed"


def auto_trim(img: Image.Image, padding: int = 2) -> Image.Image:
    """Remove transparent borders, keep padding px around content."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    alpha = np.array(img)[:, :, 3]
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)
    if not np.any(rows) or not np.any(cols):
        return img  # fully transparent — return as-is
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin = max(0, rmin - padding)
    rmax = min(img.height - 1, rmax + padding)
    cmin = max(0, cmin - padding)
    cmax = min(img.width - 1, cmax + padding)
    return img.crop((cmin, rmin, cmax + 1, rmax + 1))


def render_layer_to_canvas(layer, canvas_w: int, canvas_h: int) -> "Image.Image | None":
    """Render a single layer placed on a full-canvas RGBA image.
    Uses composite() for groups and smart objects (topil() misses embedded content),
    topil() for simple pixel/shape/text layers."""
    try:
        ltype = layer_type_name(layer) if not layer.is_group() else 'GROUP'
        if layer.is_group() or ltype == 'SMART_OBJECT':
            img = layer.composite()
        else:
            img = layer.topil()
        if img is None:
            return None
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        paste_x, paste_y = layer.left, layer.top
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        src_x = max(0, -paste_x)
        src_y = max(0, -paste_y)
        dst_x = max(0, paste_x)
        dst_y = max(0, paste_y)
        crop_w = min(img.width - src_x, canvas_w - dst_x)
        crop_h = min(img.height - src_y, canvas_h - dst_y)
        if crop_w > 0 and crop_h > 0:
            region = img.crop((src_x, src_y, src_x + crop_w, src_y + crop_h))
            canvas.paste(region, (dst_x, dst_y), region)
        return canvas
    except Exception as e:
        print(f"  [WARN] Could not render '{layer.name}': {e}")
        return None


def composite_with_blend(base: "Image.Image", overlay: "Image.Image",
                          blend_mode: str, opacity: int) -> "Image.Image":
    """
    Composite overlay onto base with the given Photoshop blend mode and opacity.
    Handles SCREEN, MULTIPLY, OVERLAY, SOFT_LIGHT, LINEAR_DODGE, and NORMAL.
    """
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    b = np.array(base, dtype=np.float32) / 255.0
    o = np.array(overlay, dtype=np.float32) / 255.0
    o[:, :, 3] *= opacity / 255.0

    Ab = b[:, :, 3:4]
    Ao = o[:, :, 3:4]
    Cb = b[:, :, :3]
    Co = o[:, :, :3]

    bm = blend_mode.lower()
    if 'screen' in bm:
        Cs = 1.0 - (1.0 - Cb) * (1.0 - Co)
    elif 'multiply' in bm:
        Cs = Cb * Co
    elif 'overlay' in bm:
        Cs = np.where(Cb < 0.5, 2 * Cb * Co, 1 - 2 * (1 - Cb) * (1 - Co))
    elif 'soft' in bm:
        Cs = np.where(Co <= 0.5,
                      Cb - (1 - 2 * Co) * Cb * (1 - Cb),
                      Cb + (2 * Co - 1) * (np.sqrt(np.clip(Cb, 0, 1)) - Cb))
    elif 'dodge' in bm:
        Cs = np.clip(Cb + Co, 0, 1)
    elif 'burn' in bm:
        Cs = np.clip(1 - (1 - Cb) / (Co + 1e-6), 0, 1)
    elif 'lighten' in bm:
        Cs = np.maximum(Cb, Co)
    elif 'darken' in bm:
        Cs = np.minimum(Cb, Co)
    else:
        Cs = Co  # normal

    Ar = Ao + Ab * (1 - Ao)
    Cr = np.where(Ar > 1e-6, (Cs * Ao + Cb * Ab * (1 - Ao)) / Ar, 0.0)

    out = np.clip(np.concatenate([Cr, Ar], axis=2) * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def bb_classify(layer) -> str:
    """
    Classify a top-level PSD layer for BB campaign production.

    The question we're answering: "Is this layer a STANDALONE USABLE ASSET
    that a designer would animate independently in a billboard, OR is it
    internal Photoshop atmosphere that should be baked into the hero visual?"

    Returns: 'BACKGROUND' | 'HERO' | 'FX' | 'TEXT' | 'LOGO' | 'UI'
    """
    name = layer.name.lower().strip()
    blend = str(getattr(layer, 'blend_mode', 'normal')).lower()
    opacity = getattr(layer, 'opacity', 255)
    ltype = layer_type_name(layer) if not layer.is_group() else 'GROUP'

    # Background: named as background or base plate
    bg_keywords = ['background', 'bg', 'back', 'پس‌زمینه', 'preferred',
                   'plate', 'canvas', 'base', 'backdrop']
    if any(k in name for k in bg_keywords):
        return 'BACKGROUND'

    # Text and UI elements are always individual
    if ltype == 'TEXT':
        return 'TEXT'
    if any(k in name for k in ['logo', 'لوگو', 'brand', 'mark', 'symbol']):
        return 'LOGO'
    if any(k in name for k in ['cta', 'button', 'btn', 'دکمه', 'call', 'action']):
        return 'UI'

    # FX/atmosphere: non-normal blend mode = internal composition detail, NOT a standalone asset.
    # Low-opacity layers named as effects also belong to the hero's atmosphere.
    fx_blends = ['screen', 'multiply', 'overlay', 'soft_light', 'hard_light',
                 'color_dodge', 'linear_dodge', 'lighten', 'darken', 'difference',
                 'exclusion', 'color_burn', 'linear_burn', 'add', 'dissolve']
    fx_keywords = ['shadow', 'glow', 'light', 'sparkle', 'flare', 'shine',
                   'reflection', 'haze', 'vignette', 'blur', 'grain', 'noise',
                   'texture', 'fx', 'effect', 'atmosphere', 'halo', 'aura',
                   'glare', 'dust', 'particle', 'bokeh']

    is_fx_blend = any(b in blend for b in fx_blends)
    is_fx_name = any(k in name for k in fx_keywords)
    is_low_opacity = opacity < 200

    if is_fx_blend:
        return 'FX'
    if is_fx_name and is_low_opacity:
        return 'FX'

    return 'HERO'


def bb_export(psd, output_dir: Path, canvas_w: int, canvas_h: int,
              trim: bool = True, verbose: bool = True) -> list:
    """
    BB Campaign Production Export.

    Philosophy: deliver the minimum set of independently animatable assets
    that a BB animator needs. This means:
    - background   → 1 PNG (the plate behind everything)
    - hero         → 1 PNG (product + ALL its atmosphere effects baked in)
    - text/logo/UI → 1 PNG each (independently controllable in the timeline)

    FX layers (glows, shadows, sparkles) are NOT separate assets — they are
    atmosphere that belongs to the hero and are composited into it.
    """
    # Collect top-level layers in bottom-to-top order (PS bottom layer first)
    top_layers = list(reversed(list(psd)))

    # Classify each layer
    classified = []
    for layer in top_layers:
        cls = bb_classify(layer)
        blend = str(getattr(layer, 'blend_mode', 'normal'))
        opacity = getattr(layer, 'opacity', 255)
        classified.append((layer, cls, blend, opacity))
        if verbose:
            print(f"        [{cls:10s}] {layer.name} (blend={blend}, opacity={opacity})")

    # Build hero composite: HERO layers first, then FX layers on top, respecting blend modes
    hero_canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    has_hero = False

    for (layer, cls, blend, opacity) in classified:
        if cls in ('HERO', 'FX'):
            img = render_layer_to_canvas(layer, canvas_w, canvas_h)
            if img is None or is_empty(img):
                continue
            hero_canvas = composite_with_blend(hero_canvas, img, blend, opacity)
            has_hero = True

    # Export
    assets = []
    counter = 1

    # 1. Background(s)
    for (layer, cls, blend, opacity) in classified:
        if cls != 'BACKGROUND':
            continue
        img = render_layer_to_canvas(layer, canvas_w, canvas_h)
        if img is None or is_empty(img):
            continue
        if trim:
            t = auto_trim(img)
            if not is_empty(t):
                img = t
        fname = f"{counter:02d}_background.png"
        img.save(str(output_dir / fname), "PNG")
        assets.append({
            "id": counter, "filename": fname, "name": layer.name,
            "class": "BACKGROUND", "blend_mode": blend, "opacity": opacity,
            "exported_size": {"width": img.width, "height": img.height},
            "palette": extract_palette(img),
        })
        if verbose:
            print(f"  [{counter:02d}] BACKGROUND → {fname}")
        counter += 1

    # 2. Hero composite (product + baked-in atmosphere)
    if has_hero and not is_empty(hero_canvas):
        if trim:
            t = auto_trim(hero_canvas)
            if not is_empty(t):
                hero_canvas = t
        fname = f"{counter:02d}_hero.png"
        hero_canvas.save(str(output_dir / fname), "PNG")
        assets.append({
            "id": counter, "filename": fname, "name": "hero_composite",
            "class": "HERO", "blend_mode": "normal", "opacity": 255,
            "exported_size": {"width": hero_canvas.width, "height": hero_canvas.height},
            "palette": extract_palette(hero_canvas),
        })
        if verbose:
            print(f"  [{counter:02d}] HERO (product + atmosphere baked in) → {fname}")
        counter += 1

    # 3. Text / Logo / UI (individually animatable)
    for (layer, cls, blend, opacity) in classified:
        if cls not in ('TEXT', 'LOGO', 'UI'):
            continue
        img = render_layer_to_canvas(layer, canvas_w, canvas_h)
        if img is None or is_empty(img):
            continue
        if trim:
            t = auto_trim(img)
            if not is_empty(t):
                img = t
        safe = sanitize_name(layer.name)
        fname = f"{counter:02d}_{cls.lower()}_{safe}.png"
        img.save(str(output_dir / fname), "PNG")
        assets.append({
            "id": counter, "filename": fname, "name": layer.name,
            "class": cls, "blend_mode": blend, "opacity": opacity,
            "exported_size": {"width": img.width, "height": img.height},
            "palette": extract_palette(img),
        })
        if verbose:
            print(f"  [{counter:02d}] {cls} → {fname}")
        counter += 1

    return assets


def is_empty(img: Image.Image) -> bool:
    """Return True if image is fully transparent or blank."""
    if img is None:
        return True
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    alpha = np.array(img)[:, :, 3]
    return np.max(alpha) < 5


def extract_palette(img: Image.Image, n: int = 6) -> list:
    """Extract top N dominant colors as HEX from image."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    # Only use opaque pixels
    mask = arr[:, :, 3] > 50
    if not np.any(mask):
        return []
    pixels = arr[mask][:, :3]
    # Quantize to reduce noise — round to nearest 32
    quantized = (pixels // 32 * 32).astype(np.uint8)
    tuples = [tuple(p) for p in quantized]
    counter = Counter(tuples)
    top = counter.most_common(n)
    return [f"#{r:02X}{g:02X}{b:02X}" for (r, g, b), _ in top]


def layer_type_name(layer) -> str:
    """Human-readable layer type."""
    if layer.is_group():
        return "GROUP"
    kind = str(layer.kind).replace("LayerKind.", "")
    type_map = {
        "type": "TEXT",
        "pixel": "PIXEL",
        "shape": "SHAPE",
        "smartobject": "SMART_OBJECT",
        "fill": "FILL",
        "adjustment": "ADJUSTMENT",
        "solidcolorfill": "COLOR_FILL",
    }
    return type_map.get(kind.lower(), kind.upper())


def guess_category(name: str, ltype: str) -> str:
    """Guess asset category from layer name and type."""
    n = name.lower()
    if ltype == "TEXT":
        if any(k in n for k in ["title", "headline", "head", "عنوان"]):
            return "TITLE"
        if any(k in n for k in ["subtitle", "sub", "زیر"]):
            return "SUBTITLE"
        if any(k in n for k in ["cta", "btn", "button", "click", "دکمه"]):
            return "CTA"
        if any(k in n for k in ["price", "قیمت", "تومان"]):
            return "PRICE"
        if any(k in n for k in ["discount", "تخفیف", "%"]):
            return "DISCOUNT"
        return "BODY"
    if any(k in n for k in ["logo", "brand", "لوگو"]):
        return "LOGO"
    if any(k in n for k in ["product", "محصول", "item"]):
        return "PRODUCT"
    if any(k in n for k in ["bg", "background", "پس‌زمینه", "back"]):
        return "BACKGROUND"
    if any(k in n for k in ["icon", "آیکون"]):
        return "ICON"
    if any(k in n for k in ["badge", "tag", "ribbon", "نشان"]):
        return "BADGE"
    if any(k in n for k in ["shadow", "gradient", "overlay", "glow"]):
        return "DECORATIVE"
    if ltype == "SHAPE":
        return "SHAPE"
    if ltype in ("FILL", "COLOR_FILL", "ADJUSTMENT"):
        return "BACKGROUND"
    return "ILLUSTRATION"


def get_text_info(layer) -> dict:
    """Extract text content and typography from a text layer."""
    info = {}
    try:
        engine_data = layer.engine_dict
        # Text content
        info['text'] = layer.text or ""
        # Font and size from engine data
        styles = engine_data.get('StyleRun', {}).get('RunArray', [])
        if styles:
            style = styles[0].get('StyleSheet', {}).get('StyleSheetData', {})
            info['font_size'] = round(style.get('FontSize', 0), 1)
            fonts = style.get('Font', None)
            if fonts is not None:
                info['font_size'] = round(style.get('FontSize', 0), 1)
            # Color
            color = style.get('FillColor', {}).get('Values', None)
            if color and len(color) >= 4:
                r, g, b = int(color[1]*255), int(color[2]*255), int(color[3]*255)
                info['text_color'] = f"#{r:02X}{g:02X}{b:02X}"
            # Font name
            font_set = engine_data.get('DocumentResources', {}).get('FontSet', [])
            font_idx = style.get('Font', 0)
            if font_set and isinstance(font_idx, int) and font_idx < len(font_set):
                info['font_family'] = font_set[font_idx].get('Name', 'Unknown')
    except Exception:
        try:
            info['text'] = layer.text or ""
        except Exception:
            info['text'] = ""
    return info


# ══════════════════════════════════════════════════════════════════════════════
#  LAYER WALKER
# ══════════════════════════════════════════════════════════════════════════════

def walk_layers(layers, prefix: str = "", depth: int = 0):
    """
    Recursively yield (layer, full_path, depth, composite_mode) for all layers.
    composite_mode=False → use topil() for individual layer pixels.
    """
    for layer in reversed(list(layers)):
        path = f"{prefix}/{layer.name}" if prefix else layer.name
        if layer.is_group():
            yield from walk_layers(layer, prefix=path, depth=depth + 1)
        yield (layer, path, depth, False)


def has_only_text_layers(layer) -> bool:
    """Return True if group contains only TEXT layers (no visual/pixel content)."""
    for child in layer:
        if child.is_group():
            if not has_only_text_layers(child):
                return False
        else:
            t = layer_type_name(child)
            if t not in ("TEXT",):
                return False
    return True


def has_any_text_layer(layer) -> bool:
    """Return True if group contains ANY text layer anywhere in its subtree."""
    for child in layer:
        if child.is_group():
            if has_any_text_layer(child):
                return True
        else:
            if layer_type_name(child) == "TEXT":
                return True
    return False


def is_artboard_wrapper(layer, canvas_w: int, canvas_h: int, threshold: float = 0.65) -> bool:
    """
    Return True if group is an artboard/canvas container that wraps the real
    layer stack. Detected via name patterns only (size-based detection is too
    ambiguous for background layers that also cover the full canvas).
    Patterns:
    - Name matches "WxH" dimensions (e.g. "2166x1493", "1080x1920")
    - Name contains "artboard" (e.g. "Artboard 1", "artboard_mobile")
    """
    if not layer.is_group():
        return False
    name = layer.name.strip()
    if re.match(r'^\d+\s*[xX×]\s*\d+$', name):
        return True
    if 'artboard' in name.lower():
        return True
    return False


def smart_walk(layers, prefix: str = "", depth: int = 0,
               canvas_w: int = 0, canvas_h: int = 0,
               inside_secondary_artboard: bool = False):
    """
    Semantic walk for --smart mode:

    Decision tree per group:
    1. Artboard/canvas wrapper (name=WxH or "artboard") → recurse.
       Secondary artboards (Artboard 1, Artboard 2…) → skip hidden layers inside.
    2. Group has ANY text layer in subtree → recurse (keeps logo, CTA, title all separate)
    3. Pure visual group (no text anywhere) → composite as ONE merged PNG

    composite_mode=True → render with layer.composite() instead of topil().
    """
    for layer in reversed(list(layers)):
        path = f"{prefix}/{layer.name}" if prefix else layer.name

        # Skip hidden layers inside secondary artboards (they're old/unused versions)
        if inside_secondary_artboard and not layer.visible:
            continue

        if layer.is_group():
            if is_artboard_wrapper(layer, canvas_w, canvas_h):
                # Detect secondary artboards by name ("Artboard 1", "Artboard 2"…)
                is_secondary = bool(re.match(r'^artboard\s*\d+$', layer.name.strip().lower()))
                yield from smart_walk(layer, prefix=path, depth=depth,
                                      canvas_w=canvas_w, canvas_h=canvas_h,
                                      inside_secondary_artboard=is_secondary)
            elif has_any_text_layer(layer):
                yield from smart_walk(layer, prefix=path, depth=depth + 1,
                                      canvas_w=canvas_w, canvas_h=canvas_h,
                                      inside_secondary_artboard=inside_secondary_artboard)
            else:
                # Pure visual group (no text): composite entire group as one PNG
                yield (layer, path, depth, True)
        else:
            yield (layer, path, depth, False)


# ══════════════════════════════════════════════════════════════════════════════
#  CORE EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════

def extract_psd(
    psd_path: str,
    output_dir: str = None,
    visible_only: bool = False,
    merge_groups: bool = False,
    do_composite: bool = True,
    trim: bool = True,
    skip_empty: bool = True,
    verbose: bool = True,
    smart: bool = False,
    bb: bool = False,
):
    psd_path = Path(psd_path)
    if not psd_path.exists():
        print(f"ERROR: File not found: {psd_path}")
        sys.exit(1)

    # Default output dir = same folder as PSD, named after file
    if output_dir is None:
        output_dir = psd_path.parent / f"{psd_path.stem}_assets"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  PSD BUTCHER v1.0")
    print(f"{'='*60}")
    print(f"  File   : {psd_path.name}")
    print(f"  Output : {output_dir}")
    print(f"{'='*60}\n")

    # ── Load PSD ──────────────────────────────────────────────────────────────
    print("  [1/4] Loading PSD...")
    psd = PSDImage.open(str(psd_path))
    canvas_w, canvas_h = psd.width, psd.height
    print(f"        Canvas: {canvas_w} x {canvas_h} px")
    print(f"        Color mode: {psd.color_mode}")

    # ── Composite preview ─────────────────────────────────────────────────────
    composite_img = None
    if do_composite:
        print("  [2/4] Rendering composite preview...")
        try:
            composite_img = psd.composite()
            if composite_img:
                comp_path = output_dir / "_composite.png"
                composite_img.save(str(comp_path), "PNG")
                print(f"        Saved: _composite.png ({composite_img.width}x{composite_img.height})")
        except Exception as e:
            print(f"        WARNING: Composite render failed: {e}")

    # ── Walk and extract layers ───────────────────────────────────────────────
    print("  [3/4] Extracting layers...")

    # ── BB MODE: campaign-ready asset export ─────────────────────────────────
    if bb:
        print("        [BB] Campaign-ready export — FX baked into hero, background separate")
        bb_assets = bb_export(psd, output_dir, canvas_w, canvas_h,
                              trim=trim, verbose=verbose)
        manifest = {
            "psd_file": psd_path.name,
            "canvas": {"width": canvas_w, "height": canvas_h},
            "color_mode": str(psd.color_mode),
            "mode": "bb",
            "exported": len(bb_assets),
            "layers": bb_assets,
        }
        print(f"\n  [4/4] Writing manifest & report...")
        manifest_path = output_dir / "_manifest.json"
        with open(str(manifest_path), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"        Saved: _manifest.json")
        print(f"\n{'='*60}")
        print(f"  DONE! (BB mode)")
        print(f"  Exported : {len(bb_assets)} campaign-ready assets")
        print(f"  Output   : {output_dir}")
        print(f"{'='*60}\n")
        return manifest

    manifest_layers = []
    exported_count = 0
    skipped_count = 0
    counter = 1

    # Smart mode uses semantic walk; flat mode uses full recursive walk
    if smart:
        all_layers = list(smart_walk(psd, canvas_w=canvas_w, canvas_h=canvas_h))
        print(f"        [SMART] Semantic export — visual groups merged, text layers individual")
    else:
        all_layers = list(walk_layers(psd))
    total = len(all_layers)

    for (layer, full_path, depth, composite_mode) in all_layers:
        # Skip groups in flat mode when merge_groups is False
        if layer.is_group() and not merge_groups and not composite_mode:
            continue

        # Skip hidden layers if visible_only
        if visible_only and not layer.visible:
            skipped_count += 1
            continue

        # Layer metadata
        ltype = "GROUP_COMPOSITE" if composite_mode else layer_type_name(layer)
        category = guess_category(layer.name, ltype if not composite_mode else layer_type_name(layer))

        # bbox is a plain tuple (left, top, right, bottom) in psd-tools 1.9+
        raw_bbox = layer.bbox
        if hasattr(raw_bbox, 'left'):
            bl, bt, br, bb_ = raw_bbox.left, raw_bbox.top, raw_bbox.right, raw_bbox.bottom
        else:
            bl, bt, br, bb_ = raw_bbox[0], raw_bbox[1], raw_bbox[2], raw_bbox[3]

        paste_x = layer.left
        paste_y = layer.top

        # Safe filename
        safe_path = sanitize_name(full_path.replace("/", "__"))
        filename = f"{counter:02d}_{safe_path}.png"
        out_path = output_dir / filename

        # ── Export: composite() for smart groups, topil() for individual layers ──
        if composite_mode:
            # Render entire group (all sub-layers, blend modes, effects) as one PNG
            try:
                img = layer.composite()
                if img is None:
                    raise ValueError("composite() returned None")
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                # Place composited group on full canvas at group's position
                canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
                src_x = max(0, -paste_x)
                src_y = max(0, -paste_y)
                dst_x = max(0, paste_x)
                dst_y = max(0, paste_y)
                crop_w = min(img.width - src_x, canvas_w - dst_x)
                crop_h = min(img.height - src_y, canvas_h - dst_y)
                if crop_w > 0 and crop_h > 0:
                    region = img.crop((src_x, src_y, src_x + crop_w, src_y + crop_h))
                    canvas.paste(region, (dst_x, dst_y), region)
                img = canvas
            except Exception as e2:
                print(f"  [SKIP] {layer.name} — composite failed: {e2}")
                skipped_count += 1
                continue
        else:
            # ── Export layer pixels via topil() ──────────────────────────────
            try:
                img = layer.topil()
                if img is None:
                    raise ValueError("topil() returned None")
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                # Paste onto transparent canvas at layer's position
                # Clamp paste position — layers can extend beyond canvas bounds
                canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
                src_x = max(0, -paste_x)
                src_y = max(0, -paste_y)
                dst_x = max(0, paste_x)
                dst_y = max(0, paste_y)
                crop_w = min(img.width - src_x, canvas_w - dst_x)
                crop_h = min(img.height - src_y, canvas_h - dst_y)
                if crop_w > 0 and crop_h > 0:
                    region = img.crop((src_x, src_y, src_x + crop_w, src_y + crop_h))
                    canvas.paste(region, (dst_x, dst_y), region)
                img = canvas
            except Exception as e2:
                print(f"  [SKIP] {layer.name} — could not render: {e2}")
                skipped_count += 1
                continue

        # Convert to RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Skip empty layers
        if skip_empty and is_empty(img):
            if verbose:
                print(f"  [SKIP] {layer.name} — empty/transparent")
            skipped_count += 1
            continue

        # Auto-trim
        original_size = img.size
        if trim:
            img = auto_trim(img)

        # Extract palette
        palette = extract_palette(img)

        # Save
        img.save(str(out_path), "PNG", optimize=True)

        # Text info
        text_info = {}
        if ltype == "TEXT":
            text_info = get_text_info(layer)

        # Layer record
        record = {
            "id": counter,
            "filename": filename,
            "name": layer.name,
            "full_path": full_path,
            "type": ltype,
            "category": category,
            "visible": layer.visible,
            "opacity": getattr(layer, 'opacity', 255),
            "blend_mode": str(getattr(layer, 'blend_mode', 'normal')),
            "bbox": {
                "left": bl,
                "top": bt,
                "right": br,
                "bottom": bb_,
                "width": br - bl,
                "height": bb_ - bt,
            },
            "canvas_size": {"width": canvas_w, "height": canvas_h},
            "exported_size": {"width": img.width, "height": img.height},
            "position_pct": {
                "x": round(bl / canvas_w * 100, 1),
                "y": round(bt / canvas_h * 100, 1),
                "w": round((br - bl) / canvas_w * 100, 1),
                "h": round((bb_ - bt) / canvas_h * 100, 1),
            },
            "palette": palette,
            **text_info,
        }
        manifest_layers.append(record)

        status = "  " if layer.visible else "  [HIDDEN]"
        print(f"  {status}[{counter:02d}] {layer.name:<35} {ltype:<15} -> {filename}")
        counter += 1
        exported_count += 1

    # ── Manifest JSON ─────────────────────────────────────────────────────────
    print(f"\n  [4/4] Writing manifest & report...")

    manifest = {
        "psd_file": psd_path.name,
        "canvas": {"width": canvas_w, "height": canvas_h},
        "color_mode": str(psd.color_mode),
        "total_layers": total,
        "exported": exported_count,
        "skipped": skipped_count,
        "layers": manifest_layers,
    }

    manifest_path = output_dir / "_manifest.json"
    with open(str(manifest_path), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"        Saved: _manifest.json")

    # ── Butcher Report XML ────────────────────────────────────────────────────
    report_path = output_dir / "_report.xml"
    with open(str(report_path), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<butcher_report tool="psd_butcher" version="1.0">\n\n')

        # Overview
        f.write('  <banner_overview>\n')
        f.write(f'    <source_file>{psd_path.name}</source_file>\n')
        f.write(f'    <canvas>{canvas_w}x{canvas_h}px</canvas>\n')
        f.write(f'    <color_mode>{psd.color_mode}</color_mode>\n')
        f.write(f'    <total_layers_in_psd>{total}</total_layers_in_psd>\n')
        f.write(f'    <exported_assets>{exported_count}</exported_assets>\n')
        f.write(f'    <skipped>{skipped_count}</skipped>\n')
        # Global palette from composite
        if composite_img:
            global_palette = extract_palette(composite_img.convert('RGBA'), n=8)
            f.write('    <global_color_palette>\n')
            for hex_color in global_palette:
                f.write(f'      <color hex="{hex_color}" />\n')
            f.write('    </global_color_palette>\n')
        f.write('  </banner_overview>\n\n')

        # Assets
        f.write('  <assets>\n')
        for layer in manifest_layers:
            f.write(f'    <asset id="{layer["id"]}">\n')
            f.write(f'      <name>{_xml(layer["name"])}</name>\n')
            f.write(f'      <filename>{layer["filename"]}</filename>\n')
            f.write(f'      <category>{layer["category"]}</category>\n')
            f.write(f'      <type>{layer["type"]}</type>\n')
            f.write(f'      <visible>{layer["visible"]}</visible>\n')
            f.write(f'      <opacity>{layer["opacity"]}</opacity>\n')
            f.write(f'      <blend_mode>{_xml(layer["blend_mode"])}</blend_mode>\n')

            b = layer["bbox"]
            f.write(f'      <bbox left="{b["left"]}" top="{b["top"]}" '
                    f'right="{b["right"]}" bottom="{b["bottom"]}" '
                    f'width="{b["width"]}" height="{b["height"]}" />\n')

            p = layer["position_pct"]
            f.write(f'      <position_pct x="{p["x"]}%" y="{p["y"]}%" '
                    f'w="{p["w"]}%" h="{p["h"]}%" />\n')

            f.write(f'      <exported_size>{layer["exported_size"]["width"]}x'
                    f'{layer["exported_size"]["height"]}px</exported_size>\n')

            if layer.get("palette"):
                f.write('      <palette>\n')
                for c in layer["palette"]:
                    f.write(f'        <color hex="{c}" />\n')
                f.write('      </palette>\n')

            if layer["type"] == "TEXT":
                f.write(f'      <text_content>{_xml(layer.get("text", ""))}</text_content>\n')
                if layer.get("font_family"):
                    f.write(f'      <font_family>{_xml(layer["font_family"])}</font_family>\n')
                if layer.get("font_size"):
                    f.write(f'      <font_size>{layer["font_size"]}px</font_size>\n')
                if layer.get("text_color"):
                    f.write(f'      <text_color>{layer["text_color"]}</text_color>\n')

            f.write(f'    </asset>\n\n')
        f.write('  </assets>\n\n')

        # Layer map (ASCII tree)
        f.write('  <layer_map>\n    <![CDATA[\n')
        for layer in manifest_layers:
            depth = layer["full_path"].count("/")
            indent = "  " * depth
            vis = "" if layer["visible"] else " [hidden]"
            f.write(f'    {indent}[{layer["id"]:02d}] {layer["name"]} ({layer["type"]}){vis}\n')
        f.write('    ]]>\n  </layer_map>\n\n')

        f.write('</butcher_report>\n')

    print(f"        Saved: _report.xml")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"  Exported : {exported_count} assets")
    print(f"  Skipped  : {skipped_count} (empty/hidden)")
    print(f"  Output   : {output_dir}")
    print(f"{'='*60}\n")

    return manifest


def _xml(s: str) -> str:
    """Escape XML special characters."""
    if not isinstance(s, str):
        s = str(s)
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ══════════════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════════════

def print_usage():
    print("""
PSD Butcher v2.0 — Surgical Asset Extractor
============================================

Usage:
    python psd_butcher.py <input.psd> [output_dir] [options]

Arguments:
    input.psd       Path to the PSD file
    output_dir      Output folder (default: <psd_name>_assets/ next to PSD)

Options:
    --bb            ⭐ BEST for BB billboard production (default when goal=campaign).
                    Classifies layers into: BACKGROUND, HERO, FX, TEXT, LOGO, UI.
                    FX layers (glows, shadows, sparkles) are baked INTO the hero.
                    Result: 2-4 clean campaign-ready assets, not 40+ PSD fragments.
                    Use when you need assets to animate directly in a BB timeline.
    --smart         Semantic export — visual groups merged, text individual.
                    Use when PSD has named groups (key visual, background, etc.)
                    and layers ARE inside groups.
    --visible-only  Skip hidden layers
    --merge-groups  Also export group layers (as merged composites)
    --no-composite  Skip the flattened composite preview
    --no-trim       Don't auto-trim transparent borders
    --keep-empty    Don't skip fully transparent layers
    --quiet         Suppress per-layer logs

Examples:
    python psd_butcher.py banner.psd --bb                       ← BB production ⭐
    python psd_butcher.py banner.psd ./out --bb --no-trim
    python psd_butcher.py banner.psd --smart                    ← group-based smart export
    python psd_butcher.py banner.psd                            ← full atomic export
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    psd_file = args[0]
    output_folder = None
    flags = set(a.lower() for a in args)

    # Second positional arg = output dir (if not a flag)
    if len(args) >= 2 and not args[1].startswith("--"):
        output_folder = args[1]

    extract_psd(
        psd_path=psd_file,
        output_dir=output_folder,
        visible_only="--visible-only" in flags,
        merge_groups="--merge-groups" in flags,
        do_composite="--no-composite" not in flags,
        trim="--no-trim" not in flags,
        skip_empty="--keep-empty" not in flags,
        verbose="--quiet" not in flags,
        smart="--smart" in flags,
        bb="--bb" in flags,
    )
