from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse


SUPPORTED_SOURCE_TYPES = {"dns", "firewall", "windows", "macos", "http", "application"}


@dataclass(frozen=True)
class NormalizedEvent:
    event_id: uuid.UUID
    occurred_at: datetime
    canonical_event: dict[str, Any]


def normalize_event(source_type: str, raw_event: dict[str, Any], timestamp: Optional[str] = None) -> NormalizedEvent:
    event_id = uuid.uuid4()
    occurred_at = parse_timestamp(timestamp or _get_raw_timestamp(raw_event))

    if source_type == "dns":
        canonical_event = _normalize_dns(event_id, occurred_at, raw_event)
    elif source_type == "http":
        canonical_event = _normalize_http(event_id, occurred_at, raw_event)
    else:
        canonical_event = _normalize_passthrough(source_type, event_id, occurred_at, raw_event)

    return NormalizedEvent(event_id=event_id, occurred_at=occurred_at, canonical_event=canonical_event)


def parse_timestamp(raw_timestamp: Optional[str]) -> datetime:
    if not raw_timestamp:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    normalized = raw_timestamp.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def to_utc_iso(timestamp: datetime) -> str:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)
    return timestamp.isoformat().replace("+00:00", "Z")


def _normalize_dns(event_id: uuid.UUID, occurred_at: datetime, raw_event: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = _base_event(
        source_type="dns",
        event_id=event_id,
        occurred_at=occurred_at,
        event_category=_first_non_none(
            _nested_get(raw_event, "event", "category"),
            raw_event.get("event_category"),
            raw_event.get("category"),
            "network",
        ),
        event_type=_first_non_none(
            _nested_get(raw_event, "event", "type"),
            raw_event.get("event_type"),
            raw_event.get("type"),
            "dns_query",
        ),
    )

    canonical["dns"] = {
        "query": _first_non_none(raw_event.get("query"), raw_event.get("qname")),
        "record_type": _first_non_none(raw_event.get("record_type"), raw_event.get("qtype")),
        "rcode": _first_non_none(raw_event.get("rcode"), raw_event.get("response_code")),
        "answers": raw_event.get("answers"),
    }
    canonical["network"] = {
        "src_ip": _first_non_none(raw_event.get("client_ip"), raw_event.get("src_ip")),
        "dst_ip": _first_non_none(raw_event.get("server_ip"), raw_event.get("dst_ip")),
    }

    return canonical


def _normalize_http(event_id: uuid.UUID, occurred_at: datetime, raw_event: dict[str, Any]) -> dict[str, Any]:
    url_value = _first_non_none(raw_event.get("url"), raw_event.get("request_url"))
    parsed_url = urlparse(str(url_value)) if url_value is not None else None

    canonical: dict[str, Any] = _base_event(
        source_type="http",
        event_id=event_id,
        occurred_at=occurred_at,
        event_category=_first_non_none(
            _nested_get(raw_event, "event", "category"),
            raw_event.get("event_category"),
            raw_event.get("category"),
            "web",
        ),
        event_type=_first_non_none(
            _nested_get(raw_event, "event", "type"),
            raw_event.get("event_type"),
            raw_event.get("type"),
            "http_request",
        ),
    )

    canonical["http"] = {
        "method": _first_non_none(raw_event.get("method"), raw_event.get("http_method")),
        "url": url_value,
        "path": parsed_url.path if parsed_url else None,
        "query": parsed_url.query if parsed_url else None,
        "status_code": _first_non_none(raw_event.get("status_code"), raw_event.get("response_status")),
        "user_agent": _first_non_none(raw_event.get("user_agent"), raw_event.get("ua")),
    }
    canonical["network"] = {
        "src_ip": _first_non_none(raw_event.get("client_ip"), raw_event.get("src_ip")),
        "dst_ip": _first_non_none(raw_event.get("server_ip"), raw_event.get("dst_ip")),
    }

    return canonical


def _normalize_passthrough(
    source_type: str,
    event_id: uuid.UUID,
    occurred_at: datetime,
    raw_event: dict[str, Any],
) -> dict[str, Any]:
    event_category = _first_non_none(
        _nested_get(raw_event, "event", "category"),
        raw_event.get("event_category"),
        raw_event.get("category"),
    )
    event_type = _first_non_none(
        _nested_get(raw_event, "event", "type"),
        raw_event.get("event_type"),
        raw_event.get("type"),
    )

    canonical = _base_event(
        source_type=source_type,
        event_id=event_id,
        occurred_at=occurred_at,
        event_category=event_category,
        event_type=event_type,
    )
    canonical["data"] = {"raw_event": raw_event}
    return canonical


def _base_event(
    source_type: str,
    event_id: uuid.UUID,
    occurred_at: datetime,
    event_category: Optional[str],
    event_type: Optional[str],
) -> dict[str, Any]:
    canonical: dict[str, Any] = {
        "event_id": str(event_id),
        "timestamp": to_utc_iso(occurred_at),
        "source": {"type": source_type},
    }

    event_obj: dict[str, str] = {}
    if event_category:
        event_obj["category"] = event_category
    if event_type:
        event_obj["type"] = event_type
    if event_obj:
        canonical["event"] = event_obj

    return canonical


def _get_raw_timestamp(raw_event: dict[str, Any]) -> Optional[str]:
    for key in ("timestamp", "ts", "time"):
        value = raw_event.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _nested_get(obj: dict[str, Any], *path: str) -> Any:
    cursor: Any = obj
    for part in path:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(part)
    return cursor


def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None
