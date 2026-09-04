#!/usr/bin/env python3
"""ACOS cross-phase consistency validator — detects semantic drift across A-D foundation."""

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
PHASE = "A-D hardening"

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

BROWSER_CAPABILITY_FILES = {
    "open_local_or_authorized_target": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "viewport_controlled_render": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "deterministic_screenshot": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "full_page_screenshot": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "element_region_screenshot": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "multi_viewport_capture": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "console_error_capture": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "page_error_capture": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "network_failure_capture": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "reduced_motion_emulation": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "readiness_wait_conditions": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "evidence_manifest_generation": REPO / "tools/browser/scripts/capture-evidence.mjs",
}

BROWSER_EVIDENCE_OUTPUTS = {
    "browser_evidence_manifest_yaml": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "screenshot_png": REPO / "tools/browser/scripts/capture-evidence.mjs",
    "console_log_json": REPO / "tools/browser/scripts/capture-evidence.mjs",
}

FORBIDDEN_DOMAIN = re.compile(r"\bcoffee\b", re.I)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_quality_gate_contract(errors: list[str]) -> None:
    stale_token_files = [
        REPO / "core" / "QUALITY_GATES.md",
        REPO / "skills" / "acos" / "acos-quality-gate" / "SKILL.md",
        REPO / "skills" / "acos" / "acos-quality-gate" / "references" / "gate-report-schema.yaml",
    ]
    for path in GATE_AUTHORITY_FILES:
        if not path.is_file():
            fail(errors, f"Missing gate authority file: {path.relative_to(REPO)}")
            continue
        text = load_text(path)
        present = {s for s in GATE_STATUSES if s in text}
        if not GATE_STATUSES.issubset(present):
            missing = GATE_STATUSES - present
            fail(errors, f"{path.relative_to(REPO)} missing gate statuses: {sorted(missing)}")
        if path not in stale_token_files:
            continue
        if re.search(r"\bAPPROVE\b(?!D)", text) and not re.search(r"\bAPPROVED\b", text):
            fail(errors, f"{path.relative_to(REPO)} contains stale APPROVE terminal token")
        if re.search(r"\bREJECT\b(?!ED)", text):
            fail(errors, f"{path.relative_to(REPO)} contains stale REJECT terminal token (not REJECTED)")

    # Semantic rules in core policy
    qg = REPO / "core" / "QUALITY_GATES.md"
    if qg.is_file():
        t = load_text(qg)
        if "BLOCKED is not approval" not in t and "BLOCKED_INSUFFICIENT_EVIDENCE is not approval" not in t:
            fail(errors, "core/QUALITY_GATES.md must state BLOCKED is not approval")
        if "may ship" not in t.lower():
            fail(errors, "core/QUALITY_GATES.md must distinguish APPROVED may ship")


def validate_phase_documentation(errors: list[str]) -> None:
    ledger = load_text(REPO / "docs" / "PROGRESS_LEDGER.md")
    checklist = load_text(REPO / "IMPLEMENTATION_CHECKLIST.md")

    for phase, token in (
        ("A", "COMPLETE"),
        ("B", "COMPLETE"),
        ("C", "COMPLETE"),
        ("D", "COMPLETE"),
    ):
        if token not in ledger or phase not in ledger:
            fail(errors, f"PROGRESS_LEDGER missing Phase {phase} completion evidence")

    if "Phase E" in checklist and "[x]" in checklist.split("## E")[1][:500]:
        fail(errors, "IMPLEMENTATION_CHECKLIST must not mark Phase E complete")

    if "NOT STARTED" not in ledger.split("Phase status")[1][:800]:
        fail(errors, "PROGRESS_LEDGER must show Phase E+ as NOT STARTED")

    for section in ("## A ", "## B ", "## C ", "## D "):
        if section not in checklist:
            fail(errors, f"IMPLEMENTATION_CHECKLIST missing section: {section.strip()}")
    if checklist.count("- [x]") < 20:
        fail(errors, "IMPLEMENTATION_CHECKLIST must reflect A-D evidence-backed completion")


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
        for field in ("requested_device_scale_factor", "effective_device_scale_factor", "console_log_json"):
            if field not in st:
                fail(errors, f"Browser schema missing field: {field}")


def validate_blender_health_semantics(errors: list[str]) -> None:
    path = REPO / "validation" / "check_blender_tool.py"
    text = load_text(path)
    if "mcp_connection_tested" in text:
        fail(errors, "check_blender_tool.py must not use misleading mcp_connection_tested field")
    for field in (
        "tcp_socket_probe_attempted",
        "tcp_socket_reachable",
        "protocol_handshake_attempted",
        "protocol_handshake_verified",
    ):
        if field not in text:
            fail(errors, f"check_blender_tool.py missing field: {field}")


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
    scan_roots = [REPO / "skills" / "acos", REPO / "tools/browser/fixtures", REPO / "registry"]
    for root in scan_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".html", ".mjs", ".py"}:
                continue
            try:
                if FORBIDDEN_DOMAIN.search(path.read_text(encoding="utf-8")):
                    fail(errors, f"Domain contamination in {path.relative_to(REPO)}")
            except (UnicodeDecodeError, OSError):
                continue


def validate_phase_boundaries(errors: list[str]) -> None:
    for name in ("benchmarks", "projects"):
        for item in (REPO / name).rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file() and item.stat().st_size > 0:
                fail(errors, f"{name}/ must remain empty: {item.relative_to(REPO)}")

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
    validate_phase_documentation(errors)
    validate_browser_capability_truth(errors)
    validate_blender_health_semantics(errors)
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
