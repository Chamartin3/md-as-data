"""Validation submodule for md_as_data package.

Provides schema-based validation for markdown documents including
frontmatter properties, section structure, and content types.
"""

from .input_parser import InputParser, ParseResult
from .schema_generator import SchemaGenerator, generate_schema
from .schema_models import (
    DocumentSchema,
    PropertySchema,
    SchemaInferenceMode,
    SectionSchema,
    SectionValidationSchema,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    ValidationSchema,
    ValidationType,
    ValueType,
)
from .schema_property_validator import PropertyValidator
from .schema_section_validator import SectionValidator
from .schema_validator import SchemaValidator

__all__ = [
    "InputParser",
    "ParseResult",
    "SchemaValidator",
    "PropertyValidator",
    "SectionValidator",
    "SchemaGenerator",
    "generate_schema",
    "DocumentSchema",
    "PropertySchema",
    "SectionSchema",
    "SectionValidationSchema",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "ValidationSchema",
    "ValidationType",
    "ValueType",
    "SchemaInferenceMode",
]
