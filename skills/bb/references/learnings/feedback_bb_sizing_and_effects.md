---
name: BB sizing rules, poke-out effects, and high-impact animations
description: Design in 120px of 150px frame, use overflow zone for بیرون‌زدگی, multi-phase animation loops, shake-on-change, floating background pattern
type: feedback
---

## Sizing & Scaling
- **Design area = bottom 120px** of the 150px iframe. Background/video top edge at y=30px max.
- **Overflow zone = top 30px** — reserved for بیرون‌زدگی (poke-out) elements.
- **Floating background:** `top: 30px; left: 5%; width: 90%; height: 115px; border-radius: 12px; box-shadow` — margin on left/right/bottom, NO margin on top (flush with design area).
- **Card sizes:** Side cards 50–65px, center/hero card 86–110px, CTA 24–28px, logo 30–38px.
- **Side cards lower** than center card (margin-top: 15–20px) for visual hierarchy.
- **Negative inline margins** (-12px) to make cards overlap/touch.

## بیرون‌زدگی (Poke-Out) — ALWAYS USE
Elements poking above the background panel are the most eye-catching technique. Always include at least one poke-out element (logo, center card, product). This creates depth and draws user attention.

## High-Impact Animation Patterns
- **Shake-on-change:** When cycling slides, surrounding elements react with small rotations (±3deg), scale bumps (1.01–1.08).
- **Expand → Takeover → Reset loop:** After carousel, side elements spread, all items show side-by-side, then CTA takes over center (big + pulses), then everything resets and loops.
- **Multi-phase orchestration:** Use callback chains (onComplete) to sequence phases, not simple setInterval.

## Layout Flexibility
- Listen to user's layout description. Don't force 70/30 split if user wants full-width video or custom layout.
- 70/30 split is DEFAULT only when no specific layout is described.
- Each brand gets its own folder: `BB/{brand-name}/`
