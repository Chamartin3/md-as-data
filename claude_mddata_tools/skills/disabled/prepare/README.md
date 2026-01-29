# Markdown Data Preparation Skill

## Purpose

The `md-prepare` skill is a foundational skill that should be used **before** any other mddata operations to ensure:

1. ✅ mddata tool is installed and accessible
2. ✅ Command parameters are understood
3. ✅ Data structures match expected formats
4. ✅ Schemas are valid before validation

## When to Use

This skill is automatically invoked when:

- User wants to work with mddata but installation status is uncertain
- Before executing `mddata write --data` (validates MarkdownDataDict format)
- Before executing `mddata schema validate` (validates schema format)
- User asks about data format requirements
- Any mddata command is mentioned and tool availability needs confirmation

## Key Features

### Installation Check
- Verifies if mddata command is available
- **Stops immediately** if mddata is not found
- Reports clearly when tool is not available
- Does not proceed with mddata operations if tool is missing

### Data Format Validation
- Validates JSON/YAML syntax
- Checks MarkdownDataDict structure (frontmatter + content)
- Verifies required fields for sections and blocks
- Ensures block types are valid

### Schema Format Validation
- Validates schema JSON/YAML syntax
- Checks property type definitions
- Verifies validation rule types
- Ensures section constraints are valid

### Format References
- Points to complete specifications (MARKDOWN_DATA.md, MARKDOWN_SCHEMA.md)
- Provides minimal working examples
- Explains common validation errors

## Supporting Files

### SKILL.md
Main skill definition with instructions for Claude Code.

### MARKDOWN_DATA.md
Complete reference for the MarkdownDataDict format used by `mddata write --data`.

**Key sections:**
- Structure overview (frontmatter, content, sections, blocks)
- Block types reference (paragraph, code_block, list, etc.)
- Complete examples
- CLI usage patterns
- Update data format for modifications

### MARKDOWN_SCHEMA.md
Complete reference for schema format used by `mddata schema validate`.

**Key sections:**
- Schema structure (properties, sections, validation)
- Property types and constraints
- Validation rules (min_length, pattern, etc.)
- Section validation (required, allowed_content, etc.)
- Multi-file schema generation
- Schema inference modes

## Integration

This skill works **before** other mddata skills:

```
User Request
    ↓
md-prepare (check installation & formats)
    ↓ (if mddata found)
    ├─→ md-query
    ├─→ md-schema
    └─→ md-generator

    ↓ (if mddata NOT found)
    └─→ STOP: Report tool is not available
```

## Critical Behavior

**If mddata is not installed:**
1. Report clearly: "I cannot use mddata because it is not installed."
2. STOP immediately - do not proceed with mddata operations
3. Do not suggest mddata commands if tool is missing

**If mddata is installed:**
1. Validate data/schema formats before operations
2. Reference complete documentation when explaining formats
3. Provide clear error messages when validation fails

## Quick Reference

### MarkdownDataDict Minimal Structure
```json
{
  "frontmatter": {},
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": []
  }
}
```

### Schema Minimal Structure
```json
{
  "version": "1.0.0",
  "properties": {},
  "sections": {}
}
```

## Related Skills

- **md-query**: Read and inspect markdown files (use after preparation)
- **md-schema**: Generate and validate schemas (use after preparation)
- **md-generator**: Generate markdown from data (use after preparation)

## Notes

- This is a **read-only** skill (allowed-tools: Bash, Read)
- Never modifies files, only checks and validates
- Should be quick and lightweight
- References complete documentation instead of duplicating
- Prevents errors through proactive preparation
- **Critical**: Stops immediately if mddata is not available
