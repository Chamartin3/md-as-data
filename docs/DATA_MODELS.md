---
title: Markdown Data Models Reference
description: Comprehensive guide to mddata's Python data models for parsing, writing, and updating markdown documents
status: final
---

# Markdown Data Models Reference

This document explains the Python data models that define the structure of markdown documents in mddata. Understanding these models is essential for working with the library programmatically.

## Overview

mddata uses three core structural models:

1. **Parse Models**: Structure returned when reading markdown files
2. **Write Models**: Structure required when creating new documents
3. **Update Models**: Structure required when modifying existing documents

All models are implemented using Python TypedDict and dataclasses to enforce type safety and provide clear contracts.

---

## 1. Parse Models (Reading Documents)

When you parse a markdown document, mddata returns a structured representation consisting of frontmatter and hierarchical content.

### 1.1 Complete Document Structure

```python
class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON export."""

    frontmatter: FrontmatterProperties
    content: SectionData  # Root section
```

**Example JSON output:**

```json
{
  "frontmatter": {
    "title": "My Document",
    "author": "John Doe",
    "date": "2026-01-13",
    "tags": ["tutorial", "markdown"]
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": null,
    "children": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "path": "introduction",
        "blocks": [
          {
            "section_id": "introduction",
            "type": "paragraph",
            "content": "This is the introduction section.",
            "metadata": {}
          }
        ],
        "children": null
      }
    ]
  }
}
```

### 1.2 Frontmatter Properties

```python
# Type alias for frontmatter property values
FrontmatterValue = (
    str | int | float | bool | list[str] | dict[str, Any] | date | datetime | None
)

FrontmatterProperties = dict[str, FrontmatterValue]
```

**Supported Types:**
- Strings: `"value"`
- Numbers: `42`, `3.14`
- Booleans: `true`, `false`
- Arrays: `["item1", "item2"]`
- Dates: `2026-01-13`
- Nested objects: `{"key": "value"}`

### 1.3 Section Structure

```python
class SectionData(TypedDict):
    """Structured data for individual sections."""

    id: str              # Generated from title (kebab-case)
    title: str           # Section heading text
    level: int           # Heading level (1-6, 0 for root)
    path: str            # Dot-separated path (e.g., "intro.overview")
    blocks: list[BlockData] | None      # Content blocks
    children: list[SectionData] | None  # Nested subsections
```

**Field Descriptions:**

- **id**: Auto-generated identifier (`"My Section"` → `"my_section"`)
- **title**: Original heading text
- **level**: Markdown heading level (1-6), or 0 for document root
- **path**: Hierarchical path using dot notation (`parent.child.grandchild`)
- **blocks**: Array of content blocks (paragraphs, lists, code, etc.)
- **children**: Nested subsections (recursive structure)

**Example:**

```json
{
  "id": "getting_started",
  "title": "Getting Started",
  "level": 1,
  "path": "getting_started",
  "blocks": [
    {
      "section_id": "getting_started",
      "type": "paragraph",
      "content": "Let's begin with the basics.",
      "metadata": {}
    }
  ],
  "children": [
    {
      "id": "installation",
      "title": "Installation",
      "level": 2,
      "path": "getting_started.installation",
      "blocks": [...],
      "children": null
    }
  ]
}
```

### 1.4 Block Structure

```python
class BlockData(TypedDict):
    """Structured data for individual blocks."""

    section_id: str             # ID of parent section
    type: str                   # BlockType value
    content: str | list[str]    # Block content
    metadata: dict[str, Any]    # Type-specific metadata
```

**Block Types:**

```python
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    TASK_LIST = "task_list"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
```

**Examples by Type:**

**Paragraph:**
```json
{
  "section_id": "intro",
  "type": "paragraph",
  "content": "This is a paragraph.",
  "metadata": {}
}
```

**Code Block:**
```json
{
  "section_id": "examples",
  "type": "code_block",
  "content": "print('Hello, world!')",
  "metadata": {
    "language": "python"
  }
}
```

**List:**
```json
{
  "section_id": "features",
  "type": "list",
  "content": ["Feature 1", "Feature 2", "Feature 3"],
  "metadata": {}
}
```

**Task List:**
```json
{
  "section_id": "todos",
  "type": "task_list",
  "content": ["Write documentation", "Add tests", "Deploy"],
  "metadata": {
    "tasks": [
      {"content": "Write documentation", "symbol": "x", "uid": "a1b2"},
      {"content": "Add tests", "symbol": " ", "uid": "c3d4"},
      {"content": "Deploy", "symbol": " ", "uid": "e5f6"}
    ]
  }
}
```

**Link:**
```json
{
  "section_id": "references",
  "type": "link",
  "content": "Documentation",
  "metadata": {
    "href": "https://example.com/docs",
    "title": "Official Docs"
  }
}
```

**Image:**
```json
{
  "section_id": "gallery",
  "type": "image",
  "content": "",
  "metadata": {
    "src": "diagram.png",
    "alt": "Architecture diagram",
    "title": "System Architecture"
  }
}
```

---

## 2. Write Models (Creating Documents)

When creating new documents, you provide data in a format that mddata will convert to markdown.

### 2.1 Document Creation Format

```python
@dataclass
class MarkdownDataUpdate:
    """Document update operations with optional policies and parameters."""

    # Core document data
    frontmatter: FrontmatterProperties = field(default_factory=dict)
    content: SectionData | None = field(default=None)

    # Update-specific metadata
    frontmatter_policy: UpdatePolicy = UpdatePolicy.MERGE
    parameters: dict[str, MarkdownFormField] = field(default_factory=dict)

    # Backward compatibility: flat section list
    sections: list[SectionUpdate] = field(default_factory=list)
```

**Two Approaches:**

#### Approach 1: Hierarchical Content (Recommended)

Use the `content` field with nested `SectionData` structure:

```python
{
    "frontmatter": {
        "title": "New Document",
        "author": "Jane Doe"
    },
    "content": {
        "id": "",
        "title": "",
        "level": 0,
        "path": "",
        "blocks": null,
        "children": [
            {
                "id": "overview",
                "title": "Overview",
                "level": 1,
                "path": "overview",
                "blocks": [
                    {
                        "section_id": "overview",
                        "type": "paragraph",
                        "content": "Document overview here.",
                        "metadata": {}
                    }
                ],
                "children": [
                    {
                        "id": "purpose",
                        "title": "Purpose",
                        "level": 2,
                        "path": "overview.purpose",
                        "blocks": [
                            {
                                "section_id": "purpose",
                                "type": "paragraph",
                                "content": "This document serves to...",
                                "metadata": {}
                            }
                        ],
                        "children": null
                    }
                ]
            }
        ]
    }
}
```

#### Approach 2: Flat Sections List (Legacy)

Use the `sections` field for simpler, flat structures:

```python
{
    "frontmatter": {
        "title": "New Document"
    },
    "sections": [
        {
            "id": "overview",
            "content": "# Overview\n\nDocument overview here."
        },
        {
            "id": "details",
            "content": "# Details\n\nDetailed information."
        }
    ]
}
```

### 2.2 Section Update Structure

```python
@dataclass
class SectionUpdate:
    """Section update with validation and recursive structure support."""

    # Required fields
    id: str                      # Section identifier
    content: str | None = None   # Raw markdown content (optional)

    # Update metadata
    policy: UpdatePolicy = UpdatePolicy.UPDATE

    # Optional structured data
    title: str | None = None
    level: int | None = None
    path: str | None = None
    blocks: list[dict[str, Any]] = field(default_factory=list)
    children: list["SectionUpdate"] = field(default_factory=list)
```

**Usage Examples:**

**Simple content string:**
```python
{
    "id": "intro",
    "content": "# Introduction\n\nWelcome to the guide."
}
```

**Structured with blocks:**
```python
{
    "id": "features",
    "title": "Features",
    "level": 1,
    "blocks": [
        {
            "section_id": "features",
            "type": "list",
            "content": ["Fast", "Reliable", "Extensible"],
            "metadata": {}
        }
    ]
}
```

**Hierarchical with children:**
```python
{
    "id": "guide",
    "title": "User Guide",
    "level": 1,
    "blocks": [
        {
            "section_id": "guide",
            "type": "paragraph",
            "content": "Complete guide to using the system.",
            "metadata": {}
        }
    ],
    "children": [
        {
            "id": "basic",
            "title": "Basic Usage",
            "level": 2,
            "blocks": [...]
        },
        {
            "id": "advanced",
            "title": "Advanced Topics",
            "level": 2,
            "blocks": [...]
        }
    ]
}
```

---

## 3. Update Models (Modifying Documents)

When modifying existing documents, you specify changes with update policies.

### 3.1 Update Policies

```python
class UpdatePolicy(Enum):
    """Unified policies for both frontmatter and section update operations."""

    REPLACE = "replace"  # Replace entire value/section
    UPDATE = "update"    # Update/merge while preserving structure
    MERGE = "merge"      # Smart merge with existing value
    APPEND = "append"    # Append to existing value/content
```

**Policy Behaviors:**

| Policy | Frontmatter | Sections |
|--------|------------|----------|
| **REPLACE** | Replace entire property | Replace section and all subsections |
| **UPDATE** | Merge properties, keep unspecified | Replace blocks, preserve unspecified subsections |
| **MERGE** | Deep merge objects/arrays | Same as UPDATE |
| **APPEND** | Append to arrays | Append blocks, recursively merge subsections |

### 3.2 Update Operations

**Frontmatter Updates:**

```python
# Replace entire frontmatter
{
    "frontmatter": {
        "title": "New Title",
        "status": "published"
    },
    "frontmatter_policy": "replace"
}

# Merge with existing
{
    "frontmatter": {
        "status": "published",
        "reviewed_by": "editor@example.com"
    },
    "frontmatter_policy": "merge"  # Keeps existing title, adds new fields
}
```

**Section Updates:**

```python
# Replace entire section
{
    "sections": [
        {
            "id": "introduction",
            "content": "# Introduction\n\nCompletely new content.",
            "policy": "replace"
        }
    ]
}

# Update section, preserve subsections
{
    "sections": [
        {
            "id": "introduction",
            "content": "# Introduction\n\nUpdated intro text.",
            "policy": "update"
        }
    ]
}

# Append to section
{
    "sections": [
        {
            "id": "notes",
            "blocks": [
                {
                    "section_id": "notes",
                    "type": "paragraph",
                    "content": "Additional note here.",
                    "metadata": {}
                }
            ],
            "policy": "append"
        }
    ]
}
```

---

## 4. Forms (Parameterized Templates)

Forms are templates with parameters that must be filled before use.

### 4.1 Form Structure

```python
@dataclass
class MarkdownForm(MarkdownDataUpdate):
    """Parameterized markdown form.

    Forms MUST have parameters - this is enforced in __post_init__.
    """

    parameters: dict[str, MarkdownFormField] = field(default_factory=dict)
```

**Key Requirement:** Forms MUST define parameters. Without parameters, use `MarkdownDataUpdate` instead.

### 4.2 Form Field Definition

```python
class MarkdownFormField(TypedDict, total=False):
    """Form field definition with validation rules."""

    # Type definition
    type: str  # "str", "int", "float", "bool", "array", "date"

    # Required/optional
    required: bool
    default: Any
    description: str

    # Validation constraints
    min: int | float
    max: int | float
    pattern: str

    # Enum validation
    enum: list[Any]
    enum_strict: bool
    enum_descriptions: dict[str, str]

    # Array validation
    item_type: str
    min_items: int
    max_items: int
    unique_items: bool
```

**Example Form:**

```json
{
  "parameters": {
    "title": {
      "type": "str",
      "required": true,
      "min": 5,
      "max": 100,
      "description": "Document title"
    },
    "status": {
      "type": "str",
      "enum": ["draft", "review", "published"],
      "enum_strict": true,
      "default": "draft",
      "description": "Document status"
    },
    "tags": {
      "type": "array",
      "item_type": "str",
      "min_items": 1,
      "max_items": 5,
      "description": "Document tags"
    }
  },
  "frontmatter": {
    "title": "{title}",
    "status": "{status}",
    "tags": "{tags}",
    "created": "{date}"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": null,
    "children": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "path": "introduction",
        "blocks": [
          {
            "section_id": "introduction",
            "type": "paragraph",
            "content": "This document covers {title}.",
            "metadata": {}
          }
        ],
        "children": null
      }
    ]
  }
}
```

### 4.3 Parameter Types

**String:**
```json
{
  "type": "str",
  "required": true,
  "min": 1,
  "max": 200,
  "pattern": "^[A-Z].*"
}
```

**Integer:**
```json
{
  "type": "int",
  "required": true,
  "min": 1,
  "max": 100
}
```

**Float:**
```json
{
  "type": "float",
  "min": 0.0,
  "max": 100.0
}
```

**Boolean:**
```json
{
  "type": "bool",
  "default": false
}
```

**Enum:**
```json
{
  "type": "str",
  "enum": ["draft", "review", "published"],
  "enum_strict": true,
  "enum_descriptions": {
    "draft": "Work in progress",
    "review": "Ready for review",
    "published": "Published and visible"
  }
}
```

**Array:**
```json
{
  "type": "array",
  "item_type": "str",
  "min_items": 1,
  "max_items": 10,
  "unique_items": true,
  "item_enum": ["python", "javascript", "rust", "go"]
}
```

### 4.4 Computed Parameters

Automatically available without definition:

- `{date}` - Current date (YYYY-MM-DD)
- `{time}` - Current time (HH:MM:SS)
- `{env.VAR}` - Environment variable

---

## 5. Python API Usage

### 5.1 Reading Documents

```python
from mddata import MarkdownFile

# Load document
doc = MarkdownFile('document.md')

# Access as dict
data = doc.mddata.to_dict()
# Returns: MarkdownDataDict

# Access frontmatter
title = doc.mddata.title
doc.mddata.status = "published"

# Query sections
query = doc.mddata.query_section('introduction')
if query.section:
    print(query.section.to_dict())
    # Returns: SectionData
```

### 5.2 Creating Documents

```python
from mddata import MarkdownFile
from mddata.models import MarkdownDataUpdate

# Create from structured data
data = MarkdownDataUpdate(
    frontmatter={"title": "New Doc", "author": "John"},
    content={
        "id": "",
        "title": "",
        "level": 0,
        "path": "",
        "blocks": None,
        "children": [
            {
                "id": "intro",
                "title": "Introduction",
                "level": 1,
                "path": "intro",
                "blocks": [
                    {
                        "section_id": "intro",
                        "type": "paragraph",
                        "content": "Welcome!",
                        "metadata": {}
                    }
                ],
                "children": None
            }
        ]
    }
)

# Generate markdown
doc = MarkdownFile.from_data(data.as_markdown_dict())
doc.save('new-document.md')
```

### 5.3 Updating Documents

```python
from mddata import MarkdownFile
from mddata.models import MarkdownDataUpdate, UpdatePolicy

# Load existing document
doc = MarkdownFile('document.md')

# Create update
update = MarkdownDataUpdate(
    frontmatter={"status": "published"},
    frontmatter_policy=UpdatePolicy.MERGE,
    sections=[
        {
            "id": "introduction",
            "content": "# Introduction\n\nUpdated content.",
            "policy": UpdatePolicy.UPDATE
        }
    ]
)

# Apply update
doc.mddata.apply_update(update)
doc.save()
```

### 5.4 Working with Forms

```python
from mddata.models import MarkdownForm
from mddata.forms import MarkdownFormFiller

# Load form
form = MarkdownForm.from_dict({
    "parameters": {
        "title": {"type": "str", "required": True},
        "status": {"type": "str", "enum": ["draft", "published"]}
    },
    "frontmatter": {
        "title": "{title}",
        "status": "{status}"
    }
})

# Fill form
filler = MarkdownFormFiller(form)
data = filler.fill(
    cli_params=['title=My Document', 'status=published']
)
# Returns: MarkdownDataUpdate (ready to use)

# Generate document
doc = MarkdownFile.from_data(data.as_markdown_dict())
doc.save('output.md')
```

---

## 6. Validation and Type Safety

### 6.1 Runtime Validation

All models include validation:

```python
# SectionUpdate validation
update = SectionUpdate(
    id="intro",
    content="# Introduction\n\nContent here.",
    level=1
)

errors = update.validate()
if errors:
    print(f"Validation errors: {errors}")
```

### 6.2 Type Checking

All models use type hints for static analysis:

```python
from mddata.models import SectionData, BlockData

# Type-checked construction
section: SectionData = {
    "id": "intro",
    "title": "Introduction",
    "level": 1,
    "path": "intro",
    "blocks": [
        {
            "section_id": "intro",
            "type": "paragraph",
            "content": "Content",
            "metadata": {}
        }
    ],
    "children": None
}
```

### 6.3 Schema Validation

Documents can be validated against schemas:

```python
from mddata import generate_schema, MarkdownData

# Generate schema from document
schema = generate_schema(doc.mddata.data)

# Create validated document
validated = MarkdownData(doc.mddata.data, schema=schema)

# Mutations are validated
validated.title = "New Title"  # Validates type/constraints
```

---

## 7. Model Hierarchy

```
Base Types (base.py)
├── FrontmatterValue
├── FrontmatterProperties
├── BlockType (Enum)
├── HeadingLevel (Enum)
└── UpdatePolicy (Enum)

Document Models (document.py)
├── BlockData (TypedDict)
├── Block (Class)
├── SectionData (TypedDict)
├── Section (Class)
├── ContentTree (Class)
└── MarkdownDataDict (TypedDict)

Form Models (forms.py)
├── MarkdownFormField (TypedDict)
└── ParameterValue (TypeAlias)

Update Models (update.py)
├── SectionUpdate (Dataclass)
├── MarkdownDataUpdate (Dataclass)
└── MarkdownForm (Dataclass, extends MarkdownDataUpdate)
```

---

## 8. Key Design Principles

### 8.1 Separation of Concerns

- **Parse models**: Read-only structures from markdown
- **Write models**: Creation and generation
- **Update models**: Modification with policies

### 8.2 Type Safety

- TypedDict for data contracts
- Dataclasses for behavior
- No `Any` types in public APIs
- Enums instead of string constants

### 8.3 Flexibility

- Support both hierarchical and flat structures
- Multiple input formats (content string, blocks, Section objects)
- Policy-based updates for fine-grained control

### 8.4 Validation

- Runtime validation in dataclasses
- Static type checking with TypedDict
- Schema validation for documents
- Parameter validation for forms

---

## 9. Common Patterns

### Pattern 1: Simple Document Creation

```python
data = {
    "frontmatter": {"title": "Quick Doc"},
    "content": {
        "id": "", "title": "", "level": 0, "path": "",
        "blocks": None,
        "children": [
            {
                "id": "main",
                "title": "Main Content",
                "level": 1,
                "path": "main",
                "blocks": [
                    {
                        "section_id": "main",
                        "type": "paragraph",
                        "content": "Document content.",
                        "metadata": {}
                    }
                ],
                "children": None
            }
        ]
    }
}
```

### Pattern 2: Incremental Updates

```python
# Update frontmatter only
{"frontmatter": {"status": "published"}, "frontmatter_policy": "merge"}

# Update one section
{"sections": [{"id": "intro", "content": "New intro", "policy": "update"}]}

# Append to section
{"sections": [{"id": "notes", "content": "Additional note", "policy": "append"}]}
```

### Pattern 3: Template Creation

```python
{
    "parameters": {
        "name": {"type": "str", "required": true},
        "items": {"type": "array", "item_type": "str"}
    },
    "frontmatter": {"author": "{name}"},
    "content": {
        "id": "", "title": "", "level": 0, "path": "",
        "blocks": None,
        "children": [
            {
                "id": "list",
                "title": "{name}'s List",
                "level": 1,
                "path": "list",
                "blocks": [
                    {
                        "section_id": "list",
                        "type": "list",
                        "content": "{items}",
                        "metadata": {}
                    }
                ],
                "children": None
            }
        ]
    }
}
```

---

## Summary

mddata's data models provide a comprehensive, type-safe foundation for working with markdown as structured data:

1. **Parse models** define the structure returned when reading documents
2. **Write models** define the structure required when creating documents
3. **Update models** define the structure required when modifying documents
4. **Form models** add parameterization for reusable templates

All models enforce structural requirements through Python's type system and runtime validation, ensuring data integrity throughout the document lifecycle.
