"""mddata - Treat markdown files as structured data objects.

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
    FrontmatterProperties,
    FrontmatterValue,
    HeadingLevel,
    MarkdownDataDict,
    # Core classes
    Section,
    SectionData,
    SectionsData,
    UpdatePolicy,  # Unified policy enum
)

# Schema validation functionality
from .models.schema import (
    DocumentSchema,
    PropertySchema,
    SectionSchema,
    ValidationLevel,
)

# Advanced processing (for custom handlers and extensions)
from .processor import (
    MarkdownProcessor,
    TokenType,
)

# Schema validation and generation
from .schema import SchemaValidator, generate_schema
from .source import MarkdownFile

# Task list functionality
from .tasklist import TaskList

# Public API - Core functionality
__all__ = [
    # Main entry points
    "MarkdownFile",
    "MarkdownData",
    # Data structures
    "Section",
    "Block",
    "ContentTree",
    # Task list functionality
    "TaskList",
    # Enums
    "BlockType",
    "HeadingLevel",
    "UpdatePolicy",
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
__author__ = "mddata"
