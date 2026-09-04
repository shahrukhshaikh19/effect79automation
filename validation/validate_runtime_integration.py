#!/usr/bin/env python3
"""ACOS Phase F runtime integration validator."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
PHASE = "F"

RUNTIME_MODULES = (
    "intake",
    "routing",
    "handoff",
    "evidence",
    "quality",
    "correction",
    "memory",
    "state",
    "adapter",
)

REQUIRED_SCHEMAS = (
    "TASK_INTAKE.schema.yaml",
    "ROUTING_DECISION.schema.yaml",
    "HANDOFF.schema.yaml",
    "EVIDENCE_REF.schema.yaml",
    "CORRECTION_REQUEST.schema.yaml",
    "MEMORY_RECORD.schema.yaml",
    "EXECUTION_STATE.schema.yaml",
    "ADAPTER_TASK_PACKET.schema.yaml",
)

FORBIDDEN_MONOLITH = REPO / "runtime" / "orchestrator.py"
MAX_MONOLITH_LINES = 800

VENDOR_PATTERNS = [
    re.compile(r"\bclaude\b.*required", re.I),
    re.compile(r"\bcursor\b.*required", re.I),
    re.compile(r"\bcodex\b.*required", re.I),
    re.compile(r"only works with anthropic", re.I),
]

DOMAIN_FORBIDDEN = re.compile(
    r"\bcoffee\b|\bcrypto portfolio\b|\bluxury brand default\b|\bcinematic website default\b",
    re.I,
)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_architecture(errors: list[str]) -> None:
    runtime = REPO / "runtime"
    if not runtime.is_dir():
        fail(errors, "Missing runtime/ directory")
        return
    if FORBIDDEN_MONOLITH.is_file():
        fail(errors, "Forbidden monolith runtime/orchestrator.py present")
    for mod in RUNTIME_MODULES:
        if not (runtime / mod).is_dir():
            fail(errors, f"Missing runtime module: {mod}")
    schemas = runtime / "schemas"
    if not schemas.is_dir():
        fail(errors, "Missing runtime/schemas/")
        return
    for name in REQUIRED_SCHEMAS:
        path = schemas / name
        if not path.is_file():
            fail(errors, f"Missing schema: {name}")
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            fail(errors, f"Schema not a mapping: {name}")

    for py in runtime.rglob("*.py"):
        if py.name == "__init__.py":
            continue
        lines = py.read_text(encoding="utf-8").splitlines()
        if len(lines) > MAX_MONOLITH_LINES:
            fail(errors, f"Module exceeds monolith threshold ({MAX_MONOLITH_LINES} lines): {py.relative_to(REPO)}")

    for pat in VENDOR_PATTERNS:
        for py in runtime.rglob("*.py"):
            if pat.search(load_text(py)):
                fail(errors, f"Vendor hard dependency pattern in {py.relative_to(REPO)}")


def validate_routing_ownership(errors: list[str]) -> None:
    packet = REPO / "runtime" / "schemas" / "ADAPTER_TASK_PACKET.schema.yaml"
    if packet.is_file():
        text = load_text(packet)
        if "phase_f_router" not in text:
            fail(errors, "ADAPTER_TASK_PACKET must declare phase_f_router as routing source")
        if "adapter_must_not" not in text:
            fail(errors, "ADAPTER_TASK_PACKET must forbid adapter rerouting")
    engine = REPO / "runtime" / "routing" / "engine.py"
    if engine.is_file() and "route_task" not in load_text(engine):
        fail(errors, "routing/engine.py must implement route_task")
    local = REPO / "adapters" / "local" / "TASK_PACKET.schema.yaml"
    if local.is_file():
        lt = load_text(local)
        if "phase f" not in lt.lower() and "phase_f" not in lt.lower():
            if "external_caller" not in lt:
                fail(errors, "Local TASK_PACKET should reference Phase F routing input")


def validate_policies(errors: list[str]) -> None:
    for name in ("ROUTING_POLICY.yaml", "RUNTIME_POLICY.yaml"):
        path = REPO / "registry" / name
        if not path.is_file():
            fail(errors, f"Missing registry/{name}")
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "authority" not in data:
            fail(errors, f"registry/{name} missing authority field")

    runtime_policy = yaml.safe_load((REPO / "registry" / "RUNTIME_POLICY.yaml").read_text(encoding="utf-8"))
    qg = runtime_policy.get("quality_gate", {})
    statuses = set(qg.get("terminal_statuses", []))
    if statuses != {"APPROVED", "REJECTED", "BLOCKED_INSUFFICIENT_EVIDENCE"}:
        fail(errors, "RUNTIME_POLICY quality_gate terminal_statuses incorrect")
    if "HR-11" not in qg.get("forbidden_ids", []):
        fail(errors, "RUNTIME_POLICY must forbid HR-11")
    correction = runtime_policy.get("correction", {})
    if "default_retry_budget" not in correction:
        fail(errors, "RUNTIME_POLICY missing correction retry budget")


def validate_quality_semantics(errors: list[str]) -> None:
    gate_py = REPO / "runtime" / "quality" / "gate.py"
    if not gate_py.is_file():
        fail(errors, "Missing runtime/quality/gate.py")
        return
    text = load_text(gate_py)
    if "BLOCKED_INSUFFICIENT_EVIDENCE" not in text:
        fail(errors, "Quality gate must handle BLOCKED_INSUFFICIENT_EVIDENCE")
    if "HR-11" in text and "FORBIDDEN" not in text:
        fail(errors, "HR-11 must not be accepted as valid gate id")
    if "validate_producer_independence" not in text:
        fail(errors, "Producer self-approval guard missing")


def validate_memory_semantics(errors: list[str]) -> None:
    mem = REPO / "runtime" / "memory" / "records.py"
    if not mem.is_file():
        fail(errors, "Missing runtime/memory/records.py")
        return
    text = load_text(mem)
    if "observation" not in text or "validated-global" not in text:
        fail(errors, "Memory promotion lifecycle not represented")
    if "MEMORY_CONFLICT_REQUIRES_RESOLUTION" not in text:
        fail(errors, "Memory conflict status missing")
    if "memory_overrides_authority" not in text:
        fail(errors, "Memory authority override guard missing")


def validate_phase_boundaries(errors: list[str]) -> None:
    phases = yaml.safe_load((REPO / "registry" / "PHASES.yaml").read_text(encoding="utf-8"))
    foundation = phases.get("execution_state", {}).get("foundation", {})
    if foundation.get("F") != "COMPLETE":
        fail(errors, "registry/PHASES.yaml must mark F COMPLETE after Phase F")
    if foundation.get("G") != "NOT_STARTED":
        fail(errors, "Phase G must remain NOT_STARTED")
    if phases.get("execution_state", {}).get("post_foundation") != "NOT_STARTED":
        fail(errors, "post_foundation must remain NOT_STARTED")
    if phases.get("foundation_ready_marker") and "FOUNDATION_READY" in str(phases):
        pass  # marker name allowed; must not be declared true
    ledger = REPO / "docs" / "PROGRESS_LEDGER.md"
    if ledger.is_file() and re.search(r"FOUNDATION_READY:\s*true", load_text(ledger), re.I):
        fail(errors, "FOUNDATION_READY must not be declared true")
    for name in ("benchmarks", "projects"):
        for item in (REPO / name).rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file() and item.stat().st_size > 0:
                fail(errors, f"{name}/ must remain empty: {item.relative_to(REPO)}")


def validate_domain_neutrality(errors: list[str]) -> None:
    for py in (REPO / "runtime").rglob("*.py"):
        if DOMAIN_FORBIDDEN.search(load_text(py)):
            fail(errors, f"Domain-specific default in {py.relative_to(REPO)}")


def validate_tests_exist(errors: list[str]) -> None:
    tests = REPO / "validation" / "tests" / "runtime" / "test_scenarios.py"
    if not tests.is_file():
        fail(errors, "Missing validation/tests/runtime/test_scenarios.py")
        return
    text = load_text(tests)
    for tid in range(1, 19):
        if f"test_t{tid}" not in text.lower() and f"def t{t}" not in text.lower():
            # allow test_t1_minimal or test_t01 naming
            if f"t{t}" not in text.lower() or "T" + str(tid) not in text:
                if f"T{tid}" not in text and f"t{t}_" not in text.lower():
                    fail(errors, f"Test scenario T{tid} not found in test_scenarios.py")


def validate_smoke_executable(errors: list[str]) -> None:
    smoke = REPO / "runtime" / "smoke.py"
    if not smoke.is_file():
        fail(errors, "Missing runtime/smoke.py")
        return
    if "run_smoke" not in load_text(smoke):
        fail(errors, "runtime/smoke.py must define run_smoke()")


def run_runtime_tests(errors: list[str]) -> None:
    tests = REPO / "validation" / "tests" / "runtime" / "test_scenarios.py"
    if not tests.is_file():
        return
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "validation.tests.runtime.test_scenarios", "-v"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    if result.returncode != 0:
        fail(errors, f"Runtime tests failed:\n{result.stdout}\n{result.stderr}")


def main() -> int:
    errors: list[str] = []
    if yaml is None:
        fail(errors, "PyYAML required")
        return 1

    print(f"ACOS v1.2 Phase {PHASE} Runtime Integration Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    validate_architecture(errors)
    validate_policies(errors)
    validate_routing_ownership(errors)
    validate_quality_semantics(errors)
    validate_memory_semantics(errors)
    validate_domain_neutrality(errors)
    validate_smoke_executable(errors)
    validate_tests_exist(errors)
    validate_phase_boundaries(errors)
    run_runtime_tests(errors)

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print("Phase F runtime integration checks complete.")
    print("Phase G certification: outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
