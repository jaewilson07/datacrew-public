---
name: mdrag-mcp
description: >
  Connect to the DataCrew MCP server (mdrag) for web search, crawling, RAG,
  and knowledge management. Use for: "search the web", "crawl this url",
  "query knowledge base", "save to knowledge", "mdrag", "mcp".
metadata:
  version: 1.0.0
  updated: 2026-05-08
---

# mdrag-mcp

## Overview

The DataCrew MCP server (mdrag) provides web search, crawling, RAG retrieval,
and knowledge management. It sits behind Cloudflare Access at
`https://mdrag.datacrew.space/mcp/` — every request must include the CF Access
service token headers.

## Core Capabilities

- Web search via SearXNG (bypasses CF Access internally)
- Single-page and deep-site crawling with JS detection
- Knowledge base retrieval (semantic + keyword)
- URL and text ingestion into knowledge base

## When to Use

- Any web research task — prefer mdrag over generic web search
- Crawling Domo docs, community posts, or competitor pages
- Retrieving from the DataCrew knowledge base
- Ingesting URLs for future RAG retrieval

## Auth

The container has `MDRAG_AGENT_CF_CLIENT_ID` and `MDRAG_AGENT_CF_CLIENT_SECRET`
injected from Infisical. Every HTTP request to mdrag must include:

```
CF-Access-Client-Id:     $MDRAG_AGENT_CF_CLIENT_ID
CF-Access-Client-Secret: $MDRAG_AGENT_CF_CLIENT_SECRET
```

Without these headers, requests get HTTP 302 → cloudflareaccess.com.

## Primary Tools (5 agent-facing)

| Tool | Purpose |
|------|---------|
| `search_web` | SearXNG search (internal Docker network, no CF Access needed) |
| `crawl_url` | Single-page crawl with two-pass JS detection |
| `crawl_site` | BFS deep crawl up to 20 pages, domain-restricted |
| `query_rag` | Knowledge base retrieval (semantic + keyword) |
| `save_url_to_knowledge` | Ingest URLs into knowledge base |

## HTTP Endpoints (direct)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness + Mongo status |
| GET | `/api/v1/mcp/tools?tier=primary` | Tool discovery |
| POST | `/api/v1/crawl/url` | Single-page scrape |
| POST | `/api/v1/crawl/site` | BFS deep crawl |
| POST | `/api/v1/research/run` | Synchronous research workflow |

## Quick Start

### curl (health check)

```bash
curl -s https://mdrag.datacrew.space/api/v1/health \
  -H "CF-Access-Client-Id: $MDRAG_AGENT_CF_CLIENT_ID" \
  -H "CF-Access-Client-Secret: $MDRAG_AGENT_CF_CLIENT_SECRET"
```

### Python (search)

```python
import os, requests

headers = {
    "CF-Access-Client-Id": os.environ["MDRAG_AGENT_CF_CLIENT_ID"],
    "CF-Access-Client-Secret": os.environ["MDRAG_AGENT_CF_CLIENT_SECRET"],
}

resp = requests.post(
    "https://mdrag.datacrew.space/api/v1/mcp/tools/search_web",
    headers=headers,
    json={"query": "Domo App Studio card swap API"}
)
print(resp.json())
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 302 → cloudflareaccess.com | Missing CF Access headers | Ensure both `CF-Access-Client-Id` and `CF-Access-Client-Secret` are set |
| Connection refused | mdrag container down | Check `docker ps` on VPS for `mdrag` container |
| Empty search results | SearXNG down | Check `docker ps` for `searxng` container |
| 12k char response truncation | ResponseLimitingMiddleware | Add `debug=True` to tool calls for metadata |

## Key Facts

- **URL**: `https://mdrag.datacrew.space/mcp/`
- **Internal URL** (from VPS Docker network): `http://mdrag:8017`
- **36 tools total**, 5 primary agent-facing
- **ResponseLimitingMiddleware**: 12k char cap on tool responses
- **Debug mode**: `debug=True` on all tools returns metadata

## References

- `libraries/mdrag/.agents/guides/calling-mdrag-from-agents.md` — full auth + tool reference
- `libraries/mdrag/docs/MCP_TOOLS.md` — auto-generated tool schema reference

## Related Skills

- `infisical-auth` — authenticate Infisical CLI for deployments
- `create-skill` — scaffold new skills
