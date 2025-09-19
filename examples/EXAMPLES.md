# mdasdata Examples Guide

This directory contains practical examples demonstrating key features of the `mdasdata` library. Each example includes test data and runnable scripts with expected outputs.

## Table of Contents

- [Multi-File Schema Generation](#multi-file-schema-generation)
- [Task Lists (Planned Feature)](#task-lists-planned-feature)

---

## Multi-File Schema Generation

**Location**: `examples/multi_file_schema/`

**Feature Status**: ✅ Implemented (Issue #004)

This example demonstrates generating schemas from multiple markdown documents, showing how the system:
- Aggregates frontmatter properties across files
- Marks properties as required based on frequency (≥75% threshold)
- Infers enum types for single-word string properties
- Handles type conflicts with union types
- Merges section hierarchies

### Example Files

The example includes three Python development documentation files:

1. **doc1.md** - Python Development Guide (draft, version 1)
2. **doc2.md** - Python Testing Tutorial (published)
3. **doc3.md** - Python Package Management (archived, version 2)

### Property Distribution

| Property | doc1 | doc2 | doc3 | Frequency | Required |
|----------|------|------|------|-----------|----------|
| title    | ✓    | ✓    | ✓    | 3/3 (100%) | Yes |
| author   | ✓    | ✓    | ✗    | 2/3 (67%)  | No |
| status   | ✓    | ✓    | ✓    | 3/3 (100%) | Yes (enum) |
| version  | ✓    | ✗    | ✓    | 2/3 (67%)  | No |
| tags     | ✓    | ✓    | ✓    | 3/3 (100%) | Yes |
| created  | ✓    | ✓    | ✓    | 3/3 (100%) | Yes |
| updated  | ✗    | ✗    | ✓    | 1/3 (33%)  | No |

### Running the Examples

#### 1. Generate Schema Using CLI (Single File)

```bash
cd /home/omidev/Code/tools/makdown_manager/mdasdata
uv run mdasdata examples/multi_file_schema/doc1.md schema generate --pretty
```

**Expected Output**:
```
Schema generated from 1 markdown file

{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true
    },
    "author": {
      "type": "str",
      "required": true
    },
    "status": {
      "type": "str",
      "required": true
    },
    "version": {
      "type": "int",
      "required": true
    },
    "tags": {
      "type": "list",
      "required": true
    },
    "created": {
      "type": "str",
      "required": true
    }
  },
  "sections": { ... },
  "validation_level": "warnings"
}
```

#### 2. Generate Merged Schema from Folder

```bash
uv run mdasdata examples/multi_file_schema/ schema generate --pretty
```

**Expected Output**:
```
Schema generated from 3 markdown files

{
  "frontmatter": {
    "title": {
      "type": "str",
      "required": true
    },
    "author": {
      "type": "str",
      "required": false
    },
    "status": {
      "type": "str",
      "required": true,
      "enum": ["draft", "published", "archived"]
    },
    "version": {
      "type": "int",
      "required": false
    },
    "tags": {
      "type": "list",
      "required": true
    },
    "created": {
      "type": "str",
      "required": true
    },
    "updated": {
      "type": "str",
      "required": false
    }
  },
  "sections": { ... },
  "validation_level": "warnings"
}
```

**Key Observations**:
- `title`, `tags`, `created` are **required** (appear in 100% of files)
- `status` is **required** and becomes an **enum** type with values `["draft", "published", "archived"]`
- `author`, `version`, `updated` are **optional** (appear in <75% of files)

#### 3. Generate Schema with Different Inference Modes

**Permissive Mode** (default - flexible constraints):
```bash
uv run mdasdata examples/multi_file_schema/ schema generate --inference-mode permissive --pretty --output examples/multi_file_schema/schema_permissive.json
```

**Strict Mode** (exact constraints):
```bash
uv run mdasdata examples/multi_file_schema/ schema generate --inference-mode strict --pretty --output examples/multi_file_schema/schema_strict.json
```

#### 4. Validate Documents Against Schema

First, generate a schema:
```bash
uv run mdasdata examples/multi_file_schema/ schema generate --output examples/multi_file_schema/merged_schema.json
```

Then validate individual documents:
```bash
# Validate doc1 (should pass - has all required fields)
uv run mdasdata examples/multi_file_schema/doc1.md schema validate examples/multi_file_schema/merged_schema.json --verbose

# Validate doc2 (should pass)
uv run mdasdata examples/multi_file_schema/doc2.md schema validate examples/multi_file_schema/merged_schema.json --verbose

# Validate doc3 (should pass - missing optional 'author' is OK)
uv run mdasdata examples/multi_file_schema/doc3.md schema validate examples/multi_file_schema/merged_schema.json --verbose
```

**Expected Output** (validation success):
```
✓ Document validation passed
  All required frontmatter properties present
  All property types match schema
  Status value 'draft' matches enum constraint
```

#### 5. Display Schema Information

```bash
uv run mdasdata examples/multi_file_schema/doc1.md schema info examples/multi_file_schema/merged_schema.json
```

**Expected Output**:
```
Schema Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontmatter Properties: 7
  Required: 4 (title, status, tags, created)
  Optional: 3 (author, version, updated)

Property Constraints:
  • status: enum ["draft", "published", "archived"]

Validation Level: warnings
```

#### 6. Run Python Example Script

```bash
uv run python examples/multi_file_schema/example_multi_file_schema.py
```

**Expected Output**:
```
============================================================
Multi-File Schema Generation Example
============================================================

Loading 3 markdown documents...

Document Overview:
------------------------------------------------------------
Document 1: Python Development Guide
  Properties: title, author, status, version, tags, created
  Status: draft

Document 2: Python Testing Tutorial
  Properties: title, author, status, tags, created
  Status: published

Document 3: Python Package Management
  Properties: title, status, version, tags, created, updated
  Status: archived

Generating merged schema from all documents...

✓ Schema generated from 3 markdown files

Frontmatter Property Analysis:
------------------------------------------------------------
title: str [REQUIRED]
  Frequency: 3/3 documents (100%)

author: str [OPTIONAL]
  Frequency: 2/3 documents (67%)

status: str [REQUIRED]
  Enum values: ['draft', 'published', 'archived']
  Frequency: 3/3 documents (100%)

version: int [OPTIONAL]
  Frequency: 2/3 documents (67%)

tags: list [REQUIRED]
  Frequency: 3/3 documents (100%)

created: str [REQUIRED]
  Frequency: 3/3 documents (100%)

updated: str [OPTIONAL]
  Frequency: 1/3 documents (33%)

Key Insights:
------------------------------------------------------------
• 'title' appears in all documents → marked as REQUIRED
• 'author' appears in 2/3 documents (67%) → marked as OPTIONAL
• 'status' appears in all documents → marked as REQUIRED
• 'status' has single-word values → inferred as ENUM type
• 'tags' appears in all documents → marked as REQUIRED
• 'version' appears in 2/3 documents → marked as OPTIONAL

✓ Schema saved to: examples/multi_file_schema/generated_schema.json

============================================================
Example completed successfully!
============================================================
```

### Understanding Schema Merging

**Frequency-Based Requirements**:
- Properties appearing in ≥75% of documents are marked as `required: true`
- Properties appearing in <75% of documents are marked as `required: false`

**Enum Type Inference**:
- Single-word string properties with consistent values become enum types
- All observed values are included in the enum array
- Null values are included when present

**Type Conflict Resolution**:
- When a property has different types across files, a union type is created
- Example: `version` is `int` in doc1, `str` in doc2 → becomes `"int|str"`

**Section Hierarchy Merging**:
- All section structures from all documents are combined
- Preserves all subsection paths and relationships
- Creates unified section schema representing all variations

---

## Task Lists (Planned Feature)

**Location**: `examples/task_lists/`

**Feature Status**: 🚧 Planned (Issue #005 - Not Yet Implemented)

This example demonstrates the **planned** task list functionality for extracting, filtering, and manipulating markdown task lists with different status indicators.

### Example Files

1. **project_tasks.md** - Software development project tasks with various statuses
2. **personal_tasks.md** - Personal task manager with daily tasks

### Task Status Indicators

The planned implementation will support:
- `[x]` - Completed tasks
- `[ ]` - Pending tasks
- `[!]` - High priority tasks
- `[~]` - In-progress tasks
- `[?]` - Blocked/waiting tasks
- `[P]` - Custom status indicators

### Running the Example

```bash
uv run python examples/task_lists/example_task_lists.py
```

**Expected Output**:
```
============================================================
Task Lists Example (PLANNED FUNCTIONALITY)
============================================================

NOTE: This example demonstrates the planned task list API
described in issue #005. Implementation is pending.

Example Task File: project_tasks.md

Planned API Usage:
------------------------------------------------------------

# Load document with task lists
from md_as_data import MarkdownFile
doc = MarkdownFile('examples/task_lists/project_tasks.md')
mddata = doc.mddata

# Get all task lists from document
task_lists = mddata.get_task_lists()
# Returns: List of TaskList objects

# Filter tasks by completion status
completed_tasks = mddata.get_completed_tasks()
pending_tasks = mddata.get_pending_tasks()

# Filter tasks by specific status indicator
priority_tasks = mddata.filter_tasks_by_status('!')
in_progress_tasks = mddata.filter_tasks_by_status('~')
blocked_tasks = mddata.filter_tasks_by_status('?')

# Work with individual task lists
for task_list in task_lists:
    # Filter within specific list
    completed = task_list.filter_completed(True)
    priority = task_list.filter_priority(True)
    custom = task_list.get_custom_status_tasks()

    # Mutate task status
    task_list.mark_completed(0)  # Mark first task as done
    task_list.mark_pending(1)    # Mark second task as pending
    task_list.set_custom_status(2, '~')  # Set custom status

    # Add/remove tasks
    task_list.add_task('New task item', status=' ')
    task_list.remove_task(0)

    # Reorder tasks
    task_list.reorder_tasks([1, 0, 2])  # Swap first two tasks

------------------------------------------------------------

Example Task List Content:
------------------------------------------------------------

## Sprint Planning

- [x] Define project scope
- [ ] Create user stories
- [!] Review security requirements (HIGH PRIORITY)
- [~] Research technology stack (IN PROGRESS)
- [?] Clarify performance requirements (BLOCKED)

------------------------------------------------------------

Expected Parsing Results:
------------------------------------------------------------

Task List Block Type: TASK_LIST

Individual Tasks:
  1. [x] Define project scope
     → Status: 'x', Completed: True, Priority: False

  2. [ ] Create user stories
     → Status: ' ', Completed: False, Priority: False

  3. [!] Review security requirements
     → Status: '!', Completed: False, Priority: True

  4. [~] Research technology stack
     → Status: '~', Completed: False, Custom: '~'

  5. [?] Clarify performance requirements
     → Status: '?', Completed: False, Custom: '?'

============================================================
For implementation details, see:
  issues/done/005_task_lists.md
============================================================
```

### Planned CLI Commands (Not Yet Available)

Once implemented, task list functionality will be available through CLI:

```bash
# Show all tasks in a document
uv run mdasdata examples/task_lists/project_tasks.md info tasks

# Filter by completion status
uv run mdasdata examples/task_lists/project_tasks.md info tasks --completed

# Filter by priority
uv run mdasdata examples/task_lists/project_tasks.md info tasks --priority

# Filter by custom status
uv run mdasdata examples/task_lists/project_tasks.md info tasks --status "~"

# Filter by section
uv run mdasdata examples/task_lists/project_tasks.md info tasks --section "sprint_planning"
```

**Note**: These commands will return errors until issue #005 is fully implemented.

---

## Additional Examples

For more examples, see:
- `examples/schemas/` - Pre-generated schema examples (minimal, simple, complex)
- Source code documentation in `README.md`
- Issue specifications in `issues/done/`

## Running All Examples

To run all working examples in sequence:

```bash
# Multi-file schema generation
uv run python examples/multi_file_schema/example_multi_file_schema.py

# Task lists (demonstration only)
uv run python examples/task_lists/example_task_lists.py
```

## Troubleshooting

### Schema Generation Issues

**Problem**: Schema doesn't show enum types for status field
- **Solution**: Ensure all status values are single words (no spaces)
- **Check**: Verify values appear consistently across files

**Problem**: Property not marked as required despite appearing in all files
- **Solution**: Verify the property name is identical across all files (case-sensitive)

### Validation Errors

**Problem**: Document fails validation with "missing required property"
- **Solution**: Check the schema requirements - add missing properties to frontmatter
- **Check**: Use `schema info` command to see all required properties

**Problem**: Enum validation fails
- **Solution**: Verify the value matches exactly one of the allowed enum values (case-sensitive)

---

## Contributing Examples

To add new examples:

1. Create a new directory under `examples/`
2. Add test markdown files demonstrating the feature
3. Create a Python script showing API usage
4. Update this `EXAMPLES.md` with running instructions
5. Include expected outputs for verification

## License

These examples are part of the mdasdata project and follow the same license terms.
