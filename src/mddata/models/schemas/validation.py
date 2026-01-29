"""Validation result models for schema validation."""

from enum import StrEnum
from typing import TypedDict


class ValidationIssueTypes(StrEnum):
    """Constants for validation issue types."""

    PROPERTY = "property"
    SECTION = "section"


class ValidationIssue(TypedDict):
    """Individual validation issue."""

    field_type: ValidationIssueTypes
    field: str  # Property/section path
    message: str
    expected: str | None
    actual: str | None


class ValidationResult(TypedDict):
    """Result of schema validation."""

    valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
