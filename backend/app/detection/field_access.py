from __future__ import annotations

from typing import Any


def get_field(event: dict[str, Any], path: str) -> Any:
    cursor: Any = event
    for part in path.split("."):
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(part)
    return cursor
