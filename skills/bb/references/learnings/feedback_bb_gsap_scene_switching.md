---
name: BB GSAP Scene Switching
description: Use .call() not timeline .set() for scene opacity toggling in multi-scene billboards
type: feedback
originSessionId: c2a34521-3f69-4cb7-92ff-9c071e329093
---
Never use `timeline.set(sceneEl, {opacity:1}, t)` to show/hide scenes. GSAP timeline `.set()` at a given position competes with standalone `gsap.set()` reset calls and may not apply the inline style (leaving element at CSS default opacity:0).

**Why:** GSAP's instant tween at position 0 with `immediateRender` can conflict with pre-timeline `gsap.set()` calls on the same property. Result: scene stays invisible even though GSAP ran.

**How to apply:** Always toggle scene visibility inside `.call()`:
```js
// ✅ CORRECT
.call(() => { gsap.set(s1, {opacity:0}); gsap.set(s2, {opacity:1}); }, null, 9.55)

// ❌ WRONG — may silently fail
.set(s1, {opacity:0}, 9.55)
.set(s2, {opacity:1}, 9.6)
```

Also combine bgPhase change + scene swap in the same `.call()` for atomic transitions:
```js
.call(() => { gsap.set(s1, {opacity:0}); bgPhase = 2; gsap.set(s2, {opacity:1}); }, null, 9.55)
```
