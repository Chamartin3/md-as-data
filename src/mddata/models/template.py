"""Template parameter types for markdown templates.

This module contains types related to parameterized templates:
- Parameter definitions and values
- Parameter type specifications
- Resolved parameter collections
"""

from typing import TypeAlias, TypedDict

from .base import ParameterType

# =============================================================================
# Parameter Value Types
# =============================================================================

# Parameter value types - simpler than full FrontmatterValue
ParameterValue: TypeAlias = str | int | float | bool | list[str] | None


# =============================================================================
# Parameter Definitions
# =============================================================================


class ParameterDefinition(TypedDict, total=False):
    """Parameter definition in template.

    A template parameter specifies how values should be provided and validated
    when applying a template to a markdown document.
    """

    type: ParameterType  # Required - data type of the parameter
    required: bool  # Optional - whether parameter must be provided
    default: ParameterValue  # Optional - default value if not provided
    description: str  # Optional - human-readable description

    # Type-specific validation constraints
    min: int | float  # Optional - minimum value for int/float
    max: int | float  # Optional - maximum value for int/float
    pattern: str  # Optional - regex pattern for str validation
    item_type: ParameterType  # Optional - type of array items

    # Enum support
    enum: list[str | int | float | bool | None]  # Optional - allowed values
    enum_descriptions: dict[str, str]  # Optional - descriptions for enum values
    enum_strict: bool  # Optional - error (True) or warn (False) on invalid values

    # Array constraints
    min_items: int  # Optional - minimum number of array items
    max_items: int  # Optional - maximum number of array items
    unique_items: bool  # Optional - whether array items must be unique

    # Array item enum support
    item_enum: list[str | int | float | bool | None]  # Optional - allowed item values
    item_enum_descriptions: dict[str, str]  # Optional - item enum descriptions
    item_enum_strict: bool  # Optional - error (True) or warn (False) on invalid items

    # Pattern validation for array items
    item_pattern: str  # Optional - regex pattern for array item validation


# Type alias for resolved parameter values
ResolvedParameters: TypeAlias = dict[str, ParameterValue]


__all__ = [
    "ParameterType",
    "ParameterValue",
    "ParameterDefinition",
    "ResolvedParameters",
]
