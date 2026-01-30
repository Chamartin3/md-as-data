"""Markdown processing functionality for parsing and serialization."""

import re
from collections.abc import Callable
from enum import StrEnum
from typing import Any, cast

import frontmatter as fm
import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token

from .models import (
    Block,
    BlockType,
    ContentTree,
    HeadingLevel,
    MarkdownDataDict,
    ParsedMarkdownData,
    Section,
    TaskItemData,
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


class MarkdownProcessor:
    """Handles all markdown transformations."""

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

    # Parsing methods
    def parse(self, text: str) -> ParsedMarkdownData:
        """Parse full markdown document and return structured data."""
        # Use python-frontmatter to extract metadata
        post = fm.loads(text)
        frontmatter_dict = post.metadata
        body = post.content

        # Use markdown-it-py to parse content structure
        tokens = self.md.parse(body)
        content_tree = self._build_content_tree(tokens)

        return cast(
            "ParsedMarkdownData",
            {
                "frontmatter": frontmatter_dict,
                "content": content_tree,
            },
        )

    def parse_content_to_section(self, text: str, section_path: str) -> Section:
        """Parse markdown text into single section."""
        # Wrap content in temporary section for proper parsing

        section_id = section_path.split(".")[-1]
        parent_path = ".".join(section_path.split(".")[:-1])
        level = parent_path.count(".") + 1 if parent_path else 1

        title = section_id.replace("_", " ").title()
        is_empty = not text or not text.strip()

        if is_empty:
            raise ValueError("Content cannot be empty or whitespace only")

        # Fallback for simple text without markdown headings
        not_markdown = "#" not in text and "\n" not in text
        if not_markdown:
            block = Block(section_id, BlockType.PARAGRAPH, text.strip())
            section = Section(title, HeadingLevel(level), parent_path)
            section.id = section_id
            section.add_block(block)

        # Check if text already starts with a heading
        text_stripped = text.lstrip()
        already_has_heading = text_stripped.startswith("#")

        if already_has_heading:
            # Text already has heading, use it directly
            temp_markdown = text
        else:
            # Add heading to the text
            mdtitle = f"{'#' * level} {title}\n\n"
            temp_markdown = f"{mdtitle}{text}"

        parsed_data = self.parse(temp_markdown)
        content_tree = parsed_data["content"]
        if not content_tree or not content_tree.get_all_sections():
            raise ValueError(f"Failed to parse content into sections:{text}")
        first_section = content_tree.get_all_sections()[0]
        section = Section(first_section.title, first_section.level, parent_path)
        section.id = section_id
        section.blocks = first_section.blocks
        # Update block section references
        for block in section.blocks:
            block.section = section_id
        return section

    def parse_content_to_tree(self, text: str) -> ContentTree:
        """Parse content into tree structure."""
        # Use markdown-it-py to parse content structure
        tokens = self.md.parse(text)
        return self._build_content_tree(tokens)

    # Serialization methods
    def serialize_document(self, data: MarkdownDataDict) -> str:
        """Serialize MarkdownData to markdown."""
        return self._serialize_markdown_data(data)

    def serialize_parsed_data(self, data: ParsedMarkdownData) -> str:
        """Serialize ParsedMarkdownData to markdown."""
        markdown_data_dict = cast(
            MarkdownDataDict,
            {"frontmatter": data["frontmatter"], "content": data["content"].to_dict()},
        )
        return self._serialize_markdown_data(markdown_data_dict)

    def _serialize_markdown_data(self, data: MarkdownDataDict) -> str:
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
        if section_data.get("children"):
            for subsection_data in section_data["children"]:
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
        elif block_type == "task_list":
            if isinstance(content, list) and "tasks" in metadata:
                items = []
                tasks_data = metadata["tasks"]
                if isinstance(tasks_data, list):
                    for i, task_content in enumerate(content):
                        if i < len(tasks_data):
                            task_item = tasks_data[i]
                            if isinstance(task_item, dict):
                                symbol = task_item.get("symbol", " ")
                            else:
                                symbol = " "
                            items.append(f"- [{symbol}] {task_content}")
                        else:
                            items.append(f"- [ ] {task_content}")
                    return "\n".join(items)
            # Fallback for malformed task list
            if isinstance(content, list):
                return "\n".join(f"- [ ] {item}" for item in content)
            else:
                return f"- [ ] {content}"
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

    def _parse_task_item(self, item_text: str) -> TaskItemData | None:
        """Parse task list item checkbox syntax.

        Matches patterns like:
        - [x] Completed task
        - [ ] Pending task
        - [!] Priority task
        - [~] In-progress task
        - [?] Blocked task
        - [P] Custom status

        Args:
            item_text: The list item text to parse

        Returns:
            TaskItemData with content and symbol if pattern matches,
            None otherwise
        """
        # Match pattern: optional whitespace, [char], space, content
        pattern = r"^\s*\[(.?)\]\s+(.*)"
        match = re.match(pattern, item_text.strip())

        if not match:
            return None

        symbol = match.group(1)
        content = match.group(2)

        return {"content": content, "symbol": symbol}

    def _handle_bullet_list(self, token: Token, state: dict) -> int:
        """Handle bullet list tokens, detecting task lists."""
        tokens = state["tokens"]
        i = state["index"]

        list_items = []
        task_items = []
        j = i + 1

        # Extract list items and check for task patterns
        while j < len(tokens) and tokens[j].type != TokenType.BULLET_LIST_CLOSE:
            if tokens[j].type == TokenType.LIST_ITEM_OPEN:
                # Find the content in this list item
                k = j + 1
                while k < len(tokens) and tokens[k].type != TokenType.LIST_ITEM_CLOSE:
                    if tokens[k].type == TokenType.INLINE:
                        item_content = tokens[k].content
                        task_data = self._parse_task_item(item_content)

                        if task_data:
                            task_items.append(task_data)
                        else:
                            list_items.append(item_content)
                        break
                    k += 1
            j += 1

        # Create appropriate block type
        if task_items and not list_items:
            # Pure task list
            block = Block(
                state["current_section"].id,
                BlockType.TASK_LIST,
                [t["content"] for t in task_items],
            )
            block.metadata["tasks"] = task_items  # type: ignore
            state["current_section"].add_block(block)
        elif list_items or task_items:
            # Regular list or mixed list (treat mixed as regular)
            all_items = [t["content"] for t in task_items] + list_items
            block = Block(state["current_section"].id, BlockType.LIST, all_items)
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

    def register_handler(self, token_type: TokenType, handler: Callable) -> None:
        """Register a new token handler or override an existing one."""
        self.token_handlers[token_type] = handler

    def unregister_handler(self, token_type: TokenType) -> None:
        """Remove a token handler."""
        self.token_handlers.pop(token_type, None)

    @staticmethod
    def format_content_with_heading(
        content: str,
        level: int,
        title: str,
        preserve_existing_heading: bool = True,
    ) -> str:
        """Format content with appropriate heading level.

        Args:
            content: Content text (may or may not include heading)
            level: Heading level (1-6)
            title: Section title to use
            preserve_existing_heading: If True, don't add heading if
                content starts with one

        Returns:
            Formatted content with heading
        """
        stripped_content = content.strip()
        if preserve_existing_heading and stripped_content.startswith("#"):
            return content

        heading_marker = "#" * level
        formatted = f"{heading_marker} {title}\n\n{stripped_content}"
        return formatted

    @staticmethod
    def preserve_section_structure(content: str, existing_section: Section) -> str:
        """Preserve section structure when updating content.

        Ensures that content maintains the correct heading level
        and title from the existing section.

        Args:
            content: New content to add
            existing_section: Existing section to preserve structure from

        Returns:
            Content with preserved section heading structure
        """
        return MarkdownProcessor.format_content_with_heading(
            content=content,
            level=existing_section.level,
            title=existing_section.title,
            preserve_existing_heading=True,
        )

    @staticmethod
    def content_has_heading(content: str) -> bool:
        """Check if content string starts with a markdown heading.

        Args:
            content: Content to check

        Returns:
            True if content starts with heading marker (#)
        """
        return content.strip().startswith("#")
