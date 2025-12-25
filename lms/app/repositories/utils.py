"""Repository utility helpers."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.inspection import inspect


def _json_serialize(value: Any) -> Any:
    """Convert non-JSON-serializable types to serializable ones."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        return [_json_serialize(item) for item in value]
    if isinstance(value, dict):
        return {k: _json_serialize(v) for k, v in value.items()}
    return value


def model_to_dict(model: Any) -> dict[str, Any]:
    """Serialize mapped column attributes to a JSON-safe plain dict."""
    mapper = inspect(model).mapper
    result: dict[str, Any] = {}
    for attr in mapper.column_attrs:
        key = attr.key
        value = getattr(model, key)
        result[key] = _json_serialize(value)
    return result


def dict_diff(
    old: dict[str, Any] | None, new: dict[str, Any] | None
) -> dict[str, Any] | None:
    if old is None or new is None:
        return None

    changed: dict[str, Any] = {}
    keys = set(old.keys()) | set(new.keys())
    for key in keys:
        if old.get(key) != new.get(key):
            changed[key] = {"old": old.get(key), "new": new.get(key)}

    return changed or None
