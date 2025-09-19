"""Schema validation engine for markdown documents."""

from typing import Any

from ..models.schema import (
    CURRENT_SCHEMA_VERSION,
    DocumentSchema,
    DocumentSchemaObj,
    ValidationLevel,
)
from ..models.validation import (
    ValidationIssue,
    ValidationResult,
)
from .schema_property_validator import PropertyValidator
from .schema_section_validator import SectionValidator


class SchemaValidator:
    """Validates markdown documents against defined schemas."""

    schema: DocumentSchemaObj

    def __init__(
        self, schema: DocumentSchema, validation_level: ValidationLevel | None = None
    ):
        """Initialize validator with document schema.

        Args:
            schema: Document schema definition
            validation_level: Override validation level (optional).
                If not provided, defaults to WARNINGS.
        """
        # Handle validation_level in schema (for backward compatibility)
        schema_validation_level = None
        if "validation_level" in schema:
            # Extract and convert the value before filtering
            schema_validation_level_str = schema["validation_level"]
            if isinstance(schema_validation_level_str, str):
                schema_validation_level = ValidationLevel(schema_validation_level_str)

        # Filter out validation_level from schema dict
        schema_dict = {k: v for k, v in schema.items() if k != "validation_level"}

        # Initialize schema object
        self.schema = DocumentSchemaObj(**schema_dict)
        self._validate_schema_version()

        # Set validation level (parameter > schema > default)
        self.validation_level = (
            validation_level or schema_validation_level or ValidationLevel.WARNINGS
        )

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

        errors.extend(
            self.property_validator.validate_properties(
                data.frontmatter if hasattr(data, "frontmatter") else {},
                self.schema.properties,
            )
        )

        errors.extend(
            self.section_validator.validate_sections(
                data.content if hasattr(data, "content") else None,
                self.schema.sections,
            )
        )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": []}

    def _validate_schema_version(self) -> None:
        """Validate schema version compatibility."""
        if not self.schema.version:
            import warnings

            warnings.warn(
                "Schema missing version field. Assuming legacy format (0.0.0). "
                "Please regenerate schema or add version field.",
                UserWarning,
                stacklevel=3,
            )
            return

        schema_version = self.schema.version

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
