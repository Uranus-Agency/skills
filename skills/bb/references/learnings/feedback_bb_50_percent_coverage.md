---
name: BB — average coverage across the runtime must hover around 50%
description: The #1 background design constraint for every BB: across the full 30s loop, the average iframe coverage by opaque content should sit around 50%. Peaks 70-80%, valleys 18-40%. Never stay high for long.
type: feedback
---

## The 50% rule

**Across the whole 30s runtime, the average pixel coverage of opaque content inside the iframe should hover around 50%.** Peaks can hit 70-80% briefly; valleys should drop to 18-40%. What matters is the *time-weighted average*, not any single frame.

**Why:** The billboard sits docked at the bottom of a publisher's article. If opaque content stays above 60% coverage for most of the loop, the ad starts feeling like a wall between the reader and the article — they scroll past or dismiss it. If coverage stays below 30% the whole time, the ad has no presence and the brand message never lands. 50% average is the sweet spot: the ad commands attention during peaks, then politely recedes during valleys so the reader sees the publisher's content breathe through.

This principle came out of the Nobitex signup billboard critique. Earlier iterations with a single always-visible ~70% panel were rejected — felt too heavy. The morphing-shape design that oscillates 18%↔78% with ~50% average was the accepted answer.

## How to budget coverage across a 30s loop

Think of it as a coverage schedule. Walk through every second of the loop and estimate opaque coverage percentage. Example from the Nobitex BB:

| Scene | Duration | Shape coverage | Seconds × % |
|-------|----------|----------------|-------------|
| Brand intro (pill) | 0 – 5.3  | ~38% | 201 |
| BTC live (big)    | 5.3 – 11.5 | ~72% | 446 |
| ETH live (mid)    | 11.5 – 17.5 | ~50% | 300 |
| USDT live (big)   | 17.5 – 22.4 | ~72% | 353 |
| Gift finale (big) | 22.4 – 26.4 | ~78% | 312 |
| Urgency pill      | 26.4 – 29.9 | ~18% | 63  |
| **Totals**        | **~30s** | **avg 56%** | |

That's slightly over 50% but acceptable. The two valleys (intro pill + urgency pill) pull the average down from what would otherwise be a ~70% constant.

**If your budget averages >60%,** add valleys: more pill/collapse geometry, longer intro, shorten peak scenes. **If your budget averages <40%,** your ad will feel ghostly — extend peaks or add a secondary content layer.

## Peaks and valleys must alternate — never two peaks back-to-back

Even if the average is 50%, a schedule like "60% → 60% → 60% → 20% → 20% → 20%" is worse than "60% → 25% → 65% → 20% → 55% → 25%". The eye needs the breathing moments between each peak or the ad reads as static weight. **Always alternate**: peak, valley, peak, valley.

## Transparent-iframe rule is downstream of this

The "body background must be transparent" rule exists TO SERVE the 50% coverage budget. You cannot have a valley if the body itself is opaque. All coverage is computed relative to the body being see-through — opaque pixels are *contributed* by bounded panels, cards, text, images. Every element counts toward the budget.

## How to apply

- **Before coding**, sketch the coverage schedule for the 30s loop. Mark each scene's target coverage. Compute the time-weighted average. If not near 50%, redesign the schedule FIRST.
- **In the manifest.json**, annotate each shape geometry with its coverage estimate as a `note` field.
- **During QA**, scrub the timeline at 2-3s intervals and eyeball coverage at each moment. If 5+ consecutive moments are >60%, you've got a wall.
- **Related pattern:** morphing/breathing shape (see `feedback_bb_morphing_breathing_shape.md`) is the mechanism. The 50% rule is the *constraint*. Don't confuse the two.
