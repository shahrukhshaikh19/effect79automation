"""PF-2 benchmark execution adversarial tests PF2-A01..PF2-A08."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.benchmark_execution.intake import build_intake_from_registration
from validation.benchmark_execution.scoring import score_benchmark
from validation.validate_benchmark_registration import canonical_hash


def _minimal_registration(**overrides) -> dict:
    base = {
        "benchmark_id": "BM-001",
        "title": "Test",
        "status": "FROZEN",
        "contract_version": "1.1",
        "normalized_brief": {
            "objective": "Premium web experience",
            "primary_goal": "Test workflow",
            "deliverable_type": "functional_interactive_web_experience",
        },
        "capability_expectations": {"motion_expected": True},
        "acceptance_contract": {
            "weight_normalization": {
                "profiles": {
                    "no_meaningful_3d": {
                        "dimensions": {
                            "functional": 15,
                            "visual": 20,
                            "creative": 20,
                            "responsive": 15,
                            "performance": 10,
                            "accessibility": 5,
                            "engineering": 10,
                            "motion_quality": 5,
                        }
                    }
                }
            }
        },
        "benchmark_contract_sha256": "abc",
    }
    base.update(overrides)
    return base


class BenchmarkExecutionAdversarialTests(unittest.TestCase):
    def test_pf2_a01_intake_no_manual_skill_ids(self) -> None:
        reg = _minimal_registration()
        intake = build_intake_from_registration(reg)
        text = str(intake)
        self.assertNotIn("ACOS-01", text)
        self.assertTrue(intake["task_signals"]["requires_3d"] is False)

    def test_pf2_a02_routing_activates_visual_route(self) -> None:
        from runtime.routing.engine import route_task

        reg = _minimal_registration()
        intake = build_intake_from_registration(reg)
        routing = route_task(intake)
        self.assertEqual(routing["status"], "ROUTED")
        planned = routing.get("planned_skill_ids") or []
        self.assertIn("ACOS-01", planned)
        self.assertIn("ACOS-13", planned)

    def test_pf2_a03_design_gate_blocks_production_when_pending(self) -> None:
        from runtime.state.execution import create_execution_state
        from runtime.state.transitions import can_transition, set_design_gate_state

        state = create_execution_state("t1")
        set_design_gate_state(state, "PENDING")
        result = can_transition(state, "PRODUCTION", {"design_gate_state": "PENDING"})
        self.assertFalse(result["allowed"])

    def test_pf2_a04_scoring_blocked_without_evidence(self) -> None:
        score = score_benchmark(
            acceptance=_minimal_registration()["acceptance_contract"],
            evidence_manifest={},
            critic_report={"hard_critic_failures": []},
            gate_status="BLOCKED_INSUFFICIENT_EVIDENCE",
            meaningful_3d_used=False,
        )
        self.assertEqual(score["benchmark_result"], "BLOCKED")
        self.assertIsNone(score["benchmark_score"])

    def test_pf2_a05_no_meaningful_3d_profile(self) -> None:
        score = score_benchmark(
            acceptance=_minimal_registration()["acceptance_contract"],
            evidence_manifest={
                "runtime_healthy": True,
                "viewports_captured": ["desktop", "laptop", "tablet", "mobile"],
                "sections_present": 7,
                "reduced_motion_verified": True,
                "interaction_verified": True,
                "performance_ok": True,
            },
            critic_report={"hard_critic_failures": []},
            gate_status="APPROVED",
            meaningful_3d_used=False,
        )
        self.assertEqual(score["profile"], "no_meaningful_3d")
        self.assertIsNotNone(score["benchmark_score"])

    def test_pf2_a06_contract_hash_excludes_execution_state(self) -> None:
        reg = _minimal_registration()
        h1 = canonical_hash(reg)
        reg2 = copy.deepcopy(reg)
        reg2["execution_state"] = {"benchmark_result": "PASS", "benchmark_score": 85.0}
        h2 = canonical_hash(reg2)
        self.assertEqual(h1, h2)

    def test_pf2_a07_frozen_contract_file_exists(self) -> None:
        reg_path = REPO / "benchmarks" / "BM-001" / "REGISTRATION.yaml"
        self.assertTrue(reg_path.is_file())
        import yaml

        data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        self.assertEqual(
            data.get("benchmark_contract_sha256"),
            "b2cb2dbaea31e07331fe1c94df1271e3c167f9a64461e2dc25410d13696cadf3",
        )

    def test_pf2_a08_implementation_required_files(self) -> None:
        impl = REPO / "benchmarks" / "BM-001" / "execution" / "implementation"
        for name in ("index.html", "styles.css", "main.js"):
            self.assertTrue((impl / name).is_file(), f"missing {name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
