# Issue Report: Multi-File Schema Generation

## Issue Description

The current schema generation system (`src/md_as_data/validation/schema_generator.py`) operates on a single markdown document at a time. This limits the ability to create comprehensive schemas that represent patterns across multiple documents in a documentation set or project. The requested feature would enable schema generation from multiple files or an entire folder, with intelligent merging of schemas to identify common patterns, required fields, and type constraints across the document collection.

### Current Behavior

- CLI command: `mdasdata document.md schema generate --output schema.json`
- Python API: `generate_schema(data: ParsedMarkdownData, inference_mode: SchemaInferenceMode) -> DocumentSchema`
- Operates on single `ParsedMarkdownData` instance
- All frontmatter properties found are marked as `required: True` by default
- Section analysis is document-specific

### Requested Behavior

1. **Multiple Input Sources**:
   - Accept one or more file paths: `mdasdata file1.md schema generate` or `mdasdata file1.md file2.md file3.md schema generate`
   - Accept folder path: `mdasdata ./docs/ schema generate`
   - Only process markdown files (*.md)
   - Display count of files used: "Schema generated from 5 markdown files"

2. **Intelligent Schema Merging**:
   - Aggregate frontmatter properties across all documents
   - Mark properties as required based on frequency of appearance (configured in generator)
   - Infer types from actual values across files
   - Calculate min/max constraints from observed values
   - Merge section structures into unified schema

3. **Type and Value Inference**:
   - For single-word string properties appearing consistently, infer as enum type (includes null values)
   - Calculate min/max values from numeric properties across files
   - Calculate min/max length from string properties across files
   - Use union types for type conflicts (e.g., `"str|int"`)

### Design Decisions

1. **Requirement Threshold**: Configured in SchemaGenerator, not as CLI argument
   - Default threshold embedded in generator logic
   - Simple approach without complex configuration

2. **Type Conflict Resolution**: Always use union types
   - Example: `version` is string in file1.md, integer in file2.md → `"str|int"`
   - No error reporting, automatic resolution

3. **Section Structure Conflicts**: Merge all section hierarchies
   - Example: file1.md has "Introduction > Overview", file2.md has "Introduction > Getting Started"
   - Result: Schema contains both subsections

4. **Value Inference for Enums**: Single-word string properties only
   - If property is single word (string) in all files → infer as enum type
   - Include null values in enum types
   - No additional constraints on occurrence count

5. **CLI Compatibility**: Use current API structure
   - Maintain existing `mdasdata <file_path(s)> schema generate` pattern
   - Accept one or multiple paths (files or folders)
   - No new flags or special modes

## Step-by-Step Reproduction

This is a feature request rather than a bug, but here's how to verify current limitations:

### Step 1: Create test documents with shared properties

```bash
cd /home/omidev/Code/tools/makdown_manager/mdasdata/examples
```

Create test files:

**examples/doc1.md**:
```markdown
---
title: Document 1
author: John Doe
status: draft
version: 1
tags: ["python", "docs"]
---
# Introduction
Content here.
```

**examples/doc2.md**:
```markdown
---
title: Document 2
author: Jane Smith
status: published
tags: ["python", "tutorial"]
---
# Introduction
More content.
```

**examples/doc3.md**:
```markdown
---
title: Document 3
status: archived
version: 2
tags: ["python"]
---
# Overview
Different content.
```

### Step 2: Attempt to generate schema from multiple files

```bash
# This should work but currently doesn't support multiple files
uv run mdasdata examples/doc1.md examples/doc2.md examples/doc3.md schema generate
```

**Expected Result**:
- Schema generated from all three markdown files
- Display: "Schema generated from 3 markdown files"
- `title`: required (appears in 3/3 files)
- `author`: not required based on generator's internal threshold
- `status`: enum type with values `["draft", "published", "archived"]` (single-word strings)
- `version`: not required, union type `"int"` (appears in 2/3 files)
- `tags`: required (appears in 3/3 files), type: list
- Sections: merged structure containing both "Introduction" and "Overview"

**Actual Result**: CLI error - only first file is processed, others are ignored or cause parsing errors.

### Step 3: Verify API limitations

```python
from md_as_data import MarkdownFile, generate_schema

# Load multiple documents
docs = [
    MarkdownFile('examples/doc1.md'),
    MarkdownFile('examples/doc2.md'),
    MarkdownFile('examples/doc3.md')
]

# Current API - can only generate schemas individually
schemas = [generate_schema(doc.mddata.data) for doc in docs]

# No built-in mechanism to merge schemas
# Would need to implement manual merging logic
```

**Expected Result**: API function that accepts multiple `ParsedMarkdownData` instances and returns merged schema.

**Actual Result**: Must manually implement schema merging logic.

## Diagnostics

**Affected Files/Classes/Components**:

1. **src/md_as_data/validation/schema_generator.py**
   - `generate_schema()` function - extend to accept one or multiple `ParsedMarkdownData` instances
   - Current: Processes single document
   - Needs: Internal merging logic to aggregate across multiple documents
   - Threshold configuration embedded in generator implementation

2. **src/cli/schema.py**
   - `generate_schema_command()` - modify to handle multiple file paths
   - Load and process all markdown files from provided paths
   - Display file count in output
   - Call `generate_schema()` with list of documents

3. **src/cli/main.py**
   - Current CLI structure: `mdasdata <file_path> <command>`
   - Extend to accept multiple paths: `mdasdata <path1> <path2> ... <command>`
   - When path is folder, recursively find *.md files

**Analysis**:

The feature requires extending the existing schema generator without creating new classes:

1. **Core Library Layer** (`schema_generator.py`):
   - Extend `generate_schema()` to accept `list[ParsedMarkdownData]` or single instance
   - Add internal merging logic in same module
   - Hard-code threshold logic (keep simple)
   - Algorithm:
     ```
     If single document:
       - Use current logic

     If multiple documents:
       For each property across all documents:
         - Count frequency (N appearances / total documents)
         - Collect all observed types → use union types for conflicts
         - Collect all observed values
         - Check if single-word string → infer enum (include nulls)
         - Calculate min/max for numbers, length for strings
         - Determine if required based on internal threshold

       For each section across all documents:
         - Merge all section hierarchies into union
         - Preserve all subsection relationships
         - Combine block type constraints
     ```

2. **CLI Layer** (`schema.py`, `main.py`):
   - Accept multiple file paths in existing structure
   - When path is directory, find all *.md files
   - Load all documents and pass to `generate_schema()`
   - Display: "Schema generated from N markdown files"

## Suggestions

### Implementation Approach

**Phase 1: Extend generate_schema() Function**

1. Modify function signature in `schema_generator.py`:
   ```python
   def generate_schema(
       data: ParsedMarkdownData | list[ParsedMarkdownData],
       inference_mode: SchemaInferenceMode = SchemaInferenceMode.PERMISSIVE
   ) -> DocumentSchema:
       # Handle both single and multiple documents
       if isinstance(data, list):
           return _generate_merged_schema(data, inference_mode)
       else:
           # Existing single-document logic
           return _generate_single_schema(data, inference_mode)
   ```

2. Implement internal merging logic:
   ```python
   def _generate_merged_schema(
       documents: list[ParsedMarkdownData],
       inference_mode: SchemaInferenceMode
   ) -> DocumentSchema:
       total_docs = len(documents)

       # Aggregate frontmatter properties
       prop_stats = {}
       for doc in documents:
           for prop_name, prop_value in doc["frontmatter"].items():
               if prop_name not in prop_stats:
                   prop_stats[prop_name] = {
                       "count": 0,
                       "types": set(),
                       "values": []
                   }
               prop_stats[prop_name]["count"] += 1
               prop_stats[prop_name]["types"].add(type(prop_value).__name__)
               if isinstance(prop_value, str) and " " not in prop_value:
                   prop_stats[prop_name]["values"].append(prop_value)

       # Generate frontmatter schema
       frontmatter_schema = {}
       for prop_name, stats in prop_stats.items():
           # Determine if required (internal threshold)
           required = stats["count"] / total_docs >= 0.75

           # Handle type conflicts with union types
           type_str = "|".join(sorted(stats["types"]))

           # Infer enum for single-word strings
           is_enum = (len(stats["types"]) == 1 and
                     "str" in stats["types"] and
                     len(stats["values"]) == stats["count"])

           frontmatter_schema[prop_name] = {
               "type": type_str,
               "required": required
           }

           if is_enum:
               frontmatter_schema[prop_name]["enum"] = list(set(stats["values"]))

       # Merge section structures
       sections_schema = _merge_section_hierarchies(documents)

       return {
           "frontmatter": frontmatter_schema,
           "sections": sections_schema,
           "validation_level": ValidationLevel.WARNINGS
       }
   ```

3. Implement section merging:
   ```python
   def _merge_section_hierarchies(
       documents: list[ParsedMarkdownData]
   ) -> dict[str, SectionSchema]:
       # Collect all sections from all documents
       all_sections = {}
       for doc in documents:
           for section in _extract_all_sections(doc["content"]):
               if section["id"] not in all_sections:
                   all_sections[section["id"]] = section
               # Merge subsections and blocks

       return all_sections
   ```

**Phase 2: CLI Integration**

1. Update `schema.py` to handle multiple file paths:
   ```python
   @app.command("generate")
   def generate_schema_command(
       inference_mode: Annotated[SchemaInferenceModeArg, typer.Option(...)] = ...,
       output: Annotated[Path | None, typer.Option(...)] = None,
       pretty: Annotated[bool, typer.Option(...)] = False
   ):
       # Get file paths from context (may be multiple)
       file_paths = cli_context.get_all_file_paths()

       # Filter to markdown files only
       md_files = [fp for fp in file_paths if fp.suffix == '.md']

       # If folder provided, find all markdown files
       folder_files = []
       for path in file_paths:
           if path.is_dir():
               folder_files.extend(path.rglob("*.md"))

       all_files = md_files + folder_files

       # Load all documents
       from md_as_data import MarkdownFile
       documents = [MarkdownFile(fp).mddata.data for fp in all_files]

       # Generate schema (handles single or multiple internally)
       schema = generate_schema(
           documents if len(documents) > 1 else documents[0],
           inference_mode=inference_mode
       )

       # Display file count
       console.print(f"Schema generated from {len(documents)} markdown file(s)")

       # Output schema
       if output:
           with open(output, 'w') as f:
               json.dump(schema, f, indent=2 if pretty else None)
       else:
           console.print_json(data=schema)
   ```

2. Update `main.py` to accept multiple paths:
   ```python
   @app.callback()
   def main(
       file_paths: Annotated[list[Path], typer.Argument(help="One or more markdown files or folders")] = [],
       ...
   ):
       # Store all paths in context
       cli_context.set_file_paths(file_paths)
   ```

**Phase 3: Testing**

1. Create unit tests for multi-document schema generation:
   - Test property frequency calculation
   - Test required field determination (internal 0.75 threshold)
   - Test enum inference for single-word strings
   - Test union type generation for type conflicts
   - Test section hierarchy merging
   - Test handling of null values in enums

2. Create integration tests for CLI:
   - Test multiple file paths: `mdasdata file1.md file2.md schema generate`
   - Test folder path: `mdasdata ./docs/ schema generate`
   - Test file count display in output
   - Test backward compatibility with single file mode

3. Create example-based tests:
   - Use existing examples/ files
   - Generate schemas from multiple documents
   - Validate merged schemas are correct

### Edge Cases to Handle

1. **Empty documents**: Skip documents with no frontmatter
2. **Property with None/null values**: Include in enum types
3. **Mixed types**: Use union types (e.g., `"str|list"`)
4. **Deeply nested sections**: Preserve full hierarchy paths when merging
5. **Single-word vs multi-word strings**: Only single-word strings become enums
6. **Non-markdown files in folders**: Filter to *.md files only

## Current Tests

**Relevant Test Suites**:

1. **tests/unit/md_as_data/validation/test_schema_generator.py**
   - Current coverage: Single document schema generation
   - Missing: Multi-document scenarios
   - Missing: Schema merging logic
   - Missing: Frequency-based requirement determination
   - Missing: Enum inference from multiple values
   - Missing: Type conflict resolution

2. **tests/unit/md_as_data/validation/test_schema_validator.py**
   - May need updates to handle union types
   - May need updates to validate enum constraints

3. **CLI tests** (if exist):
   - Missing: Multi-file schema generation command tests
   - Missing: Folder-based schema generation tests

**Analysis**:

The existing test suite focuses on single-document schema generation and validation. There are no tests for:
- Aggregating data across multiple documents
- Calculating property frequencies
- Determining required fields based on thresholds
- Inferring enums from observed values across files
- Resolving type conflicts between documents
- Merging section hierarchies

The lack of multi-document tests means this feature would not be caught by the existing test suite. New test coverage is essential before implementing this feature.

**Recommended Test Structure**:

```python
# tests/unit/md_as_data/validation/test_schema_generator.py (extend existing tests)

class TestMultiDocumentSchemaGeneration:
    def test_multiple_documents_property_frequency(self):
        """Test frequency calculation for properties across documents."""
        # 3 docs, property appears in 2 = 0.667 frequency
        ...

    def test_multiple_documents_required_determination(self):
        """Test property required when frequency >= 0.75."""
        ...

    def test_enum_inference_single_word_strings(self):
        """Test enum inference for single-word string properties."""
        ...

    def test_enum_includes_null_values(self):
        """Test that null values are included in enum types."""
        ...

    def test_union_types_for_type_conflicts(self):
        """Test union type generation for conflicting types."""
        ...

    def test_section_hierarchy_merging(self):
        """Test merging of different section structures."""
        ...

    def test_single_document_backward_compatibility(self):
        """Test that single document still works as before."""
        ...

class TestCLIMultiFileSchemaGeneration:
    def test_multiple_file_paths(self):
        """Test CLI with multiple file arguments."""
        ...

    def test_folder_path_processing(self):
        """Test CLI with folder path argument."""
        ...

    def test_file_count_display(self):
        """Test that file count is displayed in output."""
        ...

    def test_markdown_files_only(self):
        """Test that only .md files are processed from folders."""
        ...
```
