"""Convert schemas to MarkdownDocument templates."""

from ..models import (
    Block,
    BlockType,
    ContentTree,
    DocumentSchema,
    FrontmatterProperties,
    HeadingLevel,
    ParsedMarkdownData,
    Section,
    SectionSchema,
)


def _generate_frontmatter(schema: DocumentSchema) -> FrontmatterProperties:
    """
    Generate frontmatter properties from schema.

    Args:
        schema: DocumentSchema with properties field

    Returns:
        FrontmatterProperties dict with placeholder values
    """
    frontmatter: FrontmatterProperties = {}

    properties = schema.get("properties", {})
    for prop_name, prop_schema in properties.items():
        if prop_schema.get("required", False):
            # Use default value if specified, otherwise create placeholder
            if "default" in prop_schema:
                frontmatter[prop_name] = prop_schema["default"]
            else:
                # Create type-appropriate placeholder
                prop_type = prop_schema.get("type", "str")
                frontmatter[prop_name] = _create_placeholder_value(prop_type)
        # Skip optional properties without defaults

    return frontmatter


def _create_placeholder_value(
    prop_type: str,
) -> str | int | float | bool | list[str] | None:
    """
    Create a placeholder value based on property type.

    Args:
        prop_type: String representation of the property type

    Returns:
        Appropriate placeholder value for the type
    """
    if prop_type == "str":
        return "[Placeholder text]"
    elif prop_type == "int":
        return 0
    elif prop_type == "float":
        return 0.0
    elif prop_type == "bool":
        return False
    elif prop_type == "list":
        return []
    else:
        return "[Placeholder]"


def _generate_sections(schema: DocumentSchema) -> list[Section]:
    """
    Generate sections from schema.

    Args:
        schema: DocumentSchema with sections field

    Returns:
        List of Section objects with placeholder content
    """
    sections: list[Section] = []

    schema_sections = schema.get("sections", {})
    for section_id, section_schema in schema_sections.items():
        section = _generate_section(section_id, section_schema, HeadingLevel.H1)
        sections.append(section)

    return sections


def _generate_section(
    section_id: str,
    section_schema: SectionSchema,
    level: HeadingLevel,
    parent_path: str | None = None,
) -> Section:
    """
    Generate a single section with placeholder content.

    Args:
        section_id: ID for the section
        section_schema: Schema definition for the section
        level: Heading level for the section
        parent_path: Path of parent section if nested

    Returns:
        Section object with placeholder blocks and subsections
    """
    # Generate human-readable title from ID
    title = _generate_section_title(section_id)

    # Create section
    section = Section(title, level, parent_path)

    # Add placeholder blocks
    blocks = _create_placeholder_blocks(section_schema)
    for block in blocks:
        section.add_block(block)

    # Recursively add subsections
    children = section_schema.get("children", {})
    for child_id, child_schema in children.items():
        child_section = _generate_section(
            child_id, child_schema, level + 1, section.path
        )
        section.add_subsection(child_section)

    return section


def _generate_section_title(section_id: str) -> str:
    """
    Generate human-readable title from section ID.

    Args:
        section_id: Kebab-case or snake_case section ID

    Returns:
        Title-case title
    """
    # Replace underscores and hyphens with spaces, then title case
    return section_id.replace("_", " ").replace("-", " ").title()


def _create_placeholder_blocks(section_schema: SectionSchema) -> list[Block]:
    """
    Create placeholder blocks for a section based on validation rules.

    Args:
        section_schema: Schema definition for the section

    Returns:
        List of Block objects with placeholder content
    """
    validation = section_schema.get("validation", {})
    min_blocks = validation.get("min_blocks", 1)
    allowed_content = validation.get("allowed_content")

    blocks: list[Block] = []

    # Determine block types to create
    if allowed_content:
        # Use allowed content types
        block_types = (
            allowed_content[:min_blocks]
            if len(allowed_content) >= min_blocks
            else allowed_content
        )
        # Fill remaining with first allowed type
        while len(block_types) < min_blocks:
            block_types.append(allowed_content[0])
    else:
        # Default to paragraphs
        block_types = [BlockType.PARAGRAPH] * min_blocks

    # Create blocks with placeholder content
    for i, block_type in enumerate(block_types):
        content = _create_placeholder_content(block_type)
        block = Block(f"section_{i}", block_type, content)
        blocks.append(block)

    return blocks


def _create_placeholder_content(block_type: BlockType) -> str | list[str]:
    """
    Create placeholder content for a block type.

    Args:
        block_type: Type of block to create content for

    Returns:
        Placeholder content appropriate for the block type
    """
    if block_type == BlockType.PARAGRAPH:
        return "[Content placeholder]"
    elif block_type == BlockType.CODE_BLOCK:
        return "# Code placeholder"
    elif block_type in (BlockType.LIST, BlockType.ORDERED_LIST, BlockType.TASK_LIST):
        return ["- Item placeholder"]
    elif block_type == BlockType.BLOCKQUOTE:
        return "> Quote placeholder"
    elif block_type == BlockType.TABLE:
        return (
            "| Header | Placeholder |\n"
            "|--------|-------------|\n"
            "| Data   | Placeholder |"
        )
    else:
        return "[Placeholder content]"


def generate_template(schema: DocumentSchema) -> ParsedMarkdownData:
    """
    Generate a ParsedMarkdownData from a schema.

    Args:
        schema: DocumentSchema typed dictionary defining document structure

    Returns:
        ParsedMarkdownData with template content
    """
    # Generate frontmatter
    frontmatter = _generate_frontmatter(schema)

    # Generate content tree
    content_tree = ContentTree()
    sections = _generate_sections(schema)

    # Add sections to content tree
    for section in sections:
        content_tree.root.add_subsection(section)
        # Index sections for dynamic access
        content_tree._sections_index[section.id] = section

        # Recursively index subsections
        _index_sections_recursive(content_tree._sections_index, section)

    return ParsedMarkdownData(frontmatter=frontmatter, content=content_tree)


def _index_sections_recursive(
    sections_index: dict[str, Section], section: Section
) -> None:
    """
    Recursively index all sections in the tree.

    Args:
        sections_index: Dictionary to store section references
        section: Section to index along with its subsections
    """
    for subsection in section.children:
        sections_index[subsection.id] = subsection
        _index_sections_recursive(sections_index, subsection)
