# mddata Use Case Examples

This directory contains comprehensive examples demonstrating different ways to use mddata for various content management scenarios. Each example showcases different features and patterns for working with structured markdown documents.

## Examples Overview

### 1. Technical Documentation (Schema-based) 📚
**Location:** `technical_docs/`
**Approach:** JSON Schema validation

Demonstrates how to use mddata for API documentation, technical specifications, and developer guides. Features:

- **JSON Schema validation** for strict document structure
- **Mixed content** - allows content both in subsections and at root level  
- **Rich frontmatter** with version info, dates, and metadata
- **Nested sections** for organized technical content
- **Code blocks and detailed explanations** for integration examples
- **Content outside subsections** for overview and introduction text

**Best for:** API docs, technical specifications, developer guides, documentation sites

### 2. Project Management (MDForm-based) 📊
**Location:** `project_management/`  
**Approach:** Parameterized forms with validation

Shows how to use forms for project planning, tracking, and team collaboration documents. Features:

- **Parameter validation** with types, enums, and constraints
- **Computed parameters** (dates, environment variables)
- **Nested data structures** for milestones and team information
- **Array parameters** for lists of tasks, risks, and team members
- **Multi-source parameters** from CLI, files, and defaults
- **Form reusability** across different project types

**Best for:** Project plans, meeting notes, status reports, team documentation

### 3. Blog/Article (Partial MDForms) ✍️
**Location:** `blog_article/`
**Approach:** Partial forms for specific sections

Demonstrates content publishing workflows where some sections are templated while others are manually written. Features:

- **Partial forms** that control only specific sections
- **Mixed content** combining templated and manual sections
- **Section-specific updates** without regenerating entire documents
- **Content reusability** with standardized author bios and references
- **Flexible publishing** with metadata extraction for CMS systems
- **Batch operations** for updating multiple articles

**Best for:** Blogs, articles, newsletters, content publishing, marketing materials

## Quick Start Guide

### Prerequisites
Ensure mddata is installed and available in your PATH:
```bash
uv sync --dev
# OR
pip install -e .
```

### Try the Examples

1. **Technical Documentation Example:**
```bash
cd use_cases_examples/technical_docs

# Generate schema from sample document
mddata schema infer sample_valid.md --output schema.json

# Create new document from data
mddata write --data sample_data.json --schema schema.json --output new_api_doc.md

# Validate document
mddata schema validate new_api_doc.md schema.json
```

2. **Project Management Example:**
```bash
cd use_cases_examples/project_management

# Fill form with parameters
mddata write --form project_form.yaml --params sample_params.json --output new_project.md

# Update project with CLI parameters  
mddata write --form project_form.yaml \
  -p project_name="Quick Fix" \
  -p project_type="internal" \
  -p priority="high" \
  -p end_date="2024-03-15" \
  -p team_size=3 \
  --output quick_project.md
```

3. **Blog/Article Example:**
```bash
cd use_cases_examples/blog_article

# Create article metadata
mddata write --form metadata_form.yaml \
  -p title="Getting Started with mddata" \
  -p author_name="Jane Blogger" \
  -p category="Tutorial" \
  -p tags="mddata,markdown,tutorial" \
  --output new_article.md

# Add author bio section
mddata write --form author_bio_form.yaml \
  --params author_data.json \
  --output temp_bio.md
```

## Common Patterns

### Schema vs Forms vs Partial Forms

| Approach | When to Use | Strengths | Trade-offs |
|----------|-------------|-----------|------------|
| **Schema** | Strict validation needed | Strong typing, validation | Less flexibility |
| **Forms** | Template-driven content | Parameterization, reusability | Requires predefined structure |
| **Partial Forms** | Mixed manual/templated content | Maximum flexibility | More complex workflow |

### Content Structure Patterns

1. **Hierarchical Sections** - Nested subsections for organized content
2. **Mixed Content** - Content both in sections and at document root
3. **Parameterized Content** - Dynamic content based on form parameters
4. **Computed Values** - Auto-generated dates, user info, etc.
5. **Validated Data** - Type checking and constraint validation

### Workflow Patterns

1. **Generate → Validate → Publish** (Schema-based)
2. **Fill → Customize → Update** (Form-based)  
3. **Template → Fill → Merge** (Partial forms)
4. **Extract → Process → Republish** (Data transformation)

## File Organization

Each example directory contains:

- `README.md` - Detailed usage guide with step-by-step instructions
- Schema/form files (`.json`, `.yaml`) - Structure definitions
- Sample data files - Example parameters and data
- Sample documents - Example outputs and valid documents
- Invalid examples - For testing validation failures

## Integration Examples

### CI/CD Pipeline
```bash
# Validate all documentation in CI
find docs/ -name "*.md" -exec mddata schema validate {} schema.json \;

# Generate documentation from data
mddata write --data api_spec.json --schema docs_schema.json --output api_docs.md
```

### Content Management
```bash
# Extract metadata for CMS
mddata extract frontmatter article.md --format json > metadata.json

# Bulk update author information
for article in articles/*.md; do
  mddata write --form author_bio_form.yaml --params new_author.json "$article"
done
```

### Documentation Automation
```bash
# Generate project docs from configuration
mddata write --form project_form.yaml --params project_config.json --output PROJECT.md

# Update version information across docs
mddata write set-property docs/*.md version "2.1.0"
```

## Best Practices

1. **Start Simple** - Begin with basic forms/schemas, add complexity as needed
2. **Validate Early** - Use schemas to catch errors during development
3. **Separate Concerns** - Use partial forms for different content types
4. **Version Your Templates** - Keep form/schema files in version control
5. **Document Your Patterns** - Include examples of valid data structures
6. **Test Invalid Cases** - Include examples that should fail validation
7. **Automate Common Tasks** - Script repetitive document operations

## Troubleshooting

### Common Issues

1. **Schema Validation Failures**
   - Check required fields are present
   - Verify data types match schema definitions
   - Ensure enum values are from allowed list

2. **Form Parameter Errors**
   - Validate parameter syntax (no spaces in CLI params)
   - Check required parameters are provided
   - Verify array/object parameter format

3. **Section Not Found**
   - Use `mddata info sections` to see available sections
   - Check section path syntax (use hyphens, not spaces)
   - Ensure parent sections exist before adding subsections

### Debug Commands

```bash
# Check document structure
mddata info summary document.md

# View available sections
mddata info sections document.md

# Validate against schema
mddata schema validate document.md schema.json

# Extract for debugging
mddata extract json document.md --pretty
```

## Next Steps

After exploring these examples:

1. **Adapt patterns** to your specific use cases
2. **Create custom schemas/forms** for your content types  
3. **Automate workflows** with scripts and CI/CD integration
4. **Share templates** across your team or organization
5. **Contribute examples** for other domains and use cases

For more advanced features, see the main [mddata documentation](../README.md) and [CLI reference](../docs/CLI_REFERENCE.md).