"""Unit tests for schema models."""


from md_as_data.models import BlockType
from md_as_data.validation.schema_models import (
    DocumentSchema,
    PropertySchema,
    PropertyValidationSchema,
    PropertyValidationType,
    SchemaFieldNames,
    SectionSchema,
    SectionValidationSchema,
    ValidationIssue,
    ValidationIssueTypes,
    ValidationLevel,
    ValidationResult,
    ValueType,
)


class TestValueType:
    """Test ValueType enum."""

    def test_value_type_values(self):
        """Test that ValueType enum has correct values."""
        assert ValueType.STRING == "str"
        assert ValueType.INTEGER == "int"
        assert ValueType.FLOAT == "float"
        assert ValueType.BOOLEAN == "bool"
        assert ValueType.LIST == "list"
        assert ValueType.DATE == "date"
        assert ValueType.DATETIME == "datetime"

    def test_value_type_from_string(self):
        """Test creating ValueType from string."""
        assert ValueType("str") == ValueType.STRING
        assert ValueType("int") == ValueType.INTEGER
        assert ValueType("float") == ValueType.FLOAT
        assert ValueType("bool") == ValueType.BOOLEAN
        assert ValueType("list") == ValueType.LIST


class TestValidationLevel:
    """Test ValidationLevel enum."""

    def test_validation_level_values(self):
        """Test that ValidationLevel enum has correct values."""
        assert ValidationLevel.STRICT == "strict"
        assert ValidationLevel.WARNINGS == "warnings"
        assert ValidationLevel.DISABLED == "disabled"

    def test_validation_level_from_string(self):
        """Test creating ValidationLevel from string."""
        assert ValidationLevel("strict") == ValidationLevel.STRICT
        assert ValidationLevel("warnings") == ValidationLevel.WARNINGS
        assert ValidationLevel("disabled") == ValidationLevel.DISABLED


class TestPropertyValidationType:
    """Test PropertyValidationType enum."""

    def test_validation_type_values(self):
        """Test that PropertyValidationType enum has correct values."""
        assert PropertyValidationType.MIN_LENGTH == "min_length"
        assert PropertyValidationType.MAX_LENGTH == "max_length"
        assert PropertyValidationType.MIN_VALUE == "min_value"
        assert PropertyValidationType.MAX_VALUE == "max_value"
        assert PropertyValidationType.REGEX == "regex"
        assert PropertyValidationType.ALLOWED_VALUES == "allowed_values"


class TestPropertyValidationSchema:
    """Test PropertyValidationSchema TypedDict."""

    def test_validation_schema_creation(self):
        """Test creating PropertyValidationSchema."""
        schema: PropertyValidationSchema = {
            "type": PropertyValidationType.MIN_LENGTH,
            "value": 5,
            "message": "Must be at least 5 characters",
        }
        assert schema["type"] == PropertyValidationType.MIN_LENGTH
        assert schema["value"] == 5
        assert schema["message"] == "Must be at least 5 characters"


class TestPropertySchema:
    """Test PropertySchema TypedDict."""

    def test_property_schema_creation(self):
        """Test creating PropertySchema with various fields."""
        schema: PropertySchema = {
            "type": ValueType.STRING,
            "required": True,
            "default": "default_value",
            "validations": [
                {
                    "type": PropertyValidationType.MIN_LENGTH,
                    "value": 1,
                    "message": "Cannot be empty",
                }
            ],
            "description": "A test property",
        }
        assert schema["type"] == ValueType.STRING
        assert schema["required"] is True
        assert schema["default"] == "default_value"
        assert len(schema["validations"]) == 1

    def test_property_schema_optional_fields(self):
        """Test PropertySchema with only required fields."""
        schema: PropertySchema = {"type": ValueType.INTEGER}
        assert schema["type"] == ValueType.INTEGER
        assert "required" not in schema
        assert "default" not in schema


class TestSectionValidationSchema:
    """Test SectionValidationSchema TypedDict."""

    def test_section_validation_schema_creation(self):
        """Test creating SectionValidationSchema."""
        schema: SectionValidationSchema = {
            "required": True,
            "max_blocks": 10,
            "min_blocks": 1,
            "allowed_content": [BlockType.PARAGRAPH, BlockType.LIST],
        }
        assert schema["required"] is True
        assert schema["max_blocks"] == 10
        assert schema["min_blocks"] == 1
        assert len(schema["allowed_content"]) == 2


class TestSectionSchema:
    """Test SectionSchema TypedDict."""

    def test_section_schema_creation(self):
        """Test creating SectionSchema with validation config."""
        schema: SectionSchema = {
            "validation": {
                "required": True,
                "min_blocks": 1,
                "max_blocks": 5,
                "allowed_content": [BlockType.PARAGRAPH],
            },
            "description": "Test section",
        }
        assert "validation" in schema
        assert schema["validation"]["required"] is True
        assert schema["validation"]["min_blocks"] == 1

    def test_section_schema_with_subsections(self):
        """Test SectionSchema with nested subsections."""
        schema: SectionSchema = {
            "validation": {"required": True},
            SchemaFieldNames.CHILDREN: {
                "intro": {
                    "validation": {"required": True, "min_blocks": 1}
                },
                "details": {
                    "validation": {"required": False, "max_blocks": 5}
                },
            },
        }
        assert SchemaFieldNames.CHILDREN in schema
        assert schema[SchemaFieldNames.CHILDREN]["intro"]["validation"]["required"] is True


class TestDocumentSchema:
    """Test DocumentSchema TypedDict."""

    def test_document_schema_creation(self):
        """Test creating complete DocumentSchema."""
        schema: DocumentSchema = {
            SchemaFieldNames.PROPERTIES: {
                "title": {"type": ValueType.STRING, "required": True},
                "version": {"type": ValueType.FLOAT, "default": 1.0},
            },
            SchemaFieldNames.SECTIONS: {
                "introduction": {
                    "validation": {"required": True, "min_blocks": 1}
                },
                "conclusion": {
                    "validation": {"required": False}
                },
            },
        }
        assert "title" in schema[SchemaFieldNames.PROPERTIES]
        assert schema[SchemaFieldNames.PROPERTIES]["title"]["type"] == ValueType.STRING
        assert "introduction" in schema[SchemaFieldNames.SECTIONS]
        # validation_level field removed - now passed to validator constructor


class TestValidationIssue:
    """Test ValidationIssue TypedDict."""

    def test_validation_issue_frontmatter(self):
        """Test creating frontmatter ValidationIssue."""
        issue: ValidationIssue = {
            "field_type": ValidationIssueTypes.PROPERTY,
            "field": "frontmatter.title",
            "message": "Required field missing",
            "expected": "str",
            "actual": None,
        }
        assert issue["field_type"] == ValidationIssueTypes.PROPERTY
        assert issue["field"] == "frontmatter.title"

    def test_validation_issue_section(self):
        """Test creating section ValidationIssue."""
        issue: ValidationIssue = {
            "field_type": ValidationIssueTypes.SECTION,
            "field": "sections.intro",
            "message": "Section has unexpected content",
            "expected": None,
            "actual": "code_block",
        }
        assert issue["field_type"] == ValidationIssueTypes.SECTION


class TestValidationResult:
    """Test ValidationResult TypedDict."""

    def test_validation_result_valid(self):
        """Test creating valid ValidationResult."""
        result: ValidationResult = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        result: ValidationResult = {
            "valid": False,
            "errors": [
                {
                    "field_type": ValidationIssueTypes.PROPERTY,
                    "field": "frontmatter.title",
                    "message": "Missing required field",
                    "expected": "str",
                    "actual": None,
                }
            ],
            "warnings": [],
        }
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field_type"] == ValidationIssueTypes.PROPERTY

