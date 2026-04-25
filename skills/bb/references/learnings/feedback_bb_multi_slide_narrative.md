---
name: BB — always design a multi-slide narrative, not one cycling layout
description: A 30s BB is a short film, not a poster. Design 4-6 distinct scenes with a beginning, middle, and ending beat. One static layout that loops = wasted airtime.
type: feedback
---

## Rule: every BB is a 4-6 scene narrative across 30s

A billboard has 30 seconds of the viewer's peripheral attention, maybe less. Using that 30s to cycle one layout (one product, one headline, one CTA, repeat) is a creative failure — by second 10 the viewer has absorbed everything and the remaining 20s are dead airtime. Instead, structure the loop as a **short film** with distinct scenes and a clear beat-to-beat progression.

**Why:** Repeatedly during BB reviews, the user has rejected single-layout designs and asked for multi-slide narratives. Most recently on the Nobitex signup BB: "اینجا یه بیلبورد یه حرفی داره — نمی‌تونه یه چیز ثابت باشه" — the ad has a story to tell; it can't sit still. Single-layout BBs feel like static banners that someone added wiggle to. Multi-slide narratives feel like advertising.

## Canonical 30s structure

**4-6 scenes** across 30s is the sweet spot. Fewer than 4 = feels static. More than 6 = each scene is too short to land. A good default:

| Beat | Role | Typical duration |
|------|------|------------------|
| **Scene 1: Brand intro** | Who you are. Logo + one-line positioning. | 4-6s |
| **Scene 2-4: Value beats** | 2-3 distinct reasons to care. Live data, product carousel, feature hits, etc. Each scene has one clear message. | 5-7s each |
| **Scene 5: Emotional hook** | The payoff — free gift, biggest discount, celebration moment, the "yes I want this" beat. | 3-5s |
| **Scene 6: Urgency finale** | Time pressure + pulsing CTA. Makes the viewer act NOW before the loop restarts. | 2-4s |

Not every BB fits this exact template — a 2-product BB might be 1-2-2-finale = 4 scenes — but the structure (intro → value → payoff → urgency) almost always applies.

## Each scene must have a distinct visual identity

Not just different text in the same layout. Different visuals tell the viewer "this is a new beat." Ways to shift:
- **Shape morph** — the main panel changes geometry (see `feedback_bb_morphing_breathing_shape.md`)
- **Color / glow shift** — active element gets a brand-tinted glow; previous scene's tint fades
- **Layout reorg** — logo moves, CTA swaps copy, chart appears/disappears
- **Character / mascot pose change** — if you have a mascot, each scene is a different pose/expression
- **Side content rotation** — left pane shows product A in scene 2, product B in scene 3, etc.

If two adjacent scenes look 90% the same, merge them. That's not two scenes.

## Beat hierarchy — every scene has ONE job

Each scene communicates ONE message. Not two. Not "price + feature + trust badge + CTA" crammed into one frame. The viewer's attention per scene is roughly 5 seconds — enough for ONE idea. If a scene has more than one message, split it into two scenes or cut the weaker one.

Example (Nobitex BB):
- Scene 2 = "BTC price is live." (one idea: live data for BTC)
- Scene 3 = "ETH price is live." (same idea, different coin — repeated intentionally to anchor "we track all coins")
- Scene 4 = "USDT price is live." (ditto)
- Scene 5 = "Signing up gets you a free gift." (new idea, single)
- Scene 6 = "Offer is limited — act now." (urgency, single)

Notice scenes 2-4 are repetitive on purpose — the repetition IS the message (breadth of coverage).

## Loop-awareness — the last scene sets up the first

The final scene lands right before the loop restarts. If it leaves the viewer mid-thought, the brand intro (scene 1) of the next loop feels like a non-sequitur. Make the finale wrap up cleanly so the loop feels like a planned restart, not a seam:
- Urgency pill fades/collapses to almost nothing
- CTA keeps its position so it's continuous across the loop boundary
- Brand intro's geometry should be *different* from the finale's (large shape after collapsed pill, or vice versa) so the reboot reads as "the story begins again"

## How to apply

- **Before coding**, write the 4-6 scene outline in plain language. One line per scene: "Scene 2 = BTC live price + ascending chart". If you can't fit each scene in one line, you're overloading.
- **In the manifest**, include a `meta.scenario` field describing the narrative arc in 1-2 sentences — and a scene-by-scene breakdown in `tracking` (VISIT_SLIDE01-06).
- **During QA**, play the full 30s loop. Ask: "can I point to the boundary between each scene?" If two scenes blur together, the visual identity isn't distinct enough.
- **Related constraint:** this multi-slide narrative interacts with the 50% coverage rule (see `feedback_bb_50_percent_coverage.md`) — each scene has its own coverage level, and alternating peaks and valleys across scenes IS part of what makes them feel distinct.
