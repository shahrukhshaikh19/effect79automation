"""Adversarial regression tests for BM-002 certification-integrity false-pass loopholes."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.benchmark_execution.bm002_critics import _3d_critic, _visual_critic
from validation.benchmark_execution.critic_integrity import (
    assess_critic_integrity,
    cap_score_for_review_basis,
    review_is_producer_derived,
)
from validation.benchmark_execution.gate_evaluation import determine_gate_status


def _producer_visual_review() -> dict:
    return {
        "dimension_score": 10.0,
        "findings": [],
        "producer_authored": True,
        "independent_critic_review": False,
        "review_basis": "static_source_analysis",
    }


def _producer_3d_review() -> dict:
    return {
        "dimension_score": 10.0,
        "findings": [],
        "hard_failures": [],
        "producer_authored": True,
        "independent_critic_review": False,
        "review_basis": "static_source_analysis",
    }


class BM002CertificationIntegrityTests(unittest.TestCase):
    def test_producer_derived_visual_review_detected(self) -> None:
        self.assertTrue(review_is_producer_derived(_producer_visual_review()))

    def test_producer_visual_critic_cannot_pass_flagship(self) -> None:
        finding = _visual_critic(
            analysis={},
            visual_review=_producer_visual_review(),
            evidence_refs=["evidence/E-001/manifest.yaml"],
            viewport_manifest={"visual_quality_approved": False, "captures": [{"viewport": {"name": "desktop"}, "screenshot_path": "x.png"}]},
        )
        self.assertIn(finding["verdict"], ("BLOCKED_INSUFFICIENT_EVIDENCE", "FAIL"))
        self.assertLessEqual(float(finding["dimension_score"]), 6.0)
        self.assertTrue(finding["findings"])

    def test_producer_3d_critic_blocked_without_rendered_review(self) -> None:
        finding = _3d_critic(
            evidence_bundle={"E-011": _producer_3d_review()},
            analysis={"three_js": True},
            viewport_manifest={"visual_quality_approved": False},
        )
        self.assertEqual(finding["verdict"], "BLOCKED_INSUFFICIENT_EVIDENCE")
        self.assertLessEqual(float(finding["dimension_score"]), 7.0)

    def test_premium_score_without_findings_flagged(self) -> None:
        integrity = assess_critic_integrity(
            critic_report={
                "findings": [
                    {"domain": "visual", "dimension_score": 10.0, "findings": [], "verdict": "PASS"},
                    {"domain": "three_d_quality", "dimension_score": 10.0, "findings": [], "verdict": "PASS"},
                ]
            },
            evidence_bundle={
                "E-003": _producer_visual_review(),
                "E-011": _producer_3d_review(),
                "scene_log": {"self_reported": True, "source": "implementation_global"},
            },
            viewport_manifest={
                "visual_quality_approved": False,
                "captures": [
                    {"viewport": {"name": "desktop"}, "screenshot_path": "a.png"},
                    {"viewport": {"name": "laptop"}, "screenshot_path": "b.png"},
                    {"viewport": {"name": "tablet"}, "screenshot_path": "c.png"},
                    {"viewport": {"name": "mobile"}, "screenshot_path": "d.png"},
                ],
            },
        )
        self.assertFalse(integrity["integrity_ok"])
        self.assertIn("producer_derived_visual_review", integrity["false_pass_mechanisms"])
        self.assertIn("screenshots_not_interpreted", integrity["false_pass_mechanisms"])

    def test_gate_blocks_on_critic_integrity_violation(self) -> None:
        status, _, decisions = determine_gate_status(
            evidence_completeness={"sufficient": True},
            critic_report={"findings": []},
            artifact_analysis={},
            runtime_healthy=True,
            console_error_count=0,
            critic_integrity={"integrity_ok": False, "violations": ["producer derived"]},
        )
        self.assertEqual(status, "BLOCKED_INSUFFICIENT_EVIDENCE")
        self.assertTrue(decisions.get("critic_integrity_violations"))

    def test_cap_score_prevents_static_10_visual(self) -> None:
        capped, notes = cap_score_for_review_basis(
            domain="visual",
            score=10.0,
            producer_derived=True,
            rendered_review_complete=False,
        )
        self.assertLessEqual(capped, 6.0)
        self.assertTrue(notes)

    def test_historical_run_manifest_contradiction_detected(self) -> None:
        import yaml

        manifest_path = REPO / "benchmarks" / "BM-002" / "execution" / "evidence" / "E-001" / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(manifest.get("visual_quality_approved"))
        integrity = assess_critic_integrity(
            critic_report={
                "findings": [
                    {"domain": "visual", "dimension_score": 10.0, "findings": [], "verdict": "PASS"},
                ]
            },
            evidence_bundle={"E-003": _producer_visual_review(), "E-011": _producer_3d_review()},
            viewport_manifest=manifest,
        )
        self.assertFalse(integrity["integrity_ok"])
        self.assertIn("visual_quality_approved_contradiction", integrity["false_pass_mechanisms"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
