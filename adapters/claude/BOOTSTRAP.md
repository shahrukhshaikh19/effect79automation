# ACOS Phase E — Claude Adapter Bootstrap

**Adapter ID:** ADAPTER-CLAUDE-01  
**Contract:** `registry/ADAPTERS.yaml`  
**Authority:** Claude consumes ACOS — canonical intelligence remains outside this adapter.

## Entrypoint behavior

1. Read `ACOS_FINAL_CANONICAL_v1.2.md` first.
2. Read shared `AGENTS.md` (canonical, not Claude-owned).
3. Load relevant `core/*` policies per task scope.
4. Discover skills via `registry/SKILLS.yaml` — do not hard-code skill lists in this file.
5. Native Claude Code skills are linked from `.claude/skills/` — regenerate with `tools/skill_exposure/sync_native_skills.py` if missing.
6. Product requests: `python tools/host_driver/run_stage.py init --prompt "<request>" --target claude` then follow the brief, `advance`, and `capture` on EVIDENCE. Loop: `tools/host_driver/HOST_LOOP.md`.
7. If `runtime/host/CURRENT_HOST_BRIEF.md` exists, invoke only listed skills. Do not select from the full catalog.
8. Apply progressive loading per `SKILL_LOADING.md`.
9. Map tools per `TOOL_MAPPING.yaml` with truthful runtime status.

## ACOS logical authority vs host technical hierarchy

**Host technical hierarchy always applies.** The Claude adapter does **not** override higher-priority system, developer, platform, safety, or runtime instructions.

Within the freedom permitted by the host environment, ACOS **logical** authority governs ACOS behavior:

```text
canonical ACOS authority
→ activated ACOS skills
→ tool operational contracts
→ adapter compatibility guidance
→ model optimization hints
```

Shared contract: `registry/ADAPTERS.yaml` → `shared_contract.instruction_precedence` and `host_technical_hierarchy`.

If a host-level constraint prevents an ACOS requirement, report the limitation truthfully — do not pretend ACOS overrode the host.

## Agent Skills on Claude

When Claude native Agent Skills are available:

- Level 1: registry metadata / skill descriptions
- Level 2: load `SKILL.md` only for activated skills
- Level 3: references/scripts on demand

Do **not** copy proprietary or external `SKILL.md` bodies into this adapter directory.

## Tool / MCP boundaries

- Canonical families: browser, blender, git, shell, filesystem (`registry/TOOLS.yaml`)
- Host MCP/tool names are mapped in `TOOL_MAPPING.yaml`
- Report AVAILABLE / RESTRICTED / BLOCKED / UNAVAILABLE / UNKNOWN — never invent runtime evidence
- Blender: TCP reachability ≠ MCP protocol verification (see `validation/check_blender_tool.py`)

## Context strategy

See `CONTEXT_STRATEGY.md`. Load minimum bootstrap first; expand only for activated skills.

## Handoff / evidence

- Visual work requires browser/render evidence before critics approve
- Quality gate terminal statuses: APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE
- Adapters route evidence; they do not issue gate verdicts

## Licensing

Do not embed EXT-FE-01 / EXT-FE-02 content — `LICENSE_REVIEW_REQUIRED`, redistribution blocked.

## Phase F boundary

This adapter consumes Phase F routing via `runtime/host/CURRENT_HOST_BRIEF.md` (native skill names + gate lock).  
It does **not** implement routing, memory runtime, or orchestration.
