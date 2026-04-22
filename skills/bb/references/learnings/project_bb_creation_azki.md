---
name: BB creation log - Azki
description: Azki insurance billboard - multi-phase flip/mirror pattern with HTML animated background
type: project
---

Brand: Azki (insurance)
Pattern: Multi-phase with character 360 flip + mirrored layout
Key techniques:
- HTML animated background (orbs with blur + sweep) embedded from campaign-bg.html
- 6-phase master GSAP timeline: pulsing copy → campaign layout → flash vanish → 360 flip → mirrored layout → return
- Character poke-out (145px height above 120px bg)
- Smooth scaleX flip transition with back.out easing
- BG recovery overlapped with character flip to avoid empty frames
- Transform-based positioning (x/y offsets from CSS positions)
- Mirror layout using negative x values for right-positioned assets

Learnings:
- repeat:-1 in timeline blocks completion (spent multiple iterations)
- fromTo immediateRender overwrites initial state at build time
- async/await with GSAP doesn't work reliably — use single master timeline
- Positive x on right-positioned elements pushes them OFF screen (need negative for mirror)
- gsap.set for visible scaleX change causes jarring snap — must animate
- BG fade + flip must overlap to prevent dark empty frames
- Body bg must always be transparent (billboard sits on publisher page)

Date: 2026-04-07
