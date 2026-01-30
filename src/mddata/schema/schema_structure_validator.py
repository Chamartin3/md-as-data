"""Schema structure validation utilities.

This module provides validation for DocumentSchema structure itself,
ensuring that schemas conform to expected format and field requirements.
This is different from using schemas to validate documents.
"""

from mddata.models.schema import (
    CURRENT_SCHEMA_VERSION,
    DocumentSchema,
    SchemaFieldNames,
)


class SchemaValidationError(Exception):
    """Exception raised when schema structure validation fails.

    This error indicates that the schema itself is malformed or invalid,
    not that a document failed validation against a schema.
    """

    pass


def validate_schema_structure(schema: DocumentSchema) -> None:
    """Validate that a schema dictionary conforms to DocumentSchema structure.

    Checks that the schema has the correct top-level structure and that
    all required fields are present with appropriate types.

    Args:
        schema: Schema dictionary to validate

    Raises:
        SchemaValidationError: If schema structure is invalid

    Examples:
        # Valid schema passes without error
        schema = {
            "version": "1.0.0",
            "properties": {"title": {"type": "str", "required": True}},
            "sections": {}
        }
        validate_schema_structure(schema)  # OK

        # Invalid schema raises error
        schema = {"invalid_field": "value"}
        validate_schema_structure(schema)  # Raises SchemaValidationError
    """
    if not isinstance(schema, dict):
        raise SchemaValidationError(
            f"Schema must be a dictionary, got {type(schema).__name__}"
        )

    # Validate version field
    if SchemaFieldNames.VERSION in schema:
        version = schema[SchemaFieldNames.VERSION]
        if not isinstance(version, (str, type(None))):
            raise SchemaValidationError(
                f"Schema version must be a string or None, got {type(version).__name__}"
            )

        # Check version compatibility
        if version:
            try:
                schema_major = int(version.split(".")[0])
                current_major = int(CURRENT_SCHEMA_VERSION.split(".")[0])

                if schema_major > current_major:
                    raise SchemaValidationError(
                        f"Schema version {version} is newer than supported "
                        f"version {CURRENT_SCHEMA_VERSION}. "
                        f"Please upgrade mddata library."
                    )
                elif schema_major < current_major:
                    raise SchemaValidationError(
                        f"Schema version {version} is older than current "
                        f"version {CURRENT_SCHEMA_VERSION}. "
                        f"Schema may need migration."
                    )
            except (ValueError, IndexError) as e:
                raise SchemaValidationError(
                    f"Invalid schema version format: {version}"
                ) from e

    # Validate properties field (optional but must be dict if present)
    if SchemaFieldNames.PROPERTIES in schema:
        properties = schema[SchemaFieldNames.PROPERTIES]
        if not isinstance(properties, dict):
            raise SchemaValidationError(
                f"Schema '{SchemaFieldNames.PROPERTIES}' field must be a dictionary, "
                f"got {type(properties).__name__}"
            )

        # Validate each property schema
        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                raise SchemaValidationError(
                    f"Property schema for '{prop_name}' must be a dictionary, "
                    f"got {type(prop_schema).__name__}"
                )

            # Validate required 'type' field
            if "type" not in prop_schema:
                raise SchemaValidationError(
                    f"Property schema for '{prop_name}' missing required 'type' field"
                )

    # Validate sections field (optional but must be dict if present)
    if SchemaFieldNames.SECTIONS in schema:
        sections = schema[SchemaFieldNames.SECTIONS]
        if not isinstance(sections, dict):
            raise SchemaValidationError(
                f"Schema '{SchemaFieldNames.SECTIONS}' field must be a dictionary, "
                f"got {type(sections).__name__}"
            )

        # Recursively validate section schemas
        _validate_section_schemas(sections)

    # At least one of properties or sections should be present
    has_properties = SchemaFieldNames.PROPERTIES in schema
    has_sections = SchemaFieldNames.SECTIONS in schema

    if not has_properties and not has_sections:
        raise SchemaValidationError(
            "Schema must contain at least one of "
            f"'{SchemaFieldNames.PROPERTIES}' or '{SchemaFieldNames.SECTIONS}'"
        )


def _validate_section_schemas(sections: dict, path: str = "") -> None:
    """Recursively validate section schema structure.

    Args:
        sections: Dictionary of section schemas to validate
        path: Current path in section hierarchy (for error messages)

    Raises:
        SchemaValidationError: If any section schema is invalid
    """
    for section_id, section_schema in sections.items():
        current_path = f"{path}.{section_id}" if path else section_id

        if not isinstance(section_schema, dict):
            raise SchemaValidationError(
                f"Section schema for '{current_path}' must be a dictionary, "
                f"got {type(section_schema).__name__}"
            )

        # Validate children (recursive subsections)
        if SchemaFieldNames.CHILDREN in section_schema:
            children = section_schema[SchemaFieldNames.CHILDREN]
            if not isinstance(children, dict):
                raise SchemaValidationError(
                    f"Section '{current_path}' children field must be a dictionary, "
                    f"got {type(children).__name__}"
                )
            # Recursively validate child sections
            _validate_section_schemas(children, current_path)

        # Validate validation field if present
        if SchemaFieldNames.VALIDATION in section_schema:
            validation = section_schema[SchemaFieldNames.VALIDATION]
            if not isinstance(validation, dict):
                raise SchemaValidationError(
                    f"Section '{current_path}' validation field must be a dictionary, "
                    f"got {type(validation).__name__}"
                )


__all__ = ["SchemaValidationError", "validate_schema_structure"]
