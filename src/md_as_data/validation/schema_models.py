"""Schema data structures for markdown document validation."""

from enum import StrEnum
from typing import Any, Literal, TypedDict

from ..models import BlockType, FrontmatterValue

# Schema version constant for tracking schema evolution
CURRENT_SCHEMA_VERSION = "1.0.0"


class SchemaFieldNames:
    """Constants for schema field names."""

    VERSION = "version"
    PROPERTIES = "properties"
    SECTIONS = "sections"
    CHILDREN = "children"
    VALIDATION = "validation"


class ValidationIssueTypes:
    """Constants for validation issue types."""

    PROPERTY = "property"
    SECTION = "section"


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


class ValidationLevel(StrEnum):
    """Validation strictness levels."""

    STRICT = "strict"  # Raise errors on validation failures
    WARNINGS = "warnings"  # Collect warnings but don't fail
    DISABLED = "disabled"  # Skip validation entirely


class ValidationType(StrEnum):
    """Types of validations for frontmatter properties."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    REGEX = "regex"
    ALLOWED_VALUES = "allowed_values"


class ValidationSchema(TypedDict):
    """Schema definition for validations."""

    type: ValidationType
    value: Any
    message: str  # Custom error message


class PropertySchema(TypedDict, total=False):
    """Schema definition for frontmatter properties."""

    type: str  # ValueType enum value
    required: bool
    default: FrontmatterValue
    validations: list[ValidationSchema]
    description: str  # Optional property description
    enum: list[str | None]  # Allowed enum values for property


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


class DocumentSchema(TypedDict, total=False):
    """Complete document schema definition."""

    version: str  # Optional schema version for tracking evolution
    properties: dict[str, PropertySchema]  # Renamed from frontmatter
    sections: dict[str, SectionSchema]
    validation_level: ValidationLevel  # Will be deprecated - move to runtime config


class ValidationIssue(TypedDict):
    """Individual validation issue."""

    field_type: Literal[
        "property", "section"
    ]  # Updated from "frontmatter" to "property"
    field: str  # Property/section path
    message: str
    expected: str | None
    actual: str | None


class ValidationResult(TypedDict):
    """Result of schema validation."""

    valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
