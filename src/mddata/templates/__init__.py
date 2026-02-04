"""Form filling functionality for markdown data generation.

Public API:
- MarkdownFormFiller: Fill forms with parameters
- TemplateFiller: Backward compatibility alias
- ComputedParam: Enum of available computed parameters
- Models: Re-exported from centralized contracts

Note: Form loading is now handled by the unified data loader in mddata.utils
"""

from ..models import (
    MarkdownFormField,
    ParameterType,
    ParameterValue,
    ResolvedParameters,
)
from .filler import ComputedParam, MarkdownFormFiller, TemplateFiller

__all__ = [
    # Template filling
    "MarkdownFormFiller",
    "TemplateFiller",  # Backward compatibility
    "ComputedParam",
    # Type definitions
    "ParameterType",
    "MarkdownFormField",
    "ParameterValue",
    "ResolvedParameters",
]
