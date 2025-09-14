"""Schema generation from existing markdown documents."""

from typing import Literal

from ..models import (
    BlockType,
    ContentTree,
    FrontmatterProperties,
    FrontmatterValue,
    ParsedMarkdownData,
    Section,
)
from .schema_models import (
    DocumentSchema,
    PropertySchema,
    SchemaInferenceMode,
    SectionSchema,
    SectionValidationSchema,
    ValidationLevel,
    ValidationSchema,
    ValidationType,
    ValueType,
)

InferenceMode = Literal["strict", "permissive"]


class SchemaGenerator:
    """Generate schema definitions from existing markdown data."""

    def __init__(
        self,
        inference_mode: SchemaInferenceMode | None = None,
    ):
        """Initialize schema generator.

        Args:
            inference_mode: How strictly to infer constraints from data
        """
        self.inference_mode = inference_mode or SchemaInferenceMode.PERMISSIVE

    def generate_schema_from_data(self, data: ParsedMarkdownData) -> DocumentSchema:
        """Generate complete document schema from parsed data.

        Args:
            data: Parsed markdown document data

        Returns:
            Complete document schema definition
        """
        return {
            "frontmatter": self._analyze_frontmatter(data["frontmatter"]),
            "sections": self._analyze_sections(data["content"]),
            "validation_level": ValidationLevel.WARNINGS,
        }

    def _analyze_frontmatter(
        self, frontmatter: FrontmatterProperties
    ) -> dict[str, PropertySchema]:
        """Analyze frontmatter to generate property schemas.

        Args:
            frontmatter: Document frontmatter properties

        Returns:
            Dictionary of property schemas
        """
        schemas = {}
        for key, value in frontmatter.items():
            schemas[key] = self._infer_property_schema(key, value)
        return schemas

    def _infer_property_schema(
        self, key: str, value: FrontmatterValue
    ) -> PropertySchema:
        """Infer schema for a single frontmatter property.

        Args:
            key: Property name
            value: Property value

        Returns:
            Property schema definition
        """
        property_type = self._get_type_name(value)
        schema: PropertySchema = {
            "type": property_type,
            "required": True,  # Existing properties are required by default
        }

        # Only add validation rules in strict mode
        if self.inference_mode == SchemaInferenceMode.STRICT:
            schema["default"] = value

            # Create validations list using new ValidationSchema structure
            validations: list[ValidationSchema] = []

            if isinstance(value, (int, float)):
                # Add reasonable bounds for numeric values
                if isinstance(value, int) and not isinstance(value, bool):
                    validations.append(
                        {
                            "type": ValidationType.MIN_VALUE,
                            "value": 0,
                            "message": "Value must be non-negative",
                        }
                    )
                    validations.append(
                        {
                            "type": ValidationType.MAX_VALUE,
                            "value": value * 2,
                            "message": f"Value must not exceed {value * 2}",
                        }
                    )
            elif isinstance(value, str) and len(value) > 0:
                # Add length constraints for strings
                validations.append(
                    {
                        "type": ValidationType.MIN_LENGTH,
                        "value": 1,
                        "message": "Value must not be empty",
                    }
                )
                max_len = max(100, len(value) * 2)
                validations.append(
                    {
                        "type": ValidationType.MAX_LENGTH,
                        "value": max_len,
                        "message": f"Value length must not exceed {max_len}",
                    }
                )

            if validations:
                schema["validations"] = validations

        return schema

    def _analyze_sections(self, content_tree: ContentTree) -> dict[str, SectionSchema]:
        """Analyze content structure to generate section schemas.

        Args:
            content_tree: Document content tree

        Returns:
            Dictionary of section schemas
        """
        schemas = {}
        for section in content_tree.get_all_sections():
            schema = self._infer_section_schema(section)
            schemas[section.id] = schema
        return schemas

    def _infer_section_schema(self, section: Section) -> SectionSchema:
        """Infer schema for a single section.

        Args:
            section: Section to analyze

        Returns:
            Section schema definition
        """
        schema: SectionSchema = {}

        # In strict mode, add validation constraints
        if self.inference_mode == SchemaInferenceMode.STRICT:
            block_types = [block.type for block in section.blocks]
            unique_block_types = list(set(block_types))

            validation_config: SectionValidationSchema = {
                "required": False,
                "max_blocks": len(section.blocks),
                "min_blocks": len(section.blocks),
                "allowed_content": unique_block_types
                if unique_block_types
                else [BlockType.PARAGRAPH],
            }
            schema["validation"] = validation_config
        # In permissive mode, omit validation entirely if only required=False
        # (no constraints means no validation config needed)

        # Analyze subsections recursively
        if section.subsections:
            schema["subsections"] = {}
            for subsection in section.subsections:
                schema["subsections"][subsection.id] = self._infer_section_schema(
                    subsection
                )

        return schema

    def _get_type_name(self, value: FrontmatterValue) -> str:
        """Convert Python type to ValueType enum value.

        Args:
            value: Value to get type for

        Returns:
            ValueType enum value as string
        """
        # Check bool before int since bool is a subclass of int in Python
        if isinstance(value, bool):
            return ValueType.BOOLEAN.value
        elif isinstance(value, int):
            return ValueType.INTEGER.value
        elif isinstance(value, float):
            return ValueType.FLOAT.value
        elif isinstance(value, str):
            return ValueType.STRING.value
        elif isinstance(value, list):
            return ValueType.LIST.value
        else:
            return ValueType.STRING.value  # Fallback to string


def generate_schema(
    data: ParsedMarkdownData, inference_mode: SchemaInferenceMode | None = None
) -> DocumentSchema:
    """Generate schema from markdown data.

    Args:
        data: Parsed markdown document data
        inference_mode: How strictly to infer constraints

    Returns:
        Complete document schema definition
    """
    generator = SchemaGenerator(inference_mode)
    return generator.generate_schema_from_data(data)
