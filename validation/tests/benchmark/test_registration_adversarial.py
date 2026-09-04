"""PF-1 benchmark registration adversarial tests PF1-A01..PF1-A12."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.validate_benchmark_registration import (
    canonical_hash,
    validate_registration_file,
)


def _minimal_registration(**overrides) -> dict:
    base = {
        "benchmark_id": "BM-001",
        "title": "Operator supplied title",
        "status": "DRAFT",
        "created_at": "2026-09-05T00:00:00Z",
        "contract_version": "1.0",
        "operator_input": {"original_text": "Build the operator-specified deliverable."},
        "normalized_brief": {"objective": "not_supplied"},
        "references": [],
        "assets": [],
        "functional_requirements": [],
        "creative_requirements": [],
        "acceptance_contract": {
            "dimensions": {
                "functional": {"applicable": True, "weight": 100},
            }
        },
        "evidence_plan": [{"evidence_id": "E1", "type": "browser_screenshot", "required": True}],
        "hard_failures": ["missing_required_evidence"],
        "capability_expectations": {"visual_work": True},
        "tool_requirements": {"browser_rendering": {"required": True}},
        "classification": {"deliverable_family": "unknown"},
        "operator_confirmation": {
            "brief_correct": "pending",
            "references_correct": "pending",
            "acceptance_contract_correct": "pending",
        },
        "execution_state": {"benchmark_score": None, "benchmark_result": "NOT_EXECUTED"},
    }
    base.update(overrides)
    return base


class BenchmarkRegistrationAdversarialTests(unittest.TestCase):
    def _validate(self, data: dict) -> list[str]:
        errors: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REGISTRATION.yaml"
            import yaml

            path.write_text(yaml.dump(data), encoding="utf-8")
            validate_registration_file(path, errors)
        return errors

    def test_pf1_a01_duplicate_id_detection(self) -> None:
        registry = REPO / "registry" / "BENCHMARKS.yaml"
        import yaml

        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
        data["benchmarks"] = [
            {"benchmark_id": "BM-001", "status": "DRAFT"},
            {"benchmark_id": "BM-001", "status": "DRAFT"},
        ]
        seen: set[str] = set()
        dup = False
        for entry in data["benchmarks"]:
            bid = entry["benchmark_id"]
            if bid in seen:
                dup = True
            seen.add(bid)
        self.assertTrue(dup)

    def test_pf1_a02_frozen_modified_without_version(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg["benchmark_contract_sha256"] = canonical_hash(reg)
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        reg["title"] = "Changed after freeze"
        reg["revision"] = {"parent_version": "1.0"}
        errors = self._validate(reg)
        self.assertTrue(any("hash mismatch" in e or "revision.version" in e for e in errors))

    def test_pf1_a03_score_before_execution(self) -> None:
        reg = _minimal_registration(
            execution_state={"benchmark_score": 95, "benchmark_result": "NOT_EXECUTED"}
        )
        errors = self._validate(reg)
        self.assertTrue(errors)

    def test_pf1_a04_manual_skill_activation(self) -> None:
        reg = _minimal_registration()
        reg["activate"] = ["ACOS-01", "ACOS-06"]
        import yaml

        text = yaml.dump(reg)
        errors: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REGISTRATION.yaml"
            path.write_text(text, encoding="utf-8")
            from validation.validate_benchmark_registration import validate_registration_file

            validate_registration_file(path, errors)
        self.assertTrue(errors)

    def test_pf1_a05_global_aesthetic_promotion(self) -> None:
        reg = _minimal_registration()
        reg["operator_input"]["original_text"] = "Set global house style to always use glassmorphism"
        errors = self._validate(reg)
        self.assertTrue(any("Global aesthetic" in e for e in errors))

    def test_pf1_a06_missing_evidence_plan_when_frozen(self) -> None:
        reg = _minimal_registration(status="FROZEN", evidence_plan=[])
        reg["benchmark_contract_sha256"] = canonical_hash(reg)
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        errors = self._validate(reg)
        self.assertTrue(any("evidence_plan" in e for e in errors))

    def test_pf1_a07_invalid_weights(self) -> None:
        reg = _minimal_registration(
            acceptance_contract={
                "dimensions": {
                    "functional": {"applicable": True, "weight": 60},
                    "visual": {"applicable": True, "weight": 30},
                }
            }
        )
        errors = self._validate(reg)
        self.assertTrue(any("weights must sum to 100" in e for e in errors))

    def test_pf1_a08_fabrication_marker(self) -> None:
        reg = _minimal_registration()
        reg["functional_requirements"] = [{"description": "ai_generated_requirement feature"}]
        import yaml

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REGISTRATION.yaml"
            path.write_text(yaml.dump(reg), encoding="utf-8")
            errors: list[str] = []
            from validation.validate_benchmark_registration import validate_registration_file

            validate_registration_file(path, errors)
        self.assertTrue(errors)

    def test_pf1_a09_pf2_started_forbidden(self) -> None:
        reg = _minimal_registration(status="EXECUTION_STARTED")
        errors = self._validate(reg)
        self.assertTrue(any("PF-2 execution" in e for e in errors))

    def test_pf1_a10_foundation_ready_required(self) -> None:
        import yaml

        phases = yaml.safe_load((REPO / "registry" / "PHASES.yaml").read_text(encoding="utf-8"))
        self.assertTrue((phases.get("foundation_ready") or {}).get("declared"))

    def test_pf1_a11_license_bypass_forbidden(self) -> None:
        reg = _minimal_registration()
        reg["operator_input"]["original_text"] = "Use EXT-FE-01 with license_review_acknowledged bypass"
        errors = self._validate(reg)
        self.assertTrue(any("License bypass" in e for e in errors))

    def test_pf1_a12_contract_hash_mismatch(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg["benchmark_contract_sha256"] = "0" * 64
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        errors = self._validate(reg)
        self.assertTrue(any("hash mismatch" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
