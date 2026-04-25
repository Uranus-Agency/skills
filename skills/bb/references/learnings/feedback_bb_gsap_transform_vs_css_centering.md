---
name: GSAP transform conflicts with CSS translate centering
description: Never use `top: 50%; transform: translateY(-50%)` (or translateX) for floating elements that GSAP will later animate with `scale`, `rotation`, `x`, or `y`. GSAP overwrites the transform matrix — the centering disappears the moment the first tween runs.
type: feedback
---

**Rule:** For floating hero elements that GSAP will animate with `scale`, `rotation`, `x`, or `y`, do NOT center them using `top: 50%; transform: translateY(-50%)` (or the horizontal equivalent). GSAP writes to the `transform` matrix — it does not merge with a pre-existing CSS `translate`, it replaces it. The element appears to jump or land in the wrong place the instant the first tween fires.

**Why:** GSAP's transform engine reads the current matrix once, then overwrites it on every tween. If your CSS uses `transform: translateY(-50%)` for centering and your GSAP tween sets `scale: 1` or `opacity: 1` (which internally forces a transform update), the centering translate is wiped out and the element snaps to its raw `top` value. Symptoms: "my element was centered, then suddenly jumped up by half its height" or "scaling makes my element drift off-center." Observed in Tabdeal 100x-live-market where `.orbit`, `.big18`, `.coinGridFloat`, `.big100x` all used `translateY(-50%)` centering — when GSAP scale-pulsed them, they drifted.

**How to apply:**

1. **The iframe is always 150px tall — do the math, write absolute `top` values.** `top = (150 - elementHeight) / 2`. Examples:
   - 108px orbit → `top: 21px`
   - 74px coin grid → `top: 38px`
   - 66px big number → `top: 42px`
   - 84px `۱۰۰×` block → `top: 33px`
2. **Same rule horizontally.** If you need `left: 50%` centering, compute `left: (400 - elementWidth) / 2` instead of `transform: translateX(-50%)`.
3. **Exception: elements GSAP never touches.** If the element is purely CSS-animated (keyframes) or never animated at all, CSS `translate` centering is fine. The rule is specifically about elements GSAP will tween.
4. **If you MUST use CSS translate for centering**, use GSAP's `xPercent`/`yPercent` on the same element instead of `x`/`y`, and combine with the CSS translate. But this is fragile — prefer absolute top/left math.
5. **Detect the bug:** element looks centered in DevTools before the timeline starts, then "jumps" to a different Y the moment any tween on that element begins. That's the signature.

### Example: Tabdeal 100x-live-market

Before (broken):
```css
.orbit {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  left: 14px;
  width: 108px;
  height: 108px;
}
```
GSAP tween `gsap.to('.orbit', { scale: 1.05, yoyo: true, repeat: -1 })` wiped the `translateY(-50%)`, orbit drifted to `top: 0`.

After (fixed):
```css
.orbit {
  position: fixed;
  top: 21px;             /* (150 - 108) / 2 */
  left: 14px;
  width: 108px;
  height: 108px;
}
```
Now GSAP can scale/rotate/x/y without destroying the centering.

### Related: xPercent / yPercent
For elements that need to be centered on their own midpoint AND be moved by GSAP (e.g., a floating label anchored to a variable x-position), use GSAP's own percent transforms:
```js
gsap.set('.label', { xPercent: -50, yPercent: -50, left: someX, top: someY });
```
GSAP merges `xPercent` into its own matrix, so this survives subsequent tweens.
