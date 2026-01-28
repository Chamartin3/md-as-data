"""Template functionality for markdown data generation.

Public API:
- TemplateFiller: Fill templates with parameters
- ComputedParam: Enum of available computed parameters
- Models: Re-exported from centralized contracts

Note: Template loading is now handled by the unified data loader in mddata.utils
"""

from ..models import ParameterType
from ..models.contracts import (
    ParameterDefinition,
    ParameterValue,
    ResolvedParameters,
    TemplateFile,
)
from .filler import ComputedParam, TemplateFiller

__all__ = [
    # Template filling
    "TemplateFiller",
    "ComputedParam",
    # Type definitions
    "ParameterType",
    "ParameterDefinition",
    "ParameterValue",
    "TemplateFile",
    "ResolvedParameters",
]
