#!/usr/bin/env python3
"""Generate registry/EXTERNAL_SCRIPT_SECURITY.yaml from static inspection."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML required") from exc

REPO = Path(__file__).resolve().parent.parent
IMG2THREEJS = REPO / "skills" / "external" / "img2threejs"
OUT = REPO / "registry" / "EXTERNAL_SCRIPT_SECURITY.yaml"

SCRIPT_EXT = {".py", ".sh", ".ps1", ".js", ".ts", ".mjs", ".bat", ".cmd"}
LANG = {
    ".py": "python",
    ".sh": "shell",
    ".ps1": "powershell",
    ".js": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".bat": "batch",
    ".cmd": "batch",
}

FS_PATTERNS = (
    r"\bopen\s*\(",
    r"\bPath\s*\(",
    r"\bread_text\b",
    r"\bwrite_text\b",
    r"\bshutil\b",
    r"\brmtree\b",
    r"\bunlink\b",
    r"\bremove\s*\(",
    r"\bos\.remove\b",
    r"\bos\.unlink\b",
    r"\bmkdir\b",
    r"\brename\b",
)
NET_PATTERNS = (
    r"\burllib\b",
    r"\brequests\b",
    r"\bhttpx\b",
    r"\bhttp\.client\b",
    r"\bsocket\b",
    r"\bfetch\s*\(",
    r"\bcurl\b",
    r"https?://",
)
SUBPROCESS_PATTERNS = (
    r"\bsubprocess\b",
    r"\bos\.system\b",
    r"\bpopen\b",
    r"\bexecv\b",
    r"\bspawn\b",
)
SHELL_PATTERNS = (r"\bos\.system\b", r"\bsubprocess\.(?:run|call|Popen).*shell\s*=\s*True", r"\b/bin/sh\b", r"\bbash\b")
INSTALL_PATTERNS = (r"\bpip install\b", r"\bnpm install\b", r"\bnpx\b", r"\bapt-get\b", r"\bbrew install\b")
ENV_PATTERNS = (r"\bos\.environ\b", r"\bgetenv\b", r"\bprocess\.env\b")
DESTRUCTIVE_PATTERNS = (r"\brmtree\b", r"\bunlink\b", r"\bos\.remove\b", r"\bshutil\.rmtree\b", r"\bdelete\b")
BINARY_PATTERNS = (
    (r"\bplaywright\b", "playwright/node"),
    (r"\bnode\b", "node"),
    (r"\bpython3?\b", "python"),
    (r"\bblender\b", "blender"),
    (r"\bffmpeg\b", "ffmpeg"),
    (r"\bmagick\b", "imagemagick"),
)


def tri_match(text: str, patterns: tuple[str, ...]) -> str:
    if any(re.search(p, text, re.I) for p in patterns):
        return "yes"
    return "unknown"


def infer_role(rel: str) -> str:
    parts = Path(rel).parts
    if parts[0] == "scripts":
        return "top-level utility script"
    if parts[0] == "forge":
        if "tests" in parts:
            return "upstream test module (not executed by ACOS import review)"
        if len(parts) >= 2 and parts[1].startswith("stage"):
            return f"forge workflow stage: {parts[1]}"
        return "forge shared/workflow module"
    return "unknown"


def infer_risk(text: str, rel: str) -> str:
    flags = []
    if tri_match(text, NET_PATTERNS) == "yes":
        flags.append("network")
    if tri_match(text, SUBPROCESS_PATTERNS) == "yes" or tri_match(text, SHELL_PATTERNS) == "yes":
        flags.append("subprocess")
    if tri_match(text, INSTALL_PATTERNS) == "yes":
        flags.append("install")
    if "tests" in rel:
        return "low-test-module"
    if not flags:
        return "low-static-unknown"
    if "network" in flags and "install" in flags:
        return "elevated-network-install"
    if "network" in flags:
        return "elevated-network"
    if "subprocess" in flags:
        return "elevated-subprocess"
    return "moderate-" + "-".join(flags)


def external_binaries(text: str) -> list[str]:
    found: list[str] = []
    for pattern, name in BINARY_PATTERNS:
        if re.search(pattern, text, re.I):
            if name not in found:
                found.append(name)
    return found or ["none-detected"]


def build_record(path: Path) -> dict:
    rel = path.relative_to(IMG2THREEJS).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    suffix = path.suffix.lower()
    language = LANG.get(suffix, "unknown")
    fs = tri_match(text, FS_PATTERNS)
    net = tri_match(text, NET_PATTERNS)
    subp = tri_match(text, SUBPROCESS_PATTERNS)
    shell = tri_match(text, SHELL_PATTERNS)
    install = tri_match(text, INSTALL_PATTERNS)
    env = tri_match(text, ENV_PATTERNS)
    destructive = tri_match(text, DESTRUCTIVE_PATTERNS)
    return {
        "path": rel,
        "language": language,
        "runtime_role": infer_role(rel),
        "filesystem_access": fs,
        "network_access": net,
        "subprocess_execution": subp,
        "shell_execution": shell,
        "package_install_behavior": install,
        "environment_variable_access": env,
        "destructive_write_delete_behavior": destructive,
        "external_binary_requirements": external_binaries(text),
        "review_status": "static_inspection_not_executed",
        "risk_classification": infer_risk(text, rel),
        "notes": (
            "Static pattern scan only; behavior marked unknown when patterns absent. "
            "Script was not executed during ACOS Phase B hardening."
        ),
    }


def main() -> None:
    scripts = sorted(
        p for p in IMG2THREEJS.rglob("*") if p.is_file() and p.suffix.lower() in SCRIPT_EXT
    )
    records = [build_record(p) for p in scripts]
    payload = {
        "version": "1.2",
        "phase": "B-hardening",
        "authority": "registry/EXTERNAL_SKILLS_LOCK.yaml",
        "source_skill": "EXT-IMG3D-01",
        "source_local_path": "skills/external/img2threejs",
        "generated_date": date.today().isoformat(),
        "review_method": "static_pattern_inspection_only",
        "policy": {
            "scripts_not_executed": True,
            "unknown_when_unproven": True,
        },
        "required_fields": [
            "path",
            "language",
            "runtime_role",
            "filesystem_access",
            "network_access",
            "subprocess_execution",
            "shell_execution",
            "package_install_behavior",
            "environment_variable_access",
            "destructive_write_delete_behavior",
            "external_binary_requirements",
            "review_status",
            "risk_classification",
            "notes",
        ],
        "script_count": len(records),
        "scripts": records,
    }
    OUT.write_text(yaml.dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {len(records)} script records to {OUT}")


if __name__ == "__main__":
    main()
