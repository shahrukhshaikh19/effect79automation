#!/usr/bin/env python3
"""ACOS Phase D filesystem tool health check — dedicated TOOL-FS-01 runtime probe."""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVIDENCE_ROOT = REPO / "validation" / "evidence"
FS_POLICY = REPO / "tools" / "filesystem" / "filesystem-policy.yaml"
FS_CONTRACT = REPO / "tools" / "filesystem" / "CONTRACT.md"


def _blocked(reason: str, structural: str = "BLOCKED") -> int:
    print(json.dumps({
        "tool": "TOOL-FS-01",
        "structural": structural,
        "runtime": "BLOCKED",
        "reason": reason,
    }))
    return 1 if structural == "BLOCKED" else 0


def _within_evidence_workspace(path: Path) -> bool:
    try:
        path.resolve().relative_to(EVIDENCE_ROOT.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    missing = [
        str(p.relative_to(REPO))
        for p in (FS_POLICY, FS_CONTRACT)
        if not p.is_file()
    ]
    if missing:
        return _blocked(f"Missing filesystem contract files: {missing}")

    if not EVIDENCE_ROOT.is_dir():
        return _blocked("validation/evidence/ workspace root missing", structural="CONFIGURED")

    run_id = uuid.uuid4().hex[:12]
    temp_dir = EVIDENCE_ROOT / f"fs-health-{run_id}"

    if not _within_evidence_workspace(temp_dir):
        return _blocked("Temporary path resolves outside approved evidence workspace")

    operations: list[str] = []

    try:
        temp_dir.mkdir(parents=True, exist_ok=False)
        operations.append("create_directory")

        if not _within_evidence_workspace(temp_dir):
            return _blocked("Workspace boundary check failed after mkdir")

        original = temp_dir / "probe.txt"
        original.write_text("acos-fs-probe-v1", encoding="utf-8")
        operations.append("create_file")

        content = original.read_text(encoding="utf-8")
        if content != "acos-fs-probe-v1":
            return _blocked("Read verification failed")
        operations.append("read_file")

        original.write_text("acos-fs-probe-v1-modified", encoding="utf-8")
        if original.read_text(encoding="utf-8") != "acos-fs-probe-v1-modified":
            return _blocked("Modify verification failed")
        operations.append("modify_file")

        copied = temp_dir / "probe-copy.txt"
        shutil.copy2(original, copied)
        if not copied.is_file() or copied.read_text(encoding="utf-8") != "acos-fs-probe-v1-modified":
            return _blocked("Copy verification failed")
        operations.append("copy_file")

        moved = temp_dir / "probe-moved.txt"
        original.rename(moved)
        if original.exists() or not moved.is_file():
            return _blocked("Move/rename verification failed")
        operations.append("move_file")

        copied.unlink()
        moved.unlink()
        operations.append("delete_files")

        remaining = list(temp_dir.iterdir())
        if remaining:
            return _blocked(f"Cleanup incomplete; artifacts remain: {[p.name for p in remaining]}")

        print(json.dumps({
            "tool": "TOOL-FS-01",
            "structural": "CONFIGURED",
            "runtime": "AVAILABLE",
            "workspace_root": str(REPO),
            "evidence_output_root": "validation/evidence",
            "temp_workspace": str(temp_dir.relative_to(REPO)).replace("\\", "/"),
            "operations_verified": operations,
            "cleanup_confirmed": True,
        }))
        return 0

    except OSError as exc:
        print(json.dumps({
            "tool": "TOOL-FS-01",
            "structural": "CONFIGURED",
            "runtime": "BLOCKED",
            "reason": str(exc),
            "operations_attempted": operations,
        }))
        return 0

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        if temp_dir.exists():
            print(json.dumps({
                "tool": "TOOL-FS-01",
                "structural": "CONFIGURED",
                "runtime": "RESTRICTED",
                "reason": "Failed to remove temporary health-check directory",
                "temp_workspace": str(temp_dir.relative_to(REPO)).replace("\\", "/"),
            }), file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
