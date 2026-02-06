# Blog/Article Use Case (Partial MDForms)

This example demonstrates using mddata with partial forms for content publishing workflows.

## Overview

This use case shows how to:
- Use partial forms to fill specific sections of existing documents
- Combine manual content with templated fragments
- Handle author bios, references, and metadata consistently
- Support multiple content types (blog posts, tutorials, news articles)
- Allow content outside of form-controlled sections

## Files in this example

- `base_article.md` - Base article template with manual content
- `author_bio_form.yaml` - Partial form for author bio sections
- `references_form.yaml` - Partial form for references and citations
- `metadata_form.yaml` - Form for article metadata and frontmatter
- `author_data.json` - Sample author information
- `tech_article_data.json` - Example technical article data
- `sample_complete.md` - Example of completed article

## Form Structure

This example uses three separate partial forms:

### 1. Metadata Form (`metadata_form.yaml`)
Controls article frontmatter:
- `title`, `subtitle`, `author_name`
- `publish_date`, `tags`, `category`
- `estimated_reading_time`, `featured`

### 2. Author Bio Form (`author_bio_form.yaml`)  
Generates author information section:
- `author_name`, `author_title`, `author_company`
- `author_bio`, `social_links`, `profile_image`

### 3. References Form (`references_form.yaml`)
Creates citations and references:
- `references` (array of citation objects)
- `further_reading` (array of links)
- `related_articles` (array of internal links)

## Step-by-step Usage

### 1. Create Base Article with Metadata

```bash
# Fill article metadata using form
mddata write --form metadata_form.yaml \
  -p title="Advanced Python Patterns" \
  -p subtitle="Design patterns for scalable applications" \
  -p author_name="Alice Developer" \
  -p category="Programming" \
  -p tags="python,design-patterns,architecture" \
  -p estimated_reading_time=15 \
  --output new_article.md

# View the created structure
mddata info summary new_article.md
```

### 2. Add Manual Content

```bash
# Add main content sections manually
mddata write set-section new_article.md "introduction" \
  "In this article, we'll explore advanced Python design patterns that can help you build more maintainable and scalable applications."

mddata write set-section new_article.md "main-content" \
  "## Singleton Pattern\n\nThe Singleton pattern ensures a class has only one instance...\n\n## Factory Pattern\n\nThe Factory pattern provides an interface for creating objects..."

mddata write set-section new_article.md "conclusion" \
  "These patterns, when used appropriately, can significantly improve your Python code's organization and maintainability."
```

### 3. Fill Author Bio Section

```bash
# Add author bio using partial form
mddata write --form author_bio_form.yaml \
  --params author_data.json \
  --output temp_bio.md

# Extract author bio section and add to main article
mddata extract json temp_bio.md --section author-bio | \
  mddata write --data - set-section new_article.md "author-bio"

# Or use direct section filling (if supported)
mddata write fill-section new_article.md "author-bio" \
  --form author_bio_form.yaml \
  --params author_data.json
```

### 4. Add References and Citations

```bash
# Create references section
mddata write --form references_form.yaml \
  -p 'references=[{"title":"Effective Python","author":"Brett Slatkin","year":"2019"},{"title":"Clean Code","author":"Robert Martin","year":"2008"}]' \
  -p 'further_reading=["https://realpython.com/","https://python.org/dev/peps/"]' \
  --output temp_refs.md

# Add references to main article
mddata write merge new_article.md temp_refs.md --policy append

# Clean up temporary file
rm temp_refs.md
```

### 5. Update Existing Articles

```bash
# Update metadata for existing article
mddata write --form metadata_form.yaml \
  -p publish_date="2024-01-25" \
  -p featured=true \
  existing_article.md

# Add new author bio to existing article
mddata write fill-section existing_article.md "author-bio" \
  --form author_bio_form.yaml \
  --params new_author.json

# Append additional references
mddata write fill-section existing_article.md "references" \
  --form references_form.yaml \
  -p 'references=[{"title":"New Book","author":"New Author","year":"2024"}]' \
  --policy append
```

### 6. Generate Multiple Articles from Templates

```bash
# Create technical tutorial
mddata write --form metadata_form.yaml \
  --params tech_article_data.json \
  --output tech_tutorial.md

# Create news article
mddata write --form metadata_form.yaml \
  -p title="Industry News Update" \
  -p category="News" \
  -p author_name="News Team" \
  -p tags="news,industry,updates" \
  -p estimated_reading_time=5 \
  --output news_article.md
```

### 7. Validate and Extract

```bash
# Extract article metadata for CMS
mddata extract frontmatter new_article.md --format json --output article_meta.json

# Extract specific sections for preview
mddata extract json new_article.md --section introduction --section conclusion

# Validate article structure
mddata info sections new_article.md
```

### 8. Batch Processing

```bash
# Update all articles with new author bio
for article in *.md; do
  mddata write fill-section "$article" "author-bio" \
    --form author_bio_form.yaml \
    --params updated_author.json
done

# Extract all article metadata
for article in *.md; do
  mddata extract frontmatter "$article" --format json >> all_metadata.json
done
```

## Key Features Demonstrated

1. **Partial Forms**: Forms that control only specific sections
2. **Mixed Content**: Combination of templated and manual content  
3. **Section-Specific Filling**: Update individual sections with forms
4. **Content Reusability**: Reuse forms across different articles
5. **Flexible Updates**: Modify existing content without regenerating
6. **Multi-Source Content**: CLI, files, and manual editing combined
7. **Batch Operations**: Process multiple documents efficiently
8. **Content Extraction**: Export sections for other systems

## Content Workflow

1. **Create Base**: Use metadata form for frontmatter and structure
2. **Add Content**: Write main content manually or from other sources
3. **Fill Sections**: Use partial forms for standardized sections
4. **Update**: Modify specific sections without affecting others
5. **Publish**: Extract metadata and content for publishing systems

This approach provides maximum flexibility while maintaining consistency in templated sections.