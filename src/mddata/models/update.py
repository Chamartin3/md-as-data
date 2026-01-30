"""Update operation types for markdown documents.

This module contains all types related to document update operations:
- SectionUpdate: Section update with validation and structure
- BatchOperationResult: Result of batch update operations
- MarkdownDataUpdate: Document update with policies and parameters
"""

from dataclasses import dataclass, field
from typing import Any, TypeAlias, TypedDict

from .base import FrontmatterProperties, FrontmatterValue, UpdatePolicy
from .document import Section, SectionData
from .template import ParameterDefinition

# =============================================================================
# Input Data Type Definitions
# =============================================================================


class UpdateInputDict(TypedDict, total=False):
    """Base for dict to define data for update operations."""

    policy: UpdatePolicy


class InputDictSectionContent(UpdateInputDict):
    """Section input using raw markdown text content.

    Example:
        {"content": "# Title\n\nContent here", "policy": "replace"}
    """

    content: str


class InputDictSectionData(UpdateInputDict):
    """Structured section input with full SectionData fields.

    Extends SectionData with optional policy field for update control.

    Example:
        {
            "id": "intro",
            "title": "Introduction",
            "level": 1,
            "path": "intro",
            "blocks": [...],
            "children": [...],
            "policy": "update"
        }
    """

    # SectionData fields (inherited via intersection)
    id: str
    title: str
    level: int
    path: str
    blocks: list[dict[str, Any]] | None
    children: list[Any] | None  # Recursive type


class InputDictSectionObject(UpdateInputDict):
    """Explicit section input when Section object is provided.

    Example:
        {"section": <Section object>, "policy": "replace"}
    """

    section: Section


# Union of all dict-based input formats
InputDataDictOptions = (
    InputDictSectionContent | InputDictSectionData | InputDictSectionObject
)


# Complete input options type (single source of truth)
# Clean vertical dependency: Level 3 imports from Level 0 (base) and Level 1 (document)
InputDataOptions: TypeAlias = (
    FrontmatterValue  # Simple frontmatter value (Level 0: base.py)
    | InputDataDictOptions  # Typed dict formats with optional policy
    | Section  # Section object (Level 1: document.py)
)


# =============================================================================
# Section Update Operations
# =============================================================================


@dataclass
class SectionUpdate:
    """Section update with validation and recursive structure support.

    This dataclass represents a section update operation that can:
    - Create flat updates (backward compatible with BatchChanges)
    - Create hierarchical updates (new nested structure)
    - Validate section data
    - Convert to SectionData format
    - Support recursive child sections
    """

    # Required fields
    id: str  # Section identifier
    content: str | None = None  # New content (raw markdown) - optional for structured

    # Update metadata
    policy: UpdatePolicy = UpdatePolicy.UPDATE

    # Optional structured data (from SectionData)
    title: str | None = None
    level: int | None = None
    path: str | None = None
    blocks: list[dict[str, Any]] = field(default_factory=list)
    children: list["SectionUpdate"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate section update after initialization."""
        # Convert string policy to enum
        if isinstance(self.policy, str):
            self.policy = UpdatePolicy[self.policy.upper()]

        # Validate that we have either content or structured data
        if not self.content and not self.blocks and not self.children:
            raise ValueError(
                f"SectionUpdate '{self.id}' must have content, blocks, or children"
            )

        # Validate level if provided
        if self.level is not None and not (1 <= self.level <= 6):
            raise ValueError(f"Invalid heading level {self.level} (must be 1-6)")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format (for JSON serialization)."""
        result: dict[str, Any] = {
            "id": self.id,
            "policy": (
                self.policy.value
                if isinstance(self.policy, UpdatePolicy)
                else self.policy
            ),
        }

        # Add content if present
        if self.content is not None:
            result["content"] = self.content

        # Add optional structured fields if present
        if self.title is not None:
            result["title"] = self.title
        if self.level is not None:
            result["level"] = self.level
        if self.path is not None:
            result["path"] = self.path
        if self.blocks:
            result["blocks"] = self.blocks
        if self.children:
            # Recursively convert children
            result["children"] = [child.to_dict() for child in self.children]

        return result

    def to_section_data(self) -> SectionData:
        """Convert to SectionData format (for document structure)."""
        # Extract title and level from content if not provided
        if self.content and (not self.title or not self.level):
            extracted_title, extracted_level = self._extract_heading_from_content(
                self.content
            )
            title = self.title or extracted_title or self._generate_title_from_id()
            level = self.level or extracted_level or 1
        else:
            title = self.title or self._generate_title_from_id()
            level = self.level or 1

        path = self.path or self.id

        # Handle blocks - convert raw content to blocks if needed
        blocks: list[dict[str, Any]] | None
        if self.blocks:
            blocks = self.blocks
        elif self.content:
            # Strip heading and convert remaining content to blocks
            content_without_heading = self._strip_heading_from_content(self.content)
            if content_without_heading.strip():
                blocks = [
                    {
                        "section_id": self.id,
                        "type": "paragraph",
                        "content": content_without_heading,
                        "metadata": {},
                    }
                ]
            else:
                blocks = None
        else:
            blocks = None

        section_data: SectionData = {
            "id": self.id,
            "title": title,
            "level": level,
            "path": path,
            "blocks": blocks,
            "children": (
                [child.to_section_data() for child in self.children]
                if self.children
                else None
            ),
        }

        return section_data

    def _strip_heading_from_content(self, content: str) -> str:
        """Strip markdown heading from content string.

        Args:
            content: Raw content that may start with a heading
                (e.g., "# Title\n\nContent")

        Returns:
            Content without the heading line
        """
        lines = content.split("\n", 2)  # Split into at most 3 parts
        if not lines:
            return ""

        # Check if first line is a heading
        first_line = lines[0].strip()
        if first_line.startswith("#"):
            # Remove first line and any blank line after it
            if len(lines) > 1:
                # If second line is empty, skip it too
                if len(lines) > 1 and not lines[1].strip():
                    return lines[2] if len(lines) > 2 else ""
                else:
                    return "\n".join(lines[1:])
            return ""

        return content

    def _extract_heading_from_content(
        self, content: str
    ) -> tuple[str | None, int | None]:
        """Extract heading title and level from markdown content.

        Args:
            content: Raw content that may start with a heading
                (e.g., "# Title\n\nContent")

        Returns:
            Tuple of (title, level) or (None, None) if no heading found
        """
        lines = content.split("\n", 1)
        if not lines:
            return None, None

        first_line = lines[0].strip()
        if not first_line.startswith("#"):
            return None, None

        # Count heading level
        level = 0
        for char in first_line:
            if char == "#":
                level += 1
            else:
                break

        # Extract title (text after the # symbols)
        title = first_line[level:].strip()

        return title, level if 1 <= level <= 6 else None

    def _generate_title_from_id(self) -> str:
        """Generate human-readable title from section ID."""
        return self.id.replace("_", " ").replace("-", " ").title()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SectionUpdate":
        """Create SectionUpdate from dictionary."""
        # Parse policy
        policy_value = data.get("policy", "update")
        if isinstance(policy_value, str):
            policy = UpdatePolicy[policy_value.upper()]
        else:
            policy = policy_value

        # Parse children recursively
        children_data = data.get("children", [])
        children = [cls.from_dict(child) for child in children_data]

        return cls(
            id=data["id"],
            content=data.get("content"),
            policy=policy,
            title=data.get("title"),
            level=data.get("level"),
            path=data.get("path"),
            blocks=data.get("blocks", []),
            children=children,
        )

    def add_child(self, child: "SectionUpdate") -> None:
        """Add a child section update."""
        self.children.append(child)

    def has_children(self) -> bool:
        """Check if section has child updates."""
        return bool(self.children)

    def is_hierarchical(self) -> bool:
        """Check if this is a hierarchical update (has structured data)."""
        return bool(self.title or self.level or self.blocks or self.children)

    def is_flat(self) -> bool:
        """Check if this is a flat update (just id and content)."""
        return bool(self.content) and not self.is_hierarchical()

    def validate(self) -> list[str]:
        """Validate section update and return list of validation errors."""
        errors: list[str] = []

        # Validate ID
        if not self.id or not self.id.strip():
            errors.append("Section ID cannot be empty")

        # Validate content requirement
        if not self.content and not self.blocks and not self.children:
            errors.append(f"Section '{self.id}' must have content, blocks, or children")

        # Validate level
        if self.level is not None and not (1 <= self.level <= 6):
            errors.append(f"Invalid level {self.level} for section '{self.id}'")

        # Recursively validate children
        for i, child in enumerate(self.children):
            child_errors = child.validate()
            for error in child_errors:
                errors.append(f"Child {i} ({child.id}): {error}")

        return errors


# =============================================================================
# Batch Operation Results
# =============================================================================


class BatchOperationResult(TypedDict):
    """Result of batch operation."""

    success: bool
    changes_count: int
    frontmatter_changes: int
    section_changes: int
    errors: list[str]
    warnings: list[str]


# =============================================================================
# Document Update Format
# =============================================================================


@dataclass
class MarkdownDataUpdate:
    """Document update operations with optional policies and parameters.

    This dataclass represents both simple updates (from JSON/YAML data files)
    and parameterized templates. It replaces the old BatchChanges type.

    Design Philosophy:
    - Composes document structure with update metadata
    - Adds update-specific metadata (policies, parameters)
    - Supports both flat section lists (backward compat) and hierarchical content
    - Templates are just MarkdownDataUpdate with parameters defined

    Backward Compatibility:
    - Old BatchChanges JSON maps directly to this structure
    - Optional parameters field makes templates special cases
    - Flat sections list maintained for legacy support
    """

    # Core document data
    frontmatter: FrontmatterProperties = field(default_factory=dict)
    content: SectionData | None = field(default=None)

    # Update-specific metadata
    frontmatter_policy: UpdatePolicy = UpdatePolicy.MERGE
    parameters: dict[str, ParameterDefinition] = field(default_factory=dict)

    # Backward compatibility: flat section list (legacy format)
    sections: list[SectionUpdate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON/YAML serialization."""
        result: dict[str, Any] = {
            "frontmatter": self.frontmatter,
            "frontmatter_policy": (
                self.frontmatter_policy.value
                if isinstance(self.frontmatter_policy, UpdatePolicy)
                else self.frontmatter_policy
            ),
        }

        if self.content:
            result["content"] = self.content

        if self.sections:
            # Convert SectionUpdate dataclasses to dicts
            result["sections"] = [
                section.to_dict() if hasattr(section, "to_dict") else section
                for section in self.sections
            ]

        if self.parameters:
            result["parameters"] = self.parameters

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarkdownDataUpdate":
        """Create from dictionary (JSON/YAML deserialization)."""
        # Parse policy
        policy_value = data.get("frontmatter_policy", "merge")
        if isinstance(policy_value, str):
            policy = UpdatePolicy[policy_value.upper()]
        else:
            policy = policy_value

        # Parse sections - convert dicts to SectionUpdate dataclasses
        sections_data = data.get("sections", [])
        sections = [
            SectionUpdate.from_dict(section) if isinstance(section, dict) else section
            for section in sections_data
        ]

        return cls(
            frontmatter=data.get("frontmatter", {}),
            content=data.get("content"),
            frontmatter_policy=policy,
            parameters=data.get("parameters", {}),
            sections=sections,
        )

    def is_template(self) -> bool:
        """Check if this update has parameters (is a template)."""
        return bool(self.parameters)

    def has_hierarchical_content(self) -> bool:
        """Check if using new hierarchical content format."""
        return self.content is not None

    def has_flat_sections(self) -> bool:
        """Check if using legacy flat sections format."""
        return bool(self.sections)

    def _extract_heading_from_content(
        self, content: str
    ) -> tuple[str | None, int | None]:
        """Extract heading title and level from markdown content.

        Args:
            content: Raw content that may start with a heading
                (e.g., "# Title\n\nContent")

        Returns:
            Tuple of (title, level) or (None, None) if no heading found
        """
        lines = content.split("\n", 1)
        if not lines:
            return None, None

        first_line = lines[0].strip()
        if not first_line.startswith("#"):
            return None, None

        # Count heading level
        level = 0
        for char in first_line:
            if char == "#":
                level += 1
            else:
                break

        # Extract title (text after the # symbols)
        title = first_line[level:].strip()

        return title, level if 1 <= level <= 6 else None

    def _strip_heading_from_content(self, content: str) -> str:
        """Strip markdown heading from content string.

        Args:
            content: Raw content that may start with a heading
                (e.g., "# Title\n\nContent")

        Returns:
            Content without the heading line
        """
        lines = content.split("\n", 2)  # Split into at most 3 parts
        if not lines:
            return ""

        # Check if first line is a heading
        first_line = lines[0].strip()
        if first_line.startswith("#"):
            # Remove first line and any blank line after it
            if len(lines) > 1:
                # If second line is empty, skip it too
                if len(lines) > 1 and not lines[1].strip():
                    return lines[2] if len(lines) > 2 else ""
                else:
                    return "\n".join(lines[1:])
            return ""

        return content

    def as_markdown_dict(self) -> dict[str, Any]:
        """Convert to MarkdownDataDict format (frontmatter + content only).

        This method extracts just the document data (frontmatter and content),
        discarding update-specific metadata like policies and parameters.
        Useful for creating complete documents from filled templates.

        Returns:
            Dict with 'frontmatter' and 'content' keys (MarkdownDataDict format)
        """
        result: dict[str, Any] = {
            "frontmatter": self.frontmatter,
        }

        # Use hierarchical content if available, otherwise convert sections
        if self.content:
            result["content"] = self.content
        elif self.sections:
            # Convert flat sections to hierarchical content structure
            # Create a root section containing all sections
            children_data = []
            for section in self.sections:
                # Extract title and level from content heading
                # if not explicitly provided
                title = section.title
                level = section.level
                section_id = section.id

                if not title or not level:
                    if section.content:
                        extracted_title, extracted_level = (
                            self._extract_heading_from_content(section.content)
                        )
                        if not title and extracted_title:
                            title = extracted_title
                            # Only regenerate ID if original section
                            # had no explicit ID.
                            # Preserves user-specified IDs while
                            # ensuring consistency when ID is
                            # auto-generated from title
                            if not section.id:
                                from .document import Section

                                temp_section = Section(title, level or 1)
                                section_id = temp_section.id
                        if not level and extracted_level:
                            level = extracted_level

                # Create child section dict following SectionData structure
                child_dict: dict[str, Any] = {
                    "id": section_id,
                    "title": title or section.id.replace("_", " ").title(),
                    "level": level or 1,
                    "path": section.path or section_id,
                    "blocks": section.blocks if section.blocks else [],
                    "children": (
                        [child.to_section_data() for child in section.children]
                        if section.children
                        else []
                    ),
                }

                # If section has raw content string,
                # convert it to a single paragraph block
                if section.content:
                    # Strip heading from content if present
                    # (title/level already in section data)
                    content_without_heading = self._strip_heading_from_content(
                        section.content
                    )

                    # Only create blocks if there's content after stripping heading
                    if content_without_heading.strip():
                        child_dict["blocks"] = [
                            {
                                "section_id": section_id,
                                "type": "paragraph",
                                "content": content_without_heading,
                                "metadata": {},
                            }
                        ]

                children_data.append(child_dict)

            result["content"] = {
                "id": "",
                "title": "",
                "level": 0,
                "path": "",
                "blocks": [],
                "children": children_data,
            }
        else:
            # Empty content
            result["content"] = {
                "id": "",
                "title": "",
                "level": 0,
                "path": "",
                "blocks": [],
                "children": [],
            }

        return result


__all__ = [
    "UpdateInputDict",
    "InputDictSectionContent",
    "InputDictSectionData",
    "InputDictSectionObject",
    "InputDataDictOptions",
    "InputDataOptions",
    "SectionUpdate",
    "BatchOperationResult",
    "MarkdownDataUpdate",
]
