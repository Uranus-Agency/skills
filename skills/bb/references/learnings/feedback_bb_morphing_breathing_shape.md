---
name: BB — morphing/breathing shape pattern for multi-scene narratives
description: One shape that morphs geometry between scenes (peaks and valleys of coverage) packs 5-6 scenes into a single visual container without feeling cluttered, while keeping the iframe transparent.
type: feedback
---

## Rule: use one morphing shape across scenes instead of N independent panels

When you need 5-6 distinct scenes across a 30s loop AND the iframe floor must stay transparent, don't build N separate full panels that swap opacity. Build ONE shape and morph its geometry + content across scenes.

**Why:** On the Nobitex signup BB the user wanted a multi-slide narrative (brand intro → BTC live → ETH live → USDT live → gift finale → urgency pill) but also rejected any full-frame panel: the iframe must stay transparent over the publisher's article. Stacking 5 separate panels and cross-fading would create z-index chaos and require each to be transparent enough not to cover the publisher — impossible for readable content. The solution was a single `#rightPanel` that morphs through 5 geometries, with coverage ranging from ~18% (collapse pill) to ~78% (liveBig). Average ~50% keeps the billboard balanced; peaks draw attention, valleys let the empty space breathe.

## Geometry catalog (30s loop, 400×150 iframe)

```
intro pill    ~38%   top:40, right:30, 200×72,   r:26 — scene 1 brand intro
liveBig       ~72%   top:14, right:10, 282×122,  r:18 — BTC/USDT peak scenes
liveMid       ~50%   top:28, right:38, 232×94,   r:22 — ETH valley scene
giftBig       ~78%   top:12, right:12, 270×124,  r:22 — gift finale
collapse      ~18%   top:56, right:82, 156×38,   r:19 — urgency pill before loop
```

Percentages are approximate iframe coverage. The design oscillates peak → valley → peak → valley so coverage never stays high too long.

## How to animate the morph

Each morph is a single `gsap.to('#rightPanel', { top, right, width, height, borderRadius, duration: 0.6-0.85, ease: 'power3.inOut' })`. Interior content uses separate opacity tweens, timed to start after the morph begins (so new content appears into the new geometry, not the old one).

```js
// Example: liveMid → giftBig morph at 22.55s
tl.to('#rightPanel', { top:12, right:12, width:270, height:124, borderRadius:22,
                       duration:0.85, ease:'power3.inOut' }, 22.55);
tl.to('#giftContent', { opacity:1, duration:0.5 }, 23.15);  // +0.6 into the morph
```

`power3.inOut` is the right ease — it accelerates out of the old shape and decelerates into the new one. `back.out` feels springy but overshoots geometry which can bleed past the target position mid-tween.

## Design rules

1. **Never cross 80% coverage.** Above that the panel feels like a full-frame takeover, killing the transparent-iframe promise.
2. **Valleys should drop below 30% coverage** at least twice per loop — that's when the publisher's content behind the ad becomes the star. Valley = the ad "listens."
3. **Each geometry is a named scene** — document the morph sequence in the manifest with notes ("peak coverage ~72% — BTC"). Makes it editable downstream.
4. **Keep `border-radius` dynamic** — small pills read as chips/badges (high radius ratio), wide cards read as content panels (lower radius ratio). Morphing radius reinforces the mode change.
5. **Content blocks must be `position: absolute; inset: 0; flex-centered`** inside the morphing shape, so they auto-adapt to whatever geometry the shape is in. Don't pin content to absolute pixel coords inside the morph.

## Naming / manifest convention

Add a `SHAPES` object in script.js with the 5 geometries as named keys, and reference them in the morph tweens:
```js
const SHAPES = {
  intro:    { top:40, right:30, width:200, height:72,  borderRadius:26 },
  liveBig:  { top:14, right:10, width:282, height:122, borderRadius:18 },
  liveMid:  { top:28, right:38, width:232, height:94,  borderRadius:22 },
  giftBig:  { top:12, right:12, width:270, height:124, borderRadius:22 },
  collapse: { top:56, right:82, width:156, height:38,  borderRadius:19 }
};
tl.to('#rightPanel', { ...SHAPES.liveBig, duration:0.8, ease:'power3.inOut' }, 5.35);
```

Also expose in `manifest.json` as `meta.shapes` so visual editors can expose geometry knobs.

## When NOT to use this pattern

- Single-scene billboards (intro + CTA only). Overkill.
- Video-as-background billboards where the video panel covers 70% and the remaining 30% is product carousel. The 70/30 split pattern is better there.
- Billboards with heavy vector illustrations that anchor to fixed positions (mascots, phone frames). Morphing panel geometry would desync from those.

Use morphing shapes when you have **text-first content that changes per scene** (prices, headlines, countdowns) and need to telegraph scene boundaries without panel cross-fades.
