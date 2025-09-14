"""Schema validation engine for markdown documents."""

import re
from datetime import datetime
from typing import Any

from ..models import FrontmatterValue, Section
from .schema_models import (
    DocumentSchema,
    PropertySchema,
    SectionSchema,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    ValidationSchema,
    ValidationType,
    ValueType,
)


class SchemaValidator:
    """Validates markdown documents against defined schemas."""

    def __init__(self, schema: DocumentSchema):
        """Initialize validator with document schema.

        Args:
            schema: Document schema definition
        """
        self.schema = schema
        self.validation_level = ValidationLevel(
            schema.get("validation_level", ValidationLevel.WARNINGS)
        )

    def validate(self, data: Any) -> ValidationResult:
        """Validate document data against schema.

        Args:
            data: MarkdownData instance to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []

        # Skip validation if disabled
        if self.validation_level == ValidationLevel.DISABLED:
            return {"valid": True, "errors": [], "warnings": []}

        # Validate frontmatter
        if "frontmatter" in self.schema:
            fm_issues = self._validate_frontmatter(
                data.frontmatter if hasattr(data, "frontmatter") else {},
                self.schema["frontmatter"],
            )
            errors.extend(fm_issues)

        # Validate sections
        if "sections" in self.schema:
            section_issues = self._validate_sections(
                data.content if hasattr(data, "content") else None,
                self.schema["sections"],
            )
            errors.extend(section_issues)

        # Determine overall validity
        valid = len(errors) == 0

        return {"valid": valid, "errors": errors, "warnings": warnings}

    def _validate_frontmatter(
        self,
        frontmatter: dict[str, FrontmatterValue],
        schema: dict[str, PropertySchema],
    ) -> list[ValidationIssue]:
        """Validate frontmatter properties against schema."""
        issues: list[ValidationIssue] = []

        # Check required properties
        for prop_name, prop_schema in schema.items():
            if prop_schema.get("required", False) and prop_name not in frontmatter:
                issues.append(
                    {
                        "field_type": "frontmatter",
                        "field": f"frontmatter.{prop_name}",
                        "message": f"Required property '{prop_name}' is missing",
                        "expected": prop_schema.get("type", "any"),
                        "actual": None,
                    }
                )

        # Validate existing properties
        for prop_name, value in frontmatter.items():
            if prop_name in schema:
                prop_issues = self._validate_property(
                    prop_name, value, schema[prop_name]
                )
                issues.extend(prop_issues)
            elif self.validation_level == ValidationLevel.STRICT:
                issues.append(
                    {
                        "field_type": "frontmatter",
                        "field": f"frontmatter.{prop_name}",
                        "message": f"Unexpected property '{prop_name}'",
                        "expected": None,
                        "actual": str(type(value).__name__),
                    }
                )

        return issues

    def _validate_property(
        self, name: str, value: Any, schema: PropertySchema
    ) -> list[ValidationIssue]:
        """Validate individual property value."""
        issues: list[ValidationIssue] = []

        # Type validation
        if "type" in schema:
            value_type = ValueType(schema["type"])
            if not self._check_type(value, value_type):
                issues.append(
                    {
                        "field_type": "frontmatter",
                        "field": f"frontmatter.{name}",
                        "message": f"Type mismatch for '{name}'",
                        "expected": value_type.value,
                        "actual": str(type(value).__name__),
                    }
                )
                return issues  # Skip further validation if type is wrong

        # Custom validation rules (new structure with ValidationSchema list)
        if "validations" in schema:
            for validation in schema["validations"]:
                validation_issue = self._apply_validation_rule(name, value, validation)
                if validation_issue:
                    issues.append(validation_issue)

        return issues

    def _apply_validation_rule(
        self, field_name: str, value: Any, validation: ValidationSchema
    ) -> ValidationIssue | None:
        """Apply a single validation rule to a value."""
        validation_type = ValidationType(validation["type"])
        validation_value = validation["value"]
        custom_message = validation.get("message", "")

        # String/List length validations
        if validation_type == ValidationType.MIN_LENGTH:
            if isinstance(value, (str, list)) and len(value) < validation_value:
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Length {len(value)} is below minimum {validation_value}",
                    "expected": f">= {validation_value}",
                    "actual": str(len(value)),
                }

        elif validation_type == ValidationType.MAX_LENGTH:
            if isinstance(value, (str, list)) and len(value) > validation_value:
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Length {len(value)} exceeds maximum {validation_value}",
                    "expected": f"<= {validation_value}",
                    "actual": str(len(value)),
                }

        # Numeric value validations
        elif validation_type == ValidationType.MIN_VALUE:
            if isinstance(value, (int, float)) and value < validation_value:
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Value {value} is below minimum {validation_value}",
                    "expected": f">= {validation_value}",
                    "actual": str(value),
                }

        elif validation_type == ValidationType.MAX_VALUE:
            if isinstance(value, (int, float)) and value > validation_value:
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Value {value} exceeds maximum {validation_value}",
                    "expected": f"<= {validation_value}",
                    "actual": str(value),
                }

        # Regex pattern validation
        elif validation_type == ValidationType.REGEX:
            if isinstance(value, str) and not re.match(validation_value, value):
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Value does not match pattern: {validation_value}",
                    "expected": validation_value,
                    "actual": value,
                }

        # Allowed values validation
        elif validation_type == ValidationType.ALLOWED_VALUES:
            if value not in validation_value:
                return {
                    "field_type": "frontmatter",
                    "field": f"frontmatter.{field_name}",
                    "message": custom_message
                    or f"Value '{value}' not in allowed values",
                    "expected": str(validation_value),
                    "actual": str(value),
                }

        return None

    def _validate_sections(
        self, content: Any, schema: dict[str, SectionSchema]
    ) -> list[ValidationIssue]:
        """Validate document sections against schema."""
        issues: list[ValidationIssue] = []

        if not content:
            for section_id, section_schema in schema.items():
                validation_config = section_schema.get("validation", {})
                if validation_config.get("required", False):
                    issues.append(
                        {
                            "field_type": "section",
                            "field": f"sections.{section_id}",
                            "message": f"Required section '{section_id}' is missing",
                            "expected": "section",
                            "actual": None,
                        }
                    )
            return issues

        # Get all sections from content tree
        all_sections = (
            content.get_all_sections() if hasattr(content, "get_all_sections") else []
        )
        section_map = {s.id: s for s in all_sections}

        # Check required sections
        for section_id, section_schema in schema.items():
            validation_config = section_schema.get("validation", {})
            if (
                validation_config.get("required", False)
                and section_id not in section_map
            ):
                issues.append(
                    {
                        "field_type": "section",
                        "field": f"sections.{section_id}",
                        "message": f"Required section '{section_id}' is missing",
                        "expected": "section",
                        "actual": None,
                    }
                )

        # Validate existing sections
        for section_id, section in section_map.items():
            if section_id in schema:
                section_issues = self._validate_section(
                    section, schema[section_id], f"sections.{section_id}"
                )
                issues.extend(section_issues)

        return issues

    def _validate_section(
        self, section: Section, schema: SectionSchema, path: str
    ) -> list[ValidationIssue]:
        """Validate individual section."""
        issues: list[ValidationIssue] = []
        validation_config = schema.get("validation", {})

        # Validate block count
        if (
            "min_blocks" in validation_config
            and len(section.blocks) < validation_config["min_blocks"]
        ):
            min_blocks = validation_config["min_blocks"]
            block_count = len(section.blocks)
            issues.append(
                {
                    "field_type": "section",
                    "field": path,
                    "message": (
                        f"Section has {block_count} blocks, minimum is {min_blocks}"
                    ),
                    "expected": f">= {min_blocks}",
                    "actual": str(block_count),
                }
            )

        if (
            "max_blocks" in validation_config
            and len(section.blocks) > validation_config["max_blocks"]
        ):
            max_blocks = validation_config["max_blocks"]
            block_count = len(section.blocks)
            issues.append(
                {
                    "field_type": "section",
                    "field": path,
                    "message": (
                        f"Section has {block_count} blocks, maximum is {max_blocks}"
                    ),
                    "expected": f"<= {max_blocks}",
                    "actual": str(block_count),
                }
            )

        # Validate block types (uses allowed_content)
        if "allowed_content" in validation_config:
            # Convert allowed types to BlockType enums (handles both enum and string)
            from ..models import BlockType

            allowed_types_raw = validation_config["allowed_content"]
            allowed_types = set()
            for t in allowed_types_raw:
                if isinstance(t, BlockType):
                    allowed_types.add(t)
                elif isinstance(t, str):
                    # Handle string representation (from JSON)
                    try:
                        # Try direct value match first
                        allowed_types.add(BlockType(t))
                    except ValueError:
                        # Try enum name format (BlockType.PARAGRAPH)
                        if "." in t:
                            enum_name = t.split(".")[-1]
                            try:
                                allowed_types.add(BlockType[enum_name])
                            except KeyError:
                                pass

            for block in section.blocks:
                if block.type not in allowed_types:
                    issues.append(
                        {
                            "field_type": "section",
                            "field": f"{path}.blocks",
                            "message": (
                                f"Block type '{block.type.value}' "
                                f"not allowed in section"
                            ),
                            "expected": str(
                                [
                                    t.value if isinstance(t, BlockType) else t
                                    for t in allowed_types
                                ]
                            ),
                            "actual": block.type.value,
                        }
                    )

        # Validate subsections recursively
        if "subsections" in schema:
            for subsection_id, subsection_schema in schema["subsections"].items():
                subsection = next(
                    (s for s in section.subsections if s.id == subsection_id), None
                )
                if subsection:
                    subsection_issues = self._validate_section(
                        subsection, subsection_schema, f"{path}.{subsection_id}"
                    )
                    issues.extend(subsection_issues)
                else:
                    subsection_validation = subsection_schema.get("validation", {})
                    if subsection_validation.get("required", False):
                        issues.append(
                            {
                                "field_type": "section",
                                "field": f"{path}.{subsection_id}",
                                "message": (
                                    f"Required subsection '{subsection_id}' is missing"
                                ),
                                "expected": "subsection",
                                "actual": None,
                            }
                        )

        return issues

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
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_datetime(self, value: Any) -> bool:
        """Check if value is a valid datetime string."""
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
