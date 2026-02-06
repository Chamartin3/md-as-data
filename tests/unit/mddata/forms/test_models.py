"""Tests for template TypedDict models."""

import pytest

from mddata.models import (
    MarkdownDataUpdate,
    ParameterDefinition,
    ResolvedParameters,
)
from mddata.models import ParameterType


def test_parameter_type_enum_values():
    """Test ParameterType enum has expected values."""
    assert ParameterType.STR == "str"
    assert ParameterType.INT == "int"
    assert ParameterType.FLOAT == "float"
    assert ParameterType.BOOL == "bool"
    assert ParameterType.DATE == "date"
    assert ParameterType.ARRAY == "array"

    # Test all values are present
    expected = {"str", "int", "float", "bool", "date", "array"}
    assert set(ParameterType) == expected


def test_parameter_definition_structure():
    """Test parameter definition structure (TypedDict)."""
    # Valid parameter definition
    param: ParameterDefinition = {
        "type": ParameterType.STR,
        "required": True,
        "description": "A string parameter",
    }
    assert param["type"] == ParameterType.STR
    assert param["required"] is True
    assert param["description"] == "A string parameter"

    # Valid with constraints
    param2: ParameterDefinition = {
        "type": ParameterType.INT,
        "min": 1,
        "max": 100,
        "default": 50,
    }
    assert param2["min"] == 1
    assert param2["max"] == 100
    assert param2["default"] == 50


def test_parameter_default_values():
    """Test parameter default values."""
    # String default
    param: ParameterDefinition = {"type": ParameterType.STR, "default": "test"}
    assert param["default"] == "test"

    # Int default
    param2: ParameterDefinition = {"type": ParameterType.INT, "default": 42}
    assert param2["default"] == 42

    # Bool default
    param3: ParameterDefinition = {"type": ParameterType.BOOL, "default": True}
    assert param3["default"] is True

    # Array default
    param4: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "default": [1, 2, 3],
    }
    assert param4["default"] == [1, 2, 3]

    # Computed parameter syntax
    param5: ParameterDefinition = {
        "type": ParameterType.STR,
        "default": "{env.USER}",
    }
    assert param5["default"] == "{env.USER}"


def test_parameter_constraints():
    """Test parameter constraints."""
    # Constraints for int
    param: ParameterDefinition = {"type": ParameterType.INT, "min": 0, "max": 100}
    assert param["min"] == 0
    assert param["max"] == 100

    # Constraints for str
    param2: ParameterDefinition = {"type": ParameterType.STR, "pattern": r"^\w+$"}
    assert param2["pattern"] == r"^\w+$"

    # Constraints for array
    param3: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_type": ParameterType.STR,
    }
    assert param3["item_type"] == ParameterType.STR


def test_template_file_structure():
    """Test MarkdownDataUpdate structure with parameters."""
    template = MarkdownDataUpdate(
        frontmatter={"title": "Test"},
        parameters={
            "name": {"type": ParameterType.STR, "required": True},
            "count": {"type": ParameterType.INT, "default": 5},
        },
    )

    assert template.parameters is not None
    assert "name" in template.parameters
    assert template.parameters["name"]["type"] == ParameterType.STR
    assert template.frontmatter["title"] == "Test"


def test_template_file_changes_structure():
    """Test MarkdownDataUpdate with section updates."""
    from mddata.models import SectionUpdate

    template = MarkdownDataUpdate(
        frontmatter={"title": "{title}", "date": "{date}"},
        sections=[
            SectionUpdate(id="intro", content="Content with {param}"),
            SectionUpdate(id="body", content="More {content}", policy="replace"),
        ],
    )

    assert template.frontmatter is not None
    assert template.frontmatter["title"] == "{title}"
    assert len(template.sections) == 2
    assert template.sections[0].id == "intro"
    assert template.sections[0].content == "Content with {param}"


def test_resolved_parameters_type():
    """Test resolved parameters is just a dict."""
    # ResolvedParameters is now just an alias for dict
    params: ResolvedParameters = {"name": "value", "count": 42, "active": True}

    assert params["name"] == "value"
    assert params["count"] == 42
    assert params["active"] is True


def test_array_parameter_structure():
    """Test array parameter with item type."""
    param: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_type": ParameterType.STR,
        "default": ["a", "b", "c"],
    }

    assert param["type"] == ParameterType.ARRAY
    assert param["item_type"] == ParameterType.STR
    assert param["default"] == ["a", "b", "c"]


def test_computed_param_in_default():
    """Test computed parameter in default value."""
    param: ParameterDefinition = {
        "type": ParameterType.STR,
        "default": "{now}",
        "required": False,
    }

    assert param["default"] == "{now}"
    assert param["required"] is False
