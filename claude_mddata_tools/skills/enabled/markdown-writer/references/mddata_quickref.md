# mddata CLI Quick Reference

## Core Commands

### write - Create or Modify Markdown Files

The `write` command is the primary tool for working with markdown files from structured data.

```bash
# Create new file from data
mddata write --data data.json --output file.md

# Modify existing file
mddata write --data changes.json existing.md

# Create from template with parameters
mddata write --data template.yaml -p title="My Doc" -p author=John --output doc.md

# Generate template from schema
mddata write --schema schema.json --output template.md
```

**Key Parameters:**
- `--data/-d FILE`: JSON/YAML data file or `-` for stdin
- `--output/-o FILE`: Output file path
- `-p/--param KEY=VALUE`: Template parameter
- `--params FILE`: Load all parameters from file
- `--schema/-s FILE`: Schema for validation/template generation
- `--policy POLICY`: Merge policy (merge/replace/append)
- `--force/-F`: Overwrite existing files
- `--dry-run/-n`: Preview changes without applying

### modify - Granular Updates

For single property or section updates:

```bash
# Set property
mddata modify set-property file.md title "New Title"

# Set section content
mddata modify set-section file.md intro "New content"
mddata modify set-section file.md intro "Content" --policy replace
```

## Data Structure Formats

### Complete Document Structure

```json
{
  "frontmatter": {
    "title": "Document Title",
    "author": "Author Name",
    "date": "2025-01-01",
    "tags": ["tag1", "tag2"]
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 2,
        "content": "Introduction text here...",
        "subsections": []
      },
      {
        "id": "body",
        "title": "Main Body",
        "level": 2,
        "content": "Body content...",
        "subsections": [
          {
            "id": "details",
            "title": "Details",
            "level": 3,
            "content": "Detailed information..."
          }
        ]
      }
    ]
  }
}
```

### Update Structure (Partial)

For modifying existing files, provide only what needs to change:

```json
{
  "frontmatter": {
    "status": "published",
    "version": "2.0"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "Updated introduction text",
      "policy": "replace"
    },
    {
      "id": "conclusion",
      "content": "New conclusion section",
      "policy": "append"
    }
  ]
}
```

### Template Structure with Parameters

```json
{
  "parameters": {
    "title": {
      "type": "str",
      "required": true,
      "default": "Untitled"
    },
    "author": {
      "type": "str",
      "required": false
    },
    "date": {
      "type": "str",
      "required": false,
      "default": "{{date}}"
    }
  },
  "frontmatter": {
    "title": "{{title}}",
    "author": "{{author}}",
    "date": "{{date}}"
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 2,
        "content": "Written by {{author}} on {{date}}"
      }
    ]
  }
}
```

## Template Parameters

### Parameter Substitution

Templates support placeholders using `{{parameter_name}}` syntax:

```
Title: {{title}}
Author: {{author}}
Date: {{date}}
```

### Computed Parameters

Auto-generated values:
- `{{date}}` - Current date (YYYY-MM-DD)
- `{{time}}` - Current time (HH:MM:SS)
- `{{env.VAR}}` - Environment variable

### Parameter Sources (Precedence Order)

1. CLI parameters: `-p title="My Doc"`
2. Parameter files: `--params params.json`
3. Template defaults: Defined in template
4. Computed parameters: Auto-generated

## Update Policies

When modifying sections:

- **merge** (default): Merge content while preserving subsections
- **replace**: Replace entire section content
- **append**: Add content to existing section

## Common Workflows

### 1. Create from Template

```bash
# 1. Create template data file with parameters
# 2. Fill with CLI parameters
mddata write --data template.yaml \
  -p title="Project Status" \
  -p author="John Doe" \
  -p date="2025-01-01" \
  --output report.md
```

### 2. Bulk Update

```bash
# 1. Create update data file with changes
# 2. Apply to existing file
mddata write --data updates.json existing.md
```

### 3. Create Complete Document

```bash
# 1. Create complete data structure
# 2. Generate markdown
mddata write --data complete.json --output new-doc.md
```

### 4. Schema-Validated Creation

```bash
# 1. Generate or obtain schema
# 2. Create document with validation
mddata write --data data.json \
  --schema schema.json \
  --output validated.md
```
