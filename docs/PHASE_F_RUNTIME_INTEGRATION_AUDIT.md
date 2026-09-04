# Phase F — Runtime Integration Audit

**Date:** 2026-09-04  
**Baseline SHA:** `524ceff0d56fa74b450cd19d5a7fe9ad12ea5434`  
**Scope:** Routing + memory + quality integration runtime (Phase F only)

---

## Architecture

Phase F implements a modular reference runtime under `runtime/` — not a monolithic orchestrator.

```text
runtime/
├── schemas/          # Machine-readable contracts (8 schemas)
├── common/           # Registry loader + shared constants
├── intake/           # Normalization + validation
├── routing/          # Canonical owner of activated_skill_ids
├── handoff/          # Handoff build/validate
├── evidence/         # Evidence registration + provenance
├── quality/          # Quality Gate terminal-state evaluation
├── correction/       # Bounded correction requests
├── memory/           # Records, promotion, retrieval, conflicts
├── state/            # Execution state persistence + resume
├── adapter/          # Adapter-ready task packets
└── smoke.py          # Domain-neutral executable smoke flow
```

Policy registries: `registry/ROUTING_POLICY.yaml`, `registry/RUNTIME_POLICY.yaml`.

---

## Routing ownership

- **Phase F owns** `activated_skill_ids` via `runtime/routing/engine.py::route_task()`.
- Phase E adapters **consume** routing output only (`runtime/adapter/packet.py`).
- Adapters must not classify tasks or select skills autonomously (preserved from Phase E corrections).

---

## Intake

- Contract: `runtime/schemas/TASK_INTAKE.schema.yaml`
- Normalization preserves provenance labels (facts vs assumptions vs unknowns).
- Insufficient goal/profile → `ROUTING_BLOCKED_INSUFFICIENT_INPUT`.

---

## Skill activation

- Every activated skill requires an activation record with `activation_reason`.
- Unknown skill IDs rejected by `validate_routing_decision()`.
- License-restricted: EXT-FE-01/02 remain blocked unless `license_review_acknowledged`.
- Operational-restricted: EXT-IMG3D-01 requires `reconstruction_path: procedural_browser`.

---

## Handoffs

- Contract: `runtime/schemas/HANDOFF.schema.yaml`
- `runtime/handoff/validate.py` enforces required fields and forbids claim-only evidence.

---

## Evidence

- Contract: `runtime/schemas/EVIDENCE_REF.schema.yaml`
- Claim ≠ evidence enforced in `runtime/evidence/register.py`.
- Forbidden claim strings: "looks good", "tested", "passed".

---

## Critics

- Independent critics activated by task signals (visual, creative, 3D).
- `runtime/quality/gate.py::validate_producer_independence()` blocks producer self-approval.

---

## Quality Gate

Terminal statuses only: `APPROVED`, `REJECTED`, `BLOCKED_INSUFFICIENT_EVIDENCE`.

Precedence (HR/EB separation preserved):
1. Validate required evidence → EB-01 → BLOCKED if insufficient
2. Evaluate demonstrated defects → HR-01..HR-10 → REJECTED
3. Else APPROVED

HR-11 forbidden. Scores cannot override terminal state.

---

## Correction loop

- Default retry budget: 2 (`registry/RUNTIME_POLICY.yaml`)
- Budget exhausted → `HUMAN_REVIEW_REQUIRED`
- Attempts tracked in execution state.

---

## Memory

- Contract: `runtime/schemas/MEMORY_RECORD.schema.yaml`
- Categories: knowledge, taste, projects, failures, successes, model_compatibility
- Promotion lifecycle: observation → project-rule → candidate-global → validated-global → deprecated
- Prohibited shortcut: observation → validated-global
- Conflicts → `MEMORY_CONFLICT_REQUIRES_RESOLUTION`
- Memory cannot override canonical authority (`memory_overrides_authority()` guard)

---

## Adapter integration

- `runtime/adapter/packet.py` produces packets with `routing.source: phase_f_router`.
- Same semantics for Claude/Cursor/Codex/local adapter targets.

---

## Tool capability handling

- Routing respects `runtime_capabilities` truth states.
- Blender UNAVAILABLE + authored_3d_asset → `ROUTING_BLOCKED_CAPABILITY` (no fake success).
- TCP reachability ≠ MCP protocol verification (preserved from Phase D).

---

## Security

- Untrusted memory text cannot redefine Constitution/Quality Gates/Routing/Tool permissions.
- License restrictions not silently resolved.

---

## Tests

Executable suite: `validation/tests/runtime/test_scenarios.py`

| Scenario | Description |
|---|---|
| T1 | Minimal non-visual — no unnecessary visual/3D/motion |
| T2 | Visual creative — no mandatory 3D |
| T3 | Interactive 3D route with justification |
| T4 | Tool unavailable → block |
| T5 | Unknown skill rejected |
| T6 | License restriction preserved |
| T7 | Missing evidence → BLOCKED |
| T8 | Hard defect → REJECTED |
| T9 | Clean evidence → APPROVED |
| T10 | Producer self-approval forbidden |
| T11 | Retry budget exhausted |
| T12 | Memory promotion shortcut forbidden |
| T13 | Model-specific stays model-specific |
| T14 | Memory conflict represented |
| T15 | Adapter packet from Phase F routing |
| T16 | Resume from persisted state |
| T17 | Memory injection blocked |
| T18 | Domain-neutral fixtures |

Adversarial tests included for HR-11 and claim-only evidence.

---

## Smoke test

`python runtime/smoke.py` executes: intake → routing → handoff → evidence → gate → memory candidate → persist/resume.

Evidence saved under `validation/evidence/runtime/smoke/` (lightweight JSON).

---

## Validator coverage

`validation/validate_runtime_integration.py` checks architecture, routing ownership, HR/EB semantics, memory promotion, phase boundaries, domain neutrality, and runs executable tests.

---

## Phase state

```text
A–F: COMPLETE
G: NOT_STARTED
PF-*: NOT_STARTED
FOUNDATION_READY: undeclared
```

---

## Known restrictions (unchanged)

- EXT-FE-01/02: `LICENSE_REVIEW_REQUIRED`, `blocked_pending_license_review`
- EXT-IMG3D-01: operational restricted
- Blender health: TCP ≠ MCP handshake verification
- `registry/MODELS.yaml`: no invented benchmark results

---

## Unresolved risks

- Reference runtime is file-backed and synthetic — Phase G must validate operational end-to-end behavior.
- Routing policy may require expansion as real benchmarks register post-FOUNDATION_READY.

---

**Claim:** PHASE F IMPLEMENTED + LOCALLY VALIDATED — awaiting independent certification review.

---

## Certification corrections (2026-09-04)

### F-C1 — License enforcement

- Router reads canonical license state from `registry/EXTERNAL_SKILLS_LOCK.yaml` via `is_skill_license_blocked()`.
- `license_review_acknowledged` does **not** override `blocked_pending_license_review`.
- Blocked skills emit `BLOCKED_LICENSE_REVIEW_REQUIRED` with explicit rejection reason.

### F-C2 — Metadata-driven correction routing

- `registry/ROUTING_POLICY.yaml` defines `correction_responsibility` with `owner_domains` and `exclude_roles`.
- `runtime/correction/route.py` resolves owners from policy — no hard-coded ACOS-01 fallback.
- Unknown defects → `CORRECTION_ROUTING_REQUIRES_RESOLUTION`.
- Critics detect defects but are excluded from correction producer role by default.

### F-C3 — Design Gate runtime guard

- `runtime/state/transitions.py::can_transition()` enforces policy `required_before_stages`.
- Routing splits `planned_skill_ids` vs `executable_active_skill_ids` when gate is PENDING.
- PENDING/REJECTED/BLOCKED gates block PRODUCTION/SPECIALIST_ROUTING transitions.

### F-C4 — Memory creation/promotion/conflict semantics

- `create_memory_observation()` — normal creation at `observation` only.
- `promote_memory()` — stateful promotion with evidence and history.
- Structured `subject_key` + `value` conflict model — same value at different promotion levels is NOT a conflict.
- Incompatible values or explicit `conflicts_with` → `MEMORY_CONFLICT_REQUIRES_RESOLUTION`.
- Model-specific scope cannot silently migrate to global.

**Correction claim:** PHASE F CERTIFICATION CORRECTIONS COMPLETE — awaiting independent review.

---

## Design Gate unlock correction (2026-09-04)

### Gate state authority

- `authoritative_design_gate()` — execution-state gate wins over stale `routing_decision.design_gate_state`.
- Historical routing snapshots preserved for provenance only.

### Unlock flow

```text
route_task() → planned_skill_ids + initial active_skill_ids
Design Gate PENDING → gated skills planned but not active
Design Gate APPROVED → unlock_planned_skills() → active_skill_ids refreshed
No rerouting — same routing_id preserved
```

Functions: `bind_routing_to_execution()`, `refresh_executable_activations()`, `unlock_planned_skills()`.

### Adapter packet

- `build_adapter_packet(intake, routing, execution_state=state)` uses current `active_skill_ids`.
- Packet exposes `planned_skill_ids`, current `activated_skill_ids`, and current `design_gate_state`.

**Unlock claim:** PHASE F DESIGN GATE UNLOCK CORRECTION COMPLETE — awaiting independent review.
