# DataTemplate Refactoring Status

## Goal
Rename "template" to "datatemplate" throughout the codebase to clearly differentiate:
- **DataTemplate**: MarkdownDataUpdate files with parameters (YAML/JSON format)
- **Template**: Other template concepts (kept as-is)

## ✅ Completed Changes

### 1. Agent Files (Primary)
- ✅ Renamed `claude_mddata_tools/mddata-plugin/agents/md-template-designer.md` → `md-datatemplate-designer.md`
- ✅ Updated all internal references in the designer agent
- ✅ Renamed `claude_mddata_tools/mddata-plugin/agents/md-template-requirements-analyzer.md` → `md-datatemplate-requirements-analyzer.md`
- ✅ Updated all internal references in the requirements analyzer agent
- ✅ Renamed `.claude/agents/template-designer.md` → `datatemplate-designer.md`

### 2. Documentation
- ✅ Renamed `claude_mddata_tools/mddata-plugin/docs/TEMPLATE_PATTERNS.md` → `DATATEMPLATE_PATTERNS.md`
- ✅ Updated title and main headings in DATATEMPLATE_PATTERNS.md

## 📋 Remaining Tasks

### High Priority
1. **Update .claude/agents/datatemplate-designer.md** - Full content update needed
2. **Update claude_mddata_tools/README.md** - Agent references
3. **Update claude_mddata_tools/skills/render/SKILL.md** - Terminology
4. **Rename examples/templates/** → `examples/datatemplates/`
5. **Update examples README and YAML files**

### Medium Priority
6. **docs/TEMPLATES.md** - Consider renaming to DATATEMPLATES.md
7. **docs/CLI_REFERENCE.md** - Update terminology
8. **CLAUDE.md** - Update references
9. **README.md** - Update references

### Lower Priority (Code)
10. **src/cli/render.py** - Update help text
11. **src/cli/write.py** - Update help text
12. **src/mddata/models/template.py** - Add clarifying comment
13. **tests/** - Update test names and docstrings

## 🚀 Quick Start

Run the automated refactoring script:

```bash
./refactor_to_datatemplate.sh
```

This script will:
- Update .claude/agents/datatemplate-designer.md
- Update claude_mddata_tools README and skills
- Rename examples/templates to examples/datatemplates
- Update all YAML file comments
- Create .bak backups of all modified files

After running, review changes and remove backups:

```bash
# Review changes
git diff

# If satisfied, remove backups
find . -name '*.bak' -delete
```

## 🔍 Manual Review Needed

After script execution, manually review:

1. **Python help strings** - CLI command descriptions
2. **Docstrings** - Update terminology in comments
3. **CLAUDE.md** - Architecture documentation
4. **README.md** - Public documentation

## 📝 Terminology Rules

### Use "DataTemplate"
- MarkdownDataUpdate files with parameters
- YAML/JSON parameter-based generation
- Agent names and specific documentation

### Keep "Template" (unchanged)
- Python module names (`src/mddata/templates/`)
- Model file names (implementation detail)
- General template references

## ✨ Benefits

After refactoring:
- Clear distinction between datatemplates and other templates
- Easier for users to understand the parameter-based generation feature
- More precise terminology in documentation
- Better alignment with MarkdownDataUpdate model concept
