#!/bin/bash

# Script to refactor "template" to "datatemplate" in mdasdata project
# This script performs safe, targeted replacements

set -e  # Exit on error

echo "Starting datatemplate refactoring..."

# Function to replace in file with backup
safe_replace() {
    local file="$1"
    local old="$2"
    local new="$3"

    if [ -f "$file" ]; then
        echo "Processing: $file"
        sed -i.bak "s/$old/$new/g" "$file"
    else
        echo "Skipping (not found): $file"
    fi
}

# Update .claude/agents/datatemplate-designer.md (already renamed)
safe_replace ".claude/agents/datatemplate-designer.md" "template-designer" "datatemplate-designer"
safe_replace ".claude/agents/datatemplate-designer.md" "\\btemplate\\b" "datatemplate"
safe_replace ".claude/agents/datatemplate-designer.md" "Template" "DataTemplate"
safe_replace ".claude/agents/datatemplate-designer.md" "template\\.yaml" "datatemplate.yaml"
safe_replace ".claude/agents/datatemplate-designer.md" "template\\.json" "datatemplate.json"

# Update claude_mddata_tools/README.md
safe_replace "claude_mddata_tools/README.md" "md-template-designer" "md-datatemplate-designer"
safe_replace "claude_mddata_tools/README.md" "md-template-requirements-analyzer" "md-datatemplate-requirements-analyzer"

# Update claude_mddata_tools/skills/render/SKILL.md
safe_replace "claude_mddata_tools/skills/render/SKILL.md" "template" "datatemplate"
safe_replace "claude_mddata_tools/skills/render/SKILL.md" "Template" "DataTemplate"

# Update examples directory
if [ -d "examples/templates" ]; then
    echo "Renaming examples/templates to examples/datatemplates..."
    mv examples/templates examples/datatemplates

    # Update README in datatemplates
    safe_replace "examples/datatemplates/README.md" "\\btemplate\\b" "datatemplate"
    safe_replace "examples/datatemplates/README.md" "Template" "DataTemplate"
    safe_replace "examples/datatemplates/README.md" "templates/" "datatemplates/"

    # Update YAML files comments
    for yaml_file in examples/datatemplates/*.yaml; do
        if [ -f "$yaml_file" ]; then
            echo "Updating comments in: $yaml_file"
            sed -i.bak 's/# Template/# DataTemplate/g' "$yaml_file"
            sed -i.bak 's/# .*template/# datatemplate/g' "$yaml_file"
        fi
    done
fi

echo ""
echo "Refactoring complete!"
echo ""
echo "Files modified (backups created with .bak extension):"
find . -name "*.bak" -type f
echo ""
echo "Please review changes and remove .bak files when satisfied:"
echo "  find . -name '*.bak' -delete"
