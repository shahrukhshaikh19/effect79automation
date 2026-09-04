# ACOS Phase E — Claude Adapter Bootstrap

**Adapter ID:** ADAPTER-CLAUDE-01  
**Contract:** `registry/ADAPTERS.yaml`  
**Authority:** Claude consumes ACOS — canonical intelligence remains outside this adapter.

## Entrypoint behavior

1. Read `ACOS_FINAL_CANONICAL_v1.2.md` first.
2. Read shared `AGENTS.md` (canonical, not Claude-owned).
3. Load relevant `core/*` policies per task scope.
4. Discover skills via `registry/SKILLS.yaml` — do not hard-code skill lists in this file.
5. Apply progressive loading per `SKILL_LOADING.md`.
6. Map tools per `TOOL_MAPPING.yaml` with truthful runtime status.

## ACOS logical authority vs host precedence

Claude's system/developer/user message hierarchy is a **host platform** concern.  
ACOS **logical** precedence is defined in `registry/ADAPTERS.yaml` → `shared_contract.instruction_precedence`.  
When host rules conflict with ACOS constitutional policy, ACOS policy wins for ACOS work; host safety/platform rules still apply.

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

This adapter may consume `activated_skill_ids` from a future routing layer.  
It does **not** implement routing, memory runtime, or orchestration.
