"""Custom Typer argument types using application models."""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from click import Choice

from md_as_data.models import BlockType, HeadingLevel, SectionPolicy


class SectionPolicyChoice(str, Enum):
    """Section policy choices for CLI."""

    REPLACE = "replace"
    UPDATE = "update"
    APPEND = "append"
    R = "r"  # Short form
    U = "u"  # Short form
    A = "a"  # Short form


class BlockTypeChoice(str, Enum):
    """Block type choices for CLI."""

    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"


class HeadingLevelChoice(str, Enum):
    """Heading level choices for CLI."""

    H1 = "1"
    H2 = "2"
    H3 = "3"
    H4 = "4"
    H5 = "5"
    H6 = "6"


class OutputFormatChoice(str, Enum):
    """Output format choices for CLI."""

    JSON = "json"
    YAML = "yaml"


def section_policy_converter(value: str) -> SectionPolicy:
    """Convert CLI input to SectionPolicy enum."""
    policy_map = {
        "replace": SectionPolicy.REPLACE,
        "r": SectionPolicy.REPLACE,
        "update": SectionPolicy.UPDATE,
        "u": SectionPolicy.UPDATE,
        "append": SectionPolicy.APPEND,
        "a": SectionPolicy.APPEND,
    }

    policy_key = value.lower()
    if policy_key not in policy_map:
        valid_options = list(policy_map.keys())
        raise typer.BadParameter(
            f"Invalid policy '{value}'. Valid options: {valid_options}"
        )

    return policy_map[policy_key]


def block_type_converter(value: str) -> BlockType:
    """Convert CLI input to BlockType enum."""
    try:
        return BlockType(value.lower())
    except ValueError:
        valid_options = [bt.value for bt in BlockType]
        raise typer.BadParameter(
            f"Invalid block type '{value}'. Valid options: {valid_options}"
        )


def heading_level_converter(value: str) -> HeadingLevel:
    """Convert CLI input to HeadingLevel enum."""
    try:
        level_int = int(value)
        return HeadingLevel(level_int)
    except (ValueError, TypeError):
        valid_options = [
            str(hl.value) for hl in HeadingLevel if hl != HeadingLevel.ROOT
        ]
        raise typer.BadParameter(
            f"Invalid heading level '{value}'. Valid options: {valid_options}"
        )


# Common reusable argument types
MarkdownFileArg = Annotated[Path, typer.Argument(help="Path to the markdown file")]

OptionalOutputFileArg = Annotated[
    Path | None, typer.Option("--output", "-o", help="Output file (default: stdout)")
]

VerboseFlag = Annotated[
    bool, typer.Option("--verbose", "-v", help="Show verbose output")
]

PrettyFlag = Annotated[bool, typer.Option("--pretty", "-p", help="Pretty-print output")]

# Annotated types for use in CLI commands
SectionPolicyArg = Annotated[
    SectionPolicy,
    typer.Option(
        "--policy",
        "-p",
        help="Section policy: replace (r), append (a), update (u)",
        callback=lambda ctx, param, value: section_policy_converter(value)
        if value
        else SectionPolicy.UPDATE,
    ),
]

BlockTypeArg = Annotated[
    BlockType,
    typer.Option(
        "--type",
        "-t",
        help="Block type filter",
        callback=lambda ctx, param, value: block_type_converter(value)
        if value
        else None,
    ),
]

HeadingLevelArg = Annotated[
    HeadingLevel,
    typer.Option(
        "--level",
        "-l",
        help="Heading level (1-6)",
        callback=lambda ctx, param, value: heading_level_converter(value)
        if value
        else None,
    ),
]

OutputFormatArg = Annotated[
    str,
    typer.Option(
        "--format",
        "-f",
        help="Output format",
        click_type=Choice(["json", "yaml"], case_sensitive=False),
    ),
]
