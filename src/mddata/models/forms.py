"""Form field definitions for MarkdownForm parameters."""

from typing import Any, TypeAlias, TypedDict

# =============================================================================
# Parameter Value Types
# =============================================================================

# Parameter value types - simpler than full FrontmatterValue
ParameterValue: TypeAlias = str | int | float | bool | list[str] | None


# =============================================================================
# Form Field Definitions
# =============================================================================


class MarkdownFormField(TypedDict, total=False):
    """Form field definition with validation rules.

    Form fields define parameters that users must fill when using a form.
    Each field specifies type, validation constraints, and optional defaults.

    Example:
        {
            "type": "str",
            "required": True,
            "description": "Document title",
            "min": 5,
            "max": 100
        }
    """

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
    item_enum: list[Any]
    item_enum_strict: bool
    item_enum_descriptions: dict[str, str]
    item_pattern: str


# Backward compatibility alias
ParameterDefinition = MarkdownFormField


# Type alias for resolved parameter values
ResolvedParameters: TypeAlias = dict[str, ParameterValue]


__all__ = [
    "MarkdownFormField",
    "ParameterDefinition",  # Backward compatibility
    "ParameterValue",
    "ResolvedParameters",
]
