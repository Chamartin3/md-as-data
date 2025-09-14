"""md_as_data - Treat markdown files as structured data objects.

This package provides a clean API for parsing, manipulating, and serializing
markdown documents with programmatic access to frontmatter and content structure.
"""

# Core entry points
from .data import MarkdownData

# Data models and structures
from .models import (
    Block,
    # Type definitions for advanced usage
    BlockData,
    # Enums
    BlockType,
    ContentTree,
    FrontmatterPolicy,  # Backwards compatibility alias
    FrontmatterProperties,
    FrontmatterValue,
    HeadingLevel,
    MarkdownDataDict,
    # Core classes
    Section,
    SectionData,
    SectionPolicy,  # Backwards compatibility alias
    SectionsData,
    UpdatePolicy,  # Unified policy enum
)

# Advanced processing (for custom handlers and extensions)
from .processor import (
    MarkdownProcessor,
    TokenType,
)
from .source import MarkdownFile

# Schema validation functionality
from .validation import (
    DocumentSchema,
    PropertySchema,
    SchemaValidator,
    SectionSchema,
    ValidationLevel,
    generate_schema,
)

# Public API - Core functionality
__all__ = [
    # Main entry points
    "MarkdownFile",
    "MarkdownData",
    # Data structures
    "Section",
    "Block",
    "ContentTree",
    # Enums
    "BlockType",
    "HeadingLevel",
    "UpdatePolicy",
    "SectionPolicy",  # Backwards compatibility
    "FrontmatterPolicy",  # Backwards compatibility
    # Type definitions for advanced usage
    "BlockData",
    "SectionData",
    "SectionsData",
    "MarkdownDataDict",
    "FrontmatterProperties",
    "FrontmatterValue",
    # Processing
    "MarkdownProcessor",
    "TokenType",
    # Schema validation
    "DocumentSchema",
    "PropertySchema",
    "SectionSchema",
    "SchemaValidator",
    "ValidationLevel",
    "generate_schema",
]

# Version info
__version__ = "1.0.0"
__author__ = "md_as_data"
