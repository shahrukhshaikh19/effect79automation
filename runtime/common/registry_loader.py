"""Load canonical registries for Phase F runtime."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from runtime.common.constants import (
    LICENSE_RESTRICTED_SKILLS,
    OPERATIONAL_RESTRICTED_SKILLS,
)

REPO = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=1)
def load_skills_yaml() -> dict[str, Any]:
    path = REPO / "registry" / "SKILLS.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def load_external_lock() -> list[dict[str, Any]]:
    path = REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries = data.get("entries", []) if isinstance(data, dict) else []
    return [e for e in entries if isinstance(e, dict)]


@lru_cache(maxsize=1)
def load_routing_policy() -> dict[str, Any]:
    path = REPO / "registry" / "ROUTING_POLICY.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def load_runtime_policy() -> dict[str, Any]:
    path = REPO / "registry" / "RUNTIME_POLICY.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def all_known_skill_ids() -> frozenset[str]:
    ids: set[str] = set()
    skills = load_skills_yaml()
    for entry in skills.get("proprietary", []):
        if isinstance(entry, dict) and entry.get("id"):
            ids.add(str(entry["id"]))
    lock = load_external_lock()
    for entry in lock:
        if entry.get("id"):
            ids.add(str(entry["id"]))
    return frozenset(ids)


def skill_name_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    skills = load_skills_yaml()
    for entry in skills.get("proprietary", []):
        if isinstance(entry, dict) and entry.get("id") and entry.get("name"):
            mapping[str(entry["id"])] = str(entry["name"])
    for entry in load_external_lock():
        if entry.get("id") and entry.get("name"):
            mapping[str(entry["id"])] = str(entry["name"])
    return mapping


def skill_path_for_id(skill_id: str) -> str:
    name = skill_name_map().get(skill_id, "")
    if skill_id.startswith("ACOS-"):
        return f"skills/acos/{name}/SKILL.md" if name else ""
    entry = next((e for e in load_external_lock() if e.get("id") == skill_id), None)
    if entry and entry.get("local_path"):
        return f"{entry['local_path']}/SKILL.md"
    return ""


def skill_restrictions(skill_id: str) -> dict[str, Any]:
    restrictions: dict[str, Any] = {}
    if skill_id in LICENSE_RESTRICTED_SKILLS:
        restrictions["license"] = "LICENSE_REVIEW_REQUIRED"
        restrictions["commercial_redistribution_status"] = "blocked_pending_license_review"
        restrictions["activation_requires"] = "license_review_acknowledged"
    if skill_id in OPERATIONAL_RESTRICTED_SKILLS:
        entry = next((e for e in load_external_lock() if e.get("id") == skill_id), None)
        restrictions["operational_status"] = (entry or {}).get("operational_status", "restricted")
        restrictions["activation_requires"] = "explicit_reconstruction_path_procedural_browser"
    return restrictions


def is_skill_known(skill_id: str) -> bool:
    return skill_id in all_known_skill_ids()


def default_retry_budget() -> int:
    policy = load_runtime_policy()
    correction = policy.get("correction", {}) if isinstance(policy, dict) else {}
    budget = correction.get("default_retry_budget", 2)
    return int(budget) if isinstance(budget, int) else 2
