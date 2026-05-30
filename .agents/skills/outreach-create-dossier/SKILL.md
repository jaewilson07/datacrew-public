---
name: outreach-create-dossier
description: >
  Create a Domo customer outreach dossier: research a company, generate a Google Doc
  with 4 tabs (Overview, People, Org Chart, Outreach Strategy), sync contacts to
  Google Contacts, and add to Prospect Tracker. Deduplicates against existing entries.
  Use for: "/outreach/create-dossier", "create dossier", "research company for outreach",
  "outreach dossier".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# outreach-create-dossier

Full outreach pipeline for a single Domo customer prospect. Researches the company,
creates a structured Google Doc dossier, syncs contacts, and updates the tracker.

## When to Use

- User says `/outreach/create-dossier <linkedin-url>` or `/outreach create-dossier`
- User asks to research a company for outreach
- User provides a LinkedIn profile URL and wants a dossier

## Steps

### Step 1: Dedup check

**Always do this first.** Query the Prospect Tracker Google Sheet to see if the
company already exists before starting research.

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_sheets import GoogleSheets

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
sheets = GoogleSheets(authenticator=auth)

# Read the "Prospect Tracker" sheet
TRACKER_ID = "1lmbAMi9p8L8655RL6ETPkvZc_YbD4WBtX7NJKLdrmyw"
data = sheets.batch_update_values(...)  # NO — use read_values
rows = sheets.read_values(TRACKER_ID, range="Sheet1!A:Z")

# Check if company name appears in any row
company_name = "Deposco"  # extracted from input
existing = [r for r in rows if company_name.lower() in str(r).lower()]
```

If duplicates found:
1. Surface the existing entry (company name, date added, source, status)
2. Ask user: "Company X already exists in the tracker (added YYYY-MM-DD). Re-research and update the dossier, or skip?"
3. If skip → stop. If re-research → continue to Step 2 with `--from-research` flag if existing research.json exists.

### Step 2: Research the company

```bash
cd /workspace/datacrew
SCRIPTS=projects/domo-customer-outreach/scripts

PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/research/06_research_company.py \
  --company "Company Name"
```

This scrapes Slack, Domo Community forums, and LinkedIn for the company.
Output: `data/EXPORTS/research/{company_slug}/research.json`

If the user provided a LinkedIn URL, the company name is extracted from the URL
or the user must specify it. The LinkedIn URL can be passed for enrichment.

### Step 3: Create the dossier (Google Doc)

```bash
cd /workspace/datacrew
SCRIPTS=projects/domo-customer-outreach/scripts

PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/output/07_create_dossier.py \
  --company "Company Name" \
  --from-research data/EXPORTS/research/{company_slug}/research.json
```

This creates a Google Doc in the CRM folder with 4 tabs:
- Overview (company facts, Domo connection, products)
- People (key personas with career timelines)
- Org Chart (reporting structure)
- Outreach Strategy (per-persona draft messages, talking points, follow-ups)

**CRM folder ID:** `1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N`

### Step 4: Share with Jae

**Gotcha #66** — Always share new Google Docs with jae@datacrew.space:

```python
from cboti.integrations.google.drive.google_drive import GoogleDrive

drive = GoogleDrive(authenticator=auth)
drive.share_file(doc_id, "jae@datacrew.space", "writer")
```

### Step 5: Sync contacts to Google Contacts

```bash
cd /workspace/datacrew
SCRIPTS=projects/domo-customer-outreach/scripts

PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/output/09_sync_contacts.py \
  --company "Company Name" \
  --from-research data/EXPORTS/research/{company_slug}/research.json
```

This upserts personas from the research into Google Contacts CRM.

### Step 6: Confirm and report

Report back to user:
- Google Doc URL
- Number of personas found
- Number of contacts synced
- Whether it was new or an update

## CLI Commands (quick reference)

```bash
cd /workspace/datacrew
SCRIPTS=projects/domo-customer-outreach/scripts

# Full pipeline (single company)
PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/research/06_research_company.py --company "Company"
PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/output/07_create_dossier.py --company "Company" --from-research data/EXPORTS/research/company/research.json
PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/output/09_sync_contacts.py --company "Company" --from-research data/EXPORTS/research/company/research.json

# Orchestration script (alternative)
PYTHONPATH=$SCRIPTS .venv/bin/python3 $SCRIPTS/../../.agents/runbooks/generate-domo-customer-outreach/scripts/main.py research --company "Company"
```

## Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `SLACK_BOT_TOKEN` | `datacrew/.env` | Slack API (xoxb-) |
| `DATACREW_SLACK_USER_OAUTH_TOKEN` | `datacrew/.env` | Slack search.messages (xoxp-) |
| `GDOC_CLIENT` | Infisical `bd78c29a` prod | Google OAuth client JSON |
| `GDOC_TOKEN` | Infisical `bd78c29a` prod | Google OAuth token JSON |
| `DC_API_TOKEN` | Infisical `3fbb4296` prod `/mdrag` | mdrag MCP auth |

**Never `source datacrew/.env`** — JSON values break `source`. Use `grep VAR file | cut -d= -f2-` or Python `os.environ`.

## Key IDs

| Resource | ID |
|----------|-----|
| CRM Folder | `1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N` |
| Prospect Tracker | `1lmbAMi9p8L8655RL6ETPkvZc_YbD4WBtX7NJKLdrmyw` |

## Gotchas

- **Always dedup first** — creating a duplicate dossier wastes time and creates confusion in the tracker
- **Always share with jae@datacrew.space** (gotcha #66) — use `drive.share_file()` after creating any new doc
- **Always use `Tabs.upsert()`** — never `write_markdown_to_tab()` which appends instead of replacing
- **`06_research_company.py` overwrites `research.json`** — use `--from-research` to seed from existing data on re-runs
- **Google Docs API rate limit: 60 writes/min** — the scripts handle this internally
- **Slack `search.messages` requires user token (xoxp-)**, not bot token
- **letta synthesis can return empty fields** — that's intentional; renderer skips them cleanly
- **Blockquotes (`> `) are stripped in Google Docs** — use `**Label:**` + regular paragraph instead
- **Use `PYTHONPATH=$SCRIPTS .venv/bin/python3`** — NOT `uv run --project` (doesn't add scripts dir to PYTHONPATH, causes `ModuleNotFoundError: No module named 'crew_config'`)

## Related

- `datacrew/.agents/runbooks/generate-domo-customer-outreach/SKILL.md` — full pipeline reference
- `datacrew/projects/domo-customer-outreach/scripts/` — pipeline scripts
- `skills/upsert-gdoc/SKILL.md` — Google Doc write skill
- `skills/infisical-auth/SKILL.md` — Infisical authentication
