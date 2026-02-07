# Use Case Examples

End-to-end examples for three patterns.

| Directory | Pattern | Best for |
|-----------|---------|----------|
| [`technical_docs/`](technical_docs/) | Schema validation | API docs, specs, developer guides |
| [`project_management/`](project_management/) | Forms with parameter validation | Project plans, status reports |
| [`blog_article/`](blog_article/) | Partial forms (some sections templated, others manual) | Articles, newsletters |

## Quick try

```bash
# Schema-based
cd technical_docs
mddata schema infer sample_valid.md --output schema.json
mddata write --data sample_data.json --schema schema.json --output new_api_doc.md
mddata schema validate new_api_doc.md schema.json

# Form-based
cd ../project_management
mddata write --form project_form.yaml --params sample_params.json --output new_project.md

# Partial-form / mixed
cd ../blog_article
mddata write --form metadata_form.yaml \
  -p title="Getting Started" -p author_name="Jane" -p category=Tutorial \
  --output new_article.md
```

## When to use which

- **Schema** — strict structure, strong typing, no parameterization.
- **Forms** — reusable parameterized templates with validation.
- **Partial forms** — mix templated sections with hand-written content.
