# Runbook Checklist

Use this checklist before publishing a runbook.

## Naming and Scope

- [ ] Folder name is verb-first and hyphenated
- [ ] Runbook describes one recurring operational task
- [ ] Success criteria are explicit

## Structure

- [ ] `SKILL.md` exists
- [ ] `scripts/` exists and contains at least one executable task script
- [ ] `references/` includes focused support docs
- [ ] `assets/templates/` exists only if templates are reused

## Script Quality

- [ ] Script has `--help`
- [ ] Script supports `--dry-run` where appropriate
- [ ] Script outputs clear summary/status
- [ ] Script handles common errors with actionable messages

## "Just Run" Principles (CRITICAL)

Scripts must work with `uv run <script>` from project root - no additional setup required.

### .env Loading

- [ ] **Use absolute path for project root** - Never rely on `__file__` relative path calculation
- [ ] **Load .env at script start** - Use `dotenv.load_dotenv()` with explicit path
- [ ] **Handle missing .env gracefully** - Print helpful error with expected location
- [ ] Example:
  ```python
  PROJECT_ROOT = Path("/home/jaewilson07/GitHub/simpleDiscordBot")
  ENV_FILE = PROJECT_ROOT / ".env"

  from dotenv import load_dotenv
  load_dotenv(ENV_FILE, override=True)
  ```

### Parameterization

- [ ] **Use argparse** - Not manual `sys.argv` parsing
- [ ] **Sensible defaults** - Most common use case should work with no args
- [ ] **Minimal required args** - Only what's truly necessary
- [ ] **Flags for modes** - `--fresh-auth`, `--dry-run`, `--scope`
- [ ] Example:
  ```python
  parser = argparse.ArgumentParser()
  parser.add_argument("--scope", default="default", choices=["default", "readonly", "docs"])
  parser.add_argument("--fresh-auth", action="store_true")
  args = parser.parse_args()
  ```

### Port Handling

- [ ] **Use fixed port** - Not random `port=0`
- [ ] **Document port in SKILL.md** - User needs to pre-configure (e.g., Google redirect URIs)
- [ ] **Handle "port in use"** - Clear error message with fix
- [ ] **Clean up after run** - Don't leave server processes hanging

### External Service Format Handling

- [ ] **Handle multiple formats** - E.g., OAuth "web" vs "installed" client types
- [ ] **Don't assume structure** - Check for keys before accessing
- [ ] Example:
  ```python
  if "web" in data:
      client_id = data["web"]["client_id"]
  elif "installed" in data:
      client_id = data["installed"]["client_id"]
  else:
      client_id = data["client_id"]
  ```

## SOP Quality

- [ ] Quick start commands are runnable as written
- [ ] Detailed workflow follows deterministic phases
- [ ] Verification steps are explicit
- [ ] Troubleshooting covers real failure modes

## Crosslinking

- [ ] Links to relevant domain docs (`doc-domain` outputs)
- [ ] Links to relevant feature docs/registry (`document-feature` outputs)
- [ ] Links to related skills and setup docs

## Validation

- [ ] Tested on at least one clean path
- [ ] Tested on at least one failure path
- [ ] No dead links
- [ ] No stale paths or renamed scripts
- [ ] Tested with `uv run` from project root
