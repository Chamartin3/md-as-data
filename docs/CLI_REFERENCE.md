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

## write

**Unified command for creating and modifying markdown files from various sources**

The `write` command provides a modern, unified interface for all document creation and modification operations. It intelligently detects the operation mode based on provided arguments and supports multiple source types with automatic resolution.

### Subcommands

- `from` - Create/modify from data, forms, or schemas
- `set-property` - Set individual frontmatter property
- `set-section` - Modify individual section content
- `remove-property` - Remove frontmatter property

### `write from`

Create or modify markdown files from various sources with intelligent resolution.

```bash
mddata write from [TARGET_FILE] [OPTIONS]
```

**Source Options:**
- `-d, --data FILE` - Data file (JSON/YAML) with values
- `-f, --form FILE` - Form/template file (YAML) with structure
- `-s, --schema FILE` - Schema file (JSON/YAML) for validation

> **Note**: For detailed Forms documentation with parameter types, validation rules, and examples, see **[MARKDOWN_FORMS.md](MARKDOWN_FORMS.md)**

**Parameter Options:**
- `-p, --param TEXT` - Parameter override (KEY=VALUE or KEY=@file)
- `--params FILE` - Parameter file (JSON/YAML)

**Output Options:**
- `-o, --output FILE` - Output file path
- `--policy TEXT` - Update policy: merge, replace, update, append [default: merge]
- `-F, --force` - Overwrite existing files
- `-n, --dry-run` - Preview changes without applying

**Operation Modes:**

1. **CREATE** - Create new file when `--output` specified
2. **MODIFY** - Modify existing file when `TARGET_FILE` exists
3. **STDOUT** - Print to console when no output/target
4. **TEMPLATE** - Generate template when only `--schema` provided

**Resolution Order:**

1. Load form structure (if `-f` provided)
2. Merge data values (if `-d` provided)
3. Apply parameter file (if `--params` provided)
4. Apply CLI parameters (if `-p` provided, highest priority)
5. Resolve computed parameters (date, time, env vars)
6. Fill template placeholders `{{...}}`
7. Validate against schema (if `-s` provided)
8. Apply to target with specified policy

**Examples:**

```bash
# Create from data
mddata write from -d document.json -o output.md

# Fill form with parameters
mddata write from -f form.yaml -p title="Hello" -o post.md

# Combine form + data + validation
mddata write from -f form.yaml -d values.json -s schema.json -o out.md

# Modify existing file
mddata write from -d changes.json existing.md

# Generate template from schema
mddata write from -s schema.json -o template.md

# Output to stdout
mddata write from -d data.json

# Stdin/stdout pipeline
cat data.json | mddata write from -d -

# Fill form with data from stdin instead of -p options
echo '{"title": "My Post", "author": "Alice"}' | \
  mddata write from -f blog-form.yaml -d - -o post.md
```

### `write set-property`

Set frontmatter property in an existing markdown file.

```bash
mddata write set-property FILE PROPERTY VALUE [OPTIONS]
```

**Options:**
- `--json` - Parse value as JSON

**Examples:**

```bash
# Set string property
mddata write set-property document.md title "New Title"

# Set JSON array
mddata write set-property document.md tags '["a", "b"]' --json

# Set numeric value
mddata write set-property document.md version "2.0"

# Set boolean
mddata write set-property document.md draft "false" --json
```

### `write remove-property`

Remove frontmatter property from an existing markdown file.

```bash
mddata write remove-property FILE PROPERTY
```

**Examples:**

```bash
# Remove property
mddata write remove-property document.md draft

# Remove nested property
mddata write remove-property document.md metadata.old_field
```

### `write set-section`

Set section content in an existing markdown file.

```bash
mddata write set-section FILE SECTION_ID CONTENT [OPTIONS]
```

**Options:**
- `--policy TEXT` - Update policy: update, replace, append [default: update]

**Examples:**

```bash
# Update section (merge content)
mddata write set-section document.md intro "New content"

# Replace section entirely
mddata write set-section document.md intro "Replace all" --policy replace

# Append to section
mddata write set-section document.md notes "More notes" --policy append

# Create nested section
mddata write set-section document.md introduction.overview "Overview text"
```

## Real-World Workflows

### Blog Publishing

```bash
# Create draft from form
mddata write from -f blog-form.yaml \
  -p title="My Post" \
  -p author="John Doe" \
  -o posts/draft.md

# Update status when ready
mddata write set-property posts/draft.md status "published"

# Add publication date
mddata write set-property posts/draft.md published_date "2025-11-18"
```

### Documentation Generation

```bash
# Generate template from schema
mddata write from -s api-schema.json -o docs/api-template.md

# Fill with actual API data
mddata write from -f docs/api-template.md -d api-data.json -o docs/api-v2.md

# Update specific section
mddata write set-section docs/api-v2.md authentication "New auth flow"
```

---

## Write Commands

The `write` command provides a unified interface for creating and modifying markdown files.

### Command Tree

```
mddata write
├── from                Create/modify from sources
├── set-property        Set frontmatter property
├── remove-property     Remove frontmatter property
└── set-section         Set section content
```

### `write from`

Create or modify markdown files from various sources with intelligent resolution.

**Syntax:**
```bash
mddata write from [TARGET_FILE] [OPTIONS]
```

**Source Options:**
- `-d, --data FILE` - Data file (JSON/YAML) with values
- `-f, --form FILE` - Form/template file (YAML) with structure
- `-s, --schema FILE` - Schema file (JSON/YAML) for validation

> **Note**: For detailed Forms documentation with parameter types, validation rules, and examples, see **[MARKDOWN_FORMS.md](MARKDOWN_FORMS.md)**

**Parameter Options:**
- `-p, --param TEXT` - Parameter override (KEY=VALUE or KEY=@file)
- `--params FILE` - Parameter file (JSON/YAML)

**Output Options:**
- `-o, --output FILE` - Output file path
- `--policy TEXT` - Update policy: merge, replace, update, append [default: merge]
- `-F, --force` - Overwrite existing files
- `-n, --dry-run` - Preview changes without applying

**Operation Modes:**

1. **CREATE** - Create new file when `--output` specified
2. **MODIFY** - Modify existing file when `TARGET_FILE` exists
3. **STDOUT** - Print to console when no output/target
4. **TEMPLATE** - Generate template when only `--schema` provided

**Resolution Order:**

1. Load form structure (if `-f` provided)
2. Merge data values (if `-d` provided)
3. Apply parameter file (if `--params` provided)
4. Apply CLI parameters (if `-p` provided, highest priority)
5. Resolve computed parameters (date, time, env vars)
6. Fill template placeholders `{{...}}`
7. Validate against schema (if `-s` provided)
8. Apply to target with specified policy

**Examples:**

```bash
# Create from data
mddata write from -d document.json -o output.md

# Fill form with parameters
mddata write from -f form.yaml -p title="Hello" -o post.md

# Combine form + data + validation
mddata write from -f form.yaml -d values.json -s schema.json -o out.md

# Modify existing file
mddata write from -d changes.json existing.md

# Generate template from schema
mddata write from -s schema.json -o template.md

# Output to stdout
mddata write from -d data.json

# Stdin/stdout pipeline
cat data.json | mddata write from -d -

# Fill form with data from stdin instead of -p options
echo '{"title": "My Post", "author": "Alice"}' | \
  mddata write from -f blog-form.yaml -d - -o post.md
```

### `write set-property`

Set frontmatter property in an existing markdown file.

**Syntax:**
```bash
mddata write set-property FILE PROPERTY VALUE [OPTIONS]
```

**Options:**
- `--json` - Parse value as JSON

**Examples:**

```bash
# Set string property
mddata write set-property document.md title "New Title"

# Set JSON array
mddata write set-property document.md tags '["a", "b"]' --json

# Set numeric value
mddata write set-property document.md version "2.0"

# Set boolean
mddata write set-property document.md draft "false" --json
```

### `write remove-property`

Remove frontmatter property from an existing markdown file.

**Syntax:**
```bash
mddata write remove-property FILE PROPERTY
```

**Examples:**

```bash
# Remove property
mddata write remove-property document.md draft

# Remove nested property
mddata write remove-property document.md metadata.old_field
```

### `write set-section`

Set section content in an existing markdown file.

**Syntax:**
```bash
mddata write set-section FILE SECTION_ID CONTENT [OPTIONS]
```

**Options:**
- `--policy TEXT` - Update policy: update, replace, append [default: update]

**Examples:**

```bash
# Update section (merge content)
mddata write set-section document.md intro "New content"

# Replace section entirely
mddata write set-section document.md intro "Replace all" --policy replace

# Append to section
mddata write set-section document.md notes "More notes" --policy append

# Create nested section
mddata write set-section document.md introduction.overview "Overview text"
```

## Real-World Workflows

### Blog Publishing

```bash
# Create draft from form
mddata write from -f blog-form.yaml \
  -p title="My Post" \
  -p author="John Doe" \
  -o posts/draft.md

# Update status when ready
mddata write set-property posts/draft.md status "published"

# Add publication date
mddata write set-property posts/draft.md published_date "2025-11-18"
```

### Documentation Generation

```bash
# Generate template from schema
mddata write from -s api-schema.json -o docs/api-template.md

# Fill with actual API data
mddata write from -f docs/api-template.md -d api-data.json -o docs/api-v2.md

# Update specific section
mddata write set-section docs/api-v2.md authentication "New auth flow"
```

---

## Extract Commands

Extract structured data in various formats, with support for path-based extraction to retrieve specific properties or sections.

### `extract path`

Extract value at a specific path (property, nested property, or section).

```bash
mddata extract path document.md title
mddata extract path document.md tags
mddata extract path document.md metadata.author
mddata extract path document.md introduction
mddata extract path document.md features.authentication --output section.md
```

**Arguments:**
- `file_path`: Path to the markdown file
- `path`: Dot-separated path to extract

**Options:**
- `--output FILE`: Write to file instead of stdout

**Path Types:**

1. **Frontmatter Properties** - Returns the raw value
   ```bash
   mddata extract path doc.md title
   # Output: My Document Title

   mddata extract path doc.md draft
   # Output: false
   ```

2. **Array Properties** - Returns JSON array
   ```bash
   mddata extract path doc.md tags
   # Output: ["python", "markdown", "data"]
   ```

3. **Nested Properties** - Navigate into nested objects
   ```bash
   mddata extract path doc.md metadata.author
   # Output: John Doe

   mddata extract path doc.md metadata.tags
   # Output: ["tutorial", "guide"]
   ```

4. **Sections** - Returns markdown content
   ```bash
   mddata extract path doc.md introduction
   # Output: ## Introduction\n\nSection content here...

   mddata extract path doc.md features.authentication
   # Output: ### Authentication\n\nNested section content...
   ```

### `extract json`

Extract complete document or specific path as JSON.

```bash
# Extract entire document
mddata extract json document.md
mddata extract json document.md --pretty --output data.json

# Extract specific path
mddata extract json document.md --path title --pretty
mddata extract json document.md --path metadata --pretty
mddata extract json document.md --path introduction
```

**Arguments:**
- `file_path`: Path to the markdown file

**Options:**
- `--path PATH`: Dot-separated path to extract (e.g., 'title', 'metadata.tags')
- `--pretty`: Format output with indentation
- `--output FILE`: Write to file instead of stdout

**Examples:**

```bash
# Extract property as JSON
mddata extract json blog.md --path title --pretty
# Output: "Getting Started with Markdown"

# Extract array as JSON
mddata extract json blog.md --path tags --pretty
# Output: ["tutorial", "markdown"]

# Extract nested object
mddata extract json blog.md --path metadata --pretty
# Output: {"author": "Jane Doe", "version": "1.0"}

# Extract section content (as JSON string)
mddata extract json blog.md --path introduction
# Output: "## Introduction\n\nWelcome to..."
```

### `extract yaml`

Extract complete document or specific path as YAML.

```bash
# Extract entire document
mddata extract yaml document.md
mddata extract yaml document.md --output data.yaml

# Extract specific path
mddata extract yaml document.md --path metadata
mddata extract yaml document.md --path introduction
```

**Arguments:**
- `file_path`: Path to the markdown file

**Options:**
- `--path PATH`: Dot-separated path to extract
- `--output FILE`: Write to file instead of stdout

**Examples:**

```bash
# Extract nested object as YAML
mddata extract yaml blog.md --path metadata
# Output:
# author: Jane Doe
# version: 1.0

# Extract section as YAML (quoted string)
mddata extract yaml blog.md --path introduction
# Output: '## Introduction\n\nWelcome to...'
```

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

## Path-Based Extraction

All extraction commands support path-based queries to retrieve specific values instead of the entire document. Paths use dot notation to navigate the document structure.

### Path Syntax

Paths are dot-separated identifiers that can reference:

1. **Top-level properties**: `title`, `author`, `status`
2. **Nested properties**: `metadata.author`, `config.theme.colors`
3. **Section IDs**: `introduction`, `main_content.section_one`

### Path Resolution Order

When resolving a path, mddata checks in this order:

1. **Exact frontmatter property match** - `title` returns frontmatter.title
2. **Nested property navigation** - `metadata.author` navigates into frontmatter.metadata
3. **Section path match** - `introduction` returns section content

### Examples by Use Case

**Configuration Extraction:**
```bash
# Extract version number for CI/CD
VERSION=$(mddata extract path project.md version)
echo "Building version $VERSION"

# Extract author email
EMAIL=$(mddata extract path project.md metadata.contact.email)
```

**Content Extraction:**
```bash
# Extract specific section for preview
mddata extract path article.md summary > preview.md

# Extract nested section
mddata extract path docs.md api.endpoints.authentication > auth-section.md
```

**Metadata Queries:**
```bash
# Check publication status
STATUS=$(mddata extract path post.md status)
if [ "$STATUS" = "published" ]; then
  echo "Post is live"
fi

# Extract tags for indexing
mddata extract json post.md --path tags | jq -r '.[]'
```

**Pipeline Integration:**
```bash
# Extract and transform
mddata extract json doc.md --path metadata | jq '.author = "Updated"' > new-meta.json

# Extract section and process
mddata extract path doc.md changelog | grep "Version 2.0"
```

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

## write

**Write markdown files from data, templates, or schemas**

### Synopsis

```
mddata write [TARGET_FILE] [OPTIONS]
```

### Description

The `write` command is a unified interface for creating and modifying markdown files. It intelligently determines the operation mode based on file existence and command arguments.

**Operation Modes:**

- **CREATE** - Creates new file from data or schema
- **MODIFY** - Modifies existing file (auto-detected)
- **SCHEMA_TEMPLATE** - Generates template from schema
- **STDOUT** - Renders to console without file creation

### Arguments

- `TARGET_FILE` (optional) - Target markdown file to modify or create

### Options

**Data Sources:**
- `--form PATH` - Path to markdown form file (JSON or YAML)
  - Form files MUST have parameters defined
  - Use with -p/--param to fill form parameters
  - Can be combined with --data for validation
  - Mutually exclusive with schema-only operations

- `--data, -d PATH` - Path to data file (JSON or YAML)
  - Use '-' to read from stdin
  - Supports MarkdownDataDict or MarkdownDataUpdate formats
  - Auto-detects format from file extension
  - Can be combined with --form for validation

- `--schema, -s PATH` - Path to schema file (JSON or YAML)
  - For template generation (without --data or --form)
  - For validation (with --data)

**Output Control:**
- `--output, -o PATH` - Output file path
  - Creates new file at specified path
  - Overrides TARGET_FILE for output location

- `--format, -f FORMAT` - Data format: json or yaml
  - Auto-detected from file extension if not specified

**Template Parameters:**
- `--param, -p KEY=VALUE` - Template parameter
  - Can be specified multiple times
  - Supports special formats:
    - `KEY=VALUE` - Literal value
    - `KEY=@file` - Read value from file
    - `KEY=-` - Read value from stdin
    - `KEY=@-` - Read value from stdin (alternative)

- `--params PATH` - Load all parameters from JSON/YAML file
  - Combines with --param options
  - File parameters merged with CLI parameters

**Merge Policy (for modify mode):**
- `--policy POLICY` - Merge policy: merge, replace, append
  - `merge` (default) - Smart merge with existing content
  - `replace` - Replace entire value/section
  - `append` - Add content to existing value/content

**Flags:**
- `--force, -F` - Force overwrite existing file
- `--dry-run, -n` - Show what would be done without applying

### Operation Mode Detection

The write command automatically determines the operation mode:

1. **MODIFY mode** - When TARGET_FILE exists
   - Auto-detects file existence
   - Applies changes from --data or --form
   - Uses specified --policy

2. **CREATE mode** - When --output specified OR TARGET_FILE doesn't exist
   - Creates new file from --data, --form, or --schema
   - Validates against --schema if provided
   - Fills form with parameters if --form provided

3. **FORM mode** - When --form provided
   - Form files MUST have parameters defined
   - Fill form with -p/--param or --params
   - Can be combined with --data for validation
   - Produces complete MarkdownDataUpdate (no parameters)

4. **SCHEMA_TEMPLATE mode** - When --schema provided WITHOUT --data or --form
   - Generates markdown template from schema definition
   - Creates placeholder content for all sections

5. **STDOUT mode** - When no output file specified
   - Renders markdown to stdout
   - Useful for piping or previewing

### Examples

**Create from complete data:**
```bash
# Create new file from JSON data
mddata write --data document.json --output new.md

# Create from YAML data
mddata write -d document.yaml -o new.md

# Render to stdout
mddata write --data document.json
cat document.json | mddata write -d -
```

**Create from form with parameters:**
```bash
# Fill form with CLI parameters (form must have parameters defined)
mddata write --form blog.yaml -p title="My Post" -p author="John Doe" -o post.md

# Fill form with multiple parameters
mddata write --form blog.yaml \
  -p title="My Blog Post" \
  -p author="John Doe" \
  -p date="2025-10-25" \
  -p tags='["tech", "tutorial"]' \
  -o post.md

# Fill form with parameters from file
mddata write --form blog.yaml --params values.json -o post.md

# Mix file and CLI parameters (CLI overrides file)
mddata write --form blog.yaml --params values.json \
  -p status="published" -o post.md

# Validate data against form structure (form + data)
mddata write --form blog.yaml --data draft.json -o validated.md

# Form + data + parameter overrides
mddata write --form blog.yaml --data draft.json \
  -p status="published" -o final.md
```

**Generate template from schema:**
```bash
# Generate from JSON schema
mddata write --schema schema.json --output template.md

# Generate from YAML schema
mddata write -s schema.yaml -o template.md

# Force overwrite existing template
mddata write --schema schema.json --output template.md --force
```

**Modify existing file:**
```bash
# Auto-detect modify mode (file exists)
mddata write --data changes.json existing.md

# Modify with merge policy (default)
mddata write --data updates.json existing.md --policy merge

# Replace content entirely
mddata write --data replacement.json existing.md --policy replace

# Append to existing content
mddata write --data additions.json existing.md --policy append

# Modify from stdin
cat changes.json | mddata write --data - existing.md
```

**Create with schema validation:**
```bash
# Validate data against schema during creation
mddata write --data data.json --schema schema.json --output validated.md

# Combine template, params, and schema
mddata write --data template.yaml \
  --schema schema.json \
  -p title="Validated Doc" \
  -o validated.md
```

**Dry run mode:**
```bash
# Preview create operation
mddata write --data data.json --output new.md --dry-run

# Preview modify operation
mddata write --data changes.json existing.md --dry-run

# Shows operation mode and data preview
```

### Exit Codes

- `0` - Success
- `1` - Error (missing parameters, validation failure, file access error)

### Error Messages

**Missing required parameters:**
```
Error: Template parameter validation failed
Missing required parameters: title, author

Provided: description
Required: title, author, description

Provide parameters using -p KEY=VALUE or --params file.json
```

**Invalid data structure:**
```
Error: Data structure validation failed
Invalid data structure: Data must contain 'frontmatter' field

Expected format: MarkdownDataDict or MarkdownDataUpdate
Received: {"items": [...]}
```

### Notes

- File format is auto-detected from extension (.json, .yaml, .yml)
- Template parameters support computed values (date, time, env.*)
- MODIFY mode preserves existing content unless policy=replace
- Use --dry-run to preview changes before applying

---

## Examples

### Complete Workflow

```bash
# 1. Inspect document structure
mddata info sections document.md --paths

# 2. Update properties
mddata write set-property document.md status "published"

# 3. Modify section content
mddata write set-section document.md introduction "Updated intro"

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
