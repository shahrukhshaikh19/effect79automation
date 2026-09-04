"""Memory records, promotion, retrieval, and conflict handling."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from runtime.common.registry_loader import load_runtime_policy

PROMOTION_ORDER = (
    "observation",
    "project-rule",
    "candidate-global",
    "validated-global",
    "deprecated",
)

GLOBAL_SCOPES = frozenset({"validated_global", "reusable_system", "candidate_global"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_memory_observation(
    *,
    memory_id: str,
    category: str,
    scope: str,
    statement: str,
    source_task_id: str,
    evidence_refs: list[str],
    subject_key: str,
    value: str,
    claim_type: str = "fact",
    confidence: str = "low",
    model_profile: str | None = None,
    conflicts_with: list[str] | None = None,
) -> dict[str, Any]:
    """Normal runtime creation — always begins at observation promotion level."""
    if not evidence_refs:
        raise ValueError("Memory records require evidence_refs")
    if not subject_key:
        raise ValueError("Memory records require subject_key for conflict semantics")
    return {
        "memory_id": memory_id,
        "category": category,
        "scope": scope,
        "statement": statement,
        "source_task_id": source_task_id,
        "evidence_refs": evidence_refs,
        "subject_key": subject_key,
        "claim_type": claim_type,
        "value": value,
        "conflicts_with": conflicts_with or [],
        "confidence": confidence,
        "promotion_level": "observation",
        "created_at": _now(),
        "validated_at": None,
        "supersedes": None,
        "model_profile": model_profile,
        "status": "draft",
        "promotion_history": [],
    }


def create_memory_record(
    *,
    memory_id: str,
    category: str,
    scope: str,
    statement: str,
    source_task_id: str,
    evidence_refs: list[str],
    confidence: str = "low",
    promotion_level: str = "observation",
    model_profile: str | None = None,
    subject_key: str = "",
    value: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Backward-compatible wrapper — rejects non-observation direct creation."""
    if promotion_level != "observation":
        raise ValueError(
            f"Direct creation at promotion_level={promotion_level} forbidden; use create_memory_observation + promote_memory"
        )
    return create_memory_observation(
        memory_id=memory_id,
        category=category,
        scope=scope,
        statement=statement,
        source_task_id=source_task_id,
        evidence_refs=evidence_refs,
        subject_key=subject_key or f"legacy.{memory_id}",
        value=value or statement[:64],
        claim_type=kwargs.get("claim_type", "fact"),
        confidence=confidence,
        model_profile=model_profile,
        conflicts_with=kwargs.get("conflicts_with"),
    )


def validate_promotion(current: str, target: str, *, scope: str | None = None) -> list[str]:
    errors: list[str] = []
    if current == "observation" and target == "validated-global":
        errors.append("Prohibited promotion shortcut: observation → validated-global")
    if current not in PROMOTION_ORDER or target not in PROMOTION_ORDER:
        errors.append("Invalid promotion level")
        return errors
    cur_idx = PROMOTION_ORDER.index(current)
    tgt_idx = PROMOTION_ORDER.index(target)
    if tgt_idx != cur_idx + 1 and target != "deprecated":
        errors.append(f"Cannot skip promotion stages from {current} to {target}")
    if scope == "model_specific" and target == "validated-global":
        errors.append("Model-specific memory cannot promote directly to validated-global without scope migration evidence")
    return errors


def promote_memory(
    record: dict[str, Any],
    target_level: str,
    supporting_evidence_refs: list[str],
    validation_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stateful promotion with evidence, history, and scope constraints."""
    ctx = validation_context or {}
    current = record.get("promotion_level", "observation")
    errors = validate_promotion(current, target_level, scope=record.get("scope"))
    if errors:
        raise ValueError("; ".join(errors))
    if not supporting_evidence_refs:
        raise ValueError("Promotion requires supporting_evidence_refs")

    target_scope = ctx.get("target_scope")
    if record.get("scope") == "model_specific" and target_scope in GLOBAL_SCOPES:
        raise ValueError("Model-specific scope cannot silently migrate to global scope")

    promoted = dict(record)
    promoted["promotion_level"] = target_level
    promoted["evidence_refs"] = sorted(set(record.get("evidence_refs", [])) | set(supporting_evidence_refs))
    promoted["promotion_history"] = list(record.get("promotion_history", [])) + [
        {"from": current, "to": target_level, "at": _now(), "evidence_refs": supporting_evidence_refs}
    ]
    if target_level == "validated-global":
        promoted["validated_at"] = _now()
        promoted["status"] = "active"
    return promoted


def retrieve_memory(
    records: list[dict[str, Any]],
    *,
    task_id: str | None = None,
    project_id: str | None = None,
    categories: list[str] | None = None,
    promotion_levels: list[str] | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rec in records:
        if rec.get("status") in ("deprecated", "rejected", "superseded"):
            continue
        if categories and rec.get("category") not in categories:
            continue
        if promotion_levels and rec.get("promotion_level") not in promotion_levels:
            continue
        if rec.get("scope") == "model_specific" and rec.get("promotion_level") == "validated-global":
            continue
        why = "task_relevance"
        if project_id and rec.get("scope") == "project":
            why = "project_scope_match"
        results.append(
            {
                "memory_id": rec["memory_id"],
                "why_retrieved": why,
                "scope": rec.get("scope"),
                "confidence": rec.get("confidence"),
                "evidence_refs": rec.get("evidence_refs", []),
            }
        )
    return results


def detect_conflicts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Conflict by structured subject_key semantics — not promotion-level differences.
    Same subject + same value at different promotion levels is NOT a conflict.
    """
    conflicts: list[dict[str, Any]] = []
    active = [r for r in records if r.get("status") not in ("deprecated", "superseded", "rejected")]

    by_subject: dict[str, list[dict[str, Any]]] = {}
    for rec in active:
        key = rec.get("subject_key") or ""
        if key:
            by_subject.setdefault(key, []).append(rec)

    for subject_key, group in by_subject.items():
        values = {r.get("value") for r in group if r.get("value") is not None}
        if len(values) > 1:
            conflicts.append(
                {
                    "status": "MEMORY_CONFLICT_REQUIRES_RESOLUTION",
                    "subject_key": subject_key,
                    "record_ids": [r["memory_id"] for r in group],
                    "reason": "incompatible values for same subject_key",
                }
            )

    for rec in active:
        for other_id in rec.get("conflicts_with", []) or []:
            if any(o["memory_id"] == other_id for o in active):
                conflicts.append(
                    {
                        "status": "MEMORY_CONFLICT_REQUIRES_RESOLUTION",
                        "subject_key": rec.get("subject_key"),
                        "record_ids": sorted({rec["memory_id"], other_id}),
                        "reason": "explicit conflicts_with reference",
                    }
                )

    return conflicts


def memory_overrides_authority(statement: str) -> bool:
    lower = statement.lower()
    forbidden = (
        "override constitution",
        "ignore quality gate",
        "skip quality gate",
        "activate all skills",
        "blender tcp equals mcp verified",
    )
    return any(p in lower for p in forbidden)
