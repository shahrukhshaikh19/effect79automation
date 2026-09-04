# ACOS v1.2 — Generic Local/Open-Source LLM Bootstrap

**Adapter ID:** ADAPTER-LOCAL-01  
**Contract:** `registry/ADAPTERS.yaml`

Use when the host does not natively discover canonical ACOS Agent Skills.

**Routing ownership:** This adapter **consumes** routing output. It does **not** own task classification or skill activation (Phase F).

## Bootstrap instruction

You are operating under ACOS v1.2.

1. Read `ACOS_FINAL_CANONICAL_v1.2.md`.
2. Read `AGENTS.md`.
3. Read relevant `core/*` policies referenced by the task packet.
4. **Receive a bounded task packet** from the caller (`TASK_PACKET.schema.yaml`).
5. **Use only `routing.activated_skill_ids` supplied by the caller / future Phase F routing layer.**
6. Validate every supplied skill ID exists in `registry/SKILLS.yaml` and is permitted under current ACOS restrictions (including license/restriction flags).
7. Load **only** those activated skills at L2; load L3 references/scripts on demand.
8. Follow ACOS workflow and handoffs for loaded skills.
9. Keep Skill, Tool, Model, Memory and Adapter separate.
10. Do not infer a default project, domain, style or 3D-first workflow.
11. Inspect unknown external scripts before execution.
12. For visual work, require rendered/browser evidence.
13. Apply relevant independent critics and quality gates per loaded skill scope.
14. Write evidence-based progress reports.
15. Record failures/successes under memory policy without premature global promotion.

## If routing input is missing

If `activated_skill_ids` are absent for a task that requires routing:

- **Do not classify the task.**
- **Do not select or invent skills.**
- Emit **`routing_required`** or **`insufficient_routing_input`** and stop.

## Manual caller fallback (pre–Phase F)

Before Phase F exists, an **authorized external caller** may manually supply:

- normalized scope
- `activated_skill_ids`
- allowed tool families / runtime status
- output contract

The adapter validates and loads — it does **not** substitute autonomous routing.

## Smaller-model operating mode

When capability/context is limited:

- reduce active skill batch size (within supplied IDs only);
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
