# Extracting Metadata

## Overview

The `mddata extract` command exports markdown documents to structured data formats (JSON or YAML). This is useful for:
- Integrating markdown content with other systems
- Data analysis and processing pipelines
- Backup and archival
- Content migration
- API responses

## Command Structure

```bash
mddata extract <format> <file_path> [options]
```

## Data Structure

Extracted data follows the `MarkdownDataDict` structure:

```python
{
    "frontmatter": {
        # All properties from YAML frontmatter
        "property_name": value,
        ...
    },
    "content": {
        "id": "",
        "title": "",
        "level": 0,
        "path": "",
        "blocks": [],
        "children": [
            {
                "id": "section_id",
                "title": "Section Title",
                "level": 1,
                "path": "section_id",
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": "Block content text",
                        "section_id": "section_id",
                        "metadata": {}
                    },
                    ...
                ],
                "children": [
                    # Nested sections with same structure
                ]
            },
            ...
        ]
    }
}
```

## Extract to JSON

### Basic JSON Export

```bash
mddata extract json document.md
```

**Output (compact):**
```json
{"frontmatter":{"title":"API Documentation","version":2.1,"status":"published","tags":["api","reference"]},"content":{"sections":[{"id":"introduction","title":"Introduction","level":1,"path":"introduction","blocks":[{"type":"paragraph","content":"Welcome to the API documentation.","section_id":"introduction","attributes":{}}],"children":[]}]}}
```

### Pretty-Printed JSON

```bash
mddata extract json document.md --pretty
```

**Output:**
```json
{
  "frontmatter": {
    "title": "API Documentation",
    "version": 2.1,
    "status": "published",
    "tags": [
      "api",
      "reference"
    ]
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "path": "introduction",
        "blocks": [
          {
            "type": "paragraph",
            "content": "Welcome to the API documentation.",
            "section_id": "introduction",
            "attributes": {}
          }
        ],
        "children": [
          {
            "id": "overview",
            "title": "Overview",
            "level": 2,
            "path": "introduction.overview",
            "blocks": [
              {
                "type": "paragraph",
                "content": "The API provides RESTful endpoints.",
                "section_id": "introduction.overview",
                "attributes": {}
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

### Save to File

```bash
mddata extract json document.md --output data.json
```

```bash
# With pretty formatting
mddata extract json document.md --pretty --output data.json
```

## Extract to YAML

### Basic YAML Export

```bash
mddata extract yaml document.md
```

**Output:**
```yaml
frontmatter:
  title: API Documentation
  version: 2.1
  status: published
  tags:
    - api
    - reference
content:
  sections:
    - id: introduction
      title: Introduction
      level: 1
      path: introduction
      blocks:
        - type: paragraph
          content: Welcome to the API documentation.
          section_id: introduction
          attributes: {}
      subsections:
        - id: overview
          title: Overview
          level: 2
          path: introduction.overview
          blocks:
            - type: paragraph
              content: The API provides RESTful endpoints.
              section_id: introduction.overview
              attributes: {}
          subsections: []
```

### Save to File

```bash
mddata extract yaml document.md --output data.yaml
```

**Note:** YAML format is always pretty-printed for readability.

## Extract Frontmatter Only

Extract only the frontmatter properties:

### JSON Format

```bash
mddata extract frontmatter document.md
mddata extract frontmatter document.md --format json
```

**Output:**
```json
{
  "title": "API Documentation",
  "version": 2.1,
  "status": "published",
  "tags": ["api", "reference"]
}
```

### YAML Format

```bash
mddata extract frontmatter document.md --format yaml
```

**Output:**
```yaml
title: API Documentation
version: 2.1
status: published
tags:
  - api
  - reference
```

### Save to File

```bash
mddata extract frontmatter document.md --output metadata.json
mddata extract frontmatter document.md --format yaml --output metadata.yaml
```

## Understanding the Data Structure

### Frontmatter Section

Contains all properties exactly as defined in the document:

```json
{
  "frontmatter": {
    "title": "string value",
    "version": 1.0,
    "published": true,
    "tags": ["array", "of", "strings"],
    "author": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Property types preserved:**
- Strings: `"text"`
- Numbers: `42`, `3.14`
- Booleans: `true`, `false`
- Arrays: `["item1", "item2"]`
- Objects: `{"key": "value"}`
- Null: `null`

### Content Section

Hierarchical structure of sections and blocks:

```json
{
  "content": {
    "sections": [
      {
        "id": "section_id",        // Slugified section identifier
        "title": "Section Title",   // Original heading text
        "level": 1,                 // Heading level (1-6)
        "path": "section_id",       // Full path from root
        "blocks": [...],            // Content blocks
        "children": [...]        // Nested sections
      }
    ]
  }
}
```

### Block Structure

Each block contains:

```json
{
  "type": "paragraph",              // Block type
  "content": "Block content text",  // Actual content
  "section_id": "section_id",       // Parent section
  "attributes": {                   // Type-specific attributes
    "language": "python",           // For code blocks
    "ordered": true,                // For lists
    ...
  }
}
```

**Common block types:**
- `paragraph` - Text content
- `heading` - Section headers
- `list` - Ordered/unordered lists
- `code_block` - Code examples
- `blockquote` - Quoted text
- `thematic_break` - Horizontal rules
- `html_block` - Raw HTML

## Practical Examples

### Example 1: Extract for API Response

```bash
# Extract entire document as JSON
mddata extract json api-docs.md --pretty --output api-response.json

# Use in REST API
cat api-response.json | jq '.frontmatter.title'
# Output: "API Documentation"
```

### Example 2: Extract Metadata for Processing

```bash
# Extract frontmatter only
mddata extract frontmatter document.md --output metadata.json

# Process with jq
cat metadata.json | jq '.tags[]'
# Output:
# "api"
# "reference"
```

### Example 3: Convert to YAML for Configuration

```bash
# Extract as YAML
mddata extract yaml config.md --output config.yaml

# Use as application config
cat config.yaml
```

### Example 4: Batch Processing

```bash
# Extract multiple documents
for file in docs/*.md; do
  basename="${file%.md}"
  mddata extract json "$file" --pretty --output "data/${basename}.json"
done
```

### Example 5: Pipeline Integration

```bash
# Extract and transform with jq
mddata extract json document.md | jq '.content.children[0].blocks[] | select(.type == "code_block")'

# Extract and filter
mddata extract yaml document.md | yq '.frontmatter | select(.status == "published")'
```

## Working with Extracted Data

### Query with jq (JSON)

```bash
# Get all section titles
mddata extract json doc.md | jq '.content.children[].title'

# Get all code blocks
mddata extract json doc.md | jq '.content.children[].blocks[] | select(.type == "code_block")'

# Count paragraphs
mddata extract json doc.md | jq '[.content.children[].blocks[] | select(.type == "paragraph")] | length'

# Get nested subsection
mddata extract json doc.md | jq '.content.children[0].children[0].title'
```

### Query with yq (YAML)

```bash
# Get title
mddata extract yaml doc.md | yq '.frontmatter.title'

# Get all tags
mddata extract yaml doc.md | yq '.frontmatter.tags[]'

# Filter sections by level
mddata extract yaml doc.md | yq '.content.children[] | select(.level == 1) | .title'
```

### Python Processing

```python
import json

# Load extracted data
with open('data.json') as f:
    data = json.load(f)

# Access frontmatter
title = data['frontmatter']['title']
version = data['frontmatter']['version']

# Access sections
for section in data['content']['children']:
    print(f"Section: {section['title']}")
    print(f"  Blocks: {len(section['blocks'])}")
    print(f"  Subsections: {len(section['subsections'])}")
```

### JavaScript Processing

```javascript
const fs = require('fs');

// Load extracted data
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// Access frontmatter
const { title, version, tags } = data.frontmatter;

// Find code blocks
const codeBlocks = data.content.children
  .flatMap(s => s.blocks)
  .filter(b => b.type === 'code_block');

console.log(`Found ${codeBlocks.length} code blocks`);
```

## Output Options Summary

| Command | Format | Compact | Pretty | File Output |
|---------|--------|---------|--------|-------------|
| `extract json` | JSON | ✓ | | stdout |
| `extract json --pretty` | JSON | | ✓ | stdout |
| `extract json -o file.json` | JSON | ✓ | | file.json |
| `extract json --pretty -o file.json` | JSON | | ✓ | file.json |
| `extract yaml` | YAML | | ✓ | stdout |
| `extract yaml -o file.yaml` | YAML | | ✓ | file.yaml |
| `extract frontmatter` | JSON | | ✓ | stdout |
| `extract frontmatter --format yaml` | YAML | | ✓ | stdout |
| `extract frontmatter -o file.json` | JSON | | ✓ | file.json |

## Common Use Cases

### 1. Documentation Pipeline

```bash
# Extract docs for static site generator
for doc in docs/*.md; do
  mddata extract json "$doc" --pretty --output "build/$(basename ${doc%.md}).json"
done
```

### 2. Content Management System

```bash
# Extract metadata for CMS indexing
mddata extract frontmatter articles/*.md --format json
```

### 3. Data Analysis

```bash
# Extract all documents for analysis
find . -name "*.md" -exec mddata extract json {} \; > all_docs.jsonl
```

### 4. Migration

```bash
# Convert markdown to structured format for migration
mddata extract yaml old_docs.md --output new_system_format.yaml
```

### 5. API Integration

```bash
# Prepare data for REST API
mddata extract json content.md --pretty | curl -X POST -H "Content-Type: application/json" -d @- https://api.example.com/content
```

## Next Steps

- [Validate against schemas](04-schema-management.md) - Ensure data quality
- [Generate markdown from data](05-markdown-generation.md) - Reverse operation
- [Modify extracted data](06-data-transformation.md) - Transform and re-import
