---
name: BB background and layout margin rules
description: BG canvas 5px from bottom, design area 120px, poke-out zone from bg top to 150px. HTML bg canvas for animated backgrounds.
type: feedback
---

## Background & Layout Rules (learned from Azki billboard)

**BG canvas position: 5px margin from BOTTOM, not top.** The bg-canvas sits at `top: 25px` (150 - 120 - 5 = 25), `height: 120px`, creating a 5px gap at the bottom and 25px poke-out zone above.

**HTML-based animated backgrounds.** When the client provides a `campaign-bg.html`, extract its CSS (gradients, orbs, animations) and embed directly into the billboard's bg-canvas div. Scale down blur values for the smaller billboard size (e.g., `blur(80px)` → `blur(25px)`).

**Poke-out elements must stay within 0-150px.** Character height should be calculated so: `bottom: 5px` (aligned with bg bottom) + height fills up to y=0 max. For a 120px bg at top:25, a character of ~145px at bottom:5px will poke out exactly to the top.

**Flash overlay must match bg-canvas position.** The flash bang effect div must have the same `top`, `left`, `width`, `height`, and `border-radius` as the bg-canvas.

**How to apply:**
- bg-canvas: `top: 25px; left: 5px; width: calc(100% - 10px); height: 120px; border-radius: 12px`
- Character: `bottom: 5px; height: ~145px` (pokes to top)
- All text assets (copy, CTA, logo): positioned WITHIN bg bounds (between 25px and 145px vertically)
- Flash: exact same dimensions as bg-canvas
- Body: `background: transparent` always
