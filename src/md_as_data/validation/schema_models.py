"""Schema data structures for markdown document validation."""

from enum import StrEnum
from typing import Any, Literal, TypedDict

from ..models import BlockType, FrontmatterValue


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


class SectionValidationSchema(TypedDict, total=False):
    """Schema definition for section-level validations."""

    allowed_content: list[BlockType]
    max_blocks: int
    min_blocks: int
    required: bool


class SectionSchema(TypedDict, total=False):
    """Schema definition for content sections."""

    subsections: dict[str, "SectionSchema"]
    description: str
    validation: SectionValidationSchema


class DocumentSchema(TypedDict):
    """Complete document schema definition."""

    frontmatter: dict[str, PropertySchema]
    sections: dict[str, SectionSchema]
    validation_level: ValidationLevel


class ValidationIssue(TypedDict):
    """Individual validation issue."""

    field_type: Literal["frontmatter", "section"]
    field: str  # Property/section path
    message: str
    expected: str | None
    actual: str | None


class ValidationResult(TypedDict):
    """Result of schema validation."""

    valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
