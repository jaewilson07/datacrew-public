# Runbook Linking Patterns

## Intent

Runbooks are execution guides. They should link out to conceptual docs instead of duplicating them.

## Recommended Link Types

1. Domain docs:
- Link to `docs/dev-docs/<domain>/overview.md`
- Link to domain `CLAUDE.md`

2. Feature docs:
- Link to `docs/features/<feature>.md`
- Ensure feature is present in `docs/features/registry.yaml`

3. Operational references:
- Link to environment/setup docs
- Link to troubleshooting docs
- Link to script entrypoints

## Linking Rules

- Keep links one hop away from the runbook where possible
- Prefer stable paths over deep temporary notes
- When a script is referenced in SKILL.md, include exact invocation
- Add "Related skills" section for chaining tasks

## Example Cross-Skill Chain

- `create-runbook` defines SOP + scripts
- `doc-domain` updates conceptual domain docs and diagrams
- `document-feature` tracks feature discoverability in registry/index
