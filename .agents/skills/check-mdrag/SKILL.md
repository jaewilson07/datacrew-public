---
name: check-mdrag
description: >
  Health check + tool discovery for the mdrag MCP server at wikki.datacrew.space.
  Authenticates via Infisical, initializes MCP session, and reports status.
  Use for: "/check-mdrag", "mdrag health", "test mcp", "verify mdrag".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# check-mdrag

Health check and tool discovery for the DataCrew MCP server at `wikki.datacrew.space`.

## When to Use

- `/check-mdrag` — verify mdrag is up and auth works
- User asks "is mdrag working?", "check MCP", "test mdrag"
- Debugging MCP connection issues

## Steps

### 1. Get Infisical access token

```bash
INFISICAL_TOKEN=$(curl -sS -X POST "https://infisical.datacrew.space/api/v1/auth/universal-auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")
```

### 2. Get DC_API_TOKEN from Infisical

```bash
DC_API_TOKEN=$(curl -sS "https://infisical.datacrew.space/api/v3/secrets/raw/DC_API_TOKEN?environment=prod&workspaceId=3fbb4296-d4e6-4c17-83ee-b852a57a5e50&secretPath=/mdrag" \
  -H "Authorization: Bearer $INFISICAL_TOKEN" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('secret',data).get('secretValue',''))")
```

**Note**: The token value is in the `secretValue` field, NOT `value`.

### 3. Health check

```bash
curl -sS "https://wikki.datacrew.space/api/v1/health" \
  -H "Authorization: Bearer $DC_API_TOKEN"
```

Expected response:
```json
{"status":"healthy","mongodb":"connected","chunks":16,"documents":1}
```

### 4. Initialize MCP session

```bash
SESSION_ID=$(curl -sS -D - -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"datacrew-agent","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | head -1 | awk '{print $2}' | tr -d '\r')

echo "Session ID: $SESSION_ID"
```

### 5. Discover tools

```bash
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: '):
        data = json.loads(line[6:])
        tools = data.get('result', {}).get('tools', [])
        for t in tools:
            print(f'  {t[\"name\"]}')
        print(f'Total: {len(tools)} tools')
"
```

### 6. Test search_web

```bash
curl -sS -X POST "https://wikki.datacrew.space/mcp/" \
  -H "Authorization: Bearer $DC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_web","arguments":{"query":"Domo AI agents","limit":2}}}' \
  | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: '):
        data = json.loads(line[6:])
        content = data.get('result', {}).get('content', [])
        for c in content:
            print(c.get('text', '')[:300])
"
```

## Report Format

```
=== mdrag Health Check ===
Health: {"status":"healthy","mongodb":"connected","chunks":16,"documents":1}
Session: e6ef166eb9a945d7998bf7f45de5b5bf
Tools: 38 (10 primary tier)
Search test: ✓ returned 2 results
```

## Gotchas

- **Token is in `secretValue` field** — Infisical API returns `{"secret": {"secretValue": "dc_..."}}`, not `value`
- **MCP session required** — must call `initialize` before `tools/list` or `tools/call`
- **Session ID from headers** — extracted via `grep -i "mcp-session-id"`, not from response body
- **401 = missing auth** — add `Authorization: Bearer dc_<token>` header
- **403 = insufficient scope** — generate new token at `https://datacrew.space/account`
- **301 = wrong hostname** — `mdrag.datacrew.space` redirects to `wikki.datacrew.space`

## Related

- `mdrag-mcp` — full mdrag MCP reference
- `research` — uses mdrag tools for web research
- `pull-updates` — syncs mdrag source code
