---
name: BB Creation — Yekjoo 5-Campaign Suite
description: Full production workflow for yekjoo.ir campaign billboards — PSD extraction, animated bg.html per campaign, two-phase timeline with phone frame
type: project
---

## Project: Yekjoo 5-Campaign Billboard Suite

### Campaigns & URLs
| Campaign | Folder | URL | Key Visual | Colors |
|----------|--------|-----|-----------|--------|
| chatbot  | `BB/yekjoo/chatbot/` | `/chat` | ai.png | Purple `#2E0880→#9B35FF` |
| markets  | `BB/yekjoo/markets/` | `/markets` | market.png | Gold `#B87600→#FFD700` |
| referral | `BB/yekjoo/referral/` | `/` | socials.png | Green `#127000→#42D400` |
| shorts   | `BB/yekjoo/shorts/` | `/shorts` | short.png | Red `#7A0000→#EE0000` |
| websites | `BB/yekjoo/websites/` | `/websites` | web.png | Blue `#002299→#0068FF` |

### PSD Source → Billboard Coordinate Mapping
PSD canvas: 1500×600px → BB bg card: 380×120px at offset (left:5, top:25)
```
scaleX = 380/1500 = 0.2533
scaleY = 120/600  = 0.2
billboard_left = psd_left × 0.2533 + 5
billboard_top  = psd_top × 0.2 + 25
display_width  = psd_width × 0.2533
```
Assets extracted via `psd_butcher.py` (in `.claude/skills/butcher/scripts/`).

### bg.html Structure (per campaign)
Each bg.html is a 390×120px canvas animation:
- CSS: radial gradient base, 3 glow orbs (CSS animated), circuit grid, shimmer sweep
- Canvas: 60-90 particles/nodes with campaign-specific motion (neural nodes, physics coins, fire particles, etc.)
- Text readability overlay at `left:155px` (right side only, z-index:8)

### Phase 1 Assets (PNG text from PSD, exact positions)
```html
<img id="headline" class="txt" src="[headline].png" style="left:176px;top:54px;width:188px;">
<img id="subtitle" class="txt" src="[subtitle].png" style="left:176px;top:81px;width:187px;">
<div id="ctaWrap" class="cta-wrap" style="left:[X]px;top:99px;">
  <img class="yj-label" id="yjLabel" src="yeklogo.png">  <!-- logo, hidden in Phase 1 -->
  <img class="cta-rect" src="[rect].png" style="width:[W]px;">
  <img class="cta-txt" src="[label].png" style="width:[w]px;">
</div>
```
Headline top:54, subtitle top:81 (8px gap gives readable spacing).

### Phase 2: Phone + CTA + Logo (see feedback_bb_phase2_phone.md)
- bg left 35% fades via CSS mask (see feedback_bb_mask_transparency.md)
- phone frame enters from left: `left:5px; top:5px; width:130px; height:258px`
- ctaWrap moves to center: `left:262, xPercent:-50`
- yjLabel (logo) appears above ctaWrap: `xPercent:-50` via GSAP only

### Tags
```javascript
fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01); // Phase 1 start
fire_tag(ALL_EVENT_TYPES.LOOP);          // Phase 2 exit / loop
```

### Files per campaign
- `index.html` — main billboard
- `bg.html` — canvas animated background (390×120px)
- `[key].png` — product key visual (poke-out)
- `[0X]_*.png` — PSD-extracted text assets
- `yeklogo.png` — yekjoo brand mark (shared across all)
- `tags.js` — yektanet event tracking
