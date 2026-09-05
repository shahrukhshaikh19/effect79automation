"""Flagship craft locks. YAML prose is not modeling. A primitive dump is not a hero."""

from __future__ import annotations

import json
import math
import re
import struct
from pathlib import Path
from typing import Any

import yaml

from runtime.host.skill_execution import validate_artifact_execution, write_execution_receipt

CRAFT_FILES = {
    "EXT-BLD-01": "direction/blender_production.yaml",
    "EXT-BLD-02": "direction/blender_modeler.yaml",
    "EXT-BLD-03": "direction/prop_artist.yaml",
    "EXT-BLD-05": "direction/blender_materials.yaml",
    "EXT-BLD-06": "direction/blender_lookdev.yaml",
}
HARD_SURFACE_FILE = "direction/hard_surface.yaml"
BRIEF_CANDIDATES = (
    "direction/blender_production.yaml",
    "direction/blender_production_brief.yaml",
    "direction/blender_production_brief.md",
)
UNCHECKED_MODELING = re.compile(
    r"\[\s\][^\n]{0,80}(blockout|silhouette|modeling|model[ —-])",
    re.I,
)
UNCHECKED_LOOKDEV = re.compile(r"\[\s\][^\n]{0,80}look\s*dev", re.I)
PRIMITIVE_NAME = re.compile(
    r"\b(cube|sphere|cylinder|cone|torus|plane|grid|circle|ico(?:sphere)?|suzanne|uv.?sphere|nurbs)\b",
    re.I,
)


def required_craft_ids(signals: dict[str, Any] | None, planned_ids: list[str] | None = None) -> list[str]:
    ids = ["EXT-BLD-01", "EXT-BLD-02", "EXT-BLD-03", "EXT-BLD-05", "EXT-BLD-06"]
    if (signals or {}).get("requires_physical_product") or (planned_ids and "EXT-BLD-13" in planned_ids):
        ids.append("EXT-BLD-13")
    return ids


def validate_craft_artifacts(project_dir: Path, signals: dict[str, Any] | None, planned_ids: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for sid in required_craft_ids(signals, planned_ids):
        rel = HARD_SURFACE_FILE if sid == "EXT-BLD-13" else CRAFT_FILES[sid]
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        data = loaded if isinstance(loaded, dict) else {}
        issues = validate_artifact_execution(data, sid)
        invalid.extend(issues)
        if not issues:
            write_execution_receipt(project_dir, sid, rel)
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}


def validate_brief_honesty(project_dir: Path) -> list[str]:
    text = ""
    for rel in BRIEF_CANDIDATES:
        path = project_dir / rel
        if path.is_file():
            text += "\n" + path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return []
    issues: list[str] = []
    if UNCHECKED_MODELING.search(text):
        issues.append(
            "blender production brief still has modeling/blockout unchecked — export is not complete"
        )
    if UNCHECKED_LOOKDEV.search(text):
        issues.append(
            "blender production brief still has lookdev unchecked — two PNGs do not finish the brief"
        )
    return issues


def _gltf_from_asset(path: Path) -> tuple[dict[str, Any], bytes] | None:
    raw = path.read_bytes()
    if raw[:4] == b"glTF":
        if len(raw) < 20:
            return None
        json_len = struct.unpack_from("<I", raw, 12)[0]
        json_start = 20
        json_end = json_start + json_len
        if json_end > len(raw):
            return None
        try:
            gltf = json.loads(raw[json_start:json_end])
        except json.JSONDecodeError:
            return None
        bin_start = json_end
        if bin_start + 8 <= len(raw) and raw[bin_start + 4 : bin_start + 8] == b"BIN\x00":
            bin_len = struct.unpack_from("<I", raw, bin_start)[0]
            blob = raw[bin_start + 8 : bin_start + 8 + bin_len]
        else:
            blob = b""
        return gltf, blob
    if path.suffix.lower() == ".gltf":
        try:
            gltf = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        blob = b""
        buffers = gltf.get("buffers") or []
        if buffers and buffers[0].get("uri") and not str(buffers[0]["uri"]).startswith("data:"):
            bin_path = path.parent / buffers[0]["uri"]
            if bin_path.is_file():
                blob = bin_path.read_bytes()
        return gltf, blob
    return None


def _node_names(gltf: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for node in gltf.get("nodes") or []:
        if isinstance(node, dict) and node.get("name"):
            names.append(str(node["name"]))
    for mesh in gltf.get("meshes") or []:
        if isinstance(mesh, dict) and mesh.get("name"):
            names.append(str(mesh["name"]))
    return names


def _positions(gltf: dict[str, Any], blob: bytes, accessor_index: int) -> list[tuple[float, float, float]]:
    accessors = gltf.get("accessors") or []
    views = gltf.get("bufferViews") or []
    if accessor_index >= len(accessors):
        return []
    acc = accessors[accessor_index]
    if acc.get("type") != "VEC3" or acc.get("componentType") != 5126:
        return []
    view_i = acc.get("bufferView")
    if view_i is None or view_i >= len(views):
        return []
    view = views[view_i]
    offset = int(view.get("byteOffset") or 0) + int(acc.get("byteOffset") or 0)
    count = int(acc.get("count") or 0)
    end = offset + count * 12
    if end > len(blob) or count < 8:
        return []
    out: list[tuple[float, float, float]] = []
    chunk = blob[offset:end]
    for i in range(count):
        x, y, z = struct.unpack_from("<fff", chunk, i * 12)
        out.append((x, y, z))
    return out


def _is_sphere(points: list[tuple[float, float, float]]) -> bool:
    if len(points) < 48:
        return False
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    cz = sum(p[2] for p in points) / len(points)
    radii = [math.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2 + (p[2] - cz) ** 2) for p in points]
    mean = sum(radii) / len(radii)
    if mean < 1e-5:
        return False
    var = sum((r - mean) ** 2 for r in radii) / len(radii)
    return math.sqrt(var) / mean < 0.035


def _is_plane(points: list[tuple[float, float, float]]) -> bool:
    if len(points) < 16:
        return False
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]

    def flat(vals: list[float]) -> bool:
        return max(vals) - min(vals) < 1e-3 * max(1.0, max(abs(max(vals)), abs(min(vals))))

    return sum(1 for axis in (xs, ys, zs) if flat(axis)) >= 1


def _mesh_vert_counts(gltf: dict[str, Any]) -> list[int]:
    counts: list[int] = []
    accessors = gltf.get("accessors") or []
    for mesh in gltf.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            attrs = prim.get("attributes") or {}
            pos = attrs.get("POSITION")
            if pos is None or pos >= len(accessors):
                continue
            counts.append(int(accessors[pos].get("count") or 0))
    return counts


def inspect_hero_asset(path: Path) -> dict[str, Any]:
    parsed = _gltf_from_asset(path)
    if parsed is None:
        return {"ok": False, "issues": [f"{path.name}: not a readable GLB/GLTF"]}
    gltf, blob = parsed
    names = _node_names(gltf)
    primitive_names = [n for n in names if PRIMITIVE_NAME.search(n)]
    issues: list[str] = []
    if len(primitive_names) >= 2:
        issues.append(
            f"{path.name}: hero still uses default primitive names ({', '.join(primitive_names[:6])}) — not authored craft"
        )
    if names and len(primitive_names) / max(len(names), 1) >= 0.4:
        issues.append(f"{path.name}: too many primitive-named meshes — rename is not authorship")
    counts = _mesh_vert_counts(gltf)
    if len(counts) >= 12 and len(set(counts)) <= 4:
        issues.append(f"{path.name}: instance farm of a few mesh signatures — not authored plants/parts")
    sphere_hits = 0
    plane_hits = 0
    checked = 0
    for mesh in (gltf.get("meshes") or [])[:16]:
        for prim in mesh.get("primitives") or []:
            attrs = prim.get("attributes") or {}
            pos = attrs.get("POSITION")
            if pos is None:
                continue
            points = _positions(gltf, blob, int(pos))
            if len(points) < 16:
                continue
            checked += 1
            if _is_sphere(points):
                sphere_hits += 1
            if _is_plane(points):
                plane_hits += 1
    if sphere_hits >= 2:
        issues.append(f"{path.name}: at least two meshes are UV-sphere dumps — not machined/sculpted forms")
    if checked >= 2 and (sphere_hits + plane_hits) / checked >= 0.55:
        issues.append(f"{path.name}: majority of inspected meshes are sphere/plane primitives")
    return {"ok": not issues, "issues": issues, "names": names}


def validate_hero_primitives(project_dir: Path) -> list[str]:
    issues: list[str] = []
    for root in (project_dir / "implementation", project_dir / "assets"):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".glb", ".gltf"} and path.stat().st_size > 32:
                issues.extend(inspect_hero_asset(path)["issues"])
    return issues
