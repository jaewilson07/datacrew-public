---
name: add-to-gcal
description: >
  Add an event to Google Calendar from natural language or an event URL.
  Parses freeform descriptions into structured event fields. Use for:
  "/add-to-gcal", "add to calendar", "schedule this", "create calendar event".
metadata:
  version: 1.0.0
  updated: 2026-05-29
---

# add-to-gcal

Add events to Google Calendar from natural language descriptions or event URLs.

## When to Use

- `/add-to-gcal <event description>` — parse natural language into calendar event
- `/add-to-gcal <event-url>` — extract structured event from an event page
- User says "add to calendar", "schedule this", "put this on my calendar"

## Steps

### 1. Parse input

```
/add-to-gcal lunch with Sarah next Tuesday at noon
/add-to-gcal team standup every Monday 9am MT
/add-to-gcal https://lu.ma/ai-summit-2026
```

Determine: natural language description vs event URL.

### 2. Extract event fields

**If event URL** — use mdrag `extract_calendar_event_from_url`:

```bash
# Get DATACREW_API_TOKEN (see research skill for auth flow)
curl -sS -X POST "https://wikki.datacrew.space/api/v1/calendar/extract-event-from-url" \
  -H "Authorization: Bearer $DATACREW_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://lu.ma/ai-summit-2026", "timezone": "America/Denver"}'
```

Returns `ScrapedCalendarEvent` with: summary, start_datetime, end_datetime, location, description, timezone, confidence, extraction_method, warnings.

**If natural language** — parse directly:
- Extract: summary, date/time, duration, location, description
- Default timezone: `America/Denver` (Jae is in Denver, CO)
- Default duration: 1 hour if not specified
- Handle relative dates: "next Tuesday", "tomorrow", "in 2 weeks"

### 3. Create Google Calendar event

```python
from cboti.integrations.google.auth import GoogleAuth
from cboti.integrations.google_calendar import GoogleCalendar

auth = GoogleAuth(scopes=GoogleAuth.CALENDAR_SCOPES)
calendar = GoogleCalendar(authenticator=auth)

event = await calendar.create_event(
    summary="Lunch with Sarah",
    start={"dateTime": "2026-06-02T12:00:00", "timeZone": "America/Denver"},
    end={"dateTime": "2026-06-02T13:00:00", "timeZone": "America/Denver"},
    location="Denver, CO",
    description="Added via DataCrew agent"
)
```

### 4. Confirm to user

Report: event title, date/time, location, and calendar link.

## Gotchas

- **Default timezone**: `America/Denver` — Jae is in Denver
- **Partial extractions return 200 with `warnings[]`** — check warnings for missing fields
- **`extraction_method`**: `"json-ld"` = deterministic (confidence 1.0), `"letta"` = LLM (confidence ~0.7)
- **Calendar auth uses `GDOC_CLIENT` + `GDOC_TOKEN`** — same OAuth credentials as Google Docs
- **Recurring events**: if user says "every Monday", set recurrence rule

## Related

- `research` — for gathering event context from URLs
- `mdrag-mcp` — mdrag `extract_calendar_event_from_url` tool reference
