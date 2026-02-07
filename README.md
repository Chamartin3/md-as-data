# mddata

Treat markdown files as structured data. Parse, query, modify, validate, and generate markdown documents programmatically — from the CLI or Python.

## What it does

- **Parse** markdown + frontmatter into a structured object you can navigate
- **Query** sections by path (`intro.overview`) with fuzzy matching
- **Modify** frontmatter and sections in place
- **Extract** to JSON / YAML
- **Generate** markdown from data or from parameterized forms
- **Validate** documents against schemas (JSON or YAML)

## Install

```bash
uv sync --dev
```

## CLI

```bash
# Inspect
mddata info summary document.md
mddata info sections document.md

# Extract
mddata extract json document.md --pretty
mddata extract yaml document.md
mddata extract frontmatter document.md --format yaml

# Create / modify (unified write interface)
mddata write --data data.json --output new.md
mddata write --data changes.json existing.md         # modify (auto-detected)
mddata write --form template.yaml -p title="Hi" -o post.md
mddata write --schema schema.json --output template.md

# Granular edits
mddata write set-property document.md title "New Title"
mddata write set-section document.md intro "Updated content"
mddata write remove-property document.md draft

# Schemas
mddata schema infer document.md --output schema.json
mddata schema validate document.md schema.json
```

## Python

```python
from mddata import MarkdownFile

doc = MarkdownFile('document.md')

# Frontmatter
doc.mddata.title = "Updated"
doc.mddata.status = "published"

# Sections
query = doc.mddata.query_section('introduction')
if query.section:
    print(query.section.content)

doc.mddata.set_section('intro.overview', 'New overview')

# Blocks
paragraphs = doc.mddata.find_blocks(block_type='paragraph')

doc.save()
```

## Forms

Parameterized templates with typed validation. See [docs/MARKDOWN_FORMS.md](docs/MARKDOWN_FORMS.md).

```bash
mddata write --form post.yaml -p title="My Post" -p status=draft -o post.md
```

## Docs

- [docs/MARKDOWN_FORMS.md](docs/MARKDOWN_FORMS.md) — Forms & parameter validation
- [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) — Full CLI reference
- [examples/](examples/) — Runnable examples
