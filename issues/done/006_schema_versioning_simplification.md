# Issue Report: Schema Versioning and Naming Simplification

## Issue Description

The current schema validation system requires several improvements to enhance maintainability, consistency, and flexibility:

1. **No Schema Versioning**: Schemas lack version metadata, making it impossible to track schema evolution or handle backward compatibility when schema structure changes.

2. **Inconsistent Terminology**: The schema uses domain-specific terms (`frontmatter`, `subsections`) that don't align with generic data structure conventions. This creates cognitive overhead and reduces code clarity.

3. **Validation Level Coupling**: The `validation_level` is embedded within the schema itself (line 87 in `schema_models.py`), coupling validation behavior to schema data rather than runtime configuration.

4. **Monolithic Validator**: The `SchemaValidator` class (430 lines) handles both frontmatter property validation and section validation, violating single responsibility principle and making the code harder to maintain.

5. **Repeated Validation Logic**: Validation rules (min_length, max_length, regex, etc.) contain repeated string literals and duplicated error message construction across multiple methods.

6. **Magic Strings**: Field names and types are hardcoded throughout the codebase as string literals, creating opportunities for typos and making refactoring difficult.

### Current Environment

**Affected System Components**:
- Schema models: `/home/omidev/Code/tools/makdown_manager/mdasdata/src/md_as_data/validation/schema_models.py`
- Validator engine: `/home/omidev/Code/tools/makdown_manager/mdasdata/src/md_as_data/validation/schema_validator.py`
- Schema generator: `/home/omidev/Code/tools/makdown_manager/mdasdata/src/md_as_data/validation/schema_generator.py`
- CLI commands: `/home/omidev/Code/tools/makdown_manager/mdasdata/src/cli/schema.py`
- Example schemas: All JSON files in `/home/omidev/Code/tools/makdown_manager/mdasdata/examples/schemas/`
- Data integration: `/home/omidev/Code/tools/makdown_manager/mdasdata/src/md_as_data/data.py` (lines 294-303, 418-436)

**Current Usage Patterns**:
- `DocumentSchema` TypedDict defines schema structure with `frontmatter`, `sections`, `validation_level`
- `SectionSchema` uses `subsections` key for nested sections (line 77 in schema_models.py)
- `ValidationIssue.field_type` uses literals `"frontmatter"` or `"section"` (line 93)
- `SchemaValidator.__init__()` extracts `validation_level` from schema dict (line 31-33 in schema_validator.py)
- CLI displays validation results using `field_type` (lines 113, 121 in schema.py)
- Multiple example schemas in JSON format use current naming conventions

### Doubts

1. **Versioning Scheme**: Should we use semantic versioning (e.g., "1.0.0") or simple integer versioning (e.g., 1, 2, 3)? How should version compatibility be checked?

2. **Backward Compatibility Strategy**: When loading old schemas without version field or using old field names, should we:
   - Auto-migrate silently?
   - Emit warnings and auto-migrate?
   - Fail validation with clear migration instructions?
   - Support both old and new field names indefinitely?

3. **Constants Organization**: Should schema field name constants be:
   - In a dedicated `constants.py` module?
   - Within `schema_models.py` near the TypedDict definitions?
   - Split between modules (validation constants in validation/, general constants elsewhere)?

4. **Sub-validator Interface**: What should the contract be between `SchemaValidator` and the new `PropertyValidator`/`SectionValidator`?
   - Should sub-validators share state or be completely independent?
   - Should they return partial `ValidationResult` objects or lists of issues?
   - How should they handle validation level configuration?

5. **API Compatibility**: How to maintain backward compatibility?
   - The `SchemaValidator(schema)` constructor currently accepts schema with embedded validation_level
   - Should we support both `SchemaValidator(schema)` and `SchemaValidator(schema, validation_level=...)`?
   - What happens if validation_level is specified both in schema and constructor?

6. **CLI Parameter Design**: For the new `--validation-level` CLI parameter:
   - Should it override schema-embedded validation_level if both exist?
   - Should it be required or optional with fallback to schema value?
   - Where in the command structure should it appear (global option vs subcommand option)?

## Step-by-Step Reproduction

### Setup Process

1. Examine current schema structure in example files:
```bash
cd /home/omidev/Code/tools/makdown_manager/mdasdata
cat examples/schemas/simple_permissive.json
```

2. Review current schema model definitions:
```bash
cat src/md_as_data/validation/schema_models.py
```

3. Analyze validator implementation:
```bash
cat src/md_as_data/validation/schema_validator.py
```

4. Check CLI schema commands:
```bash
cat src/cli/schema.py
```

### Reproduction Steps

**Step 1: Verify lack of schema versioning**
```bash
# Check all example schemas - none contain version field
grep -r "\"version\"" examples/schemas/
# Result: No schema version field found (only document frontmatter versions)
```

**Expected**: Schemas should have version metadata
**Actual**: No version field exists in schema structure

**Step 2: Confirm current naming conventions**
```bash
# Find all uses of "frontmatter" in schema context
grep -n "frontmatter" src/md_as_data/validation/schema_models.py
# Result: Line 85 (DocumentSchema), Line 93 (ValidationIssue.field_type)

# Find all uses of "subsections"
grep -n "subsections" src/md_as_data/validation/schema_models.py
# Result: Line 77 (SectionSchema)
```

**Expected**: Generic naming (properties, children)
**Actual**: Domain-specific naming (frontmatter, subsections)

**Step 3: Locate validation_level in schema**
```bash
# Check DocumentSchema definition
sed -n '82,88p' src/md_as_data/validation/schema_models.py
```
Output shows:
```python
class DocumentSchema(TypedDict):
    """Complete document schema definition."""

    frontmatter: dict[str, PropertySchema]
    sections: dict[str, SectionSchema]
    validation_level: ValidationLevel
```

**Expected**: Validation level as runtime configuration parameter
**Actual**: Validation level embedded in schema data structure

**Step 4: Analyze SchemaValidator structure**
```bash
# Count lines in SchemaValidator
wc -l src/md_as_data/validation/schema_validator.py
# Result: 430 lines

# Check methods handling different validation concerns
grep -n "def _validate" src/md_as_data/validation/schema_validator.py
```
Output shows methods mixing property and section validation concerns:
- `_validate_frontmatter` (line 72)
- `_validate_property` (line 113)
- `_apply_validation_rule` (line 143)
- `_validate_sections` (line 223)
- `_validate_section` (line 277)

**Expected**: Separate validators for properties and sections
**Actual**: Monolithic validator handling all concerns

**Step 5: Identify repeated validation logic**
```bash
# Check for hardcoded field_type strings
grep -n "\"field_type\":" src/md_as_data/validation/schema_validator.py | wc -l
# Result: 16 occurrences

# Check for hardcoded "frontmatter" string
grep -n "\"frontmatter\"" src/md_as_data/validation/schema_validator.py | wc -l
# Result: 10 occurrences

# Check for hardcoded "section" string
grep -n "\"section\"" src/md_as_data/validation/schema_validator.py | wc -l
# Result: 7 occurrences
```

**Expected**: Constants defined once and reused
**Actual**: String literals repeated throughout validation logic

**Step 6: Test current CLI validation command**
```bash
# Generate a test schema
uv run mdasdata examples/simple.md schema generate --output /tmp/test_schema.json

# Validate document (validation level comes from schema, not CLI)
uv run mdasdata examples/simple.md schema validate /tmp/test_schema.json
```

**Expected**: Ability to specify validation level as CLI parameter
**Actual**: Validation level must be embedded in schema JSON file

**Step 7: Check how validation level is currently used**
```bash
# Find SchemaValidator instantiation in data.py
grep -n "SchemaValidator" src/md_as_data/data.py
```
Output shows line 302:
```python
self, "_validator", SchemaValidator(schema) if schema else None
```

**Expected**: Validation level passed as constructor parameter
**Actual**: Validation level read from schema dict inside validator

**Step 8: Examine validation rule encapsulation**
```bash
# Look at _apply_validation_rule method
sed -n '143,221p' src/md_as_data/validation/schema_validator.py
```
Output shows repeated if/elif blocks for each validation type (MIN_LENGTH, MAX_LENGTH, MIN_VALUE, MAX_VALUE, REGEX, ALLOWED_VALUES) with duplicated error dict construction.

**Expected**: Validation rules as callable methods indexed by validation_type
**Actual**: Large if/elif chain with repeated error construction logic

## Diagnostics

### Affected Files/Classes/Components

**Core Validation Module** (`src/md_as_data/validation/`):
- `schema_models.py`:
  - `DocumentSchema` (lines 82-87): Contains validation_level field
  - `SectionSchema` (lines 74-79): Uses `subsections` field name
  - `ValidationIssue` (lines 90-97): Uses `field_type` with literals "frontmatter"/"section"

- `schema_validator.py`:
  - `SchemaValidator.__init__()` (lines 24-33): Reads validation_level from schema
  - `SchemaValidator.validate()` (lines 35-70): Monolithic entry point
  - `_validate_frontmatter()` (lines 72-111): Property validation logic
  - `_validate_property()` (lines 113-141): Individual property validation
  - `_apply_validation_rule()` (lines 143-221): Hardcoded validation rules
  - `_validate_sections()` (lines 223-275): Section validation logic
  - `_validate_section()` (lines 277-391): Individual section validation

- `schema_generator.py`:
  - Line 54: Hardcoded `validation_level: ValidationLevel.WARNINGS`
  - Line 183: Uses `subsections` field name
  - Lines 52-55: Schema generation returns DocumentSchema with embedded validation_level

**CLI Interface** (`src/cli/schema.py`):
- Lines 100-101: `SchemaValidator(schema_data)` - no validation_level parameter
- Lines 113, 121: Display logic depends on `field_type` field name
- Lines 158-159: Info command displays `validation_level` from schema
- No `--validation-level` parameter currently exists

**Data Integration** (`src/md_as_data/data.py`):
- Line 302: `SchemaValidator(schema)` instantiation in `__init__`
- Lines 424-427: Extracts validation_level from schema for error handling

**Example Schemas** (all files in `examples/schemas/`):
- All 6 schema JSON files use current field names:
  - `"frontmatter": {...}`
  - `"subsections": {...}`
  - `"validation_level": "warnings"` or `"strict"`
- None contain version field

**Test Suite** (`tests/unit/md_as_data/validation/`):
- `test_schema_validator.py`: Tests assume validation_level in schema
- `test_schema_generator.py`: Tests verify generated schema structure includes validation_level
- Multiple test assertions check for current field names

### Analysis

**How the Issue Manifests**:

1. **Schema Evolution Tracking Failure**: Without versioning, when schema structure changes (like this refactoring), there's no way to programmatically detect schema format version. Applications loading schemas have no metadata to determine compatibility or trigger migration logic.

2. **Terminology Mismatch**: Using `frontmatter` and `subsections` creates a semantic gap:
   - `frontmatter` is markdown-specific jargon (YAML front matter)
   - `subsections` mixes hierarchical concept with markdown semantics
   - Generic terms (`properties`, `children`) would better reflect data structure and enable schema reuse in non-markdown contexts

3. **Configuration vs Data Confusion**: Embedding `validation_level` in schema conflates two concerns:
   - **Schema data**: Structural rules (what fields exist, what types they have)
   - **Runtime behavior**: How strictly to enforce rules during validation
   - This makes it impossible to validate the same schema at different strictness levels without modifying the schema file

4. **Maintenance Burden**: The 430-line monolithic `SchemaValidator`:
   - Mixes property validation (lines 72-141) and section validation (lines 223-391)
   - Makes targeted testing difficult (can't unit test property validation in isolation)
   - Violates single responsibility principle
   - Harder to extend with new validation types

5. **Code Duplication**: The `_apply_validation_rule` method:
   - Repeats `"field_type": "frontmatter"` 6 times in error construction
   - Repeats `"field": f"frontmatter.{field_name}"` 6 times
   - Could use a registry pattern: `self.validation_handlers[validation_type](value, validation_value)`

6. **Brittle String Dependencies**: Using magic strings creates risks:
   - Typo in `"frontmatter"` vs `"frontmater"` only caught at runtime
   - IDE refactoring tools can't track string literal usage
   - Grep-based code search required to find all usages

**Root Cause Analysis**:

The validation subsystem was initially implemented with schema validation tightly coupled to the markdown document model. As the system evolved:
- Schema became a serializable artifact (JSON files) while retaining runtime config (validation_level)
- Validator grew organically to handle both properties and sections without clear separation
- Field names reflected the original markdown-centric design rather than generic data structures
- No versioning mechanism was needed initially but became necessary as schema structure evolved

**Impact Assessment**:

**Current Pain Points**:
- Cannot validate same schema at different strictness levels without file modification
- Difficult to test property validation independently from section validation
- Risk of typos in repeated string literals for field types
- No migration path when schema structure changes

**Benefits of Resolution**:
- **Schema versioning**: Enables backward compatibility checks and automatic migration
- **Clearer naming**: Reduces cognitive load, improves code readability
- **Flexible validation**: Same schema can be validated at different levels based on context
- **Better testability**: Sub-validators can be unit tested independently
- **Easier maintenance**: Validation rules as methods enable cleaner code organization
- **Type safety**: Constants eliminate typo risks and enable IDE refactoring

## Suggestions

### 1. Add Schema Versioning

**Recommendation**: Use semantic versioning (semver) for schema versions.

**Rationale**:
- Semver provides clear semantics: major.minor.patch
- Major version change = breaking schema structure changes
- Minor version change = backward-compatible additions
- Patch version = non-functional updates (descriptions, formatting)

**Implementation**:
```python
# In schema_models.py
class DocumentSchema(TypedDict):
    """Complete document schema definition."""

    schema_version: str  # e.g., "1.0.0"
    properties: dict[str, PropertySchema]  # renamed from frontmatter
    sections: dict[str, SectionSchema]
    # validation_level moved to SchemaValidator constructor
```

**Migration Strategy**:
- Schemas without `schema_version` field: assumed to be version "0.0.0" (legacy)
- Implement schema migration functions: `migrate_0_to_1()`, etc.
- Emit warnings when loading legacy schemas
- Provide CLI command: `mdasdata schema migrate input.json --output migrated.json`

### 2. Rename Fields to Generic Terms

**Recommendations**:
- `frontmatter` → `properties` (document properties/metadata)
- `subsections` → `children` (hierarchical child nodes)
- `field_type` values: `"frontmatter"` → `"property"`, `"section"` → `"section"` (already generic)

**Rationale**:
- `properties`: Standard term for object attributes in JSON Schema, GraphQL, etc.
- `children`: Universal term for tree hierarchies in data structures
- More intuitive for developers unfamiliar with markdown conventions

**Implementation**:
```python
# Define constants in schema_models.py
class SchemaFieldNames:
    """Constants for schema field names."""
    SCHEMA_VERSION = "schema_version"
    PROPERTIES = "properties"
    SECTIONS = "sections"
    CHILDREN = "children"
    VALIDATION = "validation"

class ValidationIssueTypes:
    """Constants for validation issue types."""
    PROPERTY = "property"
    SECTION = "section"

# Update TypedDict definitions
class SectionSchema(TypedDict, total=False):
    """Schema definition for content sections."""

    children: dict[str, "SectionSchema"]  # renamed from subsections
    description: str
    validation: SectionValidationSchema

class ValidationIssue(TypedDict):
    """Individual validation issue."""

    field_type: Literal["property", "section"]  # updated literal
    field: str
    message: str
    expected: str | None
    actual: str | None
```

### 3. Move validation_level to Validator Construction

**Recommendation**: Make `validation_level` a `SchemaValidator` constructor parameter with fallback to schema default.

**Implementation**:
```python
# In schema_validator.py
class SchemaValidator:
    """Validates markdown documents against defined schemas."""

    def __init__(
        self,
        schema: DocumentSchema,
        validation_level: ValidationLevel | None = None
    ):
        """Initialize validator with document schema.

        Args:
            schema: Document schema definition
            validation_level: Override validation level (optional).
                If not provided, uses level from schema (deprecated) or defaults to WARNINGS.
        """
        self.schema = schema

        # Priority: 1) explicit parameter, 2) schema value (deprecated), 3) default
        if validation_level is not None:
            self.validation_level = validation_level
        elif "validation_level" in schema:
            # Emit deprecation warning
            import warnings
            warnings.warn(
                "Embedding validation_level in schema is deprecated. "
                "Pass validation_level to SchemaValidator constructor instead.",
                DeprecationWarning,
                stacklevel=2
            )
            self.validation_level = ValidationLevel(schema["validation_level"])
        else:
            self.validation_level = ValidationLevel.WARNINGS
```

**CLI Integration**:
```python
# In cli/schema.py
@app.command("validate")
def validate_command(
    schema_file: Annotated[Path, typer.Argument(...)],
    verbose: Annotated[bool, typer.Option(...)] = False,
    validation_level: Annotated[
        str | None,
        typer.Option(
            "--validation-level",
            "-l",
            help="Validation level: strict, warnings, or disabled"
        )
    ] = None,
) -> None:
    """Validate document against a schema file."""
    # ... load schema ...

    # Parse validation level if provided
    level = None
    if validation_level:
        try:
            level = ValidationLevel(validation_level)
        except ValueError:
            printer.print_error(f"Invalid validation level: {validation_level}")
            raise typer.Exit(1)

    # Create validator with optional level override
    validator = SchemaValidator(schema_data, validation_level=level)
    result = validator.validate(md_file.mddata)
    # ...
```

### 4. Split SchemaValidator into Sub-validators

**Recommendation**: Create `PropertyValidator` and `SectionValidator` classes with `SchemaValidator` as coordinator.

**Architecture**:
```python
# New file: schema_property_validator.py
class PropertyValidator:
    """Validates document properties (frontmatter) against schema."""

    def __init__(self, validation_level: ValidationLevel):
        self.validation_level = validation_level
        self._setup_validation_handlers()

    def _setup_validation_handlers(self) -> None:
        """Register validation rule handlers."""
        self.validation_handlers = {
            ValidationType.MIN_LENGTH: self._validate_min_length,
            ValidationType.MAX_LENGTH: self._validate_max_length,
            ValidationType.MIN_VALUE: self._validate_min_value,
            ValidationType.MAX_VALUE: self._validate_max_value,
            ValidationType.REGEX: self._validate_regex,
            ValidationType.ALLOWED_VALUES: self._validate_allowed_values,
        }

    def validate_properties(
        self,
        properties: dict[str, FrontmatterValue],
        schema: dict[str, PropertySchema],
    ) -> list[ValidationIssue]:
        """Validate all properties against schema."""
        # Current _validate_frontmatter logic
        ...

    def _validate_min_length(
        self, field_name: str, value: Any, constraint: Any, message: str
    ) -> ValidationIssue | None:
        """Validate minimum length constraint."""
        if isinstance(value, (str, list)) and len(value) < constraint:
            return self._create_issue(
                field_name,
                f"Length {len(value)} below minimum {constraint}",
                f">= {constraint}",
                str(len(value))
            )
        return None

    def _create_issue(
        self, field_name: str, message: str, expected: str, actual: str
    ) -> ValidationIssue:
        """Create standardized validation issue."""
        return {
            "field_type": ValidationIssueTypes.PROPERTY,
            "field": f"{SchemaFieldNames.PROPERTIES}.{field_name}",
            "message": message,
            "expected": expected,
            "actual": actual,
        }

# New file: schema_section_validator.py
class SectionValidator:
    """Validates document sections against schema."""

    def __init__(self, validation_level: ValidationLevel):
        self.validation_level = validation_level

    def validate_sections(
        self,
        content: Any,
        schema: dict[str, SectionSchema],
    ) -> list[ValidationIssue]:
        """Validate all sections against schema."""
        # Current _validate_sections logic
        ...

    def _create_issue(
        self, path: str, message: str, expected: str, actual: str
    ) -> ValidationIssue:
        """Create standardized validation issue."""
        return {
            "field_type": ValidationIssueTypes.SECTION,
            "field": path,
            "message": message,
            "expected": expected,
            "actual": actual,
        }

# Updated schema_validator.py
class SchemaValidator:
    """Validates markdown documents against defined schemas."""

    def __init__(
        self,
        schema: DocumentSchema,
        validation_level: ValidationLevel | None = None
    ):
        self.schema = schema
        self.validation_level = self._resolve_validation_level(
            validation_level, schema
        )

        # Delegate to sub-validators
        self.property_validator = PropertyValidator(self.validation_level)
        self.section_validator = SectionValidator(self.validation_level)

    def validate(self, data: Any) -> ValidationResult:
        """Validate document data against schema."""
        errors: list[ValidationIssue] = []

        if self.validation_level == ValidationLevel.DISABLED:
            return {"valid": True, "errors": [], "warnings": []}

        # Delegate to sub-validators
        if SchemaFieldNames.PROPERTIES in self.schema:
            errors.extend(
                self.property_validator.validate_properties(
                    data.frontmatter if hasattr(data, "frontmatter") else {},
                    self.schema[SchemaFieldNames.PROPERTIES],
                )
            )

        if SchemaFieldNames.SECTIONS in self.schema:
            errors.extend(
                self.section_validator.validate_sections(
                    data.content if hasattr(data, "content") else None,
                    self.schema[SchemaFieldNames.SECTIONS],
                )
            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": []}
```

**Benefits**:
- Clear separation of concerns
- Each validator can be unit tested independently
- Easier to extend with new validation types
- Reduced file size and complexity

### 5. Encapsulate Validation Rules as Callable Methods

**Recommendation**: Use handler registry pattern for validation rules.

**Implementation** (shown in PropertyValidator above):
- Define `validation_handlers` dict mapping `ValidationType` to methods
- Each validation method has consistent signature
- Apply validation by calling: `self.validation_handlers[validation_type](...)`
- Eliminates if/elif chain, makes adding new rules trivial

### 6. Define Constants for Field Names and Types

**Recommendation**: Create constant classes in `schema_models.py`.

**Implementation** (shown above):
```python
class SchemaFieldNames:
    """Constants for schema field names."""
    SCHEMA_VERSION = "schema_version"
    PROPERTIES = "properties"
    SECTIONS = "sections"
    CHILDREN = "children"
    VALIDATION = "validation"

class ValidationIssueTypes:
    """Constants for validation issue types."""
    PROPERTY = "property"
    SECTION = "section"
```

**Usage**:
```python
# Instead of: if "frontmatter" in schema:
if SchemaFieldNames.PROPERTIES in schema:
    ...

# Instead of: "field_type": "frontmatter"
"field_type": ValidationIssueTypes.PROPERTY
```

### Implementation Roadmap

**Phase 1: Constants and Naming** (low risk, high value)
1. Add constant classes to `schema_models.py`
2. Update TypedDict definitions with new field names
3. Update all code to use constants instead of literals
4. Add deprecation warnings for old field names in loaded schemas

**Phase 2: Validation Level Extraction** (medium risk)
1. Update `SchemaValidator.__init__()` to accept optional `validation_level` parameter
2. Add deprecation warning when reading from schema
3. Update CLI to add `--validation-level` option
4. Update documentation and examples

**Phase 3: Schema Versioning** (medium risk)
1. Add `schema_version` field to `DocumentSchema`
2. Implement schema migration logic
3. Update `generate_schema()` to include version "1.0.0"
4. Add CLI command for schema migration
5. Update all example schemas

**Phase 4: Validator Refactoring** (higher risk, but better testability helps)
1. Extract `PropertyValidator` class
2. Extract `SectionValidator` class
3. Refactor `SchemaValidator` to delegate to sub-validators
4. Update all tests to work with new architecture
5. Run full test suite to ensure no regressions

### Backward Compatibility Strategy

**Schema File Compatibility**:
- Support loading legacy schemas (without version, with old field names)
- Emit clear deprecation warnings
- Provide migration tool: `mdasdata schema migrate old.json --output new.json`
- Document migration guide in CHANGELOG and documentation

**API Compatibility**:
- `SchemaValidator(schema)` continues to work (reads validation_level from schema with warning)
- `SchemaValidator(schema, validation_level=...)` new recommended form
- Old field names internally mapped to new names with deprecation warnings
- Maintain compatibility for at least 2 major versions before removing deprecated paths

## Current Tests

### Relevant Test Suites

**Unit Tests**:
1. **`tests/unit/md_as_data/validation/test_schema_models.py`**: Tests TypedDict definitions
   - Should catch: Changes to `DocumentSchema`, `SectionSchema`, `ValidationIssue` structure
   - Currently missing: No tests exist for this module (opportunity to add)

2. **`tests/unit/md_as_data/validation/test_schema_validator.py`**: Tests validator behavior
   - Should catch: Changes to validation logic, validation_level handling, error message formats
   - Coverage: Tests frontmatter validation, section validation, validation levels
   - Gap: Doesn't test validation_level parameter to constructor (because it doesn't exist yet)

3. **`tests/unit/md_as_data/validation/test_schema_generator.py`**: Tests schema generation
   - Should catch: Changes to generated schema structure, field names
   - Coverage: Tests property inference, section analysis, validation level default
   - Gap: Doesn't verify schema versioning (because it doesn't exist yet)

**Integration Tests**:
1. **`tests/integration/test_cli_mutations.py`**: Tests CLI commands
   - Should catch: CLI parameter changes, output format changes
   - Gap: No tests for `schema validate` command with `--validation-level` parameter

**Why Current Tests Don't Catch This Issue**:

1. **No Schema Structure Validation**: Tests don't assert that schemas contain required fields like `schema_version`. They assume the structure defined by TypedDict is always correct.

2. **Hardcoded String Literals in Tests**: Test files use the same string literals (`"frontmatter"`, `"section"`) as the implementation, so renaming fields would break tests (which is good), but tests don't verify field name consistency.

3. **No Validator Constructor Tests**: Tests instantiate `SchemaValidator(schema)` but don't test alternative constructor signatures like `SchemaValidator(schema, validation_level=...)`.

4. **No Migration Testing**: No tests verify backward compatibility or schema migration logic because those features don't exist.

5. **No CLI Parameter Coverage**: Schema CLI commands are tested for basic functionality, but not for parameter variations like `--validation-level`.

**Recommendations for Test Improvements**:

1. **Add Schema Structure Tests**:
```python
def test_document_schema_contains_version():
    """Verify generated schemas include version field."""
    schema = generate_schema(sample_data)
    assert "schema_version" in schema
    assert schema["schema_version"] == "1.0.0"
```

2. **Add Backward Compatibility Tests**:
```python
def test_load_legacy_schema_without_version():
    """Test loading schema without version field."""
    legacy_schema = {"frontmatter": {}, "sections": {}, "validation_level": "warnings"}
    with pytest.warns(DeprecationWarning):
        validator = SchemaValidator(legacy_schema)
    # Should still work but emit warning
```

3. **Add Validator Constructor Tests**:
```python
def test_validation_level_parameter_override():
    """Test validation_level parameter overrides schema value."""
    schema = {"properties": {}, "sections": {}}
    validator = SchemaValidator(schema, validation_level=ValidationLevel.STRICT)
    assert validator.validation_level == ValidationLevel.STRICT
```

4. **Add CLI Parameter Tests**:
```python
def test_schema_validate_with_level_parameter(cli_runner):
    """Test schema validate command with --validation-level."""
    result = cli_runner.invoke(
        app, ["doc.md", "schema", "validate", "schema.json", "--validation-level", "strict"]
    )
    assert result.exit_code == 0
```

5. **Add Constants Usage Tests**:
```python
def test_schema_field_names_constants():
    """Verify constants match actual schema structure."""
    assert SchemaFieldNames.PROPERTIES == "properties"
    assert SchemaFieldNames.SECTIONS == "sections"
    assert ValidationIssueTypes.PROPERTY == "property"
```
