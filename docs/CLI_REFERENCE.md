# CLI Reference

Complete reference for the `mddata` command-line interface.

## Command Structure

```bash
mddata <command> [subcommand] <file_path> [arguments] [options]
```

The `file_path` is required for most commands and appears after the command/subcommand. It can be:
- A single markdown file: `document.md`
- A directory path: `./docs/` (for schema generation only)

The `write` command is a unified command that doesn't require a file path in all modes since it can create new files from data, modify existing files, or render to stdout.

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

Infer and validate schemas for document structure.

### `schema infer`

Infer schema from single file or directory.

```bash
# Single file
mddata schema infer document.md --output schema.json
mddata schema infer document.md --format yaml --output schema.yaml --pretty

# Directory (recursive)
mddata schema infer ./docs/ --output docs_schema.json --pretty
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

## Write Command

Unified command for creating, modifying, and rendering markdown files with intelligent auto-detection.

### `write`

Intelligent command that automatically detects operation mode based on inputs and target file existence.

**Operation Modes:**
- **CREATE**: Generate new file from data/template/schema (when output specified and target doesn't exist)
- **MODIFY**: Update existing file with data changes (when target file exists)
- **SCHEMA_TEMPLATE**: Generate template from schema only (schema only, output specified)
- **STDOUT**: Render to stdout without creating files (data/schema provided, no output)

```bash
# Create new file from data
mddata write --data data.json --output new.md

# Modify existing file
mddata write --data changes.json existing.md

# Generate template from schema
mddata write --schema schema.json --output template.md

# Render to stdout
mddata write --data data.json

# With template parameters
mddata write --data template.yaml -p title="My Doc" --output result.md

# From stdin
cat data.json | mddata write --data - --output document.md

# Dry run to preview changes
mddata write --data changes.json existing.md --dry-run
```

**Arguments:**
- `target_file`: Target file to modify (for modify mode) or positional argument for data file

**Options:**
- `--data FILE, -d FILE`: Path to data/template file (use `-` for stdin, JSON/YAML format)
- `--schema FILE, -s FILE`: Path to schema file for validation/template generation
- `--output FILE, -o FILE`: Output file path (required for create/schema_template modes)
- `--format FORMAT, -f FORMAT`: Data format: json or yaml (default: auto-detect)
- `--param KEY=VALUE, -p KEY=VALUE`: Template parameter value
- `--params FILE`: Load parameters from JSON/YAML file
- `--policy POLICY`: Merge policy: replace, update, merge, append (default: update)
- `--force, -F`: Force overwrite existing files
- `--dry-run, -n`: Preview changes without applying

**Requirements:**
- At least one of `--data` or `--schema` must be provided
- For MODIFY mode: target file must exist
- For CREATE/SCHEMA_TEMPLATE modes: `--output` is required
- For STDOUT mode: no output file, renders to console

**Data Format:**

Supports both JSON and YAML formats. JSON data uses `MarkdownDataDict` format (same as `extract json` output):

```json
{
  "frontmatter": {
    "title": "Document Title",
    "author": "Author Name"
  },
  "content": {
    "children": [
      {
        "id": "introduction",
        "title": "Introduction",
        "blocks": [
          {
            "type": "paragraph",
            "content": "Introduction content"
          }
        ]
      }
    ]
  }
}
```

**Template Parameters:**

Parameters can be provided via CLI, files, or computed values:

```bash
# CLI parameters
mddata write --data template.yaml -p title="My Doc" -p author="John"

# From parameter file
mddata write --data template.yaml --params params.json

# Computed parameters (automatic)
# {date}, {time}, {now}, {env.VAR_NAME}
```

**Merge Policies:**
- `update` (default): Merge content while preserving subsections
- `replace`: Replace entire section content
- `merge`: Deep merge data structures
- `append`: Add content to existing sections

**Examples:**

```bash
# 1. Create from data
mddata write --data document.json --output new.md

# 2. Modify existing file
mddata write --data changes.json existing.md

# 3. Generate template from schema
mddata write --schema schema.json --output template.md

# 4. With validation
mddata write --data data.json --schema schema.json --output validated.md

# 5. Template with parameters
mddata write --data template.yaml -p title="Report" --output report.md
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
# 1. Infer schema
mddata schema infer document.md --output doc-schema.json --pretty

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
mddata write --data changes.json document.md --output updated.md
```

### Directory Schema Inference

```bash
# Infer schema from all markdown files in a directory
mddata schema infer ./docs/ --format yaml --output docs-schema.yaml --pretty

# Output shows file count:
# Schema generated from 15 markdown files
```

### Template Rendering Workflow

```bash
# 1. Create schema from existing document
mddata schema infer document.md --output doc-schema.json --pretty

# 2. Generate new markdown from schema template
mddata write --schema doc-schema.json --output new-doc.md

# 3. Alternatively, extract existing doc and recreate from JSON
mddata extract json document.md --pretty --output data.json
mddata write --data data.json --output recreated.md
```

### Round-Trip Data Workflow

```bash
# 1. Extract markdown to JSON
mddata extract json document.md --pretty --output data.json

# 2. Modify JSON externally (with scripts, jq, etc.)
jq '.frontmatter.version = "2.0"' data.json > modified.json

# 3. Create new markdown from modified JSON
mddata write --data modified.json --output updated.md
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
