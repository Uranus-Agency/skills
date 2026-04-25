---
name: BB Creation — Tabdeal 100x Live Market
description: Tabdeal crypto exchange signup BB. 5-scene narrative with morphing anchor panel + 6 floating hero elements (70/30 rule birthplace). Scenes: brand/orbit → live ticker → ۱۸+ coin grid → ۱۰۰× futures chart → urgency finale.
type: project
---

**Brand:** Tabdeal (Iranian crypto exchange)
**Landing:** https://tabdeal.org/auth/register-req
**Folder:** /Users/mehran-pv/Documents/SamurAI/Tabdeal/100x-live-market/
**Goal:** Drive signups by showing a live, high-leverage, broad-market trading experience in 30 seconds.
**Date built:** 2026-04-24

This project is the birthplace of the **70/30 rule** (see `feedback_bb_70_30_rule.md`). First draft had 95% of every scene inside one rectangular morphing panel. User rejected with: "حاجی نگاه کن تو اکثر اسلایدا ۹۵ درصد اتفاقا در یک آبجکت مسطیلیه! این خوب نیست برای خلاقیت بیلبورد!" The rewrite shrank the panel to an anchor and moved hero elements outside as floating fixed siblings.

---

## Scene table (5 scenes, 30s total)

| # | Time window | Panel role | Floating hero elements outside | Coverage | Message |
|---|---|---|---|---|---|
| 1 | 0 – 4.5s | Small right panel (~210×82) with logo + "معامله هوشمند" text | `.orbit` (108×108) left — 8 coins revolving around a core | ~38% | Brand intro |
| 2 | 5 – 10.5s | Ticker panel (248×104) with 3 price rows (BTC/ETH/SOL) | `.liveBadge` floating top-left with pulse dot | ~72% (peak) | Live market is happening |
| 3 | 11 – 16.4s | Narrow bottom ribbon (260×28) labelled "بازار معاملاتی" | `.big18` huge ۱۸+ gradient right + `.coinGridFloat` 4×2 coin tiles left | ~50% | 18+ coin selection |
| 4 | 17 – 23.5s | Tiny "فیوچرز" pill (60×22) bottom-center; CTA HIDES | `.big100x` huge ۱۰۰× "سود کنید" right + `.chartFloat` rising bars + ↗ arrow left + sparkles burst | ~78% (peak) | 100× leverage futures |
| 5 | 24 – 30s | Urgency pill (190×58) center — ⚡ فرصت محدود ⚡ + draining bar | — | ~45% | Finale + BIG pulsing CTA |

Time-weighted average coverage ≈ 52% ✓ (satisfies 50% rule).

---

## 70/30 distribution enforcement

**The panel is the ANCHOR, not the container.** Across all 5 scenes, panel coverage alone never exceeds ~45%. Hero content lives outside as `position: fixed` siblings of `<body>`, independently opacity-animated per scene.

SHAPES (geometry morph):
```js
const SHAPES = {
  scene1: { top: 12,  right: 14,  width: 210, height: 82,  borderRadius: 14 },
  scene2: { top: 6,   right: 10,  width: 248, height: 104, borderRadius: 14 },
  scene3: { top: 118, right: 70,  width: 260, height: 28,  borderRadius: 14 },
  scene4: { top: 120, right: 170, width: 60,  height: 22,  borderRadius: 12 },
  scene5: { top: 42,  right: 105, width: 190, height: 58,  borderRadius: 29 }
};
```

Scene 4 is the peak-peak: the panel shrinks to a 60×22 pill, CTA hides, and the frame is owned by the floating `۱۰۰×` + chart — maximum visual drama with the iframe still showing 22% breathing room.

---

## Floating hero elements (the "outside" half of 70/30)

All with `position: fixed`, absolute numeric `top` (NOT `translateY(-50%)` — see `feedback_bb_gsap_transform_vs_css_centering.md`).

| id | Size | Position | Scene(s) | Animation |
|---|---|---|---|---|
| `orbit` | 108×108 | `left:14; top:21` | 1 | GSAP 360° loop 8s + per-coin counter-rotation |
| `liveBadge` | ~74×22 | `left:14; top:12` | 2 | Fade+drop; pulse dot via CSS keyframes |
| `big18` | ~92×66 | `right:16; top:38` | 3 | Scale-in back.out + counter 0→18 + bump |
| `coinGridFloat` | ~152×74 | `left:12; top:38` | 3 | Tiles stagger pop + sine float loop |
| `big100x` | ~112×84 | `right:14; top:33` | 4 | Back.out scale+rotate + shake + beat |
| `chartFloat` | ~136×78 | `left:14; top:34` | 4 | Bars scaleY stagger + arrow back.out + sparkle burst |
| `cta` | standard | `bottom; center` | 1,2,3,5 (HIDE in 4) | Idle pulse → big 1.32× peak pulse in scene 5 |

---

## Key design decisions

1. **Scene 4 hides the CTA.** Counter-intuitive but correct: peak drama needs the `۱۰۰×` + chart to own the frame. CTA returns in scene 5 at scale 1.18 with peak pulse 1.32 — that contrast is the conversion trigger.
2. **Panel glow color shifts per scene.** Default amber → green in scene 4 (profit) → back to amber in scene 5 (urgency). Tweened on `panelGlow.background` radial-gradient color.
3. **Panel sheen** runs continuously (2.8s sweep, 2.5s repeatDelay) — subtle light strip across the panel.
4. **Chart bars use `direction: ltr`** to escape RTL flex reversal (see `feedback_bb_rtl_chart_direction.md`). Without this fix, ascending heights render descending — arrow pointed up but chart pointed down.
5. **Live price sim runs on 700ms interval** during scene 2 only (`startPriceSim` at 6.0s, `stopPriceSim` at scene 2 exit). Prices random-walk around anchors: BTC 102450, ETH 3845, SOL 245.2. Color flash green/red on tick.
6. **Counter tweens** (0→18 for big18, scale beat for big100x) — small details that make the numbers feel alive.
7. **Scene 5 draining bar** uses `transform-origin: right center` (RTL-correct drain direction) with `scaleX: 1 → 0` over 5.2s.

---

## Tracking assignment

| Event | Trigger |
|---|---|
| VISIT_SLIDE01 | DOMContentLoaded (fire_tag at top of IIFE) |
| VISIT_SLIDE02 | 5.0s (after panel morphs to scene 2) |
| VISIT_SLIDE03 | 11.0s |
| VISIT_SLIDE04 | 17.0s |
| VISIT_SLIDE05 | 24.0s |
| CLICK2 | cta click |
| CLICK3 | logoHero click |
| CLICK6 | panel click (except cta/logoHero descendants) |
| LOOP | 30.0s via setTimeout, before location.reload() |

Click handler at bottom of body intercepts document clicks and opens `?click_url=` in `_blank`. No `stopPropagation` anywhere.

---

## Corrections from user during this build

1. **70/30 rule (the big one)** — first draft crammed everything inside morphing panels. User renamed the fix "قانون ۷۰/۳۰" and promoted it to a first principle in SKILL.md.
2. **LiveBadge overlapped ticker** — originally at `top:6 right:16` which collided with "بیت‌کوین" row. Moved to left zone `top:12 left:14` with blur backdrop.
3. **RTL reversed chart bars** — bars rendered tall-to-short (contradicting the up-arrow). Fixed with `direction: ltr` on `.chartBars`.
4. **GSAP scale wiped CSS centering** — `translateY(-50%)` on floating elements broke the moment any scale tween ran. Switched all floating elements to absolute numeric `top` math `(150 - height) / 2`.

---

## File inventory

- `index.html` — panel with 5 scene inners + 6 floating hero blocks + 5 sparkles + CTA
- `style.css` — SHAPES-agnostic styles; `.chartBars { direction: ltr }`; inline SVG crypto icons
- `script.js` — single master timeline (30s), SHAPES morph, scene entry/exit, live price sim, click tracking
- `manifest.json` — 16 elements, 40 animations, full tracking map
- Assets: Tabdeal logo PNG (inlined as data or standard img), no video, no GIF — all visuals are SVG/CSS/GSAP
