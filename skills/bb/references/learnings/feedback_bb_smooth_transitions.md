---
name: BB smooth transitions and phase timing
description: Never snap state changes — animate scaleX flips. Overlap bg recovery with character movement. No empty frames between phases.
type: feedback
---

## Smooth Transition Rules (learned from Azki billboard)

**Never use `gsap.set` for visible state changes.** If the user can see the change (like scaleX flipping from 1 to -1), it must be animated with a short tween (0.3-0.4s) using `back.out` easing for natural bounce.

**Why:** The character snap from scaleX:1 to scaleX:-1 after the 360 flip was jarring. Adding `master.to(char, { scaleX: -1, duration: 0.35, ease: "back.out(1.2)" })` made it smooth with a natural overshoot.

**Overlap phase transitions to avoid empty frames.** When bg fades out in one phase and needs to return in the next, start the recovery DURING the current animation (e.g., `-=0.7`). Never leave a gap where bg is dark and no assets are visible.

**Why:** After the character flip, there was a moment with just the character on a nearly invisible bg (opacity 0.12) and no other assets. Starting bg recovery halfway through the flip (`-=0.7`) eliminated the empty/dark frame.

**Asset entrances must overlap with each other.** Use negative position offsets (`-=0.4`, `-=0.5`) so copy, CTA, and logo slide in as a staggered wave, not one after another.

**How to apply:**
- `gsap.set` = only for invisible state resets (opacity:0 elements, off-screen elements)
- Visible transitions = always `gsap.to` with duration 0.3-0.5s
- Phase overlaps: bg recovery starts during character movement
- Asset entrance: staggered with -=0.3 to -=0.5 offsets
- Use `back.out(1.2)` for physical bounce feel on direction changes
