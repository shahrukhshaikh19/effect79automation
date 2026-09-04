"""Evidence registration with provenance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from runtime.common.constants import FORBIDDEN_EVIDENCE_CLAIMS


def register_evidence(
    *,
    evidence_id: str,
    evidence_type: str,
    producer: str,
    artifact_ref: str,
    source: str,
    runtime_context: dict[str, Any] | None = None,
    integrity_verified: bool = False,
) -> dict[str, Any]:
    summary = artifact_ref.lower().strip()
    if summary in FORBIDDEN_EVIDENCE_CLAIMS:
        raise ValueError(f"Claim-only text cannot be registered as evidence: {artifact_ref}")
    return {
        "evidence_id": evidence_id,
        "type": evidence_type,
        "producer": producer,
        "artifact_ref": artifact_ref,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runtime_context": runtime_context or {},
        "integrity": {"verified": integrity_verified},
        "status": "registered",
    }


def validate_evidence_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("evidence_id", "type", "producer", "artifact_ref", "source", "timestamp", "status"):
        if not record.get(field):
            errors.append(f"Missing evidence field: {field}")
    artifact = str(record.get("artifact_ref", "")).lower().strip()
    if artifact in FORBIDDEN_EVIDENCE_CLAIMS:
        errors.append("Claim-only artifact_ref forbidden")
    return errors
