"""Schema type definitions for markdown document validation.

This module contains all schema-related models and should be imported
as 'from mddata.models.schemas import ...'
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, TypedDict

from ..base import BlockType, FrontmatterValue
from .validation import ValidationIssue, ValidationIssueTypes, ValidationResult

# Schema version constant for tracking schema evolution
CURRENT_SCHEMA_VERSION = "1.0.0"


class SchemaFieldNames:
    """Constants for schema field names."""

    VERSION = "version"
    PROPERTIES = "properties"
    SECTIONS = "sections"
    CHILDREN = "children"
    VALIDATION = "validation"


class SchemaInferenceMode(StrEnum):
    """Modes for inferring schema from existing documents."""

    STRICT = "strict"  # Infer strict constraints based on data
    PERMISSIVE = "permissive"  # Infer basic types, allow flexibility


class ValueType(StrEnum):
    """Supported value types for frontmatter properties."""

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"
    DATE = "date"
    DATETIME = "datetime"

    def get_default_placeholder(self) -> FrontmatterValue:
        """
        Get default placeholder value for this type.

        Returns:
            Appropriate placeholder value for the type
        """
        if self == ValueType.STRING:
            return "[Placeholder text]"
        elif self == ValueType.INTEGER:
            return 0
        elif self == ValueType.FLOAT:
            return 0.0
        elif self == ValueType.BOOLEAN:
            return False
        elif self == ValueType.LIST:
            return []
        elif self == ValueType.DATE:
            return "YYYY-MM-DD"
        elif self == ValueType.DATETIME:
            return "YYYY-MM-DDTHH:MM:SS"
        else:
            return "[Placeholder]"


class ValidationLevel(StrEnum):
    """Validation strictness levels."""

    STRICT = "strict"  # Raise errors on validation failures
    WARNINGS = "warnings"  # Collect warnings but don't fail
    DISABLED = "disabled"  # Skip validation entirely


### Property Validation Types ##############################
class PropertyValidationType(StrEnum):
    """Types of validations for frontmatter properties."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    REGEX = "regex"
    ALLOWED_VALUES = "allowed_values"


class PropertyValidationSchema(TypedDict):
    """Schema definition for validations."""

    type: PropertyValidationType
    value: Any
    message: str  # Custom error message


class PropertySchema(TypedDict, total=False):
    """Schema definition for frontmatter properties."""

    type: str  # ValueType enum value
    required: bool
    default: FrontmatterValue
    validations: list[PropertyValidationSchema]
    description: str  # Optional property description
    enum: list[str | None]  # Allowed enum values for property


### Section Validation types ##############################


class SectionValidationSchema(TypedDict, total=False):
    """Schema definition for section-level validations."""

    allowed_content: list[BlockType]
    max_blocks: int
    min_blocks: int
    required: bool


class SectionSchema(TypedDict, total=False):
    """Schema definition for content sections."""

    children: dict[str, "SectionSchema"]  # Renamed from subsections
    description: str
    validation: SectionValidationSchema


### Complete Document Schema ##############################
class DocumentSchema(TypedDict, total=False):
    """Complete document schema definition.

    Note: validation_level was removed in favor of runtime configuration.
    Pass validation_level to SchemaValidator constructor instead.
    """

    version: str | None
    properties: dict[str, PropertySchema]  # Renamed from frontmatter
    sections: dict[str, SectionSchema]


@dataclass
class DocumentSchemaObj:
    """Complete document schema definition."""

    version: str | None = None
    properties: dict[str, PropertySchema] = None
    sections: dict[str, SectionSchema] = None

    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.properties is None:
            self.properties = {}
        if self.sections is None:
            self.sections = {}


__all__ = [
    # Constants
    "CURRENT_SCHEMA_VERSION",
    "SchemaFieldNames",
    # Enums
    "SchemaInferenceMode",
    "ValueType",
    "ValidationLevel",
    "PropertyValidationType",
    # Type definitions
    "PropertyValidationSchema",
    "PropertySchema",
    "SectionValidationSchema",
    "SectionSchema",
    "DocumentSchema",
    "DocumentSchemaObj",
    # Validation models (re-exported from .validation)
    "ValidationIssueTypes",
    "ValidationIssue",
    "ValidationResult",
]
