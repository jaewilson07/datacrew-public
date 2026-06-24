---
name: use-mdrag
description: >
  Call the DataCrew mdrag knowledge service at wikki.datacrew.space to search the
  web, crawl pages/sites, query the RAG knowledge base + wiki, run research, and
  do authenticated (logged-in) crawling via a browser session. Authenticates with
  the dc_ service token from Infisical. Use for: "/use-mdrag", "search the web",
  "crawl this url", "query the knowledge base", "research X", "scrape a page behind login".
metadata:
  version: 1.0.0
  created: 2026-05-29
---

# use-mdrag

Use the DataCrew **mdrag** service over HTTP at `https://wikki.datacrew.space`. Prefer
this skill over carrying mdrag MCP tools — Letta loads/unloads skills on demand, which
keeps your tool context lean (Letta recommends skills over MCP for exactly this).

Companion skill: **`/check-mdrag`** verifies mdrag is up and auth works — run it first
if calls fail.

## When to use

- Live web search → `search_web`
- Scrape one page (auto-detects JS) → `crawl_url`; BFS a site (≤20 pages) → `crawl_site`
- Ask the knowledge base / wiki → `query_rag`, `query_wiki`
- Compile crawled pages into wiki articles → `compile_wiki`
- Run a research workflow → `research`
- Crawl a page that needs login (Domo community, LinkedIn, …) → start a **browser session**, log in once, then `crawl_url(browser_profile=…)`

## Auth — get the dc_ token (same as check-mdrag)

The token is fetched from Infisical at runtime using the container's
`INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET` — nothing to store. Define this helper
once per shell, then use `mdrag <METHOD> <path> [curl args…]`:

```bash
mdrag() {
  local base="${MDRAG_BASE_URL:-https://wikki.datacrew.space}"
  local inf="${INFISICAL_SITE_URL:-https://infisical.datacrew.space}"
  if [ ! -s /tmp/.mdrag_dc_token ]; then
    if [ -n "${DATACREW_API_TOKEN:-}" ]; then
      # Direct token in env (e.g. Alix's container) — no Infisical round-trip.
      printf '%s' "$DATACREW_API_TOKEN" > /tmp/.mdrag_dc_token
    else
      # Fetch from Infisical with the container's machine identity.
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

> **Auth fallback order:** `DATACREW_API_TOKEN` env (if set) → Infisical fetch via `INFISICAL_CLIENT_ID/SECRET`. The datacrew-public bot uses the Infisical path; Alix's container is given a direct `DATACREW_API_TOKEN`.

## Common calls (HTTP REST — simplest path)

```bash
mdrag GET  /api/v1/health                                   # liveness + mongo
mdrag GET  "/api/v1/mcp/tools?tier=primary"                 # discover the curated tools
mdrag POST /api/v1/crawl/url      -d '{"url":"https://example.com"}'  # scrape one page (add "render_js":true for JS pages)
mdrag POST /api/v1/crawl/site     -d '{"url":"https://example.com","max_depth":2,"max_pages":20}'
mdrag GET  "/api/v1/wiki/search?q=topic&semantic=true"      # search the wiki
mdrag POST /api/v1/wiki/compile   -d '{...}'                # compile pages → articles
mdrag POST /api/v1/research       -d '{"topic":"...","wait":true}'   # synchronous research (wait:true blocks ≤30s; omit for async 202 + job)
mdrag POST /api/v1/searxng/search -d '{"query":"...","result_count":5}'  # web search via SearXNG
```

`crawl_site` is capped at 20 pages — for large ingests use the background ingest workflow, not this.

> **Note — web search works over REST (`/api/v1/searxng/search`) or the `search_web` MCP
> tool.** Only `query_rag` is MCP-only: don't POST to `/api/v1/query` — it requires an
> `org_id` filter the MCP path supplies for you automatically.

## Full tool set incl. query_rag + browser (MCP over HTTP)

Tools without a REST route (`query_rag`, `search_graph`, browser sessions, …) are reached
via the MCP endpoint `https://wikki.datacrew.space/mcp/` (Streamable HTTP). Use the curated
surface `https://wikki.datacrew.space/mcp/primary/` to keep the tool list small; call
`reveal_toolset(name="browser")` (or `list_capabilities`) to expose more on demand. See
**`/check-mdrag`** for the exact MCP session-init + `tools/call` sequence — reuse it with the
token above.

### Authenticated (logged-in) crawling — browser session

1. `tools/call` `start_browser_session` (no args) → returns a **noVNC URL** and reveals the
   browser toolset. Open the URL, complete Cloudflare Access if prompted, and log into the
   target site (e.g. community.domo.com). Cookies persist in your profile volume.
2. Then crawl with those cookies: `crawl_url` with `browser_profile="<domain>"` (e.g.
   `"community.domo.com"`).
3. `get_browser_session_status` checks/resumes the session; `fetch_authenticated` makes raw
   authed HTTP requests.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `401` | Token not sent/fetched — re-run the helper; check INFISICAL_CLIENT_ID/SECRET are set. |
| `403` | Token lacks scope — rotate at datacrew.space/account. |
| `301` to wikki | You used the retired `mdrag.datacrew.space` — use `wikki.datacrew.space`. |
| `502` | mdrag container down — run `/check-mdrag`; ping the operator. |
| browser `409` "not provisioned" | Call `start_browser_session` first, then retry. |

## Canonical reference

`libraries/mdrag/.agents/guides/calling-mdrag-from-agents.md` (endpoint list, auth, MCP
registration) — the source of truth this skill summarizes.
