# BB Frame Specification — Complete Technical Reference

## Viewport

- **Height:** 150px (fixed, never changes)
- **Width:** 100% of parent iframe
- **Position:** Sticky bottom of publisher page
- **Container:** Yektanet-managed iframe
- **Direction:** RTL (right-to-left, Persian default)
- **Language:** `fa` (Farsi)

## Coordinate System

- **Origin:** Bottom-left corner of the 150px frame
- **Y-axis:** `bottom: 0` = bottom edge; `top: 0` = top edge (150px from bottom)
- **X-axis (RTL):** `right: 0` = visual right edge; `left: 0` = visual left edge
- All positions use `position: fixed` — this is mandatory for every element

## Body Rules

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  width: 100%;
  height: 150px;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
```

**Never add scrolling, padding, or margin to body.**

## HTML Boilerplate

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>

  <!-- All visual elements go here -->
  <!-- Each element: position:fixed, z-index from layer map -->

  <!-- Scripts in this exact order -->
  <script src="https://cdn.yektanet.com/assets/3rdparty/gsap@3.12.5/gsap.min.js"></script>
  <script src="tags.js"></script>
  <script src="script.js"></script>

  <!-- Click URL handler — ALWAYS last before </body> -->
  <script>(function(){function gp(n){n=n.replace(/[\[]/,'\\[').replace(/[\]]/,'\\]');var r=new RegExp('[\\?&]'+n+'=([^&#]*)');var x=r.exec(location.search);return x===null?'':decodeURIComponent(x[1].replace(/\+/g,' '));}var cu=gp('click_url');if(cu){document.addEventListener('click',function(){window.open(cu,'_blank');});}})();</script>
</body>
</html>
```

## Script Loading Order

1. **GSAP** — `https://cdn.yektanet.com/assets/3rdparty/gsap@3.12.5/gsap.min.js`
2. **tags.js** — event tracking (provides `fire_tag()` and `ALL_EVENT_TYPES`)
3. **script.js** — main animation and interaction logic
4. **click_url handler** — inline script, always last

## Optional CDN Libraries

When needed by the scenario:

- **Chart.js:** `https://cdn.jsdelivr.net/npm/chart.js`
- **Lottie Web:** `https://cdn.jsdelivr.net/npm/lottie-web@5/build/player/lottie.min.js`
- **Model Viewer:** `https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js`
- **Custom Fonts:** Use `@font-face` in style.css with relative paths

## Click URL Mechanism

Yektanet appends `?click_url=ENCODED_URL` to the ad iframe's URL at serve time. The click handler script:
1. Parses `click_url` from the query string
2. Attaches a document-level click listener
3. Opens the URL in `_blank` on any click

**Never hardcode destination URLs.** The click_url is dynamic per impression.

For elements that should NOT trigger the redirect (sliders, unmute, carousel arrows), use:
```javascript
element.addEventListener('click', (e) => {
  e.stopPropagation(); // prevents click_url redirect
  // handle the interaction
});
```

## Auto-Reload Loop

Every billboard must reload after 60 seconds:
```javascript
setTimeout(() => {
  fire_tag(ALL_EVENT_TYPES.LOOP);
  location.reload();
}, 60000);
```

This fires the `LOOP` tracking event just before reload, allowing Yektanet to count ad loops.

## Responsive Behavior

- **Mobile (375px):** All elements must be visible and not overlapping
- **Tablet (768px):** Layout should scale gracefully
- **Desktop (1440px+):** Intro elements must start far enough off-screen (`right: -650px` minimum)
- **4K (3840px):** Intro at `-650px` still works because it slides to `right: 105%`

Use percentage-based positioning where possible. Use `calc()` for panel-relative elements.

## File Size Targets

- **index.html:** < 5KB
- **style.css:** < 3KB
- **script.js:** < 5KB
- **tags.js:** ~1KB (fixed)
- **Total assets (images + video):** < 300KB recommended, < 500KB max
- **Individual images:** < 50KB each (optimize PNG/WebP)
- **Video:** < 200KB, max 10s loop, compressed MP4
