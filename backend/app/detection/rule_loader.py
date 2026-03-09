from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from app.detection.types import RuleDefinition


def load_rules(ruleset_id: str | None = None, rules_dir: Path | None = None) -> list[RuleDefinition]:
    base_dir = rules_dir or resolve_rules_dir()
    if not base_dir.exists():
        raise FileNotFoundError(f"rules directory not found: {base_dir}")

    files = sorted([*base_dir.glob("*.yaml"), *base_dir.glob("*.yml")])
    rules: list[RuleDefinition] = []
    for file_path in files:
        raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"rule file {file_path} must contain a top-level object")

        if not _matches_ruleset(raw, ruleset_id):
            continue

        rule = _parse_rule(raw, file_path)
        if rule.enabled:
            rules.append(rule)

    return sorted(rules, key=lambda rule: rule.id)


def resolve_rules_dir() -> Path:
    env_value = os.getenv("RULES_DIR")
    if env_value:
        return Path(env_value)

    project_root = Path(__file__).resolve().parents[3]
    candidates = [Path("/rules"), project_root / "rules"]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[-1]


def _matches_ruleset(raw_rule: dict[str, Any], ruleset_id: str | None) -> bool:
    if not ruleset_id or ruleset_id in {"all", "default"}:
        return True

    explicit = raw_rule.get("ruleset_id") or raw_rule.get("ruleset")
    if explicit is None:
        return True

    if isinstance(explicit, str):
        return explicit == ruleset_id
    if isinstance(explicit, list):
        return ruleset_id in explicit

    return False


def _parse_rule(raw: dict[str, Any], file_path: Path) -> RuleDefinition:
    required = ["id", "name", "severity", "detect", "output"]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"rule file {file_path} missing required fields: {', '.join(missing)}")

    detect = raw["detect"]
    output = raw["output"]

    if not isinstance(detect, dict):
        raise ValueError(f"rule file {file_path} detect block must be an object")
    if not isinstance(output, dict):
        raise ValueError(f"rule file {file_path} output block must be an object")

    detect_type = str(detect.get("type", "")).strip().lower()
    if detect_type not in {"single", "sequence"}:
        raise ValueError(f"rule {raw['id']} has invalid detect.type: {detect_type}")

    if detect_type == "single" and "where" not in detect:
        raise ValueError(f"rule {raw['id']} single detect must include where")

    if detect_type == "sequence":
        stages = detect.get("stages")
        if not isinstance(stages, list) or len(stages) != 2:
            raise ValueError(f"rule {raw['id']} sequence detect must include exactly 2 stages")
        if "window_seconds" not in detect:
            raise ValueError(f"rule {raw['id']} sequence detect must include window_seconds")

    evidence = raw.get("evidence") or {}
    include_fields = evidence.get("include_fields") if isinstance(evidence, dict) else []
    if not isinstance(include_fields, list):
        include_fields = []

    return RuleDefinition(
        id=str(raw["id"]),
        name=str(raw["name"]),
        description=str(raw.get("description", "")),
        severity=str(raw["severity"]),
        enabled=bool(raw.get("enabled", True)),
        log_sources=[str(item) for item in raw.get("log_sources", [])],
        tags=[str(item) for item in raw.get("tags", [])],
        version=int(raw.get("version", 1)),
        detect_type=detect_type,
        detect=detect,
        output=output,
        evidence_fields=[str(field) for field in include_fields],
    )
