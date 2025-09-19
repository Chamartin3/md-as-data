"""Template models for parameter-based document generation."""

from typing import TypeAlias, TypedDict

from .base import ParameterType
from .document import BatchChanges

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
    when those parameters are provided.
    """

    parameters: dict[str, ParameterDefinition]  # Parameter definitions by name
    changes: BatchChanges  # Document changes to apply


# Type alias for resolved parameter values
ResolvedParameters: TypeAlias = dict[str, ParameterValue]
