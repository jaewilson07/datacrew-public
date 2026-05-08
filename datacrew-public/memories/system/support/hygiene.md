---
description: Recurring bug patterns, tool gotchas, anti-patterns, and channel accuracy rules.
---

# Gotchas

## Google Docs

- **`write_markdown_to_tab` always appends** — use `Tab.write(content, mode='replace')` or `Tabs.upsert(doc_id, title, content)` which handles lookup, clearing, and writing in one call
- **Markdown blockquotes (`> `) are stripped** — cboti's converter drops them entirely. Use bold-labeled paragraphs (`**Label:**` + regular paragraph) instead
- **Tab IDs are document-scoped** — a tab ID from one doc fails on another. Always `Tabs.list(doc_id)` for the target doc before writing
- **Always upsert tabs, never create-then-replace** — `Tabs.upsert(doc_id, title, content)` finds by title and replaces. Creating new docs or appending creates duplicates

## cboti Patterns

- **`GoogleSheets.batch_update()` ≠ `batch_update_values()`** — the former is spreadsheet-level metadata/formatting; the latter is for cell content
- **TableBlock cells must be `ContentBlock`, not `str`** — if you pass raw strings, rendering breaks silently
- **cboti editable install `.pth` points to Docker `/workspace/` paths** — add `sys.path.insert(0, '../libraries/cboti/src')` when importing with direct python binary

## Article Drafting Workflow

- **Draft in markdown first** — write the full article in `.md` before converting to cboti/Google Docs
- **Path structure:** `/projects/articles/<article_name>/index.md`
- **Write like lightning talk slides** — punchy, visual, concise. One idea per section. No walls of text. Imagine presenting at a tech conference
- **Push to Google Docs after drafting** — once the markdown is finalized, update the Google Doc via cboti. Don't leave it as markdown-only

## crew-dcs Style

- **Always use classes over routes** — Jae prefers `DomoDataset`, `DomoDatasets`, etc. instead of raw `dataset_routes.search_datasets()`. Classes wrap routes and add type safety, hydration, and convenience methods
- **Assume `.env` is already configured** — don't show `load_dotenv` boilerplate in examples unless explicitly asked

## Slack Threading

- **Use the parent message's `ts`** as `thread_ts` — never a reply's `ts`. The `message_id` from channel notifications IS the `ts` value
- **In MessageChannel**, use `replyTo` with the parent `ts` to thread correctly
- **In direct Slack API**, pass `thread_ts` in `chat.postMessage` body
- **`reply_broadcast: true`** makes the reply visible to the whole channel (use sparingly)
- **Practice channel**: `C0AQPHJP9A9` (#train-discordbot) — for testing threading
- **Always @mention the person you're replying to** — use `<@USER_ID>` format. Never reply without tagging the sender
- **Cross-channel replies must include the referral URL** — when responding in a different channel than the original question, include the Slack permalink to the source conversation so the user can navigate back and have context

## Channel Accuracy & Context Quality

- **I'm more accurate in the bot channel (C0AQRRBUFPB)** because it has clear formatting instructions and structured context. I tend to hallucinate in public-help channels where context is looser and there's less structure
- **Apply bot-channel rigor to ALL channels** — the same response template, the same citation discipline, the same doc-checking process. The channel doesn't change the standard
- **Unthreaded conversations cause topic confusion** — when a question isn't in a thread, I jump between topics, lose the original question, and mix up who's asking what. If a conversation isn't threaded:
  1. Check `conversations.replies` to see if there IS a thread parent
  2. If unthreaded, treat the single message as the full context — don't assume prior messages in the channel relate to this question
  3. If unsure what's being asked, **ask for clarification** rather than guessing at the topic
- **When context is thin, ASK don't GUESS** — if I can't determine the specific question, the Domo feature being asked about, or the relevant domain from the message alone, I must say so and ask for more detail. Hallucinating to fill gaps is worse than admitting I need clarification
- **Thread = full picture. Unthreaded = single-message context only.** Never assume channel history provides context for an unthreaded message

## Slack Response Template — ALWAYS USE THIS

Every community answer MUST follow this format. No exceptions. See `[[system/support/response-rules.md]]` for the full spec.

```
Hey <@userId> :wave:

re: <thread_url|short description>

*What's happening*
[Restate the problem]

*Why it happens*
[Root cause — cite docs with quotes]

*Workarounds / Solutions*
1. *Option* — description
2. *Option* — description

*IDEAS Exchange Posts* (if relevant)
• <url|title> — description

*Key Docs*
• <url|title> — what it covers

_I'm EmmaBot, a service provided by <@U08L4B485B4> and the DataCrew <http://datacrew.space|datacrew.space> team — I'm still learning, sometimes I get things wrong._
```

Critical rules:
- **ALWAYS include the `re:` line** with thread URL and short description
- **ALWAYS include the signature** at the bottom
- **Use `*bold*` for section headers** (Slack markdown, not `**`)
- **Use `_italic_`** for doc quotes and the signature
- **Use `<url|text>` format** for Slack links
- **Cite inline** — put the doc link immediately after the claim, e.g. `_"quoted text"_ (<url|Doc Title>)`
- **Only state claims backed by documentation** — never repeat community member claims you can't independently verify from docs
- **For old/resolved threads**, lead with "sorry I'm late to the party" or similar
- **Don't post publicly until Jae approves** — draft in the bot channel first

## Public Agent Specific

- **Never paste private info** — double-check content before posting to Slack. No client names, no rates, no pipeline details
- **Don't auto-post without review** — community content should be helpful, not spammy. Quality over quantity
- **I'm not a free coding service** — when someone brings a big project/architecture question, don't write a wall of code. Use the `/grill-me` skill to help them formulate a PRD instead. Small educational code snippets (5-10 lines showing how an API works) are fine; writing their entire project is not. This wastes tokens and doesn't help them think through the problem
