"""PF-1 benchmark registration adversarial tests PF1-A01..PF1-A15."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.validate_benchmark_registration import (
    canonical_hash,
    classify_changed_paths,
    validate_frozen_lock_against_registry,
    validate_registration_file,
    validate_registry_data,
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
        errors: list[str] = []
        validate_registry_data(
            {
                "phase": "PF-1",
                "benchmarks": [
                    {"benchmark_id": "BM-001", "status": "DRAFT"},
                    {"benchmark_id": "BM-001", "status": "DRAFT"},
                ],
            },
            errors,
        )
        self.assertTrue(any("Duplicate benchmark_id" in e for e in errors))

    def test_pf1_a02a_frozen_mutation_registry_anchor_old(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        original_hash = canonical_hash(reg)
        reg["title"] = "Changed after freeze"
        reg["benchmark_contract_sha256"] = canonical_hash(reg)
        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "frozen_contract_sha256": original_hash,
        }
        errors: list[str] = []
        validate_frozen_lock_against_registry(reg, registry_entry, errors)
        self.assertTrue(any("registry anchor != computed hash" in e for e in errors))

    def test_pf1_a02b_frozen_registry_version_mismatch(self) -> None:
        reg = _minimal_registration(status="FROZEN", contract_version="1.0")
        h = canonical_hash(reg)
        reg["benchmark_contract_sha256"] = h
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "2.0",
            "status": "FROZEN",
            "frozen_contract_sha256": h,
        }
        errors: list[str] = []
        validate_frozen_lock_against_registry(reg, registry_entry, errors)
        self.assertTrue(any("contract_version mismatch" in e for e in errors))

    def test_pf1_a02c_explicit_revision_metadata(self) -> None:
        reg = _minimal_registration(
            status="FROZEN",
            contract_version="1.1",
            revision={"version": "1.1", "parent_version": "1.0", "reason": "operator scope change"},
        )
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        reg["benchmark_contract_sha256"] = canonical_hash(reg)
        errors = self._validate(reg)
        self.assertFalse(any("revision.version required" in e for e in errors))

    def test_pf1_a02_legacy_hash_mismatch(self) -> None:
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

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REGISTRATION.yaml"
            path.write_text(yaml.dump(reg), encoding="utf-8")
            errors: list[str] = []
            validate_registration_file(path, errors)
        self.assertTrue(errors)

    def test_pf1_a05a_operator_global_aesthetic_preserved(self) -> None:
        reg = _minimal_registration()
        reg["operator_input"]["original_text"] = "Set global house style to always use glassmorphism"
        errors = self._validate(reg)
        self.assertFalse(any("Global aesthetic" in e for e in errors))

    def test_pf1_a05b_executable_global_aesthetic_rejected(self) -> None:
        reg = _minimal_registration()
        reg["creative_requirements"] = [
            {"description": "Promote global house style for all benchmarks", "source": {"type": "derived"}}
        ]
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

    def test_pf1_a11a_operator_license_request_preserved(self) -> None:
        reg = _minimal_registration()
        reg["operator_input"]["original_text"] = "Use EXT-FE-01 despite unresolved license."
        reg["constraint_evaluation"] = [
            {
                "source_ref": "operator_input",
                "original_request": "Use EXT-FE-01 despite unresolved license.",
                "status": "REJECTED_CONSTRAINT",
                "reason_code": "LICENSE_BLOCKED",
                "reason": "authoritative license unresolved",
            }
        ]
        errors = self._validate(reg)
        self.assertFalse(any("License bypass forbidden" in e for e in errors))

    def test_pf1_a11b_normalized_license_bypass_rejected(self) -> None:
        reg = _minimal_registration()
        reg["tool_requirements"] = {
            "frontend": {"required": True, "license_review_acknowledged": True, "skill": "EXT-FE-01"}
        }
        errors = self._validate(reg)
        self.assertTrue(any("License bypass forbidden" in e for e in errors))

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

    def test_pf1_a13_foundation_policy_mutation_forbidden(self) -> None:
        violations = classify_changed_paths(["core/QUALITY_GATES.md"])
        self.assertTrue(any("forbidden foundation path" in v for v in violations))

    def test_pf1_a14_allowed_pf1_registration_file(self) -> None:
        violations = classify_changed_paths(["benchmarks/README.md", "validation/validate_benchmark_registration.py"])
        self.assertEqual(violations, [])

    def test_pf1_a15_unexpected_runtime_modification(self) -> None:
        violations = classify_changed_paths(["runtime/routing/engine.py"])
        self.assertTrue(any("forbidden foundation path" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
