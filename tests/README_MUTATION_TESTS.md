# Comprehensive Mutation Testing Suite

This directory contains a comprehensive test suite for the markdown-as-data mutation functionality, covering all major areas of programmatic document modification.

## Overview

The mutation test suite verifies the correct behavior of policy-based updates, frontmatter mutations, JSON imports, heading level preservation, and CLI integration. These tests ensure that the mutation functionality works correctly across all supported use cases.

## Test Structure

### Unit Tests

#### 1. UpdatePolicy System Tests (`test_update_policies.py`)
- **Status**: ✅ **PASSING** (17/17 tests)
- **Coverage**: Complete enum functionality and backwards compatibility
- **Key Features Tested**:
  - All policy values (REPLACE, UPDATE, MERGE, APPEND)
  - Backwards compatibility aliases (SectionPolicy, FrontmatterPolicy)
  - String conversion and validation
  - Policy comparison and collection usage

#### 2. Frontmatter Mutation Tests (`test_frontmatter_mutations.py`)
- **Status**: ⚠️ **NEEDS IMPLEMENTATION** (Tests ready, implementation pending)
- **Coverage**: Comprehensive frontmatter update operations
- **Key Features Tested**:
  - `update_frontmatter()` batch update method with all policies
  - `_update_frontmatter_property()` internal method behavior
  - Smart array merging without duplicates
  - Object merging with property override
  - List type support and array handling
  - Policy-specific behaviors (MERGE, REPLACE, APPEND, UPDATE)

#### 3. JSON Import Functionality Tests (`test_json_import.py`)
- **Status**: ⚠️ **NEEDS IMPLEMENTATION** (Tests ready, implementation pending)
- **Coverage**: Complete JSON import pipeline
- **Key Features Tested**:
  - Core `_apply_json_changes()` function
  - Frontmatter policy parsing and application
  - Section updates with different policies
  - Command output integration scenarios
  - Error handling for malformed JSON
  - Performance with large payloads

#### 4. Heading Level Preservation Tests (`test_heading_levels.py`)
- **Status**: ⚠️ **NEEDS IMPLEMENTATION** (Based on TEST_PLAN_HEADING_LEVELS.md)
- **Coverage**: Complete path validation and level preservation
- **Key Features Tested**:
  - Exact section path resolution
  - Ambiguous reference detection
  - Heading level maintenance across all policies
  - New subsection creation with correct levels
  - Path-based hierarchy creation

### Integration Tests

#### 5. CLI Integration Tests (`test_cli_mutations.py`)
- **Status**: ⚠️ **NEEDS CLI CONTEXT SETUP** (Tests ready, CLI context needed)
- **Coverage**: End-to-end CLI command testing
- **Key Features Tested**:
  - `set-property` command with various data types
  - `set-section` command with all policies
  - `from-json` command with file and stdin input
  - `remove-property` command
  - Complete workflow scenarios (git integration, CI/CD pipelines)
  - Error handling and edge cases

## Running the Tests

### All Mutation Tests
```bash
python run_mutation_tests.py
```

### Individual Test Suites
```bash
# Update policy tests (currently passing)
uv run pytest tests/unit/test_update_policies.py -v

# Frontmatter mutation tests
uv run pytest tests/unit/test_frontmatter_mutations.py -v

# JSON import tests
uv run pytest tests/unit/test_json_import.py -v

# Heading level preservation tests
uv run pytest tests/unit/test_heading_levels.py -v

# CLI integration tests
uv run pytest tests/integration/test_cli_mutations.py -v
```

### With Coverage
```bash
uv run pytest tests/unit/test_update_policies.py --cov=md_as_data --cov-report=html
```

## Test Categories and Coverage

### 1. Policy-Based Operations
- ✅ **Policy enum validation** - All policy values work correctly
- ⏳ **Frontmatter policy application** - MERGE, REPLACE, APPEND behaviors
- ⏳ **Section policy application** - UPDATE, REPLACE, APPEND behaviors
- ⏳ **Policy precedence and conflicts** - When multiple policies are specified

### 2. Data Type Handling
- ⏳ **Array merging without duplicates** - Smart list combination
- ⏳ **Object merging with override** - Dictionary property updates
- ⏳ **Primitive type replacement** - String, number, boolean updates
- ⏳ **Complex nested structures** - Multi-level object updates

### 3. Path Resolution and Navigation
- ⏳ **Exact path matching** - `parent.child.grandchild` format
- ⏳ **Ambiguous reference detection** - Multiple matches handling
- ⏳ **Partial path resolution** - Unique substring matching
- ⏳ **New path creation** - Automatic hierarchy building

### 4. Heading Level Management
- ⏳ **Level preservation during updates** - H1-H6 consistency
- ⏳ **New section level calculation** - Parent level + 1
- ⏳ **Maximum depth handling** - H6 limitation
- ⏳ **Title preservation** - Original titles maintained

### 5. CLI Command Integration
- ⏳ **Property setting commands** - Simple and JSON values
- ⏳ **Section manipulation commands** - Content updates with policies
- ⏳ **Batch import operations** - JSON file and stdin processing
- ⏳ **Error handling and validation** - User-friendly error messages

## Implementation Requirements

Based on the test suite, the following implementations are needed:

### Core MarkdownData Class
```python
def update_frontmatter(
    self,
    properties: dict[str, FrontmatterPropertyValue],
    policy: UpdatePolicy = UpdatePolicy.MERGE
) -> None:
    """Batch update frontmatter properties with policy support."""

def _update_frontmatter_property(
    self,
    key: str,
    new_value: FrontmatterPropertyValue,
    policy: UpdatePolicy
) -> None:
    """Update single property with policy-specific behavior."""
```

### CLI Infrastructure
- Context management for file loading
- Environment variable support for MARKDOWN_FILE
- Policy parsing and validation
- JSON input handling from files and stdin

### JSON Import Pipeline
```python
def _apply_json_changes(
    doc: MarkdownData,
    json_data: dict,
    printer: MarkdownPrinter
) -> int:
    """Apply JSON data changes to document with policy support."""
```

## Example Test Scenarios

### Frontmatter Array Merging
```python
# Original: ["original", "test"]
# New: ["test", "python", "new"]
# MERGE Result: ["original", "test", "python", "new"]  # No duplicates
```

### Heading Level Preservation
```python
# Original: "## Section Title" (Level 2)
# Update content without heading
# Result: Still Level 2, title preserved
```

### JSON Import with Policies
```python
{
    "frontmatter": {"tags": ["new", "tags"]},
    "frontmatter_policy": "APPEND",
    "sections": [
        {"id": "intro", "content": "Updated content", "policy": "UPDATE"}
    ]
}
```

## Benefits of This Test Suite

1. **Comprehensive Coverage**: Tests all mutation functionality thoroughly
2. **Real-World Scenarios**: Includes git integration, CI/CD, and automation use cases
3. **Edge Case Validation**: Handles ambiguous references, permission errors, malformed data
4. **Performance Testing**: Large payload handling and efficiency validation
5. **Clear Documentation**: Each test has descriptive names and comprehensive docstrings
6. **Maintainable Structure**: Well-organized test classes with reusable fixtures

## Next Steps

1. **Implement Core Functionality**: Start with `update_frontmatter()` methods
2. **Add CLI Context Support**: Environment variable and file loading
3. **Implement JSON Import**: `_apply_json_changes()` function
4. **Add Heading Level Logic**: Path-based level calculation
5. **Validate Against Tests**: Run test suite to verify implementation
6. **Performance Optimization**: Based on large payload test results

This comprehensive test suite provides a complete specification for the mutation functionality, ensuring robust and reliable programmatic document modification capabilities.