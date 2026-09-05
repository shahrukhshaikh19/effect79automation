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
from runtime.host.craft_lock import inspect_hero_asset
from runtime.host.prompt_intake import classify_signals, intake_from_prompt
from runtime.host.skill_execution import SKILL_CONTRACTS, skill_md_sha256, validate_artifact_execution
from runtime.host.visual_class import (
    validate_lookdev_evidence,
    validate_visual_class,
    write_solid_png,
)
from runtime.routing.engine import route_task
import json
import math
import struct
import yaml
import zlib


def _noise_png(path: Path, width: int, height: int, base: int) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            v = (base + ((x * 17 + y * 11) % 40)) % 256
            raw.extend(bytes((v, min(255, v + 8), max(0, v - 6))))
    import struct
    import zlib

    compressed = zlib.compress(bytes(raw), 1)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b""))


def _framed_png(path: Path, width: int, height: int) -> None:
    raw = bytearray()
    mx, my = width // 5, height // 5
    for y in range(height):
        raw.append(0)
        for x in range(width):
            if x < mx or y < my or x >= width - mx or y >= height - my:
                raw.extend(b"\x08\x06\x0a")
            else:
                raw.extend(bytes((170, 150, 130)))
    compressed = zlib.compress(bytes(raw), 1)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b""))


def _craft_body(skill_id: str) -> str:
    evidence = {
        step: f"Executed {skill_id} {step} with unique production note {index:02d}."
        for index, step in enumerate(SKILL_CONTRACTS[skill_id]["procedure"])
    }
    return yaml.dump(
        {
            "skill_id": skill_id,
            "skill_md_sha256": skill_md_sha256(skill_id),
            "blender_used": True,
            "procedure_evidence": evidence,
        },
        sort_keys=False,
    )


def _write_glb(path: Path, meshes: list[tuple[str, list[tuple[float, float, float]]]]) -> None:
    blob = bytearray()
    views = []
    accessors = []
    gl_meshes = []
    nodes = []
    for index, (name, pts) in enumerate(meshes):
        raw = b"".join(struct.pack("<fff", *pt) for pt in pts)
        while len(blob) % 4:
            blob.append(0)
        offset = len(blob)
        blob.extend(raw)
        xs = [pt[0] for pt in pts]
        ys = [pt[1] for pt in pts]
        zs = [pt[2] for pt in pts]
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(raw)})
        accessors.append(
            {
                "bufferView": index,
                "componentType": 5126,
                "count": len(pts),
                "type": "VEC3",
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        )
        gl_meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": index}}]})
        nodes.append({"name": name, "mesh": index})
    while len(blob) % 4:
        blob.append(0)
    gltf = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gl_meshes,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4:
        json_bytes += b" "
    json_chunk = struct.pack("<I", len(json_bytes)) + b"JSON" + json_bytes
    bin_chunk = struct.pack("<I", len(blob)) + b"BIN\x00" + bytes(blob)
    header = b"glTF" + struct.pack("<II", 2, 12 + len(json_chunk) + len(bin_chunk))
    path.write_bytes(header + json_chunk + bin_chunk)


def _irregular_mesh() -> list[tuple[float, float, float]]:
    return [
        (0.0, 0.0, 0.0),
        (1.2, 0.1, 0.0),
        (0.4, 0.8, 0.2),
        (0.9, 0.3, 0.7),
        (-0.2, 0.5, 0.4),
        (0.3, -0.4, 0.6),
        (0.6, 0.2, -0.3),
        (1.1, 0.9, 0.1),
        (0.15, 0.55, 0.85),
        (-0.4, 0.2, 0.3),
        (0.7, -0.1, 0.5),
        (0.05, 0.95, -0.2),
        (0.8, 0.4, 0.15),
        (-0.1, 0.7, 0.6),
        (0.45, 0.05, 0.9),
        (1.0, 0.6, 0.35),
    ]


def _sphere_mesh(count: int = 80) -> list[tuple[float, float, float]]:
    pts: list[tuple[float, float, float]] = []
    phi = math.pi * (3.0 - 5.0**0.5)
    for i in range(count):
        y = 1.0 - (i / (count - 1)) * 2.0
        radius = math.sqrt(max(0.0, 1.0 - y * y))
        theta = phi * i
        pts.append((math.cos(theta) * radius, y, math.sin(theta) * radius))
    return pts


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

    def test_explicit_image_rebuild_still_routes_reconstruction(self) -> None:
        signals = classify_signals(
            "Rebuild this image in Three.js with img2three. Match this image exactly."
        )
        self.assertEqual(signals["deliverable_profile"], "reference_reconstruction")
        self.assertEqual(signals["reconstruction_path"], "procedural_browser")

    def test_mood_reference_does_not_become_img2threejs(self) -> None:
        signals = classify_signals(
            "Cinematic WebGL / Three.js landing page. The hero is a live 3D scene. "
            "Reference image is mood and composition only — do not reconstruct pixel-for-pixel. "
            "Blender must author the hero landscape and export GLB. "
            "Water: hover and drag ripples. Foliage sways as if wind is blowing."
        )
        self.assertEqual(signals["deliverable_profile"], "interactive_3d")
        self.assertEqual(signals["quality_bar"], "flagship")
        self.assertEqual(signals["reconstruction_path"], "blender_authoring")
        self.assertTrue(signals["requires_reference_analysis"])
        self.assertTrue(signals["requires_motion"])

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
        for skill_id in ("EXT-3DWEB-02", "EXT-3DWEB-03", "EXT-3DWEB-04", "EXT-BLD-01", "EXT-BLD-12", "EXT-BLD-13"):
            self.assertIn(skill_id, activated)

    def test_headphone_routes_hard_surface(self) -> None:
        intake = intake_from_prompt(
            "Create a flagship cinematic 3D launch website for a premium over-ear headphone. "
            "Blender must model this and export GLB."
        )
        intake["runtime_capabilities"]["blender"] = "AVAILABLE"
        decision = route_task(intake)
        activated = set(decision["activated_skill_ids"]) | set(decision.get("planned_skill_ids") or [])
        self.assertIn("EXT-BLD-13", activated)
        self.assertTrue(intake["task_signals"]["requires_physical_product"])

    def test_landscape_does_not_route_hard_surface(self) -> None:
        intake = intake_from_prompt(
            "Cinematic WebGL landscape. Blender must author the hero landscape and export GLB. "
            "Reference image is mood only — do not reconstruct."
        )
        intake["runtime_capabilities"]["blender"] = "AVAILABLE"
        decision = route_task(intake)
        activated = set(decision["activated_skill_ids"]) | set(decision.get("planned_skill_ids") or [])
        self.assertNotIn("EXT-BLD-13", activated)
        self.assertFalse(intake["task_signals"]["requires_physical_product"])

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


class VisualClassTests(unittest.TestCase):
    def test_lookdev_required_for_flagship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_lookdev_evidence(root, {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])

    def test_crushed_hero_fails_against_lit_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "evidence" / "viewports").mkdir(parents=True)
            write_solid_png(root / "references" / "mood.png", 48, 48, (180, 170, 200))
            write_solid_png(root / "evidence" / "viewports" / "desktop.png", 48, 48, (8, 6, 10))
            result = validate_visual_class(root, {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])
            self.assertTrue(any("silhouette" in item or "darker" in item for item in result["issues"]))

    def test_lit_hero_passes_against_lit_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "evidence" / "viewports").mkdir(parents=True)
            write_solid_png(root / "references" / "mood.png", 48, 48, (180, 170, 200))
            write_solid_png(root / "evidence" / "viewports" / "desktop.png", 48, 48, (160, 150, 180))
            result = validate_visual_class(root, {"quality_bar": "flagship"})
            self.assertTrue(result["ok"])

    def test_standard_app_skips_visual_class(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = validate_visual_class(Path(tmp), {"quality_bar": "standard"})
            self.assertTrue(result["ok"])

    def test_two_lookdev_shots_pass_without_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            look = root / "evidence" / "lookdev"
            look.mkdir(parents=True)
            _noise_png(look / "a.png", 400, 280, 90)
            _noise_png(look / "b.png", 400, 280, 100)
            result = validate_lookdev_evidence(root, {"quality_bar": "flagship"})
            self.assertTrue(result["ok"])

    def test_macro_lookdev_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            look = root / "evidence" / "lookdev"
            look.mkdir(parents=True)
            _noise_png(look / "a.png", 640, 400, 150)
            # overwrite with almost-flat scans so the file stays >4KB
            raw = bytearray()
            for y in range(400):
                raw.append(0)
                for x in range(640):
                    v = 150 + (x % 3)
                    raw.extend(bytes((v, v - 2, v - 4)))
            compressed = zlib.compress(bytes(raw), 1)
            ihdr = struct.pack(">IIBBBBB", 640, 400, 8, 2, 0, 0, 0)

            def chunk(tag: bytes, body: bytes) -> bytes:
                return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

            payload = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
            (look / "a.png").write_bytes(payload)
            (look / "b.png").write_bytes(payload)
            result = validate_lookdev_evidence(root, {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])
            self.assertTrue(any("macro" in item or "crop" in item for item in result["issues"]))

    def test_physical_lookdev_needs_full_object_frame(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            look = root / "evidence" / "lookdev"
            look.mkdir(parents=True)
            _noise_png(look / "a.png", 400, 280, 90)
            _noise_png(look / "b.png", 400, 280, 100)
            result = validate_lookdev_evidence(
                root, {"quality_bar": "flagship", "requires_physical_product": True}
            )
            self.assertFalse(result["ok"])
            _framed_png(look / "a.png", 400, 280)
            _framed_png(look / "b.png", 400, 280)
            result = validate_lookdev_evidence(
                root, {"quality_bar": "flagship", "requires_physical_product": True}
            )
            self.assertTrue(result["ok"])


class CraftLockTests(unittest.TestCase):
    def test_missing_modeler_artifact_fails_even_with_glb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "direction").mkdir()
            _write_glb(root / "implementation" / "hero.glb", [("SM_Body", _irregular_mesh())])
            (root / "direction" / "blender_export.yaml").write_text(
                _craft_body("EXT-BLD-12"), encoding="utf-8"
            )
            result = validate_flagship_production(root, ["EXT-BLD-12"], {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])
            self.assertTrue(any("blender_modeler.yaml" in item for item in result["missing"]))

    def test_unchecked_brief_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "implementation").mkdir()
            (root / "direction").mkdir()
            _write_glb(
                root / "implementation" / "hero.glb",
                [("SM_Cup", _irregular_mesh()), ("SM_Yoke", _irregular_mesh())],
            )
            for sid, rel in (
                ("EXT-BLD-01", "blender_production.yaml"),
                ("EXT-BLD-02", "blender_modeler.yaml"),
                ("EXT-BLD-03", "prop_artist.yaml"),
                ("EXT-BLD-05", "blender_materials.yaml"),
                ("EXT-BLD-06", "blender_lookdev.yaml"),
                ("EXT-3DWEB-02", "threejs_materials.yaml"),
                ("EXT-3DWEB-03", "threejs_lighting.yaml"),
                ("EXT-3DWEB-04", "threejs_camera.yaml"),
                ("EXT-BLD-12", "blender_export.yaml"),
            ):
                (root / "direction" / rel).write_text(_craft_body(sid), encoding="utf-8")
            (root / "direction" / "blender_production_brief.md").write_text(
                "## Pipeline\n- [x] Planning\n- [ ] Blockout & Silhouette\n- [ ] Modeling\n",
                encoding="utf-8",
            )
            result = validate_flagship_production(root, ["EXT-BLD-12"], {"quality_bar": "flagship"})
            self.assertFalse(result["ok"])
            self.assertTrue(any("unchecked" in item for item in result["invalid"]))

    def test_primitive_named_glb_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dump.glb"
            _write_glb(path, [("Sphere", _irregular_mesh()), ("Cylinder", _irregular_mesh())])
            result = inspect_hero_asset(path)
            self.assertFalse(result["ok"])
            self.assertTrue(any("primitive" in item for item in result["issues"]))

    def test_two_sphere_meshes_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cups.glb"
            _write_glb(path, [("SM_Cup_L", _sphere_mesh()), ("SM_Cup_R", _sphere_mesh())])
            result = inspect_hero_asset(path)
            self.assertFalse(result["ok"])
            self.assertTrue(any("sphere" in item.lower() for item in result["issues"]))


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
