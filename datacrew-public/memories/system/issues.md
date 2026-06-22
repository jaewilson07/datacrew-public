---
description: Top gotchas for a public-facing community agent.
---
# Gotchas

## Google Docs

- **`write_markdown_to_tab` always appends** — use `Tab.write(content, mode='replace')` or `Tabs.upsert(doc_id, title, content)` which handles lookup, clearing, and writing in one call
- **Markdown blockquotes (`> `) are stripped** — cboti's converter drops them entirely. Use bold-labeled paragraphs (`**Label:**` + regular paragraph) instead
- **Tab IDs are document-scoped** — a tab ID from one doc fails on another. Always `Tabs.list(doc_id)` for the target doc before writing
- **Always upsert tabs, never create-then-replace** — `Tabs.upsert(doc_id, title, content)` finds by title and replaces. Creating new docs or appending creates duplicates

## Slack Posting

- **One post per item** — NEVER combine multiple items into one message
- **Blank line between text and URLs** — separate description from links
- **Post first, then delete old** — NEVER delete before replacement is live
- **Use `SLACK_BOT_TOKEN`** for DUG Slack API calls
- **Do NOT `source datacrew/.env`** — JSON values break `source`. Use `grep VAR file | cut -d= -f2-` or Python `os.environ`
- **ALWAYS use threading** — reply to the parent message with `replyTo` to keep DMs clean. Never post as a new top-level message when responding to a specific message

## cboti Patterns

- **`GoogleSheets.batch_update()` ≠ `batch_update_values()`** — the former is spreadsheet-level metadata/formatting; the latter is for cell content
- **TableBlock cells must be `ContentBlock`, not `str`** — if you pass raw strings, rendering breaks silently
- **cboti editable install `.pth` points to Docker `/workspace/` paths** — add `sys.path.insert(0, '../libraries/cboti/src')` when importing with direct python binary

## LettaWikiClient (wiki LLM calls)

- **CRITICAL: ALWAYS use `--tools ""`** — strips all tools so the agent focuses on the prompt instead of its conversational persona. Without this, the community bot responds with "Hey! I'm here to help!" instead of following structured prompts. This was the root cause of concept extraction returning 0 concepts
- **`--tools ""` does NOT work with stdin mode (`-p -`)** — must pass prompt as CLI arg. On single-user VPS, ps visibility is acceptable
- **ALWAYS use `--yolo`** when running `letta -p` headless — without it, the agent waits for approval and can block indefinitely
- **ALWAYS use `--output-format json`** — gives timing/usage metadata for observability
- **ALWAYS use `--max-turns 2`** — prevents multi-turn loops that could burn tokens. (1 is too restrictive — kills the response before it completes)
- **Safety contract: read-only LLM calls only** — `letta -p --yolo` auto-approves ALL tool calls, so never use it for state-modifying operations (posting to Slack, writing files, deleting data)
- **Performance: simple prompts 3-5s, wiki prompts 15-80s** — set timeout to 180s for wiki operations
- **Gap detection LLM suggestions timeout** — the `_suggest_articles` step can exceed 90s. Increase timeout or make it optional
- **Conversation proliferation** — each `letta -p` creates a NEW conversation. Consider `--conversation <id>` to reuse a wiki conversation
- **`compile_wiki` → MongoDB ingestion is missing** — wiki articles are written to vault filesystem but NOT pushed to MongoDB for RAG search. Need to wire this feedback loop
- **`model` param is a no-op** — accepted for API compat but LettaWikiClient routes through the agent's configured model. Document in docstrings.
- **YouTube transcript ingestion blocked from VPS** — YouTube blocks server-side transcript requests from VPS IPs. Need a proxy service or browser-based extraction (e.g., Playwright, crawl4ai with browser)
- **Raw page directory structure** — vault expects `raw/<topic>/<page-slug>/content.md`, NOT `raw/<topic>/content.md`
- **Wiki vault is write-only for articles** — there is no `load_article()` method. The vault can save compiled articles but cannot read them back. Read files directly from the vault filesystem path instead
- **`list_articles` returns full paths, not slugs** — match by `p.stem` to find articles by slug
- **`TypologyWorkflow.generate()` returns `Typology`**, not `TypologyResult` — the result has `.nodes` and `.root_node_ids`, not `.typology.root`
- **`ConceptExtractor.extract()` returns `list[ExtractedConcept]`** — not an object with `.concepts`. ExtractedConcept has no `.description` field

## Bryce Identities — DIFFERENT people

- **Bryce Cindrich** — GitHub: `brycewc`, Slack: `bryce.cindrich` (U08JYQNT7SQ), Domo MajorDomo. Author of: Postman collection (`brycewc/domo-product-apis`), Code Engine package (`domo-product-apis-supplemental`), Domo Toolkit Chrome extension (`brycewc/domo-toolkit`), domo-scripts, domo-documentation-hub. Based in Salt Lake City, UT.
- **Brock Cooper** — GitHub: `brockcooper`. Author of `domo_python` (2018, PyPI package). Different person entirely.
- **NEVER confuse them** — Jae has corrected this explicitly. Bryce Cindrich wrote the Postman collection AND the Code Engine supplemental package.

## Pydantic Models (crew-dcs)

- **Don't use `from __future__ import annotations`** in pydantic model files — it breaks `list[dict]` resolution in Field() type hints
- **API returns `null` for optional strings** — use `str | None = None`, not `str = ""`. Found in FilesetResponse.description
- **`list` is a reserved Python name** — can't use it as a field name. Rename to `permissions` with `alias="list"`
- **`extra="ignore"`** is essential — API responses often include surprise fields not in the model
- **`populate_by_name=True`** required so both snake_case and camelCase work for model construction

## AppStudio / Page Layout

- **AppStudio `theme` is an opaque dict** — Domo doesn't document the structure. Extract from existing apps via `get_appstudio_by_id()` to see `theme.backgroundColor`, `theme.textColor`, `theme.darkMode`, etc.
- **`PageLayoutContent` types have different display flags** — CARD/VARIABLE/HEADER have bool flags (hideBorder, hideMargins, hideFooter, etc.); BUTTON/TABS/TAB_CONTENT/FORM have null flags
- **Only CARD content can have `style` dict** — includes `sourceId`, `textColor`, etc. TABS also has style
- **`PageLayoutBackground` requires `type` field** — "COLOR" or "IMAGE". For color backgrounds, set `selectedColor`, `textColor`, `darkMode`, `alpha`
- **Layout update requires write lock** — `DomoPageLayout.update()` acquires lock, updates, releases. Don't call the route directly

## crew-dcs Testing

- **Mock patching: patch at SOURCE, not import location** — When a function does `from .core import DomoDataset` inside its body (lazy import), `patch("module.DomoDataset")` fails. Patch at `crew_dcs.classes.DomoDataset.core.DomoDataset` instead
- **`cl` module mock** — crew-logger is private/404. Mock at `/tmp/cl_mock/`, install via `uv pip install -e . --python .venv/bin/python`
- **pytest discovery** — `pyproject.toml` needs `python_files = ["test_*.py", "*_tests.py"]` to discover `*_tests.py` files (the existing naming convention in crew-dcs)

## Public Agent Specific

- **Slack rate limits** — don't rapid-fire messages. Space them out
- **Don't pretend to be human** — I'm a bot. Be upfront about it
- **Check before sharing links** — make sure URLs are publicly accessible, not internal/VPS-only
- See [[system/support/hygiene.md]] for additional public agent boundaries
