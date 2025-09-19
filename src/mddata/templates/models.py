"""Template models - re-exports from centralized models package.

This module provides backward compatibility by re-exporting template-related
types from the centralized models package.
"""

from mddata.models import (
    ParameterDefinition,
    ParameterType,
    ParameterValue,
    ResolvedParameters,
    TemplateFile,
)

__all__ = [
    "ParameterType",
    "ParameterDefinition",
    "TemplateFile",
    "ResolvedParameters",
    "ParameterValue",
]
