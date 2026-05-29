---
name: research
description: >
  Smart web research via mdrag MCP. Detects YouTube URLs (transcript), web URLs
  (crawl), or plain topics (search + crawl). Optionally writes results to a
  Google Doc tab. Use for: "/research", "research this", "look up", "crawl this",
  "youtube transcript".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# research

Smart research command that routes to the right mdrag tool based on input type.

## When to Use

- `/research <topic or url>` — any web research task
- `/research <topic> --gdoc <gdoc-url>` — write results to a Google Doc tab
- User asks to look up, crawl, or research anything

## Smart URL Detection

| Input Type | Detection | Tool Used |
|------------|-----------|-----------|
| YouTube URL | `youtube.com` or `youtu.be` in URL | mdrag `research/youtube-research` runbook → `POST /api/v1/readings/save` |
| Web URL | starts with `http` | mdrag `crawl_url` MCP tool |
| Plain topic | anything else | mdrag `search_web` → `crawl_url` top 3 results |

## Steps

### 1. Parse input

```
/research "Domo App Studio card swap API"
/research "https://www.youtube.com/watch?v=abc123"
/research "https://docs.domo.com/some-page" --gdoc 1BZYkmwbP5s0gAEpqjkdF0OOuosGgm_0N
```

Extract: topic/URL, optional `--gdoc` flag with Google Doc ID.

### 2. Authenticate to mdrag

```bash
# Get Infisical token
INFISICAL_TOKEN=$(curl -sS -X POST "https://infisical.datacrew.space/api/v1/auth/universal-auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")

# Get DC_API_TOKEN
DC_API_TOKEN=$(curl -sS "https://infisical.datacrew.space/api/v3/secrets/raw/DC_API_TOKEN?environment=prod&workspaceId=3fbb4296-d4e6-4c17-83ee-b852a57a5e50&secretPath=/mdrag" \
  -H "Authorization: Bearer $INFISICAL_TOKEN" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('secret',data).get('secretValue',''))")
```

### 3. Initialize MCP session

```bash
SESSION_ID=$(curl -sS -D - -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"datacrew-agent","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | head -1 | awk '{print $2}' | tr -d '\r')
```

### 4. Route to the right tool

**YouTube URL:**

```bash
# Use the youtube-research runbook script
.venv/bin/python3 /workspace/libraries/mdrag/.agents/runbooks/research/youtube-research/scripts/research_youtube.py \
  --url "$YOUTUBE_URL" \
  --output /tmp/research-output.md
```

Or via MCP:

```bash
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"crawl_url","arguments":{"url":"'"$YOUTUBE_URL"'","debug":true}}}'
```

**Web URL:**

```bash
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"crawl_url","arguments":{"url":"'"$WEB_URL"'","debug":true}}}'
```

**Plain topic:**

```bash
# Search first
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_web","arguments":{"query":"'"$TOPIC"'","limit":3}}}'

# Then crawl top results
```

### 5. Archive raw content

```bash
# Save to local archive
mkdir -p ~/data/EXPORTS/scrape/<topic>/
# Write crawled content to content.md
```

### 6. Write to Google Doc (if --gdoc provided)

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google.drive.google_docs import GoogleDoc, Tabs

auth = GoogleAuth(scopes=GoogleAuth.DRIVE_FULL_SCOPES)
doc_client = GoogleDoc(authenticator=auth)
tabs = Tabs(client=doc_client)
await tabs.upsert(document_id=GDOC_ID, title="Research: <topic>", content=markdown_content)
```

### 7. Store learnings in MemFS

Write extracted learnings to `$MEMORY_DIR/project/<domain>/research/<topic>.md`.

## Gotchas

- **YouTube URLs cannot be crawled** — `crawl_url` returns 0 words on YouTube. Always use the youtube-research runbook or `POST /api/v1/readings/save` endpoint.
- **MCP session required** — must initialize before calling tools. Session ID goes in `Mcp-Session-Id` header.
- **12k char response cap** — `ResponseLimitingMiddleware` truncates at 12k. Use `debug=True` for metadata.
- **`Tabs.upsert()` not `write_markdown_to_tab`** — the latter always appends.
- **Infisical `secretValue` field** — the API returns the token value in `secretValue`, not `value`.

## Related

- `mdrag-mcp` — full mdrag MCP reference
- `outreach-create-dossier` — uses research as a sub-step
- `upsert-gdoc` — Google Doc write skill
