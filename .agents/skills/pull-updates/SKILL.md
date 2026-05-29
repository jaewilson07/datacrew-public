---
name: pull-updates
description: >
  Pull latest changes from all Git repos. Handles safe.directory config for
  Docker-mounted paths. Reports which repos had updates vs already up to date.
  Use for: "/pull-updates", "pull repos", "sync code", "update all repos".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# pull-updates

Pull latest changes from all DataCrew repos. Handles the "dubious ownership" issue from Docker-mounted paths.

## When to Use

- `/pull-updates` — sync all repos
- User asks to "pull latest", "update repos", "sync code"

## Repos

| Repo | Path |
|------|------|
| cboti | `/workspace/libraries/cboti` |
| mdrag | `/workspace/libraries/mdrag` |
| crew-dcs | `/workspace/libraries/crew-dcs` |
| datacrew | `/workspace/datacrew` |

## Steps

### 1. Add safe.directory for each repo

Git rejects operations on paths owned by different users (Docker mounts). Add exception:

```bash
git config --global --add safe.directory /workspace/libraries/cboti
git config --global --add safe.directory /workspace/libraries/mdrag
git config --global --add safe.directory /workspace/libraries/crew-dcs
git config --global --add safe.directory /workspace/datacrew
```

### 2. Pull each repo

```bash
cd /workspace/libraries/cboti && git pull 2>&1
cd /workspace/libraries/mdrag && git pull 2>&1
cd /workspace/libraries/crew-dcs && git pull 2>&1
cd /workspace/datacrew && git pull 2>&1
```

### 3. Report results

For each repo, report:
- "Already up to date" if no changes
- "Updated: <n> commits" if changes pulled
- List of changed files if useful

## Example Output

```
cboti: Already up to date
mdrag: Updated 3 commits (src/interfaces/mcp/_app.py, src/config/settings.py)
crew-dcs: Already up to date
datacrew: Updated 1 commit (projects/job-search/run_scoring.py)
```

## Gotchas

- **Dubious ownership error** — must add `safe.directory` for each repo before git operations
- **Protected branches** — mdrag main is protected, can't push directly — but pull is fine
- **Git -C syntax** — use `git -C /path pull` or `cd` into repo; running from wrong directory fails

## Related

- `sync-memory` — syncs memory repos (separate)
- `check-mdrag` — health check for mdrag MCP
