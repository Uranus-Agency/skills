---
name: BB Creation — Nobitex signup (crypto exchange)
description: Multi-scene live-price signup BB with 3 floating coin icons, morphing breathing card, draining-urgency finale. Taught us: no empty scenes, morph coverage oscillation, API cascade, realistic fallbacks, transparent-iframe discipline.
type: project
---

## Project snapshot

**Brand:** Nobitex (بزرگ‌ترین بازار رمزارز ایران — Iran's largest crypto exchange)
**Goal:** Drive signup clicks via live-price teaser + free-gift CTA
**Landing:** https://nobitex.ir/signup/
**Folder:** `Nobitex/nobitex-signup/`
**Shipped:** April 2026

## Final scene structure (30s loop)

| t (s) | Scene | Shape geometry | Content |
|-------|-------|----------------|---------|
| 0 – 5.3 | Brand intro | intro pill (200×72) | Big Nobitex logo + "بزرگ‌ترین بازار رمزارز ایران" tagline |
| 5.3 – 11.5 | BTC live | liveBig (282×122) | BTC name + ▲ change% + big price + lime chart + BTC coin focused |
| 11.5 – 17.5 | ETH live | liveMid (232×94) | ETH name + ▲/▼ change% + price + chart + ETH coin focused |
| 17.5 – 22.4 | USDT live | liveBig (282×122) | USDT name + change% + price + chart + USDT coin focused |
| 22.4 – 26.4 | Gift finale | giftBig (270×124) | "هدیه‌ی ثبت‌نام" headline + confetti + gift box pops in from left |
| 26.4 – 29.9 | Urgency pill | collapse (156×38) | ⚡ فرصت محدود ⚡ + draining progress bar + pulsing CTA |

All 6 scenes use the SAME `#rightPanel` element, morphed via GSAP `to()` tweens on top/right/width/height/borderRadius. Content blocks inside (`#liveContent`, `#giftContent`, `#scene6Content`) cross-fade independently.

## Left side: three floating coins (no panel, no blob)

Three absolutely-positioned coin divs (BTC / ETH / USDT) in a `.coinField` container covering left 140×142px:
- Each coin bobs with its own CSS `@keyframes floatBtc/floatEth/floatUsdt` (3.8s / 4.6s / 4.1s periods — different so they never sync)
- SVGs use `<radialGradient>` for 3D-sphere face + `<linearGradient>` for metallic rim + white ellipse for highlight — looks like physical coins, not flat icons
- Each coin has a `--coin-tint` custom property set by brand (BTC orange, ETH blue/purple, USDT green) that drives the drop-shadow glow AND a `coinPing` radar ring
- When a coin becomes the scene-active one (matching the current price being displayed), GSAP sets `scale: 1.55`, `.active` class lights up the glow + ping ring. Siblings fade to `scale: 0.72, opacity: 0.38`.

This pattern replaced an earlier "blob" design the user rejected. Free-floating elements feel more alive than any single container.

## Key technical patterns

### 1. Morphing shape (see `feedback_bb_morphing_breathing_shape.md`)
Single `#rightPanel` element morphs through 5 named geometries in a `SHAPES` object. Coverage oscillates 38% → 72% → 50% → 72% → 78% → 18% across the loop.

### 2. Live data API cascade (see `feedback_bb_live_data_cascade.md`)
Nobitex API → CoinGecko fallback (with local USDT rate conversion) → hardcoded realistic fallback. Refresh every 12s. Preview sandbox can't reach external APIs so you always see fallback in preview — trust production to hit the live endpoints.

### 3. No empty scenes (see `feedback_bb_no_empty_collapsed_scenes.md`)
The collapsed finale pill MUST carry content. Initial ship had an empty pill and the user caught it immediately. Fixed with ⚡ فرصت محدود ⚡ + draining progress bar.

### 4. Draining urgency bar (RTL)
```css
.urgentFill {
  background: linear-gradient(90deg, #C4FF4D, #A3F000);
  transform-origin: right center;  /* RTL drain: empties left-to-right visually */
}
```
```js
tl.fromTo(urgentFill,
  { scaleX: 1 },
  { scaleX: 0, duration: 2.7, ease: 'none', immediateRender: false },
27.05);
```
`immediateRender: false` is critical — without it the bar starts empty at page load instead of at 27s.

### 5. Transparent iframe discipline
Body + html = `background: transparent`. All visible backgrounds (gradient, grid texture, shine) are INSIDE `#rightPanel` which is bounded (never spans the full 400×150). Empty areas of the frame show the publisher's white article underneath. Three decorative stars + coins float in the transparent zones without covering content.

## Click-tracking assignment

| Event | Target |
|-------|--------|
| CLICK2 | CTA button |
| CLICK3 | rightPanel (the morphing card) |
| CLICK4 | liveContent (live price scenes area) |
| CLICK5 | coinField (floating coins area) |
| CLICK6 | giftBox |

All clicks also bubble to the document-level click_url handler which opens Nobitex signup in a new tab.

## What the user corrected

1. **v1: fake made-up prices** → "قیمتات همش غلطه" → replaced with realistic April 2026 values, then wired API cascade
2. **v1: ugly flat coin icons** → "خیلی غیرخلاقانه‌ست" → rebuilt as 3D gradient spheres with ping rings
3. **v1: empty collapse pill at end** → "یه اسلاید خالی داره اون آخر" → added ⚡ urgency content + draining bar
4. **(earlier) full-frame blob/panel background** → rejected because it violated the transparent-iframe rule → replaced with bounded morphing shape + free-floating coins

## Files

- `index.html` — coinField (3 coins), giftBox, rightPanel (morphing card with 6 content blocks inside), CTA, stars, confetti
- `style.css` — coin 3D gradient SVGs, shape glow/grid/corner decorations, all 6 scene content styles, urgency bar/bolt flash, confetti
- `script.js` — COINS data model + API cascade + refreshLivePrices, SHAPES geometry map, single master timeline building all 6 scenes, coin focus state toggles, tickDot positioning
- `tags.js` — standard Yektanet tracking boilerplate
- `manifest.json` — full design-of-record with all elements, animations, tracking events
- `logo.svg` — brand asset
- Test harness: `/Nobitex/harness-white.html` (docks the iframe over a white Persian article to verify publisher-proof readability)
