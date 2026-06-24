---
name: outreach-create-coverletter
description: >
  Create a tailored cover letter for a Domo or data platform job posting. Maps
  Jae's resume and consulting experience to the specific role requirements, generates
  a Google Doc in the CRM folder, and shares with jae@datacrew.space.
  Use for: "/outreach/create-coverletter", "cover letter", "write cover letter",
  "tailor application".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# outreach-create-coverletter

Generate a tailored cover letter for a job posting. Crawls the job URL, extracts
requirements, maps Jae's experience to each requirement, and creates a polished
Google Doc.

## When to Use

- User says `/outreach/create-coverletter <job-url>`
- User asks to write a cover letter for a specific job
- User provides a job posting URL and wants a tailored application

## Steps

### Step 1: Crawl the job posting

Use mdrag MCP to extract the job posting content:

```bash
# Via mdrag MCP
curl -sS -X POST "https://wikki.datacrew.space/api/v1/mcp/tools/crawl_url" \
  -H "Authorization: Bearer $DATACREW_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "<job-url>", "js_render": true}'
```

Or use the `crawl_url` MCP tool directly if registered.

### Step 2: Extract job requirements

From the crawled content, extract:
- Job title
- Company name
- Required qualifications (must-haves)
- Preferred qualifications (nice-to-haves)
- Key responsibilities
- Team/context details
- Salary range (if listed)

### Step 3: Map Jae's experience

Jae's core experience to map against:

| Area | Jae's Background |
|------|-------------------|
| Domo | 5+ years vendor consultant, built Domo User Group, Fortune 500 Domo deployments |
| Staff Engineering | Sony Fortune 500 Staff Engineer — platform architecture, data pipelines |
| AI/ML | AI automation consulting, agent building (Letta, MCP, cboti), team upskilling |
| Data Architecture | Microservices, config-driven design, API-first platforms |
| Consulting | Independent consultant at $275/hr, staff aug engagements, 1099/contractor |
| Community | Domo User Group co-founder, YouTube @datacrew.space, Connections Tour speaker network |
| Tech Stack | Python, FastAPI, Docker, Google Workspace APIs, MCP protocol, cboti, mdrag |

**Positioning rules:**
- For IC roles: lead with hands-on Domo expertise, mention DataCrew after rapport
- For Manager/Director roles: lead with strategic expertise + DataCrew
- For VP+ roles: lead with DataCrew consulting practice, COE architecture

### Step 4: Generate the cover letter

Write the cover letter following Jae's voice patterns:
- Conversational, not stiff
- Specific examples, not generic claims
- Honest about effort and scope
- No preachy sections or filler paragraphs
- Short paragraphs, scannable

Structure:
1. Opening — why this role caught attention (specific, not generic)
2. Body — 2-3 paragraphs mapping experience to requirements (with evidence)
3. Close — enthusiasm + next step (not "I look forward to hearing from you")

### Step 5: Create Google Doc

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_drive import GoogleDrive
from cboti.integrations.google.drive.google_docs import GoogleDoc, Tabs

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
drive = GoogleDrive(authenticator=auth)

# Create doc in CRM folder
CRM_FOLDER_ID = "1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N"
doc = await drive.create_document(name=f"Cover Letter - {company_name}", folder_id=CRM_FOLDER_ID)

# Write cover letter
doc_client = GoogleDoc(authenticator=auth)
tabs = Tabs(client=doc_client)
await tabs.upsert(document_id=doc.id, title="Cover Letter", content=cover_letter_markdown)

# Share with Jae
drive.share_file(doc.id, "jae@datacrew.space", "writer")
```

### Step 6: Report

Report back to user:
- Google Doc URL
- Job title and company extracted
- Key requirements mapped
- Any gaps or weak matches flagged

## Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `GDOC_CLIENT` | Infisical `bd78c29a` prod | Google OAuth client JSON |
| `GDOC_TOKEN` | Infisical `bd78c29a` prod | Google OAuth token JSON |
| `DATACREW_API_TOKEN` | Infisical `3fbb4296` prod `/datacrew` | mdrag MCP auth |

## Key IDs

| Resource | ID |
|----------|-----|
| CRM Folder | `1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N` |

## Gotchas

- **Always share with jae@datacrew.space** (gotcha #66) — use `drive.share_file()` after creating any new doc
- **`GoogleDrive.create_document()` takes `name`, NOT `title`**
- **`Tabs()` takes `client` (GoogleDoc instance), NOT `authenticator`**
- **Always use `Tabs.upsert()`** — never `write_markdown_to_tab()` which appends
- **Blockquotes (`> `) are stripped in Google Docs** — use `**Label:**` + regular paragraph
- **Job posting pages often need JS rendering** — use `js_render: true` on crawl_url
- **Some job boards block crawlers** — if crawl returns 0 words, ask user to paste the job description

## Related

- `skills/outreach-create-dossier/SKILL.md` — full dossier creation
- `skills/upsert-gdoc/SKILL.md` — Google Doc write skill
- `skills/mdrag-mcp/SKILL.md` — mdrag MCP for web crawling
