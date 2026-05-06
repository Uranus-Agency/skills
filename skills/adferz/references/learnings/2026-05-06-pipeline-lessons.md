---
date: 2026-05-06
brands: butcher_icecream_gold, butcher_nobitex_gold, butcher_charm_mashhad, butcher_nobitex_oil
formats: bb-150, bb-468, mid-300x100, rect-300x250
session_type: multi-brand batch (4 brands × 4 formats)
---

# Pipeline lessons — 2026-05-06 batch session

## LESSON 1 — Agents MUST use PNG assets, never CSS text

Sub-agents wrote CSS/HTML text for headlines and brand names instead of provided PNGs.
(`<div id="headline">یه پس‌انداز شیرین!</div>` instead of `<img src="../headline.png">`)

**Rule:** Every campaign copy element (headline, subtitle, brand name, CTA label) MUST be
an `<img src="../asset.png">`. CSS text is only for structural/decorative elements (panel
bg, accent bar, divider). If an asset exists for it, use the asset. No exceptions.

When an element changes from text → img, update the CSS:
```css
#headline, #tagline {
  max-width: 100%;
  height: auto;
  pointer-events: none;
}
```
Without this, a 1090px-wide PNG renders at native size and breaks the layout.

---

## LESSON 2 — Never patch multi-line JS blocks with regex — rewrite from scratch

Python regex with DOTALL flag deleted entire animation sequences when trying to remove
a single block. Result: corrupted scripts with orphan `}, null,` syntax errors.

**Rule:** If a script needs changes, rewrite the whole file cleanly.
Validate with `node --check script.js` — catches parse errors instantly.

---

## LESSON 3 — GSAP CDN can be blocked — always ship gsap.min.js locally for preview

CDN (`cdnjs.cloudflare.com`) was blocked in network. All iframes stuck in loading state.

**Fix:** Download via npm (CDN-independent):
```bash
npm install gsap@3.12.5 --prefix /tmp/gsap-dl
cp /tmp/gsap-dl/node_modules/gsap/dist/gsap.min.js ./gsap.min.js
# then in all index.html: src="../../gsap.min.js"
```

---

## LESSON 4 — Do not change what you don't know

`location.reload()` in `onComplete` is the correct Yektanet production standard.
Do not replace or modify it. Do not suggest alternatives. It is intentional.

**Rule:** If a pattern exists in the adferz skill or in production ad code and you
don't know why it's there — leave it. Ask before changing. The 70+ billboard builds
that shaped these rules exist for reasons not always visible in a single session.
