# Host loop (Cursor / Claude / Codex)

One conductor. The user does not pick skills or stages.

## Commands

```text
python tools/host_driver/run_stage.py init --prompt "your project request"
python tools/host_driver/run_stage.py status
python tools/host_driver/run_stage.py check
python tools/host_driver/run_stage.py advance
python tools/host_driver/run_stage.py serve
python tools/host_driver/run_stage.py capture
python tools/host_driver/run_stage.py critic-pass --attest-independent
```

`init --target claude` and `init --target codex` write the same loop for those hosts.

## Host does

1. Read `runtime/host/CURRENT_HOST_BRIEF.md` and `CURRENT_HOST_TODO.md`.
2. Execute only **Invoke now**. Write artifacts under `runtime/host/projects/<task>/`.
3. `advance`. Repeat until SHIP, REJECTED, or a real BLOCKED reason.

Stage order: CREATIVE → Design Gate → PRODUCTION → EVIDENCE → CRITICS → QUALITY_GATE → SHIP

## Hard locks

- Production stays locked until Design Gate **APPROVED**.
- Evidence must be rendered pixels (PNG/WebP), captured over HTTP. `file://` is invalid for ES modules. YAML/scripts are not evidence.
- The producer chat cannot APPROVE. A new chat runs `critic-pass --attest-independent`, inspects pixels, writes critics, then the gate.
- The conductor will override an illegal `APPROVED` to `BLOCKED_INSUFFICIENT_EVIDENCE`.
- BM-runner YAML is not a skill output.
- Authored 3D / Blender-required prompt: `docs/FLAGSHIP_PREMIUM_WORKFLOW.md`. The word “premium” is not required. Blender + craft skills are mandatory. A lathe is not complete. First-frame-only evidence is not complete when the brief names scroll beats.
- If Blender MCP/app is down: tell the user, wait, then `confirm-blender --mcp-live`. Never skip.
