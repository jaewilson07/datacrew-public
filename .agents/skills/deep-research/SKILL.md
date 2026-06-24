---
name: deep-research
description: >
  Self-guided iterative deep research — searches, reads, identifies gaps, searches
  again, and synthesizes a comprehensive report with citations. Uses mdrag as the
  engine. Use for: "/deep-research", "deep dive on", "comprehensive research",
  "investigate thoroughly", "research report on".
metadata:
  version: 1.0.0
  created: 2026-06-12
---

# deep-research

Self-guided iterative research that goes beyond a single search pass. The agent
loops: search → read → extract findings → identify gaps → search again → synthesize.
Each iteration narrows the gap between what's known and what's needed.

Unlike `/research` (single-pass search + crawl), this skill runs multiple iterations
until the research question is thoroughly answered or the iteration budget is exhausted.

## Core Capabilities

- **Iterative search loop** — up to N iterations (default 3), each targeting gaps from the previous pass
- **Multi-source research** — web search, page crawling, site crawling, RAG knowledge base
- **Gap analysis** — after each iteration, explicitly identifies what's still unknown
- **Citation tracking** — every claim in the final report links to a source URL
- **Output formats** — markdown report (default), Google Doc tab, or both
- **Configurable depth** — `--iterations N`, `--depth quick|standard|exhaustive`

## When to Use

- User asks for a "deep dive" or "comprehensive research" on a topic
- A single search pass won't cover the complexity (multi-faceted questions)
- User wants a research report with citations, not just a quick answer
- Topic requires cross-referencing multiple sources
- User says "/deep-research" or "research this thoroughly"

Do NOT use for:
- Quick lookups (use `/research` instead)
- Single-URL extraction (use `/use-mdrag` `crawl_url`)
- YouTube transcript extraction (use `/research` with a YouTube URL)

## Quick Start

```
/deep-research "Domo App Studio card swap API limitations"
/deep-research "competitive landscape of Domo consulting firms" --depth exhaustive
/deep-research "AI coding agents enterprise features 2026" --iterations 5
/deep-research "Domo MCP server architecture" --gdoc 1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N
```

## Detailed Workflow

### Step 0: Parse input

Extract from the command:
- **topic** (required) — the research question
- **--iterations N** (optional, default 3) — max search-read-analyze loops
- **--depth quick|standard|exhaustive** (optional, default standard) — preset that sets iterations and breadth
- **--gdoc DOC_ID** (optional) — write final report to a Google Doc tab
- **--focus domains** (optional) — comma-separated domains to prioritize (e.g., `--focus domo.com,docs.domo.com`)

Depth presets:

| Depth | Iterations | Results per search | Pages crawled per iteration |
|-------|-----------|-------------------|---------------------------|
| quick | 1 | 3 | 2 |
| standard | 3 | 5 | 3 |
| exhaustive | 5 | 7 | 5 |

### Step 1: Authenticate to mdrag

Use the same `mdrag()` helper from `/use-mdrag`:

```bash
mdrag() {
  local base="${MDRAG_BASE_URL:-https://wikki.datacrew.space}"
  local inf="${INFISICAL_SITE_URL:-https://infisical.datacrew.space}"
  if [ ! -s /tmp/.mdrag_dc_token ]; then
    if [ -n "${DATACREW_API_TOKEN:-}" ]; then
      printf '%s' "$DATACREW_API_TOKEN" > /tmp/.mdrag_dc_token
    else
      : "${INFISICAL_CLIENT_ID:?}" "${INFISICAL_CLIENT_SECRET:?}"
      local itok
      itok=$(curl -sS -X POST "$inf/api/v1/auth/universal-auth/login" -H "Content-Type: application/json" \
        -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}" \
        | python3 -c "import sys,json;print(json.load(sys.stdin)['accessToken'])")
      curl -sS "$inf/api/v3/secrets/raw/DATACREW_API_TOKEN?environment=prod&workspaceId=3fbb4296-d4e6-4c17-83ee-b852a57a5e50&secretPath=/datacrew" \
        -H "Authorization: Bearer $itok" \
        | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('secret',d).get('secretValue',''))" > /tmp/.mdrag_dc_token
    fi
  fi
  local m="$1" p="$2"; shift 2
  curl -fsS -X "$m" "$base$p" -H "Authorization: Bearer $(cat /tmp/.mdrag_dc_token)" \
    -H "Content-Type: application/json" "$@"
}
```

### Step 2: Check knowledge base first

Before hitting the web, check if mdrag's RAG already has relevant content:

```bash
# Initialize MCP session for query_rag (REST-only tools don't need this)
SESSION_ID=$(curl -sS -D - -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $(cat /tmp/.mdrag_dc_token)" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"deep-research","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | head -1 | awk '{print $2}' | tr -d '\r')

# Query RAG
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $(cat /tmp/.mdrag_dc_token)" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_rag","arguments":{"query":"TOPIC","limit":3}}}'
```

If RAG returns relevant results, incorporate them as **Iteration 0 findings** and note
which aspects they cover vs. which still need web research.

### Step 3: Iterative research loop

For each iteration (1 through N):

#### 3a. Formulate search query

- **Iteration 1**: Use the original topic as the search query
- **Iteration 2+**: Formulate queries targeting the **specific gaps** identified in Step 3d
  - Be specific: "Domo App Studio layout API append-only behavior" not just "Domo App Studio"
  - Use different phrasings than previous iterations to surface new sources

#### 3b. Search

```bash
mdrag POST /api/v1/searxng/search -d "{\"query\":\"SEARCH_QUERY\",\"result_count\":RESULTS_PER_SEARCH}"
```

If `--focus` domains were specified, filter results to prioritize those domains.

#### 3c. Crawl top results

For each promising result URL (up to PAGES_PER_ITERATION):

```bash
mdrag POST /api/v1/crawl/url -d "{\"url\":\"RESULT_URL\"}"
```

For sites that look like comprehensive documentation (e.g., docs.domo.com subpages):

```bash
mdrag POST /api/v1/crawl/site -d "{\"url\":\"SITE_URL\",\"max_depth\":2,\"max_pages\":10}"
```

**Extract from each page:**
- Key facts, claims, data points
- Source URL (for citations)
- Any references/links to other relevant pages (add to crawl queue)

#### 3d. Gap analysis

After crawling all results for this iteration, explicitly assess:

```
FINDINGS SO FAR:
- [fact 1] (source: URL)
- [fact 2] (source: URL)
- ...

GAPS (still unknown):
- [gap 1]: [why it matters for the research question]
- [gap 2]: [why it matters for the research question]
- ...

NEXT SEARCH QUERIES (targeting gaps):
- "[query targeting gap 1]"
- "[query targeting gap 2]"
```

**Stopping criteria** — stop iterating early if:
1. All major gaps are filled
2. Last iteration produced no new findings
3. Sources are repeating (same domains, same content)

#### 3e. Save iteration findings

Write findings to a working file so context isn't lost between iterations:

```bash
# Append to working notes
mkdir -p /tmp/deep-research
echo "## Iteration $N" >> /tmp/deep-research/notes.md
echo "$FINDINGS" >> /tmp/deep-research/notes.md
```

### Step 4: Synthesize final report

After all iterations (or early stop), compose the final report:

**Structure:**
```markdown
# Deep Research: [TOPIC]

**Date:** [today]
**Iterations:** [N completed]
**Sources:** [unique URL count]

## Executive Summary
[2-3 paragraph overview of findings — the answer to the research question]

## Key Findings

### [Finding Category 1]
- [Specific finding] ([source](URL))
- [Specific finding] ([source](URL))

### [Finding Category 2]
- [Specific finding] ([source](URL))

## Gaps & Limitations
- [What we couldn't find or verify]
- [Areas where sources conflicted]

## Sources
1. [Title](URL) — [one-line description]
2. [Title](URL) — [one-line description]
```

**Rules:**
- Every factual claim must have a citation link
- If sources conflict, note the conflict and which source seems more authoritative
- Executive summary answers the research question directly
- Gaps section is honest — don't paper over what's unknown

### Step 5: Write output

**Local file (always):**
```bash
mkdir -p /tmp/deep-research
# Write final report to /tmp/deep-research/report.md
```

**Google Doc (if --gdoc provided):**
```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_docs import GoogleDoc, Tabs

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
doc_client = GoogleDoc(authenticator=auth)
tabs = Tabs(client=doc_client)
await tabs.upsert(document_id=GDOC_ID, title="Deep Research: TOPIC", content=report_markdown)
```

**Save to knowledge base (optional):**
```bash
# Save key source URLs to mdrag RAG for future queries
mdrag POST /api/v1/readings/save -d '{"urls":["URL1","URL2"]}'
```

### Step 6: Store learnings in MemFS

Write a summary to `$MEMORY_DIR/project/<domain>/research/<topic-slug>.md` so future
sessions can build on this research rather than starting from scratch.

## Gotchas

- **12k char response cap** — mdrag's `ResponseLimitingMiddleware` truncates at 12k. For long pages, the crawl response may be cut off. Use `debug=True` for metadata (word count, etc.) and consider `crawl_site` for structured docs.
- **YouTube URLs cannot be crawled** — `crawl_url` returns 0 words on YouTube. Use the youtube-research runbook or `POST /api/v1/readings/save` instead.
- **MCP session required for query_rag** — must initialize before calling. Session ID goes in `Mcp-Session-Id` header.
- **`Tabs.upsert()` not `write_markdown_to_tab`** — the latter always appends.
- **Don't re-crawl the same URL** — track crawled URLs across iterations to avoid wasting calls.
- **Gap analysis is the key differentiator** — if you skip honest gap analysis, this degrades to a multi-pass `/research`. The value is in targeting gaps.
- **SearXNG rate limits** — don't blast 10 searches in a row. Space requests naturally across iterations.

## Related Skills

- `research` — single-pass search + crawl (simpler, faster for quick lookups)
- `use-mdrag` — full mdrag reference (auth, all endpoints, browser sessions)
- `check-mdrag` — verify mdrag is up before starting research
- `outreach-create-dossier` — uses research as a sub-step for prospect profiles
- `upsert-gdoc` — Google Doc write skill
