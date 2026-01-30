"""Unified data contract models for mddata.

This module consolidates the key data contract types used across the application:
- MarkdownDataDict: Complete document structure for JSON export
- MarkdownDataUpdate: Document update operations (replaces BatchChanges)
- DocumentSchema: Schema validation definitions

These definitions serve as data contracts between different modules,
ensuring consistent data exchange formats throughout the application.
"""

from dataclasses import dataclass, field
from typing import Any, TypeAlias, TypedDict

from .base import (
    BlockType,
    FrontmatterProperties,
    FrontmatterValue,
    ParameterType,
    UpdatePolicy,
)

# Re-export for convenience
from .document import SectionData, SectionUpdate

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

    # Enum support
    enum: list[str | int | float | bool | None]  # Optional - allowed values
    enum_descriptions: dict[str, str]  # Optional - descriptions for enum values
    enum_strict: bool  # Optional - strict mode for enum validation

    # Array constraints
    min_items: int  # Optional - minimum number of array items
    max_items: int  # Optional - maximum number of array items
    unique_items: bool  # Optional - whether array items must be unique

    # Array item enum support
    item_enum: list[str | int | float | bool | None]  # Optional - array item enum
    item_enum_descriptions: dict[str, str]  # Optional - item enum descriptions
    item_enum_strict: bool  # Optional - strict mode for item enum validation

    # Pattern validation for array items
    item_pattern: str  # Optional - regex pattern for array item validation


# =============================================================================
# Document Export Data Contracts
# =============================================================================


class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON/YAML export.

    This is the canonical serialization format for markdown documents,
    used by extract commands and API export methods.
    """

    frontmatter: FrontmatterProperties  # Document frontmatter properties
    content: SectionData  # Root section with complete hierarchy


# =============================================================================
# Document Update Data Contracts
# =============================================================================


@dataclass
class MarkdownDataUpdate:
    """Document update operations with optional policies and parameters.

    This dataclass composes MarkdownDataDict to provide update functionality
    while minimizing duplication. It represents both simple updates (from JSON)
    and parameterized templates.

    Design Philosophy:
    - Inherits structure from MarkdownDataDict through composition
    - Adds update-specific metadata (policies, parameters)
    - Supports both flat section lists (backward compat) and hierarchical content
    - Replaces both BatchChanges and TemplateFile with single unified model

    Backward Compatibility:
    - Old BatchChanges JSON maps directly to this structure
    - Optional parameters field makes templates just special cases
    - Flat sections list maintained for backward compatibility
    """

    # Core document data (from MarkdownDataDict)
    frontmatter: FrontmatterProperties = field(default_factory=dict)
    content: SectionData | None = field(default=None)

    # Update-specific metadata
    frontmatter_policy: UpdatePolicy = UpdatePolicy.MERGE
    parameters: dict[str, ParameterDefinition] = field(default_factory=dict)

    # Backward compatibility: flat section list (legacy BatchChanges format)
    sections: list[SectionUpdate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON/YAML serialization."""
        result: dict[str, Any] = {
            "frontmatter": self.frontmatter,
            "frontmatter_policy": (
                self.frontmatter_policy.value
                if isinstance(self.frontmatter_policy, UpdatePolicy)
                else self.frontmatter_policy
            ),
        }

        if self.content:
            result["content"] = self.content

        if self.sections:
            # Convert SectionUpdate dataclasses to dicts
            result["sections"] = [
                section.to_dict() if hasattr(section, "to_dict") else section
                for section in self.sections
            ]

        if self.parameters:
            result["parameters"] = self.parameters

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarkdownDataUpdate":
        """Create from dictionary (JSON/YAML deserialization).

        Supports both new format and legacy BatchChanges format.
        """
        # Parse policy
        policy_value = data.get("frontmatter_policy", "merge")
        if isinstance(policy_value, str):
            policy = UpdatePolicy[policy_value.upper()]
        else:
            policy = policy_value

        # Parse sections - convert dicts to SectionUpdate dataclasses
        sections_data = data.get("sections", [])
        sections = [
            SectionUpdate.from_dict(section) if isinstance(section, dict) else section
            for section in sections_data
        ]

        return cls(
            frontmatter=data.get("frontmatter", {}),
            content=data.get("content"),
            frontmatter_policy=policy,
            parameters=data.get("parameters", {}),
            sections=sections,
        )

    def as_markdown_dict(self) -> MarkdownDataDict:
        """Convert to MarkdownDataDict (for document export).

        Only includes core document structure, strips update metadata.
        """
        if not self.content:
            raise ValueError("Cannot convert to MarkdownDataDict without content")

        return {
            "frontmatter": self.frontmatter,
            "content": self.content,
        }

    def is_template(self) -> bool:
        """Check if this update has parameters (is a template)."""
        return bool(self.parameters)

    def has_hierarchical_content(self) -> bool:
        """Check if using new hierarchical content format."""
        return self.content is not None

    def has_flat_sections(self) -> bool:
        """Check if using legacy flat sections format."""
        return bool(self.sections)


# =============================================================================
# Template Type Aliases (Backward Compatibility)
# =============================================================================

# Templates are just MarkdownDataUpdate instances with parameters
# This alias maintains backward compatibility for existing code
TemplateFile: TypeAlias = MarkdownDataUpdate

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
