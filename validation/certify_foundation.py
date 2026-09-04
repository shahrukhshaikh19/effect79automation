#!/usr/bin/env python3
"""Phase G foundation certification runner — orchestrates G1–G4 layers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
VALIDATION = REPO / "validation"
EVIDENCE_DIR = VALIDATION / "evidence" / "foundation"
MANIFEST_PATH = EVIDENCE_DIR / "CERTIFICATION_MANIFEST.json"
RESULT_PATH = VALIDATION / "FOUNDATION_CERTIFICATION_RESULT.json"
CONTRACT_PATH = REPO / "registry" / "FOUNDATION_CERTIFICATION.yaml"

ORCHESTRATED_VALIDATORS = [
    "validate_foundation.py",
    "validate_external_skills.py",
    "validate_proprietary_skills.py",
    "validate_tools.py",
    "validate_adapters.py",
    "validate_runtime_integration.py",
    "validate_cross_phase_consistency.py",
    "validate_foundation_adversarial.py",
]

TOOL_HEALTH_CHECKS = [
    "check_browser_tool.py",
    "check_blender_tool.py",
    "check_git_tool.py",
    "check_shell_tool.py",
    "check_filesystem_tool.py",
]

RUNTIME_MODULES = (
    "intake", "routing", "handoff", "evidence", "quality",
    "correction", "memory", "state", "adapter",
)

VENDOR_PATTERNS = [
    re.compile(r"\bclaude\b.*required", re.I),
    re.compile(r"\bcursor\b.*required", re.I),
    re.compile(r"\bcodex\b.*required", re.I),
]

MANDATORY_AESTHETIC = re.compile(
    r"always use (glassmorphism|gradients|cinematic 3d|dark theme|centered hero|animate everything)",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _entry(
    check_id: str,
    layer: str,
    claim: str,
    evidence_type: str,
    producer: str,
    command: str,
    result: str,
    *,
    artifact_ref: str = "",
    limitations: str = "",
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "layer": layer,
        "phase": "G",
        "claim": claim,
        "evidence_type": evidence_type,
        "producer": producer,
        "command": command,
        "result": result,
        "artifact_ref": artifact_ref,
        "timestamp": _now(),
        "reproducibility": "deterministic" if evidence_type != "LOCAL_RUNTIME_PROBE" else "environment-dependent",
        "limitations": limitations,
    }


def run_script(script: str, *, timeout: int = 300) -> dict[str, Any]:
    path = VALIDATION / script
    if not path.is_file():
        return {"script": script, "exit_code": 127, "stdout": "", "stderr": "missing script"}
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "script": script,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-4000:] if len(proc.stdout) > 4000 else proc.stdout,
        "stderr": proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr,
    }


def run_unittest(module: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", module, "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    passed = proc.returncode == 0
    discovered = len(re.findall(r"^test_", proc.stdout + proc.stderr, re.M))
    return {
        "module": module,
        "exit_code": proc.returncode,
        "passed": passed,
        "discovered_approx": discovered,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-1000:],
    }


def run_smoke() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO / "runtime" / "smoke.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "script": "runtime/smoke.py",
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-1000:],
    }


def g1_structural(entries: list[dict], blockers: list[str]) -> bool:
    ok = True

    canonical = REPO / "ACOS_FINAL_CANONICAL_v1.2.md"
    if not canonical.is_file():
        blockers.append("G1: missing canonical master")
        ok = False
    else:
        entries.append(_entry(
            "G1-canonical-master", "structural", "Single canonical master exists",
            "STATIC_INSPECTION", "certify_foundation.py", "path check", "PASS",
            artifact_ref=str(canonical.relative_to(REPO)),
        ))

    for core in ("CONSTITUTION.md", "QUALITY_GATES.md", "ROUTING.md", "MEMORY_POLICY.md"):
        path = REPO / "core" / core
        if not path.is_file():
            blockers.append(f"G1: missing core/{core}")
            ok = False

    phases = yaml.safe_load((REPO / "registry" / "PHASES.yaml").read_text(encoding="utf-8"))
    foundation_letters = {k for k in (phases.get("foundation") or {}) if len(k) == 1}
    if foundation_letters != {"A", "B", "C", "D", "E", "F", "G"}:
        blockers.append(f"G1: phase map drift: {sorted(foundation_letters)}")
        ok = False

    lock = yaml.safe_load((REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml").read_text(encoding="utf-8"))
    ext_entries = lock.get("entries") or []
    if len(ext_entries) != 36:
        blockers.append(f"G1: external skill count {len(ext_entries)} != 36")
        ok = False
    entries.append(_entry(
        "G1-external-skills", "structural", "Exactly 36 external skills locked",
        "STATIC_INSPECTION", "certify_foundation.py", "EXTERNAL_SKILLS_LOCK.yaml count", "PASS" if len(ext_entries) == 36 else "FAIL",
    ))

    skills = yaml.safe_load((REPO / "registry" / "SKILLS.yaml").read_text(encoding="utf-8"))
    proprietary = skills.get("proprietary") or []
    if len(proprietary) != 14:
        blockers.append(f"G1: proprietary skill count {len(proprietary)} != 14")
        ok = False

    adapters = yaml.safe_load((REPO / "registry" / "ADAPTERS.yaml").read_text(encoding="utf-8"))
    families = {a.get("platform", "").lower() for a in (adapters.get("adapters") or []) if isinstance(a, dict)}
    expected = {"claude", "cursor", "codex", "local"}
    if families != expected:
        blockers.append(f"G1: adapter families {sorted(families)} != expected")
        ok = False

    monolith = REPO / "runtime" / "orchestrator.py"
    if monolith.is_file():
        blockers.append("G1: forbidden runtime/orchestrator.py present")
        ok = False
    for mod in RUNTIME_MODULES:
        if not (REPO / "runtime" / mod).is_dir():
            blockers.append(f"G1: missing runtime/{mod}")
            ok = False

    from benchmark_scope import scan_benchmarks_and_projects

    bench_errors: list[str] = []
    scan_benchmarks_and_projects(bench_errors, lambda errs, msg: errs.append(msg))
    if bench_errors:
        blockers.extend(f"G1: {e}" for e in bench_errors)
        ok = False

    entries.append(_entry(
        "G1-runtime-modular", "structural", "Phase F runtime modular; no monolith",
        "STATIC_INSPECTION", "certify_foundation.py", "runtime/ layout", "PASS" if ok else "FAIL",
    ))
    return ok


def g2_semantic(entries: list[dict], blockers: list[str]) -> bool:
    ok = True

    qg = (REPO / "core" / "QUALITY_GATES.md").read_text(encoding="utf-8")
    if "HR-11" in qg and "forbidden" not in qg.lower() and "not allowed" not in qg.lower():
        if re.search(r"HR-11.*allowed", qg, re.I):
            blockers.append("G2: HR-11 may be allowed in QUALITY_GATES")
            ok = False
    entries.append(_entry(
        "G2-hr-eb-semantics", "semantic", "HR/EB gate semantics preserved",
        "STATIC_INSPECTION", "certify_foundation.py", "core/QUALITY_GATES.md", "PASS" if ok else "FAIL",
    ))

    schema = (REPO / "runtime" / "schemas" / "ADAPTER_TASK_PACKET.schema.yaml").read_text(encoding="utf-8")
    if "phase_f_router" not in schema:
        blockers.append("G2: ADAPTER_TASK_PACKET missing phase_f_router")
        ok = False
    if "adapter_must_not" not in schema:
        blockers.append("G2: ADAPTER_TASK_PACKET missing adapter_must_not")
        ok = False

    lock = yaml.safe_load((REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml").read_text(encoding="utf-8"))
    fe_blocked = [
        e for e in (lock.get("entries") or [])
        if e.get("id") in ("EXT-FE-01", "EXT-FE-02") and e.get("license") == "LICENSE_REVIEW_REQUIRED"
    ]
    if len(fe_blocked) != 2:
        blockers.append("G2: EXT-FE-01/02 license status not truthful")
        ok = False

    models = yaml.safe_load((REPO / "registry" / "MODELS.yaml").read_text(encoding="utf-8"))
    if models.get("policy", {}).get("no_invented_benchmark_results") is not True:
        blockers.append("G2: MODELS.yaml missing no_invented_benchmark_results policy")
        ok = False
    if models.get("models"):
        blockers.append("G2: MODELS.yaml contains models without benchmark evidence")
        ok = False

    for pat in VENDOR_PATTERNS:
        for py in (REPO / "runtime").rglob("*.py"):
            if pat.search(py.read_text(encoding="utf-8")):
                blockers.append(f"G2: vendor hard dependency in {py.relative_to(REPO)}")
                ok = False

    for root in (REPO / "core", REPO / "registry", REPO / "runtime"):
        for path in root.rglob("*"):
            if path.suffix not in (".md", ".yaml", ".yml", ".py"):
                continue
            if MANDATORY_AESTHETIC.search(path.read_text(encoding="utf-8", errors="ignore")):
                blockers.append(f"G2: mandatory aesthetic in {path.relative_to(REPO)}")
                ok = False

    entries.append(_entry(
        "G2-routing-ownership", "semantic", "Phase F owns routing; adapters consume",
        "STATIC_INSPECTION", "certify_foundation.py", "schema + policy inspection", "PASS" if ok else "FAIL",
    ))
    return ok


def g3_runtime_evidence(
    entries: list[dict],
    blockers: list[str],
    restrictions: list[str],
) -> bool:
    ok = True

    runtime_tests = run_unittest("validation.tests.runtime.test_scenarios")
    entries.append(_entry(
        "G3-runtime-tests", "runtime_evidence", "Phase F runtime scenario tests pass",
        "UNIT_TEST", "unittest", f"python -m unittest {runtime_tests['module']}",
        "PASS" if runtime_tests["passed"] else "FAIL",
    ))
    if not runtime_tests["passed"]:
        blockers.append("G3: runtime scenario tests failed")
        ok = False

    cert_tests = run_unittest("validation.tests.certification.test_certification_framework")
    entries.append(_entry(
        "G3-cert-tests", "runtime_evidence", "Phase G certification framework tests pass",
        "UNIT_TEST", "unittest", f"python -m unittest {cert_tests['module']}",
        "PASS" if cert_tests["passed"] else "FAIL",
    ))
    if not cert_tests["passed"]:
        blockers.append("G3: certification framework tests failed")
        ok = False

    smoke = run_smoke()
    entries.append(_entry(
        "G3-smoke", "runtime_evidence", "Runtime smoke probe passes",
        "SMOKE_TEST", "runtime/smoke.py", "python runtime/smoke.py",
        "PASS" if smoke["exit_code"] == 0 else "FAIL",
    ))
    if smoke["exit_code"] != 0:
        blockers.append("G3: smoke probe failed")
        ok = False

    for script in TOOL_HEALTH_CHECKS:
        result = run_script(script)
        status = "PASS" if result["exit_code"] == 0 else "FAIL"
        entries.append(_entry(
            f"G3-tool-{script}", "runtime_evidence", f"Tool health check {script}",
            "LOCAL_RUNTIME_PROBE", script, f"python validation/{script}", status,
            limitations="Environment-dependent; RESTRICTED is truthful not failure",
        ))
        if result["exit_code"] != 0 and script != "check_blender_tool.py":
            blockers.append(f"G3: {script} failed")
            ok = False
        if script == "check_blender_tool.py":
            try:
                payload = json.loads(result["stdout"].splitlines()[-1] if result["stdout"] else "{}")
            except json.JSONDecodeError:
                payload = {}
            runtime_status = payload.get("runtime", "UNKNOWN")
            if payload.get("protocol_handshake_verified"):
                blockers.append("G3: Blender falsely claims protocol handshake verified")
                ok = False
            if runtime_status == "RESTRICTED":
                restrictions.append(
                    "Blender MCP: RESTRICTED — TCP reachability ≠ MCP protocol handshake"
                )

    return ok


def g4_adversarial(entries: list[dict], blockers: list[str]) -> bool:
    result = run_script("validate_foundation_adversarial.py")
    passed = result["exit_code"] == 0
    entries.append(_entry(
        "G4-adversarial", "adversarial", "G-A01..G-A20 adversarial scenarios pass",
        "INTEGRATION_TEST", "validate_foundation_adversarial.py",
        "python validation/validate_foundation_adversarial.py",
        "PASS" if passed else "FAIL",
    ))
    if not passed:
        blockers.append("G4: adversarial certification failed")
    return passed


def run_orchestrated_validators(entries: list[dict], blockers: list[str]) -> bool:
    ok = True
    for script in ORCHESTRATED_VALIDATORS:
        result = run_script(script)
        passed = result["exit_code"] == 0
        layer = "adversarial" if "adversarial" in script else "runtime_evidence"
        entries.append(_entry(
            f"validator-{script}", layer, f"Existing validator {script} passes",
            "DETERMINISTIC_VALIDATOR", script, f"python validation/{script}",
            "PASS" if passed else "FAIL",
        ))
        if not passed:
            blockers.append(f"Validator failed: {script}")
            ok = False
    return ok


def collect_known_restrictions() -> list[str]:
    restrictions = [
        "EXT-FE-01: LICENSE_REVIEW_REQUIRED — commercial redistribution blocked pending review",
        "EXT-FE-02: LICENSE_REVIEW_REQUIRED — commercial redistribution blocked pending review",
        "EXT-IMG3D-01: operationally restricted (procedural_browser path only)",
        "Blender: TCP reachability ≠ MCP protocol handshake verification",
    ]
    return restrictions


def write_manifest(payload: dict[str, Any]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_certification_result(payload: dict[str, Any]) -> None:
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_certification(*, emit_result: bool = False, tested_sha: str | None = None) -> dict[str, Any]:
    if yaml is None:
        print("PyYAML required", file=sys.stderr)
        sys.exit(1)

    entries: list[dict] = []
    blockers: list[str] = []
    restrictions = collect_known_restrictions()

    implementation_sha = tested_sha or git_sha()

    g1 = g1_structural(entries, blockers)
    g2 = g2_semantic(entries, blockers)
    validators_ok = run_orchestrated_validators(entries, blockers)
    g3 = g3_runtime_evidence(entries, blockers, restrictions)
    g4 = g4_adversarial(entries, blockers)

    layers = {
        "structural": "PASS" if g1 and not any(b.startswith("G1:") for b in blockers) else "FAIL",
        "semantic": "PASS" if g2 and not any(b.startswith("G2:") for b in blockers) else "FAIL",
        "runtime_evidence": "PASS" if g3 and validators_ok else "FAIL",
        "adversarial": "PASS" if g4 else "FAIL",
    }

    all_pass = all(v == "PASS" for v in layers.values()) and not blockers
    status = "CERTIFIED" if all_pass else "NOT_CERTIFIED"

    manifest = {
        "phase": "G",
        "generated_at": _now(),
        "implementation_sha": implementation_sha,
        "status": status,
        "layers": layers,
        "blockers": blockers,
        "restrictions": restrictions,
        "entries": entries,
        "evidence_index": "validation/FOUNDATION_EVIDENCE_INDEX.yaml",
    }
    write_manifest(manifest)

    result_payload = {
        "phase": "G",
        "status": status,
        "layers": layers,
        "blockers": blockers,
        "restrictions": restrictions,
        "evidence_index": "validation/FOUNDATION_EVIDENCE_INDEX.yaml",
        "manifest": str(MANIFEST_PATH.relative_to(REPO)),
        "baseline_sha": "0fb45835c4d6b694fde28591ca12899630c7a1d4",
        "tested_implementation_sha": implementation_sha,
        "certified_sha": implementation_sha if all_pass else None,
        "attestation_sha": git_sha() if emit_result else None,
        "generated_at": _now(),
    }

    if emit_result and all_pass:
        write_certification_result(result_payload)

    return {
        "manifest": manifest,
        "result": result_payload,
        "all_pass": all_pass,
        "entries_count": len(entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ACOS Phase G foundation certification")
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="Write FOUNDATION_CERTIFICATION_RESULT.json (attestation commit only)",
    )
    parser.add_argument(
        "--tested-sha",
        help="Implementation SHA that was tested (for attestation provenance)",
    )
    args = parser.parse_args()

    outcome = run_certification(emit_result=args.write_result, tested_sha=args.tested_sha)
    manifest = outcome["manifest"]

    print(json.dumps({
        "phase": "G",
        "status": manifest["status"],
        "layers": manifest["layers"],
        "blockers": manifest["blockers"],
        "restrictions": manifest["restrictions"],
        "implementation_sha": manifest["implementation_sha"],
        "entries": outcome["entries_count"],
    }, indent=2))

    if outcome["all_pass"]:
        print("\nPhase G certification PASSED — all layers green")
        if args.write_result:
            print(f"Result written: {RESULT_PATH.relative_to(REPO)}")
        return 0

    print("\nPhase G certification FAILED", file=sys.stderr)
    for blocker in manifest["blockers"]:
        print(f"  - {blocker}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
