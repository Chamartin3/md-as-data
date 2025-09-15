"""Schema subcommands for generation and validation operations."""

import json
from pathlib import Path
from typing import Annotated

import typer

from md_as_data.validation import SchemaInferenceMode, generate_schema

from .utils import MarkdownPrinter, cli_context

app = typer.Typer(
    name="schema",
    help="Schema generation and validation commands",
    no_args_is_help=True,
)


@app.command("generate")
def generate_schema_command(
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
        typer.Option(
            "--output", "-o", help="Output file for generated schema (JSON format)"
        ),
    ] = None,
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

    Examples:
        Single file:
        $ mdasdata document.md schema generate --pretty

        Folder:
        $ mdasdata ./documentation/ schema generate --output schema.json

        Strict inference:
        $ mdasdata ./docs/ schema generate --inference-mode strict
    """
    from md_as_data import MarkdownFile

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

        # Check the primary path from context
        if cli_context.file_path:
            primary_path = cli_context.file_path

            if primary_path.is_file():
                # Single file
                if primary_path.suffix == ".md":
                    all_file_paths.append(primary_path)
            elif primary_path.is_dir():
                # Folder - recursively find all markdown files
                md_files = sorted(primary_path.rglob("*.md"))
                if not md_files:
                    printer.print_warning(f"No markdown files found in {primary_path}")
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

        # Format JSON output
        indent = 2 if pretty else None
        json_output = json.dumps(schema, indent=indent, default=str)

        # Output to file or console
        if output:
            output.write_text(json_output)
            printer.print_success(f"Schema written to {output}")
        else:
            printer.console.print(json_output)

    except typer.Exit:
        raise
    except Exception as e:
        printer.print_error(f"Schema generation failed: {e}")
        raise typer.Exit(1)


@app.command("validate")
def validate_command(
    schema_file: Annotated[
        Path, typer.Argument(help="Path to schema file (JSON format)")
    ],
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show detailed validation results")
    ] = False,
) -> None:
    """Validate document against a schema file."""
    md_file = cli_context.ensure_file_loaded()
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load schema from file
        if not schema_file.exists():
            printer.print_error(f"Schema file not found: {schema_file}")
            raise typer.Exit(1)

        schema_data = json.loads(schema_file.read_text())

        # Import here to avoid circular dependency
        from md_as_data.validation import SchemaValidator

        # Create validator and validate
        validator = SchemaValidator(schema_data)
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

    except json.JSONDecodeError as e:
        printer.print_error(f"Invalid schema JSON: {e}")
        raise typer.Exit(1)
    except Exception as e:
        printer.print_error(f"Validation failed: {e}")
        raise typer.Exit(1)


@app.command("info")
def schema_info_command(
    schema_file: Annotated[
        Path, typer.Argument(help="Path to schema file (JSON format)")
    ],
) -> None:
    """Display information about a schema file."""
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load schema from file
        if not schema_file.exists():
            printer.print_error(f"Schema file not found: {schema_file}")
            raise typer.Exit(1)

        schema_data = json.loads(schema_file.read_text())

        # Display schema information
        printer.console.print(f"[bold]Schema: {schema_file}[/bold]\n")

        # Validation level
        validation_level = schema_data.get("validation_level", "warnings")
        printer.console.print(f"Validation Level: [cyan]{validation_level}[/cyan]")

        # Frontmatter properties
        if "frontmatter" in schema_data:
            frontmatter = schema_data["frontmatter"]
            printer.console.print(
                f"\nFrontmatter Properties: [green]{len(frontmatter)}[/green]"
            )
            for prop_name, prop_schema in frontmatter.items():
                required = prop_schema.get("required", False)
                prop_type = prop_schema.get("type", "any")
                req_marker = "[red]*[/red]" if required else " "
                printer.console.print(
                    f"  {req_marker} {prop_name}: [cyan]{prop_type}[/cyan]"
                )

        # Sections
        if "sections" in schema_data:
            sections = schema_data["sections"]
            printer.console.print(f"\nSections: [green]{len(sections)}[/green]")
            for section_id in sections.keys():
                printer.console.print(f"  • {section_id}")

    except json.JSONDecodeError as e:
        printer.print_error(f"Invalid schema JSON: {e}")
        raise typer.Exit(1)
    except Exception as e:
        printer.print_error(f"Failed to read schema: {e}")
        raise typer.Exit(1)
