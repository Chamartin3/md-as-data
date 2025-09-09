"""Data structures for representing and managing markdown content."""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar, Union, cast

if TYPE_CHECKING:
    from .file import MarkdownParser


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


class SectionPolicy(Enum):
    """Policies for section mutation operations."""

    REPLACE = "replace"  # Replace entire section and all subsections
    UPDATE = "update"  # Replace blocks and specified subsections, keep others
    APPEND = "append"  # Add content without removing existing content


class InputType(Enum):
    """Types of input for __setattr__ validation."""

    FRONTMATTER_PROPERTY = "frontmatter_property"
    SECTION_CONTENT_WITH_POLICY = "section_content_with_policy"
    SECTION_CONTENT_DEFAULT = "section_content_default"


class ValidationResult(TypedDict):
    """Result from input validation."""

    input_type: InputType
    content: ContentInput | FrontmatterPropertyValue | None
    policy: SectionPolicy | None


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

    @classmethod
    def from_dict(cls, block_data: BlockData, section_id: str | None = None) -> Block:
        """Create Block object from structured data.

        Args:
            block_data: Block specification dictionary
            section_id: Override section_id if provided

        Returns:
            Block object with proper type and metadata
        """
        block_type = BlockType(block_data["type"])
        section_ref = section_id or block_data["section_id"]

        block = cls(
            section_id=section_ref, block_type=block_type, content=block_data["content"]
        )

        # Add metadata if present
        if block_data.get("metadata"):
            block.metadata.update(block_data["metadata"])

        return block

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
    subsections: list[SectionData] | None


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

    def add_subsection(self, section: Section) -> None:
        """Add a subsection to this section."""
        if section.level <= self.level:
            raise ValueError(
                "Subsection level must be greater than parent section level. "
                f"Got {section.level} for subsection and {self.level} for parent."
            )
        self.subsections.append(section)

    def create_subsection(self, title: str, content: str | None) -> Section:
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

    @classmethod
    def from_dict(
        cls, section_data: SectionData, parent_path: str | None = None
    ) -> Section:
        """Create Section object from standard SectionData dictionary.

        Args:
            section_data: Standard SectionData with blocks field (no raw content)
                         MarkdownData handles content parsing before calling this method
            parent_path: Optional parent section path for hierarchy building

        Returns:
            Fully constructed Section object with all blocks properly parsed

        Raises:
            ValueError: If section_data is malformed or contains invalid references
            TypeError: If section_data structure is invalid
        """
        # 1. Validate input structure
        cls._validate_section_data(section_data)

        # 2. Create base section
        section = cls(
            title=section_data["title"],
            level=HeadingLevel(section_data["level"]),
            parent_path=parent_path,
        )

        # 3. Process blocks (standard SectionData format)
        blocks = section_data.get("blocks")
        if blocks is not None:
            for block_data in blocks:
                block = Block.from_dict(block_data, section.id)
                section.add_block(block)

        # 4. Add subsections recursively
        subsections = section_data.get("subsections")
        if subsections is not None:
            for subsection_data in subsections:
                subsection = cls.from_dict(subsection_data, section.path)
                section.add_subsection(subsection)

        return section

    @classmethod
    def _validate_section_data(cls, section_data: SectionData) -> None:
        """Validate section data structure."""
        required_fields = ["id", "title", "level", "path"]

        for field in required_fields:
            if field not in section_data:
                raise ValueError(f"Missing required field: '{field}'")

        # Validate level
        if not isinstance(section_data["level"], int) or not (
            1 <= section_data["level"] <= 6
        ):
            raise ValueError(
                f"Invalid heading level: {section_data['level']} (must be 1-6)"
            )

        # Validate blocks if present
        if section_data.get("blocks"):
            if not isinstance(section_data["blocks"], list):
                raise TypeError("'blocks' field must be a list")

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
ContentInput = Union[str, dict[str, Any], "Section"]

# Generic frontmatter properties type
# Type alias for frontmatter property values
FrontmatterPropertyValue = str | int | float | bool | list[str] | None | Any
FrontmatterProperty = TypeVar("FrontmatterProperty", bound=FrontmatterPropertyValue)
FrontmatterProperties = dict[str, FrontmatterPropertyValue]


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
            return self._get_section_by_path(section_id_or_path)
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

    # Policy-based mutation methods
    def set_section(
        self,
        section: Section,
        section_path: str,
        policy: SectionPolicy = SectionPolicy.UPDATE,
    ) -> None:
        """Set section with policy-based mutation.

        Args:
            section: Fully parsed Section object from MarkdownData
            section_path: Target section path (dot-separated or section ID)
            policy: Mutation policy (replace, update, append)

        Raises:
            ValueError: If section_path is invalid or conflicts exist
            TypeError: If section is not a Section object
        """
        # 1. Input validation
        if not section_path:
            raise ValueError("section_path cannot be empty")

        if not isinstance(section, Section):
            raise TypeError(f"Expected Section object, got {type(section)}")

        # 2. Find target section
        target_section = self.get_section(section_path)

        # 3. Handle new section creation
        if not target_section:
            self.add_section(section)
            return

        # 4. Apply policy-specific logic
        if policy == SectionPolicy.REPLACE:
            self._apply_replace_policy(target_section, section, section_path)
        elif policy == SectionPolicy.UPDATE:
            self._apply_update_policy(target_section, section, section_path)
        elif policy == SectionPolicy.APPEND:
            self._apply_append_policy(target_section, section, section_path)
        else:
            raise ValueError(f"Unknown policy: {policy}")

    def _apply_replace_policy(
        self, target_section: Section, new_section: Section, section_path: str
    ) -> None:
        """Complete replacement of target section and all subsections."""

        # 1. Preserve parent relationship
        parent_path = target_section.parent_path

        # 2. Remove target section from parent
        if parent_path:
            parent = self.get_section(parent_path)
            if parent:
                parent.subsections = [
                    s for s in parent.subsections if s.id != target_section.id
                ]
        else:
            # Remove from root
            self.root.subsections = [
                s for s in self.root.subsections if s.id != target_section.id
            ]

        # 3. Configure new section
        new_section.parent_path = parent_path

        # 4. Add new section
        self.add_section(new_section, parent_path)

        # 5. Update sections index
        self._sections_index[new_section.id] = new_section
        if new_section.id != target_section.id:
            if target_section.id in self._sections_index:
                del self._sections_index[target_section.id]

    def _apply_update_policy(
        self, target_section: Section, new_section: Section, section_path: str
    ) -> None:
        """Selective update preserving unspecified subsections."""

        # 1. Replace blocks completely - avoids complex block comparison
        # Clear all existing blocks and replace with new ones
        target_section.blocks.clear()
        target_section.blocks.extend(new_section.blocks)

        # Update block section references
        for block in target_section.blocks:
            block.section = target_section.id

        # 2. Update section metadata
        target_section.title = new_section.title
        target_section.level = new_section.level

        # 3. Update/add specified subsections, preserve unspecified ones
        new_subsection_ids = {s.id for s in new_section.subsections}

        # Remove existing subsections that are being replaced
        target_section.subsections = [
            s for s in target_section.subsections if s.id not in new_subsection_ids
        ]

        # Add new/updated subsections
        for new_subsection in new_section.subsections:
            target_section.add_subsection(new_subsection)

        # 4. Update section index for all modified subsections
        self._rebuild_section_index()

    def _apply_append_policy(
        self, target_section: Section, new_section: Section, section_path: str
    ) -> None:
        """Additive content modification without removing existing content."""

        # 1. Append blocks to existing ones
        for block in new_section.blocks:
            # Update section reference for new blocks
            block.section = target_section.id
            target_section.blocks.append(block)

        # 2. Handle subsections (recursive append for conflicts)
        existing_subsection_ids = {s.id for s in target_section.subsections}

        for new_subsection in new_section.subsections:
            if new_subsection.id in existing_subsection_ids:
                # Recursively append to existing subsection
                existing_subsection = next(
                    s for s in target_section.subsections if s.id == new_subsection.id
                )
                # Recursive call to handle nested appending
                self._apply_append_policy(
                    existing_subsection,
                    new_subsection,
                    f"{section_path}.{new_subsection.id}",
                )
            else:
                # Add entirely new subsection
                target_section.add_subsection(new_subsection)

        # 3. Update section index
        self._rebuild_section_index()

    def _rebuild_section_index(self) -> None:
        """Rebuild the complete sections index after structural changes."""
        self._sections_index.clear()
        self._index_section_recursive(self.root)

    def _index_section_recursive(self, section: Section) -> None:
        """Recursively rebuild section index."""
        if section.level != HeadingLevel.ROOT:
            self._sections_index[section.id] = section

        for subsection in section.subsections:
            self._index_section_recursive(subsection)

    def _get_section_by_path(self, path: str) -> Section | None:
        """Navigate to section using dot-separated path."""
        parts = path.split(".")
        current_section = self.root

        for part in parts:
            found = False
            for subsection in current_section.subsections:
                if subsection.id == part:
                    current_section = subsection
                    found = True
                    break
            if not found:
                return None

        return current_section if current_section != self.root else None

    # Serialization
    def to_dict(self) -> SectionData:
        """Convert content tree to dictionary structure."""
        return self.root.to_dict()


class ParsedMarkdownData(TypedDict):
    """Complete data structure after parsing."""

    frontmatter: FrontmatterProperties  # Flexible frontmatter
    content: ContentTree  # Root section


class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON export."""

    frontmatter: FrontmatterProperties  # Flexible frontmatter
    content: SectionData  # Root section


class SectionInputData(TypedDict, total=False):
    """Input data for section creation/modification."""

    id: str
    title: str
    level: int
    path: str
    content: str  # Raw markdown content
    blocks: list[BlockData]  # Structured blocks
    subsections: list[SectionInputData]


class SectionContentData(TypedDict):
    """Section data with raw markdown content."""

    id: str
    title: str
    level: int
    path: str
    content: str  # Raw markdown content
    subsections: list[SectionContentData] | None


class SectionBlocksData(TypedDict):
    """Section data with structured blocks."""

    id: str
    title: str
    level: int
    path: str
    blocks: list[BlockData]
    subsections: list[SectionBlocksData] | None


class MarkdownData:
    """Document with frontmatter and content structure.

    MarkdownData is the exclusive owner of the parser and handles all
    content parsing before delegating structural operations to ContentTree.
    """

    _content: ContentTree
    _frontmatter: FrontmatterProperties

    def __init__(
        self, parsed_data: ParsedMarkdownData, parser: MarkdownParser | None = None
    ) -> None:
        # Use object.__setattr__ to bypass our custom __setattr__ during init
        object.__setattr__(self, "_frontmatter", parsed_data["frontmatter"])
        object.__setattr__(self, "_content", parsed_data["content"])
        object.__setattr__(self, "_parser", parser)

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
    def frontmatter(self) -> FrontmatterProperties:
        """Get frontmatter dictionary."""
        return self._frontmatter

    @property
    def content(self) -> ContentTree:
        """Get content tree."""
        return self._content

    def get_section(self, section_id_or_path: str) -> Section | None:
        """Get section by ID or path."""
        return self._content.get_section(section_id_or_path)

    def get_all_sections(self) -> list[Section]:
        """Get all sections."""
        return self._content.get_all_sections()

    def __getattr__(self, name: str) -> FrontmatterPropertyValue | Section:
        """Dynamic access to frontmatter properties."""
        if name.startswith("_"):
            raise AttributeError("Cannot access private attribute")

        # First check if it's a frontmatter property
        if name in self.frontmatter:
            return self.frontmatter[name]

        if name in self._content.keys:
            section = self._content.__getattr__(name)
            if section is not None:
                return section

        # If not found in frontmatter, raise AttributeError for proper behavior
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    # Mutation methods

    def _set_frontmatter_property(
        self, key: str, value: FrontmatterPropertyValue
    ) -> None:
        """Set frontmatter property."""
        self._frontmatter[key] = value

    def _set_content(
        self,
        content: ContentInput,
        section_path: str | None,
        policy: SectionPolicy = SectionPolicy.UPDATE,
    ) -> None:
        """Set section content with policy support.

        MarkdownData handles all content parsing, then delegates structural
        operations to ContentTree with fully parsed Section objects.
        """
        if section_path is None:
            raise ValueError("section_path cannot be None for content setting")

        try:
            # 1. Parse and prepare section using MarkdownData's parser
            parsed_section = self._prepare_section(content, section_path)

            # 2. Delegate to ContentTree for structural operation
            self._content.set_section(parsed_section, section_path, policy)

        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to set section '{section_path}': {e}") from e

    def _prepare_section(self, content: ContentInput, section_path: str) -> Section:
        """Prepare section content and parse markdown using MarkdownData's parser."""

        if content is None:
            raise ValueError("content cannot be None")

        if isinstance(content, str):
            # Handle raw markdown string
            section_data = self._create_section_data_from_markdown(
                markdown_content=content, section_path=section_path
            )
            return Section.from_dict(section_data)

        elif isinstance(content, dict):
            # Validate format first
            input_data = cast(SectionInputData, content)
            self._validate_section_input_format(input_data)

            # Handle content vs blocks format
            if "content" in input_data:
                # Parse markdown content to blocks format
                section_data = self._create_section_data_from_markdown(
                    markdown_content=input_data["content"],
                    section_id=input_data.get("id"),
                    title=input_data.get("title"),
                    level=input_data.get("level"),
                    section_path=input_data.get("path", "root"),
                    subsections=cast(
                        "list[SectionContentData] | None", input_data.get("subsections")
                    ),
                )
                return Section.from_dict(section_data)
            else:
                # Handle blocks format directly
                blocks_data = cast(SectionData, content)
                return Section.from_dict(blocks_data)

        else:
            # Handle Section object - return as-is
            return content

    def _validate_section_input_format(self, content: SectionInputData) -> None:
        """Validate section input format (content OR blocks, not both)."""
        has_content = "content" in content
        has_blocks = "blocks" in content

        if has_content and has_blocks:
            raise ValueError(
                "Cannot specify both 'content' and 'blocks' fields - choose one format"
            )

        if not (has_content or has_blocks):
            raise ValueError(
                "Must provide either 'content' (markdown text) or 'blocks' format"
            )

        # Type validation
        if has_content and not isinstance(content["content"], str):
            raise TypeError("'content' field must be a string")

        if has_blocks and not isinstance(content["blocks"], list):
            raise TypeError("'blocks' field must be a list")

    def _create_section_data_from_markdown(
        self,
        markdown_content: str,
        section_path: str,
        section_id: str | None = None,
        title: str | None = None,
        level: int | None = None,
        subsections: list[SectionContentData] | None = None,
    ) -> SectionData:
        """Create SectionData from markdown content with optional metadata.

        This method parses markdown content directly into a complete SectionData
        structure, avoiding the need for temporary sections.
        """
        # Derive missing fields from section_path
        final_section_id = section_id or section_path.split(".")[-1]
        final_title = title or final_section_id.replace("_", " ").title()
        final_level = level or 1
        final_subsections = subsections or []

        # Parse markdown content directly into SectionData
        if not markdown_content or not markdown_content.strip():
            blocks_data = []
        elif not self._parser:
            # Fallback: create paragraph block data
            blocks_data = [
                {
                    "section_id": final_section_id,
                    "type": BlockType.PARAGRAPH.value,
                    "content": markdown_content.strip(),
                    "metadata": {},
                }
            ]
        else:
            # Parse using the parser with temporary section wrapper
            try:
                # Wrap content in temporary section for proper parsing
                temp_markdown = f"# Temp\n\n{markdown_content}"
                parsed_data = self._parser.parse(temp_markdown)  # type: ignore[attr-defined]
                content_tree = parsed_data["content"]

                if content_tree and content_tree.get_all_sections():
                    # Extract blocks from the first (temporary) section
                    first_section = content_tree.get_all_sections()[0]
                    blocks_data = [block.to_dict() for block in first_section.blocks]
                    # Update section references in block data to use final section ID
                    for block_data in blocks_data:
                        block_data["section_id"] = final_section_id
                else:
                    blocks_data = []
            except Exception:
                # Fallback to paragraph block on parse error
                blocks_data = [
                    {
                        "section_id": final_section_id,
                        "type": BlockType.PARAGRAPH.value,
                        "content": markdown_content.strip(),
                        "metadata": {},
                    }
                ]

        # Create complete SectionData structure
        return cast(
            SectionData,
            {
                "id": final_section_id,
                "title": final_title,
                "level": final_level,
                "path": section_path,
                "blocks": blocks_data,
                "subsections": final_subsections,
            },
        )

    def _validate_input(
        self,
        name: str,
        value: FrontmatterPropertyValue
        | ContentInput
        | tuple[ContentInput, SectionPolicy],
    ) -> ValidationResult:
        """Validate input and return the appropriate handling strategy."""
        # Basic validation
        if name.startswith("_"):
            raise AttributeError("Cannot modify private attribute")

        if value is None:
            raise ValueError("content cannot be None")

        # Check if trying to set existing section directly (not allowed in old API)
        if name in self._content.keys:
            # Only allow explicit section content (dict with section fields,
            # tuples with policy, Section objects)
            is_explicit_section_data = (
                isinstance(value, dict)
                and any(key in value for key in ["content", "blocks", "title", "level"])
                or isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[1], SectionPolicy)
                or hasattr(value, "add_block")  # Section object
            )
            if not is_explicit_section_data:
                raise NotImplementedError("Directly setting sections is not supported")

        # Determine input type based on content analysis
        # Policy tuple: content with explicit policy
        if isinstance(value, tuple) and len(value) == 2:
            content, policy = value
            if not isinstance(policy, SectionPolicy):
                raise TypeError(
                    f"Policy must be SectionPolicy enum, got {type(policy)}"
                )
            return {
                "input_type": InputType.SECTION_CONTENT_WITH_POLICY,
                "content": cast(ContentInput, content),
                "policy": policy,
            }

        # Check if this looks like section content (not a simple frontmatter value)
        is_section_content = (
            isinstance(value, dict)
            and any(key in value for key in ["content", "blocks", "title", "level"])
            or isinstance(value, str)
            and (
                "\n" in value  # Multiline content
                or len(value) > 50  # Long content (likely prose, not metadata)
                or any(
                    word in value.lower()
                    for word in ["content", "paragraph", "section", "chapter"]
                )  # Content keywords
            )
            or hasattr(value, "add_block")  # Section object
        )

        if is_section_content:
            return {
                "input_type": InputType.SECTION_CONTENT_DEFAULT,
                "content": cast(ContentInput, value),
                "policy": SectionPolicy.UPDATE,
            }
        else:
            # Treat as frontmatter property
            return {
                "input_type": InputType.FRONTMATTER_PROPERTY,
                "content": cast(FrontmatterPropertyValue, value),
                "policy": None,
            }

    def __setattr__(
        self,
        name: str,
        value: FrontmatterPropertyValue
        | ContentInput
        | tuple[ContentInput, SectionPolicy],
    ) -> None:
        """Dynamic property setting with policy support."""
        # Validate input and determine handling strategy
        validation = self._validate_input(name, value)

        # Route to appropriate handler based on input type
        if validation["input_type"] == InputType.SECTION_CONTENT_WITH_POLICY:
            return self._set_content(
                cast(ContentInput, validation["content"]),
                name,
                cast(SectionPolicy, validation["policy"]),
            )
        elif validation["input_type"] == InputType.SECTION_CONTENT_DEFAULT:
            return self._set_content(
                cast(ContentInput, validation["content"]),
                name,
                cast(SectionPolicy, validation["policy"]),
            )
        elif validation["input_type"] == InputType.FRONTMATTER_PROPERTY:
            return self._set_frontmatter_property(
                name, cast(FrontmatterPropertyValue, validation["content"])
            )
        else:
            raise ValueError(f"Unknown input type: {validation['input_type']}")

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
