# Core Domain API Reference

## Overview

The core domain layer (`src/mddata/`) provides a clean, pythonic API for treating markdown files as structured data objects. This document defines the public API, entry points, and interaction patterns.

## Table of Contents

1. [Entry Points](#entry-points)
2. [Primary Interfaces](#primary-interfaces)
3. [Data Access Patterns](#data-access-patterns)
4. [Mutation Patterns](#mutation-patterns)
5. [Query Patterns](#query-patterns)
6. [Extension Patterns](#extension-patterns)
7. [Complete Usage Examples](#complete-usage-examples)

---

## Entry Points

### 1. MarkdownFile - File-based Entry Point

**Purpose**: Load, manipulate, and save markdown files

**Location**: `src/mddata/source.py`

**Public API**:

```python
from mddata import MarkdownFile

# Load from file
doc = MarkdownFile('path/to/document.md')

# Access document data interface
mddata = doc.mddata  # MarkdownData instance

# Serialization methods
json_str = doc.to_json()
markdown_str = doc.to_markdown()

# Save operations
doc.save()                    # Save to original path
doc.save('new/path.md')       # Save to new path
doc.save_as('backup.md')      # Alias for save(path)

# Create from dictionary
data = {"frontmatter": {...}, "content": {...}}
doc = MarkdownFile.from_dict(data, filepath='output.md')
```

**When to use**:
- Loading markdown files from disk
- Saving changes back to files
- Round-trip file operations

---

### 2. MarkdownData - Data Manipulation Entry Point

**Purpose**: Primary interface for document manipulation

**Location**: `src/mddata/data.py`

**Public API**:

```python
from mddata import MarkdownData

# Create from parsed data (usually from MarkdownFile)
doc = MarkdownFile('document.md').mddata

# Or create directly with schema validation
from mddata import generate_schema
schema = generate_schema(parsed_data)
doc = MarkdownData(parsed_data, schema=schema)
```

**When to use**:
- Programmatic document manipulation
- Dynamic property access
- Schema-validated mutations
- Query operations

---

### 3. MarkdownProcessor - Parsing Entry Point

**Purpose**: Parse and serialize markdown text

**Location**: `src/mddata/processor.py`

**Public API**:

```python
from mddata import MarkdownProcessor

processor = MarkdownProcessor()

# Parse markdown text to structured data
parsed_data = processor.parse(markdown_text)
# Returns: ParsedMarkdownData = {
#     "frontmatter": {...},
#     "content": ContentTree
# }

# Parse content to section
section = processor.parse_content_to_section(
    text="## Overview\n\nContent here",
    section_path="introduction.overview"
)

# Serialize data back to markdown
markdown_text = processor.serialize_document(data_dict)

# Register custom token handlers (extension point)
processor.register_handler(TokenType.CUSTOM, custom_handler)
```

**When to use**:
- Custom parsing workflows
- Programmatic document generation
- Registering custom markdown syntax handlers
- Working without file I/O

---

## Primary Interfaces

### MarkdownData Interface

**Complete Public API**:

```python
class MarkdownData:
    """Primary interface for document manipulation"""

    # === PROPERTIES ===

    @property
    def frontmatter -> FrontmatterProperties:
        """Access frontmatter dictionary"""

    @property
    def content -> ContentTree:
        """Access content tree structure"""

    @property
    def data -> ParsedMarkdownData:
        """Get complete document data"""

    # === DYNAMIC ACCESS ===

    def __getattr__(name: str) -> Any:
        """Dynamic access to frontmatter and sections"""
        # doc.title → frontmatter["title"]
        # doc.introduction → content.get_section("introduction")

    def __setattr__(name: str, value: Any) -> None:
        """Dynamic property setting with type inference"""
        # doc.title = "New Title" → sets frontmatter
        # doc.introduction = "Content" → sets section

    # === SECTION OPERATIONS ===

    def get_section(section_id_or_path: str) -> Section | None:
        """Get section by ID or dot-separated path"""

    def get_all_sections() -> list[Section]:
        """Get all sections in document"""

    def query_section(section_id: str) -> SectionQuery:
        """Comprehensive section query with validation"""
        # Returns: SectionQuery(section, matched, parent, error)

    def set_section(
        section_id: str,
        content: str,
        policy: SectionPolicy = SectionPolicy.UPDATE
    ) -> None:
        """High-level section setter with auto-heading generation"""

    def append_to_section(section_id: str, content: str) -> None:
        """Append content to section"""

    def replace_section(section_id: str, content: str) -> None:
        """Replace entire section content"""

    def update_section(section_id: str, content: str) -> None:
        """Update section (merge with existing)"""

    # === FRONTMATTER OPERATIONS ===

    def update_frontmatter(
        properties: dict[str, Any],
        policy: UpdatePolicy = UpdatePolicy.MERGE
    ) -> None:
        """Update multiple frontmatter properties"""

    # === QUERY OPERATIONS ===

    def get_sections() -> SectionsData:
        """Get all sections as structured data"""

    def get_blocks(section_id: str | None = None) -> BlocksData:
        """Get blocks from section or all sections"""

    def find_blocks(
        block_type: str | None = None,
        section_id: str | None = None
    ) -> BlocksQuery:
        """Find blocks with flexible filtering"""
        # Returns: BlocksQuery(blocks, total)

    # === TASK LIST OPERATIONS ===

    def get_task_lists(section_id: str | None = None) -> list[TaskList]:
        """Get TaskList objects for advanced operations"""

    def filter_tasks_by_symbol(
        symbol: str,
        section_id: str | None = None
    ) -> list[TaskItemData]:
        """Get tasks with specific symbol (x, !, ~, etc.)"""

    def get_completed_tasks(section_id: str | None = None) -> list[TaskItemData]:
        """Get all completed tasks (marked with 'x')"""

    def get_pending_tasks(section_id: str | None = None) -> list[TaskItemData]:
        """Get all pending tasks (marked with space)"""

    # === BATCH OPERATIONS ===

    def apply_batch_changes(changes: BatchChanges) -> BatchOperationResult:
        """Apply multiple changes from structured data"""

    # === SERIALIZATION ===

    def to_dict() -> MarkdownDataDict:
        """Convert to JSON-serializable dictionary"""
```

---

## Data Access Patterns

### 1. Frontmatter Access

```python
from mddata import MarkdownFile

doc = MarkdownFile('document.md').mddata

# Read frontmatter - Dynamic property access
title = doc.title                    # Returns: str | None
author = doc.author                  # Returns: str | None
tags = doc.tags                      # Returns: list[str] | None

# Read frontmatter - Dictionary access
frontmatter = doc.frontmatter
title = frontmatter.get('title')
all_keys = frontmatter.keys()

# Check if property exists
if 'status' in doc.frontmatter:
    status = doc.status
```

### 2. Section Access

```python
# Get section by ID
intro = doc.get_section('introduction')

# Get section by path
overview = doc.get_section('introduction.overview')

# Dynamic property access
intro = doc.introduction             # Section object or raises AttributeError

# Get all sections
sections = doc.get_all_sections()    # Returns: list[Section]

# Section properties
print(intro.id)          # "introduction"
print(intro.title)       # "Introduction"
print(intro.level)       # HeadingLevel.H1
print(intro.path)        # "introduction"
print(intro.blocks)      # list[Block]
print(intro.subsections) # list[Section]
```

### 3. Block Access

```python
# Get all blocks from a section
intro = doc.get_section('introduction')
blocks = intro.blocks

# Get blocks with filtering
paragraphs = doc.find_blocks(block_type='paragraph')
intro_paragraphs = doc.find_blocks(
    block_type='paragraph',
    section_id='introduction'
)

# Access block data
for block in paragraphs.blocks:
    print(f"Type: {block.type}")         # BlockType enum
    print(f"Content: {block.content}")   # str | list[str]
    print(f"Metadata: {block.metadata}") # dict[str, Any]
    print(f"Section: {block.section}")   # section_id
```

### 4. Comprehensive Query

```python
# Query with validation and ambiguity detection
query = doc.query_section('introduction')

if query.section:
    # Exact match found
    print(f"Found: {query.section.title}")
elif query.parent:
    # New subsection - parent exists
    print(f"Can create under: {query.parent.title}")
elif query.error:
    # Error occurred (not found or ambiguous)
    print(f"Error: {query.error}")
    if query.matched:
        # Show all ambiguous matches
        for section in query.matched:
            print(f"  - {section.path}")
```

---

## Mutation Patterns

### 1. Frontmatter Mutations

```python
# Simple property assignment (type inference)
doc.title = "New Title"
doc.author = "Jane Doe"
doc.tags = ["python", "markdown"]
doc.version = 2.0
doc.published = True

# Batch updates with policies
doc.update_frontmatter(
    {"version": "2.1", "tags": ["updated"]},
    policy=UpdatePolicy.MERGE  # Smart merge
)

doc.update_frontmatter(
    {"status": "draft"},
    policy=UpdatePolicy.REPLACE  # Complete replacement
)

doc.update_frontmatter(
    {"tags": ["new-tag"]},
    policy=UpdatePolicy.APPEND  # Append to list
)
```

### 2. Section Mutations - Dynamic Assignment

```python
# Simple string assignment (type inference)
doc.introduction = "New introduction content"

# Markdown content
doc.introduction = """
## Introduction

This is a multi-line introduction with **markdown**.

- Point one
- Point two
"""

# Section object assignment
from mddata import Section, HeadingLevel, Block, BlockType

section = Section("Introduction", HeadingLevel.H1)
section.add_block(Block("intro", BlockType.PARAGRAPH, "Content"))
doc.introduction = section
```

### 3. Section Mutations - Explicit API

```python
# High-level API with automatic heading generation
doc.set_section(
    section_id="introduction.overview",
    content="Overview content here",
    policy=SectionPolicy.UPDATE  # Default
)

# Policy-based operations
doc.set_section("conclusion", "New conclusion", policy=SectionPolicy.REPLACE)
doc.set_section("updates", "More updates", policy=SectionPolicy.APPEND)

# Convenience methods
doc.append_to_section('introduction', 'Additional paragraph')
doc.replace_section('conclusion', 'Completely new conclusion')
doc.update_section('introduction', 'Updated content')
```

### 4. Batch Mutations

```python
from mddata import BatchChanges

# Define batch changes
changes: BatchChanges = {
    "frontmatter": {
        "version": "2.0",
        "updated_at": "2025-01-15"
    },
    "frontmatter_policy": "merge",
    "sections": [
        {
            "id": "introduction",
            "content": "New intro",
            "policy": "replace"
        },
        {
            "id": "conclusion",
            "content": "Additional conclusion",
            "policy": "append"
        }
    ]
}

# Apply batch changes
result = doc.apply_batch_changes(changes)

# Check results
if result["success"]:
    print(f"Applied {result['changes_count']} changes")
    print(f"  Frontmatter: {result['frontmatter_changes']}")
    print(f"  Sections: {result['section_changes']}")
else:
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
```

### 5. Mutation Policies

```python
from mddata import UpdatePolicy, SectionPolicy

# For frontmatter
UpdatePolicy.REPLACE  # Replace entire value
UpdatePolicy.MERGE    # Smart merge (lists, dicts)
UpdatePolicy.UPDATE   # Alias for MERGE
UpdatePolicy.APPEND   # Append to existing value

# For sections (alias of UpdatePolicy)
SectionPolicy.REPLACE  # Replace entire section
SectionPolicy.UPDATE   # Merge content, preserve subsections
SectionPolicy.APPEND   # Add content without removing existing
```

---

## Query Patterns

### 1. Section Queries

```python
# Simple section lookup
section = doc.get_section('introduction')

# Path-based lookup
overview = doc.get_section('introduction.overview')

# Fuzzy matching with validation
query = doc.query_section('intro')  # Partial match
if query.section:
    print(f"Matched: {query.section.path}")

# Check for new subsection creation
query = doc.query_section('introduction.new_section')
if query.parent and not query.error:
    print(f"Can create new section under: {query.parent.title}")

# Handle ambiguous references
query = doc.query_section('section')
if query.error and query.matched:
    print("Ambiguous reference. Did you mean:")
    for section in query.matched:
        print(f"  - {section.path}")
```

### 2. Block Queries

```python
# Get all blocks
all_blocks = doc.find_blocks()
print(f"Total blocks: {all_blocks.total}")

# Filter by type
paragraphs = doc.find_blocks(block_type='paragraph')
code_blocks = doc.find_blocks(block_type='code_block')
task_lists = doc.find_blocks(block_type='task_list')

# Filter by section
intro_blocks = doc.find_blocks(section_id='introduction')

# Combined filters
intro_paragraphs = doc.find_blocks(
    block_type='paragraph',
    section_id='introduction'
)

# Iterate results
for block in intro_paragraphs.blocks:
    print(f"{block.type.value}: {block.content}")
```

### 3. Task List Queries

```python
# Get TaskList objects for advanced operations
task_lists = doc.get_task_lists()
for task_list in task_lists:
    print(f"Task list in section: {task_list.block.section}")
    print(f"Total tasks: {task_list.count()}")

# Filter tasks by symbol
completed = doc.filter_tasks_by_symbol('x')
pending = doc.filter_tasks_by_symbol(' ')
priority = doc.filter_tasks_by_symbol('!')
in_progress = doc.filter_tasks_by_symbol('~')
blocked = doc.filter_tasks_by_symbol('?')

# Convenience methods
completed_tasks = doc.get_completed_tasks()
pending_tasks = doc.get_pending_tasks()

# Scoped to specific section
section_tasks = doc.get_task_lists(section_id='todo')
section_completed = doc.get_completed_tasks(section_id='todo')

# Access task data
for task in completed_tasks:
    print(f"✓ {task['content']}")  # Task text
    print(f"  Symbol: [{task['symbol']}]")  # 'x', ' ', '!', etc.
```

### 4. Structured Data Export

```python
# Get all sections as structured data
sections_data = doc.get_sections()
sections_list = sections_data['sections']      # list[SectionData]
sections_by_id = sections_data['sections_by_id']  # dict[str, SectionData]

# Get blocks as structured data
blocks_data = doc.get_blocks()
all_blocks = blocks_data['blocks']  # list[BlockData]

intro_blocks_data = doc.get_blocks(section_id='introduction')
intro_blocks = intro_blocks_data['blocks']

# Convert to JSON-serializable dictionary
data_dict = doc.to_dict()
# Returns: {
#     "frontmatter": {...},
#     "content": SectionData  # Root section
# }
```

---

## Extension Patterns

### 1. Custom Token Handlers

```python
from mddata import MarkdownProcessor, TokenType

processor = MarkdownProcessor()

def custom_callout_handler(token, state):
    """Handle custom callout syntax"""
    # Custom parsing logic
    content = extract_callout_content(token)
    block = Block(
        state['current_section'].id,
        BlockType.CUSTOM_CALLOUT,
        content
    )
    state['current_section'].add_block(block)
    return 1  # Number of tokens to advance

# Register handler
processor.register_handler(TokenType.CUSTOM, custom_callout_handler)

# Use custom processor
from mddata import MarkdownFile
doc = MarkdownFile('document.md')
doc._processor = processor  # Replace processor
```

### 2. Schema Validation

```python
from mddata import generate_schema, MarkdownData, ValidationLevel

# Generate schema from existing document
doc = MarkdownFile('template.md').mddata
schema = generate_schema(doc.data)

# Create validated document
validated_doc = MarkdownData(
    parsed_data,
    schema=schema,
    validation_level=ValidationLevel.STRICT
)

# Mutations are automatically validated
try:
    validated_doc.title = "New Title"  # Validates against schema
except ValueError as e:
    print(f"Validation failed: {e}")

# Different validation levels
ValidationLevel.STRICT    # Raises errors on validation failure
ValidationLevel.WARNINGS  # Collects warnings but doesn't fail
ValidationLevel.DISABLED  # Skips validation entirely
```

### 3. TaskList Extensions

```python
from mddata import TaskList, Block, BlockType

# Get task list blocks
task_blocks = doc.find_blocks(block_type='task_list')

for block in task_blocks.blocks:
    # Wrap in TaskList for advanced operations
    task_list = TaskList(block)

    # Filter operations
    completed = task_list.get_completed_tasks()
    pending = task_list.get_pending_tasks()
    custom = task_list.filter_by_symbol('!')

    # Statistics
    total = task_list.count()
    completion_rate = len(completed) / total if total > 0 else 0

    print(f"Completion: {completion_rate:.0%}")
```

---

## Complete Usage Examples

### Example 1: Load, Modify, Save

```python
from mddata import MarkdownFile

# Load document
doc = MarkdownFile('blog-post.md')

# Access frontmatter
print(f"Title: {doc.mddata.title}")
print(f"Author: {doc.mddata.author}")

# Modify frontmatter
doc.mddata.status = "published"
doc.mddata.updated_at = "2025-01-15"

# Modify sections
doc.mddata.set_section(
    'introduction',
    'Updated introduction with new content',
    policy=SectionPolicy.UPDATE
)

doc.mddata.append_to_section(
    'conclusion',
    '\n\nAdditional concluding thoughts.'
)

# Save changes
doc.save()  # Overwrites original
doc.save('blog-post-updated.md')  # Save to new file
```

### Example 2: Create Document Programmatically

```python
from mddata import MarkdownFile, Section, Block, BlockType, HeadingLevel

# Create structure programmatically
data = {
    "frontmatter": {
        "title": "API Documentation",
        "version": "1.0",
        "author": "Jane Doe"
    },
    "content": {
        "id": "",
        "title": "",
        "level": 0,
        "path": "",
        "blocks": None,
        "subsections": [
            {
                "id": "introduction",
                "title": "Introduction",
                "level": 1,
                "path": "introduction",
                "blocks": [
                    {
                        "section_id": "introduction",
                        "type": "paragraph",
                        "content": "Welcome to the API documentation.",
                        "metadata": {}
                    }
                ],
                "subsections": None
            },
            {
                "id": "getting_started",
                "title": "Getting Started",
                "level": 1,
                "path": "getting_started",
                "blocks": [
                    {
                        "section_id": "getting_started",
                        "type": "code_block",
                        "content": "pip install api-client",
                        "metadata": {"language": "bash"}
                    }
                ],
                "subsections": None
            }
        ]
    }
}

# Create document
doc = MarkdownFile.from_dict(data, filepath='api-docs.md')

# Save to file
doc.save()
```

### Example 3: Query and Filter

```python
from mddata import MarkdownFile, BlockType

doc = MarkdownFile('documentation.md').mddata

# Find all code blocks
code_blocks = doc.find_blocks(block_type='code_block')

print(f"Found {len(code_blocks.blocks)} code blocks:")
for block in code_blocks.blocks:
    language = block.metadata.get('language', 'unknown')
    preview = block.content[:50] + '...' if len(block.content) > 50 else block.content
    print(f"  [{language}] {preview}")

# Find all task lists
tasks = doc.get_task_lists()
for task_list in tasks:
    section_id = task_list.block.section
    completed = task_list.get_completed_tasks()
    pending = task_list.get_pending_tasks()

    print(f"\nSection: {section_id}")
    print(f"  Completed: {len(completed)}")
    print(f"  Pending: {len(pending)}")

# Query specific section
query = doc.query_section('api.authentication')
if query.section:
    print(f"Section: {query.section.title}")
    print(f"Blocks: {len(query.section.blocks)}")
elif query.error:
    print(f"Error: {query.error}")
```

### Example 4: Batch Processing

```python
from mddata import MarkdownFile, BatchChanges

doc = MarkdownFile('project.md').mddata

# Prepare batch changes
changes: BatchChanges = {
    "frontmatter": {
        "version": "2.0",
        "last_updated": "2025-01-15",
        "status": "published"
    },
    "frontmatter_policy": "merge",
    "sections": [
        {
            "id": "changelog",
            "content": "## Version 2.0\n\n- New features added\n- Bug fixes",
            "policy": "append"
        },
        {
            "id": "introduction",
            "content": "Updated introduction for version 2.0",
            "policy": "replace"
        }
    ]
}

# Apply all changes at once
result = doc.apply_batch_changes(changes)

if result['success']:
    print(f"✓ Successfully applied {result['changes_count']} changes")
    print(f"  Frontmatter updates: {result['frontmatter_changes']}")
    print(f"  Section updates: {result['section_changes']}")

    # Save to file
    MarkdownFile('project.md').mddata = doc
    doc.save()
else:
    print("✗ Batch operation failed:")
    for error in result['errors']:
        print(f"  - {error}")
```

### Example 5: Schema Validation Workflow

```python
from mddata import MarkdownFile, generate_schema, ValidationLevel

# Load template document
template = MarkdownFile('template.md').mddata

# Generate schema from template
schema = generate_schema(
    template.data,
    inference_mode='strict'  # or 'permissive'
)

# Save schema for reuse
import json
with open('schema.json', 'w') as f:
    json.dump(schema, f, indent=2)

# Load and validate new document
new_doc_data = MarkdownFile('new-document.md').mddata.data

# Create validated document instance
from mddata import MarkdownData
validated_doc = MarkdownData(
    new_doc_data,
    schema=schema,
    validation_level=ValidationLevel.STRICT
)

# All mutations are now validated
try:
    validated_doc.title = "Valid Title"  # ✓ Passes validation
    validated_doc.invalid_field = "value"  # ✗ Raises ValueError
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Summary

### Core Entry Points

1. **MarkdownFile** - For file-based workflows (load/save)
2. **MarkdownData** - For data manipulation and queries
3. **MarkdownProcessor** - For custom parsing workflows

### Key Design Principles

- **Pythonic API**: Dynamic property access, intuitive methods
- **Type Safety**: Strong typing with TypedDict contracts
- **Flexibility**: Multiple ways to achieve the same goal
- **Validation**: Optional schema validation for data integrity
- **Extensibility**: Plugin architecture for custom behavior

### Common Patterns

| Use Case | Pattern | Entry Point |
|----------|---------|-------------|
| Load file | `MarkdownFile('path.md')` | MarkdownFile |
| Read property | `doc.mddata.title` | MarkdownData |
| Set property | `doc.mddata.title = "New"` | MarkdownData |
| Query section | `doc.mddata.query_section('id')` | MarkdownData |
| Filter blocks | `doc.mddata.find_blocks(type='paragraph')` | MarkdownData |
| Batch update | `doc.mddata.apply_batch_changes(changes)` | MarkdownData |
| Save changes | `doc.save()` | MarkdownFile |
| Validate | `MarkdownData(data, schema=schema)` | MarkdownData |

This API provides a complete, intuitive interface for treating markdown files as structured, manipulable data objects.
