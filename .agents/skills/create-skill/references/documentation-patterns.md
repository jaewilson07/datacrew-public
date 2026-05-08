# Documentation Patterns - The 8-Section Structure

## Complete Section Template

Use this structure for clear, user-facing skill documentation.

---

## Section 1: Overview (2-3 sentences)

**Purpose:** Hook the reader. Answer "What does this skill enable?"

**Length:** 2-3 sentences maximum

**Content:**
- High-level purpose
- Primary value proposition
- Why someone would use it

**Example:**
```markdown
## Overview

This skill generates production-ready starter files for domolibrary2
development. Whether you're adding a test, route handler, entity class,
or utility, this skill ensures your boilerplate follows domolibrary2
conventions: async-first patterns, type hints, and error handling.
```

---

## Section 2: Core Capabilities (bulleted list)

**Purpose:** Show what the skill can do in specific, actionable terms.

**Length:** 3-5 bullet points

**Content:**
- Specific, distinct capabilities
- Action-oriented language
- No generic descriptions

**Examples:**

✅ Good:
```markdown
## Core Capabilities

- **Test files**: Async pytest with environment-variable fixtures
- **Route modules**: Single-file or folder patterns with decorators
- **Class entities**: Entity classes inheriting from DomoEntity
- **Utility functions**: Helper functions with complete type hints
- **Pattern inspection**: Reads existing code to learn patterns
```

❌ Weak:
```markdown
## Core Capabilities

- Generates files
- Works with code
- Has patterns
```

---

## Section 3: When to Use (scenario descriptions)

**Purpose:** Help users recognize when this skill solves their problem.

**Length:** 3-5 scenarios or use cases

**Content:**
- Explicit trigger phrases ("When you...", "Use this if...")
- Problem statements ("I want to...", "I need to...")
- File types or keywords if relevant
- One sentence each

**Examples:**

✅ Good:
```markdown
## When to Use

Generate a sample file when:
- Starting a new test for a feature
- Adding a new route handler or endpoint wrapper
- Creating a new entity class (DomoX)
- Writing a utility function following domolibrary2 style
- Onboarding team members to consistent patterns
```

❌ Weak:
```markdown
## When to Use

Use this skill for generating files.
```

---

## Section 4: Quick Start (actionable commands)

**Purpose:** Let users succeed immediately with minimal friction.

**Length:** 3-5 concrete commands or steps

**Content:**
- Exact commands to run
- Most common use cases first
- Code blocks with examples
- Expected output hints

**Examples:**

✅ Good:
```markdown
## Quick Start

### Generate a Test File

\`\`\`
/create-sample-file test
\`\`\`

Produces an async pytest file with fixtures and error handling.

### Generate a Route Module

\`\`\`
/create-sample-file route
\`\`\`

Produces a route handler with decorators and logging.
```

❌ Weak:
```markdown
## Quick Start

Run the skill with arguments.
```

---

## Section 5: Detailed Workflow (main instructions)

**Purpose:** Walk through the complete process step-by-step.

**Length:** Main section, as long as needed (but keep SKILL.md ≤500 lines total)

**Content:**
- Phase-based approach (Step 1, Step 2, etc.)
- Decision frameworks ("Consider X when...")
- Reference external guides
- Link to reference/ files for deep dives
- Examples showing each phase
- Progressive complexity (simple → advanced)

**Structure:**

```markdown
## Detailed Workflow

### Step 1: Understand the Context

When generating a file, consider:
- **File type**: Test, route, class, or utility?
- **Domain**: What is this for?
- **Complexity**: Simple or complex?
- **Dependencies**: What does it depend on?

### Step 2: Reference Existing Patterns

See [tests/AGENTS.md](#) for test structure.
See [routes/AGENTS.md](#) for route patterns.

### Step 3: Generate Template

Use Quick Start commands above.

### Step 4: Customize & Validate

Apply this checklist:
- [ ] Type hints on all parameters
- [ ] Docstrings complete
- [ ] Error handling appropriate

### Step 5: Run Validation

\`\`\`powershell
.\scripts\lint.ps1
\`\`\`
```

---

## Section 6: References (links to bundled documentation)

**Purpose:** Point users to detailed, focused guidance.

**Length:** 2-5 links with brief descriptions

**Content:**
- One level deep (files directly in `references/`)
- Topic-specific, clear descriptions
- Links to bundled reference files
- Can include external resources (official docs, standards)

**Examples:**

✅ Good:
```markdown
## References

Detailed guidance on domolibrary2 patterns:

- **[.github/instructions/general.instructions.md](#)** — Project-wide conventions
- **[.github/instructions/tests.instructions.md](#)** — Test standards
- **[.github/instructions/routes.instructions.md](#)** — Route patterns
- **[.github/instructions/classes.instructions.md](#)** — Entity class patterns
```

❌ Weak:
```markdown
## References

See the documentation for more info.
```

---

## Section 7: Examples (3+ real scenarios)

**Purpose:** Demonstrate the skill in action across different cases.

**Length:** 3-4 examples with detailed output

**Content:**
- Simple case (beginner scenario)
- Complex case (advanced usage)
- Edge case (boundary conditions, error recovery)
- Real, working examples (not stubs with "TODO")
- Shows expected output clearly
- Explains what pattern is being demonstrated

**Structure:**

```markdown
## Examples

### Example 1: Simple Test

**Command**: \`/create-sample-file test\`

**Output**: [show actual generated code]

**Key patterns demonstrated**:
- Async function with fixture
- Assertion patterns
- Error testing

---

### Example 2: Route Module with Decorators

**Command**: \`/create-sample-file route\`

**Output**: [show actual generated code]

**Key patterns demonstrated**:
- @route_function and @log_call
- Type hints
- RouteError raising

---

### Example 3: Entity Class

**Command**: \`/create-sample-file class\`

**Output**: [show actual generated code]

**Key patterns demonstrated**:
- @dataclass decorator
- Property definitions
- display_url property
```

**Tips for perfect examples:**
- Show complete, working code (no "..." or "..." omissions)
- Include imports and boilerplate
- Explain why each pattern matters
- Make it copy-paste ready

---

## Section 8: Troubleshooting (Q&A)

**Purpose:** Help users self-serve when stuck.

**Length:** 3-6 Q&A pairs

**Content:**
- Common questions
- Clear, actionable answers
- Links to relevant sections
- Error recovery paths
- When to escalate

**Structure:**

```markdown
## Troubleshooting

**Q: How do I know which imports to use?**

A: Check the General Instructions for standard aliases:
- `import domolibrary2.auth as dmda`
- `import domolibrary2.base.entities as dmde`

**Q: Should my method be async?**

A: Only if it calls an API. See Async Rules in [General Instructions](#).

**Q: What's the difference between RouteError and ClassError?**

A: Use RouteError for API failures. Use ClassError for entity logic.
See [Error Design Instructions](#) for details.
```

---

## Voice & Tone Guidelines

### Imperative Voice (Action-Oriented)

✅ "Create a test file" (what user should do)
✅ "Generate a route module" (direct instruction)
❌ "Consider creating a test file" (wishy-washy)
❌ "A test file can be created" (passive)

### Positive Directives

✅ "Use Type hints on all parameters"
✅ "Include error handling in routes"
❌ "Don't forget type hints"
❌ "Make sure not to skip error handling"

### Specific Examples

✅ "Use `@route_function` decorator on HTTP handlers"
✅ "Return `RouteError` on API failures"
❌ "Use decorators"
❌ "Handle errors appropriately"

### Context for Non-Obvious Choices

✅ "Use `Type | None` instead of `Optional[Type]` for consistency with Python 3.10+ style"
❌ "Use `Type | None`"

---

## Section Layout Template

```markdown
---
name: my-skill
description: [Your description]
---

# My Skill

## Overview

[2-3 sentences about what skill enables]

## Core Capabilities

- [capability 1]
- [capability 2]
- [capability 3]

## When to Use

[3-5 scenarios where skill solves problems]

## Quick Start

[3-5 concrete commands with examples]

## Detailed Workflow

### Step 1: [Phase name]
[Instructions]

### Step 2: [Phase name]
[Instructions]

## References

- [Link 1](#) — Description
- [Link 2](#) — Description

## Examples

### Example 1: [Scenario name]

[Working example with output]

### Example 2: [Scenario name]

[Working example with output]

### Example 3: [Scenario name]

[Working example with output]

## Troubleshooting

**Q: [Common question]**

A: [Clear answer]

---

**Q: [Common question]**

A: [Clear answer]
```

---

## Validation Checklist

- [ ] Overview is 2-3 sentences
- [ ] Core Capabilities are specific and action-oriented (3-5 items)
- [ ] When to Use covers 3-5 distinct scenarios
- [ ] Quick Start has 3-5 concrete commands
- [ ] Workflow is step-by-step with decisions
- [ ] References link to real files
- [ ] Examples are 3+, complete, and working (not stubs)
- [ ] Troubleshooting has 3-6 Q&A pairs
- [ ] All sections use imperative, positive voice
- [ ] Total SKILL.md ≤500 lines
