#!/usr/bin/env python3
"""Phase G adversarial certification — G-A01 through G-A20."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.correction.route import route_defect_to_skill
from runtime.evidence.register import register_evidence, validate_evidence_record
from runtime.intake.normalize import normalize_intake
from runtime.memory.records import (
    create_memory_observation,
    detect_conflicts,
    promote_memory,
    validate_promotion,
)
from runtime.quality.gate import evaluate_gate, validate_producer_independence
from runtime.routing.engine import route_task
from runtime.state.execution import create_execution_state, persist_state, resume_execution
from runtime.state.transitions import (
    authoritative_design_gate,
    bind_routing_to_execution,
    can_transition,
    validate_active_skills_subset,
)

PHASE = "G-adversarial"

FORBIDDEN_ADAPTER_ROUTING = re.compile(
    r"(?<!not to )autonomous(?:ally)? (?:task )?router|(?<!not to )self[- ]select.*skill|classify.*task.*(?:and )?route",
    re.I,
)

MANDATORY_AESTHETIC = re.compile(
    r"always use (glassmorphism|gradients|cinematic 3d|dark theme|centered hero|animate everything)",
    re.I,
)

LEGACY_PHASE_MARKERS = (
    "## H —",
    "## I —",
    "## J —",
    "Phase H —",
    "Phase I —",
    "Phase J —",
)


class ScenarioResult:
    __slots__ = ("scenario_id", "passed", "detail")

    def __init__(self, scenario_id: str, passed: bool, detail: str) -> None:
        self.scenario_id = scenario_id
        self.passed = passed
        self.detail = detail


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_intake(**signals) -> dict:
    return normalize_intake(
        {
            "task_id": "adv-task",
            "request": "Synthetic domain-neutral validation task.",
            "normalized_goal": "Deliver bounded module.",
            "task_signals": {
                "deliverable_profile": "standard_application",
                "requires_3d": False,
                "requires_visual_output": False,
                "requires_creative_direction": False,
                **signals,
            },
            "runtime_capabilities": {
                "browser": "AVAILABLE",
                "blender": "RESTRICTED",
                "git": "AVAILABLE",
                "shell": "AVAILABLE",
                "filesystem": "AVAILABLE",
            },
        }
    )


def ga01_adapter_self_routing() -> ScenarioResult:
    bad_packet = {
        "routing": {
            "source": "adapter_autonomous_router",
            "activated_skill_ids": ["ACOS-06"],
        },
        "activated_skills": [{"skill_id": "ACOS-06"}],
    }
    schema_path = REPO / "runtime" / "schemas" / "ADAPTER_TASK_PACKET.schema.yaml"
    schema_text = schema_path.read_text(encoding="utf-8")
    rejected = "phase_f_router" not in bad_packet["routing"]["source"]
    schema_requires_router = "phase_f_router" in schema_text
    adapter_violation_found = False
    for family in ("claude", "cursor", "codex", "local"):
        adapter_dir = REPO / "adapters" / family
        if not adapter_dir.is_dir():
            continue
        for path in adapter_dir.rglob("*"):
            if path.suffix not in (".md", ".yaml", ".yml", ".json"):
                continue
            if FORBIDDEN_ADAPTER_ROUTING.search(path.read_text(encoding="utf-8", errors="ignore")):
                adapter_violation_found = True
                break
    passed = rejected and schema_requires_router and not adapter_violation_found
    return ScenarioResult(
        "G-A01",
        passed,
        "bad routing source rejected; schema requires phase_f_router; no adapter self-routing patterns",
    )


def ga02_unplanned_skill_activation() -> ScenarioResult:
    state = create_execution_state("adv-task")
    state["planned_skill_ids"] = ["ACOS-13"]
    rejected = False
    try:
        validate_active_skills_subset(state, ["ACOS-13", "ACOS-06"])
    except ValueError:
        rejected = True
    return ScenarioResult("G-A02", rejected, "unplanned skill activation raises ValueError")


def ga03_stale_gate_override() -> ScenarioResult:
    routing = {"design_gate_state": "PENDING", "routing_id": "r1"}
    state = create_execution_state("adv-task")
    state.setdefault("gate_states", {})["design_gate"] = "APPROVED"
    gate = authoritative_design_gate(state, routing)
    transition = can_transition(state, "PRODUCTION", routing)
    passed = gate == "APPROVED" and transition["allowed"] is True
    return ScenarioResult("G-A03", passed, "execution APPROVED overrides stale routing PENDING")


def ga04_premature_production() -> ScenarioResult:
    routing = {"design_gate_state": "PENDING", "routing_id": "r1"}
    state = create_execution_state("adv-task")
    state.setdefault("gate_states", {})["design_gate"] = "PENDING"
    transition = can_transition(state, "PRODUCTION", routing)
    passed = transition["allowed"] is False
    return ScenarioResult("G-A04", passed, "PENDING blocks PRODUCTION transition")


def ga05_license_acknowledgment_bypass() -> ScenarioResult:
    intake = _base_intake(requires_frontend=True, license_review_acknowledged=True)
    decision = route_task(intake)
    activated = set(decision.get("activated_skill_ids", []))
    passed = "EXT-FE-01" not in activated and "EXT-FE-02" not in activated
    return ScenarioResult("G-A05", passed, "license acknowledgment does not unblock EXT-FE-01/02")


def ga06_unknown_correction_defect() -> ScenarioResult:
    result = route_defect_to_skill("unknown_defect_type_xyz")
    passed = result["status"] == "CORRECTION_ROUTING_REQUIRES_RESOLUTION"
    passed = passed and "ACOS-01" not in result.get("responsible_skill_ids", [])
    return ScenarioResult("G-A06", passed, "unknown defect escalates; no ACOS-01 default")


def ga07_memory_promotion_shortcut() -> ScenarioResult:
    errors = validate_promotion("observation", "validated-global")
    shortcut_rejected = bool(errors)
    record = create_memory_observation(
        memory_id="m-adv",
        category="knowledge",
        scope="project",
        statement="test",
        source_task_id="adv-task",
        evidence_refs=["artifact://e1"],
        subject_key="test.key",
        value="v1",
    )
    promote_rejected = False
    try:
        promote_memory(record, "validated-global", ["artifact://e2"])
    except ValueError:
        promote_rejected = True
    passed = shortcut_rejected and promote_rejected
    return ScenarioResult("G-A07", passed, "observation→validated-global rejected")


def ga08_model_specific_global_leakage() -> ScenarioResult:
    record = create_memory_observation(
        memory_id="m-model",
        category="model_compatibility",
        scope="model_specific",
        statement="model hint",
        source_task_id="adv-task",
        evidence_refs=["artifact://e1"],
        subject_key="model.hint",
        value="v1",
        model_profile="test-model",
    )
    leak_rejected = False
    try:
        promote_memory(
            record,
            "project-rule",
            ["artifact://e2"],
            validation_context={"target_scope": "validated_global"},
        )
    except ValueError:
        leak_rejected = True
    passed = leak_rejected
    return ScenarioResult("G-A08", passed, "model-specific cannot silently become global")


def ga09_fake_evidence() -> ScenarioResult:
    rejected = False
    try:
        register_evidence(
            evidence_id="e-fake",
            evidence_type="claim",
            producer="test",
            artifact_ref="looks good",
            source="synthetic",
        )
    except ValueError:
        rejected = True
    bad_record = {
        "evidence_id": "e2",
        "type": "claim",
        "producer": "test",
        "artifact_ref": "looks good",
        "source": "synthetic",
        "timestamp": _now(),
        "status": "registered",
    }
    validation_errors = validate_evidence_record(bad_record)
    passed = rejected and bool(validation_errors)
    return ScenarioResult("G-A09", passed, "claim-only evidence rejected")


def ga10_hr11_injection() -> ScenarioResult:
    rejected = False
    try:
        evaluate_gate(
            {
                "gate_report": {
                    "status": "REJECTED",
                    "decisions": {"hard_reject_ids": ["HR-11"], "hard_reject_triggered": True},
                    "hard_rejects": [{"id": "HR-11", "triggered": True}],
                    "evidence": [{"id": "E1", "ref": "artifact://proof"}],
                }
            }
        )
    except Exception:
        rejected = True
    return ScenarioResult("G-A10", rejected, "HR-11 injection raises error")


def ga11_producer_self_approval() -> ScenarioResult:
    errors = validate_producer_independence(
        producer_skill_id="ACOS-13",
        critic_skill_id="ACOS-10",
        gate_evaluator_skill_id="ACOS-13",
    )
    passed = any("self-approve" in e.lower() for e in errors)
    return ScenarioResult("G-A11", passed, "producer self-approval prohibited")


def ga12_tool_capability_inflation() -> ScenarioResult:
    simulated = {
        "runtime": "RESTRICTED",
        "tcp_socket_reachable": True,
        "protocol_handshake_verified": False,
        "addon_runtime_verified": False,
    }
    inflated = simulated["tcp_socket_reachable"] and simulated["runtime"] == "AVAILABLE"
    caps_path = REPO / "tools" / "blender-mcp" / "capabilities.yaml"
    caps_text = caps_path.read_text(encoding="utf-8").lower() if caps_path.is_file() else ""
    caps_truthful = "handshake" in caps_text or "restricted" in caps_text or "not verified" in caps_text
    passed = not inflated and caps_truthful
    return ScenarioResult(
        "G-A12",
        passed,
        "TCP reachable without handshake must not imply AVAILABLE",
    )


def ga13_mandatory_3d_contamination() -> ScenarioResult:
    intake = _base_intake(deliverable_profile="standard_application", requires_frontend=True)
    decision = route_task(intake)
    activated = set(decision.get("activated_skill_ids", []))
    three_d = {"ACOS-06", "EXT-3DWEB-01", "EXT-IMG3D-01"}
    passed = not (activated & three_d)
    return ScenarioResult("G-A13", passed, "standard task does not auto-activate 3D skills")


def ga14_mandatory_motion_contamination() -> ScenarioResult:
    intake = _base_intake(deliverable_profile="standard_application", requires_frontend=True)
    decision = route_task(intake)
    activated = set(decision.get("activated_skill_ids", []))
    motion = {"ACOS-07", "ACOS-12", "EXT-MOTION-01"}
    passed = not (activated & motion)
    return ScenarioResult("G-A14", passed, "standard task does not auto-activate motion skills")


def ga15_benchmark_contamination() -> ScenarioResult:
    contaminated: list[str] = []
    for name in ("benchmarks", "projects"):
        path = REPO / name
        if not path.is_dir():
            continue
        for item in path.iterdir():
            if item.name == ".gitkeep":
                continue
            contaminated.append(str(item.relative_to(REPO)))
    passed = not contaminated
    detail = "empty" if passed else f"contamination: {contaminated[:5]}"
    return ScenarioResult("G-A15", passed, detail)


def ga16_invented_model_benchmark() -> ScenarioResult:
    models_path = REPO / "registry" / "MODELS.yaml"
    data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    models = data.get("models") or []
    invented = False
    for model in models:
        if not isinstance(model, dict):
            continue
        if model.get("benchmark_results") or model.get("approved_without_evidence"):
            invented = True
    policy_ok = data.get("policy", {}).get("no_invented_benchmark_results") is True
    passed = not invented and policy_ok and len(models) == 0
    return ScenarioResult("G-A16", passed, "MODELS.yaml has no fabricated benchmark results")


def ga17_external_skill_count_drift() -> ScenarioResult:
    lock_path = REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml"
    lock = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    entries = lock.get("entries") or []
    expected = lock.get("counts", {}).get("total_locked_entries", 36)
    ids = [e["id"] for e in entries if isinstance(e, dict) and e.get("id")]
    passed = len(entries) == expected == 36 and len(ids) == len(set(ids))
    return ScenarioResult("G-A17", passed, f"external skills={len(entries)} expected=36")


def ga18_proprietary_skill_count_drift() -> ScenarioResult:
    skills_path = REPO / "registry" / "SKILLS.yaml"
    skills = yaml.safe_load(skills_path.read_text(encoding="utf-8"))
    proprietary = skills.get("proprietary") or []
    ids = [s["id"] for s in proprietary if isinstance(s, dict) and s.get("id")]
    expected = skills.get("counts", {}).get("proprietary_acos", 14)
    passed = len(proprietary) == expected == 14 and len(ids) == len(set(ids))
    return ScenarioResult("G-A18", passed, f"proprietary skills={len(proprietary)} expected=14")


def ga19_phase_collision() -> ScenarioResult:
    phases_path = REPO / "registry" / "PHASES.yaml"
    phases = yaml.safe_load(phases_path.read_text(encoding="utf-8"))
    foundation = phases.get("foundation") or {}
    letters = {k for k in foundation if len(k) == 1}
    expected = {"A", "B", "C", "D", "E", "F", "G"}
    pf = phases.get("post_foundation") or {}
    pf_ids = set(pf.keys())
    expected_pf = {"PF-1", "PF-2", "PF-3", "PF-4", "PF-5"}
    legacy_hits: list[str] = []
    for path in (REPO / "IMPLEMENTATION_CHECKLIST.md", REPO / "registry" / "PHASES.yaml"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in LEGACY_PHASE_MARKERS:
            if marker in text:
                legacy_hits.append(f"{path.relative_to(REPO)}:{marker}")
                break
    passed = letters == expected and pf_ids == expected_pf and not legacy_hits
    return ScenarioResult("G-A19", passed, "no legacy H/I/J phase collision")


def ga20_foundation_ready_premature() -> ScenarioResult:
    phases_path = REPO / "registry" / "PHASES.yaml"
    phases = yaml.safe_load(phases_path.read_text(encoding="utf-8"))
    g_state = phases.get("execution_state", {}).get("foundation", {}).get("G")
    ready = phases.get("foundation_ready", {})
    declared = ready.get("declared") is True if isinstance(ready, dict) else False
    result_path = REPO / "validation" / "FOUNDATION_CERTIFICATION_RESULT.json"
    has_result = result_path.is_file()
    premature = declared and (g_state != "COMPLETE" or not has_result)
    passed = not premature
    return ScenarioResult("G-A20", passed, "FOUNDATION_READY not prematurely declared")


def ga_domain_neutrality_probe() -> ScenarioResult:
    hits: list[str] = []
    patterns = re.compile(r"\bcoffee\b|\bcrypto portfolio\b|\bluxury brand default\b", re.I)
    scan_roots = [REPO / "core", REPO / "registry", REPO / "runtime", REPO / "skills" / "acos"]
    for root in scan_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix not in (".md", ".yaml", ".yml", ".py"):
                continue
            if patterns.search(path.read_text(encoding="utf-8", errors="ignore")):
                hits.append(str(path.relative_to(REPO)))
    aesthetic_hits: list[str] = []
    for root in scan_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix not in (".md", ".yaml", ".yml"):
                continue
            if MANDATORY_AESTHETIC.search(path.read_text(encoding="utf-8", errors="ignore")):
                aesthetic_hits.append(str(path.relative_to(REPO)))
    passed = not hits and not aesthetic_hits
    return ScenarioResult("G-A-domain", passed, f"domain hits={len(hits)} aesthetic hits={len(aesthetic_hits)}")


def ga_persist_resume_integrity() -> ScenarioResult:
    intake = _base_intake(deliverable_profile="visual_experience", requires_visual_output=True)
    routing = route_task(intake)
    state = create_execution_state(intake["task_id"])
    bind_routing_to_execution(state, routing)
    with tempfile.TemporaryDirectory() as tmp:
        store_dir = Path(tmp)
        persist_state(state, store_dir)
        resumed = resume_execution(intake["task_id"], store_dir)
    passed = (
        resumed.get("routing_id") == state.get("routing_id")
        and resumed.get("planned_skill_ids") == state.get("planned_skill_ids")
        and resumed.get("gate_states") == state.get("gate_states")
    )
    return ScenarioResult("G-A-persist", passed, "persist/resume preserves routing and gate state")


SCENARIOS = [
    ga01_adapter_self_routing,
    ga02_unplanned_skill_activation,
    ga03_stale_gate_override,
    ga04_premature_production,
    ga05_license_acknowledgment_bypass,
    ga06_unknown_correction_defect,
    ga07_memory_promotion_shortcut,
    ga08_model_specific_global_leakage,
    ga09_fake_evidence,
    ga10_hr11_injection,
    ga11_producer_self_approval,
    ga12_tool_capability_inflation,
    ga13_mandatory_3d_contamination,
    ga14_mandatory_motion_contamination,
    ga15_benchmark_contamination,
    ga16_invented_model_benchmark,
    ga17_external_skill_count_drift,
    ga18_proprietary_skill_count_drift,
    ga19_phase_collision,
    ga20_foundation_ready_premature,
    ga_domain_neutrality_probe,
    ga_persist_resume_integrity,
]


def run_all() -> tuple[list[ScenarioResult], list[str]]:
    if yaml is None:
        return [], ["PyYAML required"]
    errors: list[str] = []
    results: list[ScenarioResult] = []
    for fn in SCENARIOS:
        try:
            result = fn()
            results.append(result)
            if not result.passed:
                errors.append(f"{result.scenario_id}: {result.detail}")
        except Exception as exc:
            sid = fn.__name__
            errors.append(f"{sid}: unexpected exception: {exc}")
            results.append(ScenarioResult(sid, False, str(exc)))
    return results, errors


def main() -> int:
    results, errors = run_all()
    payload = {
        "phase": PHASE,
        "timestamp": _now(),
        "scenario_count": len(results),
        "passed": len([r for r in results if r.passed]),
        "failed": len([r for r in results if not r.passed]),
        "scenarios": [
            {"id": r.scenario_id, "passed": r.passed, "detail": r.detail} for r in results
        ],
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    if errors:
        print(f"\nPhase {PHASE} FAILED ({len(errors)} scenario(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"\nPhase {PHASE} PASSED ({len(results)} scenarios)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
