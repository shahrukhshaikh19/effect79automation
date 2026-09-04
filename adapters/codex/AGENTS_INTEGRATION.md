# Codex Adapter — AGENTS.md Integration

Root `AGENTS.md` is **canonical shared** implementation-agent instructions.

## Rules

- Codex reads `AGENTS.md` — does not own it
- Do not rewrite `AGENTS.md` with Codex-only precedence or vendor lock-in
- Codex-specific bootstrap lives in `adapters/codex/BOOTSTRAP.md`
- If Codex CLI expects local `AGENTS.md`, it uses the repository root file unchanged

## Precedence

Host Codex system instructions apply at platform level.  
ACOS logical precedence: `registry/ADAPTERS.yaml` → `shared_contract.instruction_precedence`.

## When AGENTS.md and adapter differ

`AGENTS.md` and canonical master win over `adapters/codex/*`.
