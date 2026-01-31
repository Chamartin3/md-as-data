# Markdown Generation

## Overview

The `mddata generate` command creates markdown documents from structured data sources:
- **From JSON data** - Generate markdown from MarkdownDataDict format
- **From schemas** - Generate document templates from schema definitions
- **Combined mode** - Generate with data validated against schema

This is useful for:
- Automated document generation
- Template-based documentation
- Data-driven content creation
- Schema-based document scaffolding

## Command Structure

```bash
mddata generate [--data source] [--schema source] [--output file] [--force]
```

**At least one source is required:**
- `--data` or `-d` - Generate from JSON data (MarkdownDataDict format)
- `--schema` or `-s` - Generate template from schema
- Both - Generate from data and validate against schema

## Generate from JSON Data

### Basic Generation

Create markdown from a JSON data file:

```bash
mddata generate --data data.json --output document.md
```

**Input data (data.json):**
```json
{
  "frontmatter": {
    "title": "API Documentation",
    "version": 1.0,
    "status": "draft",
    "tags": ["api", "reference"]
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph",
            "content": "Welcome to the API documentation."
          }
        ],
        "children": [
          {
            "id": "overview",
            "title": "Overview",
            "level": 2,
            "blocks": [
              {
                "type": "paragraph",
                "content": "This API provides RESTful endpoints."
              },
              {
                "type": "list",
                "content": "- Authentication endpoints\n- User management\n- Data operations"
              }
            ],
            "children": []
          }
        ]
      }
    ]
  }
}
```

**Generated markdown (document.md):**
```markdown
---
title: "API Documentation"
version: 1.0
status: "draft"
tags: ["api", "reference"]
---

# Introduction

Welcome to the API documentation.

## Overview

This API provides RESTful endpoints.

- Authentication endpoints
- User management
- Data operations
```

### Short Form

```bash
mddata generate -d data.json -o document.md
```

### From stdin

```bash
cat data.json | mddata generate --data - --output document.md
```

```bash
echo '{"frontmatter": {"title": "Quick Doc"}, "content": {"id": "", "title": "", "level": 0, "path": "", "blocks": [], "children": []}}' | mddata generate -d - -o quick.md
```

### Print to stdout

```bash
mddata generate --data data.json
```

Output markdown is printed to console instead of file.

### Overwrite Existing Files

```bash
mddata generate --data data.json --output existing.md --force
```

Without `--force`, the command will fail if the output file already exists.

## Generate from Schema (Templates)

### Basic Template Generation

Create a markdown template from a schema:

```bash
mddata generate --schema schema.json --output template.md
```

**Input schema (schema.json):**
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
      "required": false,
      "default": "draft",
      "enum": ["draft", "published", "archived"]
    },
    "tags": {
      "type": "list",
      "required": false
    }
  },
  "sections": {
    "introduction": {
      "validation": {
        "required": true,
        "min_blocks": 1
      },
      "children": {
        "overview": {
          "validation": {
            "required": true,
            "min_blocks": 1
          }
        }
      }
    },
    "configuration": {
      "validation": {
        "required": false
      }
    }
  }
}
```

**Generated template (template.md):**
```markdown
---
title: ""
version: 0.0
status: "draft"
tags: []
---

# Introduction

[Content required]

## Overview

[Content required]

# Configuration

[Optional content]
```

**Template generation rules:**
1. **Required properties**: Empty placeholders matching type
2. **Optional properties with defaults**: Default values used
3. **Optional properties without defaults**: Empty placeholders
4. **Required sections**: `[Content required]` placeholder
5. **Optional sections**: `[Optional content]` placeholder
6. **Section hierarchy**: Preserved from schema

### YAML Schema

```bash
mddata generate --schema schema.yaml --output template.md
```

Works with both JSON and YAML schemas (auto-detected).

## Generate with Validation

Combine data generation with schema validation:

```bash
mddata generate --data data.json --schema schema.json --output document.md
```

**Behavior:**
1. Loads data from JSON file
2. Validates data against schema
3. If validation passes: generates markdown
4. If validation fails: shows errors and exits

**Example validation failure:**
```bash
mddata generate -d invalid-data.json -s schema.json -o doc.md
```

**Output:**
```
✗ Validation failed:

Frontmatter errors:
  - Property 'title' is required but missing
  - Property 'status' value 'unknown' not in enum: ['draft', 'published', 'archived']

Section errors:
  - Required section 'introduction' is missing

Generation aborted due to validation errors.
```

## Data Format (MarkdownDataDict)

The expected JSON structure for `--data` input:

```json
{
  "frontmatter": {
    // Property name: value pairs
    "string_prop": "text",
    "number_prop": 42,
    "bool_prop": true,
    "list_prop": ["item1", "item2"],
    "object_prop": {"key": "value"}
  },
  "content": {
    "sections": [
      {
        "id": "section_id",          // Required: section identifier
        "title": "Section Title",     // Required: heading text
        "level": 1,                   // Required: heading level (1-6)
        "blocks": [                   // Optional: content blocks
          {
            "type": "paragraph",      // Required: block type
            "content": "Text content", // Required: block content
            "attributes": {}          // Optional: type-specific attrs
          }
        ],
        "children": [              // Optional: nested sections
          // Same structure as sections
        ]
      }
    ]
  }
}
```

### Minimal Example

```json
{
  "frontmatter": {},
  "content": {
    "sections": []
  }
}
```

Generates:
```markdown
---
---

```

### Full Example

```json
{
  "frontmatter": {
    "title": "User Guide",
    "author": "John Doe",
    "version": 2.5,
    "published": true,
    "tags": ["guide", "tutorial"]
  },
  "content": {
    "sections": [
      {
        "id": "getting_started",
        "title": "Getting Started",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph",
            "content": "This guide will help you get started quickly."
          },
          {
            "type": "list",
            "content": "- Install the software\n- Configure settings\n- Run first example",
            "attributes": {"ordered": false}
          }
        ],
        "children": [
          {
            "id": "installation",
            "title": "Installation",
            "level": 2,
            "blocks": [
              {
                "type": "paragraph",
                "content": "Follow these steps to install:"
              },
              {
                "type": "code_block",
                "content": "npm install package-name",
                "attributes": {"language": "bash"}
              }
            ],
            "children": []
          }
        ]
      }
    ]
  }
}
```

Generates:
```markdown
---
title: "User Guide"
author: "John Doe"
version: 2.5
published: true
tags: ["guide", "tutorial"]
---

# Getting Started

This guide will help you get started quickly.

- Install the software
- Configure settings
- Run first example

## Installation

Follow these steps to install:

```bash
npm install package-name
```
```

## Block Types Reference

### Paragraph

```json
{
  "type": "paragraph",
  "content": "Regular text content with **markdown** formatting."
}
```

### Heading

```json
{
  "type": "heading",
  "content": "Section Title",
  "attributes": {"level": 2}
}
```

Note: Headings are usually created automatically from section structure.

### List

**Unordered:**
```json
{
  "type": "list",
  "content": "- Item 1\n- Item 2\n- Item 3",
  "attributes": {"ordered": false}
}
```

**Ordered:**
```json
{
  "type": "list",
  "content": "1. First item\n2. Second item\n3. Third item",
  "attributes": {"ordered": true}
}
```

### Code Block

```json
{
  "type": "code_block",
  "content": "def hello():\n    print('Hello, world!')",
  "attributes": {"language": "python"}
}
```

### Blockquote

```json
{
  "type": "blockquote",
  "content": "This is a quoted text.\n\nIt can span multiple paragraphs."
}
```

### Thematic Break

```json
{
  "type": "thematic_break",
  "content": ""
}
```

Generates: `---`

### HTML Block

```json
{
  "type": "html_block",
  "content": "<div class=\"alert\">\n  <p>Custom HTML content</p>\n</div>"
}
```

## Practical Examples

### Example 1: Automated Report Generation

```bash
# Generate report data with script
cat > report-data.json << 'EOF'
{
  "frontmatter": {
    "title": "Monthly Report",
    "date": "2025-10-23",
    "period": "October 2025"
  },
  "content": {
    "sections": [
      {
        "id": "summary",
        "title": "Summary",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph",
            "content": "This month showed significant progress."
          }
        ],
        "children": []
      }
    ]
  }
}
EOF

# Generate report
mddata generate -d report-data.json -o monthly-report.md
```

### Example 2: Template Scaffolding

```bash
# Create schema for new documents
cat > doc-schema.json << 'EOF'
{
  "frontmatter": {
    "title": {"type": "str", "required": true},
    "author": {"type": "str", "required": true},
    "date": {"type": "str", "required": true}
  },
  "sections": {
    "abstract": {"validation": {"required": true}},
    "introduction": {"validation": {"required": true}},
    "methodology": {"validation": {"required": true}},
    "results": {"validation": {"required": true}},
    "conclusion": {"validation": {"required": true}}
  }
}
EOF

# Generate template
mddata generate -s doc-schema.json -o paper-template.md

# Result: template with all required sections
```

### Example 3: Pipeline Integration

```bash
# Extract from source, transform, generate new document
mddata extract json source.md | \
  jq '.frontmatter.status = "published"' | \
  mddata generate -d - -o published.md
```

### Example 4: Batch Generation

```bash
# Generate multiple documents from data files
for data_file in data/*.json; do
  output_file="docs/$(basename ${data_file%.json}).md"
  mddata generate -d "$data_file" -o "$output_file"
done
```

### Example 5: Validated Generation

```bash
# Generate with validation
mddata generate \
  --data user-content.json \
  --schema content-schema.json \
  --output validated-doc.md

# Only creates document if validation passes
```

## Round-Trip Workflow

Extract → Modify → Generate:

```bash
# 1. Extract document to JSON
mddata extract json original.md --pretty --output data.json

# 2. Modify data
jq '.frontmatter.version = 2.0 | .frontmatter.status = "published"' data.json > modified.json

# 3. Generate new document
mddata generate -d modified.json -o updated.md

# 4. Validate against schema (optional)
mddata schema validate updated.md schema.json
```

## Error Handling

### Missing Required Source

```bash
mddata generate -o output.md
```

```
Error: At least one source is required (--data or --schema)
```

### Invalid JSON Format

```bash
mddata generate -d invalid.json -o doc.md
```

```
Error: Invalid JSON format in data file
  Line 5: Unexpected token
```

### File Exists Without --force

```bash
mddata generate -d data.json -o existing.md
```

```
Error: Output file 'existing.md' already exists
Use --force to overwrite
```

### Schema Validation Failure

```bash
mddata generate -d data.json -s schema.json -o doc.md
```

```
✗ Validation failed: [errors listed]
Generation aborted
```

## Command Options Reference

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--data <file>` | `-d` | * | Data source (JSON, use `-` for stdin) |
| `--schema <file>` | `-s` | * | Schema source (JSON/YAML) |
| `--output <file>` | `-o` | No | Output file (default: stdout) |
| `--force` | | No | Overwrite existing output file |

\* At least one of `--data` or `--schema` is required

## Integration Examples

### With Scripts

```python
#!/usr/bin/env python3
import json
import subprocess

# Build data structure
data = {
    "frontmatter": {"title": "Generated Doc"},
    "content": {"id": "", "title": "", "level": 0, "path": "", "blocks": [], "children": []}
}

# Generate markdown
proc = subprocess.run(
    ["mddata", "generate", "-d", "-", "-o", "output.md"],
    input=json.dumps(data),
    text=True
)
```

### With APIs

```javascript
const { exec } = require('child_process');
const fs = require('fs');

// Fetch data from API
fetch('https://api.example.com/content')
  .then(res => res.json())
  .then(data => {
    // Write to temp file
    fs.writeFileSync('/tmp/data.json', JSON.stringify(data));

    // Generate markdown
    exec('mddata generate -d /tmp/data.json -o output.md', (err, stdout) => {
      if (err) throw err;
      console.log('Document generated');
    });
  });
```

### With Build Systems

```makefile
# Makefile
docs/%.md: data/%.json schemas/doc.json
	mddata generate -d $< -s schemas/doc.json -o $@ --force

all: docs/guide.md docs/api.md docs/tutorial.md
```

## Next Steps

- [Transform existing documents](06-data-transformation.md) - Modify content
- [Complex transformations](07-complex-transformations.md) - Advanced patterns
- [Schema validation](04-schema-management.md) - Ensure quality
