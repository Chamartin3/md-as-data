"""Property validator for frontmatter validation."""

import re
from typing import Any

from ..models import FrontmatterValue
from ..models.schemas import (
    PropertySchema,
    PropertyValidationType,
    ValidationLevel,
    ValueType,
)
from ..models.schemas.validation import (
    ValidationIssue,
    ValidationIssueTypes,
)


class PropertyValidator:
    """Validates document properties (frontmatter) against schema."""

    def __init__(self, validation_level: ValidationLevel):
        """Initialize property validator.

        Args:
            validation_level: Validation strictness level
        """
        self.validation_level = validation_level
        self._setup_validation_handlers()

    def _setup_validation_handlers(self) -> None:
        """Register validation rule handlers."""
        self.validation_handlers = {
            PropertyValidationType.MIN_LENGTH: self._validate_min_length,
            PropertyValidationType.MAX_LENGTH: self._validate_max_length,
            PropertyValidationType.MIN_VALUE: self._validate_min_value,
            PropertyValidationType.MAX_VALUE: self._validate_max_value,
            PropertyValidationType.REGEX: self._validate_regex,
            PropertyValidationType.ALLOWED_VALUES: self._validate_allowed_values,
        }

    def validate_properties(
        self,
        properties: dict[str, FrontmatterValue],
        schema: dict[str, PropertySchema],
    ) -> list[ValidationIssue]:
        """Validate all properties against schema.

        Args:
            properties: Document properties to validate
            schema: Property schema definitions

        Returns:
            List of validation issues found
        """
        issues: list[ValidationIssue] = []

        # Check required properties
        for field_name, field_schema in schema.items():
            if field_schema.get("required", False) and field_name not in properties:
                issues.append(
                    self._create_issue(
                        field_name,
                        f"Required property '{field_name}' is missing",
                        field_schema.get("type", "any"),
                        None,
                    )
                )

        # Validate each property
        for field_name, value in properties.items():
            if field_name in schema:
                field_issues = self._validate_property(
                    field_name, value, schema[field_name]
                )
                issues.extend(field_issues)
            elif self.validation_level == ValidationLevel.STRICT:
                issues.append(
                    self._create_issue(
                        field_name,
                        f"Unexpected property '{field_name}'",
                        None,
                        str(type(value).__name__),
                    )
                )

        return issues

    def _validate_property(
        self,
        field_name: str,
        value: Any,
        schema: PropertySchema,
    ) -> list[ValidationIssue]:
        """Validate individual property against schema."""
        issues: list[ValidationIssue] = []

        # Type validation
        if "type" in schema:
            value_type = ValueType(schema["type"])
            if not self._check_type(value, value_type):
                issues.append(
                    self._create_issue(
                        field_name,
                        f"Type mismatch for '{field_name}'",
                        value_type.value,
                        str(type(value).__name__),
                    )
                )
                return issues  # Skip further validation if type is wrong

        # Apply validation rules
        validations = schema.get("validations", [])
        for validation in validations:
            validation_type = PropertyValidationType(validation["type"])
            handler = self.validation_handlers.get(validation_type)

            if handler:
                issue = handler(
                    field_name,
                    value,
                    validation.get("value"),
                    validation.get("message", ""),
                )
                if issue:
                    issues.append(issue)

        return issues

    def _validate_min_length(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate minimum length constraint."""
        if isinstance(value, (str, list)) and len(value) < constraint:
            return self._create_issue(
                field_name,
                message or f"Length {len(value)} is below minimum {constraint}",
                f">= {constraint}",
                str(len(value)),
            )
        return None

    def _validate_max_length(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate maximum length constraint."""
        if isinstance(value, (str, list)) and len(value) > constraint:
            return self._create_issue(
                field_name,
                message or f"Length {len(value)} exceeds maximum {constraint}",
                f"<= {constraint}",
                str(len(value)),
            )
        return None

    def _validate_min_value(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate minimum value constraint."""
        if isinstance(value, (int, float)) and value < constraint:
            return self._create_issue(
                field_name,
                message or f"Value {value} is below minimum {constraint}",
                f">= {constraint}",
                str(value),
            )
        return None

    def _validate_max_value(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate maximum value constraint."""
        if isinstance(value, (int, float)) and value > constraint:
            return self._create_issue(
                field_name,
                message or f"Value {value} exceeds maximum {constraint}",
                f"<= {constraint}",
                str(value),
            )
        return None

    def _validate_regex(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate regex pattern constraint."""
        if isinstance(value, str) and not re.match(constraint, value):
            return self._create_issue(
                field_name,
                message or f"Value does not match pattern: {constraint}",
                constraint,
                value,
            )
        return None

    def _validate_allowed_values(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate allowed values constraint."""
        if value not in constraint:
            return self._create_issue(
                field_name,
                message or f"Value '{value}' not in allowed values",
                str(constraint),
                str(value),
            )
        return None

    def _create_issue(
        self, field_name: str, message: str, expected: str | None, actual: str | None
    ) -> ValidationIssue:
        """Create standardized validation issue."""
        return {
            "field_type": ValidationIssueTypes.PROPERTY,
            "field": f"frontmatter.{field_name}",
            "message": message,
            "expected": expected,
            "actual": actual,
        }

    def _check_type(self, value: Any, expected_type: ValueType) -> bool:
        """Check if value matches expected type."""

        type_checks = {
            ValueType.STRING: lambda v: isinstance(v, str),
            ValueType.INTEGER: lambda v: isinstance(v, int) and not isinstance(v, bool),
            ValueType.FLOAT: lambda v: isinstance(v, float),
            ValueType.BOOLEAN: lambda v: isinstance(v, bool),
            ValueType.LIST: lambda v: isinstance(v, list),
            ValueType.DATE: lambda v: self._is_date(v),
            ValueType.DATETIME: lambda v: self._is_datetime(v),
        }

        check_func = type_checks.get(expected_type)
        return check_func(value) if check_func else False

    def _is_date(self, value: Any) -> bool:
        """Check if value is a valid date string."""
        from datetime import datetime

        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_datetime(self, value: Any) -> bool:
        """Check if value is a valid datetime string."""
        from datetime import datetime

        if not isinstance(value, str):
            return False
        try:
            # Check that it contains time information (T or space)
            if "T" not in value and " " not in value:
                return False
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False
