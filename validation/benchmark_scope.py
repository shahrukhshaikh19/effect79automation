"""Shared benchmark directory scope rules for PF-1 registration infrastructure."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BENCHMARKS_INFRA_FILES = frozenset(
    {
        "benchmarks/README.md",
        "benchmarks/.gitkeep",
    }
)

BENCHMARKS_INFRA_PREFIXES = (
    "benchmarks/templates/",
)

BENCHMARKS_REGISTRATION_PREFIX = "benchmarks/BM-"

# PF-2: canonical BM-001 execution subtree (implementation + evidence + run records)
BENCHMARKS_EXECUTION_PREFIX = "benchmarks/BM-001/execution/"

EXECUTION_ARTIFACT_SUFFIXES = frozenset(
    {".html", ".css", ".js", ".jsx", ".tsx", ".vue", ".glb", ".gltf", ".blend", ".png", ".jpg", ".jpeg", ".webp"}
)


def rel_path(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def is_pf2_execution_path(path: Path) -> bool:
    return rel_path(path).startswith(BENCHMARKS_EXECUTION_PREFIX)


def is_allowed_benchmarks_path(path: Path) -> bool:
    rel = rel_path(path)
    if rel in BENCHMARKS_INFRA_FILES:
        return True
    if any(rel.startswith(prefix) for prefix in BENCHMARKS_INFRA_PREFIXES):
        return True
    if is_pf2_execution_path(path):
        return True
    if rel.startswith(BENCHMARKS_REGISTRATION_PREFIX):
        allowed_names = {
            "REGISTRATION.yaml",
            "ORIGINAL_INPUT.md",
            "ACCEPTANCE_CONTRACT.yaml",
            "EVIDENCE_PLAN.yaml",
        }
        if path.name in allowed_names:
            return True
        if path.is_dir() and path.name.startswith("BM-"):
            return True
    return False


def is_forbidden_execution_artifact(path: Path) -> bool:
    rel = rel_path(path)
    if not rel.startswith("benchmarks/"):
        return False
    if is_pf2_execution_path(path):
        return False
    if is_allowed_benchmarks_path(path):
        if path.suffix.lower() in EXECUTION_ARTIFACT_SUFFIXES:
            return True
        return False
    return path.is_file() and path.stat().st_size > 0


def get_post_foundation_state() -> dict[str, str]:
    """Read execution_state.post_foundation from registry/PHASES.yaml."""
    phases_path = REPO / "registry" / "PHASES.yaml"
    if not phases_path.is_file():
        return {}
    try:
        import yaml

        phases = yaml.safe_load(phases_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    pf = phases.get("execution_state", {}).get("post_foundation", {})
    return pf if isinstance(pf, dict) else {}


def pf2_active() -> bool:
    pf = get_post_foundation_state()
    return pf.get("PF-2") in ("IN_PROGRESS", "COMPLETE")


def scan_benchmarks_and_projects(errors: list[str], fail_fn) -> None:
    """Shared PF-1-aware contamination scan for foundation validators."""
    for name in ("benchmarks", "projects"):
        base = REPO / name
        if not base.is_dir():
            continue
        for item in base.rglob("*"):
            if not item.is_file():
                continue
            if name == "projects":
                if item.name == ".gitkeep":
                    continue
                if item.stat().st_size > 0:
                    fail_fn(errors, f"{name}/ must remain empty: {item.relative_to(REPO)}")
                continue
            if is_forbidden_execution_artifact(item):
                fail_fn(errors, f"forbidden benchmark execution artifact: {item.relative_to(REPO)}")
            elif item.stat().st_size > 0 and not is_allowed_benchmarks_path(item):
                fail_fn(errors, f"unexpected benchmarks content: {item.relative_to(REPO)}")
