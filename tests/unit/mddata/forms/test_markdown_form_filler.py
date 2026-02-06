"""Tests for MarkdownFormFiller class."""

import pytest
from pathlib import Path
from mddata.models import MarkdownForm, MarkdownDataUpdate
from mddata.forms import MarkdownFormFiller


# Basic Filling Tests

def test_form_filler_creation():
    """Test creating a filler with valid form."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "required": True}}
    )
    filler = MarkdownFormFiller(form)
    assert filler.form is form
    assert filler.parameters == form.parameters


def test_form_filler_requires_markdown_form():
    """⭐ Test that filler requires MarkdownForm."""
    from mddata.models import MarkdownDataUpdate

    data = MarkdownDataUpdate(frontmatter={"title": "Test"})

    with pytest.raises(TypeError, match="Expected MarkdownForm"):
        MarkdownFormFiller(data)


def test_form_filler_rejects_data_update():
    """⭐ Test that plain dict is rejected."""
    with pytest.raises(TypeError):
        MarkdownFormFiller({"some": "dict"})


def test_form_filler_returns_data_update():
    """⭐ Test that fill returns MarkdownDataUpdate."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "required": True}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"title": "Test"})

    # Result should be MarkdownDataUpdate, not MarkdownForm
    assert isinstance(result, MarkdownDataUpdate)
    assert not isinstance(result, MarkdownForm)
    # Parameters should be empty (removed during filling)
    assert result.parameters == {}


def test_fill_with_cli_params():
    """Test filling with CLI parameters."""
    form = MarkdownForm(
        parameters={"title": {"type": "str"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(cli_params=["title=CLI Title"])

    assert result.frontmatter["title"] == "CLI Title"


def test_fill_with_params_dict():
    """Test filling with parameter dictionary."""
    form = MarkdownForm(
        parameters={"title": {"type": "str"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"title": "Dict Title"})

    assert result.frontmatter["title"] == "Dict Title"


def test_fill_with_params_file(tmp_path):
    """Test filling with parameter file."""
    import json

    # Create temp params file
    params_file = tmp_path / "params.json"
    params_file.write_text(json.dumps({"title": "File Title"}))

    form = MarkdownForm(
        parameters={"title": {"type": "str"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_file=str(params_file))

    assert result.frontmatter["title"] == "File Title"


# Parameter Resolution Precedence Tests

def test_precedence_form_defaults_lowest():
    """Test that form defaults have lowest precedence."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "default": "Default"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill()

    assert result.frontmatter["title"] == "Default"


def test_precedence_data_overrides_defaults():
    """Test that params_dict overrides defaults."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "default": "Default"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"title": "Data"})

    assert result.frontmatter["title"] == "Data"


def test_precedence_cli_params_highest():
    """Test that CLI params have highest precedence."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "default": "Default"}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(
        params_dict={"title": "Data"},
        cli_params=["title=CLI"]
    )

    assert result.frontmatter["title"] == "CLI"


def test_precedence_all_three_sources():
    """⭐ Test complete precedence chain: defaults < file < dict < CLI."""
    form = MarkdownForm(
        parameters={
            "title": {"type": "str", "default": "Default"},
            "author": {"type": "str", "default": "Unknown"},
            "status": {"type": "str", "default": "draft"},
        },
        frontmatter={
            "title": "{title}",
            "author": "{author}",
            "status": "{status}",
        }
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(
        params_dict={"title": "Dict Title", "author": "Dict Author"},
        cli_params=["title=CLI Title"]
    )

    # CLI overrides dict
    assert result.frontmatter["title"] == "CLI Title"
    # Dict used when no CLI override
    assert result.frontmatter["author"] == "Dict Author"
    # Default used when nothing else provided
    assert result.frontmatter["status"] == "draft"


def test_computed_parameters_resolved():
    """Test that computed parameters are resolved."""
    form = MarkdownForm(
        parameters={"date": {"type": "str", "default": "computed:date"}},
        frontmatter={"created": "{date}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill()

    # Should resolve to actual date
    import re
    assert re.match(r"\d{4}-\d{2}-\d{2}", result.frontmatter["created"])


def test_environment_variables_resolved():
    """Test that environment variables are resolved."""
    import os
    os.environ["TEST_VAR"] = "test_value"

    form = MarkdownForm(
        parameters={"user": {"type": "str", "default": "env.TEST_VAR"}},
        frontmatter={"user": "{user}"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill()

    assert result.frontmatter["user"] == "test_value"


# Validation Tests

def test_validate_required_parameters():
    """Test validation of required parameters."""
    form = MarkdownForm(
        parameters={"title": {"type": "str", "required": True}},
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)

    with pytest.raises(Exception, match="required"):
        filler.fill(params_dict={})


def test_validate_parameter_types():
    """Test type validation."""
    form = MarkdownForm(
        parameters={"count": {"type": "int"}},
        frontmatter={"count": "{count}"}
    )
    filler = MarkdownFormFiller(form)

    # Should accept int
    result = filler.fill(params_dict={"count": 42})
    assert result.frontmatter["count"] == "42"


def test_validate_string_constraints():
    """Test string min/max validation."""
    form = MarkdownForm(
        parameters={
            "title": {
                "type": "str",
                "min": 5,
                "max": 20,
            }
        },
        frontmatter={"title": "{title}"}
    )
    filler = MarkdownFormFiller(form)

    # Valid length
    result = filler.fill(params_dict={"title": "Valid Title"})
    assert result.frontmatter["title"] == "Valid Title"

    # Too short - should fail
    with pytest.raises(Exception):
        filler.fill(params_dict={"title": "Hi"})

    # Too long - should fail
    with pytest.raises(Exception):
        filler.fill(params_dict={"title": "This is way too long for the limit"})


def test_validate_numeric_constraints():
    """Test numeric min/max validation."""
    form = MarkdownForm(
        parameters={
            "age": {
                "type": "int",
                "min": 0,
                "max": 120,
            }
        },
        frontmatter={"age": "{age}"}
    )
    filler = MarkdownFormFiller(form)

    # Valid
    result = filler.fill(params_dict={"age": 25})
    assert result.frontmatter["age"] == "25"

    # Too low
    with pytest.raises(Exception):
        filler.fill(params_dict={"age": -5})

    # Too high
    with pytest.raises(Exception):
        filler.fill(params_dict={"age": 200})


def test_validate_enum_strict_mode():
    """Test strict enum validation."""
    form = MarkdownForm(
        parameters={
            "status": {
                "type": "str",
                "enum": ["draft", "published", "archived"],
                "enum_strict": True,
            }
        },
        frontmatter={"status": "{status}"}
    )
    filler = MarkdownFormFiller(form)

    # Valid enum value
    result = filler.fill(params_dict={"status": "published"})
    assert result.frontmatter["status"] == "published"

    # Invalid enum value - should fail
    with pytest.raises(Exception):
        filler.fill(params_dict={"status": "invalid"})


def test_validate_enum_non_strict_mode():
    """Test non-strict enum validation (warnings only)."""
    form = MarkdownForm(
        parameters={
            "status": {
                "type": "str",
                "enum": ["draft", "published"],
                "enum_strict": False,
            }
        },
        frontmatter={"status": "{status}"}
    )
    filler = MarkdownFormFiller(form)

    # Should accept non-enum value and issue a warning
    with pytest.warns(UserWarning, match="value 'custom' not in enum values"):
        result = filler.fill(params_dict={"status": "custom"})
    assert result.frontmatter["status"] == "custom"


def test_validate_array_constraints():
    """Test array validation constraints."""
    form = MarkdownForm(
        parameters={
            "tags": {
                "type": "array",
                "min_items": 1,
                "max_items": 5,
                "unique_items": True,
            }
        },
        frontmatter={"tags": "{tags}"}
    )
    filler = MarkdownFormFiller(form)

    # Valid array
    result = filler.fill(params_dict={"tags": ["python", "coding"]})
    assert result.frontmatter["tags"] == "python, coding"

    # Too few items
    with pytest.raises(Exception):
        filler.fill(params_dict={"tags": []})

    # Too many items
    with pytest.raises(Exception):
        filler.fill(params_dict={"tags": ["a", "b", "c", "d", "e", "f"]})

    # Duplicate items (if unique_items enforced)
    with pytest.raises(Exception):
        filler.fill(params_dict={"tags": ["python", "python"]})


def test_validate_array_item_enum():
    """Test array item enum validation."""
    form = MarkdownForm(
        parameters={
            "langs": {
                "type": "array",
                "item_enum": ["python", "javascript", "rust"],
                "item_enum_strict": True,
            }
        },
        frontmatter={"langs": "{langs}"}
    )
    filler = MarkdownFormFiller(form)

    # Valid
    result = filler.fill(params_dict={"langs": ["python", "rust"]})
    assert result.frontmatter["langs"] == "python, rust"

    # Invalid item
    with pytest.raises(Exception):
        filler.fill(params_dict={"langs": ["python", "cobol"]})


# def test_validate_array_item_pattern():
#     """Test array item pattern validation."""
#     # TODO: Implement item_pattern validation
#     pass


# Placeholder Substitution Tests

def test_simple_placeholder_substitution():
    """Test basic placeholder substitution."""
    form = MarkdownForm(
        parameters={"name": {"type": "str"}},
        frontmatter={"greeting": "Hello {name}!"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"name": "World"})

    assert result.frontmatter["greeting"] == "Hello World!"


def test_nested_placeholder_substitution():
    """Test nested placeholder substitution."""
    form = MarkdownForm(
        parameters={
            "first": {"type": "str"},
            "last": {"type": "str"},
        },
        frontmatter={
            "author": {
                "name": "{first} {last}",
                "display": "{first} {last}"
            }
        }
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"first": "John", "last": "Doe"})

    assert result.frontmatter["author"]["name"] == "John Doe"


def test_array_placeholder_formatting():
    """Test placeholder substitution in arrays."""
    form = MarkdownForm(
        parameters={"tag": {"type": "str"}},
        frontmatter={"tags": ["{tag}-1", "{tag}-2"]}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"tag": "python"})

    assert result.frontmatter["tags"] == ["python-1", "python-2"]


def test_escaped_placeholders():
    """Test that escaped placeholders are preserved."""
    form = MarkdownForm(
        parameters={"name": {"type": "str"}},
        frontmatter={"text": "Use \\{name} for template"}
    )
    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"name": "value"})

    # Escaped placeholders should not be substituted
    assert "{name}" in result.frontmatter["text"]


def test_missing_placeholder_error():
    """Test error when placeholder value not provided."""
    form = MarkdownForm(
        parameters={"name": {"type": "str", "required": True}},
        frontmatter={"greeting": "Hello {name}!"}
    )
    filler = MarkdownFormFiller(form)

    with pytest.raises(Exception):
        filler.fill(params_dict={})


# Backward Compatibility Tests (removed - no longer supporting TemplateFiller alias)


def test_old_parameter_definition_alias_works():
    """⭐ Test that ParameterDefinition alias works."""
    from mddata.models import ParameterDefinition

    form = MarkdownForm(
        parameters={
            "title": ParameterDefinition(type="str", required=True)
        },
        frontmatter={"title": "{title}"}
    )

    filler = MarkdownFormFiller(form)
    result = filler.fill(params_dict={"title": "Test"})

    assert result.frontmatter["title"] == "Test"