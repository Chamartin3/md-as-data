"""Document structure models for markdown content."""

from __future__ import annotations

from typing import Any, NamedTuple, TypedDict, Union

from .base import (
    BlockType,
    FrontmatterProperties,
    FrontmatterPropertyValue,
    FrontmatterValue,
    HeadingLevel,
    UpdatePolicy,
)


class SectionUpdate(TypedDict, total=False):
    """Structure for section update in batch operation."""

    id: str  # Required
    content: str  # Required
    policy: str | UpdatePolicy  # Optional, defaults to UPDATE


class BatchChanges(TypedDict, total=False):
    """Structure for batch changes to document."""

    frontmatter: dict[str, FrontmatterPropertyValue]
    frontmatter_policy: str | UpdatePolicy
    sections: list[SectionUpdate]


class BatchOperationResult(TypedDict):
    """Result of batch operation."""

    success: bool
    changes_count: int
    frontmatter_changes: int
    section_changes: int
    errors: list[str]
    warnings: list[str]


class SectionQuery(NamedTuple):
    """Result of section query operation."""

    section: Section | None  # The found section (None if not found/ambiguous)
    matched: list[Section]  # All matched sections (for ambiguity detection)
    parent: Section | None  # Parent section if creating new subsection
    error: str | None  # Error message if operation failed


class BlocksQuery(NamedTuple):
    """Result of blocks query with metadata."""

    blocks: list[Block]  # Filtered blocks
    total: int  # Total blocks before filtering


class TaskItemData(TypedDict):
    """Individual task item with status metadata."""

    content: str  # Task text content without checkbox
    symbol: str  # Checkbox character (x, space, !, ~, ?, etc.)


# Public input type for external API (simplified)
InputDataOptions = Union[
    FrontmatterValue,  # Simple frontmatter value (inferred)
    dict,  # Various dict formats with optional policy
    "Section",  # Section object
]


class BlockMetadata(TypedDict, total=False):
    """Metadata attributes for blocks."""

    language: str  # For code blocks
    href: str  # For links
    src: str  # For images
    alt: str  # For images
    title: str  # For links/images
    tasks: list[TaskItemData]  # For task list blocks


class BlockData(TypedDict):
    """Structured data for individual blocks."""

    section_id: str  # ID of the section this block belongs to
    type: str  # BlockType value
    content: str | list[str]
    metadata: dict[str, Any]


class Block:
    """Base block in markdown content."""

    def __init__(
        self, section_id: str, block_type: BlockType, content: str | list[str]
    ):
        self.section = section_id
        self.type = block_type
        self.content = content
        self.metadata: dict[str, Any] = {}

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

        if self.type == BlockType.TASK_LIST:
            if isinstance(self.content, list) and "tasks" in self.metadata:
                items = []
                tasks_data = self.metadata["tasks"]
                # tasks_data should be a list[TaskItemData]
                # but metadata is typed as dict[str, str]
                # We need to handle this at runtime
                if isinstance(tasks_data, list):
                    for i, content in enumerate(self.content):
                        if i < len(tasks_data):
                            task_item = tasks_data[i]
                            if isinstance(task_item, dict):
                                symbol = task_item.get("symbol", " ")
                            else:
                                symbol = " "
                            items.append(f"- [{symbol}] {content}")
                        else:
                            # Fallback if tasks metadata is missing for some items
                            items.append(f"- [ ] {content}")
                    return "\n".join(items)
                # Fallback if tasks is not a list
                return "\n".join(f"- [ ] {item}" for item in self.content)
            else:
                # Fallback for malformed task list
                if isinstance(self.content, list):
                    return "\n".join(f"- [ ] {item}" for item in self.content)
                else:
                    return f"- [ ] {self.content}"

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
    children: list[SectionData] | None


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
        self.children: list[Section] = []
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
        self.children.append(section)

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
            section_data: Standard SectionData with blocks field (no raw
                          content). MarkdownData handles content parsing.
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
        children = section_data.get("children")
        if children is not None:
            for subsection_data in children:
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
            "children": [s.to_dict() for s in self.children],
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
        for subsection in self.children:
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
            f"blocks={len(self.blocks)} subsections={len(self.children)}>"
        )


SectionsMap = dict[str, Section]
ContentInput = Union[str, dict[str, str], "Section"]


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
        policy: UpdatePolicy = UpdatePolicy.UPDATE,
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
        if policy == UpdatePolicy.REPLACE:
            self._apply_replace_policy(target_section, section, section_path)
        elif policy == UpdatePolicy.UPDATE:
            self._apply_update_policy(target_section, section, section_path)
        elif policy == UpdatePolicy.APPEND:
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
                parent.children = [
                    s for s in parent.children if s.id != target_section.id
                ]
        else:
            # Remove from root
            self.root.children = [
                s for s in self.root.children if s.id != target_section.id
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
        new_subsection_ids = {s.id for s in new_section.children}

        # Remove existing subsections that are being replaced
        target_section.children = [
            s for s in target_section.children if s.id not in new_subsection_ids
        ]

        # Add new/updated subsections
        for new_subsection in new_section.children:
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
        existing_subsection_ids = {s.id for s in target_section.children}

        for new_subsection in new_section.children:
            if new_subsection.id in existing_subsection_ids:
                # Recursively append to existing subsection
                existing_subsection = next(
                    s for s in target_section.children if s.id == new_subsection.id
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

        for subsection in section.children:
            self._index_section_recursive(subsection)

    def _get_section_by_path(self, path: str) -> Section | None:
        """Navigate to section using dot-separated path."""
        parts = path.split(".")
        current_section = self.root

        for part in parts:
            found = False
            for subsection in current_section.children:
                if subsection.id == part:
                    current_section = subsection
                    found = True
                    break
            if not found:
                return None

        return current_section if current_section != self.root else None

    def query_section(self, section_id: str) -> SectionQuery:
        """Comprehensive section query with validation and ambiguity detection.

        This method handles ALL section lookup scenarios:
        1. Exact match (ID or path) -> returns section
        2. New subsection path (parent.child where child doesn't exist)
           -> returns parent
        3. Fuzzy match (partial ID) -> returns matches or ambiguity error
        4. Not found -> returns error

        Args:
            section_id: Section identifier - can be:
                       - Simple ID: "introduction"
                       - Full path: "introduction.overview"
                       - Partial match: "intro" (fuzzy)

        Returns:
            SectionQuery with one of these states:

            SUCCESS - Exact match:
                section=<found>, matched=[<found>], parent=None, error=None

            SUCCESS - Creating new subsection:
                section=None, matched=[], parent=<parent>, error=None

            SUCCESS - Single fuzzy match:
                section=<found>, matched=[<found>], parent=None, error=None

            ERROR - Ambiguous:
                section=None, matched=[<s1>, <s2>, ...], parent=None,
                error="Ambiguous..."

            ERROR - Not found:
                section=None, matched=[], parent=None, error="Section ... not found"

            ERROR - Invalid parent path:
                section=None, matched=[], parent=None, error="Parent path ... not found"
        """
        # STEP 1: Try exact lookup first (most common case)
        exact = self.get_section(section_id)
        if exact:
            return SectionQuery(section=exact, matched=[exact], parent=None, error=None)

        # STEP 2: Check if it's a path for creating new subsection
        # Pattern: "parent.child" or "parent.sub.child" where child doesn't exist
        if Section.SECTION_PATH_SEPARATOR in section_id:
            parts = section_id.split(Section.SECTION_PATH_SEPARATOR)
            parent_path = Section.SECTION_PATH_SEPARATOR.join(parts[:-1])

            parent = self.get_section(parent_path)
            if parent:
                # Parent exists - this is valid new subsection creation
                return SectionQuery(section=None, matched=[], parent=parent, error=None)
            # Parent doesn't exist - invalid path
            return SectionQuery(
                section=None,
                matched=[],
                parent=None,
                error=(
                    f"Parent path '{parent_path}' not found "
                    f"for new section '{section_id}'"
                ),
            )

        # STEP 3: Try fuzzy matching (partial ID match)
        # This allows users to type "intro" instead of "introduction"
        matches = []
        for section in self._sections_index.values():
            # Match if section_id equals the section ID
            if section.id == section_id:
                matches.append(section)
            # OR if section_id appears anywhere in the section's full path
            elif section_id in section.path:
                matches.append(section)

        # STEP 4: Interpret fuzzy match results
        if len(matches) == 0:
            # No matches found
            return SectionQuery(
                section=None,
                matched=[],
                parent=None,
                error=f"Section '{section_id}' not found",
            )
        if len(matches) == 1:
            # Single fuzzy match - treat as success
            return SectionQuery(
                section=matches[0], matched=matches, parent=None, error=None
            )
        # Multiple matches - ambiguous reference
        paths = [s.path for s in matches]
        return SectionQuery(
            section=None,
            matched=matches,
            parent=None,
            error=f"Ambiguous reference '{section_id}' matches: {', '.join(paths)}",
        )

    def find_blocks(
        self, block_type: str | None = None, section_id: str | None = None
    ) -> BlocksQuery:
        """Find blocks with flexible filtering.

        Args:
            block_type: Filter by block type (e.g., 'paragraph')
            section_id: Filter blocks from specific section

        Returns:
            BlocksQuery with filtered blocks and metadata
        """
        # Get base blocks
        if section_id:
            section = self.get_section(section_id)
            all_blocks = list(section.blocks) if section else []
        else:
            all_blocks = self.get_all_blocks()

        total = len(all_blocks)

        # Apply type filter
        if block_type:
            filtered = [b for b in all_blocks if b.type.value == block_type]
        else:
            filtered = all_blocks

        return BlocksQuery(blocks=filtered, total=total)

    def get_parent_section(self, path: str) -> Section | None:
        """Get parent section from dot-separated path."""
        if Section.SECTION_PATH_SEPARATOR not in path:
            return None
        parts = path.split(Section.SECTION_PATH_SEPARATOR)
        parent_path = Section.SECTION_PATH_SEPARATOR.join(parts[:-1])
        return self.get_section(parent_path)

    @staticmethod
    def generate_section_title(section_id: str) -> str:
        """Generate human-readable title from section ID."""
        return section_id.replace("_", " ").title()

    # Serialization
    def to_dict(self) -> SectionData:
        """Convert content tree to dictionary structure."""
        return self.root.to_dict()


class ParsedMarkdownData(TypedDict):
    """Complete data structure after parsing."""

    frontmatter: FrontmatterProperties
    content: ContentTree  # Root section


class MarkdownDataDict(TypedDict):
    """Complete document structure for JSON export."""

    frontmatter: FrontmatterProperties
    content: SectionData  # Root section


class SectionInputData(TypedDict, total=False):
    """Input data for section creation/modification."""

    id: str
    title: str
    level: int
    path: str
    content: str  # Raw markdown content
    blocks: list[BlockData]  # Structured blocks
    children: list[SectionInputData]


class SectionContentData(TypedDict):
    """Section data with raw markdown content."""

    id: str
    title: str
    level: int
    path: str
    content: str  # Raw markdown content
    children: list[SectionContentData] | None


class SectionBlocksData(TypedDict):
    """Section data with structured blocks."""

    id: str
    title: str
    level: int
    path: str
    blocks: list[BlockData]
    children: list[SectionBlocksData] | None
