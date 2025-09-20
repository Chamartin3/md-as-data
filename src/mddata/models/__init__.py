"""Centralized data models for mddata.

Schema models are now in a separate subpackage.
Import them as: from mddata.models.schemas import ...
"""

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

# Data contracts (from contracts module)
from .contracts import (
    MarkdownDataDict,
    MarkdownDataUpdate,
    ParameterDefinition,
    ParameterValue,
    ResolvedParameters,
    TemplateFile,
)

# Document structure models
from .document import (
    BatchOperationResult,
    Block,
    BlockData,
    BlockMetadata,
    BlocksData,
    BlocksQuery,
    ContentInput,
    ContentTree,
    InputDataOptions,
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
    "SectionInputData",
    "SectionContentData",
    "SectionBlocksData",
    "SectionUpdate",
    "BatchOperationResult",
    # Data contracts
    "MarkdownDataDict",
    "MarkdownDataUpdate",
    "ParameterDefinition",
    "ParameterValue",
    "ResolvedParameters",
    "TemplateFile",
]
