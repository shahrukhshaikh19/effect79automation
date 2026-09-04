"""Memory records, promotion, retrieval, and conflict handling."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PROMOTION_ORDER = (
    "observation",
    "project-rule",
    "candidate-global",
    "validated-global",
    "deprecated",
)

PROHIBITED_SHORTCUTS = {
    ("observation", "validated-global"),
    ("observation", "candidate-global"),  # must go through project-rule first per policy — actually candidate-global ok from project-rule
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
) -> dict[str, Any]:
    if not evidence_refs:
        raise ValueError("Memory records require evidence_refs")
    return {
        "memory_id": memory_id,
        "category": category,
        "scope": scope,
        "statement": statement,
        "source_task_id": source_task_id,
        "evidence_refs": evidence_refs,
        "confidence": confidence,
        "promotion_level": promotion_level,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validated_at": None,
        "supersedes": None,
        "model_profile": model_profile,
        "status": "draft",
    }


def validate_promotion(current: str, target: str) -> list[str]:
    errors: list[str] = []
    if (current, target) in PROHIBITED_SHORTCUTS or (current == "observation" and target == "validated-global"):
        errors.append(f"Prohibited promotion shortcut: {current} → {target}")
    if current not in PROMOTION_ORDER or target not in PROMOTION_ORDER:
        errors.append("Invalid promotion level")
    cur_idx = PROMOTION_ORDER.index(current)
    tgt_idx = PROMOTION_ORDER.index(target)
    if tgt_idx > cur_idx + 1 and not (current == "project-rule" and target == "candidate-global"):
        if current == "observation" and target != "project-rule":
            errors.append(f"Cannot skip promotion stages from {current} to {target}")
    return errors


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
            continue  # model-specific cannot silently become global without validation
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
    conflicts: list[dict[str, Any]] = []
    by_topic: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        key = rec.get("statement", "")[:80]
        by_topic.setdefault(key, []).append(rec)
    for _key, group in by_topic.items():
        if len(group) < 2:
            continue
        levels = {g.get("promotion_level") for g in group}
        if len(levels) > 1:
            conflicts.append(
                {
                    "status": "MEMORY_CONFLICT_REQUIRES_RESOLUTION",
                    "record_ids": [g["memory_id"] for g in group],
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
