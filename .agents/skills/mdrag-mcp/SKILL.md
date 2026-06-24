---
name: mdrag-mcp
description: >
  Connect to the DataCrew MCP server (mdrag) at wikki.datacrew.space for web search,
  crawling, RAG, wiki, and knowledge management. Use for: "search the web",
  "crawl this url", "query knowledge base", "save to knowledge", "mdrag", "mcp".
metadata:
  version: 2.0.0
  updated: 2026-05-28
---

# mdrag-mcp

## Overview

The DataCrew MCP server (mdrag) provides web search, crawling, RAG retrieval,
wiki management, and knowledge management. It is unified behind the Wikki gateway
at `https://wikki.datacrew.space` — every request must include a `dc_` JWT Bearer token.

**`mdrag.datacrew.space` is retired** — it 301-redirects to `wikki.datacrew.space`.
CF Access headers are DEPRECATED and no longer needed.

## Core Capabilities

- Web search via SearXNG (proxied internally through wikki)
- Single-page and deep-site crawling with JS detection
- Knowledge base retrieval (semantic + keyword)
- Wiki search, compilation, and linting
- URL and text ingestion into knowledge base
- Calendar event extraction from URLs
- AI-assisted research workflows

## When to Use

- Any web research task — prefer mdrag over generic web search
- Crawling Domo docs, community posts, or competitor pages
- Retrieving from the DataCrew knowledge base or wiki
- Ingesting URLs for future RAG retrieval
- Extracting structured event data from event pages

## Auth

Every request must include a `dc_` Bearer token:

```
Authorization: Bearer dc_<service-token>
```

Service tokens are no-expiry JWTs issued by the datacrew.space identity service.
Get one at `https://datacrew.space/account` (Log in → Developer → Service tokens → Create).
The canonical agent token is stored in Infisical at `homeserver:/datacrew` as `DATACREW_API_TOKEN`.

Anonymous requests get HTTP 401. Tokens with insufficient scope get HTTP 403.

## Primary Tools (10 agent-facing)

| Tool | Purpose |
|------|---------|
| `search_web` | SearXNG search (internal Docker network) |
| `crawl_url` | Single-page crawl with two-pass JS detection |
| `crawl_site` | BFS deep crawl up to 20 pages, domain-restricted |
| `query_rag` | Knowledge base retrieval (semantic + keyword) |
| `save_url_to_knowledge` | Ingest URLs into knowledge base |
| `save_text_to_knowledge` | Ingest raw text into knowledge base |
| `query_wiki` | Wiki search (semantic + keyword) |
| `compile_wiki` | LLM-compile raw pages → wiki articles |
| `research_with_ai` | AI-assisted research workflow |
| `search_graph` | Graph-based knowledge search |

## HTTP Endpoints (direct)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness + Mongo status |
| GET | `/api/v1/mcp/tools?tier=primary` | Tool discovery (10 primary tools) |
| POST | `/api/v1/crawl/url` | Single-page scrape |
| POST | `/api/v1/crawl/site` | BFS deep crawl |
| POST | `/api/v1/research/run` | Synchronous research workflow |
| POST | `/api/v1/searxng/search` | Web search via internal SearXNG |
| POST | `/api/v1/wiki/compile` | LLM-compile raw pages → wiki articles |
| GET | `/api/v1/wiki/search` | Search wiki (`?semantic=true` for vector) |
| POST | `/api/v1/calendar/extract-event-from-url` | Extract structured event from URL |

## Quick Start

### curl (health check)

```bash
curl -s https://wikki.datacrew.space/api/v1/health \
  -H "Authorization: Bearer $DATACREW_API_TOKEN"
```

### Python (search)

```python
import os, requests

headers = {
    "Authorization": f"Bearer {os.environ['DATACREW_API_TOKEN']}",
}

resp = requests.post(
    "https://wikki.datacrew.space/api/v1/mcp/tools/search_web",
    headers=headers,
    json={"query": "Domo App Studio card swap API"}
)
print(resp.json())
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 401 | Missing `Authorization` header | Add `Authorization: Bearer dc_<token>` to every request |
| HTTP 403 | Token has insufficient scope | Generate a new service token at `https://datacrew.space/account` |
| HTTP 301 to `wikki.datacrew.space` | Using retired `mdrag.datacrew.space` hostname | Update all calls to use `https://wikki.datacrew.space` |
| HTTP 502 | mdrag container down or crashed | Check `docker logs mdrag --tail 50` on VPS |
| Empty search results | SearXNG down | Check `docker ps` for `searxng` container |
| 12k char response truncation | ResponseLimitingMiddleware | Add `debug=True` to tool calls for metadata |

## Key Facts

- **URL**: `https://wikki.datacrew.space/mcp/` (trailing slash required for MCP)
- **Internal URL** (from VPS Docker network): `http://mdrag:8017`
- **10 primary tools** (36 total including secondary + internal)
- **ResponseLimitingMiddleware**: 12k char cap on tool responses
- **Debug mode**: `debug=True` on all tools returns metadata
- **SearXNG**: No public direct route to `search.datacrew.space` — must use `search_web` tool or `POST /api/v1/searxng/search` through wikki

## References

- `libraries/mdrag/.agents/guides/calling-mdrag-from-agents.md` — full auth + tool reference
- `libraries/mdrag/.agents/runbooks/mcp-server/SKILL.md` — deploy + gotchas
- `libraries/mdrag/.agents/runbooks/cf-access-auth/SKILL.md` — DEPRECATED (CF Access removed)
- `libraries/mdrag/docs/MCP_TOOLS.md` — auto-generated tool schema reference

## Related Skills

- `infisical-auth` — authenticate Infisical CLI for deployments
- `create-skill` — scaffold new skills
