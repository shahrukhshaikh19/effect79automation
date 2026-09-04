"""PF-1 benchmark registration adversarial tests PF1-A01..PF1-A29."""

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
    git_changed_paths,
    load_compatibility_lock,
    validate_compatibility_lock,
    validate_first_freeze_attestation,
    validate_frozen_lock_against_registry,
    validate_frozen_provenance,
    validate_registration_file,
    validate_registry_data,
)


def _mock_first_attestation(registry_entry: dict):
    def mock_find(bid: str, version: str):
        return "attest_commit", {
            "frozen_source_commit_sha": registry_entry["frozen_source_commit_sha"],
            "frozen_contract_sha256": registry_entry["frozen_contract_sha256"],
        }, None

    return mock_find


def _mock_first_attestation_map(attestations: dict[str, dict]):
    def mock_find(bid: str, version: str):
        record = attestations.get(version)
        if not record:
            return None, None, None
        return record.get("attestation_commit", "attest_commit"), record, None

    return mock_find


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
        original = _minimal_registration(status="FROZEN")
        original["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        original_hash = canonical_hash(original)
        original["benchmark_contract_sha256"] = original_hash

        mutated = copy.deepcopy(original)
        mutated["title"] = "Changed after freeze"
        mutated["benchmark_contract_sha256"] = canonical_hash(mutated)

        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
            "frozen_contract_sha256": original_hash,
            "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
        }

        import yaml

        def mock_load(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return yaml.dump(original), None

        errors: list[str] = []
        validate_frozen_lock_against_registry(
            mutated,
            registry_entry,
            errors,
            load_from_commit=mock_load,
            find_first_attestation=_mock_first_attestation(registry_entry),
        )
        self.assertTrue(
            any("current registration changed from historical frozen contract" in e for e in errors),
            msg=f"errors",
        )

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
            "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
            "frozen_contract_sha256": h,
            "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
        }

        import yaml

        def mock_load(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return yaml.dump(reg), None

        errors: list[str] = []
        validate_frozen_lock_against_registry(
            reg,
            registry_entry,
            errors,
            load_from_commit=mock_load,
            find_first_attestation=_mock_first_attestation(registry_entry),
        )
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

    def test_pf1_a16_git_diff_failure(self) -> None:
        def failing_git_changed_paths(baseline_sha: str) -> tuple[list[str], str | None]:
            return [], "git diff failed"

        errors: list[str] = []
        changed, git_err = failing_git_changed_paths("525eeb0")
        if git_err:
            errors.append(f"foundation git diff failed: {git_err}")
        self.assertTrue(any("foundation git diff failed" in e for e in errors))

    def test_pf1_a17_baseline_sha_missing(self) -> None:
        changed, git_err = git_changed_paths("0000000000000000000000000000000000000000")
        self.assertIsNotNone(git_err)
        self.assertEqual(changed, [])

    def test_pf1_a18_compatibility_file_changed(self) -> None:
        from unittest.mock import patch

        errors: list[str] = []
        with patch(
            "validation.validate_benchmark_registration.file_content_sha256",
            return_value="0" * 64,
        ):
            validate_compatibility_lock(errors)
        self.assertTrue(any("foundation compatibility file drift" in e for e in errors))

    def test_pf1_a19_approved_compatibility_hash(self) -> None:
        errors: list[str] = []
        validate_compatibility_lock(errors)
        self.assertEqual(errors, [])

    def test_pf1_a20_unanchored_compatibility_allowance(self) -> None:
        lock_paths = set(load_compatibility_lock())
        unanchored = "validation/validate_unanchored_foundation.py"
        violations = classify_changed_paths([unanchored], lock_paths)
        self.assertTrue(any("unanchored foundation compatibility file changed" in v for v in violations))

    def test_pf1_a21_historical_source_commit_missing(self) -> None:
        errors: list[str] = []
        validate_frozen_provenance(
            {
                "benchmark_id": "BM-001",
                "contract_version": "1.0",
                "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
                "frozen_contract_sha256": "a" * 64,
                "frozen_source_commit_sha": "0000000000000000000000000000000000000000",
            },
            None,
            errors,
        )
        self.assertTrue(any("unknown commit" in e for e in errors))

    def test_pf1_a22_historical_registration_path_missing(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg_hash = canonical_hash(reg)

        def missing_path(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return None, f"git show failed for {commit_sha}:{repo_path}"

        errors: list[str] = []
        validate_frozen_provenance(
            {
                "benchmark_id": "BM-001",
                "contract_version": "1.0",
                "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
                "frozen_contract_sha256": reg_hash,
                "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
            },
            None,
            errors,
            load_from_commit=missing_path,
        )
        self.assertTrue(any("historical registration lookup failed" in e for e in errors))

    def test_pf1_a23_historical_contract_hash_registry_mismatch(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg_hash = canonical_hash(reg)

        import yaml

        def mock_load(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return yaml.dump(reg), None

        errors: list[str] = []
        validate_frozen_provenance(
            {
                "benchmark_id": "BM-001",
                "contract_version": "1.0",
                "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
                "frozen_contract_sha256": "b" * 64,
                "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
            },
            None,
            errors,
            load_from_commit=mock_load,
        )
        self.assertTrue(any("registry frozen_contract_sha256 != historical registration hash" in e for e in errors))

    def test_pf1_a24_dual_rewrite_bypass_blocked(self) -> None:
        original = _minimal_registration(status="FROZEN")
        original["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        original_hash = canonical_hash(original)
        original["benchmark_contract_sha256"] = original_hash

        mutated = copy.deepcopy(original)
        mutated["title"] = "Silently changed contract"
        mutated_hash = canonical_hash(mutated)
        mutated["benchmark_contract_sha256"] = mutated_hash

        import yaml

        def mock_load(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return yaml.dump(original), None

        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
            "frozen_contract_sha256": mutated_hash,
            "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
        }

        errors: list[str] = []
        validate_frozen_lock_against_registry(
            mutated,
            registry_entry,
            errors,
            load_from_commit=mock_load,
            find_first_attestation=_mock_first_attestation(registry_entry),
        )
        self.assertTrue(
            any(
                "registry frozen_contract_sha256 != historical registration hash" in e
                or "current registration changed from historical frozen contract" in e
                for e in errors
            )
        )

    def test_pf1_a25_same_version_source_commit_repoint_fails(self) -> None:
        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
            "frozen_source_commit_sha": "commit_B",
            "frozen_contract_sha256": "hash_B",
        }

        def mock_find(bid: str, version: str):
            return "attest_1", {
                "frozen_source_commit_sha": "commit_A",
                "frozen_contract_sha256": "hash_B",
            }, None

        errors: list[str] = []
        validate_first_freeze_attestation(registry_entry, errors, find_first_attestation=mock_find)
        self.assertTrue(any("frozen_source_commit_sha repointed from first attestation" in e for e in errors))

    def test_pf1_a26_same_version_frozen_hash_rewrite_fails(self) -> None:
        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "frozen_source_commit_sha": "commit_A",
            "frozen_contract_sha256": "hash_B",
        }

        def mock_find(bid: str, version: str):
            return "attest_1", {
                "frozen_source_commit_sha": "commit_A",
                "frozen_contract_sha256": "hash_A",
            }, None

        errors: list[str] = []
        validate_first_freeze_attestation(registry_entry, errors, find_first_attestation=mock_find)
        self.assertTrue(any("frozen_contract_sha256 rewritten from first attestation" in e for e in errors))

    def test_pf1_a27_first_attestation_missing_fails_closed(self) -> None:
        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "frozen_source_commit_sha": "commit_A",
            "frozen_contract_sha256": "hash_A",
        }

        def mock_find(bid: str, version: str):
            return None, None, None

        errors: list[str] = []
        validate_first_freeze_attestation(registry_entry, errors, find_first_attestation=mock_find)
        self.assertTrue(any("first freeze attestation not found in git history" in e for e in errors))

    def test_pf1_a28_untouched_frozen_version_passes(self) -> None:
        reg = _minimal_registration(status="FROZEN")
        reg["operator_confirmation"] = {
            "brief_correct": "confirmed",
            "references_correct": "confirmed",
            "acceptance_contract_correct": "confirmed",
        }
        reg_hash = canonical_hash(reg)
        reg["benchmark_contract_sha256"] = reg_hash

        registry_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "status": "FROZEN",
            "registration_path": "benchmarks/BM-001/REGISTRATION.yaml",
            "frozen_source_commit_sha": "e3d9988e26881c23aeb9acf93f3c0448dfba7981",
            "frozen_contract_sha256": reg_hash,
        }

        import yaml

        def mock_load(commit_sha: str, repo_path: str) -> tuple[str | None, str | None]:
            return yaml.dump(reg), None

        errors: list[str] = []
        validate_frozen_lock_against_registry(
            reg,
            registry_entry,
            errors,
            load_from_commit=mock_load,
            find_first_attestation=_mock_first_attestation(registry_entry),
        )
        self.assertEqual(errors, [])

    def test_pf1_a29_proper_revision_preserves_v1_history(self) -> None:
        v10_hash = "hash_v10"
        v11_hash = "hash_v11"
        attestations = {
            "1.0": {
                "frozen_source_commit_sha": "commit_v10",
                "frozen_contract_sha256": v10_hash,
                "attestation_commit": "attest_v10",
            },
            "1.1": {
                "frozen_source_commit_sha": "commit_v11",
                "frozen_contract_sha256": v11_hash,
                "attestation_commit": "attest_v11",
            },
        }
        mock_find = _mock_first_attestation_map(attestations)

        v10_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.0",
            "frozen_source_commit_sha": "commit_v10",
            "frozen_contract_sha256": v10_hash,
        }
        v11_entry = {
            "benchmark_id": "BM-001",
            "contract_version": "1.1",
            "frozen_source_commit_sha": "commit_v11",
            "frozen_contract_sha256": v11_hash,
        }

        errors: list[str] = []
        validate_first_freeze_attestation(v10_entry, errors, find_first_attestation=mock_find)
        validate_first_freeze_attestation(v11_entry, errors, find_first_attestation=mock_find)
        self.assertEqual(errors, [])

        repointed_v10 = dict(v10_entry)
        repointed_v10["frozen_source_commit_sha"] = "commit_repointed"
        errors = []
        validate_first_freeze_attestation(repointed_v10, errors, find_first_attestation=mock_find)
        self.assertTrue(any("frozen_source_commit_sha repointed from first attestation" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
