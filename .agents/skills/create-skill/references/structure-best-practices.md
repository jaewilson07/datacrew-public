# Structure Best Practices - Claude Skills Directory Layout

## Standard Skill Directory Structure

```
skill-name/
├── SKILL.md              # Required: Frontmatter + instructions
├── references/           # Optional: Detailed reference material
│   ├── topic-1.md
│   └── topic-2.md
├── assets/               # Optional: Templates, examples, resources
│   ├── templates/
│   ├── examples/
│   └── resources/
└── scripts/              # Optional: Deterministic helper scripts
    └── helper.sh
```

---

## File Organization Principles

### SKILL.md (Required, ≤500 lines)

The main file that Claude reads and users interact with.

**Keep it focused:**
- Core functionality overview
- Quick start commands
- High-level workflow
- Links to references/ for detailed guidance
- Examples demonstrating all patterns

**When to move content elsewhere:**
- Detailed domain knowledge → `references/`
- Boilerplate code → `assets/`
- Validation logic → `scripts/`

**Sign it's too long** (move stuff to references/):
- ❌ > 500 lines total
- ❌ Multiple reference files embedded inline
- ❌ Copy-pasted code examples
- ❌ Long step-by-step walkthroughs

---

### references/ Folder (Optional)

Detailed, focused guidance that complements SKILL.md.

**Principles:**
- **One level deep only** — files directly in `references/`, no subfolders
- **Topic-specific** — each file covers one concept thoroughly
- **Linked from SKILL.md** — clear cross-reference
- **Maximum 2-3 files** — avoid cognitive overload
- **Loaded on-demand** — user discovers them via SKILL.md

**When to create a reference file:**
- Complex domain that needs explanation (e.g., "database-schema.md")
- Detailed checklist or rubric (e.g., "code-review-checklist.md")
- Best practices guide (e.g., "naming-conventions.md")
- Troubleshooting guide (e.g., "error-recovery-patterns.md")

**When NOT to create a reference file:**
- ❌ Information that fits in SKILL.md sections
- ❌ Redundant with existing documentation
- ❌ Less than 300 lines (keep in SKILL.md)
- ❌ Rarely referenced (inline in SKILL.md instead)

**Examples:**
```
references/
├── code-review-standards.md    # Detailed review criteria
├── error-patterns.md            # Common mistakes to catch
└── quality-rubric.md            # Scoring guide
```

---

### assets/ Folder (Optional)

Templates, examples, and resources that users modify or copy.

**Subfolders (if needed):**
- `templates/` — Boilerplate files users customize
- `examples/` — Real working examples
- `resources/` — Data files, configs, schemas

**Principles:**
- **Only include high-value resources** — saves significant work
- **Examples should be production-ready** — not just stubs
- **Delete unused templates before publishing** — keep minimal
- **Clear naming** — purpose obvious from filename

**When to create an asset:**
- Template that saves >20 lines of work (SKILL.md template, for example)
- Working example demonstrating complex pattern
- Reference data (schema, lookup table, config template)
- Reusable resource (validation script, data file)

**When NOT to create an asset:**
- ❌ Trivial boilerplate (2-3 lines, better inline in SKILL.md)
- ❌ Outdated examples (remove or update)
- ❌ Unused templates (delete before publishing)
- ❌ Code that changes frequently (document pattern instead)

**Examples:**
```
assets/
├── SKILL.md.template           # Boilerplate for new skills
├── templates/
│   ├── spec-template.md
│   └── checklist-template.md
├── examples/
│   ├── good-example.py
│   └── edge-case-example.py
└── resources/
    └── validation-rules.json
```

---

### scripts/ Folder (Optional)

Deterministic, reusable helper scripts (bash, Python, etc.).

**Principles:**
- **Deterministic** — same input always produces same output
- **Reusable** — not one-off tools
- **Error handling** — graceful failures with helpful messages
- **Documented** — inline comments explaining logic

**When to include:**
- Validation script that checks multiple conditions
- Schema generator from templates
- Data transformation logic
- Automated checks

**When NOT to include:**
- ❌ One-off scripts (simpler to document in SKILL.md)
- ❌ Heavy dependencies (better in virtual env docs)
- ❌ Stateful operations (databases, file systems)
- ❌ User data modification (too risky)

**Examples:**
```
scripts/
├── validate-skill.py           # Check SKILL.md structure
└── transform-spec.sh           # Transform spec format
```

---

## Directory Cleanup Checklist

Before publishing your skill, remove unused folders:

- [ ] References folder has 2-3 focused files (not more)
- [ ] Assets folder contains only high-value templates/examples
- [ ] Scripts folder is empty OR contains deterministic, reusable logic
- [ ] No `.bak`, `.old`, or `_draft` files left behind
- [ ] No credentials, API keys, or secrets in any files
- [ ] No large data files or binaries (keep git repo lean)

---

## Composability: Making Skills Work Together

### Design for Chaining

Skill A → Output (file, data) → Skill B Input

**Principles:**
1. **Standard file types** — Use common formats (.py, .md, .json)
2. **Clear output format** — Document what skill produces
3. **Predictable naming** — Easy to find/reference output
4. **Modular workflows** — Skill does one thing well
5. **Cross-reference related skills** — "See also:" section

**Example:**
```
Skill A (code-generator) → Produces Python file
                           ↓
Skill B (code-review) → Consumes .py file, outputs review

SKILL.md in B references A:
"This skill complements `code-generator-skill` for review-driven workflows."
```

---

### Progressive Disclosure

Load content on-demand to save context window:

1. **SKILL.md** — Core activation + quick start (300 lines)
2. **references/** — Detailed domain knowledge (loaded if user clicks link)
3. **assets/** — Templates/examples (only loaded if user requests)
4. **scripts/** — Helper logic (only executed if needed)

**Benefit:** Users see quick start immediately without cognitive overload.

---

## Size Guidelines

| Component | Recommended | Maximum | Rationale |
|-----------|------------|---------|-----------|
| SKILL.md | 300-400 lines | 500 lines | Keep main file focused |
| reference/ file | 200-300 lines | 400 lines | Focused on one topic |
| reference/ folder | 2-3 files | 5 files | Avoid overwhelming options |
| assets/ folder | 3-5 items | 10 items | Only essential resources |
| scripts/ folder | 0-2 scripts | 3 scripts | Keep helpers minimal |

**Total size:** Typical skill is 100-200 KB (compressed ~20-50 KB)

---

## Real-World Examples

### Example 1: Simple Utility Skill

```
code-snippet-generator/
├── SKILL.md (250 lines)           # Main content
└── assets/
    ├── templates/
    │   ├── python-class.py
    │   ├── python-test.py
    │   └── javascript-module.js
    └── examples/
        └── working-example.py
```

**Total:** ~50 KB | **Complexity:** Low | **Dependencies:** None

---

### Example 2: Complex Domain Skill

```
domain-code-review/
├── SKILL.md (450 lines)           # Comprehensive workflow
├── references/
│   ├── review-standards.md        # What to check for
│   ├── error-patterns.md          # Common mistakes
│   └── quality-rubric.md          # Scoring guide
├── assets/
│   ├── checklist.md               # Review template
│   └── examples/
│       ├── good-example.py
│       └── bad-example.py
└── scripts/
    └── validate-pr.sh             # Auto-validation
```

**Total:** ~150 KB | **Complexity:** High | **Dependencies:** bash/git

---

### Example 3: Meta-Skill

```
creating-skill/
├── SKILL.md (500 lines)           # Full guidance
├── references/
│   ├── frontmatter-guide.md
│   ├── structure-best-practices.md
│   ├── documentation-patterns.md
│   └── meta-skill-patterns.md
├── assets/
│   ├── SKILL.md.template          # Boilerplate
│   ├── example-skill/SKILL.md
│   └── quality-checklist.md
└── scripts/
    └── validate-skill.py          # Skill validator
```

**Total:** ~200 KB | **Complexity:** Very High | **Dependencies:** Python

---

## Git Workflow

### Before Committing

```powershell
# Clean up unused files
Remove-Item -Path "skill-name/_draft.md"
Remove-Item -Path "skill-name/.backup"

# Verify structure
tree skill-name /F
```

### Exclude from Version Control

```gitignore
# In .gitignore
skill-name/.DS_Store
skill-name/__pycache__/
skill-name/*.bak
skill-name/*_draft.md
```

---

## Validation Checklist

- [ ] SKILL.md ≤ 500 lines
- [ ] references/ has 2-3 focused files (or none)
- [ ] assets/ contains only essential templates/examples
- [ ] scripts/ is empty or contains deterministic logic
- [ ] No unused directories or .bak files
- [ ] No credentials/secrets in any files
- [ ] File sizes reasonable (total < 500 KB)
- [ ] Cross-references link to real files
- [ ] Directory structure matches standard layout
