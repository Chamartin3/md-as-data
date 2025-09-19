"""Section validation for markdown documents."""

from typing import Any

from ..models import BlockType, Section
from ..models.schema import (
    SchemaFieldNames,
    SectionSchema,
    ValidationLevel,
)
from ..models.validation import (
    ValidationIssue,
    ValidationIssueTypes,
)


class SectionValidator:
    """Validates document sections against schema."""

    def __init__(self, validation_level: ValidationLevel):
        """Initialize section validator.

        Args:
            validation_level: Validation strictness level
        """
        self.validation_level = validation_level

    def validate_sections(
        self, content: Any, schema: dict[str, SectionSchema]
    ) -> list[ValidationIssue]:
        """Validate all sections against schema.

        Args:
            content: Document content tree
            schema: Section schema definitions

        Returns:
            List of validation issues found
        """
        issues: list[ValidationIssue] = []

        if not content:
            # No content - check for required sections
            for section_id, section_schema in schema.items():
                validation_config = section_schema.get(SchemaFieldNames.VALIDATION, {})
                if validation_config.get("required", False):
                    issues.append(
                        {
                            "field_type": ValidationIssueTypes.SECTION,
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
            validation_config = section_schema.get(SchemaFieldNames.VALIDATION, {})
            if (
                validation_config.get("required", False)
                and section_id not in section_map
            ):
                issues.append(
                    {
                        "field_type": ValidationIssueTypes.SECTION,
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
        """Validate individual section.

        Args:
            section: Section to validate
            schema: Section schema definition
            path: Section path for error reporting

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []
        validation_config = schema.get(SchemaFieldNames.VALIDATION, {})

        # Validate block count
        if (
            "min_blocks" in validation_config
            and len(section.blocks) < validation_config["min_blocks"]
        ):
            min_blocks = validation_config["min_blocks"]
            block_count = len(section.blocks)
            issues.append(
                {
                    "field_type": ValidationIssueTypes.SECTION,
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
                    "field_type": ValidationIssueTypes.SECTION,
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
                            "field_type": ValidationIssueTypes.SECTION,
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
        if SchemaFieldNames.CHILDREN in schema:
            for subsection_id, subsection_schema in schema[
                SchemaFieldNames.CHILDREN
            ].items():
                subsection = next(
                    (s for s in section.children if s.id == subsection_id), None
                )
                if subsection:
                    subsection_issues = self._validate_section(
                        subsection, subsection_schema, f"{path}.{subsection_id}"
                    )
                    issues.extend(subsection_issues)
                else:
                    subsection_validation = subsection_schema.get(
                        SchemaFieldNames.VALIDATION, {}
                    )
                    if subsection_validation.get("required", False):
                        issues.append(
                            {
                                "field_type": ValidationIssueTypes.SECTION,
                                "field": f"{path}.{subsection_id}",
                                "message": (
                                    f"Required subsection '{subsection_id}' is missing"
                                ),
                                "expected": "subsection",
                                "actual": None,
                            }
                        )

        return issues
