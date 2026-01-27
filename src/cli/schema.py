"""Schema subcommands for generation and validation operations."""

import json
from pathlib import Path
from typing import Annotated

import typer

from mddata.models.schemas import (
    CURRENT_SCHEMA_VERSION,
    SchemaFieldNames,
)
from mddata.schema import SchemaInferenceMode, generate_schema

from .utils import MarkdownPrinter, cli_context
from .utils.types import OutputFormatChoice

app = typer.Typer(
    name="schema",
    help="Schema generation and validation commands",
    no_args_is_help=True,
)

FilePathArg = Annotated[
    Path, typer.Argument(help="Path to the markdown file or folder")
]


def _load_schema_file(schema_file: Path) -> dict:
    """Load schema from JSON or YAML file with automatic format detection.

    Detection strategy:
    1. Check file extension (.yaml/.yml vs .json)
    2. Try format-specific parser based on extension
    3. Fall back to alternate format if parsing fails

    Args:
        schema_file: Path to schema file

    Returns:
        Loaded schema as dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        Exception: If file cannot be parsed as JSON or YAML
    """
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    content = schema_file.read_text()
    suffix = schema_file.suffix.lower()

    # Try extension-based detection first
    if suffix in [".yaml", ".yml"]:
        try:
            import yaml

            return yaml.safe_load(content)
        except ImportError:
            # Fall back to JSON if YAML not available
            pass
        except Exception as e:
            raise Exception(f"Invalid YAML schema format: {e}")

    # Try JSON parsing (default for .json or unknown extensions)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # Try YAML as fallback
        try:
            import yaml

            return yaml.safe_load(content)
        except ImportError:
            raise Exception(
                f"Invalid JSON format and PyYAML not installed. JSON error: {e}"
            )
        except Exception as yaml_error:
            raise Exception(
                f"Invalid schema format. JSON error: {e}. YAML error: {yaml_error}"
            )


@app.command("generate")
def generate_schema_command(
    file_path: FilePathArg,
    inference_mode: Annotated[
        str,
        typer.Option(
            "--inference-mode",
            "-m",
            help="Schema inference mode: strict or permissive",
        ),
    ] = "permissive",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file for generated schema"),
    ] = None,
    format_type: Annotated[
        OutputFormatChoice,
        typer.Option(
            "--format",
            "-f",
            help="Output format: json or yaml",
        ),
    ] = OutputFormatChoice.JSON,
    pretty: Annotated[
        bool,
        typer.Option("--pretty/--compact", help="Pretty-print JSON output"),
    ] = True,
) -> None:
    """Generate schema from single document or folder of documents.

    Automatically detects if the input is a file or folder:
    - Single file: mdasdata document.md schema generate
    - Folder: mdasdata ./docs/ schema generate (recursively finds all *.md files)

    For folders with multiple documents, generates a merged schema by:
    - Marking properties as required if present in ≥75% of documents
    - Creating enum types for single-word string properties
    - Using union types for properties with conflicting types
    - Merging all section hierarchies

    Output format can be JSON (default) or YAML, specified via --format parameter.

    Examples:
        Single file:
        $ mdasdata document.md schema generate --pretty

        Folder:
        $ mdasdata ./documentation/ schema generate --output schema.json

        YAML format:
        $ mdasdata ./docs/ schema generate --format yaml --output schema.yaml

        Strict inference:
        $ mdasdata ./docs/ schema generate --inference-mode strict
    """
    from mddata import MarkdownFile

    printer = MarkdownPrinter(cli_context.console)

    try:
        # Validate inference mode
        try:
            mode = SchemaInferenceMode(inference_mode)
        except ValueError:
            printer.print_error(
                f"Invalid inference mode '{inference_mode}'. "
                f"Use 'strict' or 'permissive'."
            )
            raise typer.Exit(1)

        # Collect all file paths
        all_file_paths: list[Path] = []

        # Check the primary path from argument
        if not file_path.exists():
            printer.print_error(f"Path '{file_path}' does not exist")
            raise typer.Exit(1)

        if file_path.is_file():
            # Single file
            if file_path.suffix == ".md":
                all_file_paths.append(file_path)
        elif file_path.is_dir():
            # Folder - recursively find all markdown files
            md_files = sorted(file_path.rglob("*.md"))
            if not md_files:
                printer.print_warning(f"No markdown files found in {file_path}")
            all_file_paths.extend(md_files)

        if not all_file_paths:
            printer.print_error("No markdown files to process")
            raise typer.Exit(1)

        # Load all documents
        documents = []
        for file_path in all_file_paths:
            try:
                md_file = MarkdownFile(str(file_path))
                documents.append(md_file.mddata.data)
            except Exception as e:
                printer.print_error(f"Failed to load {file_path}: {e}")
                raise typer.Exit(1)

        # Display file count
        file_count = len(documents)
        file_word = "file" if file_count == 1 else "files"
        printer.console.print(
            f"[dim]Schema generated from {file_count} markdown {file_word}[/dim]\n"
        )

        # Generate schema (handles single or multiple documents)
        schema_data = (
            documents if len(documents) > 1 else documents[0] if documents else None
        )
        if schema_data is None:
            printer.print_error("No documents to generate schema from")
            raise typer.Exit(1)

        schema = generate_schema(schema_data, inference_mode=mode)

        # Serialize based on format
        if format_type == OutputFormatChoice.YAML:
            try:
                import yaml

                # Convert enums to strings via JSON serialization first
                json_str = json.dumps(schema, default=str)
                schema_dict = json.loads(json_str)

                output_content = yaml.dump(
                    schema_dict,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            except ImportError:
                printer.print_error("PyYAML not installed. Install with: uv add pyyaml")
                raise typer.Exit(1)
        else:  # JSON
            indent = 2 if pretty else None
            output_content = json.dumps(schema, indent=indent, default=str)

        # Output to file or console
        if output:
            output.write_text(output_content)
            printer.print_success(f"Schema written to {output}")
        else:
            printer.console.print(output_content)

    except typer.Exit:
        raise
    except Exception as e:
        printer.print_error(f"Schema generation failed: {e}")
        raise typer.Exit(1)


@app.command("validate")
def validate_command(
    file_path: FilePathArg,
    schema_file: Annotated[Path, typer.Argument(help="Path to schema file")],
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show detailed validation results")
    ] = False,
    validation_level: Annotated[
        str | None,
        typer.Option(
            "--validation-level",
            "-l",
            help="Validation level: strict, warnings, or disabled. "
            "Overrides schema value.",
        ),
    ] = None,
) -> None:
    """Validate document against a schema file."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load schema using unified loader
        schema_data = _load_schema_file(schema_file)

        # Import here to avoid circular dependency
        from mddata.models.schemas import ValidationLevel
        from mddata.schema import SchemaValidator

        # Parse validation level if provided
        level = None
        if validation_level:
            try:
                level = ValidationLevel(validation_level.lower())
            except ValueError:
                printer.print_error(
                    f"Invalid validation level: {validation_level}. "
                    f"Valid options: strict, warnings, disabled"
                )
                raise typer.Exit(1)

        # Create validator with optional level override
        validator = SchemaValidator(schema_data, validation_level=level)
        result = validator.validate(md_file.mddata)

        # Display results
        if result["valid"]:
            printer.print_success("✓ Document is valid according to schema")
        else:
            printer.print_error("✗ Document validation failed")

            if result["errors"]:
                printer.console.print("\n[bold red]Errors:[/bold red]")
                for error in result["errors"]:
                    printer.console.print(
                        f"  • [{error['field_type']}] {error['field']}: "
                        f"{error['message']}"
                    )

            if result["warnings"] and verbose:
                printer.console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for warning in result["warnings"]:
                    printer.console.print(
                        f"  • [{warning['field_type']}] {warning['field']}: "
                        f"{warning['message']}"
                    )

        # Exit with error code if validation failed
        if not result["valid"]:
            raise typer.Exit(1)

    except FileNotFoundError as e:
        printer.print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        printer.print_error(f"Validation failed: {e}")
        raise typer.Exit(1)


@app.command("info")
def schema_info_command(
    schema_file: Annotated[Path, typer.Argument(help="Path to schema file")],
) -> None:
    """Display information about a schema file."""
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load schema using unified loader
        schema_data = _load_schema_file(schema_file)

        # Display schema information
        printer.console.print(f"[bold]Schema: {schema_file}[/bold]\n")

        # Schema version
        version = schema_data.get(SchemaFieldNames.VERSION, "not specified")
        printer.console.print(f"Schema Version: [cyan]{version}[/cyan]")

        if version == "not specified":
            printer.console.print(
                "[yellow]⚠[/yellow]  Schema missing version field (legacy format)"
            )
        elif version != CURRENT_SCHEMA_VERSION:
            printer.console.print(
                f"[yellow]⚠[/yellow]  Schema version {version} differs from "
                f"current version {CURRENT_SCHEMA_VERSION}"
            )

        printer.console.print(
            "Validation Level: [dim]Not set (use --validation-level CLI option)[/dim]"
        )

        # Frontmatter properties
        if SchemaFieldNames.PROPERTIES in schema_data:
            properties = schema_data[SchemaFieldNames.PROPERTIES]
            printer.console.print(f"\nProperties: [green]{len(properties)}[/green]")
            for prop_name, prop_schema in properties.items():
                required = prop_schema.get("required", False)
                prop_type = prop_schema.get("type", "any")
                req_marker = "[red]*[/red]" if required else " "
                printer.console.print(
                    f"  {req_marker} {prop_name}: [cyan]{prop_type}[/cyan]"
                )

        # Sections
        if SchemaFieldNames.SECTIONS in schema_data:
            sections = schema_data[SchemaFieldNames.SECTIONS]
            printer.console.print(f"\nSections: [green]{len(sections)}[/green]")
            for section_id in sections.keys():
                printer.console.print(f"  • {section_id}")

    except FileNotFoundError as e:
        printer.print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        printer.print_error(f"Failed to read schema: {e}")
        raise typer.Exit(1)
