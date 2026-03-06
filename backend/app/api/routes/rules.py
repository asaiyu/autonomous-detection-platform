from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.detection.rule_loader import load_rules
from app.models.rule_proposal import RuleProposal
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
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ruleset mutation mode not implemented in MVP; use mode=proposal",
        )

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
