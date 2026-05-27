---
name: sync-memory
description: Push agent memory files to the Domo fileset for AI Search. Use when the user says /sync-memory or asks to sync memory to Domo.
---

# Sync Memory to Domo

Push the agent's MemFS markdown files to a Domo fileset, making them available for Domo AI Search.

## When to Use

- User says `/sync-memory`
- User asks to sync/push memory to Domo
- After making significant memory changes that should be reflected in Domo

## Execution

```bash
# 1. Get Domo credentials from Infisical if not already set
# DOMO-COMMUNITY_ACCESS_TOKEN from Infisical (hostinger VPS project, prod env)

# 2. Set env vars
export DOMO_INSTANCE=domo-community
export DOMO_ACCESS_TOKEN=<from infisical>
export DOMO_FILESET_ID=c0b71cf1-7be3-4340-b021-b3b18eab2f14
# MEMORY_DIR is set by the Letta agent runtime

# 3. Dry run first
python /workspace/.agents/runbooks/sync-memory-to-domo/scripts/main.py --dry-run --verbose

# 4. If dry run looks correct, do the real sync
python /workspace/.agents/runbooks/sync-memory-to-domo/scripts/main.py --verbose
```

## Runbook

Full runbook with troubleshooting: [[runbooks/sync-memory-to-domo/SKILL.md]]

## Fileset Details

- **Fileset ID:** `c0b71cf1-7be3-4340-b021-b3b18eab2f14`
- **Instance:** `domo-community`
- **Direction:** MemFS → Domo (push only, MemFS is authoritative)
- **Directories synced:** `system/`, `reference/`
- **File types:** `.md`, `.txt`, `.csv`, `.json`, `.yaml`, `.yml`
