---
name: md-generator
description: Generate markdown documents from structured data (JSON) or schema templates. Use when users want to create markdown from data, generate documents programmatically, create templates from schemas, or work with automated document generation.
allowed-tools: Bash(mddata:*), Read, Write
---

# Markdown Generator Skill

## Purpose

Generate markdown documents from structured data sources (JSON) or schema definitions. Enables automated document creation, template generation, and data-driven content workflows using the mddata tool.

## Prerequisites

- `mddata` command available (installed via `uv`)
- JSON data files in MarkdownDataDict format (for data generation)
- Schema files in JSON or YAML format (for template generation)

## Core Concepts

### Generation Modes

The mddata write command supports three modes:

1. **From Data** - Generate markdown from JSON data structure
2. **From Schema** - Generate template with placeholders from schema
3. **Combined** - Generate from data with schema validation

### MarkdownDataDict Format

JSON structure for markdown generation:

```json
{
  "frontmatter": {
    "property_name": "value",
    "number_property": 42,
    "array_property": ["item1", "item2"]
  },
  "content": {
    "sections": [
      {
        "id": "section_id",
        "title": "Section Title",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph|code_block|list|blockquote",
            "content": "Block content",
            "attributes": {}
          }
        ],
        "subsections": []
      }
    ]
  }
}
```

## Instructions

### 1. Generate from JSON Data

Create markdown from structured JSON data:

```bash
# From file
mddata write --data data.json --output document.md

# Short form
mddata write -d data.json -o document.md

# From stdin
cat data.json | mddata write --data - --output document.md
echo '{"frontmatter": {...}, "content": {...}}' | mddata write -d - -o doc.md

# Print to stdout (no output file)
mddata write --data data.json
```

### 2. Generate Template from Schema

Create a markdown template with placeholders:

```bash
# From JSON schema
mddata write --schema schema.json --output template.md

# From YAML schema
mddata write --schema schema.yaml --output template.md

# Short form
mddata write -s schema.json -o template.md

# Overwrite existing file
mddata write -s schema.json -o existing.md --force
```

**Generated templates include:**
- Frontmatter with default values and placeholders
- Required sections with `[Content required]` markers
- Optional sections with `[Optional content]` markers
- Proper heading hierarchy from schema structure

### 3. Generate with Validation

Combine data generation with schema validation:

```bash
# Generate and validate in one step
mddata write \
  --data data.json \
  --schema schema.json \
  --output validated-doc.md

# Short form
mddata write -d data.json -s schema.json -o doc.md
```

**Behavior:**
- Validates data against schema first
- Only generates if validation passes
- Shows detailed validation errors if fails
- Aborts generation on validation failure

### 4. Build Data Structure Programmatically

Create MarkdownDataDict JSON programmatically:

**Python Example:**
```python
import json

data = {
    "frontmatter": {
        "title": "Generated Document",
        "version": 1.0,
        "date": "2025-10-24"
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
                        "content": "This is an introduction."
                    }
                ],
                "subsections": []
            }
        ]
    }
}

# Output to stdout or file
print(json.dumps(data, indent=2))
```

**JavaScript Example:**
```javascript
const data = {
  frontmatter: {
    title: "Generated Doc",
    tags: ["auto", "generated"]
  },
  content: {
    sections: [
      {
        id: "main",
        title: "Main Section",
        level: 1,
        blocks: [
          {
            type: "paragraph",
            content: "Main content here."
          }
        ],
        subsections: []
      }
    ]
  }
};

console.log(JSON.stringify(data, null, 2));
```

### 5. Extract-Transform-Generate Workflow

Round-trip document transformation:

```bash
# 1. Extract existing document to JSON
mddata extract json original.md --output data.json --pretty

# 2. Transform data (using jq, scripts, etc.)
jq '.frontmatter.version = 2.0 | .frontmatter.status = "published"' \
  data.json > modified.json

# 3. Generate new document
mddata write -d modified.json -o updated.md

# 4. Optionally validate
mddata schema validate updated.md schema.json
```

## Block Types Reference

### Paragraph

```json
{
  "type": "paragraph",
  "content": "Text content with **markdown** formatting."
}
```

### Code Block

```json
{
  "type": "code_block",
  "content": "def hello():\n    print('Hello!')",
  "attributes": {"language": "python"}
}
```

### List (Unordered)

```json
{
  "type": "list",
  "content": "- Item 1\n- Item 2\n- Item 3",
  "attributes": {"ordered": false}
}
```

### List (Ordered)

```json
{
  "type": "list",
  "content": "1. First\n2. Second\n3. Third",
  "attributes": {"ordered": true}
}
```

### Blockquote

```json
{
  "type": "blockquote",
  "content": "This is a quote.\n\nMultiple paragraphs supported."
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
  "content": "<div class=\"alert\">\n  <p>Custom HTML</p>\n</div>"
}
```

## Usage Examples

### Example 1: Generate Blog Post from Data

```
User: "Create a blog post markdown from this JSON data"

1. Read or receive JSON data
2. Validate JSON structure
3. Generate document:
   mddata write -d blog-data.json -o blog-post.md
4. Display created document
5. Optionally show summary:
   mddata info summary blog-post.md
```

### Example 2: Create Template from Schema

```
User: "Generate a document template from our content schema"

1. Read schema file (JSON or YAML)
2. Generate template:
   mddata write -s content-schema.json -o template.md
3. Show template structure
4. Explain placeholders:
   - [Content required] - Must be filled
   - [Optional content] - Can be omitted
   - Default values - Pre-populated from schema
```

### Example 3: Automated Report Generation

```
User: "Generate monthly reports from this data"

1. Receive report data (JSON)
2. For each report:
   cat report-data.json | \
   mddata write -d - -o "report-$(date +%Y-%m).md"
3. Validate generated reports:
   mddata info summary report-*.md
```

### Example 4: API Documentation from Spec

```
User: "Generate API docs from OpenAPI spec"

1. Transform OpenAPI to MarkdownDataDict format
2. For each endpoint, create section:
   {
     "id": "endpoint_name",
     "title": "GET /api/users",
     "blocks": [
       {"type": "paragraph", "content": "Description"},
       {"type": "code_block", "content": "example", "attributes": {"language": "bash"}}
     ]
   }
3. Generate complete docs:
   mddata write -d api-docs.json -o API_REFERENCE.md
```

### Example 5: Validated Document Generation

```
User: "Create a document from data and ensure it's valid"

1. Read data and schema
2. Generate with validation:
   mddata write \
     -d content.json \
     -s content-schema.json \
     -o validated-doc.md
3. If validation fails:
   - Show detailed error messages
   - Explain what needs to be fixed
   - Reference schema requirements
4. If succeeds:
   - Confirm document created
   - Show summary
```

## Advanced Workflows

### Batch Document Generation

Generate multiple documents from data files:

```bash
# Process all data files
for data_file in data/*.json; do
  base=$(basename "$data_file" .json)
  mddata write -d "$data_file" -o "docs/$base.md"
done
```

### Pipeline Integration

Integrate with build systems:

```makefile
# Makefile example
docs/%.md: data/%.json schemas/doc.json
	mddata write -d $< -s schemas/doc.json -o $@ --force

all: docs/guide.md docs/api.md docs/tutorial.md
```

### Programmatic Generation

Generate documents from scripts:

```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime

# Build document data
doc_data = {
    "frontmatter": {
        "title": "Auto-Generated Report",
        "date": datetime.now().isoformat(),
        "generated": True
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
                        "content": "Report generated automatically."
                    }
                ],
                "subsections": []
            }
        ]
    }
}

# Generate markdown
proc = subprocess.run(
    ["mddata", "write", "-d", "-", "-o", "report.md"],
    input=json.dumps(doc_data),
    text=True,
    capture_output=True
)

if proc.returncode == 0:
    print("Document generated successfully")
else:
    print(f"Error: {proc.stderr}")
```

### Multi-Level Section Hierarchies

Create complex document structures:

```json
{
  "content": {
    "sections": [
      {
        "id": "guide",
        "title": "User Guide",
        "level": 1,
        "blocks": [
          {"type": "paragraph", "content": "Complete guide."}
        ],
        "subsections": [
          {
            "id": "basics",
            "title": "Basics",
            "level": 2,
            "blocks": [
              {"type": "paragraph", "content": "Basic concepts."}
            ],
            "subsections": [
              {
                "id": "concepts",
                "title": "Concepts",
                "level": 3,
                "blocks": [
                  {"type": "paragraph", "content": "Core concepts."}
                ],
                "subsections": []
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## Error Handling

### Missing Required Source

```
Error: At least one source is required (--data or --schema)

Solution: Provide --data or --schema parameter
```

### Invalid JSON Format

```
Error: Invalid JSON format in data file
  Line 5: Unexpected token

Solution: Validate JSON syntax using linter
```

### File Exists Without --force

```
Error: Output file 'document.md' already exists
Use --force to overwrite

Solution: Add --force flag or choose different output file
```

### Schema Validation Failure

```
✗ Validation failed:

Frontmatter errors:
  - Property 'title' is required but missing

Section errors:
  - Required section 'introduction' is missing

Generation aborted

Solution: Fix data to match schema requirements
```

### Invalid Data Structure

```
Error: Invalid MarkdownDataDict format
  Missing required key: 'content'

Solution: Ensure data has 'frontmatter' and 'content' keys
```

## Best Practices

### 1. Validate JSON Before Generation

```bash
# Check JSON syntax
cat data.json | jq . > /dev/null && echo "Valid JSON"

# Then generate
mddata write -d data.json -o doc.md
```

### 2. Use Schema Validation

Always validate when possible:

```bash
mddata write -d data.json -s schema.json -o doc.md
```

### 3. Version Control Generated Docs

Track changes in generated documents:

```bash
# Generate
mddata write -d data.json -o doc.md

# Review changes
git diff doc.md

# Commit if acceptable
git add doc.md
git commit -m "Regenerate documentation"
```

### 4. Automate Regeneration

Create scripts for reproducible generation:

```bash
#!/bin/bash
# regenerate-docs.sh

echo "Regenerating documentation..."

mddata write -d api-data.json -o docs/API.md --force
mddata write -d user-guide-data.json -o docs/GUIDE.md --force

echo "Documentation updated"
```

### 5. Template Organization

Keep schemas and templates organized:

```
project/
├── schemas/
│   ├── blog-post.json
│   ├── api-doc.json
│   └── guide.yaml
├── templates/  # Generated from schemas
│   ├── blog-post.md
│   ├── api-doc.md
│   └── guide.md
└── data/  # Data for generation
    ├── post-1.json
    ├── api-users.json
    └── user-guide.json
```

## Integration with Other Skills

### With md-template Skill

Templates can generate the JSON data:

```bash
# 1. Apply template to generate JSON
# (using custom template that outputs JSON)

# 2. Generate markdown from JSON
mddata write -d output.json -o document.md
```

### With md-schema Skill

Use schemas for validation:

```bash
# 1. Generate schema from existing docs
mddata schema infer docs/ -o schema.json

# 2. Generate new doc with validation
mddata write -d new-data.json -s schema.json -o new-doc.md
```

### With md-query Skill

Inspect generated documents:

```bash
# 1. Generate document
mddata write -d data.json -o doc.md

# 2. Verify result
mddata info summary doc.md --verbose
mddata info sections doc.md --paths
```

### With md-transformer Agent

For complex generation workflows:

```
User: "Generate 100 documents from this template with different data"

→ Use md-transformer agent for:
  - Batch data preparation
  - Parallel generation
  - Error handling
  - Validation workflows
  - Post-processing
```

## Reference Materials

### Manual References

- **Markdown Generation**: `manual/05-markdown-generation.md`
  - Complete generation reference
  - Block types and attributes
  - Data format specifications
  - Advanced examples

- **Complex Transformations**: `manual/07-complex-transformations.md`
  - Extract-Transform-Generate workflows
  - Pipeline integration
  - Scripted generation

- **Schema Management**: `manual/04-schema-management.md`
  - Schema structure
  - Validation rules
  - Template generation from schemas

### CLI Commands

Related mddata commands:
- `mddata write --data` - Generate from JSON
- `mddata write --schema` - Generate template
- `mddata extract json` - Extract to JSON
- `mddata schema validate` - Validate documents
- `mddata info` - Inspect documents

## When to Use This Skill

Use the md-generator skill when users:

1. **Want to generate markdown from data**
   - "Create markdown from this JSON"
   - "Generate docs from API spec"
   - "Build documents programmatically"

2. **Need template generation**
   - "Create a template from schema"
   - "Generate document skeleton"
   - "Build starter template"

3. **Want automated document creation**
   - "Auto-generate reports"
   - "Create docs in CI/CD"
   - "Batch generate documentation"

4. **Need validated generation**
   - "Generate and validate together"
   - "Ensure generated docs match schema"
   - "Create compliant documents"

5. **Ask about data format**
   - "What JSON format is needed?"
   - "How do I structure the data?"
   - "What blocks are available?"

## Limitations

- JSON data must follow MarkdownDataDict structure
- Schema must be valid JSON or YAML format
- Block types limited to supported markdown elements
- Validation requires compatible schema

## Output

When generating documents:

1. **Confirm generation** with file path
2. **Report success/failure** clearly
3. **Show validation errors** with details
4. **Suggest fixes** for common issues
5. **Display document summary** when helpful
6. **Reference manual** for data format

## Notes

- This skill is write-enabled (creates/overwrites files)
- Always respect --force flag requirement
- Validate JSON before generation when possible
- Use schema validation to ensure quality
- Reference manual for complete block type reference
- Coordinate with md-transformer agent for batch operations
