"""Map Phase F skill IDs to host-native skill names for Cursor / Claude / Codex."""

from __future__ import annotations

from runtime.common.registry_loader import skill_name_map, skill_path_for_id


def native_skill_name(skill_id: str) -> str:
    return skill_name_map().get(skill_id, "")


def native_invoke(skill_id: str) -> str:
    name = native_skill_name(skill_id)
    return f"/{name}" if name else ""


def describe_skill(skill_id: str) -> dict[str, str]:
    name = native_skill_name(skill_id)
    return {
        "skill_id": skill_id,
        "native_skill_name": name,
        "invoke": f"/{name}" if name else "",
        "skill_path": skill_path_for_id(skill_id),
    }
