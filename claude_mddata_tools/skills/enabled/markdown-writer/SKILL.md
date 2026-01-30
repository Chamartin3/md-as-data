---
name: markdown-writer
description: Create and modify markdown files using structured data and templates
  with the mddata CLI tool. Use this skill when users need to create new markdown
  documents from templates with parameter substitution, bulk update existing markdown
  files with structured JSON/YAML data, generate complete documents from data structures,
  or work with schema-validated markdown documents. Ideal for workflows involving
  markdown document generation, template-based content creation, and systematic document
  updates.
---
# Markdown Writer

<!-- keywords: -->
<!--   - markdown -->
<!--   - document generation -->
<!--   - templates -->
<!--   - structured data -->
<!--   - CLI -->
<!--   - mddata -->
<!--   - bulk updates -->
<!--   - schema validation -->
<!--   - parameter substitution -->
<!--   - YAML -->
<!--   - JSON -->
<!--   - content management -->
<!--   - documentation automation -->
<!--   - template filling -->
<!--   - computed parameters -->
<!-- allowed_tools: -->
<!--   - "mddata write (--data, --schema, --output, --params, -p/--param, --policy, --force, --dry-run)" -->
<!--   - "mddata modify (set-property, remove-property, set-section)" -->
<!--   - "mddata schema (infer, validate, info)" -->
<!--   - "mddata info (summary, sections, properties, blocks)" -->
<!--   - "mddata extract (json, yaml, frontmatter)" -->
## Overview

Enable programmatic creation and modification of markdown files using structured data and templates through the mddata CLI tool. This skill supports template-based document generation with parameter substitution, bulk updates from JSON/YAML data structures, complete document creation from structured data, and schema-validated document workflows.
## When to Use This Skill

Use this skill when the user requests:

1. **Template-based document creation** - "Create a meeting notes document from template", "Generate a blog post using this template"
2. **Bulk document updates** - "Update these sections and properties in the markdown file", "Apply these changes to the document"
3. **Document generation from data** - "Create a markdown report from this JSON data", "Generate documentation from this structure"
4. **Schema-validated documents** - "Create a document that conforms to this schema", "Validate and generate from template"
5. **Parameter-driven content** - "Fill in this template with these values", "Use these parameters to create the document"
## Core Workflow Decision Tree

```
User Request
    │
    ├─ Has structured data (JSON/YAML)?
    │   ├─ YES: Does data include parameters object?
    │   │   ├─ YES: Template workflow (§1)
    │   │   └─ NO: Data structure workflow (§2)
    │   └─ NO: Manual specification workflow (§3)
    │
    └─ Modifying existing file?
        ├─ YES: Update workflow (§4)
        └─ NO: Creation workflow (§1-3)



```
## 1. Template-Based Workflow

Use when the data file contains a `parameters` object with template placeholders (`{{variable}}`).

### Step 1: Identify Template Parameters

Examine the data file to identify required and optional parameters:

```yaml
parameters:
  title:
    type: str
    required: true
  author:
    type: str
    required: false
    default: "{{env.USER}}"



```
### Step 2: Gather Parameter Values

Collect parameter values from:

1. User-provided values in the request
2. Computed parameters (`{{date}}`, `{{time}}`, `{{env.VAR}}`)
3. Template defaults
4. Interactive prompts if required parameters missing
### Step 3: Execute Template Fill

```bash
# With CLI parameters
mddata write --data template.yaml \
  -p title="Document Title" \
  -p author="Author Name" \
  --output result.md

# With parameter file
mddata write --data template.yaml \
  --params params.json \
  --output result.md

# To stdout for review
mddata write --data template.yaml \
  -p title="Title" \
  -p author="Author"



```

**Example templates available in `assets/templates/`:**

- `meeting-notes-template.yaml` - Meeting notes with agenda, discussion, action items
- `blog-post-template.yaml` - Blog post with standard sections
## 2. Complete Document Creation Workflow

Use when creating an entire document from a complete data structure (no template parameters).

### Step 1: Construct Data Structure

Build JSON/YAML following the mddata format:

```json
{
  "frontmatter": {
    "title": "Document Title",
    "author": "Author",
    "date": "2025-01-26"
  },
  "content": {
    "sections": [
      {
        "id": "section_id",
        "title": "Section Title",
        "level": 2,
        "content": "Section content...",
        "subsections": []
      }
    ]
  }
}



```

Reference `assets/examples/complete-document-data.json` for a full example.
### Step 2: Execute Document Creation

```bash
# Create from complete data
mddata write --data complete.json --output document.md

# With schema validation
mddata write --data complete.json \
  --schema schema.json \
  --output validated-document.md

# Preview before writing
mddata write --data complete.json --dry-run



```
## 3. Manual Specification Workflow

Use when the user provides requirements verbally without a data file.

### Step 1: Determine Document Type

Ask: "What type of document?" (report, notes, blog post, documentation, etc.)
### Step 2: Select Approach

**Option A: Use Existing Template**

- Check `assets/templates/` for matching template
- Gather required parameters
- Proceed with Template-Based Workflow (§1)

**Option B: Build Data Structure**

- Collect frontmatter properties
- Identify section structure
- Build complete data structure
- Proceed with Complete Document Creation (§2)
### Step 3: Offer to Save Template

If the document structure may be reused:

```bash
# Generate schema from created document
mddata schema infer document.md --output schema.yaml

# Create reusable template
mddata write --schema schema.yaml --output template.yaml



```
## 4. Update Workflow

Use when modifying an existing markdown file.

### Step 1: Identify Update Scope

Determine what needs updating:

- Single property → Use `modify set-property`
- Single section → Use `modify set-section`
- Multiple changes → Use `write` with partial data
### Step 2: Choose Update Strategy

**For Granular Updates (1-2 changes):**

```bash
# Update single property
mddata modify set-property file.md status "published"

# Update single section
mddata modify set-section file.md intro "New content" --policy replace



```

**For Bulk Updates (3+ changes):**

Create update data file with only the changes:

```json
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



```

Reference `assets/examples/partial-update-data.json` for examples.
### Step 3: Execute Update

```bash
# Apply bulk update (auto-detects modify mode)
mddata write --data updates.json existing-file.md

# With specific policy
mddata write --data updates.json existing-file.md --policy merge

# Preview changes first
mddata write --data updates.json existing-file.md --dry-run



```
## Update Policies

When modifying sections, specify the appropriate policy:

- **merge** (default): Merge new content while preserving existing subsections
- **replace**: Completely replace section content including subsections
- **append**: Add new content after existing content

Specify policy either:

1. In data structure: `"policy": "replace"` per section
2. Via CLI flag: `--policy replace` for all sections
## Computed Parameters

Template parameters can use auto-generated values:

- `{{date}}` → Current date (YYYY-MM-DD)
- `{{time}}` → Current time (HH:MM:SS)
- `{{env.VAR}}` → Environment variable value

Example:

```yaml
frontmatter:
  created: "{{date}}"
  author: "{{env.USER}}"



```
## Schema Validation

For documents that must conform to specific structures:

### Generate Schema

```bash
# From single document
mddata schema infer document.md --output schema.json

# From multiple documents (merges common structure)
mddata schema infer ./docs/ --output schema.json



```
### Validate During Creation

```bash
# Create with validation
mddata write --data data.json \
  --schema schema.json \
  --output validated.md



```
### Create Template from Schema

```bash
# Generate template structure
mddata write --schema schema.json --output template.yaml



```
## Common Patterns

### Pattern 1: Recurring Documents

For regularly created documents (meeting notes, reports):

1. Create template once with parameters
2. Store in version control or shared location
3. Use with different parameter values each time

```bash
# Initial template creation
# (save meeting-notes-template.yaml)

# Weekly usage
mddata write --data meeting-notes-template.yaml \
  -p meeting_title="Weekly Sync" \
  -p date="2025-01-26" \
  -p attendees="Team A" \
  --output weekly-sync-2025-01-26.md



```
### Pattern 2: Document Generation Pipeline

For programmatic document generation:

1. Generate data structure from application/database
2. Optionally validate against schema
3. Create markdown document
4. Post-process if needed

```bash
# Application generates data.json
# Then:
mddata write --data data.json \
  --schema schema.json \
  --output generated-report.md



```
### Pattern 3: Interactive Document Builder

For guided document creation:

1. Prompt user for document type
2. Select or create appropriate template
3. Gather required parameters interactively
4. Generate document
5. Offer to save template for reuse
## Error Handling

### Missing Required Parameters

When template has required parameters without defaults:

```
ValueError: Missing required parameters: title, author
Provided: date
Available: title, author, date



```

**Resolution**: Provide missing parameters via `-p` flags or `--params` file.
### Invalid Data Structure

When data doesn't match expected format:

**Resolution**: Reference `assets/examples/` for correct structure examples, or use `mddata schema infer` on existing documents to see expected format.
### File Exists

When output file already exists:

**Resolution**: Use `--force/-F` flag to overwrite, or choose different output path.
## Resources

### references/

- **mddata_quickref.md** - Comprehensive quick reference for mddata CLI commands, data formats, and workflows
### assets/templates/

Pre-built template files ready to use:

- **meeting-notes-template.yaml** - Meeting notes with agenda, discussion, action items
- **blog-post-template.yaml** - Blog post with standard sections
### assets/examples/

Example data structures for learning and reference:

- **complete-document-data.json** - Complete document structure example
- **partial-update-data.json** - Partial update/modification example
- **template-params.json** - Parameter file example for templates
## Best Practices

1. **Use templates for recurring documents** - Define once, use many times with different parameters
2. **Store templates in version control** - Treat templates as code for team collaboration
3. **Validate with schemas** - Ensure document consistency across team/project
4. **Preview with --dry-run** - Review changes before applying, especially for updates
5. **Use descriptive section IDs** - Clear IDs make updates easier (`introduction` not `intro1`)
6. **Leverage computed parameters** - Use `{{date}}`, `{{env.VAR}}` to reduce manual input
7. **Start with examples** - Copy and modify from `assets/examples/` rather than building from scratch
8. **Keep data structures clean** - Only include sections that need updates in partial update files
## Advanced Usage

### Stdin Data Pipes

Process data from pipelines:

```bash
# From command output
generate-report-data | mddata write --data - --output report.md

# From script
cat data.json | mddata write --data - \
  --schema schema.json \
  --output validated.md



```
### Batch Processing

Generate multiple documents:

```bash
# Shell loop with templates
for meeting in meetings/*.json; do
  mddata write --data template.yaml \
    --params "$meeting" \
    --output "notes/$(basename $meeting .json).md"
done



```
### Format Flexibility

Both JSON and YAML formats supported for all data files:

```bash
# YAML template (more readable)
mddata write --data template.yaml -p title="Doc" -o out.md

# JSON data (programmatic)
mddata write --data data.json -o out.md



```

Format auto-detected from file extension (.json, .yaml, .yml).
