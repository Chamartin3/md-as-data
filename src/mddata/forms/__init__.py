"""Forms module - parameterized markdown forms and filling.

This module provides functionality for working with parameterized markdown forms.
Forms are markdown documents with parameter placeholders that can be filled with
concrete values to generate complete documents.

Public API:
- MarkdownFormFiller: Fill forms with parameter values
- ComputedParam: Available computed parameters (date, time, env vars)
"""

from .filler import ComputedParam, MarkdownFormFiller

__all__ = [
    "MarkdownFormFiller",
    "ComputedParam",
]
