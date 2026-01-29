---
name: md-query
description: Extract and analyze metadata from markdown files including frontmatter properties, document structure, sections, and content blocks. Use when users ask to inspect markdown files, check properties, view document structure, analyze sections, or query markdown metadata.
allowed-tools: Bash(mddata:*), Read
---

# Markdown Query Skill

## Purpose

Query and inspect markdown files as structured data using the mddata tool. Extract frontmatter, view sections, analyze blocks, and inspect document structure without modifying files.

## Prerequisites

- `mddata` command available in the project (installed via `mddata`)
- Markdown files with optional YAML frontmatter

## Instructions

### 1. Quick Document Summary

Get an overview of a markdown document:

```bash
mddata info summary document.md
mddata info summary document.md --verbose  # Detailed view
```

### 2. List Frontmatter Properties

View all frontmatter properties and their values:

```bash
mddata info properties document.md
mddata info properties document.md --verbose  # With types
```

### 3. View Document Sections

Display section hierarchy and structure:

```bash
mddata info sections document.md
mddata info sections document.md --blocks  # Include block counts
mddata info sections document.md --paths   # Show full paths
```

### 4. List Content Blocks

View all content blocks with filtering:

```bash
mddata info blocks document.md
mddata info blocks document.md --type paragraph
mddata info blocks document.md --type code_block --limit 5
```

**Available block types:**
- `paragraph` - Text paragraphs
- `heading` - Section headings
- `code_block` - Code blocks
- `list` - Unordered/ordered lists
- `blockquote` - Quoted text
- `horizontal_rule` - Horizontal dividers

### 5. View Task Lists

Display task items from markdown checklists:

```bash
mddata info tasks document.md
mddata info tasks document.md --section "sprint_planning"
mddata info tasks document.md --completed  # Only completed tasks
mddata info tasks document.md --pending    # Only pending tasks
```

## Usage Examples

### Example 1: Quick Inspection

```
User: "What's in this document.md file?"

1. Run: mddata info summary document.md --verbose
2. Analyze output for:
   - Title and key frontmatter
   - Number of sections
   - Content overview
3. Present structured summary to user
```

### Example 2: Property Check

```
User: "Does this markdown file have a 'status' property?"

1. Run: mddata info properties document.md --verbose
2. Check output for 'status' property
3. Report presence and value
```

### Example 3: Section Analysis

```
User: "Show me the structure of sections in this document"

1. Run: mddata info sections document.md --paths --blocks
2. Display hierarchy with:
   - Section names and paths
   - Block counts per section
   - Nesting levels
```

### Example 4: Content Extraction

```
User: "Find all code blocks in the tutorial.md file"

1. Run: mddata info blocks tutorial.md --type code_block
2. List code blocks with:
 r - Section location
   - Code content preview
   - Language (if specified)
```

## Output Interpretation

### Summary Output
- Document title and frontmatter overview
- Total sections and subsections
- Total blocks by type
- Overall structure

### Properties Output
- Property names and values
- Data types (with --verbose)
- Nested structures displayed as JSON

### Sections Output
- Hierarchical tree view
- Section IDs and titles
- Full paths (with --paths)
- Block counts (with --blocks)

### Blocks Output
- Block type and content
- Parent section
- Position in document
- Filterable by type

## Best Practices

1. **Start with Summary**: Use `info summary` first for document overview
2. **Use Verbose Mode**: Add `--verbose` for detailed information
3. **Filter Wisely**: Use type filters and limits for large documents
4. **Check Paths**: Use `--paths` to understand section hierarchy
5. **Read-Only**: This skill never modifies files, safe for inspection

## Error Handling

- If file doesn't exist, report file not found
- If frontmatter is invalid, report parsing error
- If no sections/blocks found, report empty document
- For mddata errors, check file format and syntax

## Advanced Research and Extraction

For complex document research and data extraction workflows, see:

- **[Complex Research Examples](./complex-research-examples.md)** - Advanced techniques for analyzing markdown structure
  - Document structure analysis
  - Content discovery workflows
  - Multi-document analysis
  - Quality assurance checks
  - Documentation auditing
  - 20+ comprehensive examples

- **[Extraction Examples](./extraction-examples.md)** - Practical extraction workflows
  - Basic and selective extraction
  - Data transformation pipelines
  - Integration with external tools
  - Format conversion examples
  - 20+ real-world scenarios

These references provide detailed examples for:
- Finding documentation gaps
- Analyzing code example distribution
- Task management tracking
- Building documentation metrics
- Cross-document comparison
- Extracting structured data for databases
- Creating search indexes
- Generating analytics reports
