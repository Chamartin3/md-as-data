"""File loading and orchestration for markdown parsing and serialization."""

import json
from datetime import date, datetime
from pathlib import Path

from .data import MarkdownData
from .models import (
    ContentTree,
    MarkdownDataDict,
    ParsedMarkdownData,
    Section,
)
from .models.schema import DocumentSchema
from .processor import MarkdownProcessor


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles date and datetime objects."""

    def default(self, o):
        """Convert date/datetime objects to ISO format strings."""
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


class MarkdownFile:
    """Manage read (parsing) and write (serializing) on a markdown file."""

    mddata: MarkdownData
    _processor = MarkdownProcessor()

    def __init__(self, filepath: str, raw_content: str | None = None):
        """Initialize MarkdownFile.

        Args:
            filepath: Path to the markdown file
            raw_content: Optional raw markdown content (loads from file if None)
        """
        self.filepath = Path(filepath)

        if raw_content is not None:
            # Use provided content (for from_dict use case)
            self._raw_content = raw_content
        else:
            # Load from file
            self._raw_content = self._load()

        # Parse the document
        parsed_data = self._processor.parse(self._raw_content)
        self.mddata = MarkdownData(parsed_data)

    def _load(self) -> str:
        """Load raw markdown content from file."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")

        if not self.filepath.is_file():
            raise ValueError(f"Path is not a file: {self.filepath}")

        return self.filepath.read_text(encoding="utf-8")

    # Serialization methods
    def to_json(self) -> str:
        """Serialize document to JSON string."""
        return json.dumps(self.mddata.to_dict(), indent=2, cls=DateTimeEncoder)

    def to_markdown(self) -> str:
        """Serialize document back to markdown string."""
        return self._processor.serialize_document(self.mddata.to_dict())

    def save(self, filepath: str | None = None) -> None:
        """Save the document back to markdown file.

        Args:
            filepath: Optional path to save to. If None, saves to original file path.
        """
        target_path = Path(filepath) if filepath else self.filepath
        markdown_content = self.to_markdown()
        target_path.write_text(markdown_content, encoding="utf-8")

    def save_as(self, filepath: str) -> None:
        """Save the document to a new file path."""
        self.save(filepath)

    @staticmethod
    def _normalize_section_data(section_data: dict) -> dict:
        """Normalize simplified section format to full SectionData format.

        Args:
            section_data: Section dict that may be in simplified format

        Returns:
            Normalized section dict with all required fields
        """
        # If already has all required fields, return as-is
        if all(k in section_data for k in ["id", "title", "level", "path"]):
            return section_data

        # Build normalized dict with required fields
        normalized = dict(section_data)

        # Generate title from id if missing
        if "title" not in normalized and "id" in normalized:
            normalized["title"] = normalized["id"].replace("_", " ").title()

        # Default level to 1 if missing
        if "level" not in normalized:
            normalized["level"] = 1

        # Generate path from id if missing
        if "path" not in normalized and "id" in normalized:
            normalized["path"] = normalized["id"]

        # Convert 'content' field to blocks if present
        if "content" in normalized and "blocks" not in normalized:
            content = normalized.pop("content")
            if content:
                # Create a paragraph block from the content string
                normalized["blocks"] = [
                    {
                        "type": "paragraph",
                        "content": content,
                        "section_id": normalized["id"],
                    }
                ]
            else:
                normalized["blocks"] = []

        # Ensure blocks and children exist
        if "blocks" not in normalized:
            normalized["blocks"] = []
        if "children" not in normalized:
            normalized["children"] = []

        return normalized

    @classmethod
    def from_dict(
        cls,
        data: MarkdownDataDict,
        filepath: str | None = None,
        schema: "DocumentSchema | None" = None,
    ) -> "MarkdownFile":
        """Create MarkdownFile from JSON-serializable dictionary.

        This is the inverse of MarkdownFile.to_json() / MarkdownData.to_dict().
        Allows creating markdown documents programmatically from structured data.

        Args:
            data: MarkdownDataDict with frontmatter and content (SectionData)
            filepath: Optional file path for the document (defaults to "untitled.md")
            schema: Optional schema for validation

        Returns:
            MarkdownFile instance ready to be saved or further manipulated

        Example:
            >>> data = {
            ...     "frontmatter": {"title": "Example", "author": "User"},
            ...     "content": {
            ...         "id": "",
            ...         "title": "",
            ...         "level": 0,
            ...         "path": "",
            ...         "blocks": None,
            ...         "children": [...]
            ...     }
            ... }
            >>> doc = MarkdownFile.from_dict(data, "document.md")
            >>> doc.save()
        """
        # 1. Reconstruct ContentTree from SectionData
        content_tree = ContentTree()

        # Handle both new content format and legacy sections format
        if "content" in data:
            root_data = data["content"]
            # 2. Recursively build sections from SectionData
            children = root_data.get("children")
            if children:
                for subsection_data in children:
                    section = Section.from_dict(subsection_data)
                    content_tree.add_section(section)
        elif "sections" in data:
            # Legacy format: flat sections list
            for section_data in data.get("sections", []):
                if isinstance(section_data, dict):
                    # Normalize simplified section format
                    normalized = cls._normalize_section_data(section_data)
                    section = Section.from_dict(normalized)
                    content_tree.add_section(section)

        # 3. Create ParsedMarkdownData
        parsed_data: ParsedMarkdownData = {
            "frontmatter": data["frontmatter"],
            "content": content_tree,
        }

        # 4. Create MarkdownData directly from parsed structures (preserves custom IDs)
        from .data import MarkdownData

        mddata = MarkdownData(parsed_data, schema=schema)

        # 5. Serialize to markdown text for _raw_content
        processor = MarkdownProcessor()
        markdown_text = processor.serialize_parsed_data(parsed_data)

        # 6. Create MarkdownFile instance directly (bypass __init__ to avoid re-parsing)
        target_path = filepath if filepath else "untitled.md"
        md_file = object.__new__(cls)
        md_file.filepath = Path(target_path)
        md_file._raw_content = markdown_text
        md_file.mddata = mddata

        return md_file

    @classmethod
    def create_from_schema(
        cls, schema: DocumentSchema, filepath: str, overwrite: bool = False
    ) -> "MarkdownFile":
        """
        Create a new markdown file from a schema template.

        This method uses the standard workflow:
        Schema -> MarkdownDataDict -> MarkdownFile

        Args:
            schema: DocumentSchema typed dictionary defining document structure
            filepath: Path where file will be created
            overwrite: Whether to overwrite existing file

        Returns:
            MarkdownFile instance with template content

        Raises:
            FileExistsError: If file exists and overwrite=False

        Example:
            >>> from mddata.schema import load_schema
            >>> schema = load_schema('schema.yaml')
            >>> doc = MarkdownFile.create_from_schema(
            ...     schema,
            ...     'new_document.md'
            ... )
            >>> doc.mddata.title = "New Document"
            >>> doc.save()
        """
        from .schema import schema_to_markdown_dict

        # Check file existence
        path = Path(filepath)
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}")

        # Convert schema to MarkdownDataDict
        data_dict = schema_to_markdown_dict(schema)

        # Use standard from_dict workflow
        instance = cls.from_dict(data_dict, filepath=filepath, schema=schema)

        # Save immediately
        instance.save()

        return instance
