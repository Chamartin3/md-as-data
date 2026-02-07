# Blog Article — Partial Forms

Mix templated sections (metadata, author bio, references) with hand-written content.

## Files

- `base_article.md` — base article with manual content
- `metadata_form.yaml` — frontmatter form
- `author_bio_form.yaml` — author bio section form
- `references_form.yaml` — references/citations form
- `author_data.json`, `tech_article_data.json` — sample params
- `sample_complete.md` — example finished article

## Workflow

```bash
# 1. Create base from metadata form
mddata write --form metadata_form.yaml \
  -p title="Advanced Python Patterns" \
  -p author_name="Alice Developer" \
  -p category=Programming \
  -p tags="python,design-patterns" \
  --output new_article.md

# 2. Add manual content
mddata write set-section new_article.md introduction "In this article..."
mddata write set-section new_article.md main-content "## Singleton\n\n..."
mddata write set-section new_article.md conclusion "These patterns..."

# 3. Fill author bio from a separate form
mddata write fill-section new_article.md author-bio \
  --form author_bio_form.yaml --params author_data.json

# 4. Append references
mddata write fill-section new_article.md references \
  --form references_form.yaml \
  -p 'references=[{"title":"Effective Python","author":"Slatkin","year":"2019"}]' \
  --policy append

# 5. Update metadata on an existing article
mddata write --form metadata_form.yaml -p featured=true existing_article.md

# 6. Extract for CMS
mddata extract frontmatter new_article.md --format json --output meta.json
```
