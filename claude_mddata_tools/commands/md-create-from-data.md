---
description: Create new markdown file from JSON or YAML data structure
argument-hint: <data-file> <output-file> [--incremental]
allowed-tools: Bash(mddata:*)
---

# Create Markdown From Data

Create markdown file **$2** from data file **$1**

## Workflow Options

### Option 1: Complete Document Creation (Default)

Generate complete markdown from data structure or template:
```bash
mddata write --data "$1" --output "$2"
mddata info summary "$2"
```

### Option 2: Incremental Section Creation

Create document structure first, then add sections incrementally:

**Step 1: Create initial document with frontmatter**
```bash
# Create base document with frontmatter only
mddata write --data "$1" --output "$2"
```

**Step 2: Add sections using write command**
```bash
# Add sections incrementally from section data files (modifies existing file)
mddata write --data sections.json "$2"

# Or add individual sections with modify commands
mddata modify set-section "$2" introduction "Introduction content"
mddata modify set-section "$2" conclusion "Conclusion content"
```

**Step 3: Verify final result**
```bash
mddata info summary "$2"
mddata info sections "$2" --blocks
```

---

## Data Formats

The `write` command supports two types of data files:

### 1. MarkdownDataDict (JSON/YAML)

Complete document structure with `frontmatter` and `content`:

```json
{
  "frontmatter": {
    "title": "My Document",
    "author": "John Doe",
    "date": "2025-01-24"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "blocks": [],
    "children": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph",
            "content": "This is the introduction.",
            "section_id": "introduction"
          }
        ],
        "children": []
      }
    ]
  }
}
```

### 2. Template Files (JSON/YAML)

Template with parameter definitions and substitution:

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
    tags: "{tags}"
  sections:
    - id: "introduction"
      content: "# {title}\n\nBy {author}"
```

### 3. Section Data (for Incremental Creation)

Data structure for adding sections using `write --data`:

```json
{
  "frontmatter": {
    "status": "in-progress",
    "updated": "2025-10-25"
  },
  "sections": [
    {
      "id": "section_name",
      "content": "# Section Title\n\nSection content here.",
      "policy": "update"
    },
    {
      "id": "parent.child_section",
      "content": "## Child Section\n\nNested content.",
      "policy": "update"
    }
  ]
}
```

**Policy Options:**
- `update` (default): Merge content while preserving subsections
- `replace`: Replace entire section content
- `append`: Add content to existing section

**Section Paths:**
- Use dot-notation for nested sections: `"parent.child.grandchild"`
- Parent sections must exist before creating children
- Heading levels are automatically calculated

---

## Usage Examples

**Basic Usage:**

```bash
# Create from JSON data
/md-create-from-data data.json output.md

# Create from YAML data
/md-create-from-data data.yaml output.md

# Create from stdin
cat data.json | mddata write --data - --output output.md
```

**Incremental Creation:**

```bash
# Create base document with frontmatter
/md-create-from-data base.json document.md

# Add sections incrementally
cat > sections.json << 'EOF'
{
  "sections": [
    {"id": "intro", "content": "# Introduction\n\nOverview text."},
    {"id": "methods", "content": "# Methods\n\nMethodology description."}
  ]
}
EOF

mddata write --data sections.json document.md --output document.md

# Add nested subsections
cat > subsections.json << 'EOF'
{
  "sections": [
    {"id": "methods.data_collection", "content": "## Data Collection\n\nHow data was gathered."},
    {"id": "methods.analysis", "content": "## Analysis\n\nAnalytical approach."}
  ]
}
EOF

mddata write --data subsections.json document.md --output document.md
```

**Template with Parameters:**

```bash
# Direct parameters
mddata write --data template.yaml --output output.md \
  -p title="My Document" \
  -p author="John Doe" \
  -p tags='["important", "draft"]'

# Load parameters from file
mddata write --data template.yaml --params params.json --output output.md

# Parameter from file content
mddata write --data template.yaml --output output.md \
  -p title="My Doc" \
  -p content=@content.txt

# Interactive parameter input
mddata write --data template.yaml --output output.md \
  -p title="My Doc" \
  -p description=-
```

**With Schema Validation:**

```bash
# Validate data against schema while writing
mddata write --data data.json --schema schema.json --output output.md
```

**From Schema Template:**

```bash
# Create empty template from schema
mddata write --schema schema.json --output template.md
```

**Preview Without Saving:**

```bash
# Print to stdout (no --output)
mddata write --data data.json
```

---

## Parameter Sources

When using templates, parameters are resolved in order of precedence:

1. **CLI parameters** (`-p key=value`) - highest precedence
2. **Parameter file** (`--params file.json`) - medium precedence
3. **Template defaults** - lower precedence
4. **Computed parameters** - lowest precedence

**Parameter Value Formats:**
- `key=value`: Direct string value
- `key=@file.txt`: Load value from file
- `key=-`: Interactive input from terminal
- `key=@-`: Load value from piped stdin

**Computed Parameters:**
- `{date}`: Current date (YYYY-MM-DD)
- `{time}`: Current time (HH:MM:SS)
- `{now}`: Current datetime (ISO 8601)
- `{env.VAR_NAME}`: Environment variable value

---

## Advanced Workflows

**Extract and Recreate:**

Round-trip existing document:
```bash
mddata extract json existing.md --output data.json
mddata write --data data.json --output new.md
```

**Batch Generation with Templates:**

Generate multiple documents from a template with different parameters:
```bash
# Create template once
cat > doc-template.yaml << 'EOF'
parameters:
  title: {type: str, required: true}
  author: {type: str, default: "Anonymous"}
changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    date: "{date}"
  sections:
    - id: "content"
      content: "# {title}\n\nBy {author}"
EOF

# Generate multiple documents
for name in "Report-A" "Report-B" "Report-C"; do
  mddata write --data doc-template.yaml \
    -p title="$name" \
    -p author="Team Lead" \
    --output "docs/${name}.md"
done
```

**Incremental Document Creation:**

Create documents in stages using the `modify from-data` structure:

```bash
# Step 1: Create initial document with frontmatter only
cat > initial.json << 'EOF'
{
  "frontmatter": {
    "title": "Project Report",
    "author": "Team Lead",
    "date": "2025-10-25",
    "status": "draft"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "blocks": [],
    "children": []
  }
}
EOF

mddata write --data initial.json --output report.md

# Step 2: Add sections incrementally using write command
cat > sections.json << 'EOF'
{
  "sections": [
    {
      "id": "executive_summary",
      "content": "# Executive Summary\n\nKey findings and recommendations.",
      "policy": "update"
    },
    {
      "id": "methodology",
      "content": "# Methodology\n\nResearch approach and data collection.",
      "policy": "update"
    },
    {
      "id": "results",
      "content": "# Results\n\nDetailed analysis and findings.",
      "policy": "update"
    }
  ]
}
EOF

mddata write --data sections.json report.md --output report.md

# Step 3: Add subsections to existing sections
cat > subsections.json << 'EOF'
{
  "sections": [
    {
      "id": "results.data_analysis",
      "content": "## Data Analysis\n\nStatistical findings.",
      "policy": "update"
    },
    {
      "id": "results.interpretation",
      "content": "## Interpretation\n\nKey insights from the data.",
      "policy": "update"
    }
  ]
}
EOF

mddata write --data subsections.json report.md --output report.md

# Verify the final structure
mddata info sections report.md --blocks
```

**Write Command Modes:**

- Use `mddata write --data <file> --output <new.md>` to **create new** documents from complete data or templates
- Use `mddata write --data <changes.json> <existing.md>` to **update existing** documents or **add sections incrementally**

```bash
# Create complete document at once
mddata write --data complete-data.json --output new.md

# Create base document, then add sections
mddata write --data base.json --output new.md
mddata write --data sections.json new.md --output new.md

# Update existing document with template
mddata write --data template.yaml existing.md --output existing.md -p title="Updated"
```
