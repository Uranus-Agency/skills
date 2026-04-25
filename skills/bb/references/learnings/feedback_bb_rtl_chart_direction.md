---
name: RTL reverses flex-row order — use direction:ltr for charts and bars
description: In a `<html dir="rtl">` document, `display: flex; flex-direction: row` children render visually right-to-left, which reverses bar charts, progress indicators, and anything that should read LTR (ascending, trending up). Fix by setting `direction: ltr` on that specific container.
type: feedback
---

**Rule:** BB documents are `<html dir="rtl">` for Persian text. But `display: flex; flex-direction: row` inside an RTL document renders children **right-to-left visually**. Any container whose children must read left-to-right (bar charts with ascending heights, progress bars, timelines, arrows pointing "up and to the right") will render backwards and communicate the wrong message. Fix with `direction: ltr` on that specific container — the container flips, the inner children keep their normal order, the Persian text elsewhere stays RTL.

**Why:** In Tabdeal 100x-live-market, scene 4 showed a rising bar chart (6 bars growing taller left-to-right) with an arrow pointing up-right — the classic "market going up" visual. Under RTL, the bars rendered tall-to-short (downward trend) while the arrow still pointed up. The result was an ad that visually said "price dropping" while the text said `۱۰۰×` profit. The user catches this instantly — a contradictory visual is worse than no visual, because it actively mistrains the eye.

**How to apply:**

1. **Any container whose visual order matters directionally, add `direction: ltr`.** Candidates:
   - Bar charts (ascending/descending heights must render in reading order)
   - Progress bars with labels on both ends ("0%" on left, "100%" on right)
   - Timelines with event markers
   - Coin tickers where the order is "newest → oldest" or "top gainer → bottom"
   - Arrows or indicators whose tip direction matters (up-right = bullish)
2. **Don't flip the whole `<html>` to LTR.** Keep RTL on the root for Persian text flow. Only override `direction: ltr` on the specific chart/bar container.
3. **Numerals are safe either way.** Persian/Arabic digits and Latin digits both render LTR intrinsically — the issue is only container-level flex order.
4. **Test by looking at the ad, not the code.** The code can look correct (bar[0]=15%, bar[1]=30%, bar[2]=45%, ...) and still render wrong because RTL reversed the visual placement.

### Example: Tabdeal 100x-live-market scene 4

HTML:
```html
<div class="chartFloat">
  <div class="chartBars">
    <div class="bar" style="height:15%"></div>
    <div class="bar" style="height:28%"></div>
    <div class="bar" style="height:42%"></div>
    <div class="bar" style="height:58%"></div>
    <div class="bar" style="height:76%"></div>
    <div class="bar" style="height:95%"></div>
  </div>
  <div class="arrow">↗</div>
</div>
```

Before (broken): Bars rendered right-to-left → visually descending → arrow pointed up but chart pointed down. User correctly identified this as a contradiction.

Fix (one line):
```css
.chartBars {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  direction: ltr;   /* <-- the fix */
  gap: 3px;
}
```

Now bars render in ascending order left-to-right, matching the arrow.

### Sanity check
Before shipping any BB with directional visuals, squint at it and ask: "If I strip out the text, does the visual alone tell the right story?" If the chart looks like it's going down when it should be going up, RTL ate your direction.
