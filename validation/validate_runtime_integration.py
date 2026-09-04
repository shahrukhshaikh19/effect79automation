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


def validate_license_enforcement(errors: list[str]) -> None:
    """F-C1: acknowledgment must not bypass canonical license blocks."""
    engine_text = load_text(REPO / "runtime" / "routing" / "engine.py")
    if "license_review_acknowledged" in engine_text:
        fail(errors, "routing/engine.py must not use license_review_acknowledged as bypass")
    policy_text = load_text(REPO / "registry" / "ROUTING_POLICY.yaml")
    if "activation_requires: license_review_acknowledged" in policy_text:
        fail(errors, "ROUTING_POLICY must not require license_review_acknowledged for activation")

    sys.path.insert(0, str(REPO))
    try:
        from runtime.common.registry_loader import is_skill_license_blocked
        from runtime.intake.normalize import normalize_intake
        from runtime.routing.engine import route_task

        if not is_skill_license_blocked("EXT-FE-01"):
            fail(errors, "EXT-FE-01 must be license-blocked per canonical lock")
        intake = normalize_intake(
            {
                "task_id": "val-license",
                "request": "test",
                "normalized_goal": "test frontend",
                "task_signals": {
                    "deliverable_profile": "standard_application",
                    "requires_frontend": True,
                    "license_review_acknowledged": True,
                },
                "runtime_capabilities": {"browser": "AVAILABLE"},
            }
        )
        decision = route_task(intake)
        if "EXT-FE-01" in decision.get("activated_skill_ids", []):
            fail(errors, "EXT-FE-01 activated despite blocked_pending_license_review")
    except Exception as exc:
        fail(errors, f"License enforcement probe failed: {exc}")


def validate_correction_routing_policy(errors: list[str]) -> None:
    """F-C2: correction routing must consume policy, not hard-coded skill IDs."""
    route_py = REPO / "runtime" / "correction" / "route.py"
    budget_py = REPO / "runtime" / "correction" / "budget.py"
    if not route_py.is_file():
        fail(errors, "Missing runtime/correction/route.py")
        return
    budget_text = load_text(budget_py)
    if '"ACOS-01"' in budget_text or "'ACOS-01'" in budget_text:
        fail(errors, "correction/budget.py must not hard-code ACOS-01 fallback")
    policy = yaml.safe_load((REPO / "registry" / "ROUTING_POLICY.yaml").read_text(encoding="utf-8"))
    if "correction_responsibility" not in policy:
        fail(errors, "ROUTING_POLICY missing correction_responsibility section")

    sys.path.insert(0, str(REPO))
    try:
        from runtime.correction.route import route_defect_to_skill

        unknown = route_defect_to_skill("nonexistent_defect_type_xyz")
        if unknown.get("status") != "CORRECTION_ROUTING_REQUIRES_RESOLUTION":
            fail(errors, "Unknown defect must escalate, not silently route")
        if "ACOS-01" in unknown.get("responsible_skill_ids", []):
            fail(errors, "Unknown defect must not default to ACOS-01")
    except Exception as exc:
        fail(errors, f"Correction routing probe failed: {exc}")


def validate_design_gate_guard(errors: list[str]) -> None:
    """F-C3: Design Gate must be enforced via transition guard."""
    transitions = REPO / "runtime" / "state" / "transitions.py"
    if not transitions.is_file():
        fail(errors, "Missing runtime/state/transitions.py")
        return
    text = load_text(transitions)
    if "can_transition" not in text:
        fail(errors, "transitions.py must implement can_transition")
    if "TRANSITION_BLOCKED_DESIGN_GATE" not in text:
        fail(errors, "Design gate block reason missing")

    sys.path.insert(0, str(REPO))
    try:
        from runtime.state.execution import create_execution_state
        from runtime.state.transitions import can_transition, set_design_gate_state

        state = create_execution_state("probe")
        set_design_gate_state(state, "PENDING")
        blocked = can_transition(state, "PRODUCTION")
        if blocked.get("allowed"):
            fail(errors, "PRODUCTION must be blocked when Design Gate PENDING")
        set_design_gate_state(state, "APPROVED")
        allowed = can_transition(state, "PRODUCTION")
        if not allowed.get("allowed"):
            fail(errors, "PRODUCTION must be allowed when Design Gate APPROVED")
    except Exception as exc:
        fail(errors, f"Design gate probe failed: {exc}")


def validate_memory_semantics(errors: list[str]) -> None:
    mem = REPO / "runtime" / "memory" / "records.py"
    if not mem.is_file():
        fail(errors, "Missing runtime/memory/records.py")
        return
    text = load_text(mem)
    if "create_memory_observation" not in text:
        fail(errors, "Memory must provide create_memory_observation")
    if "promote_memory" not in text:
        fail(errors, "Memory must provide stateful promote_memory")
    if "subject_key" not in text:
        fail(errors, "Memory conflict model requires subject_key")
    if "MEMORY_CONFLICT_REQUIRES_RESOLUTION" not in text:
        fail(errors, "Memory conflict status missing")

    sys.path.insert(0, str(REPO))
    try:
        from runtime.memory.records import create_memory_observation, create_memory_record, detect_conflicts, promote_memory

        try:
            create_memory_record(
                memory_id="x",
                category="knowledge",
                scope="project",
                statement="s",
                source_task_id="t",
                evidence_refs=["e"],
                promotion_level="validated-global",
                subject_key="k",
                value="v",
            )
            fail(errors, "Direct validated-global creation must fail")
        except ValueError:
            pass

        a = create_memory_observation(
            memory_id="a",
            category="knowledge",
            scope="project",
            statement="same",
            source_task_id="t1",
            evidence_refs=["e1"],
            subject_key="topic.x",
            value="alpha",
        )
        b = create_memory_observation(
            memory_id="b",
            category="knowledge",
            scope="project",
            statement="same",
            source_task_id="t2",
            evidence_refs=["e2"],
            subject_key="topic.x",
            value="alpha",
        )
        b = promote_memory(b, "project-rule", ["e3"])
        if detect_conflicts([a, b]):
            fail(errors, "Same subject+value at different promotion levels must not conflict")
    except Exception as exc:
        fail(errors, f"Memory semantics probe failed: {exc}")


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
    for tid in range(1, 35):
        if f"test_t{tid}" not in text.lower() and f"t{tid}_" not in text.lower():
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
    validate_license_enforcement(errors)
    validate_correction_routing_policy(errors)
    validate_design_gate_guard(errors)
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
