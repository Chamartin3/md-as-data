---
description: Prepare for mddata CLI usage by checking installation and understanding data formats
argument-hint: [optional-file]
allowed-tools: Bash(mddata:*), Bash(echo:*), Bash(cat:*), Bash(head:*), Read
---

# Prepare for mddata Usage

Check mddata installation, understand command parameters, and learn data format basics.

## 1. Check mddata Installation

Verify that mddata is installed and accessible:

```bash
echo "=== mddata Installation Check ==="
if command -v mddata &> /dev/null; then
  echo "✓ mddata command found"
  echo ""
  mddata --version 2>&1 || echo "mddata CLI installed"
  echo ""
  echo "✓ Ready to use mddata commands"
else
  echo "✗ mddata command not found"
  echo ""
  echo "Install with: uv pip install -e /path/to/mdasdata"
  exit 1
fi
```

## 2. Understanding Data Formats

mddata works with three main data structures:

### Schema Files (for templates and validation)

**Identify by:**
- File extension: `.json`, `.yaml`, or `.yml`
- Top-level keys: `frontmatter`, `sections`, `validation_level`
- Property definitions with `type`, `required`, `validations` fields

**Schema structure:**
```json
{
  "frontmatter": {
    "title": {"type": "str", "required": true},
    "status": {"type": "str", "enum": ["draft", "published"]}
  },
  "sections": {
    "introduction": {"validation": {"required": true}}
  },
  "validation_level": "warnings"
}
```

**Use with commands:**
- `mddata render --schema schema.json --output template.md`
- `mddata schema validate document.md schema.json`
- `mddata schema info schema.json`

### MarkdownDataDict (for generation and modification)

**Identify by:**
- File extension: `.json` or `.yaml`
- Top-level keys: `frontmatter` and `content`
- The `content` key contains a `tree` with sections

**MarkdownDataDict structure:**
```json
{
  "frontmatter": {
    "title": "My Document",
    "author": "John Doe"
  },
  "content": {
    "tree": {
      "sections": [
        {
          "id": "introduction",
          "title": "Introduction",
          "level": 2,
          "blocks": [{"type": "paragraph", "content": "..."}]
        }
      ]
    }
  }
}
```

**Use with commands:**
- `mddata render --data data.json --output document.md`
- `mddata modify from-json document.md data.json`
- `mddata extract json document.md --output data.json`

### Markdown Files (source documents)

**Identify by:**
- File extension: `.md`
- Contains frontmatter (YAML between `---` markers) and markdown content

**Use with all commands:**
- `mddata info sections document.md`
- `mddata modify set-property document.md title "New Title"`
- `mddata extract json document.md`
- `mddata schema infer document.md`

## 3. Quick Reference

**Inspect a file (if provided):**

```bash
if [ -n "$1" ] && [ -f "$1" ]; then
  echo ""
  echo "=== File Inspection: $1 ==="

  ext="${1##*.}"
  echo "Extension: .$ext"

  if [[ "$ext" == "md" ]]; then
    echo "Type: Markdown document"
    echo ""
    echo "Available commands:"
    echo "  mddata info sections $1"
    echo "  mddata extract json $1"
    echo "  mddata schema infer $1"
  elif [[ "$ext" == "json" || "$ext" == "yaml" || "$ext" == "yml" ]]; then
    echo "Type: Data file (schema or MarkdownDataDict)"
    echo ""
    echo "First few lines:"
    head -10 "$1"
    echo ""
    echo "To determine type, check for:"
    echo "  - Schema: 'type', 'required', 'validations' fields"
    echo "  - MarkdownDataDict: 'frontmatter' and 'content.tree' structure"
  fi
fi
```

## 4. Common Workflows

**Generate markdown from data:**
```bash
mddata render --data data.json --output document.md
```

**Create template from schema:**
```bash
mddata render --schema schema.json --output template.md
```

**Extract document to data:**
```bash
mddata extract json document.md --output data.json
```

**Generate schema from document:**
```bash
mddata schema infer document.md --output schema.json
```

**Validate document against schema:**
```bash
mddata schema validate document.md schema.json
```

---

## Usage Examples

**Check installation:**
```
/mddata-tools:md-prepare
```

**Inspect a file to understand its type:**
```
/mddata-tools:md-prepare schema.json
/mddata-tools:md-prepare data.yaml
/mddata-tools:md-prepare document.md
```

## Key Differences Between Data Types

| Feature | Schema | MarkdownDataDict | Markdown File |
|---------|--------|------------------|---------------|
| **Purpose** | Define structure & validation | Represent document data | Source document |
| **Format** | JSON/YAML | JSON/YAML | Markdown |
| **Structure** | Property definitions | Frontmatter + content tree | Frontmatter + sections |
| **Has `type` field** | Yes | No | N/A |
| **Has `content.tree`** | No | Yes | N/A |
| **Use for** | Validation, templates | Generation, modification | All operations |

## Tips

- **Schema files** define what a document *should* look like
- **MarkdownDataDict files** represent what a document *does* look like
- **Markdown files** are the actual documents you work with
- Use `mddata schema info` to inspect schemas
- Use `head` or `cat` to inspect data files
- Use `mddata info` commands to inspect markdown documents
