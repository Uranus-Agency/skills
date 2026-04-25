# Changelog - bb

All notable changes to the `bb` skill are documented in this file.

## [1.2.0] - 2026-04-24
### Added (learnings from Nobitex signup BB)
- **`feedback_bb_50_percent_coverage.md`** — **#1 background constraint**: time-weighted average iframe coverage across the 30s loop must hover around 50%. Peaks 70-80%, valleys 18-40%. Sketch a coverage schedule before coding.
- **`feedback_bb_multi_slide_narrative.md`** — **#1 structure constraint**: every 30s BB is a 4-6 scene short film (intro → value beats → payoff → urgency), not a single cycling layout. Each scene has one message.
- **`feedback_bb_no_empty_collapsed_scenes.md`** — every shape geometry in a morph sequence must carry visible content; collapsed finale pills need urgency text + draining bar, never sit empty. Sourced from user feedback "یه اسلاید خالی داره اون آخر".
- **`feedback_bb_morphing_breathing_shape.md`** — mechanism for the 50%-rule and multi-slide-rule: a single shape morphing through 5 named geometries with coverage oscillating 18-78%.
- **`feedback_bb_live_data_cascade.md`** — multi-source API cascade (primary → fallback → hardcoded) for live-price billboards. Fallback values MUST be realistic for shipping month.
- **`project_bb_creation_nobitex.md`** — full project capture: 6-scene morphing card, 3 floating 3D-sphere coins, live-price API cascade, urgency-pill finale.

### Changed
- SKILL.md now opens with a "TWO FIRST PRINCIPLES" block (50% coverage rule + multi-slide narrative rule) before Step Zero, establishing them as the primary design constraints every other rule is downstream of.
- SKILL.md "Multi-Phase Animation Patterns" section extended with Morphing Shape / Breathing Card pattern, Every Scene Needs Content rule, and Live Data API Cascade pointer.

## [1.1.0] - 2026-04-23
### Added
- **`manifest.json` as the 5th required output file.** Every billboard now ships a declarative JSON description of its elements and animations alongside the generated HTML/CSS/JS. This is the source of truth for the design and enables downstream tooling (visual editor, bulk variant generator, automated QA) to read and mutate billboards without re-parsing JavaScript.
- Manifest schema with `meta`, `assets`, `elements`, `animations`, and `tracking` sections.
- Manifest authoring rules: stable element ids, resolved CSS values in `style`, `editable` flags per element, primary-animation-per-element capture.
- Quality checklist entries verifying manifest integrity (element coverage, animation coverage, id stability, duration parity).

### Changed
- Output Format section renamed "Always 4 Files" → "Always 5 Files".

## [1.0.0] - 2026-04-22
### Added
- Initial production BB skill for Yektanet Digital Billboard workflows.
- Full skill specification with asset analysis, layout rules, animation patterns, and output contract.
