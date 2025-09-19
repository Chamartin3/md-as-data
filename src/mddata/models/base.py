"""Base types and enums for mddata models."""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any, TypeVar

# Type aliases for frontmatter properties
FrontmatterValue = str | int | float | bool | list[str] | dict[str, Any] | None
FrontmatterProperties = dict[str, FrontmatterValue]

# Generic frontmatter properties type
# Type alias for frontmatter property values
FrontmatterPropertyValue = FrontmatterValue | None
FrontmatterProperty = TypeVar("FrontmatterProperty", bound=FrontmatterPropertyValue)


class BlockType(Enum):
    """Types of content blocks in markdown."""

    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    TASK_LIST = "task_list"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"


class HeadingLevel(IntEnum):
    """Heading levels in markdown."""

    ROOT = 0  # Represents the root level (no heading)
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6


class UpdatePolicy(Enum):
    """Unified policies for both frontmatter and section update operations."""

    REPLACE = "replace"  # Replace entire value/section
    UPDATE = "update"  # Update/merge while preserving structure
    MERGE = "merge"  # Smart merge with existing value
    APPEND = "append"  # Append to existing value/content


class ParameterType(str, Enum):
    """Supported parameter types for templates."""

    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATE = "date"
    ARRAY = "array"
