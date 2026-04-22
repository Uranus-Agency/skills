---
name: BB creation log - INVI Gift Campaign
description: INVI gold brand gift promo billboard — live WebSocket price + INVI5 code spotlight, gold particle bg
type: project
originSessionId: c2a34521-3f69-4cb7-92ff-9c071e329093
---
Brand: INVI (Persian gold trading app)
Pattern: Multi-phase with spotlight (intro → INVI5 zoom → restore → loop)
Campaign: 5 سوت طلا هدیه اولین خرید با کد INVI5

Key techniques:
- Live WebSocket price from wss://cryptian.com/ws (goldirr market) — carried over from source billboard
- Gold coin poke-out element (CSS circle, no PNG) — positioned left:calc(50%-22px) to avoid GSAP transform conflict
- All copy as HTML/CSS text (no copy PNGs provided)
- Two-phase timeline: intro (0-9.5s) + INVI5 spotlight (9.5-14s) + restore (14-21.5s) + hold → loop
- bg.html: canvas particle system — 60 gold dust particles rising on dark green gradient, pulsing radial glow, shimmer band
- CTA tapesh: gsap.to via .call() — NOT in timeline (avoid repeat:-1 in timeline)
- Coin uses left:calc(50%-22px) NOT transform:translateX(-50%) — avoids GSAP transform overwrite
- Spotlight: scale codeChip 1.85×, flash overlay rgba(255,210,0,0.18), coin rotation shiver

Brand colors: #006756 (forest green), #81EBA4 (mint), #FFE000 (gold), #FAFFFE (white)
Fonts: Peyda-Regular.woff, IRANSans_FaNum_.woff

Learnings:
- When centering a poke-out element, use left:calc(50% - halfWidth) instead of left:50%+transform — GSAP overrides transform
- No-copy-PNG campaign works cleanly with styled HTML elements
- Gold particle canvas bg creates premium feel, very appropriate for gold trading brand
- Live API active immediately on load — billboard feels alive even before animation completes

3-Scene v2 (final):
- Scene 1: Gift — dark vignette right side makes INVI5 chip pop; "لمس برای کپی" hint; clipboard copy via navigator.clipboard, NO stopPropagation
- Scene 2: Live price + gram calc; calc +/- use stopPropagation; neon-orbit CSS animation on buttons
- Scene 3: Combined — logo poke-out centered (left:calc(50%-42px)), vertical gradient divider, left gift + right price
- bg.html eliminated — canvas inlined into index.html, CSS in style.css, JS as initBgCanvas() in script.js
- bgPhase global (1/2/3) drives particle color + vignette zones per scene
- Scene switching: use .call(()=>gsap.set(scene,{opacity})) NOT timeline.set() — see feedback_bb_gsap_scene_switching.md

Date: 2026-04-19
