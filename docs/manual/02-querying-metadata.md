# Querying Metadata

## Overview

The `mddata info` command provides various ways to inspect and query the structure of markdown documents. This is useful for understanding document organization, finding specific content, and debugging issues.

## Command Structure

```bash
mddata info <subcommand> <file_path> [options]
```

All info commands are read-only and do not modify the source file.

## Subcommands

### Summary - Quick Document Overview

Display a concise summary of the document structure:

```bash
mddata info summary document.md
```

**Example output:**
```
Document Summary: document.md
├─ Frontmatter Properties: 4
│  ├─ title: "API Documentation"
│  ├─ version: 2.1
│  ├─ status: "published"
│  └─ tags: ["api", "reference"]
├─ Sections: 5
└─ Blocks: 12
```

**Verbose mode** shows additional details:

```bash
mddata info summary document.md --verbose
```

```
Document Summary: document.md
├─ Frontmatter Properties: 4
│  ├─ title: "API Documentation" (type: str)
│  ├─ version: 2.1 (type: int)
│  ├─ status: "published" (type: str)
│  └─ tags: ["api", "reference"] (type: list, length: 2)
├─ Sections: 5
│  ├─ introduction (level: 1, blocks: 2, subsections: 1)
│  ├─ introduction.overview (level: 2, blocks: 2)
│  ├─ authentication (level: 1, blocks: 2)
│  ├─ endpoints (level: 1, blocks: 1, subsections: 1)
│  └─ endpoints.users_api (level: 2, blocks: 1)
└─ Total Blocks: 12
   ├─ paragraph: 7
   ├─ list: 1
   ├─ code_block: 1
   └─ heading: 5
```

### Properties - List Frontmatter

Display all frontmatter properties:

```bash
mddata info properties document.md
```

**Example output:**
```
Frontmatter Properties:
  title: "API Documentation"
  version: 2.1
  status: "published"
  tags: ["api", "reference"]
```

**Verbose mode** includes type information:

```bash
mddata info properties document.md --verbose
```

```
Frontmatter Properties (4 total):
  title: "API Documentation"
    Type: str
    Length: 18 characters

  version: 2.1
    Type: float

  status: "published"
    Type: str
    Enum-like: true (single word)

  tags: ["api", "reference"]
    Type: list
    Length: 2 items
    Item types: str
```

### Sections - Document Hierarchy

Display the section structure:

```bash
mddata info sections document.md
```

**Example output:**
```
Document Sections:
introduction
  overview
authentication
endpoints
  users_api
```

**Show section paths:**

```bash
mddata info sections document.md --paths
```

```
Document Sections:
introduction
  introduction.overview
authentication
endpoints
  endpoints.users_api
```

**Include block counts:**

```bash
mddata info sections document.md --blocks
```

```
Document Sections:
introduction (2 blocks)
  overview (2 blocks)
authentication (2 blocks)
endpoints (1 block)
  users_api (1 block)
```

**Combine options:**

```bash
mddata info sections document.md --paths --blocks
```

```
Document Sections:
introduction (2 blocks)
  introduction.overview (2 blocks)
authentication (2 blocks)
endpoints (1 block)
  endpoints.users_api (1 block)
```

### Blocks - Content Units

List all content blocks in the document:

```bash
mddata info blocks document.md
```

**Example output:**
```
Blocks (12 total):

Section: introduction
  [1] paragraph (45 chars)
      "Welcome to the API documentation. This..."

  [2] heading (level: 2)
      "Overview"

Section: introduction.overview
  [3] paragraph (38 chars)
      "The API provides RESTful endpoints..."

  [4] list (3 items)
      "- Feature 1\n- Feature 2\n- Feature 3"

Section: authentication
  [5] paragraph (35 chars)
      "All requests require an API key."

  [6] code_block (language: python, 3 lines)
      "import requests\nheaders = {...}"

... (more blocks)
```

**Filter by block type:**

```bash
mddata info blocks document.md --type paragraph
```

```
Paragraph Blocks (7 total):

Section: introduction
  [1] paragraph (45 chars)
      "Welcome to the API documentation. This..."

Section: introduction.overview
  [3] paragraph (38 chars)
      "The API provides RESTful endpoints..."

... (more paragraphs)
```

**Available block types:**
- `paragraph` - Text paragraphs
- `heading` - Section headings
- `list` - Lists (ordered/unordered)
- `code_block` - Code blocks
- `blockquote` - Quoted text
- `thematic_break` - Horizontal rules
- `html_block` - Raw HTML

**Limit results:**

```bash
mddata info blocks document.md --limit 5
```

```
Blocks (showing first 5 of 12 total):

Section: introduction
  [1] paragraph (45 chars)
      "Welcome to the API documentation. This..."

  [2] heading (level: 2)
      "Overview"

... (3 more blocks)
```

**Combine filters:**

```bash
mddata info blocks document.md --type code_block --limit 3
```

### Tasks - Task List Items

Display task lists found in the document:

```bash
mddata info tasks document.md
```

**Example document with tasks:**
```markdown
# Sprint Planning

- [x] Design API endpoints
- [ ] Implement authentication
- [ ] Write documentation

## Testing

- [ ] Unit tests
- [ ] Integration tests
```

**Command output:**
```
Task Lists:

Section: sprint_planning (3 tasks, 1 completed)
  [x] Design API endpoints
  [ ] Implement authentication
  [ ] Write documentation

Section: sprint_planning.testing (2 tasks, 0 completed)
  [ ] Unit tests
  [ ] Integration tests

Summary: 5 total tasks, 1 completed (20%)
```

**Filter by section:**

```bash
mddata info tasks document.md --section sprint_planning
```

```
Task Lists in section 'sprint_planning':

Section: sprint_planning (3 tasks, 1 completed)
  [x] Design API endpoints
  [ ] Implement authentication
  [ ] Write documentation

Summary: 3 total tasks, 1 completed (33%)
```

## Understanding Section IDs

Section IDs are generated from heading text and follow these rules:

### ID Generation Rules

1. **Lowercase conversion**: "Getting Started" → "getting started"
2. **Space to underscore**: "getting started" → "getting_started"
3. **Special characters removed**: "API v2.0!" → "api_v2_0"
4. **Multiple spaces collapsed**: "Hello    World" → "hello_world"

### Examples

| Heading Text | Section ID |
|--------------|------------|
| Introduction | `introduction` |
| Getting Started | `getting_started` |
| API Reference | `api_reference` |
| v2.0 Features | `v2_0_features` |
| FAQ & Support | `faq_support` |

### Path Notation

Nested sections use dot-separated paths:

```markdown
# Introduction          → introduction
## Overview            → introduction.overview
### Quick Start        → introduction.overview.quick_start
# Configuration        → configuration
## Database Setup      → configuration.database_setup
```

**Access patterns:**
```bash
# Top-level section
mddata info blocks document.md --section introduction

# Nested section (full path)
mddata info blocks document.md --section introduction.overview

# Deeply nested section
mddata info blocks document.md --section introduction.overview.quick_start
```

## Practical Examples

### Find all code examples

```bash
mddata info blocks document.md --type code_block
```

### Check document completeness

```bash
mddata info summary document.md --verbose
```

Look for sections with 0 blocks or missing required properties.

### Analyze task progress

```bash
mddata info tasks project_plan.md
```

### Export section structure for documentation

```bash
mddata info sections document.md --paths --blocks > structure.txt
```

### Inspect specific content areas

```bash
mddata info blocks document.md --section authentication
```

### Find all headings

```bash
mddata info blocks document.md --type heading
```

## Common Use Cases

### 1. Document Review

Before modifying a document, review its structure:

```bash
# Get overview
mddata info summary document.md

# Check sections
mddata info sections document.md --blocks

# Review properties
mddata info properties document.md --verbose
```

### 2. Content Audit

Find documents missing required content:

```bash
# Check if introduction exists
mddata info sections document.md | grep introduction

# Count code examples
mddata info blocks document.md --type code_block | head -1
```

### 3. Task Tracking

Monitor project task completion:

```bash
# Overall progress
mddata info tasks project.md

# Specific section progress
mddata info tasks project.md --section sprint_1
```

### 4. Documentation Quality

Verify documentation standards:

```bash
# Ensure all sections have content
mddata info sections document.md --blocks

# Check for required properties
mddata info properties document.md | grep -E "(author|version|status)"
```

## Next Steps

- [Extract data to JSON/YAML](03-extracting-metadata.md) - Export structured data
- [Validate document structure](04-schema-management.md) - Enforce standards
- [Modify document content](06-data-transformation.md) - Make changes programmatically
