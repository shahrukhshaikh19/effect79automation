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
PF1_COMPATIBILITY_LOCK_PATH = REPO / "validation" / "PF1_FOUNDATION_COMPATIBILITY_LOCK.yaml"

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

PF1_OWNED_CHANGE_PREFIXES = (
    "registry/BENCHMARKS.yaml",
    "registry/PHASES.yaml",
    "benchmarks/",
    "validation/benchmark_scope.py",
    "validation/validate_benchmark_registration.py",
    "validation/tests/benchmark/",
    "validation/PF1_FOUNDATION_COMPATIBILITY_LOCK.yaml",
    "docs/PF1_BENCHMARK_REGISTRATION_AUDIT.md",
    "docs/PROGRESS_LEDGER.md",
    "IMPLEMENTATION_CHECKLIST.md",
)

PF2_OWNED_CHANGE_PREFIXES = (
    "validation/benchmark_execution/",
    "validation/validate_benchmark_execution.py",
    "validation/tests/benchmark/test_execution_adversarial.py",
    "docs/PF2_BENCHMARK_EXECUTION_AUDIT.md",
    "tools/browser/scripts/capture-interaction.mjs",
)

FOUNDATION_COMPATIBILITY_PREFIXES = (
    "validation/validate_",
    "validation/certify_",
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


def _pf2_active() -> bool:
    from benchmark_scope import get_post_foundation_state

    pf = get_post_foundation_state()
    return pf.get("PF-2") in ("IN_PROGRESS", "COMPLETE")


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
    pf2 = pf.get("PF-2", "NOT_STARTED")
    if pf1 == "COMPLETE":
        if pf2 not in ("NOT_STARTED", "IN_PROGRESS", "COMPLETE"):
            fail(errors, f"PF-2 execution state invalid: {pf2}")
    elif pf2 != "NOT_STARTED":
        fail(errors, "PF-2 must remain NOT_STARTED until PF-1 COMPLETE")
    for other in ("PF-3", "PF-4", "PF-5"):
        if pf.get(other) != "NOT_STARTED":
            fail(errors, f"{other} must remain NOT_STARTED during PF-1/PF-2")


def validate_registry_data(
    registry: dict[str, Any],
    errors: list[str],
    *,
    load_from_commit=None,
    find_first_attestation=None,
) -> None:
    load_fn = load_file_from_commit if load_from_commit is None else load_from_commit
    find_fn = find_first_freeze_attestation_commit if find_first_attestation is None else find_first_attestation
    if registry.get("phase") not in ("PF-1", "PF-2"):
        fail(errors, "BENCHMARKS.yaml phase must be PF-1 or PF-2")
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
            _validate_registry_frozen_lock(
                entry,
                errors,
                load_from_commit=load_fn,
                find_first_attestation=find_fn,
            )


def load_compatibility_lock() -> dict[str, str]:
    if not PF1_COMPATIBILITY_LOCK_PATH.is_file() or yaml is None:
        return {}
    data = yaml.safe_load(PF1_COMPATIBILITY_LOCK_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    files = data.get("files") or {}
    if not isinstance(files, dict):
        return {}
    return {str(path): str(spec.get("sha256", "")) for path, spec in files.items() if isinstance(spec, dict)}


def file_content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_foundation_compatibility_path(path: str) -> bool:
    norm = _normalize_changed_path(path)
    return any(norm.startswith(prefix) for prefix in FOUNDATION_COMPATIBILITY_PREFIXES)


def validate_compatibility_lock(errors: list[str]) -> None:
    lock = load_compatibility_lock()
    if not lock:
        fail(errors, "PF1 foundation compatibility lock missing or empty")
        return
    for rel_path, expected_hash in sorted(lock.items()):
        if not expected_hash:
            fail(errors, f"compatibility lock missing sha256 for {rel_path}")
            continue
        file_path = REPO / rel_path
        if not file_path.is_file():
            fail(errors, f"compatibility lock references missing file: {rel_path}")
            continue
        current_hash = file_content_sha256(file_path)
        if current_hash != expected_hash:
            fail(errors, f"foundation compatibility file drift: {rel_path}")


def validate_pf1_allowlist_anchoring(errors: list[str]) -> None:
    lock_paths = set(load_compatibility_lock())
    for rel_path in lock_paths:
        if not (REPO / rel_path).is_file():
            fail(errors, f"compatibility lock references missing file: {rel_path}")


def commit_exists(commit_sha: str) -> tuple[bool, str | None]:
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"{commit_sha}^{{commit}}"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return False, f"unknown commit: {commit_sha}"
    return True, None


def load_file_from_commit(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
    proc = subprocess.run(
        ["git", "show", f"{commit_sha}:{repo_path}"],
        cwd=REPO,
        capture_output=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        if not err:
            err = f"git show failed for {commit_sha}:{repo_path}"
        return None, err
    return proc.stdout.decode("utf-8"), None


def list_registry_file_commits() -> tuple[list[str], str | None]:
    proc = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "--", "registry/BENCHMARKS.yaml"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or "git log failed"
        return [], err
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()], None


def extract_version_attestation(entry: dict[str, Any], contract_version: str) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    bid = entry.get("benchmark_id")
    version = str(contract_version)

    if str(entry.get("contract_version", "")) == version and entry.get("status") == "FROZEN":
        source = entry.get("frozen_source_commit_sha")
        frozen_hash = entry.get("frozen_contract_sha256")
        if source and frozen_hash:
            return {
                "benchmark_id": bid,
                "contract_version": version,
                "frozen_source_commit_sha": source,
                "frozen_contract_sha256": frozen_hash,
                "registration_path": entry.get("registration_path"),
            }

    for ver in entry.get("versions") or []:
        if not isinstance(ver, dict):
            continue
        if str(ver.get("contract_version", "")) != version:
            continue
        source = ver.get("frozen_source_commit_sha")
        frozen_hash = ver.get("frozen_contract_sha256")
        if source and frozen_hash:
            return {
                "benchmark_id": bid,
                "contract_version": version,
                "frozen_source_commit_sha": source,
                "frozen_contract_sha256": frozen_hash,
                "registration_path": ver.get("registration_path") or entry.get("registration_path"),
            }
    return None


def find_frozen_attestation_in_registry(
    registry: dict[str, Any],
    benchmark_id: str,
    contract_version: str,
) -> dict[str, Any] | None:
    benchmarks = registry.get("benchmarks")
    if not isinstance(benchmarks, list):
        return None
    for entry in benchmarks:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("benchmark_id", "")) != benchmark_id:
            continue
        attestation = extract_version_attestation(entry, contract_version)
        if attestation:
            return attestation
    return None


def find_first_freeze_attestation_commit(
    benchmark_id: str,
    contract_version: str,
    *,
    load_from_commit=load_file_from_commit,
    list_commits=list_registry_file_commits,
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    commits, list_err = list_commits()
    if list_err:
        return None, None, list_err
    if yaml is None:
        return None, None, "PyYAML required"

    for commit_sha in commits:
        content, load_err = load_from_commit(commit_sha, "registry/BENCHMARKS.yaml")
        if load_err:
            continue
        registry = yaml.safe_load(content)
        if not isinstance(registry, dict):
            continue
        attestation = find_frozen_attestation_in_registry(registry, benchmark_id, contract_version)
        if attestation:
            record = dict(attestation)
            record["attestation_commit_sha"] = commit_sha
            return commit_sha, record, None

    return None, None, None


def validate_first_freeze_attestation(
    registry_entry: dict[str, Any],
    errors: list[str],
    *,
    find_first_attestation=None,
) -> None:
    find_fn = find_first_freeze_attestation_commit if find_first_attestation is None else find_first_attestation
    bid = str(registry_entry.get("benchmark_id", "BM-???"))
    version = str(registry_entry.get("contract_version", ""))
    if not version:
        fail(errors, f"{bid}: FROZEN registry entry requires contract_version")
        return

    first_commit, first_entry, lookup_err = find_fn(bid, version)
    if lookup_err:
        fail(errors, f"{bid} v{version}: first freeze attestation lookup failed: {lookup_err}")
        return
    if not first_commit or not first_entry:
        fail(errors, f"{bid} v{version}: first freeze attestation not found in git history")
        return

    current_source = registry_entry.get("frozen_source_commit_sha")
    current_hash = registry_entry.get("frozen_contract_sha256")
    first_source = first_entry.get("frozen_source_commit_sha")
    first_hash = first_entry.get("frozen_contract_sha256")

    if str(current_source) != str(first_source):
        fail(
            errors,
            f"{bid} v{version}: frozen_source_commit_sha repointed from first attestation",
        )
    if str(current_hash) != str(first_hash):
        fail(
            errors,
            f"{bid} v{version}: frozen_contract_sha256 rewritten from first attestation",
        )


def validate_frozen_provenance(
    registry_entry: dict[str, Any],
    current_registration: dict[str, Any] | None,
    errors: list[str],
    *,
    load_from_commit=None,
) -> None:
    load_fn = load_file_from_commit if load_from_commit is None else load_from_commit
    bid = str(registry_entry.get("benchmark_id", "BM-???"))
    source_commit = registry_entry.get("frozen_source_commit_sha")
    reg_path_rel = str(registry_entry.get("registration_path", f"benchmarks/{bid}/REGISTRATION.yaml"))
    registry_hash = registry_entry.get("frozen_contract_sha256")

    if not registry_hash:
        fail(errors, f"{bid}: FROZEN registry entry requires frozen_contract_sha256")
    if not source_commit:
        fail(errors, f"{bid}: FROZEN registry entry requires frozen_source_commit_sha")
        return

    exists, commit_err = commit_exists(str(source_commit))
    if not exists:
        fail(errors, f"{bid}: {commit_err}")
        return

    content, load_err = load_fn(str(source_commit), reg_path_rel)
    if load_err:
        fail(errors, f"{bid}: historical registration lookup failed: {load_err}")
        return

    historical_reg = yaml.safe_load(content) if yaml else None
    if not isinstance(historical_reg, dict):
        fail(errors, f"{bid}: historical registration YAML invalid")
        return

    if str(historical_reg.get("benchmark_id", "")) != bid:
        fail(errors, f"{bid}: historical benchmark_id mismatch")

    entry_version = str(registry_entry.get("contract_version", ""))
    hist_version = str(historical_reg.get("contract_version", ""))
    if entry_version and hist_version and entry_version != hist_version:
        fail(errors, f"{bid}: historical contract_version != registry contract_version")

    historical_hash = canonical_hash(historical_reg)
    if registry_hash and str(registry_hash) != historical_hash:
        fail(errors, f"{bid}: registry frozen_contract_sha256 != historical registration hash")

    if current_registration is not None:
        current_hash = canonical_hash(current_registration)
        embedded_hash = current_registration.get("benchmark_contract_sha256") or current_registration.get("contract_hash")

        if str(current_hash) != historical_hash:
            fail(errors, f"{bid}: current registration changed from historical frozen contract")
        if embedded_hash and str(embedded_hash) != historical_hash:
            fail(errors, f"{bid}: embedded hash != historical frozen hash")
        if registry_hash and embedded_hash and str(registry_hash) != str(embedded_hash):
            fail(errors, f"{bid}: registry anchor != embedded hash (independent lock violation)")


def _validate_registry_frozen_lock(
    entry: dict[str, Any],
    errors: list[str],
    *,
    load_from_commit=None,
    find_first_attestation=None,
) -> None:
    load_fn = load_file_from_commit if load_from_commit is None else load_from_commit
    find_fn = find_first_freeze_attestation_commit if find_first_attestation is None else find_first_attestation
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

    validate_first_freeze_attestation(entry, errors, find_first_attestation=find_fn)
    validate_frozen_provenance(entry, reg_data, errors, load_from_commit=load_fn)

    embedded_hash = reg_data.get("benchmark_contract_sha256") or reg_data.get("contract_hash")
    computed_hash = canonical_hash(reg_data)
    if not embedded_hash:
        fail(errors, f"{bid}: FROZEN registration requires benchmark_contract_sha256")
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
        for version_entry in versions:
            if not isinstance(version_entry, dict):
                continue
            if not version_entry.get("frozen_source_commit_sha"):
                continue
            merged_entry = dict(entry)
            merged_entry.update(version_entry)
            validate_first_freeze_attestation(
                merged_entry,
                errors,
                find_first_attestation=find_fn,
            )
            validate_frozen_provenance(
                merged_entry,
                None,
                errors,
                load_from_commit=load_fn,
            )


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

    if status in ("EXECUTION_STARTED", "COMPLETED") and not _pf2_active():
        fail(errors, f"{bid}: PF-2 execution status forbidden during PF-1")

    op = data.get("operator_input") or {}
    if not isinstance(op, dict) or not str(op.get("original_text", "")).strip():
        fail(errors, f"{bid}: operator_input.original_text must be preserved")

    exec_state = data.get("execution_state") or {}
    if not _pf2_active():
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
    *,
    load_from_commit=None,
    find_first_attestation=None,
) -> None:
    """Validate historical freeze provenance for fixture/tests without filesystem registry."""
    load_fn = load_file_from_commit if load_from_commit is None else load_from_commit
    find_fn = find_first_freeze_attestation_commit if find_first_attestation is None else find_first_attestation
    validate_first_freeze_attestation(
        registry_entry,
        errors,
        find_first_attestation=find_fn,
    )
    validate_frozen_provenance(registry_entry, registration, errors, load_from_commit=load_fn)

    bid = registration.get("benchmark_id", "BM-???")
    embedded_hash = registration.get("benchmark_contract_sha256")
    computed = canonical_hash(registration)
    if embedded_hash and str(embedded_hash) != computed:
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
    if _pf2_active():
        return
    from benchmark_scope import is_forbidden_execution_artifact

    for path in (REPO / "benchmarks").rglob("*"):
        if path.is_file() and is_forbidden_execution_artifact(path):
            fail(errors, f"Benchmark execution artifact forbidden in PF-1: {path.relative_to(REPO)}")


def _normalize_changed_path(path: str) -> str:
    return path.replace("\\", "/")


def _is_allowed_pf1_owned_change(path: str) -> bool:
    norm = _normalize_changed_path(path)
    return any(norm == prefix or norm.startswith(prefix) for prefix in PF1_OWNED_CHANGE_PREFIXES)


def _is_locked_compatibility_change(path: str, lock_paths: set[str]) -> bool:
    norm = _normalize_changed_path(path)
    return norm in lock_paths


def _is_forbidden_foundation_change(path: str) -> bool:
    norm = _normalize_changed_path(path)
    for forbidden in FORBIDDEN_FOUNDATION_PATHS:
        if forbidden.endswith(".yaml") or forbidden.endswith(".md"):
            if norm == forbidden:
                return True
        elif norm.startswith(forbidden):
            return True
    return False


def _is_allowed_pf2_owned_change(path: str) -> bool:
    norm = _normalize_changed_path(path)
    return any(norm == prefix or norm.startswith(prefix) for prefix in PF2_OWNED_CHANGE_PREFIXES)


def classify_changed_paths(
    changed_paths: list[str],
    lock_paths: set[str] | None = None,
) -> list[str]:
    violations: list[str] = []
    locked = lock_paths or set(load_compatibility_lock())
    for raw in changed_paths:
        path = _normalize_changed_path(raw.strip())
        if not path:
            continue
        if _is_forbidden_foundation_change(path):
            violations.append(f"forbidden foundation path changed: {path}")
        elif _is_allowed_pf1_owned_change(path):
            continue
        elif _pf2_active() and _is_allowed_pf2_owned_change(path):
            continue
        elif _is_locked_compatibility_change(path, locked):
            continue
        elif _is_foundation_compatibility_path(path):
            violations.append(f"unanchored foundation compatibility file changed: {path}")
        else:
            violations.append(f"unexpected path changed since PF baseline: {path}")
    return violations


def git_changed_paths(baseline_sha: str) -> tuple[list[str], str | None]:
    exists, commit_err = commit_exists(baseline_sha)
    if not exists:
        return [], commit_err or f"unknown baseline commit: {baseline_sha}"

    proc = subprocess.run(
        ["git", "diff", "--name-only", baseline_sha, "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or "git diff failed"
        return [], err
    return [line for line in proc.stdout.splitlines() if line.strip()], None


def validate_foundation_unmodified(errors: list[str]) -> None:
    validate_compatibility_lock(errors)
    validate_pf1_allowlist_anchoring(errors)

    changed, git_err = git_changed_paths(FOUNDATION_PF_BASELINE_SHA)
    if git_err:
        fail(errors, f"foundation git diff failed: {git_err}")
        return
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
    validate_compatibility_lock(errors)
    validate_pf1_allowlist_anchoring(errors)
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
    pf = load_yaml(REPO / "registry" / "PHASES.yaml", errors) or {}
    pf2 = (pf.get("execution_state") or {}).get("post_foundation", {}).get("PF-2", "NOT_STARTED")
    if pf2 == "NOT_STARTED":
        print("PF-2 remains NOT_STARTED.")
    elif pf2 == "IN_PROGRESS":
        print("PF-2 IN_PROGRESS.")
    else:
        print(f"PF-2 {pf2}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
