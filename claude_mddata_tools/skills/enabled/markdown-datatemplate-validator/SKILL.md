---
name: markdown-datatemplate-validator
description: Create and validate properly structured markdown datatemplates (MarkdownDataUpdate YAML/JSON format) with correct parameter definitions, validation rules, and format compliance. Use when designing new markdown datatemplates, validating existing datatemplates, or ensuring datatemplate quality before deployment with mddata CLI.
version: 1.0.0
keywords:
  - markdown datatemplates
  - template validation
  - parameter validation
  - MarkdownDataUpdate
  - template structure
  - enum validation
  - array constraints
  - pattern validation
  - schema validation
  - template testing
  - datatemplate design
  - validation rules
  - template quality
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - "mddata write"
  - "mddata schema"
  - "mddata extract"
  - "mddata info"
---
# Markdown Datatemplate Validator

## Purpose

Help users create well-structured, validated markdown datatemplates using the MarkdownDataUpdate format with proper parameter definitions, validation constraints, and correct frontmatter/content structure. Markdown datatemplates are reusable document templates that combine parameter validation, placeholder substitution, and structured content to generate consistent markdown documents. Ensures datatemplates are ready for use with mddata write command and follow best practices for parameter validation, enum definitions, and array constraints.

## When to Use This Skill

Use this skill when you need to:

1. **Create new markdown datatemplates** - Design templates from scratch with proper structure
2. **Validate existing datatemplates** - Check templates for correct format and validation rules
3. **Add parameter validation** - Enhance templates with enums, patterns, and constraints
4. **Debug template issues** - Identify and fix structural or validation problems
5. **Review template quality** - Ensure templates follow best practices
6. **Test template rendering** - Verify templates work correctly with sample data

## Instructions

### 1. Define Template Purpose and Parameters

Start by identifying what the markdown datatemplate will generate:

**Ask:**
- What type of document? (bug report, meeting notes, spec, etc.)
- What are the required inputs? (title, author, date, etc.)
- What are optional inputs with defaults?
- What validation rules are needed? (enums, patterns, constraints)

**Create parameter definitions:**

```yaml
parameters:
  title:
    type: str
    required: true
    min: 10
    max: 100
    description: "Document title (10-100 characters)"

  status:
    type: str
    required: true
    enum: [draft, review, published]
    enum_strict: true
    enum_descriptions:
      draft: "Work in progress"
      review: "Under review"
      published: "Published and live"
```

### 2. Add Validation Constraints

Apply appropriate validation for each parameter type:

**String validation:**
- `min` / `max`: Length constraints
- `pattern`: Regex validation
- `enum`: Allowed values with descriptions

**Array validation:**
- `min_items` / `max_items`: Length constraints
- `unique_items`: No duplicates
- `item_enum`: Allowed values for items
- `item_pattern`: Regex for items
- `item_enum_strict`: Strict or permissive validation

**Example with full validation:**

```yaml
parameters:
  labels:
    type: array
    required: true
    min_items: 1
    max_items: 5
    unique_items: true
    item_enum: [bug, feature, docs, test]
    item_enum_strict: false
    item_pattern: "^[a-z-]+$"
    description: "1-5 unique labels (predefined or custom lowercase)"
```

### 3. Structure Frontmatter and Content

Define the document structure with parameter placeholders:

**Frontmatter:**
```yaml
frontmatter:
  title: "{title}"
  status: "{status}"
  created: "{date}"
  author: "{env.USER}"
```

**Content sections:**
```yaml
sections:
  - id: introduction
    content: |
      ## Introduction

      {introduction_text}

  - id: details
    content: |
      ## Details

      **Status**: {status}
      **Created**: {date}
```

### 4. Validate Template Structure

Use mddata commands to validate the markdown datatemplate:

```bash
# Test parameter parsing
mddata extract yaml template.yaml

# Infer schema to check structure
mddata schema infer template.yaml --format yaml --output template-schema.yaml

# View schema validation rules
mddata schema info template-schema.yaml

# Test rendering with sample data
mddata write --data template.yaml \
  -p title="Test Document" \
  -p status=draft \
  --output /tmp/test.md --dry-run
```

### 5. Test Validation Rules

Verify that validation rules work correctly:

```bash
# Test enum validation (should fail)
mddata write --data template.yaml \
  -p status="invalid" \
  --output /tmp/test.md

# Test array constraints (should fail)
mddata write --data template.yaml \
  -p 'labels=["a", "b", "c", "d", "e", "f"]' \
  --output /tmp/test.md

# Test pattern validation (should fail)
mddata write --data template.yaml \
  -p 'labels=["Invalid_Label"]' \
  --output /tmp/test.md

# Valid test (should succeed)
mddata write --data template.yaml \
  -p title="Valid Document" \
  -p status=draft \
  -p 'labels=["bug", "feature"]' \
  --output /tmp/test.md
```

### 6. Document Template Usage

Add comments explaining parameter requirements:

```yaml
# Bug Report Template v1.0
#
# Required Parameters:
#   - title: Bug title (10-100 chars)
#   - severity: critical, high, medium, or low
#   - description: Detailed description
#
# Optional Parameters:
#   - labels: Up to 5 labels (predefined or custom)
#   - assignee: GitHub username
#
# Usage:
#   mddata write --data bug-report.yaml \
#     -p title="Login fails" \
#     -p severity=high \
#     -p description="Details..." \
#     --output bug-001.md

parameters:
  # ...
```

## Examples

### Example 1: Creating a Bug Report Datatemplate

```json
{
  "parameters": {
    "title": {
      "type": "str",
      "required": true,
      "min": 10,
      "max": 100,
      "description": "Bug title"
    },
    "severity": {
      "type": "str",
      "required": true,
      "enum": ["critical", "high", "medium", "low"],
      "enum_strict": true,
      "enum_descriptions": {
        "critical": "System down, immediate fix required",
        "high": "Major feature broken",
        "medium": "Minor feature issue",
        "low": "Cosmetic or enhancement"
      }
    },
    "priority": {
      "type": "int",
      "required": true,
      "min": 1,
      "max": 5,
      "description": "Priority (1=highest, 5=lowest)"
    },
    "description": {
      "type": "str",
      "required": true,
      "min": 20,
      "description": "Detailed bug description"
    },
    "labels": {
      "type": "array",
      "required": false,
      "default": [],
      "min_items": 0,
      "max_items": 5,
      "unique_items": true,
      "item_enum": ["bug", "regression", "security", "performance"],
      "item_enum_strict": false,
      "item_pattern": "^[a-z-]+$"
    }
  },
  "frontmatter": {
    "title": "{title}",
    "severity": "{severity}",
    "priority": "{priority}",
    "status": "open",
    "created": "{date}"
  },
  "content": {
    "children": [
      {
        "id": "description",
        "title": "Description",
        "level": 2,
        "blocks": [
          {
            "type": "paragraph",
            "content": "{description}"
          }
        ]
      },
      {
        "id": "reproduction",
        "title": "Steps to Reproduce",
        "level": 2,
        "blocks": [
          {
            "type": "list",
            "content": "1. \n2. \n3. "
          }
        ]
      },
      {
        "id": "expected",
        "title": "Expected Behavior",
        "level": 2,
        "blocks": []
      },
      {
        "id": "actual",
        "title": "Actual Behavior",
        "level": 2,
        "blocks": []
      }
    ]
  }
}
```

**Validation:**

```bash
# Extract and verify structure
mddata extract yaml bug-report-template.yaml

# Test with valid data
mddata write --data bug-report-template.yaml \
  -p title="Login endpoint returns 500" \
  -p severity=critical \
  -p priority=1 \
  -p description="The /api/auth/login endpoint fails with 500 errors when..." \
  -p 'labels=["bug", "security"]' \
  --output bug-001.md

# Test enum validation (should fail)
mddata write --data bug-report-template.yaml \
  -p severity="urgent"  # Not in enum

# Test array validation (should fail)
mddata write --data bug-report-template.yaml \
  -p 'labels=["a", "b", "c", "d", "e", "f"]'  # Too many
```

### Example 2: Validating Existing Datatemplates

```bash
# Check if markdown datatemplate is well-formed
mddata extract yaml existing-template.yaml

# Infer schema to see structure
mddata schema infer existing-template.yaml \
  --format yaml --output template-schema.yaml

# Review schema for parameter definitions
mddata schema info template-schema.yaml

# Look for issues:
# - Missing required parameters
# - Weak validation (no enums/patterns where needed)
# - Missing descriptions
# - Overly permissive constraints
```

### Example 3: Common Validation Issues

**Issue: Missing enum descriptions**

```yaml
# Bad - users don't know what values mean
status:
  type: str
  enum: [draft, review, published]

# Good - clear descriptions
status:
  type: str
  enum: [draft, review, published]
  enum_descriptions:
    draft: "Work in progress"
    review: "Under review"
    published: "Live and public"
```

**Issue: Weak array validation**

```yaml
# Bad - no constraints
tags:
  type: array
  required: false

# Good - proper constraints
tags:
  type: array
  required: false
  min_items: 1
  max_items: 10
  unique_items: true
  item_pattern: "^[a-z0-9-]+$"
```

**Issue: No pattern validation**

```yaml
# Bad - accepts any string
email:
  type: str
  required: true

# Good - validates format
email:
  type: str
  required: true
  pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
```

## Additional Notes

### Best Practices

1. **Always provide descriptions** - Help users understand what each parameter does
2. **Use enums for controlled vocabularies** - Prevent typos and invalid values
3. **Add enum descriptions** - Document what each enum value means
4. **Validate arrays properly** - Set min/max items and uniqueness constraints
5. **Use patterns for format validation** - Email, URLs, version strings, etc.
6. **Non-strict enums for extensibility** - Allow custom values with pattern fallback
7. **Test validation thoroughly** - Try invalid inputs to verify constraints work
8. **Document usage in comments** - Show example commands in template file
9. **Use semantic versioning** - Track template versions for compatibility
10. **Provide sensible defaults** - Use computed parameters like {date}, {env.USER}

### Validation Checklist

Before deploying a markdown datatemplate, verify:

- [ ] All required parameters have descriptions
- [ ] Enums include enum_descriptions
- [ ] Arrays have min_items/max_items constraints
- [ ] Strings with formats have pattern validation
- [ ] Computed parameters use correct syntax ({date}, {env.VAR})
- [ ] Template renders successfully with test data
- [ ] Validation rules reject invalid inputs
- [ ] Schema inference produces expected structure
- [ ] Usage documentation is clear and accurate

### Common Parameter Types

**Strings:**
```yaml
title:
  type: str
  required: true
  min: 5
  max: 100
  pattern: "^[A-Z].*"  # Must start with capital
```

**Integers:**
```yaml
priority:
  type: int
  required: true
  min: 1
  max: 5
```

**Arrays:**
```yaml
tags:
  type: array
  required: true
  min_items: 1
  max_items: 10
  unique_items: true
  item_enum: [common, values]
  item_enum_strict: false
  item_pattern: "^[a-z-]+$"
```

**Enums:**
```yaml
status:
  type: str
  enum: [draft, review, published]
  enum_strict: true
  enum_descriptions:
    draft: "Work in progress"
```

### References

- **TEMPLATES.md** - Complete parameter validation documentation
- **markdown-writer skill** - Template usage and workflows
- **mddata-inspect skill** - Template inspection techniques
