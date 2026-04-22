---
name: BB creation log - MatigGold
description: MatigGold billboard - Two-Slide Transition, CSS orbital rings, coin depth simulation
type: project
originSessionId: 3e2644e4-cbd4-47d8-a525-b2cb8c934e6d
---
Brand: MatigGold (ماتی گلد)
Pattern: Two-Slide Transition
Campaign: طلای بدون کارمزد (Gold with no commission fee), deadline 3 Ordibehesht
Key techniques:
- CSS orbital rings: 3 concentric tilted ellipses (rotate(-18deg)) replacing 2D orbital_rings.png
- Coin orbit: GSAP ticker + parametric ellipse math (rx=52, ry=13, tilt=-18deg) for continuous orbit
- Depth simulation: sin(angle) > 0 → z-index:5 (front), < 0 → z-index:1 (back), scale 0.72–1.14
- xPercent/yPercent: -50/-50 on coins to center them on orbit origin before x/y transform
- Slide 1: orbital system centered, headline below
- Slide 2: orbit-wrap moves x=-105, scale=0.84; right panel fades in from right
- Logo poke-out: top:-17px on logo within right-panel (above bg zone at y=25)
- Single orbit-wrap element shared across both slides (moves, not duplicated)
- Server config: added "matig-gold" to .claude/launch.json at port 8783

Learnings:
- The 2D orbital rings PNG can't truly "wrap around" a subject — CSS ellipses with rotate() are the right solution
- Coin orbit on tilted ellipse: parametric + tilt rotation matrix in JS ticker works cleanly
- Parent scale on orbit-wrap naturally scales coin x/y positions (coordinate space scales together)
- gsap.globalTimeline.seek(5) is useful for debugging slide 2 state in preview

Date: 2026-04-21
