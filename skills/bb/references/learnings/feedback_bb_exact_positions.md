---
name: BB exact positioning values from production
description: Concrete pixel values and formulas that WORK — extracted from azki, yekjoo, bimebazar, melli-gold, alidino, bime final code
type: feedback
originSessionId: e4e8a028-45c4-4663-ba16-bf3438648669
---
## Production-Verified Positioning Values

### BG Canvas (IDENTICAL across all 6 campaigns)
```css
top: 25px; left: 5px; width: calc(100% - 10px); height: 120px;
border-radius: 12px; overflow: hidden; z-index: 1;
```
5px margin all sides. 25px top = 5px margin + 20px poke-out zone. **NEVER change these.**

### Z-Index Stack (from production)
```
z-index: 50   → Flash overlay
z-index: 30   → Start/gameover screens
z-index: 25   → Logo (top elements)
z-index: 18   → Phone frame
z-index: 15   → Key visuals (characters, products)
z-index: 10   → Copy text, CTAs, icons
z-index: 6    → Progress bars
z-index: 5    → Cards, secondary content
z-index: 1    → BG canvas (animated bg)
```

### Character Poke-Out (Azki pattern)
```css
left: 45px; bottom: 5px; height: 145px; z-index: 10;
/* Pokes from y=0 to y=145, overlaps bg top by 20px */
```

### Phone Frame (Yekjoo pattern)
```css
position: absolute; right: 35px; top: 0px;
width: 115px; height: 240px; border-radius: 24px;
overflow: visible; z-index: 15;
/* height 240px: extends 90px below 150px, clipped by publisher */
```
- iframe scale = `phone_inner_width / 375` = `(115-6)/375 = 0.2907`
- iframe size: `width: 375px; height: 2500px; transform: scale(0.2907); transform-origin: top left`

### CTA Zone
```css
/* Always Zone C: bottom 12-18px from bottom */
bottom: 12px;  /* melli-gold */
bottom: 30px;  /* azki, from bottom edge */
bottom: 8px;   /* standard minimum */
height: 24-28px;
```

### Copy Area (left panel in yekjoo)
```css
position: absolute; top: 35px; left: 15px; width: 220px; z-index: 10;
```

### Flash Effect (exact timing, all campaigns)
```javascript
gsap.fromTo(flash, { opacity: 0 }, {
  opacity: 0.85, duration: 0.08, ease: "power2.in",
  onComplete: () => gsap.to(flash, { opacity: 0, duration: 0.35 })
});
/* 0.08s in = 80ms = human flash perception threshold */
/* 0.35s out = natural fade */
```

### Mirror X Offsets (Azki — from right:15 CSS position)
```javascript
CX = -110    // center copy X (moves copy to billboard center)
CY = 14      // center copy Y
CRX = 155    // character moves right (before flip)
MX = -220    // mirror: right-positioned assets move to left side
```

## Why These Values
- BG canvas 5px margin: prevents border-radius clipping and shadow artifacts at edges
- CRX=155: moves char far enough right to look like it's "turning around"
- MX=-220: right:15 + 220 ≈ 235 = past center to left quadrant at 400px width
- Phone height 240px: makes phone look full-size, publisher clips the overflow below 150px

**How to apply:** Use these exact values as starting points. Only deviate if the brand has a specific layout that forces it.
