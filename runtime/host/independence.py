"""Host-verifiable critic context. A CLI boolean is never independence proof."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

CONTEXT_ENVS = ("ACOS_HOST_CONTEXT_ID", "CURSOR_TRACE_ID")


def host_context_identity() -> dict[str, Any]:
    for key in CONTEXT_ENVS:
        value = os.environ.get(key, "").strip()
        if value:
            return {"id": value, "source": key}
    return {"id": None, "source": "unavailable"}


def classify_host_context(producer_id: str | None, critic_id: str | None) -> str:
    if not producer_id or not critic_id:
        return "UNVERIFIED"
    if producer_id == critic_id:
        return "SAME_CONTEXT"
    return "DISTINCT"


def implementation_fingerprint(project_dir: Path) -> str:
    root = project_dir / "implementation"
    digest = hashlib.sha256()
    if not root.is_dir():
        return digest.hexdigest()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(rel)
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()
