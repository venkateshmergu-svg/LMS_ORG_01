"""Repository utility helpers."""

from __future__ import annotations

from typing import Any

from sqlalchemy.inspection import inspect


def model_to_dict(model: Any) -> dict[str, Any]:
    """Serialize mapped column attributes to a plain dict."""
    mapper = inspect(model).mapper
    result: dict[str, Any] = {}
    for attr in mapper.column_attrs:
        key = attr.key
        result[key] = getattr(model, key)
    return result


def dict_diff(old: dict[str, Any] | None, new: dict[str, Any] | None) -> dict[str, Any] | None:
    if old is None or new is None:
        return None

    changed: dict[str, Any] = {}
    keys = set(old.keys()) | set(new.keys())
    for key in keys:
        if old.get(key) != new.get(key):
            changed[key] = {"old": old.get(key), "new": new.get(key)}

    return changed or None
