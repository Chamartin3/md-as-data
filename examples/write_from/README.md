# `mddata write` Examples

Combinations of forms, data, and schemas.

```
write_from/
├── combined/      # form + data + schema
├── data/          # complete data files
├── forms/         # parameterized templates
├── schemas/       # validation schemas
└── validation_failures/  # inputs that should fail
```

## Form + data

```bash
mddata write --form forms/project-doc.yaml --data data/project-doc-params.json --output project-doc.md

mddata write --form forms/project-doc.yaml \
  -p project_name=MyProject -p project_type=library \
  -p version=1.0.0 -p maintainer="Jane Doe" \
  --output project-doc.md

mddata write --form forms/blog-post.yaml --data data/blog-post-params.json --output blog-post.md
```

## Data + schema

```bash
mddata schema validate data/user-profile.json schemas/user-profile.json
mddata write --data data/user-profile.json --schema schemas/user-profile.json --output user-profile.md

mddata write --data data/product-spec.yaml --schema schemas/product-spec.yaml --output product-spec.md
```

## Form + data + schema

```bash
mddata write --form combined/api-doc-form.yaml \
  --data data/api-doc-params.json \
  --schema schemas/api-doc-validation.json \
  --output api-doc.md

mddata write --form combined/meeting-agenda-form.yaml \
  --data data/meeting-agenda-params.json \
  --schema schemas/meeting-agenda-validation.json \
  --output meeting-agenda.md
```

## Validation failures

See [validation_failures/](validation_failures/) for inputs designed to fail.
