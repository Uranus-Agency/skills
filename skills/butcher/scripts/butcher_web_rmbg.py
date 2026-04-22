"""
Butcher Web BG Remover
======================
Uses Playwright to automate online background removal services.
Crops assets from original banner, uploads to remove.bg, downloads clean results.

Pipeline:
1. Crop each asset from source image (generous bbox)
2. Upload to remove.bg via Playwright
3. Download transparent PNG result
4. Auto-trim to content bounds
5. Save final asset

Usage:
    python butcher_web_rmbg.py <manifest.json> <source_image> <output_dir>
"""

import json
import sys
import os
import time
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path

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

    # Add padding for better bg removal
    pad = bbox.get('padding', 10)
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(w + pad * 2, src_w - x)
    h = min(h + pad * 2, src_h - y)

    return source_img.crop((x, y, x + w, y + h))


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


def remove_bg_via_web(crop_paths: list, output_dir: str, service: str = "remove_bg"):
    """
    Use Playwright to automate background removal via web services.
    Processes all crops in batch through the browser.
    """
    from playwright.sync_api import sync_playwright

    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Need visible for some services
        context = browser.new_context(accept_downloads=True)

        for crop_path, asset_name in crop_paths:
            page = context.new_page()
            print(f"    Uploading {asset_name} to remove.bg...", end=" ")

            try:
                page.goto("https://www.remove.bg/", timeout=30000)
                page.wait_for_timeout(2000)

                # Upload image
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(crop_path)

                # Wait for processing
                print("processing...", end=" ")
                page.wait_for_timeout(8000)  # Wait for AI processing

                # Try to download
                # Look for download button
                try:
                    with page.expect_download(timeout=15000) as download_info:
                        # Click download button
                        dl_btn = page.locator('a:has-text("Download"), button:has-text("Download")').first
                        dl_btn.click()
                    download = download_info.value
                    dl_path = os.path.join(output_dir, f"{asset_name}_rmbg.png")
                    download.save_as(dl_path)
                    print(f"OK -> {asset_name}_rmbg.png")
                except:
                    # If download fails, take screenshot of result
                    print("download failed, taking screenshot...", end=" ")
                    result_img = page.locator('.result-image, [data-testid="result"], img[src*="result"]').first
                    if result_img.is_visible():
                        ss_path = os.path.join(output_dir, f"{asset_name}_rmbg.png")
                        result_img.screenshot(path=ss_path, omit_background=True)
                        print(f"OK (screenshot) -> {asset_name}_rmbg.png")
                    else:
                        print("FAILED")
            except Exception as e:
                print(f"ERROR: {e}")
            finally:
                page.close()

        browser.close()


def run_pipeline(manifest_path: str, source_path: str, output_dir: str):
    """Full butcher pipeline."""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    source_img = Image.open(source_path).convert('RGB')
    os.makedirs(output_dir, exist_ok=True)

    crops_dir = os.path.join(output_dir, "_crops")
    rmbg_dir = os.path.join(output_dir, "_rmbg")
    os.makedirs(crops_dir, exist_ok=True)
    os.makedirs(rmbg_dir, exist_ok=True)

    assets = manifest.get("assets", [])

    print(f"\n{'='*50}")
    print(f"  BUTCHER v4 - Full Pipeline")
    print(f"  Source: {os.path.basename(source_path)} ({source_img.size[0]}x{source_img.size[1]})")
    print(f"  Assets: {len(assets)}")
    print(f"{'='*50}")

    # Phase 1: Crop all assets
    print(f"\n  Phase 1: Cropping assets from source...")
    crop_list = []
    for asset in assets:
        name = asset.get("name", "unnamed")
        bbox = asset.get("bbox", {})
        method = asset.get("bg_removal", "web")

        if method == "none":
            # Just save the whole/cropped image
            cropped = crop_asset(source_img, bbox) if bbox else source_img.copy()
            out = os.path.join(output_dir, f"{name}.png")
            cropped.save(out, "PNG")
            print(f"    [CUT] {name} -> saved directly (no bg removal)")
            continue

        cropped = crop_asset(source_img, bbox) if bbox else source_img.copy()

        # Upscale small crops for better bg removal
        min_dim = min(cropped.width, cropped.height)
        if min_dim < 200:
            scale_factor = max(2, 400 // min_dim)
            cropped = cropped.resize(
                (cropped.width * scale_factor, cropped.height * scale_factor),
                Image.LANCZOS
            )
            print(f"    [CUT] {name} -> upscaled {scale_factor}x for quality")

        crop_path = os.path.join(crops_dir, f"{name}.png")
        cropped.save(crop_path, "PNG")
        crop_list.append((crop_path, name))
        print(f"    [CUT] {name} -> {cropped.width}x{cropped.height}")

    if not crop_list:
        print("\n  No assets need bg removal. Done!")
        return

    # Phase 2: Remove backgrounds via web service
    print(f"\n  Phase 2: Removing backgrounds ({len(crop_list)} assets)...")
    remove_bg_via_web(crop_list, rmbg_dir)

    # Phase 3: Auto-trim results
    print(f"\n  Phase 3: Trimming final assets...")
    for _, name in crop_list:
        rmbg_path = os.path.join(rmbg_dir, f"{name}_rmbg.png")
        if os.path.exists(rmbg_path):
            img = Image.open(rmbg_path).convert('RGBA')
            trimmed = auto_trim(img, padding=4)
            final_path = os.path.join(output_dir, f"{name}.png")
            trimmed.save(final_path, "PNG", optimize=True)
            print(f"    [TRIM] {name} -> {trimmed.width}x{trimmed.height}")
        else:
            print(f"    [SKIP] {name} - no rmbg result found")

    print(f"\n{'='*50}")
    print(f"  DONE! Assets in: {output_dir}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python butcher_web_rmbg.py <manifest.json> <source_image> <output_dir>")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2], sys.argv[3])
