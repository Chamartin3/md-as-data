"""Unified document operations for rendering and modifying markdown files."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .models import MarkdownDataDict, MarkdownDataUpdate
from .schema import schema_to_markdown_dict
from .source import MarkdownFile
from .templates.filler import TemplateFiller
from .utils import DataLoadError, load_data_update, load_markdown_data_dict


# Error Types
@dataclass
class ParameterValidationError(Exception):
    """Error raised when template parameters are invalid or missing."""

    missing_params: list[str]
    provided_params: list[str]
    available_params: list[str]

    def __str__(self) -> str:
        missing = ", ".join(f"'{p}'" for p in self.missing_params)
        provided = ", ".join(f"'{p}'" for p in self.provided_params)
        available = ", ".join(f"'{p}'" for p in self.available_params)

        return (
            f"Missing required parameters: {missing}\n"
            f"Provided parameters: {provided}\n"
            f"Available parameters: {available}"
        )


@dataclass
class DataStructureError(Exception):
    """Error raised when data structure is invalid."""

    issue: str
    expected: str
    received: str

    def __str__(self) -> str:
        return (
            f"Data structure error: {self.issue}. "
            f"Expected: {self.expected}, received: {self.received}"
        )


@dataclass
class OperationResult:
    """Result of a document operation."""

    success: bool
    document: MarkdownDataDict | None = None
    errors: list[str] | None = None
    warnings: list[str] | None = None
    metadata: dict[str, Any] | None = None


# Operation Mode
class OperationMode(Enum):
    """Modes for document operations."""

    CREATE = "create"  # Create new file from data
    MODIFY = "modify"  # Modify existing file (merge)
    SCHEMA_TEMPLATE = "schema_template"  # Generate from schema only
    STDOUT = "stdout"  # Render to stdout (no file)


# Validation Functions
def validate_parameters(
    template_params: dict[str, Any], provided_params: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate that all required template parameters are provided.

    Args:
        template_params: Parameters defined in template (with defaults/types)
        provided_params: Parameters provided by user

    Returns:
        Tuple of (is_valid, missing_params)
    """
    # Extract required parameters (those without defaults)
    required_params = [
        name
        for name, config in template_params.items()
        if isinstance(config, dict) and not config.get("default")
    ]

    missing_params = [
        param
        for param in required_params
        if param not in provided_params and not _is_computed_param(param)
    ]

    return len(missing_params) == 0, missing_params


def _is_computed_param(param_name: str) -> bool:
    """Check if a parameter is computed (date, time, env.*)."""
    if param_name in ("date", "time"):
        return True
    if param_name.startswith("env."):
        return True
    return False


def load_and_validate_data(
    data_path: str | None, format_type: str = "json"
) -> tuple[MarkdownDataDict | None, MarkdownDataUpdate | None]:
    """Load and validate data from file or stdin.

    Args:
        data_path: Path to data file, or None for stdin
        format_type: Data format ('json' or 'yaml')

    Returns:
        Tuple of (MarkdownDataDict, MarkdownDataUpdate) or (None, None) on error
    """
    if not data_path:
        return None, None

    try:
        # Try loading as MarkdownDataDict first (complete document)
        try:
            data_dict = load_markdown_data_dict(data_path, format_type)
            return data_dict, None
        except DataLoadError:
            # If that fails, try loading as MarkdownDataUpdate (partial updates)
            try:
                data_update = load_data_update(data_path, format_type)
                return None, data_update
            except DataLoadError:
                # Both failed
                return None, None
    except Exception:
        # Any other error
        return None, None


# Operation Mode Detection
def determine_operation_mode(
    data: str | None, schema: str | None, target_file: Path | None, output: str | None
) -> OperationMode:
    """Determine the operation mode based on provided arguments.

    Args:
        data: Data source path
        schema: Schema path
        target_file: Target file for modification
        output: Output file path

    Returns:
        Detected operation mode
    """
    # STDOUT mode: data provided but no output file
    if data and not output and not target_file:
        return OperationMode.STDOUT

    # SCHEMA_TEMPLATE mode: only schema provided with output
    if not data and schema and output:
        return OperationMode.SCHEMA_TEMPLATE

    # MODIFY mode: target file exists and data provided
    if target_file and data and Path(target_file).exists():
        return OperationMode.MODIFY

    # CREATE mode: default for data + output
    if data and output:
        return OperationMode.CREATE

    # Default fallback
    return OperationMode.CREATE


# Document Operations
def write_document(
    data: MarkdownDataDict | MarkdownDataUpdate | None = None,
    schema: dict[str, Any] | None = None,
    target_file: Path | None = None,
    output_file: Path | None = None,
    operation_mode: OperationMode = OperationMode.CREATE,
    parameters: dict[str, Any] | None = None,
    policy: str = "update",
) -> OperationResult:
    """Unified write function delegating to mode-specific handlers.

    Args:
        data: Document data to write
        schema: Schema for validation/template generation
        target_file: File to modify (for MODIFY mode)
        output_file: File to create/write (for CREATE/SCHEMA_TEMPLATE modes)
        operation_mode: Operation mode
        parameters: Template parameters
        policy: Merge policy

    Returns:
        OperationResult with success status and metadata
    """
    try:
        if operation_mode == OperationMode.CREATE:
            return _create_new_document(data, schema, output_file, parameters)
        elif operation_mode == OperationMode.MODIFY:
            return _modify_existing_document(data, target_file, policy)
        elif operation_mode == OperationMode.SCHEMA_TEMPLATE:
            return _create_schema_template(schema, output_file)
        elif operation_mode == OperationMode.STDOUT:
            return _render_to_stdout(data, schema, parameters)
        else:
            return OperationResult(
                success=False, errors=[f"Unknown operation mode: {operation_mode}"]
            )
    except Exception as e:
        return OperationResult(success=False, errors=[f"Operation failed: {str(e)}"])


def _create_new_document(
    data: MarkdownDataDict | MarkdownDataUpdate,
    schema: dict[str, Any] | None,
    output_file: Path,
    parameters: dict[str, Any] | None,
) -> OperationResult:
    """Create new document from data/template/schema."""
    try:
        # Handle MarkdownDataUpdate (template) vs MarkdownDataDict (complete data)
        if isinstance(data, MarkdownDataUpdate):
            # Fill template with parameters if provided
            if parameters:
                filler = TemplateFiller(data)
                filled_data = filler.fill(parameters)
                document_data = filled_data.as_markdown_dict()
            else:
                document_data = data.as_markdown_dict()
        else:
            # Already a complete MarkdownDataDict
            document_data = data

        # Create markdown file
        markdown_file = MarkdownFile.from_dict(document_data)
        markdown_file.save(output_file)

        return OperationResult(
            success=True,
            document=document_data,
            metadata={"output_file": str(output_file), "mode": "create"},
        )
    except Exception as e:
        return OperationResult(
            success=False, errors=[f"Failed to create document: {str(e)}"]
        )


def _modify_existing_document(
    data: MarkdownDataDict | MarkdownDataUpdate, target_file: Path, policy: str
) -> OperationResult:
    """Modify existing document with merge support."""
    try:
        # Load existing document
        existing_doc = MarkdownFile(target_file)

        # Apply updates based on data type
        if isinstance(data, MarkdownDataUpdate):
            # Apply batch changes
            existing_doc.apply_update(data, policy)
        else:
            # Replace entire document (not typical for modify mode)
            existing_doc = MarkdownFile.from_data(data)

        # Save changes
        existing_doc.save(target_file)

        return OperationResult(
            success=True,
            document=existing_doc.mddata.data,
            metadata={
                "target_file": str(target_file),
                "mode": "modify",
                "policy": policy,
            },
        )
    except Exception as e:
        return OperationResult(
            success=False, errors=[f"Failed to modify document: {str(e)}"]
        )


def _create_schema_template(
    schema: dict[str, Any], output_file: Path
) -> OperationResult:
    """Generate template from schema."""
    try:
        # Convert schema to markdown template
        template_data = schema_to_markdown_dict(schema)

        # Create and save markdown file
        markdown_file = MarkdownFile.from_dict(template_data)
        markdown_file.save(output_file)

        return OperationResult(
            success=True,
            document=template_data,
            metadata={"output_file": str(output_file), "mode": "schema_template"},
        )
    except Exception as e:
        return OperationResult(
            success=False, errors=[f"Failed to create schema template: {str(e)}"]
        )


def _render_to_stdout(
    data: MarkdownDataDict | MarkdownDataUpdate,
    schema: dict[str, Any] | None,
    parameters: dict[str, Any] | None,
) -> OperationResult:
    """Render document to stdout without file creation."""
    try:
        # Handle MarkdownDataUpdate (template) vs MarkdownDataDict (complete data)
        if isinstance(data, MarkdownDataUpdate):
            # Fill template with parameters if provided
            if parameters:
                filler = TemplateFiller(data)
                filled_data = filler.fill(parameters)
                document_data = filled_data.as_markdown_dict()
            else:
                document_data = data.as_markdown_dict()
        else:
            # Already a complete MarkdownDataDict
            document_data = data

        # Create markdown file and render to stdout
        markdown_file = MarkdownFile.from_dict(document_data)
        rendered_content = markdown_file.to_markdown()

        # In a real CLI, this would print to stdout
        # For now, return it in metadata
        return OperationResult(
            success=True,
            document=document_data,
            metadata={"rendered_content": rendered_content, "mode": "stdout"},
        )
    except Exception as e:
        return OperationResult(
            success=False, errors=[f"Failed to render to stdout: {str(e)}"]
        )


# Public API
__all__ = [
    # Error types
    "ParameterValidationError",
    "DataStructureError",
    "OperationResult",
    # Operation mode
    "OperationMode",
    # Validation functions
    "validate_parameters",
    "load_and_validate_data",
    # Operation mode detection
    "determine_operation_mode",
    # Document operations
    "write_document",
]
