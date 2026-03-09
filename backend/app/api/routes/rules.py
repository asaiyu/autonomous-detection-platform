from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import yaml

from app.db.session import get_db
from app.detection.rule_loader import load_rules, resolve_rules_dir
from app.models.rule_proposal import RuleProposal
from app.models.ruleset import Ruleset
from app.schemas.rule import RuleCreateRequest, RuleCreateResponse

router = APIRouter()


class RuleSummary(BaseModel):
    id: str
    name: str
    severity: str
    version: int
    detect_type: str
    enabled: bool


@router.get("", response_model=list[RuleSummary])
def list_rules(ruleset_id: Optional[str] = Query(None)) -> list[RuleSummary]:
    rules = load_rules(ruleset_id=ruleset_id)
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
def get_rule(rule_id: str, ruleset_id: Optional[str] = Query(None)) -> dict:
    rules = load_rules(ruleset_id=ruleset_id)
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


@router.post("", response_model=RuleCreateResponse, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleCreateRequest, db: Session = Depends(get_db)) -> RuleCreateResponse:
    if payload.mode == "ruleset":
        parsed_rule = _parse_rule_yaml(payload.rule_yaml, payload.rule_id)
        rules_dir = _resolve_writable_rules_dir()
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_path = rules_dir / f"{payload.rule_id}.yaml"
        rule_path.write_text(yaml.safe_dump(parsed_rule, sort_keys=False), encoding="utf-8")

        ruleset = db.query(Ruleset).filter(Ruleset.ruleset_id == payload.ruleset_id).first()
        if ruleset is None:
            ruleset = Ruleset(
                ruleset_id=payload.ruleset_id,
                name=payload.ruleset_id,
                version=str(payload.rule_version),
                note=payload.ruleset_note,
                is_active=True,
                rules={"rule_ids": [payload.rule_id]},
            )
            db.add(ruleset)
        else:
            existing_rule_ids = []
            if isinstance(ruleset.rules, dict):
                raw = ruleset.rules.get("rule_ids")
                if isinstance(raw, list):
                    existing_rule_ids = [str(item) for item in raw]
            if payload.rule_id not in existing_rule_ids:
                existing_rule_ids.append(payload.rule_id)
            ruleset.rules = {"rule_ids": existing_rule_ids}
            ruleset.version = str(payload.rule_version)
            if payload.ruleset_note:
                ruleset.note = payload.ruleset_note

        db.commit()
        return RuleCreateResponse(ruleset_id=payload.ruleset_id, status="applied")

    proposal = RuleProposal(
        source_event_id=payload.source_event_id,
        evaluation_id=payload.evaluation_id,
        title=payload.title,
        rule_id=payload.rule_id,
        rule_version=payload.rule_version,
        proposal_status=payload.proposal_status,
        rule_yaml=payload.rule_yaml,
        rationale=payload.rationale,
        status=payload.proposal_status,
        created_by=payload.created_by,
        references_json=payload.references_json,
        risk_notes=payload.risk_notes,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return RuleCreateResponse(proposal_id=str(proposal.id), status=proposal.status)


def _parse_rule_yaml(rule_yaml: str, expected_rule_id: str) -> dict:
    try:
        payload = yaml.safe_load(rule_yaml)
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid rule YAML: {exc}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rule YAML must be a top-level object")

    parsed_rule_id = payload.get("id")
    if parsed_rule_id != expected_rule_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"rule YAML id ({parsed_rule_id}) must match rule_id ({expected_rule_id})",
        )

    return payload


def _resolve_writable_rules_dir() -> Path:
    configured = resolve_rules_dir()
    if configured.exists() and os.access(configured, os.W_OK):
        return configured
    if configured.parent.exists() and os.access(configured.parent, os.W_OK):
        return configured
    return Path(__file__).resolve().parents[4] / "rules"
