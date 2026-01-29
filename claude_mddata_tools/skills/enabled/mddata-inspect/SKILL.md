---
name: mddata-inspect
description: Efficiently inspect and query markdown document structure using mddata CLI commands with minimal context usage. Use when needing to understand document organization, locate specific content, discover frontmatter properties, map section hierarchies, or find where information exists in markdown files without reading entire documents into context. Ideal for navigating large documents, batch document analysis, and targeted information extraction.
---

# Mddata Inspect

## Overview

Inspect markdown documents efficiently by querying their structure, properties, and content organization using mddata CLI commands. This approach minimizes context usage by understanding document organization before reading any content.

**Core principle**: Always query structure first, locate content second, extract only what's needed third.

## When to Use This Skill

Invoke this skill when:
- Understanding the structure of unfamiliar markdown documents
- Locating specific information within large documents
- Discovering what frontmatter properties exist
- Mapping section hierarchies and organization
- Finding where specific content types (tables, code blocks, lists) are located
- Analyzing patterns across multiple markdown files
- Navigating documents without loading full content into context

## Inspection Workflow

Follow this decision tree for efficient document inspection:

```
User query about markdown file(s)
    │
    ├─ Unknown structure?
    │   └─> Start with Document Discovery (§1)
    │
    ├─ Need to find specific content?
    │   └─> Use Content Location (§2)
    │
    ├─ Multiple files?
    │   └─> Use Schema Discovery (§3)
    │
    └─ Need to extract data?
        └─> Use Targeted Extraction (§4)
```

### 1. Document Discovery

**Goal**: Understand document structure without reading the full file.

**Commands**:
```bash
# Step 1: Get overview
mddata info summary <file.md> --verbose

# Step 2: Map section hierarchy
mddata info sections <file.md> --paths --blocks

# Step 3: Check frontmatter
mddata info properties <file.md>

# Step 4: Identify content types
mddata info blocks <file.md>
```

**Output**: Complete structural understanding showing:
- Frontmatter properties and their types
- Section hierarchy with full paths
- Block counts per section
- Content type distribution

**Example**:
```
User: "What's in the project-plan.md file?"

Response:
- Run info summary to show document metadata
- Run info sections --paths --blocks to show organization
- Run info properties to show frontmatter
- Summarize findings without reading full content
```

### 2. Content Location

**Goal**: Find where specific information exists in a document.

**Strategy**:
1. Identify what type of content to find (table, code, list, etc.)
2. Use appropriate block type filter
3. Correlate with section structure
4. Report precise location without reading full sections

**Commands**:
```bash
# Find tables
mddata info blocks <file.md> --type table

# Find code blocks
mddata info blocks <file.md> --type code_block

# Find lists
mddata info blocks <file.md> --type list

# Map to sections
mddata info sections <file.md> --paths --blocks
```

**Block types available**: paragraph, heading, list, code_block, blockquote, table, thematic_break, html_block

**Example**:
```
User: "Where are the budget tables in the Q4-report.md?"

Response:
1. Run info blocks Q4-report.md --type table
2. Run info sections Q4-report.md --paths --blocks
3. Correlate block locations with section paths
4. Report: "Budget tables found in sections: financial.q4_budget and appendix.detailed_breakdown"
```

### 3. Schema Discovery

**Goal**: Understand structure patterns across multiple files or directories.

**Commands**:
```bash
# Infer schema from single file
mddata schema infer <file.md> --format yaml --output schema.yaml

# Infer schema from directory (recursive)
mddata schema infer <directory/> --format yaml --output schema.yaml

# View schema structure
mddata schema info schema.yaml

# Validate files against schema
mddata schema validate <file.md> schema.yaml
```

**Schema reveals**:
- Common frontmatter properties
- Typical section hierarchies
- Required vs optional elements
- Content patterns across files

**Example**:
```
User: "What's the common structure of documents in the ./docs/ folder?"

Response:
1. Run schema infer ./docs/ --format yaml --output docs-schema.yaml
2. Run schema info docs-schema.yaml
3. Summarize common patterns:
   - "All documents have 'title' and 'author' properties"
   - "Typical sections: introduction, methodology, results, conclusions"
   - "Tables appear primarily in 'results' sections"
```

### 4. Targeted Extraction

**Goal**: Extract only specific information, not entire document.

**Commands**:
```bash
# Extract frontmatter only
mddata extract frontmatter <file.md> --format json
mddata extract frontmatter <file.md> --format yaml

# Extract full structure (filter programmatically)
mddata extract json <file.md> --pretty

# Extract to YAML
mddata extract yaml <file.md>
```

**Strategy**:
1. Use info commands to locate what's needed
2. Extract minimal data structure
3. Filter the extracted JSON/YAML programmatically if needed
4. Avoid reading full markdown content

**Example**:
```
User: "Get me just the metadata from status-report.md"

Response:
1. Run extract frontmatter status-report.md --format json
2. Present the properties without loading document content
```

## Advanced Patterns

### Multi-File Comparison
```bash
# Generate individual schemas
mddata schema infer doc1.md --format yaml --output doc1-schema.yaml
mddata schema infer doc2.md --format yaml --output doc2-schema.yaml

# View each for manual comparison
mddata schema info doc1-schema.yaml
mddata schema info doc2-schema.yaml
```

### Batch Analysis
```bash
# Create collection schema
mddata schema infer ./collection/ --format yaml --output collection-schema.yaml

# Validate each file against pattern
mddata schema validate file1.md collection-schema.yaml
mddata schema validate file2.md collection-schema.yaml --verbose
```

### Section-Specific Inspection
```bash
# Find sections with most content
mddata info sections <file.md> --blocks

# Identify sparse sections (candidates for expansion)
# Use block counts from previous command
```

## Efficiency Guidelines

**Always follow this order**:
1. **Query structure** - Use info commands to understand organization
2. **Locate precisely** - Use block filters and section paths to pinpoint content
3. **Extract minimally** - Only read or extract what's absolutely needed

**Never**:
- Read full file before understanding structure
- Extract entire document when only properties needed
- Load content into context without knowing its location
- Skip the schema step when analyzing multiple files

**Command selection**:
- Unknown structure → `info summary` + `info sections`
- Finding content → `info blocks --type <type>`
- Properties only → `info properties` or `extract frontmatter`
- Multiple files → `schema infer <directory/>`
- Need data structure → `extract json` (then filter)

## Output Format

When reporting findings to users:
1. State what commands were run (for transparency)
2. Summarize structural findings clearly
3. Provide precise locations (section paths) when relevant
4. Indicate if further inspection is needed
5. Avoid reading full content unless explicitly requested

**Example response format**:
```
Inspected document.md structure:

Frontmatter properties (5):
- title: "Project Overview"
- status: "draft"
- version: 2.3
- tags: ["planning", "architecture"]
- author: "team@example.com"

Section hierarchy (7 sections):
├─ introduction (3 blocks)
├─ architecture (12 blocks)
│  ├─ architecture.overview (4 blocks)
│  └─ architecture.components (8 blocks)
├─ implementation (15 blocks)
└─ conclusions (2 blocks)

Content analysis:
- 2 tables found in section: implementation
- 5 code blocks found in sections: architecture.components, implementation
- 32 total blocks across document

To extract specific content, please specify which section or content type you need.
```

## Reference Material

For detailed command examples and patterns, see `references/inspection-patterns.md` which includes:
- Complete command reference with examples
- Common inspection workflows
- Block type reference
- Efficiency tips and best practices
- Command combinations for complex queries

Load this reference when encountering complex inspection scenarios or needing detailed command syntax.
