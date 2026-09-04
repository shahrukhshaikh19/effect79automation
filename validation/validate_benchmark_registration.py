#!/usr/bin/env python3
"""ACOS PF-1 benchmark registration validator."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
PHASE = "PF-1"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def _path_label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


BM_ID_RE = re.compile(r"^BM-\d{3}$")
FORBIDDEN_SKILL_ROUTING = re.compile(r"\b(ACOS-\d{2}|EXT-[A-Z0-9-]+)\b")
LICENSE_BYPASS = re.compile(r"license_review_acknowledged|bypass.*license|whitelist.*EXT-FE", re.I)
GLOBAL_AESTHETIC = re.compile(r"global.*(aesthetic|house style|always use)", re.I)
FABRICATION_MARKERS = ("invented_by_pf1", "ai_generated_requirement", "placeholder_company")

HASH_EXCLUDES = frozenset(
    {
        "contract_hash",
        "benchmark_contract_sha256",
        "execution_state",
        "benchmark_score",
        "benchmark_result",
        "frozen_at",
        "scores",
        "evidence_outputs",
    }
)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_yaml(path: Path, errors: list[str]) -> dict | None:
    if yaml is None:
        fail(errors, "PyYAML required")
        return None
    if not path.is_file():
        fail(errors, f"Missing file: {path.relative_to(REPO)}")
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(errors, f"Expected mapping: {path.relative_to(REPO)}")
        return None
    return data


def canonical_hash(payload: dict[str, Any]) -> str:
    cleaned = copy.deepcopy(payload)

    def _strip(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _strip(v) for k, v in obj.items() if k not in HASH_EXCLUDES}
        if isinstance(obj, list):
            return [_strip(x) for x in obj]
        return obj

    normalized = json.dumps(_strip(cleaned), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_foundation_ready(errors: list[str]) -> None:
    phases = load_yaml(REPO / "registry" / "PHASES.yaml", errors)
    if not phases:
        return
    ready = phases.get("foundation_ready") or {}
    if ready.get("declared") is not True:
        fail(errors, "FOUNDATION_READY must be declared before PF-1")
        return
    result_ref = ready.get("certification_result", "")
    if result_ref and not (REPO / result_ref).is_file():
        fail(errors, f"Missing foundation certification result: {result_ref}")
    tested = ready.get("tested_implementation_sha", "")
    if tested != "e0bd72b0ec3cc61ae59ac45bdc55fbc60dcb7a3a":
        fail(errors, "foundation tested_implementation_sha must remain e0bd72b (unchanged by PF-1)")


def validate_phase_state(errors: list[str]) -> None:
    phases = load_yaml(REPO / "registry" / "PHASES.yaml", errors)
    if not phases:
        return
    pf = phases.get("execution_state", {}).get("post_foundation", {})
    if not isinstance(pf, dict):
        fail(errors, "execution_state.post_foundation must be a per-phase mapping")
        return
    pf1 = pf.get("PF-1")
    if pf1 not in ("IN_PROGRESS", "COMPLETE"):
        fail(errors, f"PF-1 must be IN_PROGRESS or COMPLETE, got {pf1}")
    for other in ("PF-2", "PF-3", "PF-4", "PF-5"):
        if pf.get(other) != "NOT_STARTED":
            fail(errors, f"{other} must remain NOT_STARTED during PF-1")


def validate_registry(errors: list[str]) -> None:
    registry = load_yaml(REPO / "registry" / "BENCHMARKS.yaml", errors)
    if not registry:
        return
    if registry.get("phase") != "PF-1":
        fail(errors, "BENCHMARKS.yaml phase must be PF-1")
    benchmarks = registry.get("benchmarks")
    if benchmarks is None or not isinstance(benchmarks, list):
        fail(errors, "BENCHMARKS.yaml benchmarks must be a list")
        return
    seen: set[str] = set()
    for entry in benchmarks:
        if not isinstance(entry, dict):
            fail(errors, "Each benchmark registry entry must be a mapping")
            continue
        bid = entry.get("benchmark_id", "")
        if not BM_ID_RE.fullmatch(str(bid)):
            fail(errors, f"Invalid benchmark_id in registry: {bid}")
        if bid in seen:
            fail(errors, f"Duplicate benchmark_id in registry: {bid}")
        seen.add(str(bid))


def validate_infrastructure(errors: list[str]) -> None:
    required = [
        REPO / "benchmarks" / "README.md",
        REPO / "benchmarks" / "templates" / "BENCHMARK_REGISTRATION.schema.yaml",
        REPO / "benchmarks" / "templates" / "BENCHMARK_BRIEF.template.yaml",
        REPO / "benchmarks" / "templates" / "ACCEPTANCE_CONTRACT.template.yaml",
        REPO / "benchmarks" / "templates" / "EVIDENCE_PLAN.template.yaml",
        REPO / "validation" / "validate_benchmark_registration.py",
    ]
    for path in required:
        if not path.is_file():
            fail(errors, f"Missing PF-1 infrastructure: {path.relative_to(REPO)}")


def _validate_no_skill_routing(text: str, context: str, errors: list[str]) -> None:
    lowered = text.lower()
    if "activate:" in lowered or "activated_skill_ids" in lowered:
        if FORBIDDEN_SKILL_ROUTING.search(text):
            fail(errors, f"Manual skill routing forbidden in {context}")
    if "routing_override" in lowered:
        fail(errors, f"Routing override forbidden in {context}")


def _validate_no_foundation_leakage(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    label = _path_label(path)
    if GLOBAL_AESTHETIC.search(text):
        fail(errors, f"Global aesthetic promotion forbidden: {label}")
    if LICENSE_BYPASS.search(text):
        fail(errors, f"License bypass forbidden: {label}")
    for marker in FABRICATION_MARKERS:
        if marker in text:
            fail(errors, f"Fabricated requirement marker in {label}: {marker}")


def validate_registration_file(reg_path: Path, errors: list[str]) -> None:
    data = load_yaml(reg_path, errors)
    if not data:
        return

    bid = data.get("benchmark_id", "")
    if not BM_ID_RE.fullmatch(str(bid)):
        fail(errors, f"{reg_path.name}: invalid benchmark_id")

    status = data.get("status", "")
    if status not in {
        "DRAFT", "INPUT_REQUIRED", "REGISTERED", "FROZEN",
        "EXECUTION_STARTED", "COMPLETED", "INVALIDATED",
    }:
        fail(errors, f"{bid}: invalid status {status}")

    if status in ("EXECUTION_STARTED", "COMPLETED"):
        fail(errors, f"{bid}: PF-2 execution status forbidden during PF-1")

    op = data.get("operator_input") or {}
    if not isinstance(op, dict) or not str(op.get("original_text", "")).strip():
        fail(errors, f"{bid}: operator_input.original_text must be preserved")

    exec_state = data.get("execution_state") or {}
    if exec_state.get("benchmark_result") not in (None, "NOT_EXECUTED"):
        fail(errors, f"{bid}: benchmark_result must be NOT_EXECUTED before execution")
    if exec_state.get("benchmark_score") not in (None, "null"):
        fail(errors, f"{bid}: benchmark_score must be null before execution")

    text = reg_path.read_text(encoding="utf-8")
    _validate_no_skill_routing(text, _path_label(reg_path), errors)
    _validate_no_foundation_leakage(reg_path, errors)

    if data.get("global_memory_promotion"):
        fail(errors, f"{bid}: global memory promotion forbidden in PF-1")

    acceptance = data.get("acceptance_contract") or {}
    dimensions = (acceptance.get("dimensions") or {}) if isinstance(acceptance, dict) else {}
    applicable_weights = 0.0
    for name, spec in dimensions.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("applicable") is True:
            weight = spec.get("weight", 0)
            if not isinstance(weight, (int, float)) or weight <= 0:
                fail(errors, f"{bid}: invalid weight for applicable dimension {name}")
            applicable_weights += float(weight)
    if applicable_weights > 0 and abs(applicable_weights - 100.0) > 0.01:
        fail(errors, f"{bid}: applicable dimension weights must sum to 100, got {applicable_weights}")

    evidence_plan = data.get("evidence_plan")
    if status == "FROZEN" and not evidence_plan:
        fail(errors, f"{bid}: FROZEN status requires evidence_plan")

    hard_failures = data.get("hard_failures")
    if status == "FROZEN" and not hard_failures:
        fail(errors, f"{bid}: FROZEN status requires hard_failures")

    confirmation = data.get("operator_confirmation") or {}
    if status == "FROZEN":
        for key in ("brief_correct", "references_correct", "acceptance_contract_correct"):
            if confirmation.get(key) != "confirmed":
                fail(errors, f"{bid}: FROZEN requires operator_confirmation.{key}=confirmed")

    stored_hash = data.get("benchmark_contract_sha256") or data.get("contract_hash")
    if status == "FROZEN":
        if not stored_hash:
            fail(errors, f"{bid}: FROZEN requires benchmark_contract_sha256")
        else:
            computed = canonical_hash(data)
            if str(stored_hash) != computed:
                fail(errors, f"{bid}: contract hash mismatch")

    revision = data.get("revision") or {}
    if isinstance(revision, dict) and revision.get("parent_version") and not revision.get("version"):
        fail(errors, f"{bid}: revision.version required when parent_version set")


def validate_benchmark_directories(errors: list[str]) -> None:
    for path in (REPO / "benchmarks").glob("BM-*"):
        if not path.is_dir():
            continue
        reg = path / "REGISTRATION.yaml"
        if not reg.is_file():
            fail(errors, f"Missing REGISTRATION.yaml in {path.relative_to(REPO)}")
            continue
        validate_registration_file(reg, errors)
        for artifact in ("ORIGINAL_INPUT.md", "ACCEPTANCE_CONTRACT.yaml", "EVIDENCE_PLAN.yaml"):
            ap = path / artifact
            if ap.is_file():
                _validate_no_foundation_leakage(ap, errors)
                _validate_no_skill_routing(ap.read_text(encoding="utf-8"), str(ap.relative_to(REPO)), errors)


def validate_no_execution_artifacts(errors: list[str]) -> None:
    from benchmark_scope import is_forbidden_execution_artifact

    for path in (REPO / "benchmarks").rglob("*"):
        if path.is_file() and is_forbidden_execution_artifact(path):
            fail(errors, f"Benchmark execution artifact forbidden in PF-1: {path.relative_to(REPO)}")


def validate_foundation_unmodified(errors: list[str]) -> None:
    foundation_paths = [
        REPO / "core" / "CONSTITUTION.md",
        REPO / "core" / "QUALITY_GATES.md",
        REPO / "registry" / "ROUTING_POLICY.yaml",
        REPO / "registry" / "RUNTIME_POLICY.yaml",
    ]
    for path in foundation_paths:
        if not path.is_file():
            fail(errors, f"Foundation file missing: {path.relative_to(REPO)}")


def main() -> int:
    errors: list[str] = []
    print(f"ACOS PF-1 Benchmark Registration Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    validate_foundation_ready(errors)
    validate_phase_state(errors)
    validate_infrastructure(errors)
    validate_registry(errors)
    validate_benchmark_directories(errors)
    validate_no_execution_artifacts(errors)
    validate_foundation_unmodified(errors)

    if errors:
        print("VALIDATION: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    registry = yaml.safe_load((REPO / "registry" / "BENCHMARKS.yaml").read_text(encoding="utf-8"))
    benchmark_count = len(registry.get("benchmarks") or [])
    if benchmark_count == 0:
        print("VALIDATION: PASSED (framework only — BENCHMARK_INPUT_REQUIRED)")
    else:
        print(f"VALIDATION: PASSED ({benchmark_count} benchmark(s) registered)")
    print("PF-2 remains NOT_STARTED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
