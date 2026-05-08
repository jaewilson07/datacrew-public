# Frontmatter Guide - Claude Skills YAML Reference

## Required Fields

### `name` (required, string)

The unique identifier for your skill. Used to create the slash command (`/skill-name`).

**Rules:**
- Lowercase letters, hyphens only (no spaces, underscores, or special characters)
- Maximum 64 characters
- Typically gerund form: `creating-*`, `reviewing-*`, `generating-*`
- Must be unique across all skills in a project

**Examples:**
- ✅ `creating-skill` — good (action-oriented, clear purpose)
- ✅ `pr-code-review` — good (specific, action-oriented)
- ✅ `generate-api-docs` — good (gerund form, specific)
- ❌ `my_skill` — bad (underscores not allowed)
- ❌ `Code Review` — bad (spaces not allowed)
- ❌ `skill` — bad (too generic)

---

### `description` (required, string)

The human-readable description of your skill. Determines when Claude automatically activates it.

**Rules:**
- **Lead with action verb**: "Creates", "Analyzes", "Validates", "Generates"
- **Be specific** about what it does (not "does stuff")
- **Include "Use for:"** with explicit trigger patterns
- **Maximum 1024 characters**
- **Third-person voice**: "processes" not "I process"
- No XML tags or HTML formatting
- Mention file types (.py, .pptx, .md) if relevant

**Structure:**
```
[Action verb] [what it does]. Use for: [trigger patterns].
```

**Examples:**

✅ Good:
```yaml
description: Creates Python test files following domolibrary2 async patterns. Use for scaffolding new tests, writing test templates, or onboarding team members to testing conventions.
```

✅ Good:
```yaml
description: Analyzes pull requests (.diff, .patch) for code quality issues following domolibrary2 conventions. Use for code review, PR checks, or validating new modules against error handling and type hint standards.
```

❌ Weak:
```yaml
description: Does code review and stuff
```

❌ Unclear activation:
```yaml
description: A code review tool
```

---

### `metadata.version` (required, string)

Semantic version of your skill for tracking changes and compatibility.

**Format:**
```
MAJOR.MINOR.PATCH
```

**Rules:**
- **PATCH** (x.x.1): Bug fixes, no behavior changes (1.0.0 → 1.0.1)
- **MINOR** (x.1.0): New features, backward compatible (1.0.0 → 1.1.0)
- **MAJOR** (2.0.0): Breaking changes, incompatible (1.0.0 → 2.0.0)

**Examples:**
```yaml
metadata:
  version: 1.0.0  # Initial release
  version: 1.1.0  # Added new feature
  version: 2.0.0  # Breaking change
```

---

## Optional Fields

### `allowed-tools` (optional, array)

Restrict which tools your skill can use. Improves security and clarity.

**Common values:**
- `Read` — Read files
- `Write` — Write files
- `Bash` — Run bash commands
- `HTTP` — Make HTTP requests

**Example:**
```yaml
allowed-tools:
  - Read
  - Bash
```

---

### `user-invocable` (optional, boolean)

Whether users can manually trigger the skill via `/skill-name` command.

**Default:** `true` (users can invoke)

**When to set to `false`:**
- Skill is only for automatic Claude activation
- Skill is internal reference (not meant for direct use)

```yaml
user-invocable: false
```

---

### `disable-model-invocation` (optional, boolean)

Whether Claude can automatically invoke this skill when it detects relevant context.

**Default:** `false` (Claude can auto-invoke)

**When to set to `true`:**
- Skill requires explicit user consent (destructive operations)
- Skill is manual-only workflow
- Skill needs careful control

**Examples:**

Auto-invocable (Claude can use automatically):
```yaml
disable-model-invocation: false  # or omit (default)
```

Manual-only (user must explicitly trigger):
```yaml
disable-model-invocation: true
```

---

### `context` (optional, string)

How the skill executes. Default behavior runs in main session.

**Value:** `fork`

Creates an isolated subagent context. Useful for:
- Skills that need complete isolation
- Complex workflows that shouldn't interfere with main session
- Nested skill activation

```yaml
context: fork
```

---

## Complete Frontmatter Example

```yaml
---
name: creating-skill
description: Scaffolds new Claude Skills with proper structure, frontmatter, documentation, and error handling. Use for creating domain-specific skills, meta-skills, automation workflows, or enhancing existing skills.
metadata:
  version: 1.2.0
allowed-tools:
  - Read
  - Write
user-invocable: true
disable-model-invocation: false
context: fork
---
```

---

## Tips for Great Descriptions

1. **Start strong**: Lead with the action verb
   - ✅ "Creates", "Analyzes", "Validates", "Transforms"
   - ❌ "Tool for", "Helps with", "Does"

2. **Be specific**: Mention what type of files or domains
   - ✅ "Python files (.py) following PEP 8"
   - ❌ "Code files"

3. **Include activation patterns**: "Use for:" clause
   - ✅ "Use for code review, PR checks, or onboarding"
   - ❌ (no hint about when to use it)

4. **One sentence or two**: Keep it scannable
   - ✅ Two sentences max
   - ❌ Long paragraphs

5. **Third-person voice**: As if describing to others
   - ✅ "Generates", "validates", "transforms"
   - ❌ "I generate", "you should validate"

---

## Common Mistakes to Avoid

❌ **Too generic**: `description: A helpful tool`

✅ **Specific**: `description: Analyzes Python functions for docstring coverage`

---

❌ **No activation hint**: `description: Creates files`

✅ **Clear triggers**: `description: Creates test files. Use for: writing unit tests, scaffold templates, or TDD workflow`

---

❌ **Imperative voice**: `description: You should review your code`

✅ **Third-person**: `description: Analyzes code for common issues`

---

## Validation Checklist

Before committing frontmatter:

- [ ] `name`: lowercase, hyphens only, ≤64 chars
- [ ] `description`: action verb + specific details + "Use for:" + ≤1024 chars
- [ ] `metadata.version`: semantic versioning (x.y.z)
- [ ] No XML tags or HTML in description
- [ ] Third-person voice throughout
- [ ] Tested to confirm description accurately triggers skill
