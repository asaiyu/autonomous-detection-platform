from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.detection.rule_loader import load_rules

router = APIRouter()


class RuleSummary(BaseModel):
    id: str
    name: str
    severity: str
    version: int
    detect_type: str
    enabled: bool


@router.get("", response_model=list[RuleSummary])
def list_rules() -> list[RuleSummary]:
    rules = load_rules()
    return [
        RuleSummary(
            id=rule.id,
            name=rule.name,
            severity=rule.severity,
            version=rule.version,
            detect_type=rule.detect_type,
            enabled=rule.enabled,
        )
        for rule in rules
    ]


@router.get("/{rule_id}")
def get_rule(rule_id: str) -> dict:
    rules = load_rules()
    for rule in rules:
        if rule.id == rule_id:
            return {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity,
                "enabled": rule.enabled,
                "log_sources": rule.log_sources,
                "tags": rule.tags,
                "version": rule.version,
                "detect": rule.detect,
                "output": rule.output,
                "evidence_include_fields": rule.evidence_fields,
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="rule not found")
