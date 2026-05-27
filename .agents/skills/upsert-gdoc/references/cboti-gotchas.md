# cboti Google Docs Gotchas

Hard-won lessons from pushing markdown to Google Docs via cboti.

## Tab Writing

### `write_markdown_to_tab` always appends
Never use `Tab.write_markdown_to_tab()`. It appends content instead of replacing.
Use `Tabs.upsert(doc_id, title, content, mode="replace")` which handles lookup,
clearing, and writing in one call.

### Tab IDs are document-scoped
A tab ID from one doc fails on another. Always `Tabs.list(doc_id)` for the
target doc before writing. The upsert script handles this automatically.

### Always upsert, never create-then-replace
`Tabs.upsert(doc_id, title, content)` finds by title and replaces. Creating new
docs or appending creates duplicates.

## Markdown Rendering

### Blockquotes (`> `) are stripped
cboti's converter drops them entirely. Use bold-labeled paragraphs instead:

**Bad:**
```markdown
> **Note:** This only works for Admin roles.
```

**Good:**
```markdown
**Note:** This only works for Admin roles.
```

### Mermaid diagrams render as code blocks
Google Docs doesn't support Mermaid. They render as plain code blocks. If you
need diagrams, consider linking to an external Mermaid Live Editor URL.

### Bare HTML is ignored
Most HTML tags (`<details>`, `<div>`, etc.) are stripped. Use markdown-native
formatting only.

### Tables work but are limited
Simple markdown tables render fine. Complex tables (merged cells, colspans)
don't work. Keep tables simple.

## Auth

### `GDOC_CLIENT` and `GDOC_TOKEN` are JSON strings
They're stored in Infisical at `/datacrew` path. The values are JSON strings
(often with surrounding quotes from Infisical). The upsert script handles
quote-stripping automatically.

### Don't `source datacrew/.env`
JSON values in `.env` break `source`. Use `grep VAR file | cut -d= -f2-`
or Python `os.environ` to read them.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Tab not found` | Tab ID from wrong doc | Use `Tabs.upsert()` which finds by title |
| `Permission denied` | Wrong Google account | Check `GDOC_CLIENT`/`GDOC_TOKEN` match the doc owner |
| `Duplicate tabs` | Used `create` instead of `upsert` | Always use `Tabs.upsert()` |
| `Blank content` | Blockquotes-only content | Replace `> ` with bold-labeled paragraphs |
