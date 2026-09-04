#!/usr/bin/env python3
"""ACOS cross-phase consistency validator — semantic drift detection across A-D foundation."""

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
PHASE = "A-D certification"

GATE_STATUSES = {
    "APPROVED",
    "REJECTED",
    "BLOCKED_INSUFFICIENT_EVIDENCE",
}

GATE_AUTHORITY_FILES = [
    REPO / "ACOS_FINAL_CANONICAL_v1.2.md",
    REPO / "core" / "QUALITY_GATES.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "SKILL.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "references" / "gate-report-schema.yaml",
]

STALE_TOKEN_FILES = [
    REPO / "core" / "QUALITY_GATES.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "SKILL.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "references" / "gate-report-schema.yaml",
]

GATE_HR_EB_FILES = [
    REPO / "core" / "QUALITY_GATES.md",
    REPO / "ACOS_FINAL_CANONICAL_v1.2.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "SKILL.md",
    REPO / "skills" / "acos" / "acos-quality-gate" / "references" / "gate-report-schema.yaml",
]

BLENDER_DOC_FILES = [
    REPO / "docs" / "PROGRESS_LEDGER.md",
    REPO / "docs" / "TOOLS_AUDIT.md",
    REPO / "docs" / "BLENDER_RUNTIME_CORRECTION.md",
    REPO / "docs" / "FOUNDATION_CERTIFICATION_HARDENING.md",
]


def _blender_doc_line_contradictory(line: str) -> bool:
    lower = line.lower()
    if "blender" not in lower and "tool-blender" not in lower:
        return False
    if any(x in lower for x in ("not available", "never claims", "must not", "≠", "!=", "not verified")):
        return False
    if "available when mcp" in lower:
        return True
    if re.search(r"health[- ]script.*\bavailable\b", lower) and "restricted" not in lower:
        return True
    if re.search(r"mcp_connection_tested:\s*true", line, re.I):
        return True
    return False

LEGACY_PHASE_SECTIONS = [
    "## H —",
    "## I —",
    "## J —",
    "Phase H —",
    "Phase I —",
    "Phase J —",
]

FOUNDATION_PHASE_LETTERS = ("A", "B", "C", "D", "E", "F", "G")


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path, errors: list[str]) -> dict | None:
    if not path.is_file():
        fail(errors, f"Missing YAML: {path.relative_to(REPO)}")
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(errors, f"Invalid YAML mapping: {path.relative_to(REPO)}")
        return None
    return data


def validate_quality_gate_contract(errors: list[str]) -> None:
    for path in GATE_AUTHORITY_FILES:
        if not path.is_file():
            fail(errors, f"Missing gate authority file: {path.relative_to(REPO)}")
            continue
        text = load_text(path)
        present = {s for s in GATE_STATUSES if s in text}
        if not GATE_STATUSES.issubset(present):
            missing = GATE_STATUSES - present
            fail(errors, f"{path.relative_to(REPO)} missing gate statuses: {sorted(missing)}")
        if path not in STALE_TOKEN_FILES:
            continue
        if re.search(r"\bAPPROVE\b(?!D)", text) and not re.search(r"\bAPPROVED\b", text):
            fail(errors, f"{path.relative_to(REPO)} contains stale APPROVE terminal token")
        if re.search(r"\bREJECT\b(?!ED)", text):
            fail(errors, f"{path.relative_to(REPO)} contains stale REJECT terminal token (not REJECTED)")

    qg = REPO / "core" / "QUALITY_GATES.md"
    if qg.is_file():
        t = load_text(qg)
        if "BLOCKED is not approval" not in t and "BLOCKED_INSUFFICIENT_EVIDENCE is not approval" not in t:
            fail(errors, "core/QUALITY_GATES.md must state BLOCKED is not approval")
        if "may ship" not in t.lower():
            fail(errors, "core/QUALITY_GATES.md must distinguish APPROVED may ship")


def validate_hr_eb_separation(errors: list[str]) -> None:
    """HR-01..HR-10 = artifact defects → REJECTED; EB-01 = evidence insufficiency → BLOCKED."""
    for path in GATE_HR_EB_FILES:
        if not path.is_file():
            continue
        text = load_text(path)
        if "HR-11" in text:
            fail(errors, f"{path.relative_to(REPO)} still references HR-11 — use EB-01 for evidence insufficiency")
        if re.search(r"required_evidence_not_collected", text):
            fail(errors, f"{path.relative_to(REPO)} uses required_evidence_not_collected — use EB-01 / required_evidence_insufficient")

    schema_path = REPO / "skills/acos/acos-quality-gate/references/gate-report-schema.yaml"
    if schema_path.is_file():
        schema = load_text(schema_path)
        if "evidence_blockers:" not in schema:
            fail(errors, "gate-report-schema.yaml missing evidence_blockers section")
        if "EB-01" not in schema:
            fail(errors, "gate-report-schema.yaml missing EB-01 evidence blocker")
        hr_ids = re.findall(r"id: (HR-\d+)", schema)
        if "HR-11" in hr_ids:
            fail(errors, "gate-report-schema.yaml HR-11 must be removed — evidence insufficiency is EB-01")
        if hr_ids and max(int(h.split("-")[1]) for h in hr_ids) > 10:
            fail(errors, "gate-report-schema.yaml hard_rejects must be HR-01..HR-10 only")

    skill = REPO / "skills/acos/acos-quality-gate/SKILL.md"
    if skill.is_file():
        st = load_text(skill)
        if "EB-01" not in st:
            fail(errors, "acos-quality-gate SKILL.md must reference EB-01")
        if "Decision precedence" not in st and "Decision precedence (deterministic)" not in st:
            fail(errors, "acos-quality-gate SKILL.md must document deterministic decision precedence")
        if re.search(r"hard reject.*HR-11|HR-11.*hard reject", st, re.I):
            fail(errors, "acos-quality-gate SKILL.md must not map missing evidence to HR hard reject")
        if "REJECTED for evidence insufficiency alone" not in st:
            fail(errors, "acos-quality-gate SKILL.md must forbid REJECTED for evidence insufficiency alone")


def validate_phase_map(errors: list[str]) -> None:
    phases_path = REPO / "registry" / "PHASES.yaml"
    phases = load_yaml(phases_path, errors)
    if not phases:
        return

    foundation = phases.get("foundation")
    post = phases.get("post_foundation")
    if not isinstance(foundation, dict) or not isinstance(post, dict):
        fail(errors, "registry/PHASES.yaml must define foundation and post_foundation mappings")
        return

    expected_foundation = {
        "A": "canonical_foundation",
        "B": "external_skills",
        "C": "proprietary_skills",
        "D": "production_tools",
        "E": "adapters",
        "F": "routing_memory_quality_integration",
        "G": "foundation_validation",
    }
    for letter, name in expected_foundation.items():
        entry = foundation.get(letter)
        if not isinstance(entry, dict):
            fail(errors, f"PHASES.yaml missing foundation phase {letter}")
            continue
        if entry.get("name") != name:
            fail(errors, f"PHASES.yaml foundation {letter} name must be {name}, got {entry.get('name')}")

    expected_pf = {
        "PF-1": "benchmark_registration",
        "PF-2": "benchmark_evidence_correction",
        "PF-3": "generalization_benchmarks",
        "PF-4": "scale_infrastructure",
        "PF-5": "evidence_warranted_fine_tuning",
    }
    for pf_id, name in expected_pf.items():
        entry = post.get(pf_id)
        if not isinstance(entry, dict):
            fail(errors, f"PHASES.yaml missing post_foundation {pf_id}")
            continue
        if entry.get("name") != name:
            fail(errors, f"PHASES.yaml {pf_id} name must be {name}")

    exec_state = phases.get("execution_state", {})
    foundation_state = exec_state.get("foundation", {}) if isinstance(exec_state, dict) else {}
    for letter in ("A", "B", "C", "D"):
        if foundation_state.get(letter) != "COMPLETE":
            fail(errors, f"PHASES.yaml execution_state.{letter} must be COMPLETE")
    for letter in ("E", "F", "G"):
        if foundation_state.get(letter) != "NOT_STARTED":
            fail(errors, f"PHASES.yaml execution_state.{letter} must be NOT_STARTED")
    if exec_state.get("post_foundation") != "NOT_STARTED":
        fail(errors, "PHASES.yaml post_foundation must be NOT_STARTED")

    checklist = load_text(REPO / "IMPLEMENTATION_CHECKLIST.md")
    ledger = load_text(REPO / "docs" / "PROGRESS_LEDGER.md")
    canonical = load_text(REPO / "ACOS_FINAL_CANONICAL_v1.2.md")

    for legacy in LEGACY_PHASE_SECTIONS:
        if legacy in checklist:
            fail(errors, f"IMPLEMENTATION_CHECKLIST contains legacy phase section: {legacy.strip()}")

    if "registry/PHASES.yaml" not in checklist:
        fail(errors, "IMPLEMENTATION_CHECKLIST must reference registry/PHASES.yaml")

    if "## F — Routing + memory + quality integration" not in checklist:
        fail(errors, "IMPLEMENTATION_CHECKLIST Phase F must be routing_memory_quality_integration")
    if "## G — Foundation validation / certification" not in checklist:
        fail(errors, "IMPLEMENTATION_CHECKLIST Phase G must be foundation_validation")
    if "POST-FOUNDATION" not in checklist or "PF-1" not in checklist:
        fail(errors, "IMPLEMENTATION_CHECKLIST must define POST-FOUNDATION PF roadmap")

    if "Benchmark registration" in checklist.split("## F")[1].split("## G")[0]:
        fail(errors, "IMPLEMENTATION_CHECKLIST must not assign benchmark registration to Foundation Phase F")

    if "routing_memory_quality_integration" not in ledger and "Routing + memory + quality integration" not in ledger:
        fail(errors, "PROGRESS_LEDGER Phase F description must match PHASES.yaml")
    if "Foundation validation / certification" not in ledger:
        fail(errors, "PROGRESS_LEDGER must define Phase G foundation validation")
    if re.search(r"\|\s*H\s*\|", ledger) or re.search(r"\|\s*J\s*\|", ledger):
        fail(errors, "PROGRESS_LEDGER must not use legacy Foundation phases H–J")
    if "PF-*" not in ledger and "post_foundation" not in ledger.lower() and "POST-FOUNDATION" not in ledger:
        fail(errors, "PROGRESS_LEDGER must reference post-foundation PF roadmap")

    if "PHASE H —" in canonical or "PHASE J —" in canonical:
        fail(errors, "ACOS_FINAL_CANONICAL must not define legacy Foundation phases H–J")
    if "PF-1" not in canonical:
        fail(errors, "ACOS_FINAL_CANONICAL must define POST-FOUNDATION PF roadmap")

    for phase, token in (("A", "COMPLETE"), ("B", "COMPLETE"), ("C", "COMPLETE"), ("D", "COMPLETE")):
        if token not in ledger or phase not in ledger:
            fail(errors, f"PROGRESS_LEDGER missing Phase {phase} completion evidence")

    e_section = checklist.split("## E")[1].split("## F")[0] if "## E" in checklist else ""
    if "[x]" in e_section[:600]:
        fail(errors, "IMPLEMENTATION_CHECKLIST must not mark Phase E complete")
    for section_marker in ("## F ", "## G "):
        if section_marker in checklist:
            section = checklist.split(section_marker)[1].split("##")[0]
            if "[x]" in section[:800]:
                fail(errors, f"IMPLEMENTATION_CHECKLIST must not mark {section_marker.strip()} complete")


def validate_blender_documentation(errors: list[str]) -> None:
    script = REPO / "validation" / "check_blender_tool.py"
    if script.is_file():
        text = load_text(script)
        if "mcp_connection_tested" in text:
            fail(errors, "check_blender_tool.py must not use misleading mcp_connection_tested field")
        for field in (
            "tcp_socket_probe_attempted",
            "tcp_socket_reachable",
            "protocol_handshake_attempted",
            "protocol_handshake_verified",
            "addon_runtime_verified",
        ):
            if field not in text:
                fail(errors, f"check_blender_tool.py missing field: {field}")
        if re.search(r'runtime\s*=\s*"AVAILABLE"', text):
            fail(errors, "check_blender_tool.py must not return AVAILABLE without protocol handshake verification")

    tools = load_yaml(REPO / "registry" / "TOOLS.yaml", errors)
    if isinstance(tools, dict):
        blender = next((t for t in tools.get("tools", []) if t.get("id") == "TOOL-BLENDER-01"), None)
        if isinstance(blender, dict) and blender.get("status") not in ("restricted", "configured", "blocked"):
            fail(errors, "TOOL-BLENDER-01 registry status must reflect unresolved protocol verification")

    for path in BLENDER_DOC_FILES:
        if not path.is_file():
            continue
        for line in load_text(path).splitlines():
            if _blender_doc_line_contradictory(line):
                fail(
                    errors,
                    f"{path.relative_to(REPO)} contradictory Blender runtime claim: {line.strip()[:120]}",
                )
                break


def validate_browser_capability_truth(errors: list[str]) -> None:
    tools = yaml.safe_load((REPO / "registry" / "TOOLS.yaml").read_text(encoding="utf-8"))
    browser = next(t for t in tools["tools"] if t["id"] == "TOOL-BROWSER-01")
    caps = browser.get("capabilities", [])
    outputs = browser.get("evidence_outputs", [])

    cap_map = {
        "open_local_or_authorized_target": "resolveTarget",
        "viewport_controlled_render": "deviceScaleFactor",
        "deterministic_screenshot": "screenshot",
        "full_page_screenshot": "fullPage: true",
        "element_region_screenshot": "element",
        "multi_viewport_capture": "viewports",
        "console_error_capture": "console_errors",
        "page_error_capture": "pageerror",
        "network_failure_capture": "network_failures",
        "reduced_motion_emulation": "reducedMotion",
        "readiness_wait_conditions": "waitUntil",
        "evidence_manifest_generation": "manifest.yaml",
    }
    script = REPO / "tools/browser/scripts/capture-evidence.mjs"
    script_text = load_text(script) if script.is_file() else ""

    for cap in caps:
        needle = cap_map.get(cap)
        if needle and needle not in script_text:
            fail(errors, f"Browser capability {cap} not evidenced in capture script ({needle})")

    output_map = {
        "browser_evidence_manifest_yaml": "manifest.yaml",
        "screenshot_png": "screenshot",
        "console_log_json": "console_log.json",
    }
    for out in outputs:
        key = out.replace("-", "_") if isinstance(out, str) else out
        needle = output_map.get(key if key in output_map else out)
        if needle and needle not in script_text:
            fail(errors, f"Browser evidence output {out} not implemented in capture script")

    schema = REPO / "tools/browser/schemas/browser-evidence.schema.yaml"
    if schema.is_file():
        st = load_text(schema)
        for field in (
            "requested_device_scale_factor",
            "effective_device_scale_factor",
            "dpr_integrity",
            "console_log_json",
        ):
            if field not in st:
                fail(errors, f"Browser schema missing field: {field}")


def validate_blender_capabilities_structure(errors: list[str]) -> None:
    caps = yaml.safe_load((REPO / "tools/blender-mcp/capabilities.yaml").read_text(encoding="utf-8"))
    for key in ("native_capabilities", "derived_via_execute_blender_code", "restricted_capabilities"):
        if key not in caps:
            fail(errors, f"capabilities.yaml missing {key}")


def validate_openai_license_metadata(errors: list[str]) -> None:
    lock = yaml.safe_load((REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml").read_text(encoding="utf-8"))
    for eid in ("EXT-FE-01", "EXT-FE-02"):
        entry = next(e for e in lock["entries"] if e["id"] == eid)
        if entry.get("license") != "LICENSE_REVIEW_REQUIRED":
            fail(errors, f"{eid} license must remain LICENSE_REVIEW_REQUIRED unless explicit evidence found")
        if entry.get("commercial_redistribution_status") != "blocked_pending_license_review":
            fail(errors, f"{eid} missing commercial_redistribution_status restriction")


def validate_domain_neutrality(errors: list[str]) -> None:
    for name in ("benchmarks", "projects"):
        for item in (REPO / name).rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file() and item.stat().st_size > 0:
                fail(errors, f"{name}/ must remain empty during foundation: {item.relative_to(REPO)}")

    routing = REPO / "core" / "ROUTING.md"
    if routing.is_file():
        rt = load_text(routing).lower()
        for phrase in ("always activate 3d", "mandatory 3d", "3d-first default", "every project requires 3d"):
            if phrase in rt:
                fail(errors, f"core/ROUTING.md suggests mandatory 3D route: {phrase}")

    constitution = REPO / "core" / "CONSTITUTION.md"
    if constitution.is_file():
        ct = load_text(constitution).lower()
        if "house style" in ct and "no default" not in ct and "domain neutral" not in ct:
            fail(errors, "core/CONSTITUTION.md may declare fixed house style without domain neutrality guard")

    registry_skills = REPO / "registry" / "SKILLS.yaml"
    if registry_skills.is_file():
        st = load_text(registry_skills).lower()
        if re.search(r"default_(brand|product|industry|aesthetic)", st):
            fail(errors, "registry/SKILLS.yaml must not embed default brand/product/industry")


def validate_phase_boundaries(errors: list[str]) -> None:
    for adapter in ("claude", "cursor", "codex"):
        ad = REPO / "adapters" / adapter
        if ad.is_dir():
            for f in ad.iterdir():
                if f.name != ".gitkeep" and f.is_file():
                    fail(errors, f"Phase E adapter file: {f.relative_to(REPO)}")


def run_regression(errors: list[str]) -> None:
    for script in (
        "validate_foundation.py",
        "validate_external_skills.py",
        "validate_proprietary_skills.py",
        "validate_tools.py",
    ):
        result = subprocess.run(
            [sys.executable, str(REPO / "validation" / script)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        if result.returncode != 0:
            fail(errors, f"Regression failed: {script}")


def main() -> int:
    errors: list[str] = []
    if yaml is None:
        fail(errors, "PyYAML required")
        return 1

    print(f"ACOS v1.2 {PHASE} Cross-Phase Consistency Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    validate_quality_gate_contract(errors)
    validate_hr_eb_separation(errors)
    validate_phase_map(errors)
    validate_blender_documentation(errors)
    validate_browser_capability_truth(errors)
    validate_blender_capabilities_structure(errors)
    validate_openai_license_metadata(errors)
    validate_domain_neutrality(errors)
    validate_phase_boundaries(errors)
    run_regression(errors)

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print("Cross-phase consistency checks complete.")
    print("Later phases are outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
