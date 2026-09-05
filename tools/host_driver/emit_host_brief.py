#!/usr/bin/env python3
"""Write runtime/host/CURRENT_HOST_BRIEF.* from a routing decision (+ optional intake)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.adapter.host_brief import build_host_brief, write_host_brief


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit(f"Expected mapping in {path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--routing", required=True, help="Path to routing_decision.json")
    parser.add_argument("--intake", help="Optional intake JSON/YAML")
    parser.add_argument("--target", default="cursor", choices=["cursor", "claude", "codex", "local"])
    args = parser.parse_args()

    routing = _load(Path(args.routing))
    if args.intake:
        intake = _load(Path(args.intake))
    else:
        intake = {
            "task_id": routing.get("task_id") or "host-brief",
            "deliverables": [],
            "runtime_capabilities": {},
        }
    brief = build_host_brief(intake, routing, adapter_target=args.target)
    paths = write_host_brief(brief)
    print(f"Wrote {paths['md'].relative_to(REPO)}")
    print(f"Wrote {paths['yaml'].relative_to(REPO)}")
    print(f"invoke_now: {[r.get('invoke') for r in brief.get('invoke_now') or []]}")
    print(f"design_gate: {brief.get('design_gate_state')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
