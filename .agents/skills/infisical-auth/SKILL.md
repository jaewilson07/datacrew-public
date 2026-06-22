---
name: infisical-auth
description: >
  Authenticate the Infisical CLI on the VPS using machine identity credentials
  from .env, then deploy or re-deploy the datacrew-public container with secrets
  injected. Use for: "deploy datacrew-public", "redeploy", "infisical login",
  "restart container", "fetch secrets".
metadata:
  version: 1.0.0
  updated: 2026-05-07
---

# infisical-auth

## Overview

The Infisical CLI on the VPS does not persist login sessions between commands.
Every deploy must authenticate fresh using the machine identity credentials in
`.env`, then immediately run the deploy script within the same shell session.

## Core Capabilities

- Authenticates Infisical CLI via universal-auth (machine identity)
- Deploys the datacrew-public container with secrets injected from Infisical
- Works around the CLI's inability to persist sessions on the VPS

## When to Use

- Deploying or re-deploying the datacrew-public container
- Any time the container needs fresh secrets (token rotation, new secret added)
- After VPS reboots or container crashes

## Quick Start

```bash
# One-liner: authenticate + deploy
ssh deploy@187.77.216.108 \
  'export PATH="$HOME/.local/bin:$PATH" && \
   export INFISICAL_API_URL=https://infisical.datacrew.space && \
   export INFISICAL_TOKEN="$(infisical login --method universal-auth \
     --client-id 8b6a5698-61ff-4f0e-a403-3df29f667f31 \
     --client-secret 015fd0cb965de429d310bf73536d1884b178ef8023ae8c9f97c394f213bad72d \
     --plain 2>/dev/null)" && \
   cd /home/deploy/workspaces/simpleDiscordBot/infrastructure/bonker && \
   uv run --no-project python setup/hostinger/deploy_docker_containers.py \
     local letta-code-channels-datacrew-public'
```

## Detailed Workflow

### Step 1: Authenticate Infisical CLI

The CLI requires `INFISICAL_TOKEN` set as an env var — the login session does
NOT persist between commands. You must capture the token and export it in the
same shell:

```bash
export INFISICAL_API_URL=https://infisical.datacrew.space
export INFISICAL_TOKEN="$(infisical login --method universal-auth \
  --client-id 8b6a5698-61ff-4f0e-a403-3df29f667f31 \
  --client-secret 015fd0cb965de429d310bf73536d1884b178ef8023ae8c9f97c394f213bad72d \
  --plain 2>/dev/null)"
```

Verify it works:

```bash
infisical export --projectId 3fbb4296-d4e6-4c17-83ee-b852a57a5e50 \
  --env prod --path /datacrew --format dotenv | head -3
```

### Step 2: Deploy the container

```bash
cd /home/deploy/workspaces/simpleDiscordBot/infrastructure/bonker
uv run --no-project python setup/hostinger/deploy_docker_containers.py \
  local letta-code-channels-datacrew-public
```

You should see: `[info] Injected 16 secret(s) from Infisical path(s) ['/datacrew']`

### Step 3: Verify

```bash
docker logs letta-code-channels-datacrew-public 2>&1 | tail -10
```

Look for: `Registered successfully` and `Connected. Awaiting instructions.`

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Infisical fetch failed` | CLI not authenticated | Re-run Step 1 (INFISICAL_TOKEN not set) |
| `No valid login session found` | Token expired or not exported | Must export in same shell before deploy |
| `Unauthorized` in container logs | Wrong LETTA_API_KEY in Infisical | Ensure it's a server key (`sk-let-...`), not agent token |
| `LETTA_API_KEY is required` | Secret not injected | Check Infisical path `/datacrew` has the key |
| Blank Slack tokens | Infisical export failed silently | Check `PUBLIC_DATACREW_SLACK_BOT_TOKEN` exists at `/datacrew` |

## Key Facts

- **Infisical project (deploy)**: `3fbb4296-d4e6-4c17-83ee-b852a57a5e50` — VPS deploy secrets at `/datacrew`
- **Infisical project (datacrew/.env)**: `de8b26a4-8d69-46fa-bb32-9715ab396d6f` — local dev secrets
- **Secret path**: `/datacrew` (16 secrets total)
- **Machine identity**: client ID + secret in `.env` (NOT in Infisical — bootstrap credentials)
- **uv path on VPS**: `$HOME/.local/bin/uv` (must be in PATH)
- **Deploy script**: `setup/hostinger/deploy_docker_containers.py`
- **Container name**: `letta-code-channels-datacrew-public`

> ⚠️ **Two projects exist.** The deploy script uses project `3fbb4296` (from
> `infisical.json`). The `datacrew/.env` has `INFISICAL_PROJECT_ID=de8b26a4`
> which is the WRONG project for VPS deploys. Always use `--projectId 3fbb4296`
> or the deploy script (which reads from `infisical.json`).

## References

- `.env` — machine identity credentials (INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET, INFISICAL_PROJECT_ID)
- Deploy script: `infrastructure/bonker/setup/hostinger/deploy_docker_containers.py`
- Compose: `infrastructure/bonker/apps/letta-code-channels-datacrew-public/docker-compose.yml`
- Infisical dashboard: `https://infisical.datacrew.space/organizations/e899ebbe-5c41-4d53-b1ce-28cd18db1987/projects/secret-management/de8b26a4-8d69-46fa-bb32-9715ab396d6f/overview`

## Related Skills

- `create-skill` — scaffold new skills
- `create-runbook` — scaffold new runbooks
