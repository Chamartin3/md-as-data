"""Schema validation types for markdown documents.

This module consolidates all schema-related types:
- Schema structure definitions (DocumentSchema, PropertySchema, SectionSchema)
- Validation configuration (ValidationLevel, PropertyValidationType)
- Validation results (ValidationIssue, ValidationResult)
- Schema inference modes
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, TypedDict

from .base import BlockType, FrontmatterValue

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
        """Get default placeholder value for this type."""
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


# =============================================================================
# Property Validation
# =============================================================================


class PropertyValidationType(StrEnum):
    """Types of validations for frontmatter properties."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    REGEX = "regex"
    ALLOWED_VALUES = "allowed_values"


class PropertyValidationSchema(TypedDict):
    """Schema definition for property validations."""

    type: str  # PropertyValidationType enum value
    value: Any  # Validation constraint value
    message: str  # Custom error message


class PropertySchema(TypedDict, total=False):
    """Schema definition for frontmatter properties."""

    type: str  # ValueType enum value
    required: bool  # Whether property is required
    default: FrontmatterValue  # Default value if not provided
    validations: list[PropertyValidationSchema]  # Validation rules
    description: str  # Optional property description
    enum: list[str | None]  # Allowed enum values for property


# =============================================================================
# Section Validation
# =============================================================================


class SectionValidationSchema(TypedDict, total=False):
    """Schema definition for section-level validations."""

    allowed_content: list[BlockType]  # Allowed block types
    max_blocks: int  # Maximum number of blocks
    min_blocks: int  # Minimum number of blocks
    required: bool  # Whether section is required


class SectionSchema(TypedDict, total=False):
    """Schema definition for content sections."""

    children: dict[str, "SectionSchema"]  # Nested section schemas
    description: str  # Section description
    validation: SectionValidationSchema  # Validation rules


# =============================================================================
# Complete Document Schema
# =============================================================================


class DocumentSchema(TypedDict, total=False):
    """Complete document schema definition.

    This is the canonical schema format for document validation,
    used by schema generation and validation commands.

    Note: validation_level was removed in favor of runtime configuration.
    Pass validation_level to SchemaValidator constructor instead.
    """

    version: str | None  # Schema version
    properties: dict[str, PropertySchema]  # Frontmatter property schemas
    sections: dict[str, SectionSchema]  # Section schemas


@dataclass
class DocumentSchemaObj:
    """Complete document schema definition as dataclass."""

    version: str | None = None
    properties: dict[str, PropertySchema] | None = None
    sections: dict[str, SectionSchema] | None = None

    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.properties is None:
            self.properties = {}
        if self.sections is None:
            self.sections = {}


# =============================================================================
# Validation Results
# =============================================================================


class ValidationIssueTypes(StrEnum):
    """Constants for validation issue types."""

    PROPERTY = "property"
    SECTION = "section"


class ValidationIssue(TypedDict):
    """Individual validation issue."""

    field_type: str  # ValidationIssueTypes enum value
    field: str  # Property/section path
    message: str  # Error/warning message
    expected: str | None  # Expected value/format
    actual: str | None  # Actual value/format


class ValidationResult(TypedDict):
    """Result of schema validation."""

    valid: bool  # Whether validation passed
    errors: list[ValidationIssue]  # Validation errors
    warnings: list[ValidationIssue]  # Validation warnings


__all__ = [
    # Constants
    "CURRENT_SCHEMA_VERSION",
    "SchemaFieldNames",
    # Enums
    "SchemaInferenceMode",
    "ValueType",
    "ValidationLevel",
    "PropertyValidationType",
    "ValidationIssueTypes",
    # Property validation
    "PropertyValidationSchema",
    "PropertySchema",
    # Section validation
    "SectionValidationSchema",
    "SectionSchema",
    # Document schema
    "DocumentSchema",
    "DocumentSchemaObj",
    # Validation results
    "ValidationIssue",
    "ValidationResult",
]
