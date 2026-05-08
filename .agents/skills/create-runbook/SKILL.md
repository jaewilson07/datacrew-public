---
name: create-runbook
description: Creates SOP-style runbooks for recurring tasks with executable scripts. Use for: "create runbook", "turn this into SOP", "standardize recurring task".
metadata:
  version: 2.0.0
  updated: 2026-04-03
---

# create-runbook

Create action-first runbooks with runnable scripts. Crosslink, don't repeat.

## Runbook Structure

```
.agents/runbooks/<verb-noun>/
├── SKILL.md           ← Minimal docs, crosslinks
├── scripts/
│   └── main.py        ← Executable CLI
├── references/        ← Optional: detailed refs
└── assets/            ← Optional: templates
```

## Templates

See: `assets/templates/runbook-skeleton.md`

## Rules

- **Verb-first naming**: `sync-models`, `launch-ssh`, not `model-sync-guide`
- **Script-backed**: Every step runs via script
- **Crosslink**: Link to existing docs, don't copy
- **Minimal markdown**: Commands, not prose
- **API-first**: Scripts call FastAPI REST routes or FastMCP endpoints — never import library internals.
  See: `.agents/skills/microservices-api-first/SKILL.md` for the thin-script pattern.
  If the service doesn't exist yet, add a `⚠️ temporary` note in the runbook.

## FastAPI vs FastMCP (quick rule)

| Script triggers a | Use |
|---|---|
| Deterministic workflow / CRUD | **FastAPI** `POST http://localhost:{PORT}/v1/{route}` |
| Letta agent tool invocation | **FastMCP** tool call |

## Related Skills

- `microservices-api-first` — Thin-script pattern, port registry, FastAPI vs FastMCP decision table
- `refresh-documentation` — Update docs after changes
- `creating-skill` — Create new skills
- `review-documentation` — Read-before/write-after conventions
- `create-chronjob` — Document scheduled maintenance jobs with runbook-backed recovery
- `.agents/plans/microservices-architecture/PLAN.md` — Authoritative design principles
