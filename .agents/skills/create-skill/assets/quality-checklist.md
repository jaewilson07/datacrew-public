# Skill Quality Checklist

Use this checklist to validate your skill before publishing.

---

## Frontmatter Validation

- [ ] **name**: Lowercase letters and hyphens only (no spaces, underscores)
- [ ] **name**: Maximum 64 characters
- [ ] **name**: Action-oriented (gerund form preferred: `creating-*`, `generating-*`)
- [ ] **description**: Starts with action verb ("Creates", "Analyzes", "Validates")
- [ ] **description**: Includes "Use for:" clause with specific triggers
- [ ] **description**: Maximum 1024 characters
- [ ] **description**: No XML tags or HTML formatting
- [ ] **version**: Semantic versioning format (x.y.z)

---

## SKILL.md Structure

- [ ] **Overview**: 2-3 sentences describing what skill enables
- [ ] **Core Capabilities**: 3-5 specific, action-oriented bullet points
- [ ] **When to Use**: 3-5 distinct use case scenarios
- [ ] **Quick Start**: 3-5 concrete commands with examples
- [ ] **Detailed Workflow**: Step-by-step process with decision frameworks
- [ ] **References**: 2-3 focused, linked reference files (or none)
- [ ] **Examples**: 3+ real scenarios (simple, complex, edge case)
- [ ] **Troubleshooting**: 3-6 Q&A pairs with actionable answers

---

## Content Quality

- [ ] **SKILL.md line count**: ≤ 500 lines total
- [ ] **Examples**: Are complete and working (not stubs with "TODO")
- [ ] **Examples**: Show expected output clearly
- [ ] **References**: One level deep (files directly in `references/`, no subfolders)
- [ ] **References**: Each file is 200-400 lines and focused on one topic
- [ ] **Voice**: Imperative and action-oriented ("Create", not "Please create")
- [ ] **Voice**: Positive directives ("Use X", not "Don't forget X")
- [ ] **All links**: Point to actual files (no broken references)

---

## Directory Structure

- [ ] **SKILL.md**: Present in root
- [ ] **references/**: Has 0-3 focused files (or folder empty if not needed)
- [ ] **assets/**: Contains only high-value templates/examples
- [ ] **scripts/**: Empty or contains deterministic, reusable logic
- [ ] **Unused directories**: Deleted (no `.bak`, `_draft`, or temporary files)
- [ ] **No credentials**: No API keys, passwords, or secrets in any file
- [ ] **File sizes**: Total skill < 500 KB (reasonable git footprint)

---

## Functionality

- [ ] **Activation**: Tested with 3+ real scenarios
- [ ] **Skill activates**: On expected trigger patterns (if auto-triggering)
- [ ] **Output quality**: Matches documented capability
- [ ] **Error handling**: Documented in workflow or examples
- [ ] **Composability**: Clear how output feeds into other skills
- [ ] **Dependencies**: All external dependencies documented

---

## Documentation Quality

- [ ] **No jargon**: Concepts explained for new users
- [ ] **Examples provided**: For non-obvious patterns
- [ ] **Edge cases**: Documented in examples or troubleshooting
- [ ] **Escape hatches**: Document when/how to break rules
- [ ] **Progressive disclosure**: Simple overview leads to detailed references
- [ ] **Related skills**: Mentioned if applicable

---

## Pre-Publication Checklist

1. **Clean up**:
   - [ ] Remove all `.bak`, `_draft`, `TODO`, or temporary files
   - [ ] Delete unused directories
   - [ ] Verify no secrets/credentials in files

2. **Test**:
   - [ ] Run through each command in Quick Start
   - [ ] Test 3+ activation scenarios
   - [ ] Verify examples work as documented

3. **Review**:
   - [ ] Read SKILL.md cover-to-cover
   - [ ] Check all links work
   - [ ] Verify YAML frontmatter is valid

4. **Package**:
   - [ ] Create ZIP if distributing
   - [ ] Include README with installation instructions
   - [ ] Test ZIP extraction and functionality

---

## Quality Scoring

**Calculate your score:**

| Component | Full | Partial | Missing | Score |
|-----------|------|---------|---------|-------|
| Frontmatter (8 checks) | 8×3 | ×2 | ×0 | ___ |
| Structure (8 checks) | 8×3 | ×2 | ×0 | ___ |
| Content (8 checks) | 8×3 | ×2 | ×0 | ___ |
| **Total** | | | | ___ / 72 |

**Convert to 0-100 score:**
- 72 = 100%
- 65-71 = 90%+
- 57-64 = 80%+
- 49-56 = 70%+
- < 49 = Needs work (< 70%)

---

## Priority Improvements

Address gaps in this order:

1. **Critical** (affects activation):
   - Frontmatter validation
   - Core capability description

2. **High** (affects user success):
   - Quick start commands
   - Examples completeness

3. **Medium** (improves polish):
   - References organization
   - Troubleshooting Q&A

4. **Low** (nice-to-have):
   - Voice consistency
   - Related skills mentions

---

## Notes

**Use this checklist:**
- [ ] Before publishing (self-check)
- [ ] After major updates (validation)
- [ ] When seeking feedback (share completed checklist)
- [ ] Quarterly (maintain quality over time)

**Track your score over time:**
- v1.0.0: 82/100
- v1.1.0: 88/100
- v1.2.0: 95/100

Goal: Reach 90%+ for high-quality, maintainable skills.
