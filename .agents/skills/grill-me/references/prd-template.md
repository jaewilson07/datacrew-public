# PRD Template

Use this template when synthesizing a PRD from the `/grill-me` conversation.

```markdown
# PRD: [Project Name]

## Problem Statement
[1-2 sentences describing the problem being solved]

## Goals & Success Criteria
- [ ] Goal 1 — [how you'll measure it]
- [ ] Goal 2 — [how you'll measure it]

## Scope
**In scope (v1):**
- ...

**Out of scope (for now):**
- ...

## Architecture Approach
[High-level pattern — no code, just the approach]
- Where does it run? (App Studio, Jupyter, CodeEngine, external)
- What's the data flow?
- What Domo services/APIs does it depend on?

## Key Domo APIs / Features
- [API endpoint or feature] — [what it provides for this project]
- [API endpoint or feature] — [what it provides for this project]

## Data & Integration
- **Datasets involved:** [list or "TBD"]
- **Data volume:** [approximate]
- **Refresh cadence:** [real-time, hourly, daily, etc.]
- **External integrations:** [none / list]

## Governance & Security
- **Access control:** [who should see the outputs?]
- **PDP requirements:** [yes/no, details]
- **Compliance constraints:** [none / list]

## Open Questions
- [ ] Question 1
- [ ] Question 2

## Next Steps
1. [Concrete action item]
2. [Concrete action item]
```
