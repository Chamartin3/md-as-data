"""Validation submodule for md_as_data package.

Provides schema-based validation for markdown documents including
frontmatter properties, section structure, and content types.
"""

from .generator import SchemaGenerator, generate_schema
from .schema_models import (
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
from .schema_property_validator import PropertyValidator
from .schema_section_validator import SectionValidator
from .schema_validator import SchemaValidator

__all__ = [
    "SchemaValidator",
    "PropertyValidator",
    "SectionValidator",
    "SchemaGenerator",
    "generate_schema",
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
