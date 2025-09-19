# CLI Reference

Complete reference for the `mddata` command-line interface.

## Command Structure

```bash
mddata <command> [subcommand] <file_path> [arguments] [options]
```

The `file_path` is required for most commands and appears after the command/subcommand. It can be:
- A single markdown file: `document.md`
- A directory path: `./docs/` (for schema generation only)

The `generate` command is a top-level command that doesn't require a file path since it creates new files from data or schema sources.

---

## Info Commands

Query and inspect markdown file structure.

### `info summary`

Display file summary with basic statistics.

```bash
mddata info summary document.md
mddata info summary document.md --verbose
```

**Options:**
- `--verbose`: Show detailed information

### `info properties`

List all frontmatter properties.

```bash
mddata info properties document.md
mddata info properties document.md --verbose
```

**Options:**
- `--verbose`: Show property values and types

### `info sections`

Show document sections with hierarchy.

```bash
mddata info sections document.md
mddata info sections document.md --blocks --paths
```

**Options:**
- `--blocks`: Include block counts per section
- `--paths`: Display full section paths

### `info blocks`

List all content blocks with optional filtering.

```bash
mddata info blocks document.md
mddata info blocks document.md --type paragraph --limit 10
```

**Options:**
- `--type TYPE`: Filter by block type (paragraph, code_block, heading, list, etc.)
- `--limit N`: Limit number of blocks displayed

### `info tasks`

Display task list information from document.

```bash
mddata info tasks document.md
mddata info tasks document.md --section "sprint_planning"
mddata info tasks document.md --symbol "x"
mddata info tasks document.md --completed
mddata info tasks document.md --pending
```

**Options:**
- `--section SECTION`: Filter tasks by section
- `--symbol SYMBOL`: Filter by specific checkbox symbol
- `--completed`: Show only completed tasks
- `--pending`: Show only pending tasks
- `--verbose`: Show detailed task information

---

## Modify Commands

Modify document content and properties.

### `modify set-property`

Set or update a frontmatter property.

```bash
mddata modify set-property document.md title "New Title"
mddata modify set-property document.md tags '["new", "tags"]' --json
```

**Arguments:**
- `file_path`: Path to the markdown file
- `key`: Name of the property to set
- `value`: Value to assign (string or JSON)

**Options:**
- `--json`: Parse value as JSON (for arrays, objects, etc.)

### `modify remove-property`

Remove a frontmatter property.

```bash
mddata modify remove-property document.md draft
```

**Arguments:**
- `file_path`: Path to the markdown file
- `key`: Name of the property to remove

### `modify set-section`

Modify section content or create new subsections.

```bash
mddata modify set-section document.md intro "New content"
mddata modify set-section document.md intro "Replace all" --policy replace
mddata modify set-section document.md parent.child "New subsection"
```

**Arguments:**
- `file_path`: Path to the markdown file
- `section_id`: Section identifier or path (e.g., `intro` or `parent.child.subsection`)
- `content`: New content for the section

**Options:**
- `--policy POLICY`: Content merge policy (default: `update`)
  - `update`: Merge content while preserving subsections
  - `replace`: Replace entire section content
  - `append`: Add content to existing section

**Path Support:**
- Use dot-separated paths for nested sections: `introduction.overview`
- Create new subsections automatically: `parent.new_child`

### `modify from-json`

Apply bulk changes from JSON file or stdin.

```bash
mddata modify from-json document.md changes.json
mddata modify from-json document.md - < changes.json
mddata modify from-json document.md changes.json --dry-run
```

**Arguments:**
- `file_path`: Path to the markdown file
- `source`: Path to JSON file containing changes (use `-` for stdin)

**Options:**
- `--dry-run`: Preview changes without saving

**JSON Format:**
```json
{
  "frontmatter": {
    "title": "New Title",
    "status": "published"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "Updated intro",
      "policy": "replace"
    }
  ]
}
```

### `modify from-template`

Apply template with parameter substitution to create or modify documents.

```bash
# Basic template application
mddata modify from-template document.md template.yaml \
  -p title="My Document" \
  -p author="John Doe"

# Load parameters from file
mddata modify from-template document.md template.yaml \
  --params params.json

# Mix parameter sources (CLI overrides file)
mddata modify from-template document.md template.yaml \
  --params base_params.json \
  -p title="Override Title"

# Load template from stdin
cat template.yaml | mddata modify from-template document.md -

# Parameter from files or stdin
mddata modify from-template document.md template.yaml \
  -p content=@content.txt \
  -p password=- \
  -p config=@config.json

# Dry run to preview changes
mddata modify from-template document.md template.yaml \
  -p title="Test" \
  --dry-run
```

**Arguments:**
- `file_path`: Path to the markdown file to modify
- `template_path`: Path to template file (JSON/YAML) or `-` for stdin

**Options:**
- `-p, --param KEY=VALUE`: Parameter value (KEY=VALUE, KEY=@file, KEY=-, KEY=@-)
- `--params FILE`: Load all parameters from JSON/YAML file
- `--format FORMAT`: Template format for stdin (yaml or json, default: yaml)
- `-n, --dry-run`: Preview changes without applying them

**Parameter Sources (Precedence Order):**
1. **CLI parameters** (`-p key=value`) - highest precedence
2. **Parameter file** (`--params file.json`) - medium precedence
3. **Template defaults** - lower precedence
4. **Computed parameters** (`{date}`, `{env.VAR}`, etc.) - lowest precedence

**Parameter Value Formats:**
- `key=value`: Direct string value
- `key=@file.txt`: Load value from file
- `key=-`: Interactive input from terminal
- `key=@-`: Load value from piped stdin

**Template Format:**
Templates are JSON or YAML files with `parameters` and `changes` sections:

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Document title"
  author:
    type: str
    default: "Anonymous"
  tags:
    type: array
    item_type: str

changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    created: "{date}"
  sections:
    - id: "introduction"
      content: "# {title}\n\nBy {author}"
```

**Computed Parameters:**
- `{date}`: Current date (YYYY-MM-DD)
- `{time}`: Current time (HH:MM:SS)
- `{now}`: Current datetime (ISO 8601)
- `{env.VAR_NAME}`: Environment variable value

---

## Extract Commands

Extract structured data in various formats.

### `extract json`

Extract complete document as JSON.

```bash
mddata extract json document.md
mddata extract json document.md --pretty --output data.json
```

**Arguments:**
- `file_path`: Path to the markdown file

**Options:**
- `--pretty`: Format output with indentation
- `--output FILE`: Write to file instead of stdout

### `extract yaml`

Extract complete document as YAML.

```bash
mddata extract yaml document.md
mddata extract yaml document.md --output data.yaml
```

**Arguments:**
- `file_path`: Path to the markdown file

**Options:**
- `--output FILE`: Write to file instead of stdout

### `extract frontmatter`

Extract only frontmatter properties.

```bash
mddata extract frontmatter document.md
mddata extract frontmatter document.md --format json
mddata extract frontmatter document.md --format yaml
```

**Arguments:**
- `file_path`: Path to the markdown file

**Options:**
- `--format FORMAT`: Output format (json or yaml, default: json)

---

## Schema Commands

Generate and validate schemas for document structure.

### `schema generate`

Generate schema from single file or directory.

```bash
# Single file
mddata schema generate document.md --output schema.json
mddata schema generate document.md --format yaml --output schema.yaml --pretty

# Directory (recursive)
mddata schema generate ./docs/ --output docs_schema.json --pretty
```

**Arguments:**
- `file_path`: Path to markdown file or folder

**Options:**
- `--format FORMAT`: Output format (`json` or `yaml`, default: `json`)
- `--output FILE`: Output file path (default: stdout)
- `--pretty`: Format output with indentation
- `--inference-mode MODE`: Inference mode (`permissive` or `strict`, default: `permissive`)

**Inference Modes:**
- `permissive`: Flexible constraints allowing document evolution
- `strict`: Exact constraints based on current structure

**Multi-File Generation:**
When a directory path is provided:
- Recursively processes all `.md` files
- Aggregates frontmatter properties across documents
- Marks properties as required if appearing in ≥75% of documents
- Creates enum types for consistent single-word string values
- Uses union types for conflicting property types
- Merges all section hierarchies

### `schema validate`

Validate document against schema file.

```bash
mddata schema validate document.md schema.json
mddata schema validate document.md schema.yaml --verbose
```

**Arguments:**
- `file_path`: Path to the markdown file
- `schema_file`: Path to schema file (JSON or YAML)

**Options:**
- `--verbose`: Show detailed validation results
- `--validation-level LEVEL`: Override schema validation level (strict, warnings, disabled)

**Format Auto-Detection:**
Schema format is automatically detected from file extension (`.json`, `.yaml`, `.yml`).

### `schema info`

Display schema information and structure.

```bash
mddata schema info schema.json
mddata schema info schema.yaml
```

**Arguments:**
- `schema_file`: Path to schema file (JSON or YAML)

---

## Generate Command

Create new markdown files from structured data or schema templates.

### `generate`

Unified command to generate markdown files from JSON data, schema templates, or both.

```bash
# Generate from JSON data
mddata generate --data data.json --output document.md
mddata generate -d data.json -o document.md  # Short form

# Generate from stdin
cat data.json | mddata generate --data - --output document.md
echo '{"frontmatter": {"title": "New Doc"}, "content": {...}}' | mddata generate -d - -o new.md

# Generate template from schema
mddata generate --schema schema.json --output template.md
mddata generate -s schema.yaml -o template.md

# Generate from data with schema validation (both parameters)
mddata generate --data data.json --schema schema.json --output document.md
mddata generate -d data.json -s schema.yaml -o document.md

# Print to stdout (omit --output)
mddata generate --data data.json
```

**Options:**
- `--schema FILE, -s FILE`: Path to schema file (JSON or YAML) for template generation
- `--data FILE, -d FILE`: Path to JSON data file (use `-` for stdin, MarkdownDataDict format)
- `--output FILE, -o FILE`: Output markdown file path (prints to stdout if omitted)
- `--force, -F`: Force overwrite existing file if it exists

**Requirements:**
- At least one of `--schema` or `--data` must be provided
- When using `--schema` alone, `--output` is required
- When using `--data` alone, `--output` is optional (defaults to stdout)
- When using both, generates from data and validates against schema

**JSON Data Format:**

The JSON data must match the `MarkdownDataDict` format (same as output from `export json`):

```json
{
  "frontmatter": {
    "title": "Document Title",
    "author": "Author Name",
    "date": "2025-10-21"
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 2,
        "blocks": [
          {
            "type": "paragraph",
            "content": "This is the introduction paragraph."
          }
        ],
        "subsections": []
      }
    ]
  }
}
```

**Schema Template Behavior:**

When using `--schema`, creates a markdown template with:
- All required frontmatter properties set to default values or placeholders
- Section structure matching the schema's section definitions
- Placeholder content for each section
- Proper heading levels based on section hierarchy

**Examples:**

```bash
# 1. Generate schema from existing document
mddata schema generate document.md --output doc-schema.json --pretty

# 2. Create new template from schema
mddata generate --schema doc-schema.json --output new-document.md

# 3. Generate from data and validate with schema
mddata generate --data data.json --schema doc-schema.json --output validated.md

# Result: new-document.md with same structure as document.md
```

---

## Examples

### Complete Workflow

```bash
# 1. Inspect document structure
mddata info sections document.md --paths

# 2. Update properties
mddata modify set-property document.md status "published"

# 3. Modify section content
mddata modify set-section document.md introduction "Updated intro"

# 4. Extract to JSON
mddata extract json document.md --pretty --output updated.json
```

### Schema Validation Workflow

```bash
# 1. Generate schema
mddata schema generate document.md --output doc-schema.json --pretty

# 2. Validate document
mddata schema validate document.md doc-schema.json --verbose

# 3. Show schema details
mddata schema info doc-schema.json
```

### Bulk Processing

```bash
# Create changes file
cat > changes.json <<EOF
{
  "frontmatter": {
    "version": "2.0",
    "updated": "2025-10-10"
  },
  "sections": [
    {
      "id": "changelog",
      "content": "## Changelog\n\n- Version 2.0 released",
      "policy": "replace"
    }
  ]
}
EOF

# Apply changes
mddata modify from-json document.md changes.json
```

### Directory Schema Generation

```bash
# Generate schema from all markdown files in a directory
mddata schema generate ./docs/ --format yaml --output docs-schema.yaml --pretty

# Output shows file count:
# Schema generated from 15 markdown files
```

### Template Generation Workflow

```bash
# 1. Create schema from existing document
mddata schema generate document.md --output doc-schema.json --pretty

# 2. Generate new markdown from schema template
mddata generate --schema doc-schema.json --output new-doc.md

# 3. Alternatively, extract existing doc and recreate from JSON
mddata extract json document.md --pretty --output data.json
mddata generate --data data.json --output recreated.md
```

### Round-Trip Data Workflow

```bash
# 1. Extract markdown to JSON
mddata extract json document.md --pretty --output data.json

# 2. Modify JSON externally (with scripts, jq, etc.)
jq '.frontmatter.version = "2.0"' data.json > modified.json

# 3. Generate new markdown from modified JSON
mddata generate --data modified.json --output updated.md
```

---

## Error Handling

The CLI provides comprehensive error messages:

- **Invalid paths**: Clear errors with suggestions for similar sections
- **Ambiguous references**: Shows all matching sections when path is unclear
- **Missing parents**: Validates parent paths exist before creating subsections
- **File operations**: Proper error reporting for access issues
- **Schema validation**: Detailed error messages with property paths

---

## Output Formats

All commands support rich terminal output with:
- **Colorized output**: Syntax highlighting for better readability
- **Formatted tables**: Structured data display
- **Progress indicators**: For long-running operations
- **Error highlighting**: Clear visual distinction for errors and warnings
