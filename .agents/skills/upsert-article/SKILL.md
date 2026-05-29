---
name: upsert-article
description: >
  Draft or update a blog article. Accepts a topic (new article) or URL
  (update existing). Optionally writes to a specific Google Doc. Follows Jae's
  voice patterns and DataCrew article rules. Use for: "/upsert-article",
  "write article", "draft blog post", "update article".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# upsert-article

Draft or update blog articles in Jae's voice, with optional Google Doc output.

## When to Use

- `/upsert-article <topic>` — draft a new article on a topic
- `/upsert-article <url>` — crawl URL, extract content, rewrite/update as article
- `/upsert-article <topic or url> <gdoc-url>` — write to an existing Google Doc as a tab
- User asks to write, draft, or update a blog post or article

## Steps

### 1. Parse input

```
/upsert-article "MCP vs Skills for Domo automation"
/upsert-article "https://datacrew.space/blog/existing-article"
/upsert-article "Domo App Studio tips" 1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N
```

Extract: topic or URL, optional Google Doc ID.

### 2. Research (if needed)

If topic: use mdrag `search_web` + `crawl_url` to gather source material.
If URL: use mdrag `crawl_url` to extract existing content.

See `research` skill for mdrag auth and session setup.

### 3. Draft the article

Follow Jae's voice patterns (see `reference/jae-voice-patterns.md` in memory):

**Article rules:**
- **Target audience**: 33+ analysts/managers who grew up with Facebook, NOT coders
- **Tone**: Reassuring, approachable, not technical. "Here's how you make it real for you"
- **Core metaphor**: AI = really smart new hire; memories = onboarding docs
- **Length**: 7–10 min read (~1,500 words)
- **Personal story first**: Open with why he needed the automation
- **Educate on WHEN, not HOW**: Readers care about when to build, not mechanics
- **CTA**: Always include automation consulting + team upskilling CTA
- **Onyx Reporting** = two words, not "OnyxReporting"

**Voice patterns:**
- Conversational, no preachy sections
- Actual prompts as examples (not abstract descriptions)
- Honest about effort — "this took me 3 hours"
- Meta-commentary about AI process is OK
- No bullet-point lists of features — tell a story instead

### 4. Write to Google Doc

**If gdoc-url provided** — upsert as a tab:

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_docs import GoogleDoc, Tabs

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
doc_client = GoogleDoc(authenticator=auth)
tabs = Tabs(client=doc_client)
await tabs.upsert(document_id=GDOC_ID, title="Article: <topic>", content=article_markdown)
```

**If no gdoc-url** — create new Google Doc in CRM folder:

```python
from cboti.integrations.google.drive.google_drive import GoogleDrive

drive = GoogleDrive(authenticator=auth)
doc = await drive.create_document(name="Article: <topic>", folder_id="1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N")
# Then upsert tab with content
await tabs.upsert(document_id=doc.id, title="Article", content=article_markdown)
```

### 5. Share with Jae

```python
await drive.share_file(doc.id, "jae@datacrew.space", "writer")
```

**Always share** — gotcha #66: forgetting to add jae@datacrew.space as editor.

## Gotchas

- **`GoogleDrive.create_document()` takes `name`, NOT `title`** — wrong param = silent failure
- **`Tabs()` takes `client` (GoogleDoc instance), NOT `authenticator`** — common mistake
- **Markdown blockquotes (`> `) are stripped in Google Docs** — use bold-labeled paragraphs (`**Label:**` + regular paragraph) instead
- **Always upsert tabs, never create-then-replace** — `Tabs.upsert()` handles dedup by title
- **Always share with jae@datacrew.space** — or Jae can't edit the doc

## Related

- `research` — for gathering source material
- `upsert-gdoc` — general Google Doc write skill
- `outreach-create-dossier` — creates dossiers in same CRM folder
