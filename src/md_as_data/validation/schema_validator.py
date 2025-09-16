"""Schema validation engine for markdown documents."""

from typing import Any

from .schema_models import (
    CURRENT_SCHEMA_VERSION,
    DocumentSchema,
    SchemaFieldNames,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
)
from .schema_property_validator import PropertyValidator
from .schema_section_validator import SectionValidator


class SchemaValidator:
    """Validates markdown documents against defined schemas."""

    def __init__(
        self, schema: DocumentSchema, validation_level: ValidationLevel | None = None
    ):
        """Initialize validator with document schema.

        Args:
            schema: Document schema definition
            validation_level: Override validation level (optional).
                If not provided, uses level from schema (deprecated)
                or defaults to WARNINGS.
        """
        self.schema = schema
        self._validate_schema_version()

        # Resolve validation level
        self.validation_level = self._resolve_validation_level(validation_level)

        # Delegate to sub-validators
        self.property_validator = PropertyValidator(self.validation_level)
        self.section_validator = SectionValidator(self.validation_level)

    def validate(self, data: Any) -> ValidationResult:
        """Validate document data against schema.

        Args:
            data: Document data to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors: list[ValidationIssue] = []

        if self.validation_level == ValidationLevel.DISABLED:
            return {"valid": True, "errors": [], "warnings": []}

        # Delegate to sub-validators
        if SchemaFieldNames.PROPERTIES in self.schema:
            errors.extend(
                self.property_validator.validate_properties(
                    data.frontmatter if hasattr(data, "frontmatter") else {},
                    self.schema[SchemaFieldNames.PROPERTIES],
                )
            )

        if SchemaFieldNames.SECTIONS in self.schema:
            errors.extend(
                self.section_validator.validate_sections(
                    data.content if hasattr(data, "content") else None,
                    self.schema[SchemaFieldNames.SECTIONS],
                )
            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": []}

    def _resolve_validation_level(
        self, validation_level: ValidationLevel | None
    ) -> ValidationLevel:
        """Resolve validation level from parameter, schema, or default."""
        if validation_level is not None:
            return validation_level

        if "validation_level" in self.schema:
            import warnings

            warnings.warn(
                "Embedding validation_level in schema is deprecated. "
                "Pass validation_level to SchemaValidator constructor instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            return ValidationLevel(self.schema["validation_level"])

        return ValidationLevel.WARNINGS

    def _validate_schema_version(self) -> None:
        """Validate schema version compatibility."""
        if SchemaFieldNames.VERSION not in self.schema:
            import warnings

            warnings.warn(
                "Schema missing version field. Assuming legacy format (0.0.0). "
                "Please regenerate schema or add version field.",
                UserWarning,
                stacklevel=3,
            )
            return

        schema_version = self.schema[SchemaFieldNames.VERSION]

        # Parse versions for comparison
        current_major = int(CURRENT_SCHEMA_VERSION.split(".")[0])
        schema_major = int(schema_version.split(".")[0])

        if schema_major > current_major:
            raise ValueError(
                f"Schema version {schema_version} is newer than supported "
                f"version {CURRENT_SCHEMA_VERSION}. "
                f"Please update the md_as_data library."
            )

        if schema_major < current_major:
            import warnings

            warnings.warn(
                f"Schema version {schema_version} is older than current "
                f"version {CURRENT_SCHEMA_VERSION}. "
                f"Consider regenerating the schema for latest features.",
                UserWarning,
                stacklevel=3,
            )
