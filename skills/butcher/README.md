# Butcher

Dissect any advertising banner into campaign-ready transparent PNGs for BB billboard production.

Send image → get folder of clean assets.

---

## Setup

```bash
pip install pillow numpy playwright
python3 -m playwright install chromium
```

Set your OpenRouter API key once:

```bash
export OPENROUTER_API_KEY=sk-or-...
```

Add to your shell profile (`~/.zshrc` or `~/.bashrc`) to persist it.

---

## Usage

```bash
python3 scripts/butcher_auto.py manifest.json
```

Output lands in `butcher_[name]/` next to the source image — one transparent PNG per asset.

---

## Manifest format

```json
{
  "source": "/path/to/banner.jpg",
  "name": "campaign_name",
  "assets": [
    {
      "name": "background_plate",
      "method": "direct_crop",
      "bbox": {"x_pct": 0, "y_pct": 0, "w_pct": 100, "h_pct": 100}
    },
    {
      "name": "key_visual",
      "method": "transparentor",
      "prompt": "describe the subject to isolate",
      "contrast_bg": "#FF00FF",
      "tolerance": 38,
      "softness": 1.2,
      "model": "google/gemini-2.5-flash-image",
      "bbox": {"x_pct": 0, "y_pct": 0, "w_pct": 45, "h_pct": 100}
    },
    {
      "name": "headline",
      "method": "removebg",
      "bbox": {"x_pct": 55, "y_pct": 15, "w_pct": 35, "h_pct": 20},
      "bg_color": "#1A1A2E",
      "tolerance": 28,
      "softness": 1.0
    },
    {
      "name": "cta_button",
      "method": "removebg",
      "bbox": {"x_pct": 60, "y_pct": 70, "w_pct": 25, "h_pct": 18},
      "bg_color": "#1A1A2E",
      "tolerance": 28,
      "softness": 1.0
    }
  ]
}
```

---

## Methods

| Method | Use for | How |
|--------|---------|-----|
| `direct_crop` | Background plate | Crop region as-is |
| `transparentor` | Key visual, complex product/person | Sends crop to Gemini → isolates subject on contrast bg → removes bg |
| `removebg` | Text, logo, CTA button on flat bg | LAB-based bg removal with known color → exact original pixels |

### Which method to use

- **Key visual** (person, product, illustration) → `transparentor`
- **Text / headline / subtitle** on flat bg → `removebg` + `bg_color`
- **Logo** on flat bg → `removebg` + `bg_color`
- **CTA button** on flat bg → `removebg` + `bg_color`
- **CTA button** on complex/gradient bg → `transparentor`

> Never use `transparentor` for text or logos — Gemini regenerates content and will change letterforms or drop characters. `removebg` gives pixel-perfect results from the original.

---

## `transparentor` options

| Field | Default | Description |
|-------|---------|-------------|
| `model` | `google/gemini-2.5-flash-image` | OpenRouter model |
| `contrast_bg` | `#FF00FF` | Background color for Gemini to render on |
| `tolerance` | `40` | BG removal threshold (higher = more aggressive) |
| `softness` | `1.2` | Edge feathering |
| `bbox` | full image | Source crop sent to Gemini |

API key is read from `OPENROUTER_API_KEY` env var automatically.

## `removebg` options

| Field | Required | Description |
|-------|----------|-------------|
| `bbox` | yes | Crop region |
| `bg_color` | yes | Exact background hex (sample from corners) |
| `tolerance` | 28 | LAB distance threshold |
| `softness` | 1.0 | Edge feathering |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `butcher_auto.py` | Main orchestrator — reads manifest, runs all assets |
| `removebg_pro.py` | Standalone LAB-based background removal |
| `butcher_render.py` | Playwright text/button renderer (legacy, for re-rendering) |
| `psd_butcher.py` | PSD layer extractor — use `--bb` flag for BB production |
| `removebg_service.py` | Local drag-and-drop web service for manual BG removal |
