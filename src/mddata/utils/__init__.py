"""Utility functions for mddata."""

from .data_loader import (
    DataFormat,
    DataLoadError,
    load_data,
    load_data_update,
    load_markdown_data_dict,
)

# Backward compatibility alias
JSONDataError = DataLoadError

__all__ = [
    # Data loading utilities
    "load_data",
    "load_markdown_data_dict",
    "load_data_update",
    "DataLoadError",
    "DataFormat",
    # Backward compatibility
    "JSONDataError",
]
