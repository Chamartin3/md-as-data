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
    """Generate schema definitions from existing markdown data.

    Supports both single-document and multi-document schema generation.
    For multi-document schemas, implements intelligent merging with:
    - Frequency-based requirement determination (75% threshold)
    - Automatic type conflict resolution using union types
    - Enum inference for single-word string properties
    - Section hierarchy merging
    """

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

    def generate_merged_schema(
        self, documents: list[ParsedMarkdownData]
    ) -> DocumentSchema:
        """Generate merged schema from multiple markdown documents.

        Aggregates frontmatter properties across documents with:
        - Frequency-based requirement determination (≥75% = required)
        - Type conflict resolution using union types
        - Enum inference for single-word string properties
        - Section hierarchy merging

        Args:
            documents: List of parsed markdown documents

        Returns:
            Merged document schema definition
        """
        # Aggregate property statistics across all documents
        prop_stats = self._aggregate_property_stats(documents)

        # Generate merged frontmatter schema
        frontmatter_schema = self._generate_merged_frontmatter_schema(
            prop_stats, len(documents)
        )

        # Merge section hierarchies from all documents
        sections_schema = self._merge_section_hierarchies(documents)

        return {
            "frontmatter": frontmatter_schema,
            "sections": sections_schema,
            "validation_level": ValidationLevel.WARNINGS,
        }

    def _aggregate_property_stats(
        self, documents: list[ParsedMarkdownData]
    ) -> dict[str, dict]:
        """Aggregate statistics for frontmatter properties across documents.

        Args:
            documents: List of parsed markdown documents

        Returns:
            Dictionary mapping property names to aggregated statistics
        """
        prop_stats: dict[str, dict] = {}

        for doc in documents:
            for prop_name, prop_value in doc["frontmatter"].items():
                if prop_name not in prop_stats:
                    prop_stats[prop_name] = {
                        "count": 0,
                        "types": set(),
                        "values": [],
                    }

                prop_stats[prop_name]["count"] += 1
                prop_stats[prop_name]["types"].add(self._get_type_name(prop_value))
                prop_stats[prop_name]["values"].append(prop_value)

        return prop_stats

    def _generate_merged_frontmatter_schema(
        self, prop_stats: dict[str, dict], total_docs: int
    ) -> dict[str, PropertySchema]:
        """Generate merged frontmatter schema from aggregated statistics.

        Args:
            prop_stats: Aggregated property statistics
            total_docs: Total number of documents

        Returns:
            Dictionary of property schemas
        """
        frontmatter_schema = {}

        for prop_name, stats in prop_stats.items():
            # Calculate frequency and determine if required (≥75% threshold)
            frequency = stats["count"] / total_docs
            required = frequency >= 0.75

            # Resolve type conflicts using union types (alphabetically sorted)
            type_str = "|".join(sorted(stats["types"]))

            # Check if all values are single-word strings for enum inference
            all_single_word = all(
                self._is_single_word_string(v) or v is None for v in stats["values"]
            )

            schema: PropertySchema = {
                "type": type_str,
                "required": required,
            }

            # Infer enum for single-word string properties
            if all_single_word and len(stats["types"]) == 1:
                enum_values = self._infer_enum_values(stats["values"])
                if enum_values:
                    schema["enum"] = enum_values

            # Add validation constraints in strict mode
            if self.inference_mode == SchemaInferenceMode.STRICT:
                validations = self._infer_validation_constraints(stats["values"])
                if validations:
                    schema["validations"] = validations

            frontmatter_schema[prop_name] = schema

        return frontmatter_schema

    def _merge_section_hierarchies(
        self, documents: list[ParsedMarkdownData]
    ) -> dict[str, SectionSchema]:
        """Merge section hierarchies from all documents.

        Args:
            documents: List of parsed markdown documents

        Returns:
            Merged section schemas preserving all structures
        """
        merged_sections: dict[str, SectionSchema] = {}

        for doc in documents:
            for section in doc["content"].get_all_sections():
                section_id = section.id

                if section_id not in merged_sections:
                    # First occurrence - create initial schema
                    merged_sections[section_id] = self._infer_section_schema(section)
                else:
                    # Merge with existing schema
                    existing_schema = merged_sections[section_id]
                    new_schema = self._infer_section_schema(section)

                    # Merge subsections if present
                    if "subsections" in new_schema:
                        if "subsections" not in existing_schema:
                            existing_schema["subsections"] = {}
                        existing_schema["subsections"].update(new_schema["subsections"])

        return merged_sections

    def _is_single_word_string(self, value: FrontmatterValue) -> bool:
        """Check if value is a single-word string (no spaces).

        Args:
            value: Value to check

        Returns:
            True if value is a single-word string
        """
        return isinstance(value, str) and " " not in value.strip()

    def _infer_enum_values(
        self, values: list[FrontmatterValue], include_null: bool = True
    ) -> list[str | None]:
        """Infer enum values from collected values.

        Args:
            values: List of collected values
            include_null: Whether to include None values

        Returns:
            List of unique enum values
        """
        enum_set = set()

        for value in values:
            if value is None and include_null:
                enum_set.add(None)
            elif isinstance(value, str):
                enum_set.add(value)

        return sorted([v for v in enum_set if v is not None]) + (
            [None] if None in enum_set else []
        )

    def _infer_validation_constraints(
        self, values: list[FrontmatterValue]
    ) -> list[ValidationSchema]:
        """Infer validation constraints from collected values.

        Args:
            values: List of collected values

        Returns:
            List of validation schemas
        """
        validations: list[ValidationSchema] = []

        # Filter numeric values
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        if numeric_values:
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            validations.append(
                {
                    "type": ValidationType.MIN_VALUE,
                    "value": min_val,
                    "message": f"Value must be at least {min_val}",
                }
            )
            validations.append(
                {
                    "type": ValidationType.MAX_VALUE,
                    "value": max_val,
                    "message": f"Value must not exceed {max_val}",
                }
            )

        # Filter string values
        string_values = [v for v in values if isinstance(v, str)]
        if string_values:
            min_len = min(len(v) for v in string_values)
            max_len = max(len(v) for v in string_values)
            validations.append(
                {
                    "type": ValidationType.MIN_LENGTH,
                    "value": min_len,
                    "message": f"Value length must be at least {min_len}",
                }
            )
            validations.append(
                {
                    "type": ValidationType.MAX_LENGTH,
                    "value": max_len,
                    "message": f"Value length must not exceed {max_len}",
                }
            )

        return validations


def generate_schema(
    data: ParsedMarkdownData | list[ParsedMarkdownData],
    inference_mode: SchemaInferenceMode | None = None,
) -> DocumentSchema:
    """Generate schema from single or multiple markdown documents.

    When multiple documents are provided, schemas are intelligently merged:
    - Properties appearing in ≥75% of documents marked as required
    - Type conflicts resolved using union types (e.g., "str|int")
    - Single-word string properties inferred as enums (including null values)
    - Section hierarchies merged preserving all structures

    Args:
        data: Single parsed markdown document or list of documents
        inference_mode: How strictly to infer constraints

    Returns:
        Complete document schema definition
    """
    generator = SchemaGenerator(inference_mode)

    # Dispatch based on input type
    if isinstance(data, list):
        return generator.generate_merged_schema(data)
    else:
        return generator.generate_schema_from_data(data)
