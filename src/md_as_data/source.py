"""File loading and orchestration for markdown parsing and serialization."""

import json
from pathlib import Path

from .data import MarkdownData
from .processor import MarkdownProcessor


class MarkdownFile:
    """Manage read (parsing) and write (serializing) on a markdown file."""

    mddata: MarkdownData
    _processor = MarkdownProcessor()

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
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
        return json.dumps(self.mddata.to_dict(), indent=2)

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
