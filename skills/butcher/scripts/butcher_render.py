"""
Butcher Asset Renderer
======================
Takes a JSON asset manifest and renders each asset as a transparent PNG.
Uses Playwright (headless Chromium) for pixel-perfect Persian text & CSS rendering.

Usage:
    python butcher_render.py <manifest.json> <output_dir>

Manifest format: see generate_manifest() for the schema.
"""

import json
import sys
import os
import math
import time
from pathlib import Path

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def generate_html_for_asset(asset: dict, fonts_css: str = "") -> str:
    """Generate a self-contained HTML page for a single asset."""

    asset_type = asset.get("type", "unknown")

    # Route to the right renderer
    renderers = {
        "background": render_background,
        "card": render_card,
        "cta": render_cta,
        "text": render_text,
        "badge": render_badge,
        "logo": render_logo,
        "shape": render_shape,
        "icon": render_icon,
        "gradient_overlay": render_gradient_overlay,
        "decorative": render_decorative,
    }

    renderer = renderers.get(asset_type, render_generic)
    inner_html, inner_css = renderer(asset)

    return f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="utf-8">
<style>
  {fonts_css}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    background: transparent !important;
    width: {asset.get('width', 400)}px;
    height: {asset.get('height', 300)}px;
    overflow: hidden;
  }}
  #asset {{
    position: absolute;
    top: 0; left: 0;
    width: {asset.get('width', 400)}px;
    height: {asset.get('height', 300)}px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  {inner_css}
</style>
</head>
<body>
<div id="asset">
  {inner_html}
</div>
</body>
</html>"""


# ============================================================
# RENDERERS — one per asset type
# ============================================================

def render_background(asset: dict):
    """Render background with gradient, pattern, solid color, or texture."""
    props = asset.get("properties", {})
    bg_type = props.get("bg_type", "solid")

    if bg_type == "gradient":
        colors = props.get("colors", ["#1a5e3a", "#0d4a2a"])
        angle = props.get("angle", 135)
        stops = ", ".join(colors)
        bg_css = f"linear-gradient({angle}deg, {stops})"
    elif bg_type == "radial_gradient":
        colors = props.get("colors", ["#1a5e3a", "#0d4a2a"])
        stops = ", ".join(colors)
        bg_css = f"radial-gradient(ellipse at center, {stops})"
    else:
        bg_css = props.get("color", "#1a5e3a")

    pattern_css = ""
    pattern_html = ""
    if props.get("pattern"):
        pat = props["pattern"]
        pat_type = pat.get("type", "none")
        pat_color = pat.get("color", "rgba(255,255,255,0.05)")
        pat_size = pat.get("size", 30)

        if pat_type == "diagonal_lines":
            pattern_css = f"""
            .pattern {{
                position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                background: repeating-linear-gradient(
                    {pat.get('angle', 45)}deg,
                    transparent,
                    transparent {pat_size//2}px,
                    {pat_color} {pat_size//2}px,
                    {pat_color} {pat_size//2 + 1}px
                );
            }}"""
            pattern_html = '<div class="pattern"></div>'
        elif pat_type == "grid":
            pattern_css = f"""
            .pattern {{
                position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                background-image:
                    linear-gradient({pat_color} 1px, transparent 1px),
                    linear-gradient(90deg, {pat_color} 1px, transparent 1px);
                background-size: {pat_size}px {pat_size}px;
            }}"""
            pattern_html = '<div class="pattern"></div>'
        elif pat_type == "gold_bricks" or pat_type == "bricks":
            # Gold bar / brick pattern like Melli Gold
            pattern_css = f"""
            .pattern {{
                position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                opacity: 0.08;
            }}
            .brick-row {{
                display: flex;
                flex-wrap: nowrap;
                gap: 4px;
                margin-bottom: 4px;
            }}
            .brick {{
                width: {pat_size}px;
                height: {pat_size // 2}px;
                border: 1.5px solid {pat_color};
                border-radius: 2px;
            }}
            .brick-row.offset {{
                margin-left: {pat_size // 2}px;
            }}"""
            rows = asset.get('height', 300) // (pat_size // 2 + 4) + 1
            cols = asset.get('width', 400) // (pat_size + 4) + 2
            row_html = ""
            for r in range(rows):
                offset = " offset" if r % 2 else ""
                bricks = "".join(['<div class="brick"></div>' for _ in range(cols)])
                row_html += f'<div class="brick-row{offset}">{bricks}</div>'
            pattern_html = f'<div class="pattern">{row_html}</div>'

    css = f"""
    .bg-layer {{
        width: 100%; height: 100%;
        background: {bg_css};
        position: relative;
        overflow: hidden;
    }}
    {pattern_css}
    """
    html = f'<div class="bg-layer">{pattern_html}</div>'
    return html, css


def render_card(asset: dict):
    """Render a card (white/colored rounded rect) with optional text and decorative elements."""
    props = asset.get("properties", {})
    bg_color = props.get("bg_color", "#FFFFFF")
    border_radius = props.get("border_radius", 20)
    shadow = props.get("shadow", "none")
    text = props.get("text", "")
    text_color = props.get("text_color", "#C8A255")
    font_family = props.get("font_family", "B Yekan, Yekan, IRANSansX, Vazirmatn, Tahoma")
    font_size = props.get("font_size", 36)
    font_weight = props.get("font_weight", "bold")
    line_height = props.get("line_height", 1.3)
    text_align = props.get("text_align", "center")
    padding = props.get("padding", "20px 30px")

    # Optional decorative dots/spheres
    decorations_html = ""
    decorations_css = ""
    if props.get("decorations"):
        for i, dec in enumerate(props["decorations"]):
            dec_type = dec.get("type", "sphere")
            x = dec.get("x", "50%")
            y = dec.get("y", "50%")
            size = dec.get("size", 14)
            color = dec.get("color", "#C8A255")

            if dec_type == "sphere" or dec_type == "gold_sphere":
                decorations_css += f"""
                .dec-{i} {{
                    position: absolute;
                    top: {y}; left: {x};
                    width: {size}px; height: {size}px;
                    border-radius: 50%;
                    background: radial-gradient(circle at 35% 35%, #F5E6A3, {color} 50%, #8B6914 100%);
                    box-shadow: 0 1px 3px rgba(0,0,0,0.3), inset 0 -1px 2px rgba(0,0,0,0.2);
                    transform: translate(-50%, -50%);
                }}"""
                decorations_html += f'<div class="dec-{i}"></div>'

    shadow_css = ""
    if shadow and shadow != "none":
        shadow_css = f"box-shadow: {shadow};"

    css = f"""
    .card {{
        position: relative;
        width: {asset.get('width', 280)}px;
        height: {asset.get('height', 200)}px;
        background: {bg_color};
        border-radius: {border_radius}px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: {padding};
        {shadow_css}
    }}
    .card-text {{
        font-family: {font_family};
        font-size: {font_size}px;
        font-weight: {font_weight};
        color: {text_color};
        line-height: {line_height};
        text-align: {text_align};
        direction: rtl;
    }}
    {decorations_css}
    """
    html = f"""
    <div class="card">
        <div class="card-text">{text}</div>
        {decorations_html}
    </div>
    """
    return html, css


def render_cta(asset: dict):
    """Render a CTA button (pill, rounded rect, etc.)."""
    props = asset.get("properties", {})
    bg_color = props.get("bg_color", "#C8A255")
    bg_gradient = props.get("bg_gradient", "")
    text = props.get("text", "خرید")
    text_color = props.get("text_color", "#1a5e3a")
    font_family = props.get("font_family", "B Yekan, Yekan, IRANSansX, Vazirmatn, Tahoma")
    font_size = props.get("font_size", 18)
    font_weight = props.get("font_weight", "bold")
    border_radius = props.get("border_radius", 999)
    padding = props.get("padding", "12px 40px")
    border = props.get("border", "none")
    shadow = props.get("shadow", "none")
    icon = props.get("icon", "")  # e.g., "chevron_left" for ‹

    bg = bg_gradient if bg_gradient else bg_color

    icon_html = ""
    if icon == "chevron_left":
        icon_html = '<span class="cta-icon">‹</span>'
    elif icon == "chevron_right":
        icon_html = '<span class="cta-icon">›</span>'
    elif icon:
        icon_html = f'<span class="cta-icon">{icon}</span>'

    css = f"""
    .cta {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {bg};
        color: {text_color};
        font-family: {font_family};
        font-size: {font_size}px;
        font-weight: {font_weight};
        border-radius: {border_radius}px;
        padding: {padding};
        border: {border};
        box-shadow: {shadow};
        direction: rtl;
        white-space: nowrap;
        letter-spacing: 0.3px;
    }}
    .cta-icon {{
        font-size: {font_size + 6}px;
        line-height: 1;
    }}
    """
    html = f'<div class="cta">{text}{icon_html}</div>'
    return html, css


def render_text(asset: dict):
    """Render standalone text element."""
    props = asset.get("properties", {})
    text = props.get("text", "")
    text_color = props.get("text_color", "#FFFFFF")
    font_family = props.get("font_family", "B Yekan, Yekan, IRANSansX, Vazirmatn, Tahoma")
    font_size = props.get("font_size", 32)
    font_weight = props.get("font_weight", "bold")
    text_align = props.get("text_align", "center")
    line_height = props.get("line_height", 1.4)
    text_shadow = props.get("text_shadow", "none")

    css = f"""
    .text-el {{
        font-family: {font_family};
        font-size: {font_size}px;
        font-weight: {font_weight};
        color: {text_color};
        text-align: {text_align};
        line-height: {line_height};
        direction: rtl;
        text-shadow: {text_shadow};
    }}
    """
    # Support raw HTML for mixed-color or styled text
    raw_html = props.get("html", "")
    content = raw_html if raw_html else text
    html = f'<div class="text-el">{content}</div>'
    return html, css


def render_badge(asset: dict):
    """Render a badge (discount, label, tag)."""
    props = asset.get("properties", {})
    bg_color = props.get("bg_color", "#FF0000")
    text = props.get("text", "")
    text_color = props.get("text_color", "#FFFFFF")
    font_size = props.get("font_size", 16)
    font_weight = props.get("font_weight", "bold")
    shape = props.get("shape", "circle")  # circle, pill, rectangle
    border_radius = props.get("border_radius", "50%" if shape == "circle" else "12px")
    size = props.get("size", 60)

    css = f"""
    .badge {{
        width: {size}px; height: {size if shape == 'circle' else 'auto'}px;
        background: {bg_color};
        border-radius: {border_radius};
        display: flex;
        align-items: center;
        justify-content: center;
        color: {text_color};
        font-family: B Yekan, Yekan, IRANSansX, Vazirmatn, Tahoma;
        font-size: {font_size}px;
        font-weight: {font_weight};
        direction: rtl;
        padding: 4px 8px;
    }}
    """
    html = f'<div class="badge">{text}</div>'
    return html, css


def render_logo(asset: dict):
    """Render a text-based logo."""
    props = asset.get("properties", {})
    text = props.get("text", "")
    text_color = props.get("text_color", "#FFFFFF")
    font_family = props.get("font_family", "B Yekan, Yekan, IRANSansX, Tahoma")
    font_size = props.get("font_size", 28)
    font_weight = props.get("font_weight", "bold")

    css = f"""
    .logo {{
        font-family: {font_family};
        font-size: {font_size}px;
        font-weight: {font_weight};
        color: {text_color};
        letter-spacing: 1px;
    }}
    """
    html = f'<div class="logo">{text}</div>'
    return html, css


def render_shape(asset: dict):
    """Render geometric shapes."""
    props = asset.get("properties", {})
    shape = props.get("shape", "rectangle")
    bg_color = props.get("bg_color", "#FFFFFF")
    border_radius = props.get("border_radius", 0)
    border = props.get("border", "none")
    shadow = props.get("shadow", "none")
    rotation = props.get("rotation", 0)

    css = f"""
    .shape {{
        width: {asset.get('width', 100)}px;
        height: {asset.get('height', 100)}px;
        background: {bg_color};
        border-radius: {border_radius}{'%' if shape == 'circle' else 'px'};
        border: {border};
        box-shadow: {shadow};
        transform: rotate({rotation}deg);
    }}
    """
    html = '<div class="shape"></div>'
    return html, css


def render_icon(asset: dict):
    """Render icons using CSS shapes or SVG."""
    props = asset.get("properties", {})
    icon_type = props.get("icon_type", "circle")
    color = props.get("color", "#C8A255")
    size = props.get("size", 20)

    if icon_type == "gold_sphere" or icon_type == "sphere":
        css = f"""
        .icon {{
            width: {size}px; height: {size}px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #F5E6A3, {color} 50%, #8B6914 100%);
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        """
    elif icon_type == "dot":
        css = f"""
        .icon {{
            width: {size}px; height: {size}px;
            border-radius: 50%;
            background: {color};
        }}
        """
    else:
        css = f"""
        .icon {{
            width: {size}px; height: {size}px;
            background: {color};
        }}
        """
    html = '<div class="icon"></div>'
    return html, css


def render_gradient_overlay(asset: dict):
    """Render a gradient overlay layer."""
    props = asset.get("properties", {})
    colors = props.get("colors", ["rgba(0,0,0,0.5)", "transparent"])
    angle = props.get("angle", 180)
    stops = ", ".join(colors)

    css = f"""
    .overlay {{
        width: 100%; height: 100%;
        background: linear-gradient({angle}deg, {stops});
    }}
    """
    html = '<div class="overlay"></div>'
    return html, css


def render_decorative(asset: dict):
    """Render decorative elements: sparkles, dots, particles."""
    props = asset.get("properties", {})
    dec_type = props.get("dec_type", "dots")

    if dec_type == "gold_spheres_row":
        count = props.get("count", 3)
        size = props.get("size", 12)
        gap = props.get("gap", 6)
        color = props.get("color", "#C8A255")
        spheres_html = ""
        for _ in range(count):
            spheres_html += f"""<div style="
                width:{size}px;height:{size}px;border-radius:50%;
                background:radial-gradient(circle at 35% 35%, #F5E6A3, {color} 50%, #8B6914 100%);
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            "></div>"""
        css = f".deco {{ display: flex; gap: {gap}px; align-items: center; }}"
        html = f'<div class="deco">{spheres_html}</div>'
    else:
        css = ""
        html = ""
    return html, css


def render_generic(asset: dict):
    """Fallback renderer."""
    props = asset.get("properties", {})
    text = props.get("text", "?")
    css = """
    .generic {
        font-family: Tahoma; font-size: 20px; color: #999;
        border: 2px dashed #ccc; padding: 20px; border-radius: 8px;
    }
    """
    html = f'<div class="generic">{text}</div>'
    return html, css


# ============================================================
# MAIN RENDERER — uses Playwright
# ============================================================

def render_assets(manifest_path: str, output_dir: str):
    """Render all assets from a manifest JSON to transparent PNGs."""
    from playwright.sync_api import sync_playwright

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    brand = manifest.get("brand", "unknown")
    fonts_css = manifest.get("fonts_css", "")
    assets = manifest.get("assets", [])

    print(f"\n{'='*50}")
    print(f"  BUTCHER - Rendering {len(assets)} assets for [{brand}]")
    print(f"  Output: {output_dir}")
    print(f"{'='*50}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for asset in assets:
            name = asset.get("name", "unnamed")
            w = asset.get("width", 400)
            h = asset.get("height", 300)

            print(f"  [CUT] Rendering: {name} ({w}x{h})...", end=" ")

            context = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=2,  # 2x for retina quality
            )
            page = context.new_page()

            html = generate_html_for_asset(asset, fonts_css)

            # Write temp HTML
            temp_html_path = os.path.join(output_dir, f"_temp_{name}.html")
            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html)

            page.goto(f"file:///{temp_html_path.replace(os.sep, '/')}")
            page.wait_for_timeout(300)  # Let fonts load

            # Screenshot with transparency
            output_path = os.path.join(output_dir, f"{name}.png")
            page.screenshot(
                path=output_path,
                omit_background=True,  # THIS is the key — transparent background!
            )

            # Clean up temp file
            os.remove(temp_html_path)
            context.close()

            print(f"OK -> {name}.png")

        browser.close()

    print(f"\n{'='*50}")
    print(f"  DONE! {len(assets)} assets saved to {output_dir}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python butcher_render.py <manifest.json> <output_dir>")
        sys.exit(1)
    render_assets(sys.argv[1], sys.argv[2])
