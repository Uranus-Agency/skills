# adferz CHANGELOG

## 1.0.0 — 2026-04-30

Initial release. Unified skill replacing split `bb`, `bb-300x100`, `bb-300x250`, `bb-468`.

### Supports
- **bb-150** (400 × 150 sticky-bottom narrative — full Yektanet Digital Billboard)
- **bb-468** (468 × 60 sticky-bottom small leaderboard)
- **mid-300x100** (300 × 100 mid-content small banner)
- **rect-300x250** (300 × 250 in-content medium rectangle)

### Common rules (apply to all four)
- 50–60% sinusoidal coverage curve with KV-fills-frame exception
- 70/30 distribution at every instant
- Text-Always-Readable (TAR) — every text element gets backdrop / self-backing / halo / hidden
- Loop on `tl.onComplete` — never fixed `setTimeout(reload, 30000)`
- Anti-pattern-bias rotation per brand (audit last 2–3 builds before picking treatment)
- Asset-driven invention preferred over default catalogue
- 100-pt 9-category self-scoring rubric mandatory before delivery
- TAR-friendly z-index map (text always above KV)

### Learnings
References cross to `~/.claude/skills/bb/references/learnings/` for backward-compat. The reference table at the bottom of SKILL.md lists when to read each.

### Replaces
- `bb` (1.3.0)
- `bb-300x100` (1.0)
- `bb-300x250` (1.0)
- `bb-468` (assumed sibling)

The split skills remain installed for backward-compatibility with any in-flight work but new tasks should use `/adferz`.
