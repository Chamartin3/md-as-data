"""Unified data contract models for mddata.

This module consolidates the key data contract types used across the application:
- BatchChanges: Batch modification operations
- MarkdownDataDict: Complete document structure for JSON export
- TemplateFile: Template-based document generation
- DocumentSchema: Schema validation definitions

These TypedDict definitions serve as data contracts between different modules,
ensuring consistent data exchange formats throughout the application.
"""

from typing import Any, TypeAlias, TypedDict

from .base import (
    BlockType,
    FrontmatterPropertyValue,
    FrontmatterValue,
    ParameterType,
    UpdatePolicy,
)

# Re-export for convenience
from .document import SectionData

# =============================================================================
# Batch Operations Data Contracts
# =============================================================================


class SectionUpdate(TypedDict, total=False):
    """Structure for section update in batch operation.

    Used to specify changes to a single section within a BatchChanges operation.
    """

    id: str  # Required - section identifier or path
    content: str  # Required - new content for the section
    policy: str | UpdatePolicy  # Optional - update policy (defaults to UPDATE)


class BatchChanges(TypedDict, total=False):
    """Structure for batch changes to document.

    Enables atomic updates to multiple document parts (frontmatter and sections)
    in a single operation. Used by CLI modify from-json and Python API.
    """

    frontmatter: dict[str, FrontmatterPropertyValue]  # Properties to update
    frontmatter_policy: str | UpdatePolicy  # How to apply frontmatter updates
    sections: list[SectionUpdate]  # Section updates to apply


# =============================================================================
# Document Export Data Contracts
# =============================================================================


class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON/YAML export.

    This is the canonical serialization format for markdown documents,
    used by extract commands and API export methods.
    """

    frontmatter: dict[str, FrontmatterPropertyValue]
    content: SectionData  # Root section with complete hierarchy


# =============================================================================
# Template Data Contracts
# =============================================================================

# Parameter value types
ParameterValue: TypeAlias = str | int | float | bool | list[str] | None


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


class TemplateFile(TypedDict):
    """Complete template file structure.

    A template file defines parameters and the changes to apply to a document
    when those parameters are provided. Used for parameterized document generation.
    """

    parameters: dict[str, ParameterDefinition]  # Parameter definitions by name
    changes: BatchChanges  # Document changes to apply


# Type alias for resolved parameter values
ResolvedParameters: TypeAlias = dict[str, ParameterValue]


# =============================================================================
# Schema Validation Data Contracts
# =============================================================================


class PropertyValidationSchema(TypedDict):
    """Schema definition for property validations.

    Defines validation rules for frontmatter properties.
    """

    type: str  # PropertyValidationType enum value
    value: Any  # Validation constraint value
    message: str  # Custom error message


class PropertySchema(TypedDict, total=False):
    """Schema definition for frontmatter properties.

    Specifies type, requirements, and validation rules for a property.
    """

    type: str  # ValueType enum value
    required: bool  # Whether property is required
    default: FrontmatterValue  # Default value if not provided
    validations: list[PropertyValidationSchema]  # Validation rules
    description: str  # Optional property description
    enum: list[str | None]  # Allowed enum values for property


class SectionValidationSchema(TypedDict, total=False):
    """Schema definition for section-level validations.

    Specifies content constraints and requirements for sections.
    """

    allowed_content: list[BlockType]  # Allowed block types
    max_blocks: int  # Maximum number of blocks
    min_blocks: int  # Minimum number of blocks
    required: bool  # Whether section is required


class SectionSchema(TypedDict, total=False):
    """Schema definition for content sections.

    Defines structure and validation rules for document sections.
    """

    children: dict[str, "SectionSchema"]  # Nested section schemas
    description: str  # Section description
    validation: SectionValidationSchema  # Validation rules


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
