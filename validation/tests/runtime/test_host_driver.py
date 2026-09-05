"""Host-driver intake, brief staging, and Design Gate tests."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.adapter.host_brief import select_invoke_ids
from runtime.host.artifact_contract import (
    pixel_evidence,
    validate_critic_independence,
    validate_creative_artifacts,
    validate_flagship_evidence,
    validate_flagship_production,
)
from runtime.host.audit import audit_session
from runtime.host.design_gate import evaluate_host_design_gate
from runtime.host.independence import implementation_fingerprint
from runtime.host.prompt_intake import classify_signals, intake_from_prompt
from runtime.host.skill_execution import SKILL_CONTRACTS, skill_md_sha256, validate_artifact_execution
from runtime.routing.engine import route_task


class PromptIntakeTests(unittest.TestCase):
    def test_no_default_3d_for_plain_app(self) -> None:
        signals = classify_signals("Add a settings form and save user preferences.")
        self.assertEqual(signals["deliverable_profile"], "standard_application")
        self.assertFalse(signals["requires_3d"])

    def test_3d_only_when_prompt_says_so(self) -> None:
        signals = classify_signals("Build a scroll-driven WebGL launch site with a Three.js hero.")
        self.assertEqual(signals["deliverable_profile"], "interactive_3d")
        self.assertTrue(signals["requires_3d"])
        self.assertEqual(signals["quality_bar"], "flagship")
        self.assertEqual(signals["reconstruction_path"], "blender_authoring")
        intake = intake_from_prompt("Build a scroll-driven WebGL launch site with a Three.js hero.")
        self.assertTrue(intake["normalized_goal"])

    def test_plain_3d_mention_is_not_flagship(self) -> None:
        signals = classify_signals("Add a small Three.js icon to the settings page.")
        self.assertEqual(signals["deliverable_profile"], "interactive_3d")
        self.assertEqual(signals["quality_bar"], "standard")
        self.assertEqual(signals["reconstruction_path"], "none")

    def test_locked_blender_brief_is_flagship_without_premium_word(self) -> None:
        signals = classify_signals(
            "BUILD ONLY THIS. Product: Cinderwell Still. "
            "Blender must model this still and export GLB. "
            "Scroll states, this order only: BENCH CHARGE RISE COIL CATCH."
        )
        self.assertEqual(signals["quality_bar"], "flagship")
        self.assertEqual(signals["reconstruction_path"], "blender_authoring")
        self.assertTrue(signals["requires_motion"])


class BriefStageTests(unittest.TestCase):
    def test_pending_creative_excludes_critics(self) -> None:
        activations = {
            "ACOS-01": {"stage": "CREATIVE_DIRECTION"},
            "ACOS-10": {"stage": "INDEPENDENT_CRITICS"},
            "ACOS-06": {"stage": "SPECIALIST_ROUTING"},
            "ACOS-13": {"stage": "QUALITY_GATE"},
        }
        invoke, focus = select_invoke_ids(
            ["ACOS-01", "ACOS-10", "ACOS-06", "ACOS-13"],
            activations,
            workflow_stage="WAITING_BLENDER",
            design_gate="PENDING",
        )
        self.assertEqual(invoke, [])
        self.assertEqual(focus, "waiting_blender")
        invoke, focus = select_invoke_ids(
            ["ACOS-01", "ACOS-10", "ACOS-06", "ACOS-13"],
            activations,
            workflow_stage="CREATIVE",
            design_gate="PENDING",
        )
        self.assertEqual(invoke, ["ACOS-01"])
        self.assertEqual(focus, "creative_and_design_gate")
        self.assertNotIn("ACOS-10", invoke)
        self.assertNotIn("ACOS-06", invoke)

    def test_production_after_gate(self) -> None:
        activations = {
            "ACOS-01": {"stage": "CREATIVE_DIRECTION"},
            "ACOS-06": {"stage": "SPECIALIST_ROUTING"},
            "EXT-3DWEB-01": {"stage": "PRODUCTION"},
        }
        invoke, focus = select_invoke_ids(
            ["ACOS-01", "ACOS-06", "EXT-3DWEB-01"],
            activations,
            workflow_stage="PRODUCTION",
            design_gate="APPROVED",
        )
        self.assertEqual(set(invoke), {"ACOS-06", "EXT-3DWEB-01"})
        self.assertEqual(focus, "specialist_production")


class DesignGateTests(unittest.TestCase):
    def test_missing_artifacts_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_host_design_gate(Path(tmp), ["ACOS-01", "ACOS-04"])
            self.assertEqual(result["status"], "BLOCKED_INSUFFICIENT_EVIDENCE")
            self.assertTrue(result["substantive_review_performed"])

    def test_thin_thesis_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "direction").mkdir()
            (root / "direction" / "creative_direction.yaml").write_text(
                "skill_procedure_executed: true\nproducer: acos-creative-director\ncentral_creative_thesis: short\n",
                encoding="utf-8",
            )
            result = evaluate_host_design_gate(root, ["ACOS-01"])
            self.assertEqual(result["status"], "REJECTED")


class EvidenceContractTests(unittest.TestCase):
    def test_scripts_and_yaml_are_not_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ev = root / "evidence"
            ev.mkdir()
            (ev / "capture-config.yaml").write_text("target: x\n", encoding="utf-8")
            (ev / "capture-states.mjs").write_text("console.log(1)\n", encoding="utf-8")
            (ev / "shot.png").write_bytes(b"0" * 64)
            self.assertEqual(pixel_evidence(root), ["evidence/shot.png"])


class IndependenceTests(unittest.TestCase):
    def test_same_session_cannot_attest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            critics = root / "critics"
            critics.mkdir()
            (critics / "visual_critic.yaml").write_text(
                "inspected_rendered_output: true\n"
                "independence: same_host_session_as_producer\n"
                "findings:\n  - {id: V-01, observation: x}\n",
                encoding="utf-8",
            )
            result = validate_critic_independence(
                root, ["ACOS-10"], critic_pass_id=None, attested=False
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["independent_host_context"], "UNVERIFIED")

    def test_boolean_attestation_does_not_prove_independence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            result = validate_critic_independence(
                root,
                ["ACOS-10"],
                critic_pass_id="pass-1",
                attested=True,
                roles={
                    "producer_host_context_id": None,
                    "critic_host_context_id": None,
                    "independent_host_context": "UNVERIFIED",
                    "independence_claim": "operator_attested",
                    "critic_pass_id": "pass-1",
                },
            )
            self.assertFalse(result["ok"])
            self.assertTrue(any("UNVERIFIED" in item for item in result["issues"]))

    def test_distinct_host_context_can_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "implementation" / "index.html").write_text("<html></html>", encoding="utf-8")
            critics = root / "critics"
            critics.mkdir()
            (critics / "visual_critic.yaml").write_text(
                "inspected_rendered_output: true\n"
                "critic_pass_id: pass-1\n"
                "findings:\n  - {id: V-01, observation: x}\n",
                encoding="utf-8",
            )
            frozen = implementation_fingerprint(root)
            result = validate_critic_independence(
                root,
                ["ACOS-10"],
                critic_pass_id="pass-1",
                attested=False,
                roles={
                    "producer_host_context_id": "producer-chat",
                    "critic_host_context_id": "critic-chat",
                    "independent_host_context": "DISTINCT",
                    "critic_pass_id": "pass-1",
                    "critic_frozen_implementation_sha256": frozen,
                },
            )
            self.assertTrue(result["ok"])

    def test_audit_blocks_ship_without_distinct_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "implementation" / "index.html").write_text("<html></html>", encoding="utf-8")
            (root / "evidence").mkdir()
            (root / "evidence" / "a.png").write_bytes(b"0" * 64)
            (root / "evidence" / "b.png").write_bytes(b"0" * 64)
            session = {
                "intake": {"task_id": "host-test"},
                "routing": {"routing_id": "r1", "planned_skill_ids": []},
                "state": {
                    "current_stage": "QUALITY_GATE",
                    "planned_skill_ids": ["ACOS-10"],
                    "gate_states": {"design_gate": "APPROVED", "quality_gate": "NOT_EVALUATED"},
                },
                "roles": {
                    "producer_session_id": "p1",
                    "critic_pass_id": "pass-1",
                    "independent_attestation": True,
                    "independence_claim": "operator_attested",
                    "independent_host_context": "UNVERIFIED",
                },
            }
            audit = audit_session(session, root)
            self.assertFalse(audit["ship_allowed"])
            self.assertTrue(any("UNVERIFIED" in b or "DISTINCT" in b for b in audit["blockers"]))


class FlagshipWorkflowTests(unittest.TestCase):
    def test_locked_blender_brief_routes_craft_pack(self) -> None:
        intake = intake_from_prompt(
            "BUILD ONLY THIS. Product: Cinderwell Still. "
            "Blender must model this still and export GLB. "
            "Scroll states, this order only: BENCH CHARGE RISE COIL CATCH."
        )
        intake["runtime_capabilities"]["blender"] = "AVAILABLE"
        decision = route_task(intake)
        activated = set(decision["activated_skill_ids"]) | set(decision.get("planned_skill_ids") or [])
        self.assertEqual(decision["status"], "ROUTED")
        for skill_id in ("EXT-3DWEB-02", "EXT-3DWEB-03", "EXT-3DWEB-04", "EXT-BLD-01", "EXT-BLD-12"):
            self.assertIn(skill_id, activated)

    def test_flagship_route_activates_craft_and_blender(self) -> None:
        intake = intake_from_prompt(
            "Build a premium cinematic 3D launch website for an original physical instrument."
        )
        intake["runtime_capabilities"]["blender"] = "AVAILABLE"
        decision = route_task(intake)
        activated = set(decision["activated_skill_ids"]) | set(decision.get("planned_skill_ids") or [])
        self.assertEqual(decision["status"], "ROUTED")
        for skill_id in ("EXT-3DWEB-02", "EXT-3DWEB-03", "EXT-3DWEB-04", "EXT-BLD-01", "EXT-BLD-12"):
            self.assertIn(skill_id, activated)

    def test_flagship_blocks_without_blender(self) -> None:
        intake = intake_from_prompt(
            "Build a premium cinematic 3D launch website for an original physical instrument."
        )
        intake["runtime_capabilities"]["blender"] = "UNAVAILABLE"
        decision = route_task(intake)
        self.assertEqual(decision["status"], "ROUTING_BLOCKED_CAPABILITY")

    def test_flagship_production_requires_glb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "implementation" / "index.html").write_text("<html></html>", encoding="utf-8")
            result = validate_flagship_production(
                root,
                ["EXT-BLD-12", "EXT-3DWEB-02"],
                {"quality_bar": "flagship"},
            )
            self.assertFalse(result["ok"])

    def test_export_stamp_cannot_be_threejs_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "implementation" / "hero.glb").write_bytes(b"0" * 64)
            (root / "direction").mkdir()
            (root / "direction" / "blender_export.yaml").write_text(
                "skill_procedure_executed: true\nblender_used: true\nproducer: threejs-core\n",
                encoding="utf-8",
            )
            result = validate_flagship_production(root, ["EXT-BLD-12"], {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])
            self.assertTrue(any("threejs-core" in item for item in result["invalid"]))

    def test_named_scroll_beats_need_state_shots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence" / "viewports").mkdir(parents=True)
            (root / "evidence" / "viewports" / "desktop.png").write_bytes(b"0" * 64)
            result = validate_flagship_evidence(
                root,
                {"quality_bar": "flagship"},
                "Scroll states, this order only: BENCH CHARGE RISE COIL CATCH.",
            )
            self.assertFalse(result["ok"])


class SkillExecutionProofTests(unittest.TestCase):
    def test_boolean_flag_is_not_execution_proof(self) -> None:
        issues = validate_artifact_execution(
            {"skill_procedure_executed": True, "producer": "acos-creative-director"},
            "ACOS-01",
        )
        self.assertTrue(issues)

    def test_producer_name_is_not_execution_proof(self) -> None:
        issues = validate_artifact_execution({"producer": "acos-creative-director"}, "ACOS-01")
        self.assertTrue(issues)

    def test_hash_mismatch_fails(self) -> None:
        issues = validate_artifact_execution(
            {
                "skill_id": "ACOS-01",
                "skill_md_sha256": "0" * 64,
                "procedure_evidence": {
                    step: f"Executed canonical SKILL.md {step} with unique note {index:02d}."
                    for index, step in enumerate(SKILL_CONTRACTS["ACOS-01"]["procedure"])
                },
            },
            "ACOS-01",
        )
        self.assertTrue(any("does not match live SKILL.md" in item for item in issues))

    def test_live_hash_and_procedure_evidence_pass_binding(self) -> None:
        data = {
            "skill_id": "ACOS-01",
            "skill_md_sha256": skill_md_sha256("ACOS-01"),
            "procedure_evidence": {
                step: f"Executed canonical SKILL.md {step} with unique note {index:02d}."
                for index, step in enumerate(SKILL_CONTRACTS["ACOS-01"]["procedure"])
            },
        }
        self.assertEqual(validate_artifact_execution(data, "ACOS-01"), [])

    def test_creative_validator_rejects_self_attested_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "direction").mkdir()
            (root / "direction" / "creative_direction.yaml").write_text(
                "skill_procedure_executed: true\nproducer: acos-creative-director\n"
                "central_creative_thesis: a long enough thesis that would have passed the old boolean check.\n",
                encoding="utf-8",
            )
            result = validate_creative_artifacts(root, ["ACOS-01"])
            self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
