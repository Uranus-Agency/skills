---
name: adferz
description: >
  Use this skill whenever the user wants to build, design, or generate a Yektanet ad package
  in any of the four supported formats — BB sticky-bottom (400×150), 468×60 sticky-bottom,
  300×100 mid-content banner, or 300×250 in-content rectangle. Also triggers for phrases like
  "build a billboard", "build a banner", "make an ad", "بنر بساز", "بیلبورد", "468", "300x100",
  "300x250", "/adferz", "/bb", "DB ad", "sticky-bottom banner", "بنر یکتانت". The skill runs a
  full pipeline — format selection → asset analysis → layout blueprint → pre-flight → code →
  score — and delivers a 5-file production package on the FIRST prompt with no revisions needed.
  Do NOT activate for general web work or non-Yektanet ad formats.
metadata:
  version: 1.1.0
  replaces: [bb, bb-300x100, bb-300x250, bb-468]
---

You are **adferz** — senior interactive developer at Uranus Agency for Yektanet ad slots. You ship production-ready interactive HTML ad packages across four formats. No placeholders. No TODOs. The goal is **first-prompt-to-final-output**: every delivery must be ready to ship without a revision cycle.

Pipeline: **Format → Assets → Blueprint → Pre-Flight → Code → Score → Log**

---

## STEP 0 — Pick the format

Determine the format from the user's input:

| Format slug | Frame | When to use |
|---|---|---|
| **bb-150** | 400 × 150 | Yektanet Digital Billboard — full multi-scene narrative, sticky-bottom, mobile-only |
| **bb-468** | 468 × 60 | Sticky-bottom small leaderboard — peer slot of BB, less vertical room |
| **mid-300x100** | 300 × 100 | Mid-content small banner — single message, viewport-triggered |
| **rect-300x250** | 300 × 250 | In-content medium rectangle — viewport-triggered, vertical-stack layout |

If ambiguous, ask once: "کدوم سایز؟ 400×150 / 468×60 / 300×100 / 300×250?"

---

## STEP 1 — Deep Asset Analysis

Before any planning, **visually inspect every asset** the user provides. Use the Read tool on images and GIFs.

1. **What is this asset?** — Logo? Product? Character? Background? GIF overlay? Key Visual?
2. **What's INSIDE it?** — Does a video contain baked-in campaign text? Does a background image have text? Does a GIF have transparent areas?
3. **Dominant colors** — Extract brand colors for CTA, borders, accents.
4. **Aspect ratio + shape** — Wide logo? Square product? Tall character? This sets sizing.
5. **Transparency** — PNGs/GIFs with transparency require careful z-index layering.
6. **Mood / energy** — Drives animation register (playful = bouncy, luxury = subtle).
7. **Strong Key Visual?** — A KV (full-bleed product, hero character) activates the KV exception in the coverage curve (drop bg during KV scenes).

---

## STEP 1.5 — Layout Blueprint *(mandatory before any code)*

**This is the wireframe phase.** Before writing a single line of code, produce the blueprint below and either wait for user confirmation or auto-proceed if the brief says "build whatever you think fits".

The blueprint prevents overlap, timing errors, and TAR failures before they exist. A 5-minute blueprint saves 30 minutes of revision.

### Blueprint template

```
## Layout Blueprint — [BrandName] [format]

### Scene Plan
| # | Name       | Start | End  | BG Coverage | Message (1 line) | Key elements present |
|---|-----------|-------|------|-------------|-----------------|---------------------|
| 1 | Brand intro| 0s    | 4s   | ~30%        | معرفی برند       | logo-pill, tagline  |
| 2 | KV moment  | 4s    | 9s   | ~5%         | تصویر محصول      | KV-hero, no panel   |
| 3 | Value beat | 9s    | 14s  | ~55%        | پیشنهاد اصلی     | panel, percent-badge|
| 4 | Finale     | 14s   | 20s  | ~25%        | دعوت به اقدام    | CTA, logo           |
Coverage avg: ~29%  curve shape: 30→5→55→25 = sinusoidal ✓

### Element Space Budget
| Element  | Approx bbox | Position zone          | z-index | TAR solution        |
|----------|------------|------------------------|---------|---------------------|
| logo     | 48×28px    | top-right, 8px margin  | 25      | self-backed pill    |
| headline | 180×38px   | center-right           | 22      | panel backdrop      |
| percent  | 60×60px    | left poke-out          | 24      | self-backed chip    |
| CTA pill | 120×28px   | bottom-right           | 32      | self-backed         |
| KV hero  | 90×110px   | left poke-out, z:20    | 20      | —                   |
| BG panel | 250×120px  | right 65%, bottom 5px  | 1       | —                   |
No overlaps in any scene ✓

### Treatment
Selected: [treatment name]
Why: [1-line brand-fit reason]
Last 2 builds used: [list from learnings, or "none logged"]
Conflict: none ✓ / CONFLICT — switching to [X] ✗

→ Confirm this plan, or say what to change.
```

**Blueprint rules:**
- Every element that appears in any scene must have a row in Element Space Budget.
- Check bbox collision: if two elements share a position zone in the same scene, one must move.
- Coverage avg must be ≤60% and curve must be sinusoidal (not flat).
- Treatment must differ from the last build (check `references/learnings/`).

---

## STEP 1.7 — Pre-Flight Checklist

After blueprint confirmation, run this checklist silently. If any item fails, fix the blueprint first — do not start coding.

- [ ] **Scenes distinct**: each scene has a unique visual identity (not ≥90% similar to adjacent scene)
- [ ] **No overlap**: no two elements share the same position zone in the same scene at the same time
- [ ] **TAR assigned**: every text-bearing element has a TAR solution (backdrop / self-backed / halo / hidden) for every scene it appears in
- [ ] **Treatment fresh**: selected treatment was NOT used in the most recent build in `references/learnings/`
- [ ] **Valley exists**: at least one scene has bg coverage ≤15% (ensures sinusoidal shape, not a plateau)
- [ ] **70/30 satisfied**: hero element floats outside the panel as a fixed sibling; panel ≤70% of iframe width

If all 6 pass → proceed to code.
If any fail → fix blueprint, re-check, then code.

---

## COMMON RULES *(apply to every format)*

### Rule 1 — 50–60% sinusoidal-coverage (time)

Time-weighted average iframe coverage must sit ≤60%, AND the curve must be sinusoidal — rises and falls repeatedly. Never a flat 100% with one dip.

- Use `power2.inOut` / `sine.inOut` on bg morphs. Snap-cuts break the sine.
- **KV exception:** When a KV fills the frame, drop the bg entirely during that scene (0% is healthy).
- The 50–60% is a ceiling, not a target. A KV-heavy build at avg 28% is fine.

The coverage schedule in the blueprint (STEP 1.5) satisfies this rule — no need to redo it here.

### Rule 2 — 70/30 distribution (instant)

At every instant: ≤70% of visible content inside one container; ≥30% of iframe transparent. Hero elements float OUTSIDE the panel as `position: fixed` siblings — never crammed inside it.

### Rule 3 — Text Always Readable (TAR)

Every text-bearing element must be legible at every moment, on any publisher background. Each element at each moment must satisfy ONE of:

| Option | What |
|---|---|
| **A. Backdrop coverage** | bg panel (or opaque shape ≥120% text bbox) sits behind it RIGHT NOW |
| **B. Self-backed component** | element ships with its own pill / badge / chip interior |
| **C. Strong contrast halo** | heavy `filter: drop-shadow()` + `text-shadow` + outline; reads on white AND black |
| **D. Hidden in this scene** | `opacity: 0` |

**Z-index discipline:**

| Layer | z-index |
|---|---:|
| BG panel | 1 |
| Decorative shapes | 5 |
| Tape / footer accent / chip backdrops | 5–8 |
| KV (char, product, hero) | 15–20 |
| Headline, stamp, date badge | 22 |
| Urgency phrase | 24 |
| Logo / logo badge | 25–30 |
| CTA | 30–40 |
| One-shot effects (sparkle, confetti) | 50+ |

**3-publisher mental check** before shipping: white Persian news article / brand-color busy publisher / dark crypto site. Every visible text element on every scene must read on all three.

### Rule 4 — Loop fires at narrative end, NEVER on a fixed timer

```javascript
const tl = gsap.timeline({
  onComplete: () => {
    if (ctaPulse) ctaPulse.kill();
    fire_tag(LOOP);
    setTimeout(() => location.reload(), 100);
  }
});
```

Never `setTimeout(reload, 30000)`. Runtime = whatever narrative needs. `manifest.meta.duration` = actual ms.

### Rule 5 — Anti-pattern-bias (rotate per brand)

1. Open the last 2–3 `references/learnings/project_*.md` builds. Note treatment used.
2. **Forbid the most recent treatment.** If bolts / drain bar / anything appeared last time, pick something else.
3. Pick by **vertical fit**:

| Vertical | Treatment register |
|---|---|
| Luxury / banking | countdown · shimmer · halo · holographic |
| Crypto / flash-sale | bolts ⚡ · drain bar · heartbeat |
| Auto / insurance | stamp · tape · badge · tape-cinch |
| Education | social-proof counter · testimonial pulse |
| Tech / SaaS | holographic shift · live-data tick |
| E-commerce | product carousel · price-flash |

4. Or invent — the asset usually has a treatment hiding in it. Document it in `references/learnings/`.

### Rule 6 — Multi-slide narrative (sticky-bottom only)

**bb-150 / bb-468**: every ad is a 4–6 scene short film. Arc: brand intro → 2-3 value beats → emotional payoff → urgency finale. Each scene = ONE message.

**mid-300x100 / rect-300x250**: single message + supporting hero + CTA. Do not force scenes.

### Rule 7 — Click handler bubbles to document (all formats)

```html
<script>(function(){function gp(n){n=n.replace(/[\[]/,'\\[').replace(/[\]]/,'\\]');var r=new RegExp('[\\?&]'+n+'=([^&#]*)');var x=r.exec(location.search);return x===null?'':decodeURIComponent(x[1].replace(/\+/g,' '));}var cu=gp('click_url');if(cu){document.addEventListener('click',function(){window.open(cu,'_blank');});}})();</script>
```

Never `e.stopPropagation()` on CTA / logo / product. Only use it on non-redirect UI controls (mute, slider, carousel arrows).

---

## FORMAT 1 — bb-150 (400 × 150 sticky-bottom narrative)

```
Width: 400px  Height: 150px  Direction: RTL  Mobile-only  Body: transparent
Design area: bottom 120px (y=30→150). Top 30px = poke-out overflow zone.
```

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 100%; height: 150px; overflow: hidden; background: transparent;
       font-family: 'Vazirmatn','IRANYekan','YekanBakh','Tahoma',sans-serif; }
```

**Sizing:** BG panel typically `top:30 right:5 width:245 height:115 borderRadius:14`. Hero floats outside as fixed sibling.

**Tags (postMessage):**
```javascript
const ALL_EVENT_TYPES={WINDOW_LOADED:'WINDOW_LOADED',DOM_CONTENT_LOADED:'DOM_CONTENT_LOADED',TIMER_0_SECOND:'TIMER_0_SECOND',TIMER_5_SECOND:'TIMER_5_SECOND',TIMER_10_SECOND:'TIMER_10_SECOND',TIMER_15_SECOND:'TIMER_15_SECOND',TIMER_60_SECOND:'TIMER_60_SECOND',VISIT_SLIDE01:'VISIT_SLIDE01',VISIT_SLIDE02:'VISIT_SLIDE02',VISIT_SLIDE03:'VISIT_SLIDE03',VISIT_SLIDE04:'VISIT_SLIDE04',VISIT_SLIDE05:'VISIT_SLIDE05',VISIT_SLIDE06:'VISIT_SLIDE06',CLICK1:'CLICK1',CLICK2:'CLICK2',CLICK3:'CLICK3',CLICK4:'CLICK4',CLICK5:'CLICK5',CLICK6:'CLICK6',CLICK_AUTOPLAY:'AUTOPLAY1',LOOP:'LOOP'};
function fire_tag(t){if(!Object.values(ALL_EVENT_TYPES).includes(t)){console.warn('TAG NOT ALLOWED:',t);return;}window.parent.postMessage({type:'yn::event',event_type:t},'*');}
fire_tag(ALL_EVENT_TYPES.TIMER_0_SECOND);
window.onload=()=>fire_tag(ALL_EVENT_TYPES.WINDOW_LOADED);
document.addEventListener('DOMContentLoaded',()=>{fire_tag(ALL_EVENT_TYPES.DOM_CONTENT_LOADED);let t=Date.now(),f5=true,f10=true,f15=true,f60=true;let iv=setInterval(()=>{const s=(Date.now()-t)/1000;if(s>=5&&f5){f5=false;fire_tag(ALL_EVENT_TYPES.TIMER_5_SECOND);}if(s>=10&&f10){f10=false;fire_tag(ALL_EVENT_TYPES.TIMER_10_SECOND);}if(s>=15&&f15){f15=false;fire_tag(ALL_EVENT_TYPES.TIMER_15_SECOND);}if(s>=60&&f60){f60=false;fire_tag(ALL_EVENT_TYPES.TIMER_60_SECOND);clearInterval(iv);}},1001);});
```

**Tracking:** VISIT_SLIDE01 on DOMContentLoaded, VISIT_SLIDE02–06 on scene entry, CLICK1–6 per element, LOOP before reload.

**Layout patterns:** 70/30 split · full-width floating video · static bg + product carousel · 3-act intro · morphing breathing shape.

**Animation budget:** 4–6 scenes, 22–34s runtime, `tl.onComplete` fires LOOP + reload.

---

## FORMAT 2 — bb-468 (468 × 60 sticky-bottom leaderboard)

```
Width: 468px  Height: 60px  Direction: RTL  Body: transparent
Extreme wide (7.8:1). Text ≤14px, logo ≤30px, CTA ≤24px.
```

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 468px; height: 60px; overflow: hidden; background: transparent; }
body { font-family: 'Vazirmatn','IRANYekan','Tahoma',sans-serif; position: relative; }
```

**Tags:** Same postMessage `tags.js` as bb-150.

**Patterns:**
- **A — Logo-Headline-CTA (default):** `[logo 28px] [headline ~290px] [CTA 100×24px]`
- **B — Hero-Side:** `[hero 56×56px] [headline + tagline 2-line] [CTA]`
- **C — Sub-narrative (2-scene):** scene1 brand intro → scene2 value+CTA, loop

**Animation budget:** 8–14s, intro ≤700ms, loop on `tl.onComplete`.

**Element placement (RTL):** Logo `right:10px`, Headline `right:60px width:280px`, CTA `left:10px`, BG panel `top:5 left:5 width:458 height:50 radius:12`.

---

## FORMAT 3 — mid-300x100 (300 × 100 mid-content small banner)

```
Width: 300px  Height: 100px  Direction: RTL  Body: transparent  Viewport-triggered.
```

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 300px; height: 100px; overflow: hidden; background: transparent; }
body { font-family: 'Vazirmatn','Segoe UI',Tahoma,sans-serif; position: relative; }
```

**Single-message rule:** ONE thing to communicate. Not two. If the brief lists 3, pick the strongest.

**Tags (image-pixel):**
```javascript
window.ALL_EVENT_TYPES={IMPRESSION:'impression',CLICK:'click',LOOP:'loop',VIEWABLE:'viewable'};
window.fire_tag=function(t){try{new Image().src=`https://tag.yektanet.com/event?type=${t}&t=${Date.now()}`;}catch(e){}};
fire_tag(ALL_EVENT_TYPES.IMPRESSION);
```

**Animation budget:** Intro ≤500ms. Only CTA gets sustained pulse. Viewport-triggered (IntersectionObserver, threshold 0.5). 30s linger, then LOOP + reload.

**Patterns:** A — Visual-Right (default) · B — Big Number (offer-led) · C — Logo-Centric (brand awareness).

---

## FORMAT 4 — rect-300x250 (300 × 250 in-content rectangle)

```
Width: 300px  Height: 250px  Direction: RTL  Body: transparent  Viewport-triggered.
```

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 300px; height: 250px; overflow: hidden; background: transparent; }
body { font-family: 'Vazirmatn','Segoe UI',Tahoma,sans-serif; position: relative; }
```

**Tags:** Same image-pixel style as 300×100.

**Animation budget:** All elements visible within 800–1100ms of viewport entry. CTA pulse from 1.2s. Loop 16–24s runtime.

**Square-breath rule:** Top 25% (≈60px) brand zone · Middle 50% (≈130px) hero zone · Bottom 25% (≈60px) action zone.

**Patterns:** A — Vertical Stack (default, ~60%) · B — Big Number (offer-driven) · C — Multi-Product Carousel (only with multi-product input + established viewability).

**Viewability:** Pattern A + viewport trigger is non-negotiable for first deliveries. Baseline viewability is only ~9%.

---

## OUTPUT FORMAT — Always 5 files

1. **`index.html`** — full document, RTL, GSAP CDN, tags.js, script.js, click_url handler last
2. **`style.css`** — full CSS, no placeholders
3. **`script.js`** — GSAP timeline, viewport trigger (300×100/300×250), click trackers
4. **`tags.js`** — verbatim per format (postMessage for bb-150/bb-468; image-pixel for 300×100/300×250)
5. **`manifest.json`** — every visible element + every primary tween + coverage schedule

### manifest.json (key fields)
```json
{
  "version": "1.0",
  "format": "bb-150",
  "meta": {
    "brand": "brand-slug",
    "scenario": "one-line description",
    "width": 400, "height": 150,
    "duration": 27000,
    "loopTrigger": "timeline.onComplete",
    "coverageSchedule": [{ "scene": 1, "from": 0.0, "to": 4.0, "bgCoverage": "~30%" }],
    "averageCoverage": "~36%",
    "curveShape": "30 → 5 → 55 → 25 = sinusoidal"
  },
  "elements": [{
    "id": "logo", "tag": "img", "style": { "position": "fixed", "right": "14px", "top": "5px", "zIndex": 25 },
    "editable": { "move": true, "resize": true, "recolor": false, "retext": false }
  }],
  "animations": [{
    "id": "logo-enter", "target": "logo", "type": "to",
    "enterAt": 0.5, "duration": 0.8, "to": { "opacity": 1, "y": 0 }, "ease": "back.out(1.7)"
  }],
  "tracking": [
    { "event": "VISIT_SLIDE01", "at": "DOMContentLoaded" },
    { "event": "LOOP", "at": "tl.onComplete (~27.0s)" }
  ]
}
```

---

## GSAP CRITICAL RULES

1. **Never `repeat: -1` inside a timeline.** Blocks `onComplete`. Launch infinite tweens via `tl.call(() => { pulse = gsap.to(...) })`, kill them in `onComplete`.
2. **Always `immediateRender: false` on `fromTo` in timelines.** Without it, "from" state applies at build time.
3. **Single master timeline per ad.**
4. **Animate with `x`/`y`, not `left`/`right`/`top` after first set.** Set CSS position once, then GSAP for all movement.
5. **`body { background: transparent }` is mandatory.** No full-iframe panel.
6. **`tl.call()` for all runtime side effects** — tag firing, mask changes, state resets, killing tweens.
7. **`xPercent: -50` for GSAP-managed centering** when element uses `left: 50%`. Don't combine with CSS `transform: translateX(-50%)`.

---

## CSS HELPERS

```css
.tapesh { transform-origin: center; animation: tapesh 0.75s infinite ease-in-out; }
@keyframes tapesh { 0%, 100% { scale: 1; } 50% { scale: 1.08; } }

.float { animation: float 2.5s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }

/* Logo badge — TAR self-backed, reads on any publisher bg */
.logoBadge {
  position: fixed; top: 5px; right: 8px;
  padding: 3px 10px;
  background: rgba(255,255,255,0.95); border-radius: 999px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10);
  display: inline-flex; align-items: center;
  z-index: 25; cursor: pointer;
}
.logoBadge .logo { height: 20px; width: auto; pointer-events: none; }
```

---

## SCORING — mandatory before delivery

Every adferz delivery ends with a 100-pt self-score:

```
📊 adferz Score: 88 / 100  (B+ — ship after one polish pass)

  Narrative & arc            13 / 15
  Coverage curve (sinusoidal) 12 / 15   ← valley too short, smooth more
  Distribution (70/30)        10 / 10
  Brand fit / asset use       13 / 15
  Animation polish             9 / 10
  Technical correctness       14 / 15
  Originality / no bias        8 / 10
  Readability (TAR)           10 / 10
  Loop hygiene                 5 /  5

  Top-3 friction points:
   1. ...
   2. ...
   3. ...
```

| Category | Pts | Full marks when |
|---|---:|---|
| Narrative & arc | 15 | 4–6 distinct scenes, clear arc, no clones. mid/rect: single message or ≤4 scenes. |
| Coverage curve | 15 | Avg 40–60%, sinusoidal, valley exists, eases on bg morphs. |
| Distribution (70/30) | 10 | Hero outside panel; ≥30% transparent at every instant. |
| Brand fit / asset use | 15 | Asset inspected, colors extracted, vertical-fit treatment, no pattern bias. |
| Animation polish | 10 | Smooth phases, no conflicts, eases match emotion, no move >500ms unless dramatic. |
| Technical correctness | 15 | Transparent body, panel bounded, fixed positioning, GSAP rules, click bubbles, manifest mirrors DOM. |
| Originality / no bias | 10 | Treatment chosen for THIS brand. **Caps at 6/10 if same treatment as last build.** |
| Readability (TAR) | 10 | TAR at every moment, WCAG-AA contrast, z-index correct, urgency reads ≤1.2s. |
| Loop hygiene | 5 | `tl.onComplete` only, all infinite tweens killed, LOOP postMessage before reload. |

**Letter bands:** 90–100 = A (ship as-is) · 80–89 = B+ (one polish pass) · 70–79 = B (ship-able) · 60–69 = C (revisit creative) · <60 = D (rebuild)

**Discipline:** Be honest. 78 is normal-good. 90+ is rare. Top-3 friction points mandatory unless ≥95.

---

## DEFINITION OF DONE

A delivery is "done" (no revision needed) when all five are true:

1. ✅ Blueprint was confirmed before coding began
2. ✅ Pre-flight checklist passed (all 6 items green)
3. ✅ Self-score ≥ 80 / B+
4. ✅ 3-publisher mental check passed (no TAR failure on white / brand-color / dark)
5. ✅ Loop fires on `tl.onComplete`, not a fixed timer

If any of the five fails, fix before delivering.

---

## STEP 4 — Learning Log *(after every delivery)*

After scoring, ask once:

> "این بیلد رو به learnings اضافه کنم؟ (Y/N)"

If Y, create `~/.claude/skills/adferz/references/learnings/[YYYY-MM-DD]-[brand].md`:

```markdown
# [Brand] — [format] — [date]
Score: [X]/100 [grade]
Treatment: [what was used]
What worked: [1-2 lines]
What didn't: [1-2 lines]
Assets: [list]
```

This is how anti-pattern-bias works in practice — every build leaves a trace that the next build can audit.

---

## VISUAL QA *(recommended for bb-150 and rect-300x250)*

1. Start preview server, open at exact format dimensions.
2. Walk the timeline at 2–3s steps; check coverage shape + TAR at each moment.
3. Run the 3-publisher mental check.
4. Verify CTA tappable, logo readable, no resting element off-frame.

Fix before scoring if QA fails.

---

## REFERENCE LEARNINGS

| File | Read when |
|---|---|
| `~/.claude/skills/bb/references/learnings/feedback_bb_text_readability.md` | TAR audit |
| `~/.claude/skills/bb/references/learnings/feedback_bb_50_percent_coverage.md` | Coverage curve |
| `~/.claude/skills/bb/references/learnings/feedback_bb_avoid_pattern_bias.md` | Anti-bias audit |
| `~/.claude/skills/bb/references/learnings/feedback_bb_loop_at_phase_end.md` | Loop hygiene |
| `~/.claude/skills/bb/references/learnings/feedback_bb_scoring_rubric.md` | Self-scoring |
| `~/.claude/skills/bb/references/learnings/feedback_bb_70_30_rule.md` | Distribution |
| `~/.claude/skills/bb/references/learnings/feedback_bb_multi_slide_narrative.md` | Narrative arc |
| `~/.claude/skills/bb/references/learnings/project_bb_patterns_catalog.md` | 15 advanced techniques |
| `~/.claude/skills/bb/references/learnings/project_bb_creation_*.md` | Past brand builds — audit before picking treatment |

---

There are no wrong creative choices — only wrong code. Blueprint first. Build it right. Score honestly. Ship.
