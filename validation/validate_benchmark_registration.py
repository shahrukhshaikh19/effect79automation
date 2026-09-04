#!/usr/bin/env python3
"""ACOS PF-1 benchmark registration validator."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
PHASE = "PF-1"
FOUNDATION_PF_BASELINE_SHA = "525eeb02b8eecc88845e5ed1e8aecbbaa4393d7f"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SCHEMA_PATH = REPO / "benchmarks" / "templates" / "BENCHMARK_REGISTRATION.schema.yaml"

BM_ID_RE = re.compile(r"^BM-\d{3}$")
FORBIDDEN_SKILL_ROUTING = re.compile(r"\b(ACOS-\d{2}|EXT-[A-Z0-9-]+)\b")
LICENSE_BYPASS = re.compile(
    r"license_review_acknowledged|bypass.*license|whitelist.*EXT-FE|despite unresolved license",
    re.I,
)
GLOBAL_AESTHETIC = re.compile(
    r"global.*(aesthetic|house style)|promote.*global|house style for all benchmarks|always use glassmorphism",
    re.I,
)
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

EXECUTABLE_POLICY_KEYS = (
    "normalized_brief",
    "functional_requirements",
    "creative_requirements",
    "acceptance_contract",
    "tool_requirements",
    "capability_expectations",
    "constraint_evaluation",
    "hard_failures",
    "evidence_plan",
    "classification",
    "references",
    "assets",
)

PF1_ALLOWED_CHANGE_PREFIXES = (
    "registry/BENCHMARKS.yaml",
    "registry/PHASES.yaml",
    "benchmarks/",
    "validation/benchmark_scope.py",
    "validation/validate_benchmark_registration.py",
    "validation/tests/benchmark/",
    "validation/validate_foundation.py",
    "validation/validate_cross_phase_consistency.py",
    "validation/validate_runtime_integration.py",
    "validation/validate_external_skills.py",
    "validation/validate_proprietary_skills.py",
    "validation/validate_tools.py",
    "validation/validate_foundation_adversarial.py",
    "validation/certify_foundation.py",
    "docs/PF1_BENCHMARK_REGISTRATION_AUDIT.md",
    "docs/PROGRESS_LEDGER.md",
    "IMPLEMENTATION_CHECKLIST.md",
)

FORBIDDEN_FOUNDATION_PATHS = (
    "core/",
    "skills/acos/",
    "runtime/",
    "adapters/",
    "registry/ROUTING_POLICY.yaml",
    "registry/RUNTIME_POLICY.yaml",
    "ACOS_FINAL_CANONICAL_v1.2.md",
    "AGENTS.md",
)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _path_label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


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


def load_schema_hash_excludes() -> frozenset[str]:
    if not SCHEMA_PATH.is_file() or yaml is None:
        return HASH_EXCLUDES
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    excludes = schema.get("hash_excludes") if isinstance(schema, dict) else None
    if isinstance(excludes, list):
        return frozenset(str(x) for x in excludes)
    return HASH_EXCLUDES


def validate_hash_excludes_parity(errors: list[str]) -> None:
    schema_excludes = load_schema_hash_excludes()
    if schema_excludes != HASH_EXCLUDES:
        missing = sorted(schema_excludes - HASH_EXCLUDES)
        extra = sorted(HASH_EXCLUDES - schema_excludes)
        fail(
            errors,
            f"hash_excludes drift: schema-only={missing}, code-only={extra}",
        )


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


def _serialize_policy_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return yaml.dump(value, default_flow_style=False) if yaml else str(value)


def _validate_no_skill_routing_text(text: str, context: str, errors: list[str]) -> None:
    lowered = text.lower()
    if "activate:" in lowered or "activated_skill_ids" in lowered:
        if FORBIDDEN_SKILL_ROUTING.search(text):
            fail(errors, f"Manual skill routing forbidden in {context}")
    if "routing_override" in lowered:
        fail(errors, f"Routing override forbidden in {context}")


def _validate_executable_policy_text(text: str, context: str, errors: list[str]) -> None:
    if GLOBAL_AESTHETIC.search(text):
        fail(errors, f"Global aesthetic promotion forbidden in {context}")
    if LICENSE_BYPASS.search(text):
        fail(errors, f"License bypass forbidden in executable contract field: {context}")
    for marker in FABRICATION_MARKERS:
        if marker in text:
            fail(errors, f"Fabricated requirement marker in {context}: {marker}")


def _validate_constraint_evaluation(items: Any, bid: str, errors: list[str]) -> None:
    if not isinstance(items, list):
        return
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        ctx = f"{bid}.constraint_evaluation[{idx}]"
        for key in ("status", "reason_code", "reason"):
            if key in item:
                _validate_executable_policy_text(str(item[key]), f"{ctx}.{key}", errors)
        if item.get("status") in ("APPROVED", "APPROVED_CONSTRAINT") and item.get("reason_code") == "LICENSE_OVERRIDE":
            fail(errors, f"{ctx}: cannot approve license override in executable contract")


def _validate_executable_contract_fields(data: dict[str, Any], bid: str, errors: list[str]) -> None:
    if "activate" in data or "activated_skill_ids" in data:
        _validate_no_skill_routing_text(_serialize_policy_value(data), bid, errors)

    for key in EXECUTABLE_POLICY_KEYS:
        if key not in data:
            continue
        if key == "constraint_evaluation":
            _validate_constraint_evaluation(data[key], bid, errors)
            continue
        text = _serialize_policy_value(data[key])
        _validate_executable_policy_text(text, f"{bid}.{key}", errors)
        _validate_no_skill_routing_text(text, f"{bid}.{key}", errors)

    if data.get("global_memory_promotion"):
        fail(errors, f"{bid}: global memory promotion forbidden in PF-1")

    for req_list_name in ("functional_requirements", "creative_requirements"):
        for req in data.get(req_list_name) or []:
            if not isinstance(req, dict):
                continue
            source = req.get("source") or {}
            if isinstance(source, dict) and source.get("type") == "operator":
                if source.get("source_ref") == "operator_input.original_text":
                    fail(errors, f"{bid}: requirement cannot masquerade as verbatim operator_input")


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


def validate_registry_data(registry: dict[str, Any], errors: list[str]) -> None:
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
        bid = str(entry.get("benchmark_id", ""))
        if not BM_ID_RE.fullmatch(bid):
            fail(errors, f"Invalid benchmark_id in registry: {bid}")
        if bid in seen:
            fail(errors, f"Duplicate benchmark_id in registry: {bid}")
        seen.add(bid)

        if entry.get("status") == "FROZEN":
            _validate_registry_frozen_lock(entry, errors)


def _validate_registry_frozen_lock(entry: dict[str, Any], errors: list[str]) -> None:
    bid = entry.get("benchmark_id")
    reg_path_rel = entry.get("registration_path", f"benchmarks/{bid}/REGISTRATION.yaml")
    reg_path = REPO / reg_path_rel
    if not reg_path.is_file():
        fail(errors, f"{bid}: FROZEN registry entry missing registration file: {reg_path_rel}")
        return

    reg_data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    if not isinstance(reg_data, dict):
        fail(errors, f"{bid}: registration file must be a mapping")
        return

    registry_hash = entry.get("frozen_contract_sha256")
    embedded_hash = reg_data.get("benchmark_contract_sha256") or reg_data.get("contract_hash")
    computed_hash = canonical_hash(reg_data)

    if not registry_hash:
        fail(errors, f"{bid}: FROZEN registry entry requires frozen_contract_sha256")
    if not embedded_hash:
        fail(errors, f"{bid}: FROZEN registration requires benchmark_contract_sha256")
    if registry_hash and embedded_hash and str(registry_hash) != str(embedded_hash):
        fail(errors, f"{bid}: registry frozen_contract_sha256 != registration embedded hash")
    if registry_hash and str(registry_hash) != computed_hash:
        fail(errors, f"{bid}: registry frozen_contract_sha256 != computed contract hash")
    if embedded_hash and str(embedded_hash) != computed_hash:
        fail(errors, f"{bid}: registration embedded hash != computed contract hash")

    reg_version = str(reg_data.get("contract_version", ""))
    entry_version = str(entry.get("contract_version", ""))
    if entry_version and reg_version and entry_version != reg_version:
        fail(errors, f"{bid}: registry contract_version != registration contract_version")

    versions = entry.get("versions") or []
    if isinstance(versions, list) and versions:
        frozen_versions = [
            v for v in versions if isinstance(v, dict) and v.get("contract_version") == entry_version
        ]
        if len(frozen_versions) != 1:
            fail(errors, f"{bid}: versions history must contain exactly one record for contract_version {entry_version}")


def validate_registry(errors: list[str]) -> None:
    registry = load_yaml(REPO / "registry" / "BENCHMARKS.yaml", errors)
    if registry:
        validate_registry_data(registry, errors)


def validate_infrastructure(errors: list[str]) -> None:
    required = [
        REPO / "benchmarks" / "README.md",
        SCHEMA_PATH,
        REPO / "benchmarks" / "templates" / "BENCHMARK_BRIEF.template.yaml",
        REPO / "benchmarks" / "templates" / "ACCEPTANCE_CONTRACT.template.yaml",
        REPO / "benchmarks" / "templates" / "EVIDENCE_PLAN.template.yaml",
        REPO / "validation" / "validate_benchmark_registration.py",
    ]
    for path in required:
        if not path.is_file():
            fail(errors, f"Missing PF-1 infrastructure: {path.relative_to(REPO)}")


def validate_registration_file(reg_path: Path, errors: list[str]) -> None:
    data = load_yaml(reg_path, errors)
    if not data:
        return

    bid = data.get("benchmark_id", "")
    if not BM_ID_RE.fullmatch(str(bid)):
        fail(errors, f"{_path_label(reg_path)}: invalid benchmark_id")

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

    _validate_executable_contract_fields(data, str(bid), errors)

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
    if isinstance(revision, dict):
        if revision.get("parent_version") and not revision.get("version"):
            fail(errors, f"{bid}: revision.version required when parent_version set")
        if revision.get("version") and not revision.get("reason"):
            fail(errors, f"{bid}: revision.reason required when version present")


def validate_frozen_lock_against_registry(
    registration: dict[str, Any],
    registry_entry: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate triple-hash anchoring for fixture/tests without filesystem registry."""
    bid = registration.get("benchmark_id", "BM-???")
    registry_hash = registry_entry.get("frozen_contract_sha256")
    embedded_hash = registration.get("benchmark_contract_sha256")
    computed = canonical_hash(registration)

    if str(registry_hash) != str(embedded_hash):
        fail(errors, f"{bid}: registry anchor != embedded hash (independent lock violation)")
    if str(registry_hash) != computed:
        fail(errors, f"{bid}: registry anchor != computed hash (silent mutation detected)")
    if str(embedded_hash) != computed:
        fail(errors, f"{bid}: embedded hash != computed hash")

    if str(registry_entry.get("contract_version", "")) != str(registration.get("contract_version", "")):
        fail(errors, f"{bid}: registry/registration contract_version mismatch")


def validate_benchmark_directories(errors: list[str]) -> None:
    for path in (REPO / "benchmarks").glob("BM-*"):
        if not path.is_dir():
            continue
        reg = path / "REGISTRATION.yaml"
        if not reg.is_file():
            fail(errors, f"Missing REGISTRATION.yaml in {path.relative_to(REPO)}")
            continue
        validate_registration_file(reg, errors)
        for artifact in ("ACCEPTANCE_CONTRACT.yaml", "EVIDENCE_PLAN.yaml"):
            ap = path / artifact
            if ap.is_file():
                data = yaml.safe_load(ap.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    _validate_executable_contract_fields(data, path.name, errors)


def validate_no_execution_artifacts(errors: list[str]) -> None:
    from benchmark_scope import is_forbidden_execution_artifact

    for path in (REPO / "benchmarks").rglob("*"):
        if path.is_file() and is_forbidden_execution_artifact(path):
            fail(errors, f"Benchmark execution artifact forbidden in PF-1: {path.relative_to(REPO)}")


def _normalize_changed_path(path: str) -> str:
    return path.replace("\\", "/")


def _is_allowed_pf1_change(path: str) -> bool:
    norm = _normalize_changed_path(path)
    return any(norm == prefix or norm.startswith(prefix) for prefix in PF1_ALLOWED_CHANGE_PREFIXES)


def _is_forbidden_foundation_change(path: str) -> bool:
    norm = _normalize_changed_path(path)
    for forbidden in FORBIDDEN_FOUNDATION_PATHS:
        if forbidden.endswith(".yaml") or forbidden.endswith(".md"):
            if norm == forbidden:
                return True
        elif norm.startswith(forbidden):
            return True
    return False


def classify_changed_paths(changed_paths: list[str]) -> list[str]:
    violations: list[str] = []
    for raw in changed_paths:
        path = _normalize_changed_path(raw.strip())
        if not path:
            continue
        if _is_forbidden_foundation_change(path):
            violations.append(f"forbidden foundation path changed: {path}")
        elif not _is_allowed_pf1_change(path):
            violations.append(f"unexpected path changed since PF baseline: {path}")
    return violations


def _git_changed_paths(baseline_sha: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", baseline_sha, "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def validate_foundation_unmodified(errors: list[str]) -> None:
    changed = _git_changed_paths(FOUNDATION_PF_BASELINE_SHA)
    if not changed:
        return
    for violation in classify_changed_paths(changed):
        fail(errors, violation)


def main() -> int:
    errors: list[str] = []
    print("ACOS PF-1 Benchmark Registration Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    validate_hash_excludes_parity(errors)
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
