from __future__ import annotations

from app.detection.operators import evaluate_operator


def test_string_and_set_operators() -> None:
    assert evaluate_operator("equals", "abc", "abc")
    assert evaluate_operator("iequals", "ABC", "abc")
    assert evaluate_operator("contains", "hello-world", "world")
    assert evaluate_operator("icontains", "Hello-World", "world")
    assert evaluate_operator("regex", "evil-example.com", "evil-example\\.com")
    assert evaluate_operator("in", "windows", ["dns", "windows"])
    assert evaluate_operator("nin", "linux", ["dns", "windows"])


def test_existence_and_numeric_operators() -> None:
    assert evaluate_operator("exists", "value", None)
    assert evaluate_operator("not_exists", None, None)
    assert evaluate_operator("gt", 10, 5)
    assert evaluate_operator("gte", 5, 5)
    assert evaluate_operator("lt", 2, 5)
    assert evaluate_operator("lte", 5, 5)
    assert evaluate_operator("between", 5, [1, 10])
