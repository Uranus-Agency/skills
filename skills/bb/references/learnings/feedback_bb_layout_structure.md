---
name: BB billboard standard layout and structure
description: Exact layout pattern for billboards - split 70/30 layout, slide-up video, drop-in product, logo badge, pill CTA, not full-width video background
type: feedback
---

BB billboards must follow the standard split layout pattern, NOT full-width video backgrounds.

**Why:** User provided reference output showing the correct structure. Full-width video with overlaid elements was wrong. The correct approach is a 70/30 split with structured panels and sequenced entrance animations.

**How to apply:**

**Layout (150px height, mobile-first ~400px width):**
- Right 70%: `videoContainer` — video panel with rounded top corners, slides up from below
- Left 30%: `product` — GIF/image scaled 2.5x, drops in from top (`top: -150px` → `top: 15px`)
- Logo: centered badge above the 70/30 split point, white bg + brand-color border + rounded top corners, slides down from top
- CTA: centered pill button in `rightContainer` (above video area), pulsing `tapesh` animation (scale 1→1.2→1), brand color bg + black border
- Glass overlay: semi-transparent panel behind video for depth
- `--radius: 10px`, `--side-margin: 5px` CSS variables

**Animation sequence (GSAP):**
1. Video slides up (`bottom: -112px` → `0`, 1s) + glass slides up simultaneously
2. Logo fades in + slides to `top: 0` (delay 1s, duration 1s)
3. onComplete: product drops in + headers scale in + CTA fades in

**Required elements:**
- `tags.js` — full Yektanet event system with timer events + postMessage
- `iranyekanx` font from Yektanet CDN
- `30s auto-reload` via setTimeout
- Click tracking: CLICK1=logo, CLICK2=cta, CLICK3=product
- `click_url` query param handler
- Video border: 2px solid brand-color
- Video `object-fit: cover`, `object-position: top`

**Brand color application:**
- Extract primary color from logo (e.g., Bitpin green #4EF09D)
- Apply to: CTA background, video border, logo border, glass gradient
- CTA text: always black
- Logo badge bg: always white
