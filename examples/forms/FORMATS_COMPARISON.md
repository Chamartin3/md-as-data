# Form Formats Comparison

This document shows the same meeting notes form implemented in both formats to help you choose the best approach for your needs.

## Side-by-Side Comparison

### Raw Markdown Format

**File:** `meeting-notes.yaml` (original format)

```yaml
parameters:
  title:
    type: str
    required: true

  attendees:
    type: array
    item_type: str
    default: []

frontmatter:
  title: "{title}"
  date: "{date}"

sections:
  - id: "meetings"
    content: |
      ## {title} - {date}

      ### Attendees
      {attendees_list}

      ### Action Items
      {action_items_list}
    policy: append
```

**Characteristics:**
- ✅ Quick to write
- ✅ Familiar markdown syntax
- ❌ Heading levels hardcoded in content
- ❌ Can't parameterize the section heading level
- ❌ Mixes structure with content

---

### Structured YAML Format

**File:** `meeting-structured.yaml` (recommended format)

```yaml
parameters:
  title:
    type: str
    required: true

  attendees:
    type: array
    item_type: str
    default: []

frontmatter:
  title: "{title}"
  date: "{date}"

sections:
  - id: "meetings"
    title: "{title} - {date}"    # <-- Explicit, parameterized
    level: 2                      # <-- Explicit heading level
    policy: append
    content: |                    # <-- Content only, no heading
      ### Attendees
      {attendees_list}

      ### Action Items
      {action_items_list}
```

**Characteristics:**
- ✅ Clear separation of structure and content
- ✅ Heading level explicit and changeable
- ✅ Title can use parameters
- ✅ Easier to validate and process
- ✅ Better for complex forms
- ❌ Slightly more verbose

---

## Output Comparison

Both formats produce the same output:

```markdown
---
title: Sprint Planning
date: 2025-11-19
---
# Meetings

## Sprint Planning - 2025-11-19

### Attendees
- Alice
- Bob
- Charlie

### Action Items
- Update docs
- Review PRs
```

---

## When to Use Each

### Use Raw Markdown When:

1. **Quick prototyping** - You need a form fast
2. **Simple forms** - Single section, no complex structure
3. **Static headings** - Section titles don't need parameters
4. **One-off forms** - Not building a reusable library

**Example use case:**
```yaml
# Quick changelog entry
sections:
  - id: "changelog"
    content: |
      ## Version {version}

      Released {date}

      {changes}
```

### Use Structured YAML When:

1. **Parameterized titles** - Section headings use parameters
2. **Reusable forms** - Building a form library
3. **Complex structure** - Multiple levels, nested sections
4. **Tool integration** - Other tools process the forms
5. **Team collaboration** - Clearer for other developers

**Example use case:**
```yaml
# Targeted meeting entries with dynamic titles
parameters:
  target:
    type: str
    required: true
    description: "Target section (e.g., 'november_2025')"

  meeting_title:
    type: str
    required: true

sections:
  - id: "{target}"              # <-- Dynamic section targeting
    title: "{meeting_title} - {date}"  # <-- Parameterized title
    level: 2
    policy: append
    content: |
      Meeting content...
```

---

## Migration Guide

### Converting from Raw Markdown to Structured YAML

**Before (Raw Markdown):**
```yaml
sections:
  - id: "section"
    content: |
      ## {title}

      Content here
```

**After (Structured YAML):**
```yaml
sections:
  - id: "section"
    title: "{title}"
    level: 2
    content: |
      Content here
```

**Steps:**
1. Extract the heading from `content`
2. Add `title` field with the heading text (without `##`)
3. Add `level` field (count `#` symbols: `##` = 2, `###` = 3, etc.)
4. Remove heading from `content`

---

## Best Practices

### For Both Formats

✅ **DO:**
- Use descriptive parameter names
- Add parameter descriptions
- Use validation constraints
- Set sensible defaults
- Document your forms

❌ **DON'T:**
- Mix both formats in the same form
- Use ambiguous parameter names
- Skip validation rules
- Hardcode values that should be parameters

### Structured YAML Specific

✅ **DO:**
- Always specify `level` explicitly (1-6)
- Use parameters in `title` when titles vary
- Keep `content` focused on body text
- Use `policy: append` for accumulating entries

❌ **DON'T:**
- Include headings in `content` field
- Use level 0 or > 6
- Forget to specify `title` when using structured format

---

## Examples in This Directory

| File | Format | Purpose |
|------|--------|---------|
| `meeting-notes.yaml` | Raw Markdown | Original meeting notes form |
| `meeting-structured.yaml` | Structured YAML | Same form, structured format |
| `log-entry.yaml` | Raw Markdown | Simple changelog entries |
| `log-entry-structured.yaml` | Structured YAML | Structured changelog |
| `bug-report.yaml` | Raw Markdown | Complex bug report with validation |
| `simple.yaml` | Raw Markdown | Minimal starting point |

---

## Summary

**Choose Raw Markdown** for simple, quick forms where headings are static.

**Choose Structured YAML** for reusable, maintainable forms with parameterized titles and complex structures.

**Both formats are supported** and produce valid markdown output. Use what best fits your workflow!

For more details, see:
- `docs/MARKDOWN_FORMS.md` - Complete forms documentation
- `examples/forms/README.md` - Usage examples
- `examples/forms/SUMMARY.md` - Feature overview
