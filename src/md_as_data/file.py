"""File loading and orchestration for markdown parsing and serialization."""

import json
import re
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any

import frontmatter
import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token

from .models import (
    Block,
    BlockType,
    ContentTree,
    HeadingLevel,
    MarkdownData,
    MarkdownDataDict,
    ParsedMarkdownData,
    Section,
)


class TokenType(StrEnum):
    """Token types from markdown-it parser."""

    # Block structure tokens
    HEADING_OPEN = "heading_open"
    HEADING_CLOSE = "heading_close"
    PARAGRAPH_OPEN = "paragraph_open"
    PARAGRAPH_CLOSE = "paragraph_close"

    # List tokens
    BULLET_LIST_OPEN = "bullet_list_open"
    BULLET_LIST_CLOSE = "bullet_list_close"
    ORDERED_LIST_OPEN = "ordered_list_open"
    ORDERED_LIST_CLOSE = "ordered_list_close"
    LIST_ITEM_OPEN = "list_item_open"
    LIST_ITEM_CLOSE = "list_item_close"

    # Code tokens
    FENCE = "fence"
    CODE_BLOCK = "code_block"
    CODE_INLINE = "code_inline"

    # Quote tokens
    BLOCKQUOTE_OPEN = "blockquote_open"
    BLOCKQUOTE_CLOSE = "blockquote_close"

    # Table tokens
    TABLE_OPEN = "table_open"
    TABLE_CLOSE = "table_close"
    THEAD_OPEN = "thead_open"
    THEAD_CLOSE = "thead_close"
    TBODY_OPEN = "tbody_open"
    TBODY_CLOSE = "tbody_close"
    TR_OPEN = "tr_open"
    TR_CLOSE = "tr_close"
    TH_OPEN = "th_open"
    TH_CLOSE = "th_close"
    TD_OPEN = "td_open"
    TD_CLOSE = "td_close"

    # Inline tokens
    INLINE = "inline"
    TEXT = "text"
    EM_OPEN = "em_open"
    EM_CLOSE = "em_close"
    STRONG_OPEN = "strong_open"
    STRONG_CLOSE = "strong_close"
    LINK_OPEN = "link_open"
    LINK_CLOSE = "link_close"
    IMAGE = "image"

    # Other tokens
    HR = "hr"
    SOFTBREAK = "softbreak"
    HARDBREAK = "hardbreak"
    HTML_BLOCK = "html_block"
    HTML_INLINE = "html_inline"


class TokenNesting(StrEnum):
    """Token nesting values."""

    OPENING = "1"
    CLOSING = "-1"
    SELF_CLOSING = "0"


class HeadingTag(StrEnum):
    """HTML heading tags."""

    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"


class MarkdownParser:
    """Parse markdown into MarkdownDocument."""

    def __init__(self):
        self.md = MarkdownIt("commonmark")
        # Map token types to their handler methods
        self.token_handlers: dict[TokenType, Callable] = {
            TokenType.HEADING_OPEN: self._handle_heading,
            TokenType.PARAGRAPH_OPEN: self._handle_paragraph,
            TokenType.BULLET_LIST_OPEN: self._handle_bullet_list,
            TokenType.ORDERED_LIST_OPEN: self._handle_ordered_list,
            TokenType.FENCE: self._handle_fence_code,
            TokenType.BLOCKQUOTE_OPEN: self._handle_blockquote,
        }

    def parse(self, content: str) -> ParsedMarkdownData:
        """Parse markdown content into MarkdownDocument."""
        # Use python-frontmatter to extract metadata
        post = frontmatter.loads(content)
        frontmatter_dict = post.metadata
        body = post.content

        # Use markdown-it-py to parse content structure
        tokens = self.md.parse(body)
        content_tree = self._build_content_tree(tokens)

        return ParsedMarkdownData(
            frontmatter=frontmatter_dict,
            content=content_tree,
        )

    def _build_content_tree(self, tokens: list[Token]) -> ContentTree:
        """Build content tree from markdown-it tokens."""
        content_tree = ContentTree()

        # Parser state
        state = {
            "current_section": content_tree.root,
            "section_stack": [content_tree.root],
            "content_tree": content_tree,
            "tokens": tokens,
            "index": 0,
        }

        # Process tokens
        while state["index"] < len(tokens):
            token = tokens[state["index"]]

            # Get handler for this token type
            handler = self.token_handlers.get(token.type)

            if handler:
                # Call the appropriate handler
                advance = handler(token, state)
                state["index"] += advance
            else:
                # No handler for this token type, skip it
                state["index"] += 1

        return content_tree

    def _handle_heading(self, token: Token, state: dict) -> int:
        """Handle heading tokens to create sections."""
        tokens = state["tokens"]
        i = state["index"]

        # Get heading level
        level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
        heading_level = HeadingLevel(level)

        # Get heading text from next token
        title = "Untitled"
        if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.INLINE:
            title = tokens[i + 1].content

        # Find appropriate parent based on level
        section_stack = state["section_stack"]
        while len(section_stack) > 1 and section_stack[-1].level >= level:
            section_stack.pop()

        parent_section = section_stack[-1]
        parent_path = (
            None
            if parent_section == state["content_tree"].root
            else parent_section.path
        )

        # Create new section with correct parent_path
        section = Section(title, heading_level, parent_path)

        # Add to content tree
        if parent_section == state["content_tree"].root:
            state["content_tree"].add_section(section)
        else:
            state["content_tree"].add_section(section, parent_section.path)

        section_stack.append(section)
        state["current_section"] = section

        # Skip heading_open, inline, and heading_close tokens
        return 3

    def _handle_paragraph(self, token: Token, state: dict) -> int:
        """Handle paragraph tokens."""
        tokens = state["tokens"]
        i = state["index"]

        # Get paragraph content from next token
        if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.INLINE:
            content = tokens[i + 1].content
            block = Block(state["current_section"].id, BlockType.PARAGRAPH, content)
            state["current_section"].add_block(block)

        # Skip paragraph_open, inline, and paragraph_close tokens
        return 3

    def _handle_bullet_list(self, token: Token, state: dict) -> int:
        """Handle bullet list tokens."""
        tokens = state["tokens"]
        i = state["index"]

        list_items = []
        j = i + 1

        while j < len(tokens) and tokens[j].type != TokenType.BULLET_LIST_CLOSE:
            if tokens[j].type == TokenType.LIST_ITEM_OPEN:
                # Find the content in this list item
                k = j + 1
                while k < len(tokens) and tokens[k].type != TokenType.LIST_ITEM_CLOSE:
                    if tokens[k].type == TokenType.INLINE:
                        list_items.append(tokens[k].content)
                        break
                    k += 1
            j += 1

        if list_items:
            block = Block(state["current_section"].id, BlockType.LIST, list_items)
            state["current_section"].add_block(block)

        # Return how many tokens to skip
        return j - i + 1

    def _handle_ordered_list(self, token: Token, state: dict) -> int:
        """Handle ordered list tokens."""
        tokens = state["tokens"]
        i = state["index"]

        list_items = []
        j = i + 1

        while j < len(tokens) and tokens[j].type != TokenType.ORDERED_LIST_CLOSE:
            if tokens[j].type == TokenType.LIST_ITEM_OPEN:
                # Find the content in this list item
                k = j + 1
                while k < len(tokens) and tokens[k].type != TokenType.LIST_ITEM_CLOSE:
                    if tokens[k].type == TokenType.INLINE:
                        list_items.append(tokens[k].content)
                        break
                    k += 1
            j += 1

        if list_items:
            block = Block(
                state["current_section"].id, BlockType.ORDERED_LIST, list_items
            )
            state["current_section"].add_block(block)

        # Return how many tokens to skip
        return j - i + 1

    def _handle_fence_code(self, token: Token, state: dict) -> int:
        """Handle fenced code block tokens."""
        content = token.content
        block = Block(state["current_section"].id, BlockType.CODE_BLOCK, content)

        # Add language metadata if present
        if token.info:
            block.metadata["language"] = token.info

        state["current_section"].add_block(block)

        # Fence token is self-contained
        return 1

    def _handle_blockquote(self, token: Token, state: dict) -> int:
        """Handle blockquote tokens."""
        tokens = state["tokens"]
        i = state["index"]

        quote_content = []
        j = i + 1

        while j < len(tokens) and tokens[j].type != TokenType.BLOCKQUOTE_CLOSE:
            if tokens[j].type == TokenType.INLINE:
                quote_content.append(tokens[j].content)
            j += 1

        if quote_content:
            block = Block(
                state["current_section"].id,
                BlockType.BLOCKQUOTE,
                " ".join(quote_content),
            )
            state["current_section"].add_block(block)

        # Return how many tokens to skip
        return j - i + 1

    def _extract_links_and_images(self, content: str) -> list[Block]:
        """Extract links and images from inline content."""
        blocks = []

        # Simple regex patterns for links and images
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

        # Find images first (they start with !)
        for match in re.finditer(image_pattern, content):
            alt_text = match.group(1)
            src = match.group(2)
            block = Block(
                "", BlockType.IMAGE, alt_text
            )  # No section_id for extracted links/images
            block.metadata["src"] = src
            block.metadata["alt"] = alt_text
            blocks.append(block)

        # Find links
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            href = match.group(2)
            # Skip if this is actually an image
            if not content[max(0, match.start() - 1) : match.start()] == "!":
                block = Block(
                    "", BlockType.LINK, text
                )  # No section_id for extracted links/images
                block.metadata["href"] = href
                blocks.append(block)

        return blocks

    def register_handler(self, token_type: TokenType, handler: Callable) -> None:
        """Register a new token handler or override an existing one."""
        self.token_handlers[token_type] = handler

    def unregister_handler(self, token_type: TokenType) -> None:
        """Remove a token handler."""
        self.token_handlers.pop(token_type, None)


class MarkdownSerializer:
    """Convert MarkdownDocument back to markdown text."""

    def serialize(self, data: MarkdownDataDict) -> str:
        """Serialize complete document to markdown string."""
        frontmatter = data["frontmatter"]
        content = data["content"]
        parts = []

        # Serialize frontmatter
        frontmatter_str = self._serialize_frontmatter(frontmatter)
        if frontmatter_str:
            parts.append(frontmatter_str)

        # Serialize content
        content_str = self._serialize_content(content)
        if content_str:
            parts.append(content_str)

        return "\n".join(parts)

    def _serialize_frontmatter(self, frontmatter: dict[str, Any]) -> str:
        """Convert frontmatter to YAML format."""
        if not frontmatter:
            return ""

        yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_content}---"

    def _serialize_content(self, content_data) -> str:
        """Convert content data to markdown."""
        # content_data is a SectionData, reconstruct the text
        return self._section_data_to_text(content_data)

    def _section_data_to_text(self, section_data: dict) -> str:
        """Convert SectionData dict to markdown text."""
        lines = []

        # Add heading if not root
        if section_data.get("level", 0) > 0:
            heading_marker = "#" * section_data["level"]
            lines.append(f"{heading_marker} {section_data['title']}")
            lines.append("")  # Empty line after heading

        # Add blocks
        if section_data.get("blocks"):
            for block_data in section_data["blocks"]:
                block_text = self._block_data_to_text(block_data)
                if block_text:
                    lines.append(block_text)
                    lines.append("")  # Empty line after block

        # Add subsections
        if section_data.get("subsections"):
            for subsection_data in section_data["subsections"]:
                subsection_text = self._section_data_to_text(subsection_data)
                if subsection_text:
                    lines.append(subsection_text)

        # Clean up trailing empty lines
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def _block_data_to_text(self, block_data: dict) -> str:
        """Convert BlockData dict to markdown text."""
        block_type = block_data["type"]
        content = block_data["content"]
        metadata = block_data.get("metadata", {})

        if block_type == "paragraph":
            return str(content)
        elif block_type == "code_block":
            language = metadata.get("language", "")
            return f"```{language}\n{content}\n```"
        elif block_type == "list":
            if isinstance(content, list):
                return "\n".join(f"- {item}" for item in content)
            else:
                return f"- {content}"
        elif block_type == "ordered_list":
            if isinstance(content, list):
                return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(content))
            else:
                return f"1. {content}"
        elif block_type == "blockquote":
            content_str = str(content)
            lines = content_str.split("\n")
            return "\n".join(f"> {line}" for line in lines)
        elif block_type == "link":
            href = metadata.get("href", "#")
            title = metadata.get("title", "")
            title_attr = f' "{title}"' if title else ""
            return f"[{content}]({href}{title_attr})"
        elif block_type == "image":
            src = metadata.get("src", "")
            alt = metadata.get("alt", str(content))
            title = metadata.get("title", "")
            title_attr = f' "{title}"' if title else ""
            return f"![{alt}]({src}{title_attr})"
        else:
            return str(content)


class MarkdownFile:
    """Manage read (parsing) and write (serializing) on a markdown file."""

    mddata: MarkdownData

    def register_handler(self, token_type: TokenType, handler: Callable) -> None:
        """Register a new token handler or override an existing one."""
        self._parser.register_handler(token_type, handler)

    def unregister_handler(self, token_type: TokenType) -> None:
        """Remove a token handler."""
        self._parser.unregister_handler(token_type)

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._raw_content = self._load()

        # Initialize parser and serializer instances
        self._parser = MarkdownParser()
        self._serializer = MarkdownSerializer()

        # Parse the document
        data = self._parser.parse(self._raw_content)
        self.mddata = MarkdownData(data)

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
        return self._serializer.serialize(self.mddata.to_dict())

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
