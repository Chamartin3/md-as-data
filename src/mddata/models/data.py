"""Data interchange contracts for markdown documents.

This module contains types used for importing/exporting markdown data:
- MarkdownDataDict: Complete document export format
"""

from .base import FrontmatterProperties
from .document import SectionData

# =============================================================================
# Document Export Format
# =============================================================================


class MarkdownDataDict(dict):
    """Complete document structure for JSON/YAML export.

    This is the canonical serialization format for markdown documents,
    used by extract commands and API export methods.
    """

    frontmatter: FrontmatterProperties  # Document frontmatter properties
    content: SectionData  # Root section with complete hierarchy


__all__ = [
    "MarkdownDataDict",
]
