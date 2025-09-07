"""Data structures for representing and managing markdown content."""

from enum import Enum, IntEnum
from typing import Any, TypedDict


class BlockType(Enum):
    """Types of content blocks in markdown."""

    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"


class HeadingLevel(IntEnum):
    """Heading levels in markdown."""

    ROOT = 0  # Represents the root level (no heading)
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6


class BlockMetadata(TypedDict, total=False):
    """Metadata attributes for blocks."""

    language: str  # For code blocks
    href: str  # For links
    src: str  # For images
    alt: str  # For images
    title: str  # For links/images


class BlockData(TypedDict):
    """Structured data for individual blocks."""

    section_id: str  # ID of the section this block belongs to
    type: str  # BlockType value
    content: str | list[str]
    metadata: BlockMetadata


class Block:
    """Base block in markdown content."""

    def __init__(
        self, section_id: str, block_type: BlockType, content: str | list[str]
    ):
        self.section = section_id
        self.type = block_type
        self.content = content
        self.metadata: BlockMetadata = {}

    def to_dict(self) -> BlockData:
        """Convert block to dictionary structure."""
        return {
            "section_id": self.section,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Return a block as markdown text representation."""
        if self.type == BlockType.PARAGRAPH:
            return str(self.content)

        if self.type == BlockType.CODE_BLOCK:
            language = self.metadata.get("language", "")
            return f"```{language}\n{self.content}\n```"

        if self.type == BlockType.LIST:
            if isinstance(self.content, list):
                return "\n".join(f"- {item}" for item in self.content)
            else:
                return f"- {self.content}"

        if self.type == BlockType.ORDERED_LIST:
            if isinstance(self.content, list):
                return "\n".join(
                    f"{i + 1}. {item}" for i, item in enumerate(self.content)
                )
            else:
                return f"1. {self.content}"

        if self.type == BlockType.BLOCKQUOTE:
            # Split into lines and add > prefix
            content = str(self.content)
            lines = content.split("\n")
            return "\n".join(f"> {line}" for line in lines)

        if self.type == BlockType.LINK:
            href = self.metadata.get("href", "#")
            title = self.metadata.get("title", "")
            title_attr = f' "{title}"' if title else ""
            return f"[{self.content}]({href}{title_attr})"

        if self.type == BlockType.IMAGE:
            src = self.metadata.get("src", "")
            alt = self.metadata.get("alt", str(self.content))
            title = self.metadata.get("title", "")
            title_attr = f' "{title}"' if title else ""
            return f"![{alt}]({src}{title_attr})"

        if self.type == BlockType.TABLE:
            # Basic table serialization (would need more complex logic for real tables)
            return str(self.content)

        # Fallback for unknown block types
        return str(self.content)


class BlocksData(TypedDict):
    """Structured data for blocks collection."""

    blocks: list[BlockData]


class SectionData(TypedDict):
    """Structured data for individual sections."""

    id: str
    title: str
    level: int  # HeadingLevel value
    path: str
    blocks: list[BlockData] | None
    subsections: list["SectionData"] | None


class SectionsData(TypedDict):
    """Structured data for sections collection."""

    sections: list[SectionData]
    sections_by_id: dict[str, SectionData]


class Section:
    """Section with heading, content, and nested structure."""

    SECTION_ID_PREFIX = ""
    SECTION_PATH_SEPARATOR = "."
    SECTION_ID_SEPARATOR = "_"  # Replace spaces s in title

    def __init__(self, title: str, level: HeadingLevel, parent_path: str | None = None):
        self.id = self._generate_id(title)
        self.title = title
        self.level = level
        self.blocks: list[Block] = []
        self.subsections: list[Section] = []
        self.parent_path = parent_path  # Optional reference to parent section path

    def _generate_id(self, title: str) -> str:
        """Generate kebab-case ID from title."""
        return self.SECTION_ID_PREFIX + title.lower().replace(
            self.SECTION_PATH_SEPARATOR, ""
        ).replace(",", "").replace(" ", self.SECTION_ID_SEPARATOR).replace(
            "_", self.SECTION_ID_SEPARATOR
        )

    @property
    def path(self) -> str:
        """Generate a path-like representation of the section."""
        if self.parent_path:
            return f"{self.parent_path}{self.SECTION_PATH_SEPARATOR}{self.id}"
        return self.id

    @classmethod
    def is_path(cls, identifier: str) -> bool:
        """Check if identifier is a path (contains separator)."""
        return cls.SECTION_PATH_SEPARATOR in identifier

    # Mutation methods
    def add_block(self, block: Block) -> None:
        """Add a block to this section."""
        block.section = self.id  # Ensure block references this section
        self.blocks.append(block)

    def add_subsection(self, section: "Section") -> None:
        """Add a subsection to this section."""
        if section.level <= self.level:
            raise ValueError(
                "Subsection level must be greater than parent section level. "
                f"Got {section.level} for subsection and {self.level} for parent."
            )
        self.subsections.append(section)

    def create_subsection(self, title: str, content: str | None) -> "Section":
        """Create and add a subsection."""
        new_level = (
            HeadingLevel(self.level + 1)
            if self.level < HeadingLevel.H6
            else HeadingLevel.H6
        )
        subsection = Section(title, new_level)
        if content is not None:
            text_block = Block(subsection.id, BlockType.PARAGRAPH, content)
            subsection.add_block(text_block)
        self.add_subsection(subsection)
        return subsection

    # Serialization
    def to_dict(self) -> SectionData:
        """Convert section to dictionary structure."""
        return {
            "id": self.id,
            "title": self.title,
            "level": int(self.level),
            "blocks": [b.to_dict() for b in self.blocks],
            "subsections": [s.to_dict() for s in self.subsections],
            "path": self.path,
        }

    def to_text(self) -> str:
        lines = []
        # Add heading if not root and not skipping title
        if self.level != HeadingLevel.ROOT:
            heading_marker = "#" * int(self.level)
            lines.append(f"{heading_marker} {self.title}")
            lines.append("")  # Empty line after heading

        # Add blocks
        for block in self.blocks:
            block_str = block.to_text()
            if block_str:
                lines.append(block_str)
                lines.append("")  # Empty line after block

        # Add subsections
        for subsection in self.subsections:
            subsection_str = subsection.to_text()
            if subsection_str:
                lines.append(subsection_str)

        # Clean up trailing empty lines
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def __repr__(self) -> str:
        level_name = self.level.name if hasattr(self.level, "name") else str(self.level)
        return (
            f"<Section {self.id} title={self.title} level={level_name} "
            f"blocks={len(self.blocks)} subsections={len(self.subsections)}>"
        )


SectionsMap = dict[str, Section]


class ContentTree:
    """Hierarchical content structure with dynamic property access."""

    def __init__(self):
        self.root = Section("", HeadingLevel.ROOT)
        self._sections_index: SectionsMap = {}

    @property
    def paths(self) -> list[str]:
        """Get all section paths in the tree."""
        return [section.path for section in self._sections_index.values()]

    @property
    def keys(self) -> list[str]:
        """Get all section IDs in the tree."""
        return list(self._sections_index.keys()) + ["root"]

    def __dir__(self):
        """Include section IDs in dir() output for better introspection."""
        return self.keys

    # Getters
    # Get section by ID using dynamic property access
    def __getattr__(self, name: str) -> Section | None:
        """Dynamic property access to sections by ID."""
        if name.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return self._sections_index.get(name)

    def get_section(self, section_id_or_path: str) -> Section | None:
        """Get section by ID or using dot-separated path."""
        if Section.is_path(section_id_or_path):
            matching_path = [
                s for s in self._sections_index.values() if s.path == section_id_or_path
            ]
            return matching_path[0] if matching_path else None
        return self._sections_index.get(section_id_or_path)

    def get_all_sections(self) -> list[Section]:
        """Get all sections in tree."""
        return list(self._sections_index.values())

    def get_all_blocks(self) -> list[Block]:
        """Get all blocks from all sections."""
        blocks = []
        for section in self._sections_index.values():
            blocks.extend(section.blocks)
        return blocks

    # Mutation methods
    def add_section(self, section: Section, parent_path: str | None = None) -> None:
        """Add section to tree."""
        if parent_path:
            if Section.is_path(parent_path):
                parent = self.get_section(parent_path)
            else:
                parent = self._sections_index.get(parent_path)

            if parent:
                parent.add_subsection(section)
            else:
                self.root.add_subsection(section)
        else:
            self.root.add_subsection(section)
        self._sections_index[section.id] = section

    # Serialization
    def to_dict(self) -> SectionData:
        """Convert content tree to dictionary structure."""
        return self.root.to_dict()


class ParsedMarkdownData(TypedDict):
    """Complete data structure after parsing."""

    frontmatter: dict[str, Any]  # Flexible frontmatter
    content: ContentTree  # Root section


class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON export."""

    frontmatter: dict[str, Any]  # Flexible frontmatter
    content: SectionData  # Root section


class MarkdownData:
    """Finds and mutates document data"""

    def __init__(self, parsed_data: ParsedMarkdownData) -> None:
        # Use object.__setattr__ to bypass our custom __setattr__ during init
        object.__setattr__(self, "_frontmatter", parsed_data["frontmatter"])
        object.__setattr__(self, "_content", parsed_data["content"])

    def __repr__(self) -> str:
        return (
            "<MarkdownData "
            f"properties={len(self.frontmatter.keys())} "
            f"sections={len(self.content.keys)} "
            f"frontmatter_keys={list(self.frontmatter.keys())}"
            ">"
        )

    def __dir__(self):
        """Include frontmatter keys in dir() output for better introspection."""
        return ["data"] + list(self.frontmatter.keys()) + self._content.keys

    @property
    def data(self) -> ParsedMarkdownData:
        """Get complete document data."""
        return {"frontmatter": self._frontmatter, "content": self._content}

    @property
    def frontmatter(self) -> dict[str, Any]:
        """Get frontmatter dictionary."""
        return self._frontmatter

    @property
    def content(self) -> ContentTree:
        """Get content tree."""
        return self._content

    def get_section(self, section_id_or_path: str) -> Section | None:
        """Get section by ID or path."""
        return self._content.get_section(section_id_or_path)

    def __getattr__(self, name: str) -> Any:
        """Dynamic access to frontmatter properties."""
        if name.startswith("_"):
            raise AttributeError("Cannot access private attribute")

        # First check if it's a frontmatter property
        if name in self.frontmatter:
            return self.frontmatter[name]

        if name in self._content.keys:
            return self._content.__getattr__(name)

        # If not found in frontmatter, raise AttributeError for proper behavior
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    # Mutation methods

    def _set_frontmatter_property(self, key: str, value: Any) -> None:
        """Set frontmatter property."""
        self._frontmatter[key] = value

    def _set_content(self, content: Section, section_path: str | None) -> None:
        """Set she contents of specified section."""
        raise NotImplementedError("Directly setting sections is not supported yet.")

    def __setattr__(self, name: str, value: Any) -> None:
        """Dynamic setting of frontmatter properties."""
        if name.startswith("_"):
            raise AttributeError("Cannot modify private attribute")
        if name in self._content.keys:
            return self._set_content(value, name)
        self._set_frontmatter_property(name, value)

    def get_sections(self) -> SectionsData:
        """Get all sections from the content tree as structured data."""
        sections_list = [
            section.to_dict() for section in self.content.get_all_sections()
        ]
        sections_by_id = {
            section.id: section.to_dict() for section in self.content.get_all_sections()
        }
        return {"sections": sections_list, "sections_by_id": sections_by_id}

    def get_blocks(self, section_id: str | None = None) -> BlocksData:
        """Get blocks from a specific section or all sections as structured data."""
        if section_id:
            section = self.content.get_section(section_id)
            if section:
                return {"blocks": [b.to_dict() for b in section.blocks]}
            return {"blocks": []}

        blocks = []
        for section in self.content.get_all_sections():
            blocks.extend([b.to_dict() for b in section.blocks])
        return {"blocks": blocks}

    # Serialization
    def to_dict(self) -> MarkdownDataDict:
        """Convert to JSON-serializable dictionary."""
        return {"frontmatter": self.frontmatter, "content": self.content.to_dict()}
