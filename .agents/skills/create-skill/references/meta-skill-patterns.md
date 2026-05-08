# Meta-Skill Patterns - Skills That Create or Enhance Other Skills

## What is a Meta-Skill?

A **meta-skill** is a skill that helps you work with other skills. It might:
- Create new skills from scratch
- Validate existing skills for quality
- Enhance skills with missing sections
- Automate skill publication workflows
- Generate documentation for skills

**Example:** `creating-skill` helps you build new skills following best practices.

---

## Meta-Skill Workflow Phases

All meta-skills follow a common pattern:

### Phase 1: Analyze

Understand the input or current state.

**Questions to answer:**
- What is the user trying to accomplish?
- What existing artifacts (scripts, docs, code) does the user have?
- What standards or conventions should apply?
- What's missing or incomplete?

**Example (creating-skill):**
```
Input: User wants to create a new skill for "code review"
→ Analyze: What triggers should activate it? What's the core workflow?
```

### Phase 2: Validate

Check against standards, best practices, and quality criteria.

**Questions to answer:**
- Does it follow the required structure?
- Are required sections present?
- Do frontmatter fields meet standards?
- Is documentation complete?
- What's the quality score (0-100)?

**Example:**
```
Check: Does SKILL.md have all 8 sections?
Check: Is description specific enough to trigger correctly?
Check: Are examples complete and working?
Quality Score: 75/100 (missing error handling in examples)
```

### Phase 3: Generate or Enhance

Create new artifacts or improve existing ones.

**Tasks:**
- Create directory structure with standard folders
- Generate boilerplate SKILL.md with frontmatter
- Create reference file templates
- Generate example assets

**Example:**
```
Generate: skill-name/
├── SKILL.md (with frontmatter template)
├── references/ (empty, ready for content)
├── assets/ (with SKILL.md template)
└── scripts/ (empty)
```

### Phase 4: Integrate

Make the output compatible with existing workflows.

**Tasks:**
- Ensure file paths use project conventions
- Link to relevant documentation
- Test activation triggers
- Prepare for publication

---

## Common Meta-Skill Types

### Type 1: Skill Generator

**Purpose:** Create new skills from scratch

**Workflow:**
1. **Analyze** intent: What should the new skill do?
2. **Generate** structure: Create directory layout
3. **Populate** SKILL.md: Frontmatter + 8-section template
4. **Suggest** content: Prompt for user to fill in sections

**Tool pattern:**
```
/creating-skill new my-skill-purpose
```

**Output:**
```
my-skill-purpose/
├── SKILL.md (with templates filled in)
├── references/README.md (explains how to add guides)
└── assets/ (with SKILL.md template example)
```

---

### Type 2: Skill Validator

**Purpose:** Check existing skills for quality and completeness

**Workflow:**
1. **Analyze** structure: Verify directory layout
2. **Validate** frontmatter: Check YAML fields
3. **Audit** documentation: Verify all 8 sections present
4. **Score** quality: Rate 0-100 with recommendations

**Tool pattern:**
```
/creating-skill validate ./path/to/skill/
```

**Output:**
```
Quality Report:
- Structure: ✓ (proper directories)
- Frontmatter: ✓ (all required fields)
- Documentation: ⚠ (missing troubleshooting)
- Examples: ✓ (3 scenarios covered)
- Quality Score: 82/100

Recommendations:
1. Add Q&A section to troubleshooting
2. Expand error handling examples
3. Link to related skills
```

---

### Type 3: Skill Enhancer

**Purpose:** Improve existing skills by adding missing content

**Workflow:**
1. **Analyze** current skill: What's missing?
2. **Identify** gaps: Which sections are incomplete?
3. **Generate** missing content: Suggest enhancements
4. **Offer** refactoring: Propose structural improvements

**Tool pattern:**
```
/creating-skill enhance ./path/to/skill/
```

**Output:**
```
Enhancements suggested:
✓ SKILL.md organization: Good
⚠ Frontmatter description: Too generic (suggested rewording)
⚠ Workflow section: Needs step numbers
✓ References: Present and focused
⚠ Examples: Missing edge cases
+ Add troubleshooting Q&A

Would you like me to:
1. Rewrite description for better activation?
2. Add step numbers to workflow?
3. Generate edge case examples?
```

---

### Type 4: Skill Publisher

**Purpose:** Prepare skills for distribution

**Workflow:**
1. **Validate** skill: Run full quality checks
2. **Clean** files: Remove unused directories, .bak files
3. **Generate** metadata: Create version info, README
4. **Publish** package: Create distributable archive

**Tool pattern:**
```
/creating-skill publish ./path/to/skill/
```

**Output:**
```
Skill published:
- skill-name-v1.0.0.zip (45 KB)
- README.md generated
- Metadata: version 1.0.0, ready for distribution
```

---

## Implementation Patterns for Meta-Skills

### Pattern 1: Checklist-Based Validation

Use a self-serve checklist in SKILL.md:

```markdown
## Quality Checklist

- [ ] SKILL.md ≤ 500 lines
- [ ] Frontmatter: name (lowercase, hyphens), description (action verb + use cases)
- [ ] All 8 sections present
- [ ] Examples are complete (not stubs)
- [ ] References are one level deep
- [ ] No unused directories

**How to use:**
1. Copy this checklist
2. Go through each item in your skill
3. Check boxes as you complete
4. Address any unchecked items
```

**Benefit:** Users can self-validate without running scripts.

---

### Pattern 2: Structured Analysis Output

Format validation results for clarity:

```markdown
## Analysis Result

| Component | Status | Notes |
|-----------|--------|-------|
| SKILL.md | ✓ Good | 350 lines, well-organized |
| Frontmatter | ✓ Good | All required fields present |
| References | ⚠ Needs work | Only 1 file, recommend 2-3 |
| Examples | ✓ Good | 4 scenarios, all working |
| **Overall Score** | **85/100** | Good quality, minor improvements needed |

### Recommendations (Priority Order)

1. **High impact**: Add 1-2 more reference files (gain +10 points)
2. **Medium impact**: Expand error handling examples (gain +5 points)
3. **Low impact**: Improve formatting in troubleshooting (gain 0 points, but cleaner)
```

**Benefit:** Users see exactly what needs work and in what order.

---

### Pattern 3: Template-Driven Generation

Provide templates that users can customize:

**For skill.md boilerplate:**
```markdown
---
name: YOUR-SKILL-NAME
description: [Action verb] [what]. Use for: [triggers].
metadata:
  version: 1.0.0
---

# YOUR SKILL TITLE

## Overview
[2-3 sentences about what your skill enables]

## Core Capabilities
- [capability 1]
- [capability 2]
- [capability 3]

[... rest of 8 sections ...]
```

**Benefit:** Users start with structure already in place.

---

### Pattern 4: Progressive Refinement

Guide users through improvement phases:

```markdown
## Create Your Skill - 4 Phases

### Phase 1: Define Purpose (5 min)
- What problem does this solve?
- Write 1-2 sentence summary

### Phase 2: Plan Workflow (10 min)
- What steps will users follow?
- Create numbered list

### Phase 3: Write Documentation (20 min)
- Fill in 8-section template
- Add examples

### Phase 4: Validate & Publish (5 min)
- Run quality checklist
- Address any gaps
```

**Benefit:** Users progress steadily without overwhelm.

---

## Meta-Skill Implementation Tips

### 1. Be Explicit About Standards

Don't make users guess. State standards clearly:

```markdown
## Skill Standards This Tool Enforces

✓ Frontmatter: name (lowercase, hyphens only)
✓ Description: action verb + "Use for:" clause
✓ Documentation: 8-section structure required
✓ SKILL.md: maximum 500 lines
✓ References: maximum 3 files, one level deep
```

### 2. Provide Escape Hatches

Allow users to deviate when justified:

```markdown
## When to Break These Rules

**Rule**: SKILL.md ≤ 500 lines
**Escape hatch**: If your workflow requires deep detail, move to references/

**Rule**: References, one level deep
**Escape hatch**: If multiple topics need sub-organization, use subfolders

Always document your reasoning in README.md.
```

### 3. Give Examples of Each Level

Show bad → good progression:

```markdown
## Frontmatter Quality Levels

❌ Bad:
```yaml
name: code_review
description: A tool for code review
```

⚠️ Better:
```yaml
name: code-review
description: Reviews Python code for quality issues
```

✅ Excellent:
```yaml
name: code-review
description: Analyzes Python files (.py) for code quality issues following domolibrary2 conventions. Use for code review, PR checks, or validating new modules.
```
```

### 4. Make Validation Results Actionable

Not just "FAILED", explain what to do:

```markdown
❌ Issue: Description is too generic

Current: "A helpful tool for code review"

Recommended: "Analyzes Python code for common bugs and style issues. Use for PR reviews, code quality checks, and onboarding validation."

Why: Better description helps Claude automatically activate skill when relevant.
```

---

## Meta-Skill Example: Complete Implementation

See `creating-skill` itself for a full working example:

- **Analyze phase**: Scan existing code, understand intent
- **Validate phase**: Check skill structure against standards (frontmatter-guide.md)
- **Generate phase**: Create skill scaffold with templates (SKILL.md.template in assets)
- **Integrate phase**: Link to documentation, provide examples

---

## Validation Checklist for Your Meta-Skill

- [ ] Clear phases: Analyze → Validate → Generate → Integrate
- [ ] Standards explicitly stated (not assumed)
- [ ] Checklists provided for self-validation
- [ ] Examples show bad → better → best progression
- [ ] Output is actionable (not just scoring)
- [ ] Escape hatches documented for edge cases
- [ ] Reference files support main workflow
- [ ] Examples of created/enhanced artifacts included
