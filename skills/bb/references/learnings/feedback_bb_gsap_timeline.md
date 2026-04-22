---
name: BB GSAP timeline critical rules
description: Critical GSAP patterns learned from production — fromTo immediateRender, infinite tweens outside timeline, callback chains, single master timeline
type: feedback
---

## GSAP Timeline Rules (learned from Azki billboard)

**Never put `repeat: -1` inside a timeline.** Infinite tweens block timeline completion. Always use `tl.call(function() { gsap.to(..., {repeat: -1}) })` to start infinite animations as separate tweens.

**Why:** The Azki build was stuck for multiple iterations because a CTA pulse tween with `repeat: -1` was added directly to the timeline, preventing `onComplete` from ever firing.

**Always use `immediateRender: false` on `fromTo` in timelines.** Without it, the "from" values get applied at BUILD time, overriding earlier tweens instantly.

**Why:** Assets disappeared at the start because `fromTo` for phase 4b immediately set their values to the "from" state when the master timeline was constructed.

**Use a single master timeline, not async/await or callback chains with separate timelines.** A single `gsap.timeline()` with sequential `.to()` calls is the most reliable pattern. Rebuild it in `onComplete` for looping.

**Why:** Callback chains with separate timelines and `gsap.delayedCall` inside Promises never resolved. The single master timeline pattern (matching melli-gold's approach) worked first try.

**How to apply:**
- Single master timeline per billboard with `onComplete: rebuild`
- `.call()` for infinite tweens, tag firing, and `gsap.set` state changes
- `immediateRender: false` on every `fromTo` that isn't at position 0
- Kill infinite tweens with `.kill()` via `.call()` before the next phase needs that element
