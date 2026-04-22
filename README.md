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
    voocher/
        SKILL.md
        references/
            README.md

commands/
    bb.md
    voocher.md

plugin.json
README.md
```

## Install One Skill (from GitHub)

Use the Skills CLI format `owner/repo@skill-name`:

```bash
npx skills add uranus-agency/skills@bb -g -y
npx skills add uranus-agency/skills@voocher -g -y
```

## Local Development Workflow

1. Develop only inside `skills/<skill-name>/`.
2. Keep each skill's references and examples in its own `references/` folder.
3. If needed, add a matching command file in `commands/<skill-name>.md`.
4. Bump versions and release notes when behavior changes.

## Add a New Skill

1. Create `skills/<new-skill>/SKILL.md` with valid YAML frontmatter.
2. Set `name` in frontmatter equal to the folder name.
3. Add a clear `description` with trigger keywords.
4. Optionally add `commands/<new-skill>.md`.
5. Commit and tag release.

## Current Skills

- `bb` — Yektanet Digital Billboard builder.
- `voocher` — Voucher/promo flow assistant scaffold.

## Author

Uranus Agency — dev@uranus-agency.ir
