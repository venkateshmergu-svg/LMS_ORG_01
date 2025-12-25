"""Unit tests for repository utilities."""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.utils import _json_serialize, dict_diff, model_to_dict


class TestJsonSerialize:
    """Tests for _json_serialize helper."""

    def test_serialize_none(self):
        """Should return None for None."""
        assert _json_serialize(None) is None

    def test_serialize_uuid(self):
        """Should convert UUID to string."""
        uid = uuid4()
        result = _json_serialize(uid)
        assert result == str(uid)
        assert isinstance(result, str)

    def test_serialize_datetime(self):
        """Should convert datetime to ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = _json_serialize(dt)
        assert result == "2024-01-15T10:30:00"

    def test_serialize_date(self):
        """Should convert date to ISO format."""
        d = date(2024, 1, 15)
        result = _json_serialize(d)
        assert result == "2024-01-15"

    def test_serialize_decimal(self):
        """Should convert Decimal to float."""
        dec = Decimal("10.50")
        result = _json_serialize(dec)
        assert result == 10.5
        assert isinstance(result, float)

    def test_serialize_enum(self):
        """Should extract enum value."""

        class TestEnum(Enum):
            VALUE = "test_value"

        result = _json_serialize(TestEnum.VALUE)
        assert result == "test_value"

    def test_serialize_bytes(self):
        """Should decode bytes to string."""
        data = b"hello world"
        result = _json_serialize(data)
        assert result == "hello world"

    def test_serialize_bytes_with_invalid_utf8(self):
        """Should handle invalid UTF-8 bytes gracefully."""
        data = b"\xff\xfe"
        result = _json_serialize(data)
        assert isinstance(result, str)

    def test_serialize_list(self):
        """Should serialize list items recursively."""
        uid = uuid4()
        items = [uid, date(2024, 1, 15), Decimal("5.0")]
        result = _json_serialize(items)

        assert result[0] == str(uid)
        assert result[1] == "2024-01-15"
        assert result[2] == 5.0

    def test_serialize_tuple(self):
        """Should serialize tuple items recursively."""
        items = (uuid4(), "plain")
        result = _json_serialize(items)

        assert isinstance(result, list)
        assert len(result) == 2

    def test_serialize_dict(self):
        """Should serialize dict values recursively."""
        uid = uuid4()
        data = {"id": uid, "date": date(2024, 1, 15)}
        result = _json_serialize(data)

        assert result["id"] == str(uid)
        assert result["date"] == "2024-01-15"

    def test_serialize_nested_structure(self):
        """Should handle nested structures."""
        data = {
            "users": [
                {"id": uuid4(), "created": datetime(2024, 1, 1, 12, 0)},
                {"id": uuid4(), "created": datetime(2024, 2, 1, 12, 0)},
            ]
        }
        result = _json_serialize(data)

        assert len(result["users"]) == 2
        assert isinstance(result["users"][0]["id"], str)
        assert isinstance(result["users"][0]["created"], str)

    def test_serialize_plain_types_unchanged(self):
        """Should pass through plain types unchanged."""
        assert _json_serialize("hello") == "hello"
        assert _json_serialize(42) == 42
        assert _json_serialize(3.14) == 3.14
        assert _json_serialize(True) is True


class TestModelToDict:
    """Tests for model_to_dict helper."""

    @patch("lms.app.repositories.utils.inspect")
    def test_converts_model_attributes(self, mock_inspect):
        """Should convert mapped column attributes to dict."""
        # Create mock model
        model = MagicMock()
        model.id = uuid4()
        model.name = "Test"
        model.created_at = datetime(2024, 1, 15, 10, 0)

        # Setup inspect mock
        mock_attr_id = MagicMock()
        mock_attr_id.key = "id"
        mock_attr_name = MagicMock()
        mock_attr_name.key = "name"
        mock_attr_created = MagicMock()
        mock_attr_created.key = "created_at"

        mock_mapper = MagicMock()
        mock_mapper.column_attrs = [mock_attr_id, mock_attr_name, mock_attr_created]
        mock_inspect.return_value.mapper = mock_mapper

        result = model_to_dict(model)

        assert "id" in result
        assert "name" in result
        assert "created_at" in result
        assert result["name"] == "Test"

    @patch("lms.app.repositories.utils.inspect")
    def test_serializes_values(self, mock_inspect):
        """Should serialize complex values."""
        uid = uuid4()
        model = MagicMock()
        model.id = uid

        mock_attr = MagicMock()
        mock_attr.key = "id"
        mock_mapper = MagicMock()
        mock_mapper.column_attrs = [mock_attr]
        mock_inspect.return_value.mapper = mock_mapper

        result = model_to_dict(model)

        # UUID should be converted to string
        assert result["id"] == str(uid)


class TestDictDiff:
    """Tests for dict_diff helper."""

    def test_returns_none_when_old_is_none(self):
        """Should return None when old dict is None."""
        result = dict_diff(None, {"key": "value"})
        assert result is None

    def test_returns_none_when_new_is_none(self):
        """Should return None when new dict is None."""
        result = dict_diff({"key": "value"}, None)
        assert result is None

    def test_returns_none_when_both_none(self):
        """Should return None when both dicts are None."""
        result = dict_diff(None, None)
        assert result is None

    def test_returns_none_when_equal(self):
        """Should return None when dicts are equal."""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 2}

        result = dict_diff(old, new)

        assert result is None

    def test_detects_changed_value(self):
        """Should detect changed values."""
        old = {"name": "Alice"}
        new = {"name": "Bob"}

        result = dict_diff(old, new)

        assert result is not None
        assert result["name"]["old"] == "Alice"
        assert result["name"]["new"] == "Bob"

    def test_detects_added_key(self):
        """Should detect added keys."""
        old = {"a": 1}
        new = {"a": 1, "b": 2}

        result = dict_diff(old, new)

        assert result is not None
        assert "b" in result
        assert result["b"]["old"] is None
        assert result["b"]["new"] == 2

    def test_detects_removed_key(self):
        """Should detect removed keys."""
        old = {"a": 1, "b": 2}
        new = {"a": 1}

        result = dict_diff(old, new)

        assert result is not None
        assert "b" in result
        assert result["b"]["old"] == 2
        assert result["b"]["new"] is None

    def test_detects_multiple_changes(self):
        """Should detect multiple changes."""
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 10, "b": 2, "c": 30}

        result = dict_diff(old, new)

        assert result is not None
        assert "a" in result
        assert "c" in result
        assert "b" not in result  # unchanged

    def test_handles_empty_dicts(self):
        """Should handle empty dicts."""
        result = dict_diff({}, {})
        assert result is None

        result = dict_diff({}, {"new": 1})
        assert result is not None
        assert "new" in result
