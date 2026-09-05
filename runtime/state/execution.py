"""Execution state persistence and resume."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.common.constants import EXECUTION_EVENT_TYPES
from runtime.common.registry_loader import REPO

DEFAULT_STORE = REPO / "validation" / "evidence" / "runtime" / "state"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_execution_state(task_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "routing_id": None,
        "current_stage": "INTAKE",
        "completed_stages": [],
        "planned_skill_ids": [],
        "active_skill_ids": [],
        "gate_states": {
            "design_gate": "NOT_APPLICABLE",
            "quality_gate": "NOT_EVALUATED",
            "product_form_gate": "NOT_APPLICABLE",
        },
        "critic_states": {},
        "correction_attempts": [],
        "memory_candidates": [],
        "evidence_refs": [],
        "blocked_reasons": [],
        "events": [],
        "status": "ACTIVE",
    }


def append_event(state: dict[str, Any], event_type: str, payload_ref: str = "") -> dict[str, Any]:
    if event_type not in EXECUTION_EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")
    state.setdefault("events", []).append(
        {"event_type": event_type, "timestamp": _now(), "payload_ref": payload_ref}
    )
    return state


def persist_state(state: dict[str, Any], store_dir: Path | None = None) -> Path:
    directory = store_dir or DEFAULT_STORE
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{state['task_id']}.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return path


def load_state(task_id: str, store_dir: Path | None = None) -> dict[str, Any] | None:
    directory = store_dir or DEFAULT_STORE
    path = directory / f"{task_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resume_execution(task_id: str, store_dir: Path | None = None) -> dict[str, Any]:
    state = load_state(task_id, store_dir)
    if state is None:
        raise FileNotFoundError(f"No persisted state for task {task_id}")
    append_event(state, "EXECUTION_RESUMED", payload_ref=task_id)
    persist_state(state, store_dir)
    return state
