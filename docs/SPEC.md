# API Specification

This document defines the core public API of the markdown-as-data library, including all modules, objects, parameters, and data types available for programmatic use.

## Table of Contents

- [Core Classes](#core-classes)
- [Data Types](#data-types)
- [Enums](#enums)
- [Entry Points](#entry-points)

---

## Core Classes

### MarkdownFile

Primary entry point for file operations and document management.

```python
class MarkdownFile:
    def __init__(self, filepath: str) -> None

    # Properties
    @property
    def mddata: MarkdownData
    @property
    def filepath: Path

    # Serialization methods
    def to_json(self) -> str
    def to_markdown(self) -> str

    # File operations
    def save(self, filepath: str | None = None) -> None
    def save_as(self, filepath: str) -> None
```

**Parameters:**
- `filepath`: Path to markdown file (required)

**Properties:**
- `mddata`: The parsed MarkdownData object
- `filepath`: Path to the markdown file

**Methods:**
- `to_json()`: Serialize document to JSON string
- `to_markdown()`: Serialize document back to markdown string
- `save()`: Save to original or specified file path
- `save_as()`: Save to new file path

---

### MarkdownData

Parsed document with frontmatter and content structure. Main interface for document manipulation.

```python
class MarkdownData:
    def __init__(self, parsed_data: ParsedMarkdownData) -> None

    # Properties
    @property
    def data: ParsedMarkdownData
    @property
    def frontmatter: FrontmatterProperties
    @property
    def content: ContentTree

    # Dynamic access
    def __getattr__(self, name: str) -> FrontmatterPropertyValue | Section
    def __setattr__(self, name: str, value: InputDataOptions) -> None

    # Section operations
    def get_section(self, section_id_or_path: str) -> Section | None
    def get_all_sections(self) -> list[Section]

    # Data accessors
    def get_sections(self) -> SectionsData
    def get_blocks(self, section_id: str | None = None) -> BlocksData

    # Mutation methods with policies
    def append_to_section(self, section_id_or_path: str, block_markdown: str) -> None
    def replace_section(self, section_id_or_path: str, section_contents: InputDataOptions) -> None
    def update_section(self, section_id_or_path: str, section_contents: InputDataOptions) -> None

    # Operation inference
    def infer_operation_type(self, name: str, value: InputDataOptions,
                             policy: SectionPolicy | None = None) -> UpdateOperation

    # Serialization
    def to_dict(self) -> MarkdownDataDict
```

**Dynamic Properties:**
- All frontmatter keys are accessible as properties (e.g., `doc.title`, `doc.author`)
- Content sections accessible through content tree (e.g., `doc.content.introduction`)

**Methods:**
- `get_section()`: Get specific section by ID or path
- `get_all_sections()`: Get list of all sections
- `get_sections()`: Get all sections as structured data
- `get_blocks()`: Get blocks from specific section or all sections
- `append_to_section()`: Append markdown content to existing section
- `replace_section()`: Replace entire section content
- `update_section()`: Update section content while preserving subsections
- `infer_operation_type()`: Determine operation type from value
- `to_dict()`: Convert to JSON-serializable dictionary

---

### ContentTree

Hierarchical content structure with dynamic property access.

```python
class ContentTree:
    def __init__(self) -> None

    # Properties
    @property
    def root: Section
    @property
    def paths: list[str]
    @property
    def keys: list[str]

    # Access methods
    def __getattr__(self, name: str) -> Section | None  # Dynamic section access
    def get_section(self, section_id_or_path: str) -> Section | None
    def get_all_sections(self) -> list[Section]
    def get_all_blocks(self) -> list[Block]

    # Mutation methods
    def add_section(self, section: Section, parent_path: str | None = None) -> None

    # Serialization
    def to_dict(self) -> SectionData
```

**Parameters:**
- `section_id_or_path`: Section identifier or dot-separated path
- `parent_path`: Optional parent section path for new sections

**Methods:**
- `get_section()`: Retrieve section by ID or hierarchical path
- `get_all_sections()`: Get all sections in tree
- `get_all_blocks()`: Get all blocks from all sections
- `add_section()`: Add section to tree with optional parent

---

### MarkdownProcessor

Handles markdown parsing and serialization operations.

```python
class MarkdownProcessor:
    def __init__(self) -> None

    # Properties
    @property
    def token_handlers: dict[TokenType, Callable]

    # Parsing methods
    def parse(self, text: str) -> ParsedMarkdownData
    def parse_content_to_section(self, text: str, section_path: str) -> Section

    # Serialization methods
    def serialize_document(self, document_data: MarkdownDataDict) -> str
    def serialize_section(self, section: Section) -> str
    def serialize_block(self, block: Block) -> str
```

**Methods:**
- `parse()`: Parse full markdown document into structured data
- `parse_content_to_section()`: Parse text into a single section
- `serialize_document()`: Convert document data back to markdown
- `serialize_section()`: Convert section to markdown text
- `serialize_block()`: Convert block to markdown text

---

### Section

Individual content section with heading, blocks, and nested structure.

```python
class Section:
    def __init__(self, title: str, level: HeadingLevel, parent_path: str | None = None) -> None

    # Properties
    @property
    def id: str
    @property
    def title: str
    @property
    def level: HeadingLevel
    @property
    def path: str
    @property
    def blocks: list[Block]
    @property
    def subsections: list[Section]
    @property
    def parent_path: str | None

    # Static methods
    @classmethod
    def is_path(cls, identifier: str) -> bool

    # Mutation methods
    def add_block(self, block: Block) -> None
    def add_subsection(self, section: Section) -> None
    def create_subsection(self, title: str, content: str | None) -> Section

    # Serialization
    def to_dict(self) -> SectionData
    def to_text(self) -> str
```

**Parameters:**
- `title`: Section heading text (required)
- `level`: Heading level from HeadingLevel enum (required)
- `parent_path`: Optional path to parent section
- `identifier`: Section ID or path for validation

**Methods:**
- `is_path()`: Check if identifier contains path separator
- `add_block()`: Add content block to section
- `add_subsection()`: Add nested section
- `create_subsection()`: Create and add new subsection with optional content
- `to_dict()`: Convert to dictionary structure
- `to_text()`: Convert to markdown text representation

---

### Block

Individual content element (paragraph, code, list, etc.).

```python
class Block:
    def __init__(self, section_id: str, block_type: BlockType, content: str | list[str]) -> None

    # Properties
    @property
    def section: str
    @property
    def type: BlockType
    @property
    def content: str | list[str]
    @property
    def metadata: BlockMetadata

    # Serialization
    def to_dict(self) -> BlockData
    def to_text(self) -> str
```

**Parameters:**
- `section_id`: ID of containing section (required)
- `block_type`: Type from BlockType enum (required)
- `content`: Block content as string or list of strings (required)

**Methods:**
- `to_dict()`: Convert to dictionary structure
- `to_text()`: Convert to markdown text representation

---

## Data Types

### TypedDict Interfaces

All data structures use TypedDict for type safety and JSON serialization.

#### MarkdownDataDict
Complete document structure for JSON export.
```python
class MarkdownDataDict(TypedDict):
    frontmatter: dict[str, Any]  # Document metadata
    content: SectionData         # Root section data
```

#### SectionData
Structured data for individual sections.
```python
class SectionData(TypedDict):
    id: str                           # Section identifier
    title: str                        # Section heading
    level: int                        # Heading level (1-6)
    path: str                         # Hierarchical path
    blocks: list[BlockData] | None    # Content blocks
    subsections: list[SectionData] | None  # Nested sections
```

#### SectionsData
Collection of sections with lookup index.
```python
class SectionsData(TypedDict):
    sections: list[SectionData]              # All sections as list
    sections_by_id: dict[str, SectionData]   # Sections indexed by ID
```

#### BlockData
Structured data for individual blocks.
```python
class BlockData(TypedDict):
    section_id: str                    # Parent section ID
    type: str                          # Block type (BlockType value)
    content: str | list[str]           # Block content
    metadata: BlockMetadata            # Additional attributes
```

#### BlocksData
Collection of blocks.
```python
class BlocksData(TypedDict):
    blocks: list[BlockData]            # All blocks as list
```

#### BlockMetadata
Optional metadata attributes for blocks.
```python
class BlockMetadata(TypedDict, total=False):
    language: str                      # For code blocks
    href: str                          # For links
    src: str                           # For images
    alt: str                           # For images
    title: str                         # For links/images
```

---

## Enums

### BlockType
Content block types in markdown.
```python
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
```

### HeadingLevel
Markdown heading levels with arithmetic support.
```python
class HeadingLevel(IntEnum):
    ROOT = 0  # Root level (no heading)
    H1 = 1    # # Heading
    H2 = 2    # ## Heading
    H3 = 3    # ### Heading
    H4 = 4    # #### Heading
    H5 = 5    # ##### Heading
    H6 = 6    # ###### Heading
```

### SectionPolicy
Section modification policies for content operations.
```python
class SectionPolicy(Enum):
    UPDATE = "update"      # Merge content preserving subsections
    REPLACE = "replace"    # Replace entire section content
    APPEND = "append"      # Add content to existing section
```

---

## Entry Points

### Package Imports
```python
# Core functionality
from md_as_data import MarkdownFile, MarkdownData

# Data structures
from md_as_data import Section, Block, ContentTree

# Type definitions
from md_as_data import (
    BlockType, HeadingLevel, SectionPolicy,
    MarkdownDataDict, SectionData, BlockData,
    SectionsData, BlocksData, BlockMetadata
)

# Advanced processing (for custom handlers and extensions)
from md_as_data import MarkdownProcessor, TokenType

```

### Command Line Interface

The library provides a modern CLI built with Typer for file manipulation:

```bash
# Install and use
uv sync --dev
uv run mdasdata <file_path> <command> [subcommand] [options]
```

**Command Groups:**
- `info`: Query and inspect document structure
- `modify`: Modify content and frontmatter properties
- `export`: Export data in various formats

**Key Features:**
- **Path-based section access**: `parent.child.grandchild` notation
- **Section policies**: `update`, `replace`, `append` for different modification behaviors
- **Rich terminal output**: Colorized, formatted display with error validation
- **Bulk operations**: JSON-based batch processing
- **Export formats**: JSON, YAML with optional pretty-printing

**Example Commands:**
```bash
# Information queries
uv run mdasdata doc.md info sections --paths
uv run mdasdata doc.md info properties --verbose

# Content modification
uv run mdasdata doc.md modify set-property title "New Title"
uv run mdasdata doc.md modify set-section intro "New content" --policy replace
uv run mdasdata doc.md modify from-json changes.json --dry-run

# Data export
uv run mdasdata doc.md export json --pretty
uv run mdasdata doc.md export frontmatter --format yaml
```

---

## Usage Patterns

### Basic Document Loading
```python
from md_as_data import MarkdownFile

# Load and access document
file = MarkdownFile('document.md')
doc = file.mddata

# Access frontmatter
print(doc.title, doc.author)

# Navigate content
intro = doc.content.introduction
overview = doc.content.get_section('introduction.overview')
```

### Document Modification
```python
# Modify frontmatter
doc.status = "published"
doc.version = "2.0"

# Save changes
file.save()  # Save to original file
file.save_as('updated.md')  # Save to new file
```

### Data Export
```python
# Get structured data
frontmatter = file.mddata.frontmatter           # Direct property access
sections = file.mddata.get_sections()           # Structured data method
blocks = file.mddata.get_blocks()               # Structured data method

# Access content tree
all_sections = file.mddata.content.get_all_sections()
all_blocks = file.mddata.content.get_all_blocks()

# Serialize
json_data = file.to_json()
markdown_text = file.to_markdown()
```

This specification covers all public interfaces available in the markdown-as-data library v1.0.