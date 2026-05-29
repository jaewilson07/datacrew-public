---
name: add-to-dumpster-fire
description: >
  Add an initiative to the dumpster fire retrospective. Upserts to the Google Doc
  (source of truth), then syncs to Slack Canvas (read-only mirror). Deduplicates
  by thread URL. Use for: "/add-to-dumpster-fire", "add to retro", "update
  retrospective", "dumpster fire".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# add-to-dumpster-fire

Add or update an initiative in the dumpster fire retrospective. GDoc is source of truth; Canvas is a read-only mirror.

## When to Use

- `/add-to-dumpster-fire` — add current conversation context as a new initiative
- `/add-to-dumpster-fire <thread-url>` — add a specific Slack thread
- User says "add this to the dumpster fire" or "add to retro"

## Steps

### 1. Gather context

If thread URL provided: read the thread, summarize what's being worked on and why.
If no URL: use current conversation context to identify the initiative.

### 2. Dedup check

Read the retrospective Google Doc (ID: `1tmx0eNoHlsgh1xRdnpq9BBDaHhiYr9hlYHLic-d7vw`) and search for the thread URL. If found, merge into the existing entry instead of creating a duplicate.

### 3. Format the entry

Every initiative follows this template:

```markdown
## [Initiative Name]

🔄 [One-line status / description]

[Optional: Key insight or context]

- [Slack Thread](URL)
- [Doc Link 1](URL)

YYYY-MM-DD - [Activity summary]

**Outcomes**

[Concrete outcomes, or "None yet"]

**To Do**

- [Action item 1]
```

**Template rules:**
- Initiative Name: short, scannable heading
- One-line status: start with emoji (🔄 🚧 ✅ ❌ ⏳)
- Links: at minimum the Slack thread
- Date + Activity: chronological, newest first
- Outcomes: write "None yet" if nothing yet
- To Do: write "None" if nothing pending

### 4. Upsert to Google Doc

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_docs import GoogleDoc, Tabs

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
doc_client = GoogleDoc(authenticator=auth)
tabs = Tabs(client=doc_client)

# Read current content, find existing entry, merge or append
await tabs.upsert(document_id="1tmx0eNoHlsgh1xRdnpq9BBDaHhiYr9hlYHLic-d7vw", title="Dumpster Fire", content=updated_content)
```

### 5. Sync to Slack Canvas

```bash
python3 .agents/runbooks/update-retrospective/scripts/main.py --sync
```

Or directly via cboti:

```python
from cboti.slack.canvas_client import CanvasClient

canvas = CanvasClient(token=SLACK_BOT_TOKEN)
# Use canvases.edit (plural, NOT canvas.edit)
# Operation: "replace" with markdown content
```

**Canvas ID**: `F0B6GCEKRMY`

## Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `RETRO_GDOC_ID` | `1tmx0eNoHlsgh1xRdnpq9BBDaHhiYr9hlYHLic-d7vw` | Google Doc ID for retrospective |
| `RETRO_CANVAS_ID` | `F0B6GCEKRMY` | Canvas ID to update |
| `DATACREW_SLACK_BOT_TOKEN` | (from env) | Bot token for Slack API |

## Gotchas

- **`canvases.edit` not `canvas.edit`** — singular form returns `unknown_method`
- **To rename canvas**: use `operation: "rename"` with `title_content` (not `document_metadata_update` or `set_title`)
- **GDoc is source of truth** — never edit the Canvas directly; always edit GDoc then sync
- **Blockquotes stripped in GDoc** — replace `> ` with `**Label:**` + regular paragraph
- **Dedup by thread URL** — if URL already exists in the doc, merge instead of creating duplicate

## Related

- `update-retrospective` runbook (`.agents/runbooks/update-retrospective/`) — full runbook with reaction lifecycle
- `upsert-gdoc` — Google Doc write skill
- `research` — for gathering context before adding an initiative
