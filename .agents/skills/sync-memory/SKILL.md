---
name: sync-memory
description: >
  Push agent memory files to Domo fileset (AI Search) and Google Docs. Commits
  any uncommitted changes first. Use for: "/sync-memory", "push memory",
  "sync to domo", "backup memory".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# sync-memory

Sync agent memory to Domo fileset (AI Search) and Google Docs. Commits uncommitted changes first.

## When to Use

- `/sync-memory` — push memory to Domo + GDocs
- User asks to "sync memory", "push memory to Domo", "backup memory"

## Steps

### 1. Commit uncommitted memory changes

```bash
cd "$MEMORY_DIR"
git add -A
git commit -m "chore: memory sync $(date +%Y-%m-%d)" || echo "Nothing to commit"
```

### 2. Push to remote (if auth working)

```bash
git push 2>&1 || echo "Push failed — local commit saved"
```

Note: Memory push to `letta-ai/agent-memory.git` may fail due to GitHub auth issues. Local commit is still valid.

### 3. Sync to Domo fileset

Uses existing runbook: `.agents/runbooks/sync-memory-stores/`

```bash
python3 .agents/runbooks/sync-memory-stores/scripts/sync_to_domo.py
```

This pushes memory files to Domo fileset for AI Search. Requires:
- `DOMO_CLIENT_ID` + `DOMO_CLIENT_SECRET` (from Infisical)
- Fileset ID configured in runbook

### 4. Sync to Google Docs

Uses existing runbook: `datacrew/.agents/runbooks/sync-memory-gdocs/`

```bash
cd /workspace/datacrew
python3 .agents/runbooks/sync-memory-gdocs/scripts/sync_to_gdocs.py
```

Creates/updates tabs in a Google Doc with memory contents.

## Configuration

| Variable | Source | Description |
|----------|--------|-------------|
| `MEMORY_DIR` | env | Agent memory directory (usually `~/.letta/agents/<id>/memory`) |
| `DOMO_CLIENT_ID` | Infisical | Domo API auth |
| `DOMO_CLIENT_SECRET` | Infisical | Domo API auth |
| `GDOC_CLIENT` + `GDOC_TOKEN` | Infisical | Google Docs auth |

## Gotchas

- **Memory push may fail** — GitHub auth on `letta-ai/agent-memory.git` is flaky. Local commits are still valid.
- **Domo sync requires valid tokens** — check `DOMO_CLIENT_ID` + `DOMO_CLIENT_SECRET` in Infisical
- **Run from correct directories** — Domo sync from workspace root, GDocs sync from datacrew/

## Related

- `sync-memory-stores` runbook (`.agents/runbooks/sync-memory-stores/`) — Domo sync
- `sync-memory-gdocs` runbook (`datacrew/.agents/runbooks/sync-memory-gdocs/`) — GDocs sync
- `check-mdrag` — health check for mdrag (separate from memory sync)
