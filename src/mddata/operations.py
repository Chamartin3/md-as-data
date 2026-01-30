"""Unified document operations for rendering and modifying markdown files."""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .errors import DataStructureError, ParameterValidationError
from .models import MarkdownDataDict, MarkdownDataUpdate
from .schema import SchemaValidator, schema_to_markdown_dict
from .source import MarkdownFile
from .templates.filler import TemplateFiller
from .utils import DataLoadError, load_data_update, load_markdown_data_dict

# Configure logging
logger = logging.getLogger(__name__)


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
def _normalize_schema_type_names(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize schema type names and convert shorthand fields to validation rules.

    Normalizations:
    - 'array' -> 'list' for type fields
    - 'enum' field -> validation rule with type 'allowed_values'
    - 'pattern' field -> validation rule with type 'regex'

    Args:
        schema: Schema definition with potentially non-standard type names

    Returns:
        Normalized schema with standard type names and validation rules
    """
    normalized = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            # Recursively normalize nested dicts
            normalized[key] = _normalize_schema_type_names(value)

            # Normalize type field if present
            if "type" in normalized[key] and normalized[key]["type"] == "array":
                normalized[key]["type"] = "list"

            # Convert 'enum' to validation rule
            if "enum" in normalized[key]:
                enum_values = normalized[key].pop("enum")
                validations = normalized[key].get("validations", [])
                validations.append(
                    {
                        "type": "allowed_values",
                        "value": enum_values,
                        "message": (
                            f"Value must be one of: "
                            f"{', '.join(str(v) for v in enum_values)}"
                        ),
                    }
                )
                normalized[key]["validations"] = validations

            # Convert 'pattern' to validation rule
            if "pattern" in normalized[key]:
                pattern = normalized[key].pop("pattern")
                validations = normalized[key].get("validations", [])
                validations.append(
                    {
                        "type": "regex",
                        "value": pattern,
                        "message": f"Value must match pattern: {pattern}",
                    }
                )
                normalized[key]["validations"] = validations
        else:
            normalized[key] = value
    return normalized


def validate_against_schema(
    document_data: MarkdownDataDict, schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate document data against schema.

    Args:
        document_data: Document data to validate
        schema: Schema definition

    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        # Normalize schema format: 'frontmatter' -> 'properties' if needed
        normalized_schema = dict(schema)
        if "frontmatter" in normalized_schema and "properties" not in normalized_schema:
            normalized_schema["properties"] = normalized_schema.pop("frontmatter")

        # Normalize type names (array -> list)
        normalized_schema = _normalize_schema_type_names(normalized_schema)

        validator = SchemaValidator(normalized_schema)

        # Create a simple object with frontmatter and content attributes
        class ValidationData:
            def __init__(self, data: MarkdownDataDict):
                self.frontmatter = data.get("frontmatter", {})
                # Build ContentTree from content dict
                content_data = data.get("content")
                if content_data:
                    from mddata.models.document import ContentTree, Section

                    content_tree = ContentTree()
                    children = content_data.get("children")
                    if children:
                        for subsection_data in children:
                            section = Section.from_dict(subsection_data)
                            content_tree.add_section(section)
                    self.content = content_tree
                else:
                    self.content = None

        validation_data = ValidationData(document_data)
        result = validator.validate(validation_data)

        if not result["valid"]:
            error_messages = [
                (
                    f"{issue.get('path', 'unknown')}: "
                    f"{issue.get('message', 'validation error')}"
                )
                for issue in result["errors"]
            ]
            return False, error_messages

        return True, []
    except Exception as e:
        return False, [f"Schema validation error: {str(e)}"]


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
    data_path: str | None,
    format_type: str = "json",
    cli_params: list[str] | None = None,
    params_file: str | None = None,
) -> tuple[MarkdownDataDict | None, MarkdownDataUpdate | None]:
    """Load and validate data from file or stdin.

    Args:
        data_path: Path to data file, or None for stdin
        format_type: Data format ('json' or 'yaml')
        cli_params: Template parameters in KEY=VALUE format (optional)
        params_file: JSON/YAML file with parameter definitions (optional)

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
            # If that fails, try MarkdownDataUpdate (templates/partial updates)
            try:
                data_update = load_data_update(
                    data_path, format_type, cli_params, params_file
                )
                return None, data_update
            except DataLoadError:
                # Both failed
                return None, None
    except ParameterValidationError:
        # Preserve parameter validation errors with full details
        raise
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
    force_overwrite: bool = False,
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
        force_overwrite: Allow overwriting existing files (for CREATE mode)

    Returns:
        OperationResult with success status and metadata
    """
    try:
        if operation_mode == OperationMode.CREATE:
            return _create_new_document(
                data, schema, output_file, parameters, force_overwrite
            )
        elif operation_mode == OperationMode.MODIFY:
            return _modify_existing_document(
                data, target_file, policy, schema, parameters
            )
        elif operation_mode == OperationMode.SCHEMA_TEMPLATE:
            return _create_schema_template(schema, output_file, force_overwrite)
        elif operation_mode == OperationMode.STDOUT:
            return _render_to_stdout(data, schema, parameters)
        else:
            return OperationResult(
                success=False, errors=[f"Unknown operation mode: {operation_mode}"]
            )
    except ParameterValidationError as e:
        # Convert parameter validation errors to OperationResult
        return OperationResult(success=False, errors=[str(e)])
    except ValueError as e:
        # Convert value errors to OperationResult
        return OperationResult(success=False, errors=[str(e)])
    except Exception as e:
        return OperationResult(success=False, errors=[f"Operation failed: {str(e)}"])


def _create_new_document(
    data: MarkdownDataDict | MarkdownDataUpdate,
    schema: dict[str, Any] | None,
    output_file: Path,
    parameters: dict[str, Any] | None,
    force_overwrite: bool = False,
) -> OperationResult:
    """Create new document from data/template/schema."""
    try:
        # Check if file exists and handle overwrite protection
        if output_file.exists() and not force_overwrite:
            return OperationResult(
                success=False,
                errors=[
                    f"File already exists: {output_file}. Use --force to overwrite."
                ],
            )

        # Handle MarkdownDataUpdate (template) vs MarkdownDataDict (complete data)
        if isinstance(data, MarkdownDataUpdate):
            # Fill template with parameters if provided
            if parameters:
                filler = TemplateFiller(data)
                filled_data = filler.fill(params_dict=parameters)
                document_data = filled_data.as_markdown_dict()
            else:
                document_data = data.as_markdown_dict()
        else:
            # Already a complete MarkdownDataDict
            document_data = data

        # Validate against schema if provided
        if schema:
            is_valid, validation_errors = validate_against_schema(document_data, schema)
            if not is_valid:
                return OperationResult(success=False, errors=validation_errors)

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
    data: MarkdownDataDict | MarkdownDataUpdate,
    target_file: Path,
    policy: str,
    schema: dict[str, Any] | None = None,
    parameters: dict[str, Any] | None = None,
) -> OperationResult:
    """Modify existing document with merge support."""
    try:
        # Load existing document
        existing_doc = MarkdownFile(target_file)

        # Apply updates based on data type
        if isinstance(data, MarkdownDataUpdate):
            # Fill template with parameters if provided
            if data.is_template() and parameters:
                filler = TemplateFiller(data)
                data = filler.fill(params_dict=parameters)

            # Apply batch changes using MarkdownData's method
            batch_result = existing_doc.mddata.apply_batch_changes(data)
            if not batch_result["success"]:
                return OperationResult(
                    success=False,
                    errors=batch_result["errors"],
                    warnings=batch_result["warnings"],
                )
        else:
            # Replace entire document with new data (not typical for modify mode)
            existing_doc = MarkdownFile.from_dict(data, filepath=str(target_file))

        # Validate against schema if provided (before saving)
        if schema:
            document_data = existing_doc.mddata.data
            is_valid, validation_errors = validate_against_schema(document_data, schema)
            if not is_valid:
                return OperationResult(success=False, errors=validation_errors)

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
    schema: dict[str, Any], output_file: Path, force_overwrite: bool = False
) -> OperationResult:
    """Generate template from schema."""
    try:
        # Check if file exists and handle overwrite protection
        if output_file.exists() and not force_overwrite:
            return OperationResult(
                success=False,
                errors=[
                    f"File already exists: {output_file}. Use --force to overwrite."
                ],
            )

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
        logger.debug(f"_render_to_stdout called with data type: {type(data).__name__}")
        logger.debug(f"Parameters provided: {bool(parameters)}")
        if parameters:
            logger.debug(f"Parameter keys: {list(parameters.keys())}")

        # Validate input data
        if data is None:
            error_msg = (
                "Data is None - cannot render to stdout.\n"
                "Hint: Ensure data was loaded correctly from the input file."
            )
            logger.error(error_msg)
            return OperationResult(success=False, errors=[error_msg])

        # Handle MarkdownDataUpdate (template) vs MarkdownDataDict (complete data)
        if isinstance(data, MarkdownDataUpdate):
            logger.debug("Processing MarkdownDataUpdate (template)")

            # Fill template with parameters if provided
            if parameters:
                logger.debug("Filling template with parameters")
                try:
                    filler = TemplateFiller(data)
                    if filler is None:
                        raise ValueError("TemplateFiller initialization returned None")

                    filled_data = filler.fill(params_dict=parameters)
                    if filled_data is None:
                        template_params = (
                            list(data.parameters.keys()) if data.parameters else []
                        )
                        raise ValueError(
                            "Template filler returned None. "
                            "This usually indicates missing "
                            "required parameters.\n"
                            f"Provided parameters: {list(parameters.keys())}\n"
                            f"Template parameters: {template_params}"
                        )

                    logger.debug(f"Filled data type: {type(filled_data).__name__}")
                    document_data = filled_data.as_markdown_dict()

                    if document_data is None:
                        raise ValueError(
                            "as_markdown_dict() returned None. "
                            "This indicates an issue with the template structure."
                        )
                except Exception as e:
                    error_msg = (
                        f"Failed to fill template: {str(e)}\n"
                        f"Location: src/mddata/operations.py:_render_to_stdout\n"
                        f"Data type: {type(data).__name__}\n"
                        f"Has parameters: {bool(data.parameters)}\n"
                        f"Provided params: {list(parameters.keys())}"
                    )
                    logger.error(error_msg, exc_info=True)
                    return OperationResult(success=False, errors=[error_msg])
            else:
                logger.debug("Converting template to markdown dict without parameters")
                document_data = data.as_markdown_dict()
                if document_data is None:
                    raise ValueError("as_markdown_dict() returned None for template")
        else:
            # Already a complete MarkdownDataDict
            logger.debug("Using MarkdownDataDict directly")
            document_data = data

        # Validate document_data before creating file
        if document_data is None:
            error_msg = (
                "document_data is None after processing\n"
                "Location: src/mddata/operations.py:_render_to_stdout\n"
                "Hint: Check that template filling or data conversion succeeded"
            )
            logger.error(error_msg)
            return OperationResult(success=False, errors=[error_msg])

        # Validate against schema if provided
        if schema:
            is_valid, validation_errors = validate_against_schema(document_data, schema)
            if not is_valid:
                return OperationResult(success=False, errors=validation_errors)

        # Create markdown file and render to stdout
        logger.debug("Creating MarkdownFile from document_data")
        markdown_file = MarkdownFile.from_dict(document_data)

        if markdown_file is None:
            raise ValueError("MarkdownFile.from_dict() returned None")

        logger.debug("Rendering markdown content")
        rendered_content = markdown_file.to_markdown()

        if rendered_content is None:
            raise ValueError("to_markdown() returned None")

        # In a real CLI, this would print to stdout
        # For now, return it in metadata
        return OperationResult(
            success=True,
            document=document_data,
            metadata={"rendered_content": rendered_content, "mode": "stdout"},
        )
    except Exception as e:
        # Enhanced error message with context
        error_msg = (
            f"Failed to render to stdout: {str(e)}\n"
            f"Location: src/mddata/operations.py:_render_to_stdout\n"
            f"Data type: {type(data).__name__ if data else 'None'}\n"
        )
        logger.error(error_msg, exc_info=True)
        return OperationResult(success=False, errors=[error_msg])


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
