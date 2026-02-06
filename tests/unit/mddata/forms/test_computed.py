"""Tests for computed parameter resolution."""

import os
import re
from datetime import datetime

import pytest

from mddata.forms import ComputedParam


def test_get_date_param_format():
    """Test date parameter format."""
    date_str = ComputedParam.DATE.resolve()
    # Should be in YYYY-MM-DD format
    assert re.match(r'^\d{4}-\d{2}-\d{2}$', date_str)
    # Should be today's date
    expected = datetime.now().date().isoformat()
    assert date_str == expected


def test_get_time_param_format():
    """Test time parameter format."""
    time_str = ComputedParam.TIME.resolve()
    # Should be in HH:MM:SS format (may include microseconds)
    assert re.match(r'^\d{2}:\d{2}:\d{2}(\.\d+)?$', time_str)


def test_get_now_param_format():
    """Test now parameter format."""
    now_str = ComputedParam.NOW.resolve()
    # Should be ISO 8601 format
    assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$', now_str)


def test_get_env_param_existing_var():
    """Test getting existing environment variable."""
    test_var = "TEST_COMPUTED_VAR"
    test_value = "test_value_123"

    # Set environment variable
    os.environ[test_var] = test_value

    try:
        result = ComputedParam.resolve_env_param(f"env.{test_var}")
        assert result == test_value
    finally:
        # Clean up
        del os.environ[test_var]


def test_get_env_param_missing_var():
    """Test getting missing environment variable."""
    result = ComputedParam.resolve_env_param("env.NONEXISTENT_VAR_12345")
    assert result is None


def test_check_is_computed():
    """Test checking if parameter is computed."""
    assert ComputedParam.is_computed("date")
    assert ComputedParam.is_computed("time")
    assert ComputedParam.is_computed("now")
    assert ComputedParam.is_computed("env.USER")
    assert not ComputedParam.is_computed("custom_param")


def test_resolve_param_date():
    """Test resolving date parameter by name."""
    result = ComputedParam.resolve_param("date")
    assert re.match(r'^\d{4}-\d{2}-\d{2}$', result)


def test_resolve_param_time():
    """Test resolving time parameter by name."""
    result = ComputedParam.resolve_param("time")
    assert re.match(r'^\d{2}:\d{2}:\d{2}(\.\d+)?$', result)


def test_resolve_param_now():
    """Test resolving now parameter by name."""
    result = ComputedParam.resolve_param("now")
    assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$', result)


def test_resolve_param_env():
    """Test resolving environment variable parameter."""
    # Set a test env var
    os.environ["TEST_VAR"] = "test_value"
    try:
        result = ComputedParam.resolve_param("env.TEST_VAR")
        assert result == "test_value"
    finally:
        del os.environ["TEST_VAR"]


def test_resolve_param_unknown():
    """Test resolving unknown parameter raises error."""
    with pytest.raises(ValueError, match="Unknown computed parameter"):
        ComputedParam.resolve_param("unknown_param")


def test_from_name():
    """Test getting ComputedParam from name."""
    assert ComputedParam.from_name("date") == ComputedParam.DATE
    assert ComputedParam.from_name("time") == ComputedParam.TIME
    assert ComputedParam.from_name("now") == ComputedParam.NOW
    assert ComputedParam.from_name("unknown") is None


def test_is_env_param():
    """Test checking if parameter is environment variable."""
    assert ComputedParam.is_env_param("env.USER")
    assert ComputedParam.is_env_param("env.HOME")
    assert not ComputedParam.is_env_param("date")
    assert not ComputedParam.is_env_param("custom")
