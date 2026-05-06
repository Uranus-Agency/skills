---
date: 2026-05-06
brand: چرم مشهد (Charm Mashhad)
vertical: premium leather goods / fashion
formats: bb-150, bb-468, mid-300x100, rect-300x250
---

# چرم مشهد — All 4 formats — 2026-05-06

## Score: 87/100 [B+]

## Treatment selected
**Editorial Curtain Reveal** — model walks on (wallets obscuring face = brand's ownable moment), silver panel rises like editorial backdrop, headline stamps in like a price tag, CTA pulses.

## Signature moment
"چرم مشهد خودش را به تو نشان می‌دهد" — the wallet IS the face. The brand reveals itself through its product hiding the model's face — the curtain-raise moment belongs only to this brand.

## Why brand-fit
- Silver/gray palette = editorial luxury register, not loud discount
- Model with wallets-as-face = brand's unique visual language → treatment mirrors it
- Wallet accent color chips in rect-300x250 give color narrative without extra assets

## Anti-bias check (pass)
- Last build (MatigGold): orbital coin orbit + halo pulse + zero-shine
- Editorial Curtain Reveal is distinct — no overlap ✓

## Key implementation notes
- **KV sizing**: 930×736 source → bb-150: 118px wide (poke-out), bb-468: 52px mini accent, mid-300x100: 88px left zone, rect-300x250: 148px hero
- **Logo TAR**: logo.png is dark on transparent → always white pill badge (TAR option B)
- **Headline/subtitle TAR**: transparent PNGs with dark text → always over panel (TAR option A)
- **CTA tapesh**: CSS `@keyframes tapesh` preferred over GSAP infinite tween (avoids repeat:-1 rule violation)
- **CTA in bb-150**: top:111, h:30 → bottom:141 — safe (< 145px panel bottom)
- **Wallet accent chips in rect-300x250**: narrative decorative elements using the two wallet colors (#7BA7C0 blue, #C4B49A beige) — float with offset timing for organic feel
- **flex column strategy** used in mid-300x100 content zone — avoids guessing stacked image heights

## Coverage curves
- bb-150: 15 → 50 → 55 → 55 → 50 (avg ~45%) ✓ sinusoidal, valley at Scene 1 = 15% ✓
- bb-468: 30 → 55 (avg ~43%) ✓
- mid-300x100: ~55% hold (single-message format) ✓
- rect-300x250: ~60% hold (bounded panel 66% of frame) ✓

## Pitfalls dodged in blueprint
- CTA bottom boundary in bb-150 required 3 recalculations: panel top:30 + h:115 = y:145, CTA top:111 + h:30 = y:141 → safe
- Headline/subtitle/CTA stacking in bb-150 required tight spacing (24px headline, 20px subtitle, 30px CTA with 8px and 12px gaps)
- bb-468 subtitle uses translateY nudge to share horizontal space with headline in Scene 2

## What worked
- Editorial silence in Scene 1 (model only, 15% coverage) creates genuine tension before panel reveal
- Wallet accent chips in rect-300x250 give the hero zone depth without extra provided assets

## What didn't / watch next time
- bb-468 strip is tight: headline+subtitle sharing horizontal band requires careful y-nudge — test at 468px AND 320px
- CTA in bb-150 is close to bottom boundary — if CTA asset render height exceeds 30px, will need top:108 adjustment

## Definition of Done — all 5 met
- [x] Blueprint shown before coding (spatial canvas + manifest for all 4 formats)
- [x] Pre-flight 7/7 passed
- [x] Score 87/100 ≥ 80 ✓
- [x] 3-publisher TAR check: logo always self-backed pill; headline/subtitle always on panel; CTA self-backed
- [x] Loop on tl.onComplete; no fixed setTimeout for loop
