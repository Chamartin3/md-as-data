# Markdown Data Format

This guide explains the JSON/YAML data format for representing markdown documents. This format is used when you want to create markdown files programmatically or extract existing markdown documents into structured data.

## Use Cases

Use the Markdown Data format when you need to:

- **Generate markdown files** from structured data (databases, APIs, other systems)
- **Extract markdown content** to JSON/YAML for processing or analysis
- **Transform documents** by extracting, modifying data, and regenerating
- **Integrate with tools** that work with JSON/YAML data
- **Apply batch modifications** to existing documents
- **Version control data** separately from presentation

### CLI Commands

The Markdown Data format is used by these commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `mddata generate --data` | Create markdown from data | `mddata generate --data doc.json --output doc.md` |
| `mddata extract json` | Extract markdown to JSON | `mddata extract json doc.md --output data.json` |
| `mddata extract yaml` | Extract markdown to YAML | `mddata extract yaml doc.md --output data.yaml` |
| `mddata write from -d` | Apply batch changes | `mddata write from -d doc.md changes.json` |

---

## Structure Overview

Markdown data consists of two main parts:

```
Markdown Data
├── frontmatter     → Document metadata (YAML properties)
└── content         → Document structure (sections and blocks)
    ├── root section (level 0)
    └── children sections
        ├── blocks (content)
        └── children sections (recursive)
```

**Minimal structure:**

```json
{
  "frontmatter": {},
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": []
  }
}
```

---

## Complete Structure Reference

### Document Root

```json
{
  "frontmatter": { /* metadata properties */ },
  "content": { /* document structure */ }
}
```

**Two required fields:**
- `frontmatter` - Document metadata (object)
- `content` - Document content structure (section object)

---

## Frontmatter

Document metadata stored as YAML frontmatter. Contains any key-value pairs you need.

**Supported value types:**

| Type | Example | Description |
|------|---------|-------------|
| String | `"value"` | Text content |
| Number | `42`, `3.14` | Integer or decimal |
| Boolean | `true`, `false` | True/false values |
| List | `["item1", "item2"]` | Array of values |
| Object | `{"key": "value"}` | Nested structure |
| Null | `null` | Empty value |

### Example

```json
{
  "frontmatter": {
    "title": "Getting Started Guide",
    "author": "Jane Developer",
    "date": "2025-10-21",
    "version": 1.0,
    "tags": ["tutorial", "beginner", "guide"],
    "published": true,
    "draft": false,
    "metadata": {
      "category": "Documentation",
      "difficulty": "beginner",
      "estimated_time": "30 minutes"
    },
    "contributors": ["Alice", "Bob"],
    "last_updated": null
  }
}
```

### YAML Format

```yaml
frontmatter:
  title: "Getting Started Guide"
  author: "Jane Developer"
  date: "2025-10-21"
  version: 1.0
  tags:
    - tutorial
    - beginner
    - guide
  published: true
  metadata:
    category: "Documentation"
    difficulty: "beginner"
```

---

## Content Structure

The `content` field contains the document's hierarchical structure with sections and blocks.

### Root Section

Every document has exactly one root section at level 0:

```json
{
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [
      // Top-level sections go here
    ]
  }
}
```

**Root section properties:**
- `id` - Always empty string `""`
- `title` - Always empty string `""`
- `level` - Always `0`
- `path` - Always empty string `""`
- `blocks` - Usually empty array `[]` (content goes in child sections)
- `children` - Array of section objects

---

## Sections

Sections represent markdown headings and their content. Each section can contain blocks and child sections.

### Section Object

```json
{
  "id": "section_identifier",
  "title": "Section Title",
  "level": 2,
  "path": "parent.section_identifier",
  "blocks": [ /* content blocks */ ],
  "children": [ /* nested sections */ ]
}
```

### Section Fields

#### `id` (string, required)

Section identifier used for referencing. Generated from title:
- Lowercase
- Spaces replaced with underscores
- Special characters removed

**Examples:**
- `"Introduction"` → `"introduction"`
- `"Getting Started"` → `"getting_started"`
- `"API Reference"` → `"api_reference"`

#### `title` (string, required)

Human-readable section heading exactly as it appears in markdown.

**Examples:**
- `"Introduction"`
- `"Getting Started"`
- `"API Reference"`

#### `level` (number, required)

Heading level corresponding to markdown heading depth:

| Level | Markdown | Usage |
|-------|----------|-------|
| `0` | (none) | Root section only |
| `1` | `#` | Document title (H1) |
| `2` | `##` | Main sections (H2) |
| `3` | `###` | Subsections (H3) |
| `4` | `####` | Sub-subsections (H4) |
| `5` | `#####` | Deep nesting (H5) |
| `6` | `######` | Deepest level (H6) |

#### `path` (string, required)

Dot-separated path showing section hierarchy:

**Examples:**
- Top-level section: `"introduction"`
- Nested section: `"getting_started.installation"`
- Deep nesting: `"guide.advanced.performance.optimization"`

**Rules:**
- Root section path is always `""`
- Top-level sections use just their ID: `"section_id"`
- Nested sections join parent path with ID: `"parent.child"`

#### `blocks` (array, required)

List of content blocks in this section. Can be empty array `[]`.

#### `children` (array, required)

List of nested section objects. Can be empty array `[]`.

### Section Examples

**Simple section (no nesting):**

```json
{
  "id": "introduction",
  "title": "Introduction",
  "level": 2,
  "path": "introduction",
  "blocks": [
    {
      "section_id": "introduction",
      "type": "paragraph",
      "content": "Welcome to this guide.",
      "metadata": {}
    }
  ],
  "children": []
}
```

**Section with subsections:**

```json
{
  "id": "getting_started",
  "title": "Getting Started",
  "level": 2,
  "path": "getting_started",
  "blocks": [],
  "children": [
    {
      "id": "prerequisites",
      "title": "Prerequisites",
      "level": 3,
      "path": "getting_started.prerequisites",
      "blocks": [
        {
          "section_id": "prerequisites",
          "type": "list",
          "content": ["Python 3.11+", "Basic CLI knowledge"],
          "metadata": {}
        }
      ],
      "children": []
    },
    {
      "id": "installation",
      "title": "Installation",
      "level": 3,
      "path": "getting_started.installation",
      "blocks": [
        {
          "section_id": "installation",
          "type": "code_block",
          "content": "pip install mddata",
          "metadata": {"language": "bash"}
        }
      ],
      "children": []
    }
  ]
}
```

---

## Blocks

Blocks represent different types of content within sections.

### Block Object

```json
{
  "section_id": "section_identifier",
  "type": "block_type",
  "content": "content here",
  "metadata": {}
}
```

### Block Fields

#### `section_id` (string, required)

ID of the section containing this block. Must match the parent section's `id` field.

#### `type` (string, required)

Block type identifier. See [Block Types](#block-types) for all supported types.

#### `content` (string or array, required)

Block content. Format depends on block type:
- **Single string**: Paragraphs, code blocks, blockquotes
- **Array of strings**: Lists, task lists

#### `metadata` (object, required)

Additional block-specific data. Can be empty object `{}`. See [Block Types](#block-types) for type-specific metadata.

---

## Block Types

### Paragraph

Plain text content.

```json
{
  "section_id": "intro",
  "type": "paragraph",
  "content": "This is a paragraph of text. It can span multiple sentences.",
  "metadata": {}
}
```

**Markdown output:**
```markdown
This is a paragraph of text. It can span multiple sentences.
```

### Code Block

Fenced code block with optional language specification.

```json
{
  "section_id": "examples",
  "type": "code_block",
  "content": "def hello():\n    print('Hello, world!')",
  "metadata": {
    "language": "python"
  }
}
```

**Markdown output:**
````markdown
```python
def hello():
    print('Hello, world!')
```
````

**Metadata fields:**
- `language` (string, optional) - Syntax highlighting language

### Unordered List

Bullet point list.

```json
{
  "section_id": "features",
  "type": "list",
  "content": [
    "First feature",
    "Second feature",
    "Third feature"
  ],
  "metadata": {}
}
```

**Markdown output:**
```markdown
- First feature
- Second feature
- Third feature
```

### Ordered List

Numbered list.

```json
{
  "section_id": "steps",
  "type": "ordered_list",
  "content": [
    "First step",
    "Second step",
    "Third step"
  ],
  "metadata": {}
}
```

**Markdown output:**
```markdown
1. First step
2. Second step
3. Third step
```

### Task List

Checklist with completion status.

```json
{
  "section_id": "todos",
  "type": "task_list",
  "content": [
    "Complete documentation",
    "Review code",
    "Deploy to production"
  ],
  "metadata": {
    "tasks": [
      {"content": "Complete documentation", "symbol": "x"},
      {"content": "Review code", "symbol": " "},
      {"content": "Deploy to production", "symbol": " "}
    ]
  }
}
```

**Markdown output:**
```markdown
- [x] Complete documentation
- [ ] Review code
- [ ] Deploy to production
```

**Metadata fields:**
- `tasks` (array, required) - Array of task objects:
  - `content` (string) - Task text
  - `symbol` (string) - Checkbox character:
    - `"x"` - Completed
    - `" "` - Incomplete
    - `"!"` - High priority
    - `"~"` - In progress
    - `"?"` - Uncertain

### Blockquote

Quoted text.

```json
{
  "section_id": "quotes",
  "type": "blockquote",
  "content": "This is a quoted passage.\nIt can span multiple lines.",
  "metadata": {}
}
```

**Markdown output:**
```markdown
> This is a quoted passage.
> It can span multiple lines.
```

### Other Block Types

The following block types are supported but less commonly used:

**Link** (`"link"`):
```json
{
  "section_id": "resources",
  "type": "link",
  "content": "Click here",
  "metadata": {
    "href": "https://example.com",
    "title": "Example site"
  }
}
```

**Image** (`"image"`):
```json
{
  "section_id": "screenshots",
  "type": "image",
  "content": "Screenshot description",
  "metadata": {
    "src": "images/screenshot.png",
    "alt": "Application screenshot"
  }
}
```

**Table** (`"table"`):
```json
{
  "section_id": "data",
  "type": "table",
  "content": "Table content (format varies)",
  "metadata": {}
}
```

---

## Complete Examples

### Simple Document

```json
{
  "frontmatter": {
    "title": "Quick Note",
    "date": "2025-10-21"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [
      {
        "id": "note",
        "title": "Note",
        "level": 2,
        "path": "note",
        "blocks": [
          {
            "section_id": "note",
            "type": "paragraph",
            "content": "This is a quick note.",
            "metadata": {}
          }
        ],
        "children": []
      }
    ]
  }
}
```

### Multi-Section Document

```json
{
  "frontmatter": {
    "title": "Project Setup Guide",
    "author": "Development Team",
    "date": "2025-10-21",
    "tags": ["guide", "setup"]
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [
      {
        "id": "overview",
        "title": "Overview",
        "level": 2,
        "path": "overview",
        "blocks": [
          {
            "section_id": "overview",
            "type": "paragraph",
            "content": "This guide covers project setup and configuration.",
            "metadata": {}
          }
        ],
        "children": []
      },
      {
        "id": "installation",
        "title": "Installation",
        "level": 2,
        "path": "installation",
        "blocks": [
          {
            "section_id": "installation",
            "type": "paragraph",
            "content": "Follow these steps to install:",
            "metadata": {}
          },
          {
            "section_id": "installation",
            "type": "ordered_list",
            "content": [
              "Clone the repository",
              "Install dependencies",
              "Configure environment"
            ],
            "metadata": {}
          }
        ],
        "children": [
          {
            "id": "dependencies",
            "title": "Dependencies",
            "level": 3,
            "path": "installation.dependencies",
            "blocks": [
              {
                "section_id": "dependencies",
                "type": "code_block",
                "content": "npm install",
                "metadata": {"language": "bash"}
              }
            ],
            "children": []
          }
        ]
      },
      {
        "id": "configuration",
        "title": "Configuration",
        "level": 2,
        "path": "configuration",
        "blocks": [
          {
            "section_id": "configuration",
            "type": "paragraph",
            "content": "Set up your configuration file:",
            "metadata": {}
          },
          {
            "section_id": "configuration",
            "type": "code_block",
            "content": "{\n  \"port\": 3000,\n  \"debug\": true\n}",
            "metadata": {"language": "json"}
          }
        ],
        "children": []
      }
    ]
  }
}
```

---

## Update Data Format

For batch modifications to existing documents, use a simplified format with update policies.

### Structure

```json
{
  "frontmatter": {
    "property": "new_value"
  },
  "frontmatter_policy": "merge",
  "sections": [
    {
      "id": "section_id",
      "content": "New content as markdown text",
      "policy": "update"
    }
  ]
}
```

### Frontmatter Policy

Controls how frontmatter properties are merged:

| Policy | Behavior |
|--------|----------|
| `"merge"` | Merge new properties with existing (default) |
| `"replace"` | Replace all frontmatter completely |

### Section Updates

Each section update specifies:

**Fields:**
- `id` (string, required) - Section identifier or path
- `content` (string, required) - New content as markdown text
- `policy` (string, optional) - Update policy (default: `"update"`)

**Section Policies:**

| Policy | Behavior |
|--------|----------|
| `"update"` | Merge content, preserve subsections (default) |
| `"replace"` | Replace entire section including subsections |
| `"append"` | Add content to end of section |

### Update Examples

**Update properties:**
```json
{
  "frontmatter": {
    "status": "published",
    "version": "2.0",
    "last_updated": "2025-10-21"
  },
  "frontmatter_policy": "merge"
}
```

**Replace section:**
```json
{
  "sections": [
    {
      "id": "introduction",
      "content": "## Introduction\n\nCompletely new introduction text.",
      "policy": "replace"
    }
  ]
}
```

**Append to section:**
```json
{
  "sections": [
    {
      "id": "changelog",
      "content": "\n### Version 2.0\n\n- New features\n- Bug fixes",
      "policy": "append"
    }
  ]
}
```

**Update nested section:**
```json
{
  "sections": [
    {
      "id": "getting_started.installation",
      "content": "## Installation\n\nUpdated installation steps:\n\n```bash\npip install mddata\n```",
      "policy": "update"
    }
  ]
}
```

---

## CLI Usage Examples

### Generate Markdown

```bash
# From JSON data
mddata generate --data document.json --output output.md

# From YAML data
mddata generate --data document.yaml --output output.md

# From stdin
cat document.json | mddata generate --data - --output output.md

# Print to stdout (no file)
mddata generate --data document.json
```

### Extract to Data

```bash
# Extract to JSON
mddata extract json document.md --output data.json

# Extract to YAML
mddata extract yaml document.md --output data.yaml

# Pretty formatting
mddata extract json document.md --pretty --output data.json

# Print to stdout
mddata extract json document.md
```

### Apply Updates

```bash
# Apply updates from file
mddata write from -d document.md updates.json

# Apply from stdin
cat updates.json | mddata write from -d document.md -

# Preview changes (dry run)
mddata write from -d document.md updates.json --dry-run
```

---

## Common Workflows

### Round-Trip Conversion

Extract, modify, and regenerate:

```bash
# 1. Extract to data
mddata extract json original.md --output data.json

# 2. Modify data.json (edit manually or programmatically)

# 3. Generate new document
mddata generate --data data.json --output modified.md
```

### Batch Updates

Apply multiple changes at once:

```bash
# Create updates file
cat > updates.json << 'EOF'
{
  "frontmatter": {
    "updated": "2025-10-21",
    "reviewed": true
  },
  "sections": [
    {
      "id": "changelog",
      "content": "\n- Updated on 2025-10-21",
      "policy": "append"
    }
  ]
}
EOF

# Apply updates
mddata write from -d document.md updates.json
```

### Data Integration

Use with external tools:

```bash
# Extract for processing
mddata extract json doc.md | jq '.frontmatter.tags' > tags.json

# Generate from API response
curl https://api.example.com/content | \
  jq '{frontmatter: .meta, content: .body}' | \
  mddata generate --data - --output generated.md

# Convert between formats
mddata extract yaml doc.md | yq -o json > data.json
```

---

## YAML Format

All examples work in YAML format:

```yaml
frontmatter:
  title: "Quick Note"
  date: "2025-10-21"

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: note
      title: Note
      level: 2
      path: note
      blocks:
        - section_id: note
          type: paragraph
          content: "This is a quick note."
          metadata: {}
      children: []
```

**YAML Benefits:**
- More readable for humans
- Supports comments
- Less verbose (no quotes needed for most strings)
- Better for manual editing

**JSON Benefits:**
- More compact
- Standard web format
- Better for programmatic use
- Widely supported by tools

Both formats are fully interchangeable.

---

## Tips and Best Practices

### Section Organization

1. **Use descriptive IDs**: Clear, meaningful section identifiers
   - Good: `"getting_started"`, `"api_reference"`
   - Bad: `"section1"`, `"s1"`

2. **Keep paths accurate**: Child paths must include parent
   - Correct: `"parent.child"`, `"guide.setup.install"`
   - Incorrect: `"child"` (when it has a parent)

3. **Match section IDs**: Block `section_id` must match parent section `id`

### Content Guidelines

1. **Use appropriate block types**: Choose the right type for your content
   - Use `"code_block"` for code, not `"paragraph"`
   - Use `"ordered_list"` when order matters

2. **Include metadata**: Always include metadata object, even if empty `{}`

3. **Preserve formatting**: Use `\n` for line breaks in strings

### Data Validation

Before using data files:

```bash
# Validate JSON syntax
cat data.json | jq empty

# Validate YAML syntax
cat data.yaml | yq empty

# Pretty-format JSON
cat data.json | jq '.' > formatted.json

# Convert YAML to JSON
yq -o json data.yaml > data.json
```

---

## Troubleshooting

### Common Issues

**"Invalid JSON format"**
- Validate with `jq`: `cat file.json | jq empty`
- Check for trailing commas (not allowed in JSON)
- Verify all quotes are properly closed

**"Section path mismatch"**
- Ensure child section `path` includes parent path
- Example: If parent is `"guide"`, child should be `"guide.setup"`, not `"setup"`

**"Missing required fields"**
- All sections must have: `id`, `title`, `level`, `path`, `blocks`, `children`
- All blocks must have: `section_id`, `type`, `content`, `metadata`

**"Invalid block type"**
- Check block `type` against supported types
- Common typo: `"code"` instead of `"code_block"`

### Getting Help

```bash
# View document structure
mddata info sections document.md --paths

# List all sections
mddata info sections document.md

# Check frontmatter
mddata info properties document.md

# Validate structure by round-trip
mddata extract json doc.md | mddata generate --data - --output test.md
```

---

## Related Documentation

- [Schema Format](MARKDOWN_SCHEMA.md) - Validation rules for markdown documents
- [CLI Reference](CLI_REFERENCE.md) - Complete command documentation
- [Examples](../examples/generation/) - Working example files
