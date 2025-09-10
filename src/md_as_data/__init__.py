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
    FrontmatterProperties,
    FrontmatterValue,
    HeadingLevel,
    MarkdownDataDict,
    # Core classes
    Section,
    SectionData,
    SectionPolicy,
    SectionsData,
)

# Advanced processing (for custom handlers and extensions)
from .processor import (
    MarkdownProcessor,
    TokenType,
)
from .source import MarkdownFile

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
    "SectionPolicy",
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
]

# Version info
__version__ = "1.0.0"
__author__ = "md_as_data"
