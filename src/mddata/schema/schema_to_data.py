"""Convert DocumentSchema to MarkdownDataDict template.

This module provides functionality to convert schema definitions into
markdown document templates with placeholder values.
"""

from mddata.models import MarkdownDataDict, SectionData
from mddata.models.schemas import DocumentSchema, SchemaFieldNames, ValueType


def schema_to_markdown_dict(schema: DocumentSchema) -> MarkdownDataDict:
    """Convert a DocumentSchema to a MarkdownDataDict template.

    Creates a markdown document structure from a schema definition,
    populating properties with placeholder values based on their types
    and creating sections with placeholder content.

    Args:
        schema: DocumentSchema defining the structure

    Returns:
        MarkdownDataDict template with placeholder values

    Examples:
        >>> schema = {
        ...     "properties": {
        ...         "title": {"type": "str", "required": True},
        ...         "status": {"type": "str", "enum": ["draft", "published"]}
        ...     },
        ...     "sections": {
        ...         "introduction": {
        ...             "description": "Opening section"
        ...         }
        ...     }
        ... }
        >>> data = schema_to_markdown_dict(schema)
        >>> data["frontmatter"]["title"]
        '[Placeholder text]'
    """
    # Build frontmatter from property schemas
    frontmatter: dict = {}

    properties = schema.get(SchemaFieldNames.PROPERTIES, {})
    for prop_name, prop_schema in properties.items():
        # Use default value if specified, otherwise use type-based placeholder
        if "default" in prop_schema:
            frontmatter[prop_name] = prop_schema["default"]
        elif "enum" in prop_schema and prop_schema["enum"]:
            # Use first enum value as default
            frontmatter[prop_name] = prop_schema["enum"][0]
        else:
            # Get type and create placeholder
            value_type_str = prop_schema.get("type", "str")
            try:
                value_type = ValueType(value_type_str)
                frontmatter[prop_name] = value_type.get_default_placeholder()
            except ValueError:
                # Unknown type, use generic placeholder
                frontmatter[prop_name] = "[Placeholder]"

    # Build content tree from section schemas
    sections = schema.get(SchemaFieldNames.SECTIONS, {})
    content = _build_section_tree(sections, level=1)

    # Create root section if no sections defined
    if not content["children"]:
        content["blocks"] = [
            {
                "section_id": "root",
                "type": "paragraph",
                "content": "[Document content goes here]",
                "metadata": {},
            }
        ]

    return {
        "frontmatter": frontmatter,
        "content": content,
    }


def _build_section_tree(
    sections: dict, level: int = 1, parent_path: str = ""
) -> SectionData:
    """Recursively build section tree from schema sections.

    Args:
        sections: Dictionary of section schemas
        level: Current heading level
        parent_path: Path to parent section (for building section paths)

    Returns:
        SectionData with nested subsections
    """
    # Root section data
    root: SectionData = {
        "id": "root",
        "title": "",
        "level": 0,
        "path": "",
        "blocks": [],
        "children": [],
    }

    for section_id, section_schema in sections.items():
        # Build section path
        section_path = f"{parent_path}.{section_id}" if parent_path else section_id

        # Get description as placeholder content
        description = section_schema.get("description", "")
        placeholder_content = (
            description if description else f"[Content for {section_id} section]"
        )

        # Create section data
        section: SectionData = {
            "id": section_id,
            "title": _generate_title_from_id(section_id),
            "level": level,
            "path": section_path,
            "blocks": [
                {
                    "section_id": section_id,
                    "type": "paragraph",
                    "content": placeholder_content,
                    "metadata": {},
                }
            ],
            "children": [],
        }

        # Recursively process children (subsections)
        children = section_schema.get(SchemaFieldNames.CHILDREN, {})
        if children:
            child_tree = _build_section_tree(children, level + 1, section_path)
            section["children"] = child_tree["children"]

        root["children"].append(section)

    return root


def _generate_title_from_id(section_id: str) -> str:
    """Generate human-readable title from section ID.

    Args:
        section_id: Section identifier (e.g., "api_reference")

    Returns:
        Title-cased string (e.g., "Api Reference")
    """
    # Replace underscores and hyphens with spaces
    title = section_id.replace("_", " ").replace("-", " ")
    # Title case (capitalize first letter of each word)
    return title.title()


__all__ = ["schema_to_markdown_dict"]
