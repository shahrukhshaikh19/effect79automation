#!/usr/bin/env python3
"""ACOS PF-2 benchmark execution validator."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmark_scope import get_post_foundation_state, is_pf2_execution_path
from validation.validate_benchmark_registration import canonical_hash, load_yaml

FROZEN_CONTRACT_HASH = "b2cb2dbaea31e07331fe1c94df1271e3c167f9a64461e2dc25410d13696cadf3"
FROZEN_SOURCE_SHA = "18f52a8216c897b08d8dd27cb4f7b14e97b9b955"
REQUIRED_EVIDENCE = ("E-001", "E-002", "E-005", "E-007", "E-008", "E-009", "E-010")


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def validate_phase_state(errors: list[str]) -> None:
    pf = get_post_foundation_state()
    if pf.get("PF-1") != "COMPLETE":
        fail(errors, "PF-2 requires PF-1 COMPLETE")
    pf2 = pf.get("PF-2", "NOT_STARTED")
    if pf2 not in ("IN_PROGRESS", "COMPLETE"):
        fail(errors, f"PF-2 must be IN_PROGRESS or COMPLETE for execution validation, got {pf2}")
    for other in ("PF-3", "PF-4", "PF-5"):
        if pf.get(other) != "NOT_STARTED":
            fail(errors, f"{other} must remain NOT_STARTED during PF-2")


def validate_frozen_contract(errors: list[str]) -> dict[str, Any] | None:
    reg_path = REPO / "benchmarks" / "BM-001" / "REGISTRATION.yaml"
    if not reg_path.is_file():
        fail(errors, "Missing BM-001 REGISTRATION.yaml")
        return None
    data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    if data.get("benchmark_contract_sha256") != FROZEN_CONTRACT_HASH:
        fail(errors, "BM-001 contract hash mismatch — frozen contract altered")
    computed = canonical_hash(data)
    if computed != FROZEN_CONTRACT_HASH:
        fail(errors, "BM-001 canonical hash recomputation failed — contract mutated")
    if data.get("status") != "FROZEN":
        fail(errors, "BM-001 registration status must remain FROZEN (execution via execution_state)")
    if data.get("global_memory_promotion") is not False:
        fail(errors, "BM-001 global_memory_promotion must remain false")
    return data


def validate_implementation(errors: list[str]) -> None:
    impl = REPO / "benchmarks" / "BM-001" / "execution" / "implementation"
    for name in ("index.html", "styles.css", "main.js"):
        if not (impl / name).is_file():
            fail(errors, f"Missing implementation artifact: {name}")


def validate_execution_report(errors: list[str], pf2: str) -> dict[str, Any] | None:
    report_path = REPO / "benchmarks" / "BM-001" / "execution" / "run" / "EXECUTION_REPORT.yaml"
    if pf2 == "IN_PROGRESS" and not report_path.is_file():
        return None
    if not report_path.is_file():
        fail(errors, "Missing EXECUTION_REPORT.yaml")
        return None
    report = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
    if report.get("contract_hash") != FROZEN_CONTRACT_HASH:
        fail(errors, "EXECUTION_REPORT contract_hash mismatch")
    if not report.get("routing_id"):
        fail(errors, "EXECUTION_REPORT missing routing_id")
    if not report.get("design_gate_result"):
        fail(errors, "EXECUTION_REPORT missing design_gate_result")
    if pf2 == "COMPLETE":
        if report.get("benchmark_result") not in ("PASS", "FAIL", "BLOCKED"):
            fail(errors, "PF-2 COMPLETE requires truthful benchmark_result")
        if not report.get("quality_gate_result"):
            fail(errors, "EXECUTION_REPORT missing quality_gate_result")
    return report


def validate_evidence_artifacts(errors: list[str], report: dict[str, Any] | None) -> None:
    if not report:
        return
    captured = set(report.get("evidence_captured") or [])
    for eid in REQUIRED_EVIDENCE:
        if eid not in captured and report.get("design_gate_result") == "APPROVED":
            fail(errors, f"Missing required evidence: {eid}")
    evidence_root = REPO / "benchmarks" / "BM-001" / "execution" / "evidence"
    if report.get("design_gate_result") == "APPROVED" and not evidence_root.is_dir():
        fail(errors, "Missing evidence directory")


def validate_no_global_memory_promotion(errors: list[str]) -> None:
    report_path = REPO / "benchmarks" / "BM-001" / "execution" / "run" / "EXECUTION_REPORT.yaml"
    if not report_path.is_file():
        return
    text = report_path.read_text(encoding="utf-8").lower()
    if "global_memory_promotion: true" in text.replace(" ", ""):
        fail(errors, "BM-001 aesthetic must not be promoted to global memory")


def validate_execution_scope(errors: list[str]) -> None:
    bm_root = REPO / "benchmarks" / "BM-001"
    for item in bm_root.rglob("*"):
        if not item.is_file():
            continue
        if item.suffix.lower() in {".html", ".css", ".js"} and not is_pf2_execution_path(item):
            fail(errors, f"Execution artifact outside execution/: {item.relative_to(REPO)}")


def main() -> int:
    errors: list[str] = []
    print("ACOS PF-2 Benchmark Execution Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    pf = get_post_foundation_state()
    pf2 = pf.get("PF-2", "NOT_STARTED")

    validate_phase_state(errors)
    validate_frozen_contract(errors)
    validate_implementation(errors)
    validate_execution_scope(errors)
    report = validate_execution_report(errors, pf2)
    validate_evidence_artifacts(errors, report)
    validate_no_global_memory_promotion(errors)

    runner = REPO / "validation" / "benchmark_execution" / "run_bm001.py"
    if not runner.is_file():
        fail(errors, "Missing validation/benchmark_execution/run_bm001.py")

    if errors:
        print("VALIDATION: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("VALIDATION: PASSED")
    if report:
        print(f"BM-001 result: {report.get('benchmark_result')} score={report.get('benchmark_score')}")
    print(f"PF-2 state: {pf2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
