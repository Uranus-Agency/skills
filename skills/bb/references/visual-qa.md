# BB Visual QA — Post-Build Placement Verification

## Overview

After generating billboard code, BB must **render and visually inspect** the output using Claude Preview tools. This catches placement errors, overlaps, viewport bleeds, and z-index problems that code review alone cannot detect.

---

## QA Workflow (3 Steps)

### Step 1 — Render at Both Viewports

```
1. Start preview server (preview_start "bb-preview")
2. Navigate to the billboard's index.html (preview_eval → window.location.href)
3. Resize to mobile: 375x150
4. Take screenshot
5. Resize to desktop: 1440x150
6. Take screenshot
```

### Step 2 — Inspect All Key Elements

Run this diagnostic script via `preview_eval` to get bounding boxes of all visible elements:

```javascript
(function() {
  const els = document.querySelectorAll('img, video, div, span, a, button, canvas');
  const results = [];
  for (const el of els) {
    const rect = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (rect.width > 0 && rect.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden') {
      results.push({
        tag: el.tagName,
        class: (el.className || '').toString().substring(0, 50),
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        w: Math.round(rect.width),
        h: Math.round(rect.height),
        bottom: Math.round(rect.y + rect.height),
        right: Math.round(rect.x + rect.width),
        zIndex: cs.zIndex,
        position: cs.position,
        opacity: cs.opacity,
        inViewport: rect.y >= -5 && (rect.y + rect.height) <= 155 && rect.x >= -5 && (rect.x + rect.width) <= (window.innerWidth + 5)
      });
    }
  }
  return JSON.stringify(results, null, 2);
})()
```

### Step 3 — Run Checks Against Rules

Evaluate every element against the placement rules below. Report any failures.

---

## Placement Rules (from 70+ Production Billboards)

### Rule 1: Viewport Containment

Every **resting-state** element must be fully inside the 150px viewport.

| Check | Pass condition |
|-------|---------------|
| Top edge | `y >= -5` (5px tolerance for anti-aliasing) |
| Bottom edge | `y + height <= 155` (5px tolerance) |
| Left edge | `x >= -5` |
| Right edge | `x + width <= viewportWidth + 5` |

**Exception:** Intro elements (`.intro`, `.motion`) start off-screen and exit off-screen — they are exempt during animation. Only check their position if they have a resting state.

**Exception:** Elements that intentionally bleed (e.g., spinner-bg extending 15-20px beyond frame for visual effect) — flag but don't fail if the overflow is symmetric and intentional.

### Rule 2: Logo Placement

| Property | Mobile (375px) | Desktop (1440px) |
|----------|---------------|-----------------|
| Position | Top-right quadrant | Top-right quadrant |
| y (top) | 0–15px | 0–15px |
| Height | 30–50px | 30–50px |
| Fully visible | Must not be cropped by viewport edges | Same |
| Not obscured | z-index must be >= content layer z-index | Same |

**Production evidence:**
- Tapsi: logo at y=-1, h=37, x=265 (mobile) / x=1330 (desktop) — always top-right
- Wallex: logo at y=30, h=35, x=28 (left-aligned for this brand) — exception for left-logo layouts
- Technolife: logo at y=0, h=35, x=296 — top-right
- MelliGold: header at y=2, h=50, x=231 — top-right area

### Rule 3: CTA Placement

| Property | Required |
|----------|----------|
| Position | Zone C (y >= 95px, bottom area) |
| Fully visible | Must be within viewport |
| Height | 23–34px |
| Has `.tapesh` class | Must pulse/animate |
| Not overlapped | No element with higher z-index covers it |
| Gap from logo | >= 10px vertical distance |
| Tappable | Not hidden under transparent overlay |

**Production evidence:**
- Tapsi: CTA at y=103, h=23 — Zone C
- Wallex: CTA at y=103, h=29 — Zone C
- Technolife: CTA at y=118, h=25 — Zone C
- MelliGold: CTA at y=103, h=28 — Zone C

**CTA must NEVER be:**
- Above y=90 (too high, competes with content)
- Below y=135 (risks being cut off or under device chrome)
- Narrower than 70px (too small to tap)

### Rule 4: Background Panel

| Property | Required |
|----------|----------|
| Width | 55–75% of viewport (standard) or 95–100% (full-width) |
| Height | 100–140px |
| Position | `right: 0` to `right: var(--side-margin)` for standard; centered for full-width |
| z-index | Negative (behind all content) |
| Bottom-aligned | `bottom: 0` or close |

**Production evidence:**
- Tapsi: bg w=356 (95% of 375), h=122, z=-1
- Wallex: bg w=368 (98% of 375), h=117, z=auto (but behind content)
- Technolife: bg w=365 (97%), h=112, z=-200
- MelliGold: bg w=355 (95%), h=120, z=-999

### Rule 5: No Unintended Overlaps

Check for elements that should NOT overlap:

| Pair | Rule |
|------|------|
| Logo + CTA | Must have >= 10px vertical gap |
| Logo + Overline | Logo above overline, no overlap |
| CTA + Products | CTA z-index > product z-index if they share space |
| Background + Content | Background z-index must be lower than all content |
| Multiple products | Products in carousel should stack at same position (only one visible at a time) |

**How to detect overlap:**
```
Two elements A and B overlap if:
  A.x < B.x + B.width AND
  A.x + A.width > B.x AND
  A.y < B.y + B.height AND
  A.y + A.height > B.y
```

When overlap is detected between non-background elements:
1. Check if one is intentionally behind (lower z-index)
2. Check if one has `opacity: 0` (hidden, part of animation)
3. Check if they're carousel items (expected to stack)
4. If none of the above → **FLAG AS ERROR**

### Rule 6: Z-Index Correctness

Verify the layering order matches the spec:

```
Background (z: -999999 to -100)
  < Logo (z: -1 to 5)
    < Products/Overline (z: 1-9)
      < CTA (z: 99)
        < Stars (z: 9999)
          < Intro (z: 99999)
            < Unmute (z: 99999999)
```

**Common z-index errors:**
- CTA behind product (can't be clicked)
- Logo behind background panel (invisible)
- Intro element at z:1 (gets hidden during animation)

### Rule 7: RTL Layout Integrity

| Check | Expected |
|-------|----------|
| Brand column | Right 30% of viewport |
| Hero column | Left 70% of viewport |
| Logo | Right-aligned (or centered over right panel) |
| CTA | Right-aligned (or centered over right panel) |
| Products | Left-aligned |
| Text direction | Right-to-left |

**Exception:** Full-width layouts (video-as-content, full-bg) may center elements instead.

### Rule 8: Responsive Scaling

Compare mobile (375px) and desktop (1440px) screenshots:

| Element | Mobile behavior | Desktop behavior |
|---------|----------------|-----------------|
| Background | Fills 95-100% width | Fills 95-100% width |
| Logo | Stays in right area | Stays in right area (x scales proportionally) |
| CTA | Stays in Zone C | Stays in Zone C |
| Products | Left area, properly sized | Left area, may appear larger |
| Video | Fills allocated width | Fills allocated width (wider on desktop) |
| Brand column (.right) | ~180-190px wide | ~500-720px wide |

**Key check:** At desktop, verify content doesn't cluster in one corner leaving large empty spaces. The `position:fixed` + percentage widths should distribute content.

### Rule 9: Animation Resting State

After intro animation completes (wait ~12s or eval `gsap.globalTimeline.progress()`):

| Check | Required |
|-------|----------|
| CTA visible and pulsing | `.tapesh` animation active |
| At least one element floating | `.float` animation active |
| All resting elements in viewport | Nothing stuck off-screen |
| No flickering/glitching | Smooth infinite loops |

### Rule 10: Interactive Element Isolation

For billboards with interactive elements (carousel arrows, unmute button, sliders):

| Check | Required |
|-------|----------|
| `stopPropagation()` on interactive elements | Clicking them must NOT trigger click_url redirect |
| Interactive z-index | Higher than surrounding content |
| Touch target size | >= 20x20px |

---

## QA Report Format

After inspection, output a report:

```
## Visual QA Report

### Mobile (375x150)
- [PASS/FAIL] Viewport containment: all elements within bounds
- [PASS/FAIL] Logo: visible at (x, y), size WxH
- [PASS/FAIL] CTA: visible at (x, y), size WxH, in Zone C
- [PASS/FAIL] Background: proper coverage, behind content
- [PASS/FAIL] No unintended overlaps
- [PASS/FAIL] Z-index layers correct
- [PASS/FAIL] RTL layout intact

### Desktop (1440x150)
- [PASS/FAIL] Same checks as mobile
- [PASS/FAIL] Responsive scaling — no clustering, proportional distribution

### Animation
- [PASS/FAIL] CTA tapesh pulsing in resting state
- [PASS/FAIL] Float animation present
- [PASS/FAIL] No elements stuck off-screen after intro

### Issues Found
1. [element] — [problem] — [fix suggestion]
```

---

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| CTA hidden behind product | Product z-index > CTA z-index | Set CTA `z-index: 99` |
| Logo cropped at top | `top: -10px` or negative margin | Set `top: 2px` minimum |
| Element below viewport | `bottom: -20px` with tall element | Raise bottom value or reduce height |
| Products overlap CTA on mobile | Fixed left position too far right at 375px | Use `left: calc()` with percentage |
| Background doesn't reach edges | `width: 70%` with `right: 10px` | Use `width: calc(70% - var(--side-margin))` |
| Empty space on desktop right | Right panel uses fixed px width | Use percentage width for `.right` div |
| Intro never exits on 4K | `right: -400px` start is visible on 3840px screen | Use `right: -650px` minimum |
| CTA not tappable | Transparent overlay on top with higher z-index | Add `pointer-events: none` to overlay |
| Multiple visible carousel items | Missing `opacity: 0` on non-active items | Set all items to `opacity: 0`, active to `opacity: 1` |

---

## Quick Diagnostic Commands

### Check if CTA is tappable (no overlapping elements blocking it)
```javascript
(function() {
  const cta = document.querySelector('.cta, .tapesh, [class*="cta"]');
  if (!cta) return 'NO CTA FOUND';
  const rect = cta.getBoundingClientRect();
  const cx = rect.x + rect.width / 2;
  const cy = rect.y + rect.height / 2;
  const topEl = document.elementFromPoint(cx, cy);
  return {
    ctaClass: cta.className,
    ctaRect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
    topElementAtCenter: topEl ? { tag: topEl.tagName, class: topEl.className } : 'none',
    ctaIsToppable: topEl === cta || cta.contains(topEl)
  };
})()
```

### Check logo-CTA gap
```javascript
(function() {
  const logo = document.querySelector('.logo, .mainLogo, .header, [class*="logo"]');
  const cta = document.querySelector('.cta, .tapesh, [class*="cta"]');
  if (!logo || !cta) return 'MISSING LOGO OR CTA';
  const lr = logo.getBoundingClientRect();
  const cr = cta.getBoundingClientRect();
  const gap = cr.y - (lr.y + lr.height);
  return {
    logoBottom: Math.round(lr.y + lr.height),
    ctaTop: Math.round(cr.y),
    verticalGap: Math.round(gap),
    pass: gap >= 10
  };
})()
```

### Check all elements in viewport
```javascript
(function() {
  const vw = window.innerWidth;
  const fails = [];
  document.querySelectorAll('img, video, div, span, a, button').forEach(el => {
    const rect = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (rect.width > 5 && rect.height > 5 && cs.display !== 'none' && cs.opacity !== '0' && cs.visibility !== 'hidden') {
      const cls = (el.className || '').toString();
      if (cls.includes('intro') || cls.includes('motion')) return; // skip intro elements
      if (rect.y + rect.height < -5 || rect.y > 155 || rect.x + rect.width < -5 || rect.x > vw + 5) {
        fails.push({ class: cls.substring(0, 30), x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) });
      }
    }
  });
  return fails.length === 0 ? 'ALL IN VIEWPORT' : { outOfBounds: fails };
})()
```
