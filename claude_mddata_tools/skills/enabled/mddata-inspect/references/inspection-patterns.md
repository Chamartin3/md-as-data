# Mddata Inspection Patterns

This reference provides common inspection patterns and command examples for efficiently querying markdown documents with minimal context usage.

## Core Inspection Commands

### Document Overview
```bash
# Get quick summary of file structure
mddata info summary <file.md>
mddata info summary <file.md> --verbose

# Multi-file inspection
mddata info summary doc1.md doc2.md doc3.md
```

### Section Structure
```bash
# View all sections with hierarchy
mddata info sections <file.md>

# Include full paths for precise targeting
mddata info sections <file.md> --paths

# Show block counts per section
mddata info sections <file.md> --blocks
```

### Frontmatter Properties
```bash
# List all properties
mddata info properties <file.md>

# Detailed property information with types
mddata info properties <file.md> --verbose
```

### Content Blocks
```bash
# List all blocks with types
mddata info blocks <file.md>

# Filter by block type
mddata info blocks <file.md> --type paragraph
mddata info blocks <file.md> --type code_block
mddata info blocks <file.md> --type list
mddata info blocks <file.md> --type table

# Limit results
mddata info blocks <file.md> --limit 10
```

### Task Lists
```bash
# View all tasks in document
mddata info tasks <file.md>

# Tasks in specific section
mddata info tasks <file.md> --section "project_planning"
```

## Inspection Workflows

### 1. Understanding Unknown Document Structure

**Goal**: Learn what's in a document without reading it entirely.

**Steps**:
1. Get overview: `mddata info summary <file.md> --verbose`
2. Map sections: `mddata info sections <file.md> --paths --blocks`
3. Check properties: `mddata info properties <file.md>`
4. Identify content types: `mddata info blocks <file.md>`

**Output**: Complete understanding of document organization and metadata.

### 2. Locating Specific Information

**Goal**: Find where specific content exists in a document.

**Steps**:
1. Get section structure: `mddata info sections <file.md> --paths`
2. Search by content type:
   - Tables: `mddata info blocks <file.md> --type table`
   - Code: `mddata info blocks <file.md> --type code_block`
   - Lists: `mddata info blocks <file.md> --type list`
3. Use section paths to target specific areas
4. Extract only needed section: `mddata extract json <file.md>` (filter by section in JSON output)

**Output**: Precise location of content without loading full document.

### 3. Schema Discovery for Multiple Files

**Goal**: Understand common structure across multiple markdown files.

**Steps**:
1. Infer schema from directory: `mddata schema infer <directory/> --format yaml --output schema.yaml`
2. View schema structure: `mddata schema info schema.yaml`
3. Use schema to understand:
   - Common frontmatter properties
   - Typical section hierarchies
   - Required vs optional elements
   - Content patterns across files

**Output**: Structural patterns across document collection.

### 4. Targeted Content Extraction

**Goal**: Extract only specific information from a document.

**Steps**:
1. Locate content using info commands
2. Extract targeted data:
   - Properties only: `mddata extract frontmatter <file.md> --format json`
   - Specific section: Use `mddata extract json <file.md>` and filter sections array
   - Full structure: `mddata extract json <file.md> --pretty`

**Output**: Minimal data extraction with precise targeting.

## Command Combinations

### Finding Tables in Specific Sections
```bash
# Step 1: See section structure
mddata info sections document.md --paths

# Step 2: Identify sections with blocks
mddata info sections document.md --blocks

# Step 3: Find all tables
mddata info blocks document.md --type table

# Step 4: Extract section with table (use JSON filtering)
mddata extract json document.md --pretty
```

### Comparing Document Structures
```bash
# Generate schemas for comparison
mddata schema infer doc1.md --format yaml --output doc1-schema.yaml
mddata schema infer doc2.md --format yaml --output doc2-schema.yaml

# View each schema
mddata schema info doc1-schema.yaml
mddata schema info doc2-schema.yaml

# Compare manually or use diff tools
```

### Batch Document Analysis
```bash
# Infer schema from entire directory
mddata schema infer ./documents/ --format yaml --output collection-schema.yaml

# View aggregated structure
mddata schema info collection-schema.yaml

# Validate individual docs against common schema
mddata schema validate doc1.md collection-schema.yaml
mddata schema validate doc2.md collection-schema.yaml
```

## Efficiency Tips

1. **Always start with info commands** - Never read full file until you know where to look
2. **Use --paths flag** - Shows exact section identifiers for targeting
3. **Use --blocks flag** - Shows content density per section
4. **Filter early** - Use --type and --limit to reduce output
5. **Schema first for directories** - Understand patterns before diving into individual files
6. **Extract to JSON** - Structured data is easier to filter programmatically than reading markdown

## Block Types Reference

Available block types for filtering:
- `paragraph` - Regular text paragraphs
- `heading` - Section headings
- `list` - Bulleted or numbered lists
- `code_block` - Fenced code blocks
- `blockquote` - Quoted text
- `table` - Tables
- `thematic_break` - Horizontal rules
- `html_block` - Raw HTML blocks

## Common Patterns by Use Case

### Documentation Navigation
```bash
mddata info sections <file.md> --paths --blocks
mddata info properties <file.md>
```

### Data Location
```bash
mddata info blocks <file.md> --type table
mddata info blocks <file.md> --type code_block
```

### Metadata Inspection
```bash
mddata info properties <file.md> --verbose
mddata extract frontmatter <file.md> --format json
```

### Structure Analysis
```bash
mddata schema infer <file-or-directory> --format yaml --output schema.yaml
mddata schema info schema.yaml
```

### Task Management
```bash
mddata info tasks <file.md>
mddata info tasks <file.md> --section "sprint_planning"
```
