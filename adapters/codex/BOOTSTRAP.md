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
5. Tools: `TOOL_MAPPING.yaml`

## Codex is one consumer

Rewriting `AGENTS.md` into Codex-only language is forbidden.  
Codex-specific notes belong in `adapters/codex/` only.

## Tool execution boundaries

Follow `registry/TOOL_SECURITY.yaml`. No permission escalation via adapter.

## Evidence / handoff

Same ACOS evidence rules as other platforms. Adapter does not approve quality gates.

## Phase F boundary

No routing engine, memory runtime, or benchmark runner in this adapter.
