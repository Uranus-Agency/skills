---
name: BB — no empty scenes, especially collapsed/minimized finale
description: Every scene must have visible content — when a shape morphs smaller at the end, fill the small shape with urgency content, don't just let it sit empty.
type: feedback
---

## Rule: an empty shape is a dead slide. Even the small/collapsed ones.

When the main billboard shape morphs to a smaller geometry at the end of a loop (pill, badge, chip), the collapsed shape MUST carry content. Empty shape = the viewer reads the billboard as broken.

**Why:** On the Nobitex signup BB the right-panel morphed: intro pill → liveBig → liveMid → giftBig → collapse. The collapse state was built but we forgot to put anything inside it. User caught this instantly: *"یه اسلاید خالی داره اون آخر! اونو درست کن"* ("there's an empty slide at the end — fix it"). The final 3 seconds of every loop were just a dark pill with nothing in it. Reads as a bug, not a feature.

**The symmetric pitfall:** the big scenes are always carefully populated (chart, price, logo, tagline), but the small/collapse states get treated as "transition scenery" — they're not. They are fully-fledged scenes that occupy 10%+ of the loop time. Treat them like any other scene.

## Canonical collapse-pill content (urgency finale)

The collapse pill is usually the last 2-3 seconds of the loop. Pack it with urgency:
- ⚡ "فرصت محدود" / "همین حالا" / "آخرین فرصت" ⚡  (flashing bolts on both sides)
- Draining progress bar (GSAP `scaleX: 1 → 0` over the scene duration, `transformOrigin: 'right center'` for RTL drain)
- Optionally: pulsing CTA swap ("ثبت‌نام رایگان" → "فقط امروز!")

This creates fear-of-missing-out right before the loop restarts. The viewer either clicks or watches it play again.

## How to apply

- **Audit every shape geometry in the morph sequence.** For each geometry, ask: "is there content visible inside this shape right now?" If no → that's an empty slide.
- **A collapsed pill should have 1-2 lines of tight copy MAX** (font-size 11-12px, white-space: nowrap, letter-spacing: -.2px). You have ~156×38px to work with.
- **Draining bars communicate urgency.** Use `transformOrigin: 'right center'` for RTL (drains left-to-right), `transform-origin: left center` for LTR. Match the scene duration exactly (e.g. 2.7s drain over 2.7s scene).
- **Rule-of-thumb:** if a scene has `opacity: 1` on the main shape but every content block above it has `opacity: 0`, you've built an empty slide. Fix it before shipping.

## The broader principle

This is adjacent to the "no empty frames between phases" rule in `feedback_bb_smooth_transitions.md`, but distinct:
- *smooth_transitions* → no empty FRAMES (timing gaps during transitions)
- *this rule* → no empty SCENES (content gaps within a held geometry)

Both failures read as "the ad is broken." Audit for both.
