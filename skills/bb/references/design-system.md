# BB Design System — Visual Rules & Advanced Techniques

## Zone System (150px Canvas — Design in 120px)

The iframe is 150px, but the **actual design area is 120px** (bottom 120px). Top 30px = overflow zone for بیرون‌زدگی (poke-out effects that grab attention).

```
┌──────────────────────────────────────────────┐ ← top: 0px
│  OVERFLOW ZONE (0–30px): Poke-out elements   │
│  Cards, logos extending above background      │
├──────────────────────────────────────────────┤ ← 30px (design area top)
│  ZONE A (30–60px): Top of bg panel, logos    │
│                                               │
├──────────────────────────────────────────────┤ ← ~60px
│  ZONE B (60–120px): Main visual, hero,       │
│  cards, products, chart                       │
│                                               │
├──────────────────────────────────────────────┤ ← ~120px
│  ZONE C (120–150px): CTA, action bar         │
└──────────────────────────────────────────────┘ ← 150px (bottom)
```

**بیرون‌زدگی (Poke-Out):** Always try to have at least one element extend into the overflow zone (0–30px). This is the most eye-catching technique for billboards — elements poking above the background create depth and draw attention.

### RTL Layout Split (Mobile ~400px width)

```
┌──────────────────────────┬─────────┐
│                          │         │
│   RIGHT 70%              │ LEFT    │
│   videoContainer         │ 30%     │
│   (video/background)     │ product │
│   + logo badge centered  │ /GIF    │
│   + CTA pill centered    │         │
└──────────────────────────┴─────────┘
```

**Right 70%** = video/background panel (videoContainer with rounded top corners, slides up from bottom, brand-color border)
**Left 30%** = product/GIF column (scaled 2.5x, drops in from top)
**Logo** = centered badge above the 70/30 split point (white bg, brand-color border, rounded top corners)
**CTA** = centered pill in rightContainer above video (tapesh pulsing animation)

**Target viewport:** Mobile-only, 390-410px width, 150px height. Never design for desktop widths.

---

## Typography

### Font Stack
```css
font-family: 'Vazirmatn', 'IRANYekan', 'YekanBakh', 'Peyda', 'Tahoma', sans-serif;
```

### Size Guide
| Element | Size | Weight |
|---------|------|--------|
| Main headline | 18–24px | 900 |
| Sub-headline | 13–16px | 700 |
| Badge / number | 28–48px | 900 |
| CTA text | 12–15px | 700 |
| Small labels | 10–12px | 400 |
| Countdown digits | 20–28px | 900 |
| Price display | 16–22px | 700 |

### Font Loading (when using live text)
```css
@font-face {
  font-family: 'Vazirmatn';
  src: url('Vazirmatn-Bold.woff2') format('woff2');
  font-weight: 700;
  font-display: swap;
}
```

**Prefer image assets for Persian text** — live text only when dynamic content is needed (countdown, price, calculator output).

---

## Color System

### CSS Variables Template
```css
:root {
  --primary: /* brand primary color */;
  --secondary: /* brand secondary color */;
  --cta: /* CTA accent color (often contrasting) */;
  --text: /* white or dark, based on background */;
  --bg-dark: /* dark overlay for glass effects */;
}
```

### Color Rules
1. **CTA must contrast** with everything around it — if bg is dark, CTA is bright (and vice versa)
2. **Never gray on gray** — ensure all text/elements have readable contrast
3. **Dark overlays:** `rgba(0,0,0,0.3)` to `rgba(0,0,0,0.6)` for glass effects
4. **Gradient backgrounds:** `linear-gradient(135deg, color1, color2)` or `radial-gradient()`
5. **Brand compliance:** Always match the brand's primary and secondary colors

---

## Background Styles

### Solid Image (most common)
```css
.bg {
  position: fixed;
  right: 0;
  bottom: 0;
  width: 70%;
  height: 120px;
  z-index: -100;
}
```

### Gradient (no image)
```css
.bg {
  position: fixed;
  right: 0;
  bottom: 0;
  width: 70%;
  height: 130px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  z-index: -100;
}
```

### Full-Width Image
```css
.bg {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 150px;
  object-fit: cover;
  z-index: -999999;
}
```

### Video Background
```css
.bg-video {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 60%;
  height: 150px;
  object-fit: cover;
  z-index: -999999;
}
.glass {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 60%;
  height: 150px;
  background: rgba(0,0,0,0.4);
  z-index: -200;
}
```

---

## Animation Timing Reference

| Animation | Duration | Easing | Delay |
|-----------|----------|--------|-------|
| Background scale-up | 0.8s | `power2.out` | — |
| Logo drop-in | 0.6s | `back.out(1.5)` | overlap -0.3s |
| Headline slide-in | 0.7s | `power2.out` | overlap -0.2s |
| Badge bounce-in | 0.8s | `back.out(1.7)` | overlap -0.3s |
| Product slide-in | 0.8s | `power2.out` | overlap -0.2s |
| CTA rise-up | 0.7s | `back.out(1.5)` | overlap -0.3s |
| Curtain open | 1.0–1.2s | `power2.inOut` | 0.5–2s delay |
| Fade in | 0.5–1.0s | `linear` | — |
| Fade out | 0.5s | `linear` | — |
| Intro slide across | 8–11s | `linear` | immediate |
| Fortune wheel fast spin | 0.3s/rotation | `none` | — |
| Fortune wheel slow stop | 2.0s | `power3.out` | — |
| CTA tapesh pulse | 0.75s | `ease-in-out` | infinite |
| Product float bob | 2.5s | `ease-in-out` | infinite |
| Stick hammer wobble | 0.6s | `ease-in-out` | per cycle |
| Stagger (multi-element) | 0.1–0.15s/item | `power2.out` | — |

---

## Advanced Visual Techniques

### Glass Morphism
```css
.glass-panel {
  position: fixed;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
}
```

### Gradient Mesh Background
```css
.mesh-bg {
  background:
    radial-gradient(at 20% 30%, rgba(255,0,100,0.3) 0%, transparent 50%),
    radial-gradient(at 80% 70%, rgba(0,100,255,0.3) 0%, transparent 50%),
    radial-gradient(at 50% 50%, rgba(255,200,0,0.2) 0%, transparent 50%);
}
```

### Particle / Star Field
```css
.star {
  position: fixed;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  z-index: 9999;
  animation: twinkle 2s infinite alternate;
}
@keyframes twinkle {
  0% { opacity: 0.3; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1.2); }
}
```

### LED Ring (for fortune wheel)
```javascript
// Position 16 LEDs in a circle
const LEDS = 16;
const RADIUS = 55;
for (let i = 0; i < LEDS; i++) {
  const angle = (i / LEDS) * 360;
  led.style.transform = `rotate(${angle}deg) translateY(-${RADIUS}px)`;
}
// Alternate flash
setInterval(() => {
  leds.forEach((led, i) => {
    led.style.background = (i % 2 === toggle) ? 'yellow' : 'transparent';
  });
  toggle = !toggle;
}, 500);
```

### Orbital Product Display
```css
.orbit-track {
  position: fixed;
  width: 200px;
  height: 200px;
  animation: orbit-spin 20s linear infinite;
}
.orbit-product {
  position: absolute;
  width: 40px;
  height: 40px;
}
@keyframes orbit-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Clip-Path Reveal
```css
.reveal {
  clip-path: circle(0% at 50% 50%);
  transition: clip-path 1s ease-out;
}
.reveal.active {
  clip-path: circle(100% at 50% 50%);
}
```

### Text Shadow Glow (for live prices, headlines)
```css
.glow-text {
  color: #ffffff;
  text-shadow:
    0 0 6px rgba(255, 255, 255, 0.8),
    0 0 12px rgba(255, 255, 255, 0.6),
    0 0 20px rgba(255, 255, 255, 0.4);
}
```

### Live Indicator Dot (pulsing green/white dot)
```css
.live-indicator {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #4ade80;
  animation: livePulse 0.5s ease-in-out infinite;
}
@keyframes livePulse {
  0% { transform: scale(0.95); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.6; }
}
```

### Thought Bubble Animation (comic-style)
```css
.circle-dot { width: 8px; height: 8px; border-radius: 50%; background: white; }
.circle-medium { width: 15px; height: 15px; border-radius: 50%; background: white; }
.cloud { width: 95%; opacity: 0; will-change: opacity, transform; }
```
```javascript
// Dots appear first (small → medium → cloud)
gsap.to('.circle-dot', { opacity: 1, scale: 1, visibility: 'visible', duration: 0.3, ease: 'back.out(1)' });
gsap.to('.circle-medium', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1)' }, '-=0.1');
gsap.to('.cloud', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1)',
  onComplete: () => gsap.to('.cloud', { y: '-=6', duration: 0.8, yoyo: true, repeat: -1 })
}, '-=0.2');
```

### Centered Full-Width Background (95-98% with rounded top)
```css
.bg {
  position: fixed;
  width: calc(100% - 20px);
  height: 120px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border-radius: 10px;
  z-index: -999;
}
```

### Video Controls Hidden (suppress native controls)
```css
video::-webkit-media { display: none !important; }
video::-webkit-media-panel { display: none !important; }
video::-webkit-media-start-playback-button { display: none !important; }
```

### Noise Texture Overlay
```css
.noise::after {
  content: '';
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 150px;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.05;
  pointer-events: none;
  z-index: 9998;
}
```

---

## Quality Standards

### Must Have
- `dir="rtl"` and `lang="fa"` on `<html>`
- `position: fixed` on ALL elements (never absolute/relative)
- `body { height: 150px; overflow: hidden; }`
- GSAP CDN from `cdn.yektanet.com`
- `tags.js` loaded (provides `fire_tag` and `ALL_EVENT_TYPES`)
- `click_url` handler script before `</body>`
- CTA with `.tapesh` animation class
- Product with `.float` animation (when applicable)
- `fire_tag()` calls on all act transitions and click interactions
- Persian numerals where applicable: `toLocaleString('fa-IR')`
- `location.reload()` after 60s with `LOOP` tag
- `stopPropagation()` on non-redirect interactive elements

### Must NOT
- Use `position: absolute` or `position: relative`
- Add margin or padding to `*` or `body` (beyond reset)
- Use CSS transitions for complex multi-step sequences (use GSAP)
- Forget `stopPropagation()` on carousel controls, sliders, unmute
- Set intro element closer than `right: -650px`
- Overlap CTA and logo (10px+ gap)
- Use English numerals without conversion
- Hardcode click destination URLs
- Place elements below `bottom: 0` unless intentionally bleeding
- Exceed 60s without reload
