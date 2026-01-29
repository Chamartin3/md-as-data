# Markdown Schema Format

This guide explains the JSON/YAML schema format for defining validation rules and structure requirements for markdown documents. Schemas ensure document consistency, validate content, and help generate compliant documents.

## Use Cases

Use Markdown Schemas when you need to:

- **Validate documents** against defined structure and rules
- **Ensure consistency** across multiple documents
- **Generate templates** with predefined structure and defaults
- **Document requirements** for markdown file structure
- **Auto-generate schemas** from existing documents to capture patterns
- **Enforce standards** for team documentation

### CLI Commands

The Markdown Schema format is used by these commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `mddata schema generate` | Create schema from document(s) | `mddata schema generate doc.md -o schema.json` |
| `mddata schema validate` | Validate document against schema | `mddata schema validate doc.md schema.json` |
| `mddata schema info` | Display schema information | `mddata schema info schema.json` |
| `mddata generate --schema` | Generate template from schema | `mddata generate --schema schema.json -o template.md` |

---

## Structure Overview

A schema defines two types of rules:

```
Markdown Schema
├── properties      → Frontmatter property rules
│   └── property_name
│       ├── type (str, int, bool, list, etc.)
│       ├── required (true/false)
│       ├── default (value)
│       ├── enum (allowed values)
│       └── validations (constraints)
│
└── sections        → Content structure rules
    └── section_id
        ├── description
        ├── validation (block rules)
        └── children (nested sections)
```

**Minimal schema:**

```json
{
  "version": "1.0.0",
  "properties": {},
  "sections": {}
}
```

---

## Complete Structure Reference

### Schema Root

```json
{
  "version": "1.0.0",
  "properties": { /* property schemas */ },
  "sections": { /* section schemas */ }
}
```

**Three fields (all optional):**
- `version` - Schema version identifier
- `properties` - Frontmatter property validation rules
- `sections` - Document structure validation rules

---

## Version

Optional version identifier for schema tracking.

```json
{
  "version": "1.0.0"
}
```

**Format:** Typically semantic versioning (e.g., `"1.0.0"`, `"2.1.3"`)

**Usage:**
- Track schema changes over time
- Ensure compatibility between tools
- Document schema evolution

---

## Properties

Define validation rules for frontmatter properties.

### Structure

```json
{
  "properties": {
    "property_name": {
      "type": "str",
      "required": true,
      "default": "value",
      "description": "Property description",
      "enum": ["option1", "option2"],
      "validations": []
    }
  }
}
```

Each property name maps to a **Property Schema** object.

### Property Schema

#### `type` (string, required)

Property data type. Determines what values are allowed.

**Supported types:**

| Type | Description | Example Values |
|------|-------------|----------------|
| `"str"` | String/text | `"hello"`, `"2025-10-21"` |
| `"int"` | Integer number | `42`, `-10`, `0` |
| `"float"` | Decimal number | `3.14`, `-0.5`, `100.0` |
| `"bool"` | Boolean | `true`, `false` |
| `"list"` | Array/list | `["item1", "item2"]` |
| `"dict"` | Object/dictionary | `{"key": "value"}` |

**Union types** (multiple types allowed):
- `"str|int"` - String or integer
- `"str|null"` - String or null
- `"int|float"` - Integer or decimal

#### `required` (boolean, optional)

Whether the property must be present in documents.

```json
{
  "title": {
    "type": "str",
    "required": true  // Document must have a title
  },
  "draft": {
    "type": "bool",
    "required": false  // Draft is optional
  }
}
```

**Default:** `false` (property is optional)

#### `default` (any, optional)

Default value used when property is missing.

```json
{
  "status": {
    "type": "str",
    "required": false,
    "default": "draft"  // Use "draft" if not specified
  },
  "version": {
    "type": "int",
    "required": false,
    "default": 1
  }
}
```

**Type must match:** Default value type must match the specified `type`.

#### `description` (string, optional)

Human-readable description of the property's purpose.

```json
{
  "priority": {
    "type": "int",
    "required": true,
    "description": "Task priority level from 1 (highest) to 5 (lowest)"
  }
}
```

#### `enum` (array, optional)

List of allowed values for the property.

```json
{
  "status": {
    "type": "str",
    "required": false,
    "enum": ["draft", "published", "archived"]
  },
  "category": {
    "type": "str",
    "enum": ["tutorial", "guide", "reference", "api"]
  }
}
```

**Auto-generated:** When generating schemas from documents, `enum` is automatically created for single-word string properties with consistent values.

**Null support:**
```json
{
  "optional_field": {
    "type": "str",
    "enum": ["value1", "value2", null]  // Allows null as valid value
  }
}
```

#### `validations` (array, optional)

Additional validation rules for the property. See [Validation Rules](#validation-rules).

### Property Examples

**Simple string:**
```json
{
  "title": {
    "type": "str",
    "required": true
  }
}
```

**String with constraints:**
```json
{
  "title": {
    "type": "str",
    "required": true,
    "validations": [
      {
        "type": "min_length",
        "value": 1,
        "message": "Title cannot be empty"
      },
      {
        "type": "max_length",
        "value": 100,
        "message": "Title too long (max 100 characters)"
      }
    ]
  }
}
```

**Enumerated values:**
```json
{
  "status": {
    "type": "str",
    "required": false,
    "default": "draft",
    "enum": ["draft", "review", "published", "archived"],
    "description": "Document publication status"
  }
}
```

**Integer with range:**
```json
{
  "priority": {
    "type": "int",
    "required": true,
    "default": 3,
    "validations": [
      {
        "type": "min_value",
        "value": 1,
        "message": "Priority must be at least 1"
      },
      {
        "type": "max_value",
        "value": 5,
        "message": "Priority cannot exceed 5"
      }
    ],
    "description": "Priority level (1-5)"
  }
}
```

**List/array:**
```json
{
  "tags": {
    "type": "list",
    "required": false,
    "default": [],
    "description": "Document tags for categorization"
  }
}
```

**Union type:**
```json
{
  "version": {
    "type": "str|int",
    "required": true,
    "description": "Version number (string like '1.0' or integer like 1)"
  }
}
```

---

## Validation Rules

Additional constraints for property values.

### Validation Rule Structure

```json
{
  "type": "validation_type",
  "value": "constraint_value",
  "message": "Custom error message"
}
```

**Fields:**
- `type` (string, required) - Validation type
- `value` (any, required) - Constraint value
- `message` (string, required) - Error message shown when validation fails

### String Validations

#### Minimum Length

```json
{
  "type": "min_length",
  "value": 5,
  "message": "Must be at least 5 characters"
}
```

Ensures string has at least the specified number of characters.

#### Maximum Length

```json
{
  "type": "max_length",
  "value": 100,
  "message": "Cannot exceed 100 characters"
}
```

Ensures string does not exceed the specified length.

#### Pattern Matching

```json
{
  "type": "pattern",
  "value": "^[A-Z].*",
  "message": "Must start with a capital letter"
}
```

Validates string against a regular expression pattern.

**Common patterns:**
- Email: `"^[^@]+@[^@]+\\.[^@]+$"`
- URL: `"^https?://.*"`
- Date: `"^\\d{4}-\\d{2}-\\d{2}$"` (YYYY-MM-DD)
- Username: `"^[a-zA-Z0-9_]{3,20}$"` (3-20 alphanumeric + underscore)

### Numeric Validations

#### Minimum Value

```json
{
  "type": "min_value",
  "value": 0,
  "message": "Must be non-negative"
}
```

Ensures number is at least the specified value.

#### Maximum Value

```json
{
  "type": "max_value",
  "value": 100,
  "message": "Cannot exceed 100"
}
```

Ensures number does not exceed the specified value.

### Validation Examples

**Email validation:**
```json
{
  "email": {
    "type": "str",
    "required": true,
    "validations": [
      {
        "type": "pattern",
        "value": "^[^@]+@[^@]+\\.[^@]+$",
        "message": "Invalid email format"
      }
    ]
  }
}
```

**Date format:**
```json
{
  "date": {
    "type": "str",
    "required": true,
    "validations": [
      {
        "type": "pattern",
        "value": "^\\d{4}-\\d{2}-\\d{2}$",
        "message": "Date must be in YYYY-MM-DD format"
      }
    ]
  }
}
```

**Percentage:**
```json
{
  "completion": {
    "type": "int",
    "required": true,
    "validations": [
      {
        "type": "min_value",
        "value": 0,
        "message": "Percentage cannot be negative"
      },
      {
        "type": "max_value",
        "value": 100,
        "message": "Percentage cannot exceed 100"
      }
    ]
  }
}
```

---

## Sections

Define structure and content requirements for document sections.

### Structure

```json
{
  "sections": {
    "section_id": {
      "description": "Section description",
      "validation": {
        "required": true,
        "min_blocks": 1,
        "max_blocks": 10,
        "allowed_content": ["paragraph", "list"]
      },
      "children": {
        "child_section_id": {
          // Nested section schema
        }
      }
    }
  }
}
```

Each section ID maps to a **Section Schema** object.

### Section Schema

#### `description` (string, optional)

Human-readable description of the section's purpose.

```json
{
  "introduction": {
    "description": "Opening section that provides document overview"
  }
}
```

#### `validation` (object, optional)

Content validation rules for this section. See [Section Validation](#section-validation).

#### `children` (object, optional)

Nested section schemas using the same structure (recursive).

```json
{
  "getting_started": {
    "description": "Getting started guide",
    "children": {
      "prerequisites": {
        "description": "Required software and knowledge"
      },
      "installation": {
        "description": "Installation instructions"
      }
    }
  }
}
```

### Section Validation

#### `required` (boolean, optional)

Whether the section must exist in documents.

```json
{
  "introduction": {
    "validation": {
      "required": true  // Document must have introduction section
    }
  },
  "appendix": {
    "validation": {
      "required": false  // Appendix is optional
    }
  }
}
```

#### `min_blocks` (integer, optional)

Minimum number of content blocks required in the section.

```json
{
  "introduction": {
    "validation": {
      "min_blocks": 1  // Must have at least 1 block
    }
  }
}
```

#### `max_blocks` (integer, optional)

Maximum number of content blocks allowed in the section.

```json
{
  "summary": {
    "validation": {
      "max_blocks": 3  // Cannot have more than 3 blocks
    }
  }
}
```

#### `allowed_content` (array, optional)

List of allowed block types for this section.

```json
{
  "examples": {
    "validation": {
      "allowed_content": ["code_block", "paragraph"]
    }
  }
}
```

**Supported block types:**
- `"paragraph"` - Text paragraphs
- `"code_block"` - Code blocks
- `"list"` - Unordered lists
- `"ordered_list"` - Numbered lists
- `"task_list"` - Task checklists
- `"blockquote"` - Quoted text
- `"table"` - Tables
- `"link"` - Links
- `"image"` - Images

### Section Examples

**Required section:**
```json
{
  "introduction": {
    "description": "Document introduction",
    "validation": {
      "required": true,
      "min_blocks": 1,
      "max_blocks": 3,
      "allowed_content": ["paragraph"]
    }
  }
}
```

**Optional section with flexible content:**
```json
{
  "notes": {
    "description": "Additional notes and remarks",
    "validation": {
      "required": false,
      "allowed_content": ["paragraph", "list", "blockquote"]
    }
  }
}
```

**Code examples section:**
```json
{
  "examples": {
    "description": "Code examples and demonstrations",
    "validation": {
      "required": false,
      "min_blocks": 1,
      "allowed_content": ["code_block", "paragraph"]
    }
  }
}
```

**Hierarchical structure:**
```json
{
  "guide": {
    "description": "User guide",
    "validation": {
      "required": true
    },
    "children": {
      "basics": {
        "description": "Basic concepts",
        "validation": {
          "required": true,
          "min_blocks": 1
        }
      },
      "advanced": {
        "description": "Advanced topics",
        "validation": {
          "required": false
        },
        "children": {
          "performance": {
            "description": "Performance optimization"
          },
          "security": {
            "description": "Security best practices"
          }
        }
      }
    }
  }
}
```

---

## Complete Schema Examples

### Simple Document Schema

```json
{
  "version": "1.0.0",
  "properties": {
    "title": {
      "type": "str",
      "required": true,
      "validations": [
        {
          "type": "min_length",
          "value": 1,
          "message": "Title cannot be empty"
        }
      ]
    },
    "author": {
      "type": "str",
      "required": true
    },
    "date": {
      "type": "str",
      "required": true,
      "validations": [
        {
          "type": "pattern",
          "value": "^\\d{4}-\\d{2}-\\d{2}$",
          "message": "Date must be YYYY-MM-DD"
        }
      ]
    },
    "tags": {
      "type": "list",
      "required": false,
      "default": []
    }
  },
  "sections": {
    "introduction": {
      "description": "Document introduction",
      "validation": {
        "required": true,
        "min_blocks": 1
      }
    },
    "content": {
      "description": "Main content",
      "validation": {
        "required": true
      }
    }
  }
}
```

### Blog Post Schema

```json
{
  "version": "1.0.0",
  "properties": {
    "title": {
      "type": "str",
      "required": true,
      "validations": [
        {
          "type": "min_length",
          "value": 10,
          "message": "Title too short"
        },
        {
          "type": "max_length",
          "value": 100,
          "message": "Title too long"
        }
      ]
    },
    "author": {
      "type": "str",
      "required": true
    },
    "date": {
      "type": "str",
      "required": true
    },
    "status": {
      "type": "str",
      "required": false,
      "default": "draft",
      "enum": ["draft", "published", "archived"]
    },
    "tags": {
      "type": "list",
      "required": false,
      "default": []
    },
    "excerpt": {
      "type": "str",
      "required": false,
      "validations": [
        {
          "type": "max_length",
          "value": 200,
          "message": "Excerpt too long"
        }
      ]
    }
  },
  "sections": {
    "introduction": {
      "description": "Post introduction",
      "validation": {
        "required": true,
        "min_blocks": 1,
        "max_blocks": 3,
        "allowed_content": ["paragraph"]
      }
    },
    "content": {
      "description": "Main post content",
      "validation": {
        "required": true,
        "min_blocks": 3,
        "allowed_content": ["paragraph", "list", "code_block", "blockquote"]
      }
    },
    "conclusion": {
      "description": "Post conclusion",
      "validation": {
        "required": false,
        "max_blocks": 2,
        "allowed_content": ["paragraph"]
      }
    }
  }
}
```

### API Documentation Schema

```json
{
  "version": "1.0.0",
  "properties": {
    "endpoint": {
      "type": "str",
      "required": true,
      "description": "API endpoint path"
    },
    "method": {
      "type": "str",
      "required": true,
      "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
      "description": "HTTP method"
    },
    "version": {
      "type": "str",
      "required": false,
      "default": "v1"
    },
    "deprecated": {
      "type": "bool",
      "required": false,
      "default": false
    }
  },
  "sections": {
    "overview": {
      "description": "Endpoint overview",
      "validation": {
        "required": true,
        "min_blocks": 1,
        "max_blocks": 3,
        "allowed_content": ["paragraph"]
      }
    },
    "request": {
      "description": "Request specification",
      "validation": {
        "required": true
      },
      "children": {
        "headers": {
          "description": "Request headers",
          "validation": {
            "allowed_content": ["code_block", "paragraph"]
          }
        },
        "body": {
          "description": "Request body",
          "validation": {
            "allowed_content": ["code_block", "paragraph"]
          }
        }
      }
    },
    "response": {
      "description": "Response specification",
      "validation": {
        "required": true
      },
      "children": {
        "success": {
          "description": "Success responses",
          "validation": {
            "required": true,
            "allowed_content": ["code_block", "paragraph"]
          }
        },
        "errors": {
          "description": "Error responses",
          "validation": {
            "allowed_content": ["code_block", "paragraph"]
          }
        }
      }
    },
    "examples": {
      "description": "Usage examples",
      "validation": {
        "required": false,
        "allowed_content": ["code_block", "paragraph"]
      }
    }
  }
}
```

---

## CLI Usage Examples

### Generate Schema

```bash
# From single document
mddata schema generate document.md --output schema.json

# Pretty formatting
mddata schema generate document.md --output schema.json --pretty

# YAML format
mddata schema generate document.md --format yaml --output schema.yaml

# From multiple documents (aggregated)
mddata schema generate ./docs/ --output aggregated_schema.json --pretty
```

**Multi-file behavior:**
- Aggregates properties across all documents
- Properties in ≥75% of files marked as required
- Creates enum types for consistent single-word values
- Merges all section hierarchies
- Uses union types for conflicting property types

### Validate Documents

```bash
# Basic validation
mddata schema validate document.md schema.json

# Verbose output (show all issues)
mddata schema validate document.md schema.json --verbose

# Works with YAML schemas (auto-detected)
mddata schema validate document.md schema.yaml
```

### Display Schema Info

```bash
# Show schema details
mddata schema info schema.json

# Works with YAML
mddata schema info schema.yaml
```

### Generate Template

```bash
# Create template from schema
mddata generate --schema schema.json --output template.md

# With force overwrite
mddata generate --schema schema.json --output template.md --force
```

**Generated template includes:**
- Frontmatter with default values
- Section structure from schema
- Placeholder content for sections

### Validated Generation

```bash
# Generate with validation
mddata generate \
  --data data.json \
  --schema schema.json \
  --output validated.md
```

---

## YAML Format

All schemas work in YAML format:

```yaml
version: "1.0.0"

properties:
  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 1
        message: "Title cannot be empty"

  status:
    type: str
    required: false
    default: draft
    enum:
      - draft
      - published
      - archived

  tags:
    type: list
    required: false
    default: []

sections:
  introduction:
    description: "Document introduction"
    validation:
      required: true
      min_blocks: 1
      max_blocks: 3
      allowed_content:
        - paragraph

  content:
    description: "Main content"
    validation:
      required: true
    children:
      examples:
        description: "Code examples"
        validation:
          allowed_content:
            - code_block
            - paragraph
```

---

## Schema Generation Strategies

### Permissive Mode (Default)

Generates flexible schemas that allow document evolution:

```bash
mddata schema generate document.md --output schema.json
```

**Characteristics:**
- Optional properties unless very common (≥75% of files)
- Wide content type allowances
- Flexible block constraints
- Suitable for evolving documentation

### Strict Mode

Generates exact schemas matching current structure:

```bash
mddata schema generate document.md --mode strict --output schema.json
```

**Characteristics:**
- Exact block counts (min = max = actual count)
- All present properties marked required
- Strict content type restrictions
- Suitable for enforcing templates

---

## Common Workflows

### Create Standard Template

```bash
# 1. Generate schema from example document
mddata schema generate example.md --output standard_schema.json

# 2. Create template from schema
mddata generate --schema standard_schema.json --output template.md

# 3. Use template for new documents
cp template.md new_document.md
# Edit new_document.md
```

### Validate Documentation Set

```bash
# 1. Generate schema from all documents
mddata schema generate ./docs/ --output docs_schema.json

# 2. Validate each document
for doc in ./docs/*.md; do
  echo "Validating $doc"
  mddata schema validate "$doc" docs_schema.json --verbose
done
```

### Enforce Team Standards

```bash
# 1. Create canonical schema for document type
# Edit schema.json to define team standards

# 2. Pre-commit validation hook
#!/bin/bash
for file in $(git diff --cached --name-only | grep '\.md$'); do
  if ! mddata schema validate "$file" schema.json; then
    echo "Schema validation failed for $file"
    exit 1
  fi
done
```

---

## Tips and Best Practices

### Schema Design

1. **Start permissive**: Use permissive schemas initially, tighten as patterns emerge
2. **Document requirements**: Use `description` fields extensively
3. **Provide defaults**: Set sensible defaults for optional properties
4. **Use enums**: Define categorical values with `enum` for consistency
5. **Validate early**: Add validations to catch errors early

### Property Design

```yaml
# Good property design
email:
  type: str
  required: true
  description: "Author contact email"
  validations:
    - type: pattern
      value: "^[^@]+@[^@]+\\.[^@]+$"
      message: "Invalid email format"

priority:
  type: int
  required: false
  default: 3
  description: "Priority level (1-5, higher is more important)"
  validations:
    - type: min_value
      value: 1
      message: "Priority must be at least 1"
    - type: max_value
      value: 5
      message: "Priority cannot exceed 5"
```

### Section Design

```yaml
# Good section design
sections:
  introduction:
    description: "Opening section providing document overview"
    validation:
      required: true
      min_blocks: 1
      max_blocks: 3
      allowed_content:
        - paragraph

  examples:
    description: "Working code examples"
    validation:
      required: false
      min_blocks: 1
      allowed_content:
        - code_block
        - paragraph
```

---

## Troubleshooting

### Common Issues

**"Validation failed: missing required property"**
- Check schema for `required: true` properties
- Ensure document has all required frontmatter fields
- Use `mddata info properties document.md` to see current properties

**"Validation failed: section not found"**
- Schema requires section that document doesn't have
- Check section IDs match exactly (case-sensitive)
- Use `mddata info sections document.md` to see structure

**"Validation failed: invalid block type"**
- Section contains blocks not in `allowed_content` list
- Review `allowed_content` constraints
- Use `mddata info blocks document.md` to see block types

**"Schema generation from directory found no files"**
- Ensure directory contains `.md` files
- Check recursive search is working
- Verify file permissions

### Debugging Validation

```bash
# Check what schema expects
mddata schema info schema.json

# See document structure
mddata info sections document.md --paths
mddata info properties document.md

# Verbose validation output
mddata schema validate document.md schema.json --verbose

# Test schema with known-good document
mddata schema validate example.md schema.json
```

---

## Related Documentation

- [Markdown Data Format](MARKDOWN_DATA.md) - Document data structure reference
- [CLI Reference](CLI_REFERENCE.md) - Complete command documentation
- [Examples](../examples/schemas/) - Schema example files
