#!/usr/bin/env python3
"""ACOS v1.2 Phase D production tool layer validator."""

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
PHASE = "D"

VALID_STATUSES = {"configured", "available", "restricted", "blocked", "optional"}
REQUIRED_FAMILIES = {"browser", "blender", "git", "shell", "filesystem"}
TRI_VALUES = {"yes", "no", "unknown"}

REQUIRED_TOOL_FIELDS = (
    "id",
    "name",
    "category",
    "purpose",
    "implementation",
    "status",
    "required",
    "capabilities",
    "evidence_outputs",
    "security_class",
    "network_access",
    "filesystem_access",
    "subprocess_access",
    "destructive_operations",
    "human_approval_required_for",
    "health_check",
    "version_or_pin",
    "configuration_source",
    "notes",
)

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
]

BROWSER_REQUIRED = [
    "tools/browser/package.json",
    "tools/browser/schemas/browser-evidence.schema.yaml",
    "tools/browser/scripts/capture-evidence.mjs",
    "tools/browser/fixtures/blank.html",
]

BLENDER_REQUIRED = [
    "tools/blender-mcp/UPSTREAM.yaml",
    "tools/blender-mcp/capabilities.yaml",
    "tools/blender-mcp/destructive-action-policy.yaml",
    "tools/blender-mcp/security-review.yaml",
    "tools/blender-mcp/schemas/blender-evidence.schema.yaml",
]

GIT_REQUIRED = ["tools/git/CONTRACT.md", "tools/git/git-policy.yaml"]
SHELL_REQUIRED = ["tools/shell/CONTRACT.md", "tools/shell/shell-policy.yaml"]
FS_REQUIRED = ["tools/filesystem/CONTRACT.md", "tools/filesystem/filesystem-policy.yaml"]

SECURITY_EXECUTABLES = [
    "tools/browser/scripts/bootstrap.mjs",
    "tools/browser/scripts/capture-evidence.mjs",
    "tools/browser/scripts/health-check.mjs",
    "validation/check_browser_tool.py",
    "validation/check_blender_tool.py",
    "validation/check_git_tool.py",
    "validation/check_shell_tool.py",
    "validation/validate_tools.py",
]

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_yaml(path: Path, errors: list[str]) -> dict | list | None:
    if yaml is None:
        fail(errors, "PyYAML required")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"Failed to parse {path.relative_to(REPO)}: {exc}")
        return None
    return data


def validate_tools_registry(errors: list[str]) -> None:
    path = REPO / "registry" / "TOOLS.yaml"
    if not path.is_file():
        fail(errors, "Missing registry/TOOLS.yaml")
        return
    data = load_yaml(path, errors)
    if not isinstance(data, dict):
        return

    families = set(data.get("capability_families", []))
    if families != REQUIRED_FAMILIES:
        fail(errors, f"capability_families must be exactly {sorted(REQUIRED_FAMILIES)}: got {sorted(families)}")

    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        fail(errors, "TOOLS.yaml missing tools list")
        return

    ids: set[str] = set()
    cats: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            fail(errors, "Tool entry is not a mapping")
            continue
        tid = tool.get("id")
        if tid in ids:
            fail(errors, f"Duplicate tool id: {tid}")
        ids.add(tid)
        for field in REQUIRED_TOOL_FIELDS:
            if field not in tool:
                fail(errors, f"{tid}: missing field {field}")
        status = tool.get("status")
        if status not in VALID_STATUSES:
            fail(errors, f"{tid}: invalid status {status}")
        cat = tool.get("category")
        cats.add(cat)
        cfg = tool.get("configuration_source")
        if cfg and not (REPO / str(cfg)).exists():
            fail(errors, f"{tid}: configuration_source missing: {cfg}")
        hc = tool.get("health_check")
        if hc and not (REPO / str(hc)).is_file():
            fail(errors, f"{tid}: health_check missing: {hc}")

    if cats != REQUIRED_FAMILIES:
        fail(errors, f"Tool categories must cover families: missing {REQUIRED_FAMILIES - cats}")


def validate_tool_security(errors: list[str]) -> None:
    path = REPO / "registry" / "TOOL_SECURITY.yaml"
    if not path.is_file():
        fail(errors, "Missing registry/TOOL_SECURITY.yaml")
        return
    data = load_yaml(path, errors)
    if not isinstance(data, dict):
        return
    records = data.get("records")
    if not isinstance(records, list):
        fail(errors, "TOOL_SECURITY.yaml missing records list")
        return

    paths: list[str] = []
    for rec in records:
        if not isinstance(rec, dict):
            fail(errors, "Security record is not a mapping")
            continue
        p = rec.get("path_or_tool")
        if not p:
            fail(errors, "Security record missing path_or_tool")
            continue
        paths.append(p)
        for tri in (
            "filesystem_access",
            "network_access",
            "subprocess_execution",
            "shell_execution",
            "package_install_behavior",
            "environment_variable_access",
            "destructive_write_delete_behavior",
            "credential_access",
        ):
            val = rec.get(tri)
            if val is not None and val not in TRI_VALUES:
                fail(errors, f"{p}: {tri} must be yes/no/unknown")

    if len(paths) != len(set(paths)):
        fail(errors, "Duplicate security inventory paths")

    for rel in SECURITY_EXECUTABLES:
        if rel not in paths:
            fail(errors, f"Security inventory missing executable: {rel}")
        if not (REPO / rel).is_file():
            fail(errors, f"Security inventory path missing on disk: {rel}")


def validate_browser_layer(errors: list[str]) -> None:
    for rel in BROWSER_REQUIRED:
        if not (REPO / rel).is_file():
            fail(errors, f"Browser layer missing: {rel}")
    pkg = (REPO / "tools/browser/package.json").read_text(encoding="utf-8")
    if '"playwright": "1.49.1"' not in pkg:
        fail(errors, "Playwright must be pinned to 1.49.1 in tools/browser/package.json")
    if "latest" in pkg.lower():
        fail(errors, "Browser package.json must not reference latest")


def validate_blender_layer(errors: list[str]) -> None:
    for rel in BLENDER_REQUIRED:
        if not (REPO / rel).is_file():
            fail(errors, f"Blender MCP layer missing: {rel}")
    upstream = load_yaml(REPO / "tools/blender-mcp/UPSTREAM.yaml", errors)
    if isinstance(upstream, dict):
        sha = upstream.get("upstream", {}).get("commit_sha", "")
        if not SHA_RE.fullmatch(str(sha)):
            fail(errors, f"Blender upstream commit SHA invalid: {sha}")


def validate_git_shell_fs(errors: list[str]) -> None:
    for group, files in (
        ("git", GIT_REQUIRED),
        ("shell", SHELL_REQUIRED),
        ("filesystem", FS_REQUIRED),
    ):
        for rel in files:
            if not (REPO / rel).is_file():
                fail(errors, f"{group} contract missing: {rel}")

    git_policy = load_yaml(REPO / "tools/git/git-policy.yaml", errors)
    if isinstance(git_policy, dict):
        destructive = git_policy.get("operation_classes", {}).get("destructive", {})
        if destructive.get("normalized_as_ordinary") is not False:
            fail(errors, "Git destructive operations must not be normalized as ordinary")

    shell_policy = load_yaml(REPO / "tools/shell/shell-policy.yaml", errors)
    if isinstance(shell_policy, dict):
        if shell_policy.get("arbitrary_execution_default") is not False:
            fail(errors, "Shell arbitrary_execution_default must be false")


def check_phase_boundaries(errors: list[str]) -> None:
    for name in ("benchmarks", "projects"):
        base = REPO / name
        for item in base.rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file() and item.stat().st_size > 0:
                fail(errors, f"{name}/ must remain empty: {item.relative_to(REPO)}")

    adapter_files = []
    for adapter in ("claude", "cursor", "codex"):
        ad = REPO / "adapters" / adapter
        if ad.is_dir():
            for f in ad.iterdir():
                if f.name != ".gitkeep" and f.is_file():
                    adapter_files.append(str(f.relative_to(REPO)))
    if adapter_files:
        fail(errors, f"Phase E adapter contamination: {adapter_files}")

    forbidden = [REPO / "CLAUDE.md", REPO / ".cursor" / "rules"]
    for p in forbidden:
        if p.exists():
            fail(errors, f"Phase E contamination: {p.relative_to(REPO)}")


def scan_obvious_secrets(errors: list[str]) -> None:
    scan_roots = [REPO / "tools", REPO / "registry"]
    for root in scan_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in {".png", ".jpg", ".lock"}:
                continue
            if "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for pat in SECRET_PATTERNS:
                if pat.search(text):
                    fail(errors, f"Possible secret pattern in {path.relative_to(REPO)}")


def run_regression(errors: list[str]) -> None:
    for script in (
        "validate_foundation.py",
        "validate_external_skills.py",
        "validate_proprietary_skills.py",
    ):
        path = REPO / "validation" / script
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        if result.returncode != 0:
            fail(errors, f"Regression failed: {script}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)


def main() -> int:
    errors: list[str] = []
    print(f"ACOS v1.2 Phase {PHASE} Tools Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    if not (REPO / "validation" / "evidence").is_dir():
        fail(errors, "Missing validation/evidence/ output root")

    validate_tools_registry(errors)
    validate_tool_security(errors)
    validate_browser_layer(errors)
    validate_blender_layer(errors)
    validate_git_shell_fs(errors)
    check_phase_boundaries(errors)
    scan_obvious_secrets(errors)
    run_regression(errors)

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print("Phase D structural tool layer checks complete.")
    print("Runtime health: run validation/check_*_tool.py separately.")
    print("Phase E+ (adapters/orchestration): NOT VALIDATED (not started)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
