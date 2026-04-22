# Template Skill - Start Here

Use this checklist when creating a new skill from this template.

## 1) Copy and Rename

- Copy `skills/template` to `skills/<new-skill-name>`
- Rename `name` in `SKILL.md` to match folder name exactly

## 2) Frontmatter

- Update `description` with real trigger keywords
- Set initial `version` (e.g. `0.1.0`)

## 3) Scope and Contract

- Replace all placeholders (`<...>`)
- Define explicit in-scope and out-of-scope behavior
- Define concrete output artifacts

## 4) Optional Command

- Copy `commands/template.md` to `commands/<new-skill-name>.md`
- Replace placeholders and argument hints

## 5) QA

- Ensure no placeholder tokens remain
- Ensure trigger keywords are domain-specific
- Ensure output rules are implementation-ready
