---
description: Wiki LLM architecture — all wiki operations use letta -p via LettaWikiClient
---
# Wiki LLM Architecture

## Core Change

All wiki LLM operations now use `letta -p` (headless CLI) via `LettaWikiClient` instead of `LLMCompletionClient` (OpenAI).

## LettaWikiClient

- **Location:** `src/integrations/letta/wiki_client.py`
- **Default agent:** `agent-61955fc7-fd63-43c3-b955-6bd02bea6693` (wiki-operations agent — DO NOT use the community bot agent)
- **CLI flags:** `--yolo` (skip approval, required for headless) + `--output-format json` (timing/usage metadata) + `--max-turns 2` (prevent multi-turn loops)
- **Prompt passing:** ALWAYS via stdin (`letta -p -`) — passing prompt as CLI arg leaks content in `ps` output on shared hosts
- **Timeout:** 180s default (wiki prompts take 15-80s; simple prompts finish in 3-5s)
- **Methods:**
  - `prompt(text)` → returns plain text response
  - `prompt_json(text)` → returns parsed JSON
  - `parse_json(text)` → static method, handles markdown fences + embedded JSON

## CRITICAL: Why NOT the Community Bot Agent

The community bot agent (`agent-5afcfa48-81d3-430f-87fe-0a814fecff7e`) has a conversational persona ("Hey! I'm here to help!") that **overrides structured prompts**. When `letta -p` sends a JSON-formatting instruction, the community bot's persona wins and returns conversational text instead of JSON. This caused:
- `ConceptExtractor.extract()` returning 0 concepts because the agent ignored the structured output instruction
- `prompt_json()` calls failing because the response wasn't valid JSON

The dedicated wiki-operations agent (`agent-61955fc7-fd63-43c3-b955-6bd02bea6693`) has a structured persona that follows JSON formatting instructions. Always use it for wiki LLM calls.

## Workflows Using LettaWikiClient

- `CompileWorkflow` — wiki article compilation
- `TypologyWorkflow` — hierarchical category scaffolding
- `ConceptExtractor` — named entity extraction
- `GapDetector` — knowledge gap detection
- `WikiBridge` — cross-source linking (wiki ↔ RAG ↔ graph)
- `RoundtripWorkflow` — extract/modify/recompile
- `LintWorkflow` — quality checks + inconsistency detection
- `ResearchWorkflow` — SearXNG → crawl4ai → archive → LLM learnings

## Mock Pattern for Tests

Old: `llm.create.return_value = Mock(choices=[Mock(message=Mock(content='...'))])`
New: `letta.prompt.return_value = 'plain text response'`

For JSON: `letta.prompt.return_value = '[{"slug": "test"}]'`

## Performance

- **Simple prompts:** 3-5s (quick lookups, short responses)
- **Wiki prompts:** 15-80s (compile, typology, gap detection, multi-article tasks)
- **Gap detection LLM suggestions:** can timeout at 90s — increase timeout or make optional
- Set `letta -p` timeout to 180s for safety margin

## Vault Gotchas

- **Wiki vault is write-only for articles** — there is no `load_article()` method. The vault can write compiled articles to disk but cannot read them back. If you need article content, read the file directly from the vault filesystem path instead.
- Raw page directory structure: `raw/<topic>/<page-slug>/content.md`

## Known Issues

- Wiki articles NOT ingested into MongoDB RAG yet — need compile → MongoDB feedback loop
- YouTube transcript ingestion blocked from VPS — YouTube blocks server-side requests; need proxy or browser-based extraction
