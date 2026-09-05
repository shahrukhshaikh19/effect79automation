"""PF-2 benchmark execution adversarial tests PF2-A01..PF2-A24."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.benchmark_execution.artifact_analysis import analyze_implementation
from validation.benchmark_execution.critics import evaluate_critics, _visual_critic, _creative_critic
from validation.benchmark_execution.evidence_contract import (
    required_evidence_ids,
    validate_evidence_artifact,
    validate_required_evidence,
)
from validation.benchmark_execution.gate_evaluation import build_gate_report, determine_gate_status, evaluate_quality_gate
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


def _full_evidence_records() -> dict[str, str]:
    root = REPO / "benchmarks" / "BM-001" / "execution" / "evidence"
    return {
        "E-001": str(root / "E-001" / "manifest.yaml"),
        "E-002": str(root / "E-002" / "implementation_check.json"),
        "E-003": str(root / "E-003" / "visual_consistency_review.json"),
        "E-004": str(root / "E-004" / "responsive_behavior_check.json"),
        "E-005": str(root / "E-005" / "console_log.json"),
        "E-006": str(root / "E-006" / "network_request_log.json"),
        "E-007": str(root / "E-007" / "interaction_log.json"),
        "E-008": str(root / "E-008" / "manifest.yaml"),
        "E-009": str(root / "E-009" / "performance_metrics.json"),
        "E-010": str(REPO / "benchmarks" / "BM-001" / "execution" / "run" / "gate_report.yaml"),
    }


class BenchmarkExecutionAdversarialTests(unittest.TestCase):
    def test_pf2_a01_intake_no_manual_skill_ids(self) -> None:
        intake = build_intake_from_registration(_minimal_registration())
        self.assertNotIn("ACOS-01", str(intake))
        self.assertFalse(intake["task_signals"]["requires_3d"])

    def test_pf2_a02_required_evidence_from_frozen_plan(self) -> None:
        required = required_evidence_ids(meaningful_3d_used=False)
        self.assertIn("E-003", required)
        self.assertIn("E-004", required)
        self.assertIn("E-006", required)
        self.assertNotIn("E-011", required)

    def test_pf2_a03_e011_required_when_3d_used(self) -> None:
        required = required_evidence_ids(meaningful_3d_used=True)
        self.assertIn("E-011", required)

    def test_pf2_a04_missing_e003_blocked(self) -> None:
        records = _full_evidence_records()
        del records["E-003"]
        result = validate_required_evidence(meaningful_3d_used=False, evidence_records=records)
        self.assertFalse(result["sufficient"])
        self.assertIn("E-003", result["missing"])

    def test_pf2_a05_missing_e004_blocked(self) -> None:
        records = _full_evidence_records()
        del records["E-004"]
        result = validate_required_evidence(meaningful_3d_used=False, evidence_records=records)
        self.assertFalse(result["sufficient"])
        self.assertIn("E-004", result["missing"])

    def test_pf2_a06_missing_e006_blocked(self) -> None:
        records = _full_evidence_records()
        del records["E-006"]
        result = validate_required_evidence(meaningful_3d_used=False, evidence_records=records)
        self.assertFalse(result["sufficient"])
        self.assertIn("E-006", result["missing"])

    def test_pf2_a07_empty_evidence_file_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.json"
            path.write_text("{}", encoding="utf-8")
            errors = validate_evidence_artifact("E-002", path)
            self.assertTrue(errors)

    def test_pf2_a08_four_screenshots_alone_no_visual_pass(self) -> None:
        analysis = {"glassmorphism_detected": True, "hard_failure_signals": [{"id": "arbitrary_glassmorphism"}]}
        review = {"dimension_score": 4.0, "findings": [{"severity": "critical", "detail": "glass"}]}
        finding = _visual_critic(analysis=analysis, visual_review=review, evidence_refs=["E-001"])
        self.assertEqual(finding["verdict"], "FAIL")

    def test_pf2_a09_five_sections_alone_no_creative_pass(self) -> None:
        analysis = {"sections": 7, "fictional_brand_present": False, "hard_failure_signals": [], "floating_card_grid": True}
        finding = _creative_critic(analysis=analysis, direction=None, evidence_refs=["E-001"])
        self.assertEqual(finding["verdict"], "FAIL")

    def test_pf2_a10_hard_reject_produces_rejected(self) -> None:
        analysis = {"hard_failure_signals": [{"id": "arbitrary_glassmorphism", "evidence_ref": "styles.css", "detail": "blur"}]}
        status, hard_rejects, _ = determine_gate_status(
            evidence_completeness={"sufficient": True},
            critic_report={"findings": []},
            artifact_analysis=analysis,
            runtime_healthy=True,
            console_error_count=0,
        )
        self.assertEqual(status, "REJECTED")
        self.assertTrue(any(hr.get("triggered") for hr in hard_rejects))

    def test_pf2_a11_hardcoded_false_hr_cannot_bypass_findings(self) -> None:
        analysis = {"hard_failure_signals": [{"id": "generic_saas_landing_template", "evidence_ref": "x", "detail": "y"}]}
        status, hard_rejects, decisions = determine_gate_status(
            evidence_completeness={"sufficient": True},
            critic_report={"findings": []},
            artifact_analysis=analysis,
            runtime_healthy=True,
            console_error_count=0,
        )
        gate = build_gate_report(
            gate_status=status,
            hard_rejects=hard_rejects,
            decisions=decisions,
            evidence_records=[{"id": "E-001", "ref": "x"}],
            critic_report={"findings": []},
        )
        if status == "REJECTED":
            gate["gate_report"]["status"] = "APPROVED"
        result = evaluate_quality_gate(gate)
        self.assertNotEqual(result["status"], "APPROVED")

    def test_pf2_a12_score_cannot_override_rejected(self) -> None:
        score = score_benchmark(
            acceptance=_minimal_registration()["acceptance_contract"],
            gate_status="REJECTED",
            critic_report={"dimension_scores": {"visual": 10, "creative": 10, "functional": 10, "responsive": 10, "performance": 10, "accessibility": 10, "engineering": 10, "motion_quality": 10}},
            evidence_completeness={"sufficient": True},
            meaningful_3d_used=False,
        )
        self.assertEqual(score["benchmark_result"], "FAIL")
        self.assertIsNone(score["benchmark_score"])

    def test_pf2_a13_score_cannot_override_blocked(self) -> None:
        score = score_benchmark(
            acceptance=_minimal_registration()["acceptance_contract"],
            gate_status="BLOCKED_INSUFFICIENT_EVIDENCE",
            critic_report={"dimension_scores": {}},
            evidence_completeness={"sufficient": False},
            meaningful_3d_used=False,
        )
        self.assertEqual(score["benchmark_result"], "BLOCKED")
        self.assertIsNone(score["benchmark_score"])

    def test_pf2_a14_producer_cannot_self_approve(self) -> None:
        from runtime.quality.gate import validate_producer_independence

        errors = validate_producer_independence(producer_skill_id="ACOS-04", critic_skill_id="ACOS-04")
        self.assertTrue(errors)

    def test_pf2_a15_contract_hash_unchanged(self) -> None:
        reg_path = REPO / "benchmarks" / "BM-001" / "REGISTRATION.yaml"
        import yaml

        data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        self.assertEqual(
            data.get("benchmark_contract_sha256"),
            "b2cb2dbaea31e07331fe1c94df1271e3c167f9a64461e2dc25410d13696cadf3",
        )

    def test_pf2_a16_missing_evidence_blocks_gate(self) -> None:
        status, _, _ = determine_gate_status(
            evidence_completeness={"sufficient": False, "missing": ["E-003"]},
            critic_report={"findings": []},
            artifact_analysis={},
            runtime_healthy=True,
            console_error_count=0,
        )
        self.assertEqual(status, "BLOCKED_INSUFFICIENT_EVIDENCE")

    def test_pf2_a17_critic_missing_e003_blocks(self) -> None:
        report = evaluate_critics(
            routing={"planned_skill_ids": ["ACOS-10", "ACOS-11"]},
            analysis=analyze_implementation(REPO / "benchmarks" / "BM-001" / "execution" / "implementation"),
            evidence_bundle={},
            direction={},
            meaningful_3d_used=False,
        )
        blocked = [f for f in report["findings"] if f.get("verdict") == "BLOCKED_INSUFFICIENT_EVIDENCE"]
        self.assertTrue(blocked)

    def test_pf2_a18_implementation_files_exist(self) -> None:
        impl = REPO / "benchmarks" / "BM-001" / "execution" / "implementation"
        for name in ("index.html", "styles.css", "main.js"):
            self.assertTrue((impl / name).is_file(), f"missing {name}")

    def test_pf2_a19_execution_state_hash_exclusion(self) -> None:
        reg = _minimal_registration()
        h1 = canonical_hash(reg)
        reg2 = copy.deepcopy(reg)
        reg2["execution_state"] = {"benchmark_result": "FAIL", "certified_result": "INVALIDATED"}
        self.assertEqual(h1, canonical_hash(reg2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
