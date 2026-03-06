from __future__ import annotations

import re
from typing import Any


def evaluate_operator(op: str, left: Any, right: Any) -> bool:
    normalized_op = op.lower()

    if normalized_op == "exists":
        return left is not None
    if normalized_op == "not_exists":
        return left is None

    if normalized_op == "equals":
        return left == right
    if normalized_op == "iequals":
        if left is None or right is None:
            return False
        return str(left).lower() == str(right).lower()

    if normalized_op == "contains":
        return _contains(left, right, case_insensitive=False)
    if normalized_op == "icontains":
        return _contains(left, right, case_insensitive=True)

    if normalized_op == "regex":
        if left is None or right is None:
            return False
        return re.search(str(right), str(left)) is not None

    if normalized_op == "in":
        return _in_operator(left, right)
    if normalized_op == "nin":
        return not _in_operator(left, right)

    if normalized_op == "gt":
        return _compare_numeric(left, right, lambda l, r: l > r)
    if normalized_op == "gte":
        return _compare_numeric(left, right, lambda l, r: l >= r)
    if normalized_op == "lt":
        return _compare_numeric(left, right, lambda l, r: l < r)
    if normalized_op == "lte":
        return _compare_numeric(left, right, lambda l, r: l <= r)
    if normalized_op == "between":
        return _between(left, right)

    raise ValueError(f"unsupported operator: {op}")


def _contains(left: Any, right: Any, case_insensitive: bool) -> bool:
    if left is None or right is None:
        return False

    if isinstance(left, list):
        haystack = [str(item) for item in left]
        needle = str(right)
        if case_insensitive:
            needle = needle.lower()
            haystack = [item.lower() for item in haystack]
        return needle in haystack

    left_text = str(left)
    right_text = str(right)
    if case_insensitive:
        left_text = left_text.lower()
        right_text = right_text.lower()
    return right_text in left_text


def _in_operator(left: Any, right: Any) -> bool:
    if not isinstance(right, (list, tuple, set)):
        return False

    right_values = set(right)
    if isinstance(left, list):
        return any(item in right_values for item in left)
    return left in right_values


def _compare_numeric(left: Any, right: Any, comparator: Any) -> bool:
    left_num = _to_float(left)
    right_num = _to_float(right)
    if left_num is None or right_num is None:
        return False
    return bool(comparator(left_num, right_num))


def _between(left: Any, right: Any) -> bool:
    left_num = _to_float(left)
    if left_num is None:
        return False

    min_value: Any = None
    max_value: Any = None

    if isinstance(right, (list, tuple)) and len(right) == 2:
        min_value, max_value = right
    elif isinstance(right, dict):
        min_value = right.get("min")
        max_value = right.get("max")
    else:
        return False

    min_num = _to_float(min_value)
    max_num = _to_float(max_value)
    if min_num is None or max_num is None:
        return False
    return min_num <= left_num <= max_num


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
