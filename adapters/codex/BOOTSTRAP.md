# ACOS Phase E — Codex Adapter Bootstrap

**Adapter ID:** ADAPTER-CODEX-01  
**Contract:** `registry/ADAPTERS.yaml`  
**AGENTS integration:** `AGENTS_INTEGRATION.md`

## Entrypoint

Codex consumes shared root `AGENTS.md` — it does **not** replace or fork it.

1. Read `ACOS_FINAL_CANONICAL_v1.2.md`
2. Read `AGENTS.md` (canonical shared agent instructions)
3. Load task-relevant `core/*`, `registry/SKILLS.yaml`, and `registry/TOOLS.yaml`
4. Progressive skills: `SKILL_LOADING.md`
5. Native Codex skills are linked from `.agents/skills/` — regenerate with `tools/skill_exposure/sync_native_skills.py` if missing.
6. Product requests: `python tools/host_driver/run_stage.py init --prompt "<request>" --target codex` then follow the brief, `advance`, and `capture` on EVIDENCE. Loop: `tools/host_driver/HOST_LOOP.md`.
7. If `runtime/host/CURRENT_HOST_BRIEF.md` exists, invoke only listed skills. Do not select from the full catalog.
8. Tools: `TOOL_MAPPING.yaml`

## Codex is one consumer

Rewriting `AGENTS.md` into Codex-only language is forbidden.  
Codex-specific notes belong in `adapters/codex/` only.

## Tool execution boundaries

Follow `registry/TOOL_SECURITY.yaml`. No permission escalation via adapter.

## Evidence / handoff

Same ACOS evidence rules as other platforms. Adapter does not approve quality gates.

## Phase F boundary

No routing engine, memory runtime, or benchmark runner in this adapter.
