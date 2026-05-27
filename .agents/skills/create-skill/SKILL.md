---
name: create-skill
description: >
  Scaffold or rewrite SKILL.md files using the monorepo quality standard.
  Use for: "create skill", "rewrite skill", "standardize SKILL.md", "scaffold skill".
metadata:
  version: 2.2.1
  updated: 2026-04-21
---

# create-skill

## Overview

Create or modernize skill documentation so each skill is concise, actionable,
and structurally consistent. This skill also enforces `env_loader` policy and
`EXPORTS/` placement for runtime outputs.

## Core Capabilities

- Scaffolds new skill folders and baseline `SKILL.md`
- Rewrites existing skills to the standard section structure
- Enforces frontmatter naming, versioning, and trigger quality
- Enforces `env_loader` policy for scripts that read environment variables
- Enforces `<skill_folder>/EXPORTS/` for generated runtime outputs

## When to Use

- You are adding a new skill
- Existing skills are inconsistent or too verbose
- A skill has scripts that still use raw `load_dotenv`
- A skill writes generated outputs outside an `EXPORTS/` folder

## Quick Start

```bash
# Create a new skill folder
mkdir -p .agents/skills/<skill-name>/{references,assets,scripts,EXPORTS}

# Seed SKILL.md from template
cp .agents/skills/create-skill/assets/SKILL.md.template \
   .agents/skills/<skill-name>/SKILL.md

# Verify frontmatter quickly
rg -n "^name:|^description:|^metadata:|^  version:" .agents/skills/<skill-name>/SKILL.md
```

## Detailed Workflow

### Step 1: Define purpose and triggers

Set a clear action-oriented `description` and include a practical `Use for:`
list of trigger phrases.

### Step 2: Scaffold structure

Required minimum:

```text
.agents/skills/<name>/
|-- SKILL.md
|-- references/        # optional
|-- assets/            # optional
|-- scripts/           # optional
`-- EXPORTS/           # required if skill generates files
```

### Step 3: Author SKILL.md sections

Use this section order for consistency:
1. Overview
2. Core Capabilities
3. When to Use
4. Quick Start
5. Detailed Workflow
6. References
7. Related Skills

### Step 4: Enforce env_loader policy

If scripts read env vars, they must use:

```python
from env_loader import load_env
load_env()
```

Never introduce new direct `load_dotenv` calls in skill/runbook/test scripts.

### Step 5: Enforce EXPORTS policy

If a skill generates reports, files, downloads, snapshots, or exports, output
must be written to one of:
- `<skill_folder>/EXPORTS/` — skill-scoped outputs (preferred)
- `/data/EXPORTS/` — repo-root fallback for test fixtures and generated images

Both paths are gitignored. **Never commit binary or generated output files**
(images, JSON snapshots, fixtures) outside these directories. The pre-push
safety hook blocks `/data/` paths from being tracked.

Ensure repo `.gitignore` contains:

```text
**/EXPORTS/
/data/EXPORTS/
```
### Step 8: Enforce API-first in scripts

If the skill includes scripts that invoke library capabilities:
- Call the service's FastAPI REST route for deterministic outcomes.
- Call FastMCP tool endpoints for Letta agent–backed activity.
- Never import library SDK internals from a skill script.

See: `.agents/skills/microservices-api-first/SKILL.md` for the thin-script pattern
and `.agents/plans/microservices-architecture/PLAN.md` § Design Principles for rationale.
## References

- `assets/SKILL.md.template` - base markdown template
- `assets/quality-checklist.md` - quality gate before publishing
- `references/frontmatter-guide.md` - naming and metadata rules
- `references/structure-best-practices.md` - structural conventions

## Related Skills

- `create-runbook` - scaffold operational runbooks
- `create-test` - scaffold behavioral tests
- `create-chronjob` - scaffold scheduled maintenance jobs
- `create-plan` - scaffold phased implementation plans
- `review-agents-folder` - normalize `.agents/` folder structure
- `update-documentation` - post-implementation docs pass
- `tdd` - test-first implementation workflow
- `prd-to-issues` - convert PRD scope to issue slices
