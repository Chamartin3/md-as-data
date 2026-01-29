---
description: Validate markdown file against a schema
argument-hint: <markdown-file> <schema-file>
allowed-tools: Bash(mddata:*)
---

# Schema Validation

Validate **$1** against schema **$2**

## Run Validation

Execute schema validation with verbose output:
```bash
mddata schema validate "$1" "$2" --verbose
```

**Validation Checks:**
- Required frontmatter properties present
- Property types match schema
- Required sections exist
- Section content meets constraints
- Block types allowed in sections

## Schema Information

Display schema details:
```bash
mddata schema info "$2"
```

**If Validation Fails:**

1. **Check missing properties:**
   ```bash
   mddata info properties $1 --verbose
   ```

2. **Check section structure:**
   ```bash
   mddata info sections $1 --paths
   ```

3. **Fix issues and re-validate:**
   ```bash
   mddata modify set-property $1 <property> <value>
   mddata schema validate $1 $2 --verbose
   ```

**Generate Schema from Document:**
```bash
mddata schema infer $1 --output schema.json --pretty
```
