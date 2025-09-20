"""Template models - re-exports from centralized contracts module.

This module provides backward compatibility by re-exporting template-related
types from the centralized contracts module.

Note: TemplateFile is now just a type alias for MarkdownDataUpdate.
Templates are MarkdownDataUpdate instances with parameters defined.
"""

from .contracts import (
    MarkdownDataUpdate,
    ParameterDefinition,
    ParameterValue,
    ResolvedParameters,
    TemplateFile,
)

__all__ = [
    "ParameterDefinition",
    "ParameterValue",
    "ResolvedParameters",
    "TemplateFile",
    "MarkdownDataUpdate",
]
