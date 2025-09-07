# Command-Line Interface

This document describes the command-line interface (CLI) for the markdown-as-data library.

## Installation

The CLI is available after installing the library:

```bash
# Clone and install with uv (recommended)
git clone <repository-url>
cd mdasdata
uv sync --dev
```

## Usage

Access the CLI through uv:

```bash
uv run mdasdata [COMMAND] [OPTIONS]
```

---

## Commands

### parse

Parse markdown file and output structured JSON.

```bash
uv run mdasdata parse [OPTIONS] FILE
```

**Arguments:**
- `FILE`: Path to markdown file (required)

**Options:**
- `--pretty, -p`: Pretty print JSON with syntax highlighting
- `--output, -o PATH`: Output file path (default: stdout)
- `--frontmatter`: Extract only frontmatter properties
- `--sections`: Extract only section structure

**Examples:**

```bash
# Basic parsing - outputs complete document structure
uv run mdasdata parse document.md

# Pretty printed output with syntax highlighting
uv run mdasdata parse document.md --pretty

# Save output to file
uv run mdasdata parse document.md --output result.json

# Extract frontmatter only
uv run mdasdata parse document.md --frontmatter

# Extract sections only (structure without frontmatter)
uv run mdasdata parse document.md --sections
```

**Output Formats:**

1. **Complete Document** (default):
   ```json
   {
     "frontmatter": {
       "title": "My Document",
       "author": "John Doe"
     },
     "content": {
       "id": "",
       "title": "",
       "level": 0,
       "path": "",
       "blocks": [],
       "subsections": [...]
     }
   }
   ```

2. **Frontmatter Only** (`--frontmatter`):
   ```json
   {
     "title": "My Document",
     "author": "John Doe",
     "tags": ["example", "documentation"]
   }
   ```

3. **Sections Only** (`--sections`):
   ```json
   {
     "sections": [...],
     "sections_by_id": {...}
   }
   ```

---

### info

Display summary information about a markdown file.

```bash
uv run mdasdata info [OPTIONS] FILE
```

**Arguments:**
- `FILE`: Path to markdown file (required)

**Example:**
```bash
uv run mdasdata info document.md
```

**Sample Output:**
```
File: document.md
Frontmatter properties: 4
  • title: My Document
  • author: John Doe
  • date: 2024-01-15
  • tags: ['example', 'documentation']
Sections: 5
Total blocks: 12
Block types:
  • paragraph: 8
  • code_block: 2
  • list: 2
```

**Information Displayed:**
- File path
- Number of frontmatter properties
- First 5 frontmatter key-value pairs (truncated if values are long)
- Total number of sections
- Total number of blocks
- Block type distribution (most common first)

---

## Global Options

### Help

Get help for any command:

```bash
uv run mdasdata --help              # General help
uv run mdasdata parse --help        # Command-specific help
uv run mdasdata info --help         # Command-specific help
```

---

## Integration Examples

### Shell Scripting

Process multiple files:
```bash
# Process all markdown files in a directory
for file in docs/*.md; do
  echo "Processing $file"
  uv run mdasdata parse "$file" > "json/$(basename "$file" .md).json"
done
```

### With jq for Data Processing

Extract specific information using jq:
```bash
# Count sections in a document
uv run mdasdata parse doc.md --sections | jq '.sections | length'

# Extract all section titles
uv run mdasdata parse doc.md --sections | jq -r '.sections[].title'

# Get document metadata
uv run mdasdata parse doc.md --frontmatter | jq -r '.title, .author, .date'

# Find all documents with specific tag
find docs -name "*.md" -exec uv run mdasdata parse {} --frontmatter \; | jq -s 'map(select(.tags // [] | contains(["python"])))'
```

### Batch Processing

Extract frontmatter from multiple documents:
```bash
# Combine frontmatter from multiple files
uv run mdasdata parse *.md --frontmatter | jq -s '.'
```

Export content for migration:
```bash
# Extract structured content for system migration
uv run mdasdata parse legacy-doc.md --sections > content-export.json
```

---

## Error Handling

The CLI provides clear error messages for common issues:

- **File not found**: `Error: File 'document.md' not found`
- **Invalid file path**: Path validation with helpful suggestions
- **Parsing errors**: Detailed error messages with line numbers when possible
- **Permission errors**: Clear indication of file access issues

Exit codes:
- `0`: Success
- `1`: Error occurred

---

## Performance Notes

- Large files (>10MB) may take several seconds to process
- Pretty printing (`--pretty`) adds minimal overhead
- JSON output is optimized for streaming and can handle large documents
- Memory usage scales with document complexity (sections and blocks)

This CLI interface provides quick access to markdown parsing and analysis capabilities without requiring Python programming knowledge.