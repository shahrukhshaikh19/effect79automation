# ACOS v1.2 — Generic Local/Open-Source LLM Bootstrap

**Adapter ID:** ADAPTER-LOCAL-01  
**Contract:** `registry/ADAPTERS.yaml`

Use when the host does not natively discover canonical ACOS Agent Skills.

## Bootstrap instruction

You are operating under ACOS v1.2.

1. Read `ACOS_FINAL_CANONICAL_v1.2.md`.
2. Read `AGENTS.md`.
3. Read relevant `core/*` policies for the task.
4. Read `registry/SKILLS.yaml`.
5. Classify the current task.
6. Select only relevant **approved** skills via registry — do not shortlist new foundation skills.
7. Load selected `SKILL.md` files (L2) — not all skills.
8. Load references/resources only when needed (L3).
9. Follow ACOS workflow and handoffs.
10. Keep Skill, Tool, Model, Memory and Adapter separate.
11. Do not infer a default project, domain, style or 3D-first workflow.
12. Inspect unknown external scripts before execution.
13. For visual work, require rendered/browser evidence.
14. Apply relevant independent critics and quality gates.
15. Write evidence-based progress reports.
16. Record failures/successes under memory policy without premature global promotion.

## Bounded task packet

When no native skill support exists, compile input per `TASK_PACKET.schema.yaml`.

## Smaller-model operating mode

When capability/context is limited:

- reduce active skill batch size;
- break work into deterministic stages;
- use explicit input/output contracts;
- validate after each stage;
- use scripts for repeatable checks;
- do not compensate by deleting canonical requirements.

The adapter changes execution strategy, not ACOS truth.

## Phase F boundary

See `FALLBACK_BOUNDARY.md` — external orchestration hook only, not Phase F runtime.

## Model registry

`registry/MODELS.yaml` remains empty until benchmark evidence. Do not invent model scores or approval status.
