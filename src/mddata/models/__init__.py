"""Centralized data models for mddata.

This package provides a clean vertical dependency structure:

Level 0: base.py - Base types and enums
Level 1: document.py - Document structures
Level 2: schema.py, template.py - Validation and parameterization (parallel)
Level 3: update.py - Update operations and results
Level 4: data.py - Data interchange contracts

Only types used outside this package are exported.
"""

# Level 0: Base types and enums
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

# Level 4: Data interchange contracts
from .data import MarkdownDataDict

# Level 1: Document structure models
from .document import (
    Block,
    BlockData,
    BlockMetadata,
    BlocksData,
    BlocksQuery,
    ContentInput,
    ContentTree,
    ParsedMarkdownData,
    PathQuery,
    Section,
    SectionBlocksData,
    SectionContentData,
    SectionData,
    SectionInputData,
    SectionQuery,
    SectionsData,
    SectionsMap,
    TaskItemData,
)

# Level 2: Template parameter types
from .forms import (
    MarkdownFormField,  # New primary name
    ParameterDefinition,  # Backward compatibility alias
    ParameterValue,
    ResolvedParameters,
)

# Level 3: Update operation types
from .update import (
    BatchOperationResult,
    InputDataDictOptions,
    InputDataOptions,
    InputDictSectionContent,
    InputDictSectionData,
    InputDictSectionObject,
    MarkdownDataUpdate,
    MarkdownForm,
    SectionUpdate,
    UpdateInputDict,
)

# Schema types are in separate subpackage for organization
# Import as: from mddata.models.schema import ...

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
    "PathQuery",
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
    # Template parameter types
    "MarkdownFormField",
    "ParameterDefinition",  # Deprecated
    "ParameterValue",
    "ResolvedParameters",
    # Update operation types
    "UpdateInputDict",
    "InputDictSectionContent",
    "InputDictSectionData",
    "InputDictSectionObject",
    "InputDataDictOptions",
    "SectionUpdate",
    "BatchOperationResult",
    "MarkdownDataUpdate",
    "MarkdownForm",
    # Data interchange contracts
    "MarkdownDataDict",
]
