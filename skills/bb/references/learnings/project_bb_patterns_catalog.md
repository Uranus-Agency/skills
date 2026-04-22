---
name: BB billboard patterns catalog from production analysis
description: Comprehensive catalog of animation patterns, techniques, and brand-specific approaches extracted from 70+ production billboards across 50+ brands in Uranus-Billboard-main
type: project
---

Deep analysis of C:\Users\m.khorshidsavar\desain\Uranus-Billboard-main revealed these production patterns across 70+ billboards:

**Pattern Distribution:**
- 3-Act intro (truck/mascot crosses): ~35% of billboards
- Video-as-content (baked text): ~15% (bitpin, tapsi, snappmarket)
- Product carousel cycling: ~20% (elanza, gsm, khanoumi, technolife)
- Fortune wheel / gamification: ~5% (melligold)
- Live data / price chart: ~10% (wallex, daricgold, taline, saraf)
- Countdown timer: ~5% (bluebank, various blackfriday)
- Multi-video sequential: ~5% (snappmarket)
- GIF intro + slide transition: ~5% (azkivam)

**Advanced Techniques Found in Production:**
1. Sequential video chaining via video.ended event (snappmarket)
2. Mid-video pause at specific timestamp with CTA overlay (snappmarket)
3. LED ring with brightness+drop-shadow glow toggling (melligold)
4. Spinner blur during fast rotation, un-blur on slow stop (melligold)
5. Thought bubble animation: dots → circles → cloud (snappmarket)
6. Sound effects on interaction via new Audio() (snappmarket)
7. Spotlight/focus-zoom loop: elements fade → hero zooms → all return (wallex)
8. Elastic pop animation for live price updates (wallex)
9. Dynamic overline image swap based on API data direction (wallex)
10. Background gradient cycling with gsap (azkivam)
11. Deep onComplete nesting for sequential reveals (tapsi)
12. Display:none → display:block toggle via gsap.set (tapsi, snappmarket)
13. Product rotation with display toggle, not just opacity (snappmarket)
14. Video controls hidden via ::-webkit-media CSS (snappmarket)
15. gsap.delayedCall for timed recursive sequences (wallex)

**Why:** These patterns were extracted from actual production code that ran on publisher sites. They represent battle-tested approaches for the 150px Yektanet iframe format.

**How to apply:** When choosing animation patterns for a new billboard, match the scenario to the closest production pattern. The pattern distribution above shows the frequency — 3-Act and Product Carousel cover ~55% of all use cases. Use advanced techniques (multi-video, fortune wheel, live data) only when the scenario specifically calls for them.
