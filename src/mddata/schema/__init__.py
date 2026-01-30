"""Validation submodule for md_as_data package.

Provides schema-based validation for markdown documents including
frontmatter properties, section structure, and content types.
"""

from ..models.schema import (
    DocumentSchema,
    PropertySchema,
    PropertyValidationSchema,
    PropertyValidationType,
    SchemaInferenceMode,
    SectionSchema,
    SectionValidationSchema,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    ValueType,
)
from .generator import SchemaGenerator, generate_schema
from .schema_loader import load_schema
from .schema_property_validator import PropertyValidator
from .schema_section_validator import SectionValidator
from .schema_structure_validator import (
    SchemaValidationError,
    validate_schema_structure,
)
from .schema_to_data import schema_to_markdown_dict
from .schema_validator import SchemaValidator

__all__ = [
    "SchemaValidator",
    "PropertyValidator",
    "SectionValidator",
    "SchemaGenerator",
    "generate_schema",
    "schema_to_markdown_dict",
    "load_schema",
    "validate_schema_structure",
    "SchemaValidationError",
    "DocumentSchema",
    "PropertySchema",
    "SectionSchema",
    "PropertyValidationSchema",
    "SectionValidationSchema",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "PropertyValidationType",
    "ValueType",
    "SchemaInferenceMode",
]
