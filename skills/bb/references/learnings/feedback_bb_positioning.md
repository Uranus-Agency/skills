---
name: BB positioning and transform rules
description: Use GSAP x/y transforms for animation, not CSS left/right changes. Mirror layout requires negative x. Body bg always transparent.
type: feedback
---

## Positioning Rules (learned from Azki billboard)

**Animate with GSAP `x`/`y` transforms, never animate CSS `left`/`right`/`top` properties.** Set CSS position once, then use `x` offset for all movement.

**Why:** GSAP cannot reliably animate from `left: 50%` to `left: auto`. Multiple iterations were wasted trying CSS property animations. Transform-based movement (x/y) is reliable and composable.

**Mirror layout = negative x offset.** When assets have CSS `right: 15px` and need to appear on the LEFT side, use a large negative `x` value (e.g., `x: -220`). Positive x moves them further right (off-screen).

**Why:** MX was set to +210 initially, pushing assets off-screen to the right instead of mirroring them left. Fixed by using -220.

**Character mirror position = calculate from CSS left.** If character is at `left: 45px` in campaign layout, the mirrored CRX should place it symmetrically: `CRX ≈ billboard_width - char_width - 45 - CSS_left`. Don't just guess large numbers.

**Body background must ALWAYS be `transparent`.** The billboard sits on a publisher's page. Never set a body background color — the bg-canvas provides the visual background.

**How to apply:**
- CSS: set `right`/`left`/`top`/`bottom` once for base position
- GSAP: use only `x`, `y`, `scale`, `opacity`, `rotation` for animation
- Centering in phase 1: use negative `x` offset from CSS position (e.g., CX = -110)
- Mirror: negative x values to flip right-positioned assets to left
- Always `background: transparent` on body
