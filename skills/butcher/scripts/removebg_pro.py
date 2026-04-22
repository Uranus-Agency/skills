"""
RemoveBG Pro — Professional Background Removal
================================================
Uses LAB color space segmentation + alpha matting.
No external AI models needed — pure scipy/numpy/PIL.

Much better than flood-fill because:
  1. Works in perceptually uniform LAB color space
  2. Handles disconnected background regions (between arms, hair, etc.)
  3. Alpha matting for smooth, anti-aliased edges
  4. Morphological cleanup for professional output

Usage:
    python removebg_pro.py <input_image> <output_image> [--tolerance 30]
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from scipy.ndimage import binary_fill_holes, binary_dilation, binary_erosion, gaussian_filter
import argparse
import os


def rgb_to_lab(rgb_array: np.ndarray) -> np.ndarray:
    """Convert RGB to CIE LAB color space for perceptually uniform distance."""
    # Normalize to 0-1
    rgb = rgb_array.astype(np.float64) / 255.0

    # Linearize sRGB
    mask = rgb > 0.04045
    rgb[mask] = ((rgb[mask] + 0.055) / 1.055) ** 2.4
    rgb[~mask] = rgb[~mask] / 12.92

    # RGB to XYZ (D65 illuminant)
    x = rgb[:,:,0] * 0.4124564 + rgb[:,:,1] * 0.3575761 + rgb[:,:,2] * 0.1804375
    y = rgb[:,:,0] * 0.2126729 + rgb[:,:,1] * 0.7151522 + rgb[:,:,2] * 0.0721750
    z = rgb[:,:,0] * 0.0193339 + rgb[:,:,1] * 0.1191920 + rgb[:,:,2] * 0.9503041

    # Normalize by D65 white point
    x /= 0.95047
    y /= 1.00000
    z /= 1.08883

    # XYZ to LAB
    def f(t):
        mask = t > 0.008856
        result = np.zeros_like(t)
        result[mask] = t[mask] ** (1/3)
        result[~mask] = 7.787 * t[~mask] + 16/116
        return result

    fx, fy, fz = f(x), f(y), f(z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return np.stack([L, a, b], axis=-1)


def sample_background_color(img_array: np.ndarray, margin: int = 15) -> np.ndarray:
    """Sample background color from image borders (corners + edges).
    Returns multiple sample colors for better matching."""
    h, w = img_array.shape[:2]

    # Collect samples from edges
    samples = []
    # Top/bottom strips
    samples.append(img_array[:margin, :, :].reshape(-1, 3))
    samples.append(img_array[-margin:, :, :].reshape(-1, 3))
    # Left/right strips
    samples.append(img_array[:, :margin, :].reshape(-1, 3))
    samples.append(img_array[:, -margin:, :].reshape(-1, 3))

    all_samples = np.concatenate(samples, axis=0)

    # Use median (robust against outliers like foreground elements near edges)
    bg_color = np.median(all_samples, axis=0)

    # Also compute std for adaptive tolerance
    bg_std = np.std(all_samples, axis=0)

    return bg_color, bg_std, all_samples


def compute_bg_distance(lab_image: np.ndarray, bg_samples_lab: np.ndarray) -> np.ndarray:
    """Compute minimum color distance to background samples in LAB space.
    Uses multiple cluster centers for gradient backgrounds."""
    from scipy.cluster.vq import kmeans

    # Cluster background samples into 2-4 centers (handles gradients)
    n_clusters = min(4, max(2, len(bg_samples_lab) // 100))
    try:
        centers, _ = kmeans(bg_samples_lab.astype(np.float64), n_clusters)
    except:
        centers = np.mean(bg_samples_lab, axis=0, keepdims=True)

    # For each pixel, find minimum distance to any cluster center
    h, w = lab_image.shape[:2]
    flat = lab_image.reshape(-1, 3)

    min_dist = np.full(flat.shape[0], np.inf)
    for center in centers:
        dist = np.sqrt(np.sum((flat - center) ** 2, axis=1))
        min_dist = np.minimum(min_dist, dist)

    return min_dist.reshape(h, w)


def create_alpha_matte(distance_map: np.ndarray, threshold_low: float, threshold_high: float) -> np.ndarray:
    """Create soft alpha matte with smooth transitions.
    - distance < threshold_low: transparent (background)
    - distance > threshold_high: opaque (foreground)
    - between: smooth gradient (edge region)
    """
    alpha = np.zeros_like(distance_map, dtype=np.float64)

    # Background
    bg_mask = distance_map < threshold_low
    # Foreground
    fg_mask = distance_map > threshold_high
    # Transition zone
    trans_mask = ~bg_mask & ~fg_mask

    alpha[fg_mask] = 1.0
    alpha[bg_mask] = 0.0

    if np.any(trans_mask):
        # Smooth linear interpolation in transition zone
        alpha[trans_mask] = (distance_map[trans_mask] - threshold_low) / (threshold_high - threshold_low)

    return alpha


def morphological_cleanup(alpha: np.ndarray, iterations: int = 2) -> np.ndarray:
    """Clean up alpha matte with morphological operations."""
    # Binarize for morphological ops
    binary = alpha > 0.5

    # Fill small holes in foreground
    binary = binary_fill_holes(binary)

    # Remove small noise blobs
    labeled, num_features = ndimage.label(binary)
    if num_features > 1:
        component_sizes = ndimage.sum(binary, labeled, range(1, num_features + 1))
        largest = np.argmax(component_sizes) + 1
        # Keep only components > 1% of largest
        threshold = component_sizes[largest - 1] * 0.01
        for i in range(1, num_features + 1):
            if component_sizes[i - 1] < threshold:
                binary[labeled == i] = False

    # Also remove small foreground noise
    # Erode slightly then dilate to remove thin artifacts
    struct = ndimage.generate_binary_structure(2, 1)
    cleaned = binary_erosion(binary, struct, iterations=1)
    cleaned = binary_dilation(cleaned, struct, iterations=1)

    # Merge back: use cleaned binary but preserve soft edges from original alpha
    result = alpha.copy()
    # Where cleaned says background but original alpha was low, force to 0
    result[~cleaned & (alpha < 0.7)] = 0.0

    return result


def refine_edges(alpha: np.ndarray, rgb_array: np.ndarray, radius: float = 1.5) -> np.ndarray:
    """Refine edges using guided filter-like approach for smooth anti-aliasing."""
    # Find edge pixels (where alpha is between 0.05 and 0.95)
    edge_mask = (alpha > 0.05) & (alpha < 0.95)

    if not np.any(edge_mask):
        return alpha

    # Apply Gaussian blur to alpha for smooth edges
    smoothed = gaussian_filter(alpha, sigma=radius)

    # Blend: use smoothed alpha at edges, original elsewhere
    result = alpha.copy()
    result[edge_mask] = smoothed[edge_mask]

    # Ensure 0-1 range
    result = np.clip(result, 0, 1)

    return result


def remove_background(
    img: Image.Image,
    tolerance: int = 30,
    edge_softness: float = 1.5,
    denoise: bool = True
) -> Image.Image:
    """
    Professional background removal pipeline.

    Args:
        img: Input PIL Image
        tolerance: Background detection sensitivity (10-60, lower = more aggressive)
        edge_softness: Edge smoothing radius (0.5-3.0)
        denoise: Remove small noise artifacts
    """
    rgb = np.array(img.convert('RGB'))
    h, w = rgb.shape[:2]

    print(f"  [1/6] Converting to LAB color space...")
    lab = rgb_to_lab(rgb)

    print(f"  [2/6] Sampling background color from edges...")
    bg_color_rgb, bg_std, bg_samples = sample_background_color(rgb, margin=max(10, min(h, w) // 20))
    bg_samples_lab = rgb_to_lab(bg_samples.reshape(1, -1, 3)).reshape(-1, 3)

    print(f"  [3/6] Computing color distance map...")
    distance = compute_bg_distance(lab, bg_samples_lab)

    # Adaptive thresholds based on tolerance
    # LAB distance: ~10 is barely noticeable, ~30 is clearly different, ~50+ is very different
    threshold_low = tolerance * 0.6
    threshold_high = tolerance * 1.4

    print(f"  [4/6] Creating alpha matte (thresholds: {threshold_low:.0f}-{threshold_high:.0f})...")
    alpha = create_alpha_matte(distance, threshold_low, threshold_high)

    if denoise:
        print(f"  [5/6] Morphological cleanup...")
        alpha = morphological_cleanup(alpha)

    print(f"  [6/6] Refining edges (softness={edge_softness})...")
    alpha = refine_edges(alpha, rgb, radius=edge_softness)

    # Compose final RGBA
    alpha_uint8 = (alpha * 255).astype(np.uint8)
    rgba = np.dstack([rgb, alpha_uint8])

    return Image.fromarray(rgba, 'RGBA')


def auto_trim(img: Image.Image, padding: int = 6) -> Image.Image:
    """Trim transparent borders."""
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
# CLI
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RemoveBG Pro')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output PNG path')
    parser.add_argument('--tolerance', type=int, default=30, help='BG detection sensitivity (10-60)')
    parser.add_argument('--softness', type=float, default=1.5, help='Edge softness (0.5-3.0)')
    parser.add_argument('--no-trim', action='store_true', help='Skip auto-trim')
    args = parser.parse_args()

    print(f"\n  RemoveBG Pro")
    print(f"  Input: {args.input}")

    img = Image.open(args.input)
    print(f"  Size: {img.width}x{img.height}")

    result = remove_background(img, tolerance=args.tolerance, edge_softness=args.softness)

    if not args.no_trim:
        result = auto_trim(result)
        print(f"  Trimmed: {result.width}x{result.height}")

    result.save(args.output, 'PNG', optimize=True)
    print(f"  Saved: {args.output}")
    print(f"  Done!\n")
