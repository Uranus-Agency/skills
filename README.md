# Uranus Skills Monorepo

This repository contains multiple installable skills for Claude Code under one GitHub repo.

## Goal

Keep each skill isolated so teams can develop and release them independently, while users install only the skill they need.

## Repo Layout

```
skills/
    bb/
        SKILL.md
        references/
            ...
    template/
        SKILL.md
        references/
            START_HERE.md

commands/
    bb.md
    template.md

plugin.json
README.md
```

## Install One Skill (from GitHub)

Use the Skills CLI format `owner/repo@skill-name`:

```bash
npx skills add uranus-agency/skills@bb -g -y
```

## Local Development Workflow

1. Develop only inside `skills/<skill-name>/`.
2. Keep each skill's references and examples in its own `references/` folder.
3. If needed, add a matching command file in `commands/<skill-name>.md`.
4. Bump versions and release notes when behavior changes.

## Add a New Skill

1. Copy `skills/template` to `skills/<new-skill>`.
2. Update `skills/<new-skill>/SKILL.md` frontmatter (`name`, `description`, `version`).
3. Replace all placeholders (`<...>`) with real domain rules.
4. Optional: copy `commands/template.md` to `commands/<new-skill>.md` and customize.
5. Run a placeholder check and ensure no template tokens remain.
6. Commit and tag release.

## Template Files

- Skill template: `skills/template/SKILL.md`
- Template checklist: `skills/template/references/START_HERE.md`
- Command template: `commands/template.md`

## Current Skills

- `bb` — Yektanet Digital Billboard builder.
- `template` — Base scaffold for creating new skills consistently.

## Author

Uranus Agency — dev@uranus-agency.ir
