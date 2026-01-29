# Schema Management

## Overview

Schemas define the expected structure, types, and constraints for markdown documents. The `mddata schema` command provides tools for:
- **Generating** schemas from existing documents
- **Validating** documents against schemas
- **Inspecting** schema definitions
- **Enforcing** documentation standards

## Command Structure

```bash
mddata schema <subcommand> [arguments] [options]
```

## Schema Structure

A schema defines the expected document structure:

```json
{
  "frontmatter": {
    "property_name": {
      "type": "str",
      "required": true,
      "default": "value",
      "enum": ["option1", "option2"],
      "validations": [
        {
          "type": "min_length",
          "value": 1,
          "message": "Must not be empty"
        }
      ]
    }
  },
  "sections": {
    "section_id": {
      "validation": {
        "required": true,
        "min_blocks": 1,
        "max_blocks": 10,
        "allowed_content": ["paragraph", "list"]
      },
      "subsections": {
        "subsection_id": {
          "validation": {...}
        }
      }
    }
  },
  "validation_level": "strict"
}
```

### Frontmatter Property Schema

Each property can specify:

```json
{
  "property_name": {
    "type": "str | int | float | bool | list | dict",
    "required": true | false,
    "default": "default value",
    "enum": ["allowed", "values"],
    "validations": [
      {"type": "min_length", "value": 1, "message": "Custom error"},
      {"type": "max_length", "value": 100, "message": "Custom error"},
      {"type": "pattern", "value": "^[a-z]+$", "message": "Custom error"},
      {"type": "min", "value": 0, "message": "Custom error"},
      {"type": "max", "value": 100, "message": "Custom error"}
    ]
  }
}
```

**Property Types:**
- `str` - String values
- `int` - Integer numbers
- `float` - Decimal numbers
- `bool` - Boolean (true/false)
- `list` - Arrays
- `dict` - Objects/dictionaries
- Union types: `"int|str"` - Multiple allowed types

### Section Validation Schema

Each section can specify:

```json
{
  "section_id": {
    "validation": {
      "required": true,           // Section must exist
      "min_blocks": 1,            // Minimum block count
      "max_blocks": 10,           // Maximum block count
      "allowed_content": [        // Allowed block types
        "paragraph",
        "list",
        "code_block"
      ]
    },
    "subsections": {              // Nested section schemas
      "subsection_id": {...}
    }
  }
}
```

### Validation Levels

```json
{
  "validation_level": "strict | warnings | disabled"
}
```

- **`strict`**: Validation errors stop operations
- **`warnings`**: Validation errors generate warnings but allow operations
- **`disabled`**: No validation performed

## Generating Schemas

### From Single Document

Generate a schema based on a single document's structure:

```bash
mddata schema generate document.md --output schema.json
```

**Example document:**
```markdown
---
title: "API Guide"
version: 1.0
status: "draft"
tags: ["api", "guide"]
---

# Introduction

Welcome to the API guide.

## Overview

This section provides an overview.
```

**Generated schema (default: permissive mode):**
```json
{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true
    },
    "version": {
      "type": "float",
      "required": true
    },
    "status": {
      "type": "str",
      "required": true,
      "enum": ["draft"]
    },
    "tags": {
      "type": "list",
      "required": true
    }
  },
  "sections": {
    "introduction": {
      "validation": {
        "required": true,
        "min_blocks": 1
      },
      "subsections": {
        "overview": {
          "validation": {
            "required": true,
            "min_blocks": 1
          }
        }
      }
    }
  },
  "validation_level": "warnings"
}
```

### Pretty-Printed Output

```bash
mddata schema generate document.md --output schema.json --pretty
```

### YAML Format

```bash
mddata schema generate document.md --format yaml --output schema.yaml
```

**YAML output:**
```yaml
frontmatter:
  title:
    type: str
    required: true
  version:
    type: float
    required: true
  status:
    type: str
    required: true
    enum:
      - draft
  tags:
    type: list
    required: true
sections:
  introduction:
    validation:
      required: true
      min_blocks: 1
    subsections:
      overview:
        validation:
          required: true
          min_blocks: 1
validation_level: warnings
```

### From Multiple Documents (Folder)

Generate a merged schema from all markdown files in a folder:

```bash
mddata schema generate ./docs/ --output docs-schema.json --pretty
```

**Folder structure:**
```
docs/
├── api-guide.md       (title, version, status: "draft", tags)
├── user-guide.md      (title, version, status: "published", tags)
└── admin-guide.md     (title, status: "published")
```

**Generated merged schema:**
```json
{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true        // In 3/3 documents (100%)
    },
    "version": {
      "type": "float",
      "required": false       // In 2/3 documents (67%)
    },
    "status": {
      "type": "str",
      "required": true,       // In 3/3 documents (100%)
      "enum": ["draft", "published"]  // All observed values
    },
    "tags": {
      "type": "list",
      "required": false       // In 2/3 documents (67%)
    }
  },
  "sections": {
    "introduction": {
      "validation": {
        "required": true,
        "min_blocks": 1
      }
    },
    "installation": {        // Only in some documents
      "validation": {
        "required": false,
        "min_blocks": 1
      }
    }
  },
  "validation_level": "warnings"
}
```

**Schema merging rules:**
1. **Required properties**: Present in ≥75% of documents
2. **Enum inference**: Single-word strings with consistent values
3. **Type conflicts**: Resolved with union types (e.g., `"int|str"`)
4. **Section merging**: All sections from all documents included
5. **Null values**: Included in enum definitions when present

**Output message:**
```
Schema generated from 3 markdown files
```

### Inference Modes

#### Permissive Mode (Default)

Generates flexible schemas allowing document evolution:

```bash
mddata schema generate document.md --output schema.json
```

**Characteristics:**
- Minimal constraints
- `validation_level: "warnings"`
- Enum inference for single-word strings
- Required properties (≥75% frequency for folders)
- No max_blocks limits

#### Strict Mode

Generates exact schemas matching current structure:

```bash
mddata schema generate document.md --mode strict --output schema.json
```

**Characteristics:**
- Exact type matching
- `validation_level: "strict"`
- All properties required
- Strict block count limits
- Allowed content types specified

## Validating Documents

### Basic Validation

```bash
mddata schema validate document.md schema.json
```

**Success output:**
```
✓ Validation passed: document.md
  - All frontmatter properties valid
  - All required sections present
  - All section constraints satisfied
```

**Failure output:**
```
✗ Validation failed: document.md

Frontmatter errors:
  - Property 'title' is required but missing
  - Property 'status' value 'archived' not in enum: ['draft', 'published']

Section errors:
  - Required section 'introduction' is missing
  - Section 'overview' has 0 blocks (minimum: 1)
```

### Verbose Validation

```bash
mddata schema validate document.md schema.json --verbose
```

**Verbose output:**
```
Validating document.md against schema.json

Frontmatter validation:
  ✓ title: "API Guide" (type: str)
  ✓ version: 1.0 (type: float)
  ✓ status: "draft" (enum: ['draft', 'published'])
  ✓ tags: ["api", "guide"] (type: list)

Section validation:
  ✓ introduction (required: true, blocks: 2, min_blocks: 1)
    ✓ introduction.overview (required: true, blocks: 1, min_blocks: 1)

✓ Validation passed: All constraints satisfied
```

### Format Auto-Detection

Schemas are automatically detected by file extension:

```bash
# JSON schema
mddata schema validate document.md schema.json

# YAML schema
mddata schema validate document.md schema.yaml
mddata schema validate document.md schema.yml
```

## Inspecting Schemas

Display schema information without a document:

```bash
mddata schema info schema.json
```

**Output:**
```
Schema Information: schema.json

Validation Level: warnings

Frontmatter Properties (4):
  title (str, required)
  version (float, required)
  status (str, required, enum: ['draft', 'published'])
  tags (list, required)

Sections (2):
  introduction
    Required: true
    Min blocks: 1
    Subsections: 1
      overview (required: true, min_blocks: 1)

  installation
    Required: false
    Min blocks: 1
```

**YAML schema:**
```bash
mddata schema info schema.yaml
```

## Practical Examples

### Example 1: Enforce Documentation Standards

```bash
# Generate schema from template document
mddata schema generate template.md --mode strict --output docs-schema.json

# Validate all documents
for doc in docs/*.md; do
  mddata schema validate "$doc" docs-schema.json
done
```

### Example 2: Quality Assurance

```bash
# Generate permissive schema from existing docs
mddata schema generate ./existing-docs/ --output baseline-schema.json --pretty

# Validate new documents
mddata schema validate new-document.md baseline-schema.json --verbose
```

### Example 3: Migration Validation

```bash
# Before migration: generate schema
mddata schema generate old-format.md --output migration-schema.json

# After migration: validate
mddata schema validate new-format.md migration-schema.json

# Inspect differences
mddata schema info migration-schema.json
```

### Example 4: CI/CD Integration

```bash
#!/bin/bash
# validate-docs.sh

SCHEMA="docs/schema.json"
FAILED=0

echo "Validating documentation..."

for doc in docs/**/*.md; do
  if ! mddata schema validate "$doc" "$SCHEMA"; then
    echo "❌ Failed: $doc"
    FAILED=$((FAILED + 1))
  else
    echo "✅ Passed: $doc"
  fi
done

if [ $FAILED -gt 0 ]; then
  echo "Validation failed: $FAILED document(s)"
  exit 1
fi

echo "All documents valid!"
```

### Example 5: Schema Evolution

```bash
# Generate current state schema
mddata schema generate ./docs/ --output current-schema.json --pretty

# Review changes
diff previous-schema.json current-schema.json

# Update schema
cp current-schema.json docs-schema.json
```

## Schema Workflows

### Workflow 1: New Project

```bash
# 1. Create template document
cat > template.md << 'EOF'
---
title: "Document Title"
version: 1.0
status: "draft"
tags: []
---

# Introduction

Content here.

## Overview

More content.
EOF

# 2. Generate strict schema
mddata schema generate template.md --mode strict --output project-schema.json --pretty

# 3. Validate new documents
mddata schema validate new-doc.md project-schema.json
```

### Workflow 2: Existing Project

```bash
# 1. Generate permissive schema from all docs
mddata schema generate ./docs/ --output baseline-schema.json --pretty

# 2. Review and edit schema manually
vi baseline-schema.json

# 3. Validate all documents
for doc in docs/**/*.md; do
  mddata schema validate "$doc" baseline-schema.json --verbose
done
```

### Workflow 3: Schema Refinement

```bash
# 1. Generate initial schema
mddata schema generate doc.md --output v1-schema.json

# 2. Add custom validations
cat > v2-schema.json << 'EOF'
{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true,
      "validations": [
        {"type": "min_length", "value": 5, "message": "Title too short"},
        {"type": "max_length", "value": 100, "message": "Title too long"}
      ]
    },
    "version": {
      "type": "float",
      "required": true,
      "validations": [
        {"type": "min", "value": 1.0, "message": "Version must be >= 1.0"}
      ]
    }
  },
  "validation_level": "strict"
}
EOF

# 3. Validate with refined schema
mddata schema validate doc.md v2-schema.json --verbose
```

## Format Comparison

| Feature | JSON | YAML |
|---------|------|------|
| Human-readable | ✓ | ✓✓ |
| Easy to edit | ✓ | ✓✓ |
| Compact | ✓✓ | ✓ |
| Comments | ✗ | ✓ |
| Widely supported | ✓✓ | ✓ |
| Tool support | ✓✓ | ✓ |

**Recommendation:**
- Use **YAML** for manual editing and version control
- Use **JSON** for programmatic generation and API integration
- Both formats are fully interchangeable

## Command Reference

| Command | Description | Output |
|---------|-------------|--------|
| `schema generate <file>` | Generate schema from document | JSON/YAML schema |
| `schema generate <folder>` | Generate merged schema | JSON/YAML schema |
| `schema generate --mode strict` | Generate strict schema | Strict constraints |
| `schema generate --format yaml` | Generate YAML schema | YAML format |
| `schema validate <doc> <schema>` | Validate document | Pass/fail report |
| `schema validate --verbose` | Detailed validation | Verbose report |
| `schema info <schema>` | Display schema info | Schema summary |

## Next Steps

- [Generate documents from schemas](05-markdown-generation.md) - Create templates
- [Modify documents](06-data-transformation.md) - Make schema-compliant changes
- [Complex transformations](07-complex-transformations.md) - Advanced schema usage
