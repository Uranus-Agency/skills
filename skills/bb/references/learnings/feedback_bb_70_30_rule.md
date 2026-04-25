---
name: The 70/30 rule — floating elements outside the panel
description: At least 30% of the iframe viewport must stay transparent at any instant, and no more than ~70% of the total visible content may live inside a single rectangular panel. Hero elements (big numbers, charts, orbits, product tiles) must float OUTSIDE the morphing panel as `position: fixed` siblings of `body`.
type: feedback
---

**Rule:** No more than ~70% of the visible content may sit inside a single rectangular container. At least 30% of the iframe viewport must remain transparent at every instant. Hero visual elements — big numbers, charts, orbits, logos, product tiles — must float OUTSIDE the morphing panel, not be crammed inside it.

**Why:** When 95% of a scene's content lives inside one rectangle (even if that rectangle is artfully morphed), the ad reads as a single "box with text inside." That's boring and unclickable. The eye has nowhere else to land, there's no sense of depth, and the publisher's article has no room to peek through even though we technically preserved body transparency. The user (Tabdeal project, 2026-04-24) called out: "حاجی نگاه کن تو اکثر اسلایدا ۹۵ درصد اتفاقا در یک آبجکت مسطیلیه! این خوب نیست برای خلاقیت بیلبورد!" — and explicitly renamed this design principle "قانون ۷۰/۳۰" (the 70/30 rule).

**How to apply:**

1. **The morphing panel is an ANCHOR, not a container.** Keep it small (~20–45% coverage) and use it for supporting text (labels, pills, ticker rows, urgency strip). Let it morph shape/position across scenes as the narrative's visual thread.
2. **Put hero elements OUTSIDE the panel.** Big numbers (`۱۸+`, `۱۰۰×`), orbital animations, chart bars, product carousels, badges — these become `position: fixed` siblings of `<body>`, not children of the panel. Each gets a stable `id` and is independently opacity-animated in/out per scene.
3. **Distribute content across zones.** A good scene uses 2–3 separate visual zones (e.g., left-floating chart + right-floating big number + bottom-center panel pill). Never stack everything in one rectangle.
4. **Coverage audit before coding.** Sketch each scene's coverage: panel % + floating element % + CTA %. If the panel alone exceeds ~50%, redesign — shrink the panel and move a hero element outside.
5. **Transparency test.** At any moment in the 30s loop, mentally outline the iframe and ask: "Where can I see through to the publisher's article?" If the answer is "only a thin strip at the edges," you're violating 70/30.
6. **This stacks with the 50% coverage rule.** 70/30 is about *distribution* (don't put everything in one box). The 50% rule is about *time-weighted average* (don't stay heavy too long). Both must hold.

### Example: Tabdeal 100x-live-market

Before (violated 70/30): Panel morphs across 5 scenes, but `۱۸+`, coin grid, `۱۰۰×`, chart bars — ALL inside the panel. 95% coverage in one rectangle per scene.

After (compliant): Panel stays small (~180×72 → 248×104 → 260×28 ribbon → 60×22 mini-pill → 190×58 urgency pill). Hero elements live outside:
- Scene 1: `.orbit` (108×108) fixed `left:14; top:21` on the LEFT, panel on the RIGHT.
- Scene 2: `.liveBadge` floats top-left, ticker panel mid-right.
- Scene 3: `.big18` (huge `۱۸+` gradient) floats right; `.coinGridFloat` (4×2 tiles) floats left; panel shrinks to a bottom ribbon labelled "بازار معاملاتی."
- Scene 4 (peak): `.big100x` (huge `۱۰۰×`) floats right; `.chartFloat` (bars + arrow) floats left; panel shrinks to a tiny "فیوچرز" pill bottom-center; CTA hides.
- Scene 5: panel returns as the urgency pill; CTA returns big and pulsing.

### CSS pattern for floating hero elements

```css
.heroElement {
  position: fixed;          /* sibling of <body>, NOT inside .panel */
  left: 14px;               /* or right: 16px — pick the free side */
  top: 21px;                /* absolute numeric, NOT top:50%+translateY */
  width: ...;
  height: ...;
  z-index: 4;               /* below CTA (99), above panel (5) or independent */
  opacity: 0;               /* GSAP animates to 1 on scene enter */
}
```

**Avoid `top: 50%; transform: translateY(-50%)` for floating elements that GSAP will animate** — GSAP's `scale`/`rotation` tweens overwrite the `transform`, breaking the centering. Instead, compute absolute `top` as `(iframe-height − element-height) / 2`. The iframe is always 150px tall, so math is trivial.

### HTML structure

```html
<body>
  <!-- morphing anchor panel -->
  <div class="panel" id="panel">
    <div class="scene" id="scene1Inner">...</div>
    <div class="scene" id="scene2Inner">...</div>
    ...
  </div>

  <!-- floating hero elements (outside panel, 70/30 rule) -->
  <div class="orbit" id="orbit">...</div>
  <div class="big18" id="big18">...</div>
  <div class="coinGridFloat" id="coinGridFloat">...</div>
  <div class="big100x" id="big100x">...</div>
  <div class="chartFloat" id="chartFloat">...</div>

  <!-- CTA stays fixed -->
  <div class="cta" id="cta">...</div>
</body>
```

### Quick sanity check per scene

Ask two questions:
1. **Can I point to at least two distinct visual zones?** (e.g., "hero element on the left, panel on the right") If everything is in one area, you're violating 70/30.
2. **Is the total opaque area ≤ ~70% of the 400×150 iframe (≤ 42,000 px²)?** If it's higher, one of the zones needs to shrink.
