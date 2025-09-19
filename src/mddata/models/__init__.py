"""Centralized data models for mddata."""

# Base types and enums
from .base import (
    BlockType,
    FrontmatterProperties,
    FrontmatterProperty,
    FrontmatterPropertyValue,
    FrontmatterValue,
    HeadingLevel,
    ParameterType,
    UpdatePolicy,
)

# Document structure models
from .document import (
    BatchChanges,
    BatchOperationResult,
    Block,
    BlockData,
    BlockMetadata,
    BlocksData,
    BlocksQuery,
    ContentInput,
    ContentTree,
    InputDataOptions,
    MarkdownDataDict,
    ParsedMarkdownData,
    Section,
    SectionBlocksData,
    SectionContentData,
    SectionData,
    SectionInputData,
    SectionQuery,
    SectionsData,
    SectionsMap,
    SectionUpdate,
    TaskItemData,
)

# Schema models
from .schema import (
    CURRENT_SCHEMA_VERSION,
    DocumentSchema,
    DocumentSchemaObj,
    PropertySchema,
    PropertyValidationSchema,
    PropertyValidationType,
    SchemaFieldNames,
    SchemaInferenceMode,
    SectionSchema,
    SectionValidationSchema,
    ValidationLevel,
    ValueType,
)

# Template models
from .template import (
    ParameterDefinition,
    ParameterValue,
    ResolvedParameters,
    TemplateFile,
)

# Validation result models
from .validation import (
    ValidationIssue,
    ValidationIssueTypes,
    ValidationResult,
)

__all__ = [
    # Base types and enums
    "BlockType",
    "HeadingLevel",
    "UpdatePolicy",
    "ParameterType",
    "FrontmatterValue",
    "FrontmatterProperties",
    "FrontmatterPropertyValue",
    "FrontmatterProperty",
    # Document models
    "SectionQuery",
    "BlocksQuery",
    "TaskItemData",
    "BlockMetadata",
    "BlockData",
    "Block",
    "BlocksData",
    "SectionData",
    "SectionsData",
    "Section",
    "SectionsMap",
    "ContentInput",
    "InputDataOptions",
    "ContentTree",
    "ParsedMarkdownData",
    "MarkdownDataDict",
    "SectionInputData",
    "SectionContentData",
    "SectionBlocksData",
    "SectionUpdate",
    "BatchChanges",
    "BatchOperationResult",
    # Schema models
    "CURRENT_SCHEMA_VERSION",
    "SchemaFieldNames",
    "SchemaInferenceMode",
    "ValueType",
    "ValidationLevel",
    "PropertyValidationType",
    "PropertyValidationSchema",
    "PropertySchema",
    "SectionValidationSchema",
    "SectionSchema",
    "DocumentSchema",
    "DocumentSchemaObj",
    # Validation models
    "ValidationIssueTypes",
    "ValidationIssue",
    "ValidationResult",
    # Template models
    "ParameterDefinition",
    "ParameterValue",
    "ResolvedParameters",
    "TemplateFile",
]
