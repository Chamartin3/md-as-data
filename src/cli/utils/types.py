"""Custom Typer argument types using application models."""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from mddata.models import BlockType, HeadingLevel, UpdatePolicy


class OutputFormatChoice(str, Enum):
    """Output format choices for CLI."""

    JSON = "json"
    YAML = "yaml"


def section_policy_converter(value: str) -> UpdatePolicy:
    """Convert CLI input to UpdatePolicy enum, supporting shorthand aliases."""
    # Map shorthand to full enum values
    shorthand_map = {
        "r": UpdatePolicy.REPLACE,
        "u": UpdatePolicy.UPDATE,
        "a": UpdatePolicy.APPEND,
    }

    # Check if value is shorthand
    if value.lower() in shorthand_map:
        return shorthand_map[value.lower()]

    # Try to convert to enum directly
    try:
        return UpdatePolicy(value.lower())
    except ValueError:
        valid_options = [p.value for p in UpdatePolicy] + list(shorthand_map.keys())
        raise typer.BadParameter(
            f"Invalid policy '{value}'. Valid options: {valid_options}"
        )


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
    UpdatePolicy,
    typer.Option(
        "--policy",
        "-p",
        help="Section policy: replace (r), append (a), update (u)",
        callback=lambda ctx, param, value: section_policy_converter(value)
        if value
        else UpdatePolicy.UPDATE,
    ),
]

BlockTypeArg = Annotated[
    BlockType | None,
    typer.Option(
        "--type",
        "-t",
        help="Block type filter",
    ),
]

HeadingLevelArg = Annotated[
    HeadingLevel | None,
    typer.Option(
        "--level",
        "-l",
        help="Heading level (1-6)",
    ),
]

OutputFormatArg = Annotated[
    OutputFormatChoice,
    typer.Option(
        "--format",
        "-f",
        help="Output format (json or yaml)",
    ),
]
