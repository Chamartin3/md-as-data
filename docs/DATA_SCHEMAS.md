# Data Schemas Reference

This document describes the three core data structures used in mddata operations.

## Overview of Data Structures

The mddata system uses three distinct data structures, each serving a specific purpose:

| Schema Name | Type Name | Purpose | Format Support | Used By |
|------------|-----------|---------|----------------|---------|
| **Document Schema** | `DocumentSchema` | Defines validation rules and structure requirements for markdown documents | JSON, YAML | `schema generate`, `schema validate`, `schema info`, `generate --schema` |
| **Markdown Data** | `MarkdownDataDict` | Complete document structure including frontmatter and hierarchical content | **JSON only** | `extract`, `generate --data`, `modify from-json` |
| **Update Data** | `UpdateDataDict` | Incremental changes to apply to existing documents | **JSON only** | `modify from-json` |

### Key Differences

- **Document Schema**: Describes *what a document should look like* (validation rules, required fields, allowed types)
- **Markdown Data**: Contains *actual document content* (the data itself - frontmatter values, section text, structure)
- **Update Data**: Specifies *changes to make* (partial updates, section modifications with policies)

### Format Support Summary

- **Full JSON/YAML support**: Document Schema (all schema operations)
- **JSON only**: Markdown Data and Update Data (all data operations)
- **Both formats**: Extract operations can output in either JSON or YAML

---

## Document Schema (Validation)

**Type Name**: `DocumentSchema`

Defines validation rules for markdown documents. Can also be used to generate document templates. This is the result of the `mddata schema generate` command.

### CLI Usage

**Template Generation Commands:**
```bash
# Generate template document from schema
mddata generate --schema schema.yaml --output template.md
mddata generate -s schema.json -o template.md
```

**Schema Generation Commands:**
```bash
# Generate schema from a single document
mddata schema generate document.md --output schema.yaml
mddata schema generate document.md --format json --output schema.json

# Generate schema from multiple documents (folder)
mddata schema generate ./docs/ --output merged-schema.yaml --pretty
```

**Validation Commands:**
```bash
# Validate document against schema
mddata schema validate document.md schema.yaml
mddata schema validate document.md schema.json --verbose

# Schema is passed as a file path argument
# Format is auto-detected from extension (.yaml, .yml, .json)
```

**Info Commands:**
```bash
# Display schema information
mddata schema info schema.yaml
mddata schema info schema.json
```

### Structure

```yaml
frontmatter:
  # Property name as key
  title:
    type: "str"  # "str" | "int" | "float" | "bool" | "list" | "dict"
    required: true
    validations:
      - type: "min_length"
        value: 1
        message: "Title cannot be empty"

  status:
    type: "str"
    required: false
    default: "draft"
    enum: ["draft", "published", "archived"]

  tags:
    type: "list"
    required: false

  version:
    type: "str|int"  # Union type (accepts multiple types)
    required: false

sections:
  introduction:
    validation:
      required: true
      min_blocks: 1
      max_blocks: 10
      allowed_content: ["paragraph", "code_block"]

  conclusion:
    validation:
      required: false

validation_level: "strict"  # "strict" | "warnings" | "disabled"
```

### Field Descriptions

**Frontmatter Property Validation:**
- `type`: Expected data type(s) - use `|` for union types
- `required`: Whether property must exist
- `default`: Default value if not provided
- `enum`: List of allowed values
- `validations`: Additional validation rules

**Section Validation:**
- `required`: Whether section must exist
- `min_blocks`: Minimum number of content blocks
- `max_blocks`: Maximum number of content blocks
- `allowed_content`: List of permitted block types

**Validation Levels:**
- `"strict"`: Raise errors on validation failures
- `"warnings"`: Collect warnings without failing
- `"disabled"`: Skip validation entirely

### Example (JSON format)

```json
{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true
    },
    "priority": {
      "type": "int",
      "required": false,
      "enum": [1, 2, 3, 4, 5]
    }
  },
  "sections": {
    "summary": {
      "validation": {
        "required": true,
        "min_blocks": 1
      }
    }
  },
  "validation_level": "warnings"
}
```
## Markdown Data

**Type Name**: `MarkdownDataDict`

Complete document structure used for generation operations and as the result of extraction. Contains actual document content including frontmatter and hierarchical sections.

### CLI Usage

**Extraction Commands:**
```bash
# Extract complete document structure to JSON
mddata extract json document.md --output data.json
mddata extract json document.md --pretty

# Extract to YAML format
mddata extract yaml document.md --output data.yaml

# Extract to stdout
mddata extract json document.md
```

**Generation Commands:**
```bash
# Generate markdown from MarkdownData JSON file (JSON only)
mddata generate --data data.json --output new-document.md

# Generate from stdin (JSON only)
cat data.json | mddata generate --data - --output document.md
echo '{"frontmatter": {...}, "content": {...}}' | mddata generate --data -

# Generate template from schema (supports both JSON and YAML)
mddata generate --schema schema.json --output template.md
mddata generate --schema schema.yaml --output template.md

# Generate from data and validate against schema
mddata generate --data data.json --schema schema.yaml --output document.md
```

### Structure

**Note:** Examples below show the structure in YAML format for readability, but Markdown Data operations only accept JSON format.

```yaml
frontmatter:
  # Document metadata (key-value pairs)
  title: "Document Title"
  author: "Author Name"
  tags: ["tag1", "tag2"]
  date: "2025-01-15"
  custom_field: "any value"

content:
  # Top-level sections (no parent)
  sections:
    - id: "introduction"
      title: "Introduction"
      level: 1
      path: "introduction"
      blocks:
        - type: "paragraph"
          content: "Introduction paragraph text."
        - type: "code_block"
          content: "code example"
          language: "python"

      # Nested subsections
      subsections:
        - id: "overview"
          title: "Overview"
          level: 2
          path: "introduction.overview"
          blocks:
            - type: "paragraph"
              content: "Overview paragraph."
          subsections: []

    - id: "conclusion"
      title: "Conclusion"
      level: 1
      path: "conclusion"
      blocks:
        - type: "paragraph"
          content: "Concluding remarks."
      subsections: []
```

### Field Descriptions

**Frontmatter:**
- Any valid YAML/JSON key-value pairs
- Values can be strings, numbers, lists, or nested objects
- All properties are optional unless schema validation is enabled

**Content Sections:**
- `id`: Unique section identifier (used for path navigation)
- `title`: Display title for the section heading
- `level`: Heading level (1-6, where 1 is `#`, 2 is `##`, etc.)
- `path`: Dot-separated hierarchical path (e.g., `"parent.child"`)
- `blocks`: List of content blocks within the section
- `subsections`: Nested child sections (recursive structure)

**Content Blocks:**
- `type`: Block type - `"paragraph"`, `"code_block"`, `"list"`, `"blockquote"`, `"heading"`, etc.
- `content`: Text content of the block
- `language`: (code blocks only) Programming language identifier

### Example (JSON format)

```json
{
  "frontmatter": {
    "title": "API Documentation",
    "version": "1.0.0",
    "status": "published"
  },
  "content": {
    "sections": [
      {
        "id": "getting_started",
        "title": "Getting Started",
        "level": 1,
        "path": "getting_started",
        "blocks": [
          {
            "type": "paragraph",
            "content": "Quick start guide."
          }
        ],
        "subsections": []
      }
    ]
  }
}
```

## Update Data

**Type Name**: `UpdateDataDict`

Incremental update structure for the `modify from-json` command. Specifies partial changes to apply to existing documents without requiring the full document structure.

### CLI Usage

**Modify from File:**
```bash
# Apply updates from a JSON file
mddata modify from-json document.md updates.json

# Preview changes without modifying (dry run)
mddata modify from-json document.md updates.json --dry-run
```

**Modify from Stdin:**
```bash
# Pipe JSON updates from stdin
echo '{"frontmatter": {"title": "New"}}' | mddata modify from-json document.md -

# Inline JSON updates with heredoc
mddata modify from-json document.md - <<EOF
{
  "frontmatter": {
    "status": "published",
    "version": "2.0"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "Updated content",
      "policy": "replace"
    }
  ]
}
EOF
```

### Structure

**Note:** The `modify from-json` command only accepts JSON format. For human-readable examples, the structure is shown in YAML below, but you must convert it to JSON when using the command.

```yaml
# Optional: Update frontmatter properties
frontmatter:
  title: "Updated Title"
  new_property: "new value"
  # Set to null to remove a property
  removed_property: null

# Optional: Update sections
sections:
  - id: "introduction"
    content: "New introduction content"
    policy: "update"  # "update" | "replace" | "append"

  - id: "introduction.overview"
    content: "New subsection content"
    policy: "replace"

  # Create new section
  - id: "new_section"
    content: "Brand new section content"
    # Policy defaults to "update"
```

### Field Descriptions

**Frontmatter Updates:**
- Specify only properties to add or modify
- Set property to `null` to remove it
- Unspecified properties remain unchanged

**Section Updates:**
- `id`: Section path (existing or new)
- `content`: New content text (without heading)
- `policy`: How to merge content
  - `"update"`: Merge content, preserve subsections (default)
  - `"replace"`: Replace entire section content
  - `"append"`: Add content to existing section

### Example (JSON format)

```json
{
  "frontmatter": {
    "version": "2.0.0",
    "last_updated": "2025-01-20",
    "draft": null
  },
  "sections": [
    {
      "id": "introduction",
      "content": "Completely new introduction.",
      "policy": "replace"
    },
    {
      "id": "changelog.v2",
      "content": "Version 2.0 changes."
    }
  ]
}
```


## Format Support

### Schema Operations (Full Format Support)

Schema operations support both YAML and JSON formats with automatic detection:

```bash
# Generate schema in YAML or JSON format
mddata schema generate document.md --format yaml
mddata schema generate document.md --format json

# Validate with YAML or JSON schema (auto-detected)
mddata schema validate document.md schema.yaml
mddata schema validate document.md schema.json

# Info command works with both formats
mddata schema info schema.yaml
mddata schema info schema.json
```

Format is automatically detected based on file extension (`.yaml`, `.yml`, `.json`).

### Data Operations (JSON Only)

Data modification and generation operations only support JSON format:

```bash
# Extract operations support both formats
mddata extract json document.md
mddata extract yaml document.md

# Modify operations require JSON format
mddata modify from-json document.md updates.json

# Generate with --data requires JSON format
mddata generate --data data.json --output document.md

# Generate with --schema supports both formats
mddata generate --schema schema.yaml --output template.md
```
