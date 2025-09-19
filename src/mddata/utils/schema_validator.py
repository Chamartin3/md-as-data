"""Utility for validating schema structure before use."""

from typing import Any

from ..models import DocumentSchema


class SchemaValidationError(ValueError):
    """Raised when schema structure is invalid."""

    def __init__(
        self,
        message: str,
        path: str | None = None,
        details: str | None = None,
    ):
        """
        Initialize schema validation error.

        Args:
            message: Main error message
            path: Path in schema where error occurred (e.g., "properties.title")
            details: Additional details or suggestions
        """
        self.path = path
        self.details = details

        full_message = f"Invalid schema structure: {message}"
        if path:
            full_message += f"\n  Location: {path}"
        if details:
            full_message += f"\n  Details: {details}"

        super().__init__(full_message)


def validate_schema_structure(schema: DocumentSchema) -> None:
    """
    Validate that schema has correct structure before use.

    Args:
        schema: DocumentSchema to validate

    Raises:
        SchemaValidationError: If schema structure is invalid
    """
    if not isinstance(schema, dict):
        raise SchemaValidationError(
            "Schema must be a dictionary/object",
            details="Received type: " + type(schema).__name__,
        )

    # Validate properties section if present
    if "properties" in schema:
        _validate_properties(schema["properties"])

    # Validate sections section if present
    if "sections" in schema:
        _validate_sections(schema["sections"])


def _validate_properties(properties: Any, path: str = "properties") -> None:
    """
    Validate properties section structure.

    Args:
        properties: Properties dictionary to validate
        path: Current path in schema for error reporting

    Raises:
        SchemaValidationError: If properties structure is invalid
    """
    if properties is None:
        raise SchemaValidationError(
            "Properties section cannot be null/None",
            path=path,
            details="Either define property schemas or remove the 'properties' key",
        )

    if not isinstance(properties, dict):
        raise SchemaValidationError(
            "Properties must be a dictionary/object",
            path=path,
            details=f"Received type: {type(properties).__name__}",
        )

    # Validate each property definition
    for prop_name, prop_schema in properties.items():
        prop_path = f"{path}.{prop_name}"

        if prop_schema is None:
            raise SchemaValidationError(
                f"Property '{prop_name}' schema cannot be null/None",
                path=prop_path,
                details=(
                    "Each property must have a schema definition "
                    "with at least a 'type' field"
                ),
            )

        if not isinstance(prop_schema, dict):
            raise SchemaValidationError(
                f"Property '{prop_name}' schema must be a dictionary/object",
                path=prop_path,
                details=f"Received type: {type(prop_schema).__name__}",
            )

        # Validate required fields
        if "type" not in prop_schema:
            raise SchemaValidationError(
                f"Property '{prop_name}' is missing required 'type' field",
                path=prop_path,
                details="Valid types: str, int, float, bool, list",
            )


def _validate_sections(sections: Any, path: str = "sections") -> None:
    """
    Validate sections structure.

    Args:
        sections: Sections dictionary to validate
        path: Current path in schema for error reporting

    Raises:
        SchemaValidationError: If sections structure is invalid
    """
    if sections is None:
        raise SchemaValidationError(
            "Sections cannot be null/None",
            path=path,
            details="Either define section schemas or remove the 'sections' key",
        )

    if not isinstance(sections, dict):
        raise SchemaValidationError(
            "Sections must be a dictionary/object",
            path=path,
            details=f"Received type: {type(sections).__name__}",
        )

    # Validate each section
    for section_id, section_schema in sections.items():
        section_path = f"{path}.{section_id}"

        if section_schema is None:
            raise SchemaValidationError(
                f"Section '{section_id}' schema cannot be null/None",
                path=section_path,
                details=(
                    "Each section must have a schema definition "
                    "(at minimum an empty 'children' object)"
                ),
            )

        if not isinstance(section_schema, dict):
            raise SchemaValidationError(
                f"Section '{section_id}' schema must be a dictionary/object",
                path=section_path,
                details=f"Received type: {type(section_schema).__name__}",
            )

        # Validate children if present
        if "children" in section_schema:
            children = section_schema["children"]
            children_path = f"{section_path}.children"

            if children is None:
                raise SchemaValidationError(
                    f"Section '{section_id}' children cannot be null/None",
                    path=children_path,
                    details="Use an empty object {} for sections with no children",
                )

            if not isinstance(children, dict):
                raise SchemaValidationError(
                    f"Section '{section_id}' children must be a dictionary/object",
                    path=children_path,
                    details=f"Received type: {type(children).__name__}",
                )

            # Recursively validate child sections
            if children:  # Only validate if not empty
                _validate_sections(children, children_path)
