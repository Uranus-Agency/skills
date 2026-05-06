---
date: 2026-04-30
brand: matiggold
vertical: finance / luxury / gold-trading
formats: bb-150, bb-468, mid-300x100, rect-300x250
---

# MatigGold campaign — orbital coin orbit + halo pulse + zero-shine

## Treatment selected
**Orbital coin orbit + halo pulse around percent3d + zero-shine pulse**.

## Why brand-fit
- Asset itself dictates: `orbital_rings.png` + `coin1.png` + `coin2.png` literally provided. Treatment IS the asset language.
- Vertical = luxury/finance → premium register (halo, shimmer, gold-glow) over loud register (bolts, drain).
- Hero is `percent_3d.png` (3D metallic green "0%") — zero-shine pulse on it amplifies the offer.

## Anti-bias check (pass)
Last builds in this skill:
- 2026-04-30 azki → tape-cinch
- 2026-04-30 basalam → price-flash + social-proof counter
- 2026-04-30 snappfood → countdown + scooter-arrival
- 2026-04-30 bimebazar → shield + comparison-bars + savings-stamp

Orbital-coin-orbit + halo-pulse + zero-shine is **fresh** — does not appear in last builds.

## Key implementation notes
- **Coin orbit math**: parametric ellipse `(rx=70 ry=26 tilt=-8°)` in bb-150, `(rx=100 ry=32 tilt=-10°)` in rect-300x250. Depth-aware z-index swap (in front of percent3d when `Math.sin(angle) > 0`, behind when negative). Scale 0.7–1.2 from depth.
- **Canvas backdrop**: 22–36 sparkles (count scaled by panel area) with green+gold mix (55% gold), radial gradient `#1e5c30 → #134023 → #061712`. Use `requestAnimationFrame` — kill on `tl.onComplete`.
- **Halo pulse**: CSS class `.haloP` with keyframe animation; toggle on/off via `tl.call(() => el.classList.add/remove('haloP'))`. Don't run as GSAP infinite tween (prefer CSS for sustained loops).
- **Logo TAR**: `logo.png` is a near-transparent white outline → invert filter (`brightness(0) invert(1)`) inside dark pill. Self-backed = TAR option B.

## Coverage curve
- bb-150: 30 → 5 → 60 → 55 → 25 (avg ~33%) ✓ sinusoidal
- rect-300x250: 25 → 5 → 60 → 30 (avg ~30%) ✓ sinusoidal

## Pitfalls dodged thanks to Blueprint phase
- `headline.png` aspect (~6:1) sized as `width:218px` in bb-150 → gives ~36px height; would have collided with discount-code if blueprint hadn't pre-set top:50 vs top:60 separation.
- Coin orbit `cx,cy` matched percent3d midpoint by computing center BEFORE any code; saved at least one revision cycle.
- `bg.html` original is 390×120 fixed canvas; would have iframe-mismatch in rect-300x250 if not adapted to inline canvas per-format with format-specific dimensions.

## Definition of Done — all 5 met
- [x] Blueprint confirmed (auto-proceed per user "خودت یه سناریو بزن")
- [x] Pre-flight 6/6 passed
- [x] Score ≥ 80 (achieved 92–96 across formats)
- [x] 3-publisher TAR check (logo always self-backed; text on panel only when panel is up)
- [x] Loop on `tl.onComplete` (no fixed `setTimeout(reload, …)`)
