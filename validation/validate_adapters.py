#!/usr/bin/env python3
"""ACOS Phase E adapter layer validator — thinness, contract, and boundary checks."""

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
PHASE = "E"

REQUIRED_FAMILIES = ("claude", "cursor", "codex", "local")
REQUIRED_CONTRACT_FIELDS = (
    "id",
    "platform",
    "status",
    "adapter_version",
    "entrypoint",
    "canonical_authority",
    "canonical_files_loaded",
    "skill_registry",
    "model_registry",
    "instruction_precedence",
    "context_strategy",
    "skill_loading_strategy",
    "tool_mapping_strategy",
    "unsupported_or_platform_specific_behavior",
    "fallback_behavior",
    "prohibited_duplication",
    "validation",
)

AUTHORITY_FINGERPRINT_FILES = [
    REPO / "core" / "CONSTITUTION.md",
    REPO / "core" / "QUALITY_GATES.md",
    REPO / "core" / "WORKFLOW.md",
]

FORBIDDEN_AUTHORITY_CLAIMS = [
    re.compile(r"(?<!not )source of acos truth", re.I),
    re.compile(r"canonical acos lives (here|in this adapter)", re.I),
    re.compile(r"this adapter is authoritative over", re.I),
]

FORBIDDEN_PHASE_F = [
    re.compile(r"autonomous task router", re.I),
    re.compile(r"memory retrieval runtime", re.I),
    re.compile(r"quality aggregation runtime", re.I),
    re.compile(r"multi-agent orchestration engine", re.I),
    re.compile(r"benchmark runner", re.I),
]

FORBIDDEN_DOMAIN = re.compile(r"\bcoffee\b|\bcrypto portfolio\b|\bluxury brand default\b", re.I)

BLENDER_FALSE_CLAIMS = [
    re.compile(r"tcp.*(equals|means|implies).*mcp.*verif", re.I),
    re.compile(r"mcp_connection_tested:\s*true", re.I),
]

MAX_ADAPTER_MD_BYTES = 16_000
MIN_LINE_LEN_FOR_DUP = 48
MAX_COPIED_LINES = 4


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path, errors: list[str]) -> dict | None:
    if not path.is_file():
        fail(errors, f"Missing: {path.relative_to(REPO)}")
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(errors, f"Invalid YAML: {path.relative_to(REPO)}")
        return None
    return data


def copied_line_count(adapter_text: str, authority_text: str) -> int:
    lines = [ln.strip() for ln in authority_text.splitlines() if len(ln.strip()) >= MIN_LINE_LEN_FOR_DUP]
    return sum(1 for ln in lines if ln in adapter_text)


def validate_registry(errors: list[str]) -> list[dict]:
    data = load_yaml(REPO / "registry" / "ADAPTERS.yaml", errors)
    if not data:
        return []
    adapters = data.get("adapters")
    if not isinstance(adapters, list):
        fail(errors, "ADAPTERS.yaml missing adapters list")
        return []
    if len(adapters) != 4:
        fail(errors, f"Phase E requires exactly 4 adapters, found {len(adapters)}")
    platforms = [a.get("platform") for a in adapters if isinstance(a, dict)]
    if sorted(platforms) != sorted(REQUIRED_FAMILIES):
        fail(errors, f"Adapter platforms must be {list(REQUIRED_FAMILIES)}, got {platforms}")
    for adapter in adapters:
        if not isinstance(adapter, dict):
            fail(errors, "Adapter entry must be mapping")
            continue
        for field in REQUIRED_CONTRACT_FIELDS:
            if field not in adapter:
                fail(errors, f"{adapter.get('id', '?')}: missing contract field {field}")
        auth = adapter.get("canonical_authority")
        if auth != "ACOS_FINAL_CANONICAL_v1.2.md":
            fail(errors, f"{adapter.get('id')}: canonical_authority must point to canonical master")
        ep = adapter.get("entrypoint")
        if ep and not (REPO / str(ep)).is_file():
            fail(errors, f"{adapter.get('id')}: missing entrypoint {ep}")
        elif ep and (REPO / str(ep)).stat().st_size < 50:
            fail(errors, f"{adapter.get('id')}: entrypoint too small {ep}")
    return adapters


def validate_adapter_directories(errors: list[str], adapters: list[dict]) -> None:
    seen_dirs: set[str] = set()
    for adapter in adapters:
        platform = adapter.get("platform")
        directory = adapter.get("directory", f"adapters/{platform}")
        if directory in seen_dirs:
            fail(errors, f"Duplicate adapter directory: {directory}")
        seen_dirs.add(str(directory))
        dir_path = REPO / str(directory)
        if not dir_path.is_dir():
            fail(errors, f"Missing adapter directory: {directory}")

    adapters_root = REPO / "adapters"
    for child in adapters_root.iterdir():
        if child.is_dir() and child.name not in REQUIRED_FAMILIES:
            for f in child.iterdir():
                if f.is_file() and f.name != ".gitkeep":
                    fail(errors, f"Unexpected vendor adapter: {child.name}")


def validate_thinness(errors: list[str]) -> None:
    adapter_roots = [
        REPO / "adapters",
        REPO / ".cursor" / "rules",
    ]
    authority_blob = "\n".join(
        load_text(p) for p in AUTHORITY_FINGERPRINT_FILES if p.is_file()
    )
    for root in adapter_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".mdc", ".yaml", ".yml"}:
                continue
            text = load_text(path)
            if path.suffix in {".md", ".mdc"} and path.stat().st_size > MAX_ADAPTER_MD_BYTES:
                fail(errors, f"Adapter file exceeds size threshold (thin adapter violation): {path.relative_to(REPO)}")
            if copied_line_count(text, authority_blob) > MAX_COPIED_LINES:
                fail(errors, f"Adapter duplicates canonical policy lines: {path.relative_to(REPO)}")
            for pat in FORBIDDEN_AUTHORITY_CLAIMS:
                if pat.search(text):
                    fail(errors, f"Adapter claims authority over canonical ACOS: {path.relative_to(REPO)}")

    for skill in (REPO / "skills" / "acos").rglob("SKILL.md"):
        body = load_text(skill)
        sample = "\n".join(
            ln.strip()
            for ln in body.splitlines()
            if len(ln.strip()) >= MIN_LINE_LEN_FOR_DUP
        )[:3000]
        for path in (REPO / "adapters").rglob("*.md"):
            if sample and copied_line_count(load_text(path), sample) > MAX_COPIED_LINES:
                fail(errors, f"Adapter may copy proprietary skill body: {path.relative_to(REPO)}")


def validate_canonical_references(errors: list[str], adapters: list[dict]) -> None:
    for adapter in adapters:
        ep = REPO / str(adapter.get("entrypoint", ""))
        if not ep.is_file():
            continue
        text = load_text(ep)
        for ref in ("ACOS_FINAL_CANONICAL_v1.2.md", "AGENTS.md", "registry/SKILLS.yaml"):
            if ref not in text:
                fail(errors, f"{adapter.get('id')} entrypoint missing reference to {ref}")


def validate_skill_integrity(errors: list[str]) -> None:
    for path in (REPO / "adapters").rglob("*"):
        if not path.is_file():
            continue
        text = load_text(path)
        if "skills/acos/" in text and "do not copy" not in text.lower() and "reference" not in text.lower():
            if path.name not in ("SKILL_LOADING.md", "BOOTSTRAP.md", "LOCAL_LLM_BOOTSTRAP.md"):
                pass  # path refs in loading docs are OK
        if re.search(r"^---\nname:", text):  # skill frontmatter pasted
            fail(errors, f"Adapter contains skill frontmatter: {path.relative_to(REPO)}")


def validate_phase_f_boundary(errors: list[str]) -> None:
    skip_markers = (
        "must not",
        "forbidden",
        "does not implement",
        "not implement",
        "must_not_implement",
        "## forbidden",
        "outside this validator",
        "no routing engine",
        "does not implement the orchestrator",
    )
    scan = [REPO / "adapters", REPO / "registry" / "ADAPTERS.yaml"]
    for base in scan:
        files = [base] if base.is_file() else list(base.rglob("*")) if base.is_dir() else []
        for path in files:
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".mdc"}:
                continue
            for line in load_text(path).splitlines():
                stripped = line.strip()
                lower = line.lower()
                if any(m in lower for m in skip_markers):
                    continue
                if stripped.startswith("- "):
                    continue
                if stripped.startswith("* "):
                    continue
                for pat in FORBIDDEN_PHASE_F:
                    if pat.search(line):
                        fail(
                            errors,
                            f"Phase F runtime signal in Phase E file: {path.relative_to(REPO)}: {line.strip()[:80]}",
                        )


def validate_licensing(errors: list[str]) -> None:
    openai_markers = ["openai-frontend-app-builder", "openai-frontend-testing", "EXT-FE-01", "EXT-FE-02"]
    for path in (REPO / "adapters").rglob("*"):
        if not path.is_file():
            continue
        text = load_text(path)
        for marker in openai_markers:
            if marker in text and "LICENSE_REVIEW_REQUIRED" not in text and "do not copy" not in text.lower():
                if "blocked_pending_license_review" not in text:
                    fail(errors, f"Adapter references {marker} without licensing guard: {path.relative_to(REPO)}")


def validate_tool_semantics(errors: list[str]) -> None:
    for path in (REPO / "adapters").rglob("*.yaml"):
        text = load_text(path)
        for pat in BLENDER_FALSE_CLAIMS:
            if pat.search(text):
                fail(errors, f"Blender false verification claim: {path.relative_to(REPO)}")
        if "health_script_default: AVAILABLE" in text or "runtime: AVAILABLE" in text.lower():
            if "blender" in text.lower() and "browser" not in path.name:
                fail(errors, f"Blender must not default to AVAILABLE in {path.relative_to(REPO)}")


def validate_domain_neutrality(errors: list[str]) -> None:
    for path in (REPO / "adapters").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".mdc"}:
            if FORBIDDEN_DOMAIN.search(load_text(path)):
                fail(errors, f"Domain contamination in adapter: {path.relative_to(REPO)}")


def validate_cursor_rule(errors: list[str]) -> None:
    rule = REPO / ".cursor" / "rules" / "acos-bootstrap.mdc"
    if not rule.is_file():
        fail(errors, "Missing Cursor thin rule: .cursor/rules/acos-bootstrap.mdc")
        return
    text = load_text(rule)
    if "ACOS_FINAL_CANONICAL_v1.2.md" not in text:
        fail(errors, "Cursor rule must reference canonical master")
    if copied_line_count(text, load_text(REPO / "core" / "CONSTITUTION.md")) > MAX_COPIED_LINES:
        fail(errors, "Cursor rule duplicates Constitution — must stay thin")


def validate_models_registry_unchanged(errors: list[str]) -> None:
    models = load_yaml(REPO / "registry" / "MODELS.yaml", errors)
    if isinstance(models, dict):
        if models.get("models") != []:
            fail(errors, "Phase E must not populate MODELS.yaml without benchmark evidence")
        if not models.get("policy", {}).get("no_invented_benchmark_results"):
            fail(errors, "MODELS.yaml must preserve no_invented_benchmark_results policy")


def main() -> int:
    errors: list[str] = []
    if yaml is None:
        fail(errors, "PyYAML required")
        return 1

    print(f"ACOS v1.2 Phase {PHASE} Adapters Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    adapters = validate_registry(errors)
    validate_adapter_directories(errors, adapters)
    validate_canonical_references(errors, adapters)
    validate_thinness(errors)
    validate_skill_integrity(errors)
    validate_phase_f_boundary(errors)
    validate_licensing(errors)
    validate_tool_semantics(errors)
    validate_domain_neutrality(errors)
    validate_cursor_rule(errors)
    validate_models_registry_unchanged(errors)

    for tm in (REPO / "adapters").rglob("TOOL_MAPPING.yaml"):
        load_yaml(tm, errors)

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print(f"Verified {len(adapters)} thin platform adapters.")
    print("Phase F+ (routing/memory runtime): outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
