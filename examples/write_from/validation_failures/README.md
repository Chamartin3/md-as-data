# Validation Failure Examples

This directory contains examples that should FAIL with validation errors to demonstrate proper error handling.

## Example Categories

### 1. Missing Required Parameters
**Form:** `../forms/project-doc.yaml`
**Data:** `missing-required.json`

**Expected Error:** Missing required parameter 'project_name'

```bash
mddata write from \
  --form ../forms/project-doc.yaml \
  --data validation_failures/missing-required.json \
  -o /tmp/test.md
```

### 2. Invalid Enum Value
**Form:** `../forms/project-doc.yaml`
**Data:** `invalid-enum.json`

**Expected Error:** Value 'invalid_type' not in enum

```bash
mddata write from \
  --form ../forms/project-doc.yaml \
  --data validation_failures/invalid-enum.json \
  -o /tmp/test.md
```

### 3. String Too Short
**Form:** `../combined/api-doc-form.yaml`
**Data:** `string-too-short.json`

**Expected Error:** String length below minimum (min: 3)

```bash
mddata write from \
  --form ../combined/api-doc-form.yaml \
  --data validation_failures/string-too-short.json \
  -o /tmp/test.md
```

### 4. Pattern Mismatch
**Form:** `../combined/api-doc-form.yaml`
**Data:** `pattern-mismatch.json`

**Expected Error:** Value does not match pattern

```bash
mddata write from \
  --form ../combined/api-doc-form.yaml \
  --data validation_failures/pattern-mismatch.json \
  -o /tmp/test.md
```

## Usage

Run these commands to verify error handling:

```bash
cd examples/write_from

# Test all validation failures
for file in validation_failures/*.json; do
    echo "Testing: $file"
    mddata write from \
      --form forms/project-doc.yaml \
      --data "$file" \
      -o /tmp/test.md 2>&1 | head -3
    echo "---"
done
```

## Expected Behavior

- Clear error messages explaining what's wrong
- Identification of which parameter failed
- Helpful suggestions when possible
- No file created when validation fails
