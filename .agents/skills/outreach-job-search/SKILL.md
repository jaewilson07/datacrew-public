---
name: outreach-job-search
description: >
  Run the DataCrew job search scoring pipeline: scrape recent jobs, filter via L1
  keyword scoring and L2 Ollama LLM scoring, then post the top results as a formatted
  digest to Slack. Use for: "/outreach/job-search", "run job search", "score jobs",
  "job digest", "find jobs".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# outreach-job-search

Run the job search scoring pipeline and post a digest of top results to Slack.

## When to Use

- User says `/outreach/job-search`
- User asks to run job scoring, find jobs, or post a job digest
- User wants to see what new Domo/data platform jobs are available

## Steps

### Step 1: Verify environment

Ensure required env vars are set. The pipeline reads from `datacrew/.env`:

```bash
# Check key vars exist
grep DATACREW_SLACK_BOT_TOKEN /workspace/datacrew/.env | head -1
grep OLLAMA_BASE_URL /workspace/datacrew/.env | head -1
```

If `OLLAMA_BASE_URL` is not set, default to `http://ollama.jaewilson07.twingate.com:11434`.

### Step 2: Run the scoring pipeline

```bash
cd /workspace/datacrew/projects/job-search

JOB_SEARCH_SLACK_BOT_TOKEN=$DATACREW_SLACK_BOT_TOKEN \
JOB_SEARCH_SLACK_CHANNEL_ID=C0B23VA3CJY \
PYTHONPATH=src:/workspace/datacrew \
.venv/bin/python3 run_scoring.py --yolo
```

The `--yolo` flag enables autonomous execution — no approval needed per step.

**What the pipeline does:**
1. **Scrape** — Pull recent jobs from configured sources (7-day window)
2. **L1 (KeywordScorer)** — Fast regex filter: seniority + hard_blocks cut noise
3. **L2 (LettaScorer w/ Ollama backend)** — Local LLM scoring via `gemma3:12b` at the Ollama endpoint
4. **Post** — Format top results and post to Slack via `SlackJobPoster`

### Step 3: Verify Slack post

After the pipeline completes, confirm the digest was posted to `#datacrew-customer-outreach` (C0B23VA3CJY).

## CLI Commands

```bash
# Full pipeline (score + post)
cd /workspace/datacrew/projects/job-search
JOB_SEARCH_SLACK_BOT_TOKEN=$DATACREW_SLACK_BOT_TOKEN \
JOB_SEARCH_SLACK_CHANNEL_ID=C0B23VA3CJY \
PYTHONPATH=src:/workspace/datacrew \
.venv/bin/python3 run_scoring.py --yolo

# Score only (no Slack post)
JOB_SEARCH_SLACK_BOT_TOKEN=$DATACREW_SLACK_BOT_TOKEN \
JOB_SEARCH_SLACK_CHANNEL_ID=C0B23VA3CJY \
PYTHONPATH=src:/workspace/datacrew \
.venv/bin/python3 run_scoring.py --yolo --no-post
```

## Pipeline Architecture

| Layer | Scorer | Method | Speed |
|-------|--------|--------|-------|
| L1 | KeywordScorer | Regex: seniority + hard_blocks | Fast |
| L2 | LettaScorer (Ollama backend) | Local LLM (`gemma3:12b`) | ~30s/job |
| L3 | LettaScorer | Letta API (fallback, credits exhausted) | N/A |

**Profile:** `profiles/jae-consultant-fte.yaml`
- `must_have_any: ["domo"]`
- `seniority: [senior, principal, staff, director, lead, manager, architect, consultant, engineer, analyst, developer]`
- `comp_min: $130k FTE`

**Database:** `data/EXPORTS/job_search.db` — persisted jobs, deduped by URL

## Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `DATACREW_SLACK_BOT_TOKEN` | `datacrew/.env` | Slack bot token (xoxb-) |
| `OLLAMA_BASE_URL` | `datacrew/.env` or default | Ollama endpoint for L2 scoring |
| `JOB_SEARCH_SLACK_BOT_TOKEN` | Set from `DATACREW_SLACK_BOT_TOKEN` | Pipeline Slack auth |
| `JOB_SEARCH_SLACK_CHANNEL_ID` | Hardcoded `C0B23VA3CJY` | Target Slack channel |

## Key IDs

| Resource | ID |
|----------|-----|
| Slack Channel | `C0B23VA3CJY` (#datacrew-customer-outreach) |
| Job DB | `data/EXPORTS/job_search.db` |
| Profile | `profiles/jae-consultant-fte.yaml` |

## Gotchas

- **Use `--yolo` for autonomous runs** — the pipeline is designed for hands-off execution
- **Use `SlackJobPoster` for ALL Slack formatting** — never create duplicate Block Kit formatting (gotcha #72)
- **Post to `C0B23VA3CJY`** — NOT `C0AR7M4M0V9` (old channel)
- **Empty `seniority: []` in profile causes noise** — always validate the profile has meaningful filters (gotcha #73)
- **L3 LettaScorer credits exhausted** — don't enable unless credits are refreshed
- **Ollama must be reachable** — check `http://ollama.jaewilson07.twingate.com:11434` before running
- **VPS can't run Ollama** — L2 scoring requires the local GPU endpoint via Twingate
- **sentence-transformers removed** — no more OOM/disk-full failures from torch
- **Use `.venv/bin/python3` directly** — NOT `uv run` (30+ sec resolver overhead)

## Related

- `datacrew/projects/job-search/` — pipeline source code
- `skills/outreach-create-dossier/SKILL.md` — dossier creation for top-tier companies
- `skills/mdrag-mcp/SKILL.md` — mdrag MCP for web research
