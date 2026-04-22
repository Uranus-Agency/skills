---
name: BB creation log - Melligold Billboard
description: Melligold gold trading platform — interactive prediction slide + live price + carousel with bg kills + shatter CTA
type: project
originSessionId: 4baa6c70-9d05-4396-b1e4-b903379b70c7
---
Brand: Melligold (Persian gold trading platform)
Pattern: Interactive Slide 0 → Card Carousel → Expand All → CTA Shatter → Reload
Campaign: پیشبینی روند قیمت طلا (صعودی / نزولی) + کارت‌های محصول

Path: C:\Users\m.khorshidsavar\Desktop\melli\final melli

---

## Slide 0 — Interactive Prediction

- Transparent bg (no video), full-screen dark overlay removed — orbs only
- Live gold price in price box — WebSocket from wss://cryptian.com/ws (market: goldirr)
- Price formula: `Math.round(bid_price * 100).toLocaleString("fa-IR") + " تومان"`
- Question: "روند قیمت طلا چیه؟" — dark pill backdrop (rgba(8,3,0,0.65) + gold border)
- Buttons: "↑ صعودی" (green) / "↓ نزولی" (red) — both trigger carousel + open click_url
- 10s auto-timer → transitionToCarousel(null)
- Golden orb system: 12 .ray divs, radial-gradient circles, 65% sparkle / 35% bokeh drift, NO mix-blend-mode
- Canvas bg inside #priceBox (initPriceBoxCanvas): shimmer sweep + breathing radial glow + 14 dust particles
- Canvas bg inside #priceBadge (initBadgeCanvas): shimmer sweep + 7 dust particles, bottom glow

---

## Live Price Badge

- Persistent across all carousel slides, disappears in CTA phase
- Position: `position:fixed; top:6px; left:14px` — above left card ("بخر")
- LIVE pill: `position:absolute; bottom:-9px; left:8px` — pokes out BELOW badge
- Canvas animated bg (dark gold gradient + shimmer + dust)
- Badge overflow:visible (so LIVE pill shows below), canvas has border-radius:6px
- Entrance: drops in from y:-14 with back.out(1.8) ease after transition
- Exit: fades out in ctaTakeover with cards

---

## Transition: Slide 0 → Carousel

- slide0 fades out (opacity→0, y→-20, 0.4s)
- videoWrapper opens: scaleX:0→1 (0.65s, power2.out, delay 0.25s)
- Badge drops in: fromTo opacity/y/scale with back.out(1.8), delay 0.35s
- Entrance timeline (delay 0.55s): rightCard → centerCards[0] → leftCard → cta
- Canvas pixel dims resized to actual badge size in badge onComplete

---

## Carousel — Slide Logic

- C1 (currentSlide=0): video bg visible
- C1→C2 (currentSlide becomes 1): BG_KILL fires, bg stays DEAD (no revive)
- C2→C3 (currentSlide becomes 2): no bg animation, just card swap (bg already hidden)
- 6 cycling BG_KILL styles: scaleX / scaleY / scale+opacity / slide left / slide right / blink

### BG_KILLS array
```javascript
var BG_KILLS = [
  { kill:{scaleX:0, duration:0.2, ease:"power3.in"}, revive:{scaleX:1, duration:0.3, ease:"power2.out"}, clean:{scaleX:1} },
  { kill:{scaleY:0, ...}, revive:{scaleY:1, ...}, clean:{scaleY:1} },
  { kill:{scale:0, opacity:0, ...}, revive:{scale:1, opacity:1, ...}, clean:{scale:1,opacity:1} },
  { kill:{x:-450, ...}, revive:{x:0, ...}, clean:{x:0} },
  { kill:{x:450, ...}, revive:{x:0, ...}, clean:{x:0} },
  { kill:{opacity:0, duration:0.08}, revive:{opacity:1, duration:0.12}, clean:{opacity:1} },
];
```
Only used on C1→C2. C2→C3 has no bg kill.

---

## Expand Phase

- All 3 center cards spread: c0 at x:70, c1 center, c2 at x:-70
- rightCard x:+40, leftCard x:-40
- Hold 2s → onDone

---

## CTA Takeover + Shatter + End

Order:
1. bg restored: set scaleX/Y/scale/x, to opacity:1 (0.5s) — bg comes back BEFORE explosion
2. Cards exit (y:-40, stagger 0.05), sides fade, badge fades
3. CTA moves to center (bottom:"50%", height:40, back.out(1.4))
4. shatterBg() — 4×3 grid DOM pieces jitter then implode to center
5. CTA pulses ×3 (scale 1→1.25→1, yoyo, repeat:3)
6. CTA fades out (opacity→0, scale→0.8, y→-10, 0.45s)
7. onDone → fire_tag(LOOP) → location.reload()

### shatterBg()
- Creates 4×3 fixed-position divs over video-wrapper area
- Dark green gradient pieces (matches bg color)
- Phase 1: jitter (0.06s each, stagger 0.01) — crack effect
- Phase 2: implode to center (x/y toward cx,cy × 0.85, scale→0, rotation, 0.32s)
- videoWrapper opacity→0 at start, NOT restored (shatter owns it)

---

## Loop

- One full loop ~28–29s (includes 10s slide 0)
- After ctaTakeover: fire_tag(LOOP) + location.reload() — NO resetAll phase
- Safety fallback: setTimeout reload at 90s

---

## Tags (tags.js events used)
- CLICK1: btnUp (صعودی)
- CLICK2: btnDown (نزولی)
- CLICK3: rightCard
- CLICK4: cta
- CLICK5: leftCard
- CLICK6: centerCards
- VISIT_SLIDE01: carousel start + first cycle
- VISIT_SLIDE02: cycle to C2
- VISIT_SLIDE03: cycle to C3
- LOOP: on reload

---

## Key Learnings

- No mix-blend-mode on orbs — washes out on non-black backgrounds; use solid radial-gradient opacity
- Badge starting opacity:0 — gsap.set() in init, CSS alone unreliable (cache issues)
- Canvas inside badge/priceBox: remove background CSS, add overflow:hidden (or visible if pill pokes out), z-index:0 on canvas, z-index:1 on text
- LIVE pill below badge uses overflow:visible on parent + bottom:-9px positioning
- bg kill only on C1→C2; C2/C3 are deliberately bgless — client choice
- stopPropagation removed from all elements — click_url must bubble freely
- Bg restored at START of ctaTakeover (not end of expand) for cleaner visual sequence

Date: 2026-04-21
