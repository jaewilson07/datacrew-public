---
name: upsert-gdoc
description: >
  Write or update Google Doc tabs using cboti. Use for: "push to google doc",
  "update gdoc", "write to google doc", "upsert gdoc tab", "publish article".
metadata:
  version: 1.0.0
  updated: 2026-05-08
---

# upsert-gdoc

## Overview

Write markdown content to Google Doc tabs using cboti's `GoogleDoc.Tabs.upsert()`.
Handles auth, tab lookup, clearing, and writing in one call. This is the ONLY
safe way to write to Google Docs — never use `write_markdown_to_tab` (it appends)
and never create-then-replace (it creates duplicates).

## Core Capabilities

- **Upsert tabs**: Find by title and replace content, or create if missing
- **Multi-tab docs**: Push multiple tabs to a single document in one run
- **Markdown conversion**: cboti handles markdown-to-GDoc rendering
- **Auth handled**: Reads `GDOC_CLIENT` and `GDOC_TOKEN` from env/Infisical

## When to Use

- Publishing drafted articles to a Google Doc
- Updating an existing tab with revised content
- Pushing multiple articles as separate tabs in one doc
- Any time you need to write markdown to a Google Doc

## Quick Start

```bash
# Push a single tab to a Google Doc
python3 .agents/skills/upsert-gdoc/scripts/upsert_gdoc_tab.py \
  --doc-id 1zHb6nnleJbyeOak-UxRnhXZsOxe67c6JD7zsj6dBitU \
  --title "My Article" \
  --file articles/my-article/index.md

# Push multiple tabs
python3 .agents/skills/upsert-gdoc/scripts/upsert_gdoc_tab.py \
  --doc-id 1zHb6nnleJbyeOak-UxRnhXZsOxe67c6JD7zsj6dBitU \
  --title "Tab 1" --file articles/article-1/index.md \
  --title "Tab 2" --file articles/article-2/index.md
```

## Detailed Workflow

### Step 1: Prepare your markdown

Write your content as a markdown file. Follow the gotchas in
[references/cboti-gotchas.md](./references/cboti-gotchas.md) to avoid
rendering issues.

Key rules:
- **No blockquotes** (`> `) — they get stripped. Use **bold-labeled paragraphs** instead
- **No bare HTML** — cboti's converter ignores most HTML tags
- **Mermaid diagrams** — render as code blocks, not live diagrams

### Step 2: Run the upsert script

```bash
python3 .agents/skills/upsert-gdoc/scripts/upsert_gdoc_tab.py \
  --doc-id <GOOGLE_DOC_ID> \
  --title "Tab Title" \
  --file path/to/content.md
```

The script will:
1. Authenticate with Google using `GDOC_CLIENT` + `GDOC_TOKEN` from env
2. Find the tab by title (or create it if it doesn't exist)
3. Clear existing content and write the new markdown
4. Print the tab ID and URL

### Step 3: Verify

Open the Google Doc and check:
- Tab title matches what you specified
- Content rendered correctly (no stripped blockquotes, no broken formatting)
- Links are clickable

## Gotchas

See [references/cboti-gotchas.md](./references/cboti-gotchas.md) for the full
list. The top 3 that bite every time:

1. **`write_markdown_to_tab` always appends** — use `Tabs.upsert()` with `mode="replace"`
2. **Blockquotes are stripped** — use `**Label:**` + regular paragraph instead
3. **Tab IDs are document-scoped** — never reuse a tab ID from a different doc

## References

- **[cboti-gotchas.md](./references/cboti-gotchas.md)** — Full list of Google Docs rendering gotchas
- **[upsert_gdoc_tab.py](./scripts/upsert_gdoc_tab.py)** — Reusable upsert script

## Related Skills

- `create-skill` — scaffold new skills
- `mdrag-mcp` — research content before writing
