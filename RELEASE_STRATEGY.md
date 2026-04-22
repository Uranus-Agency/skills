# Uranus Skills Release Strategy

This repository is a multi-skill monorepo. Each skill has its own version and changelog.

## 1) Versioning Model

Use semantic versioning per skill:
- `MAJOR`: breaking behavior changes
- `MINOR`: backward-compatible features
- `PATCH`: bug fixes and wording/internal improvements

Examples:
- `bb` can be `1.1.0`
- `voocher` can remain `0.1.0`

A skill version is defined in its `skills/<skill>/SKILL.md` frontmatter `version`.

## 2) Changelog Model

Each skill must have its own changelog:
- `skills/<skill>/CHANGELOG.md`

Use this format:

```md
## [1.1.0] - 2026-04-22
### Added
- ...

### Changed
- ...

### Fixed
- ...
```

## 3) Git Tag Convention

Create tags per skill release using this format:
- `<skill>-v<version>`

Examples:
- `bb-v1.1.0`
- `voocher-v0.1.0`

## 4) Release Steps (Per Skill)

1. Update `version` in `skills/<skill>/SKILL.md`.
2. Update `skills/<skill>/CHANGELOG.md`.
3. Commit with skill-scoped message:
   - `release(bb): v1.1.0`
4. Create annotated tag:
   - `git tag -a bb-v1.1.0 -m "bb v1.1.0"`
5. Push branch and tag:
   - `git push origin main`
   - `git push origin bb-v1.1.0`

## 5) Quality Gate Before Tag

- Skill name in frontmatter equals folder name
- No template placeholders like `<...>` remain
- Changelog has release date and clear Added/Changed/Fixed notes
- Install test passes:
  - `npx skills add uranus-agency/skills@<skill> -g -y`

## 6) Parallel Releases

Multiple skills can release independently in the same week. Keep tags and changelogs isolated by skill.

## 7) Template Rule for New Skills

Every new skill copied from `skills/template` must include:
- `SKILL.md` with `version`
- `CHANGELOG.md` (starting at `0.1.0`)
