---
description: Template command for Uranus skills. Copy, rename, and customize for your new skill.
argument-hint: <brief> [constraints]
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "TodoWrite", "Skill"]
---

# <SkillName> - Command Template

You are **<SkillName>** command handler.

## Your Task

1. Load the `<skill-name>` skill.
2. Parse `$ARGUMENTS` and extract requirements.
3. Produce implementation-ready output based on the skill contract.
4. Add a concise delivery checklist.

## If No Arguments Provided

Ask for the minimum required inputs to proceed.

## User Input

$ARGUMENTS
