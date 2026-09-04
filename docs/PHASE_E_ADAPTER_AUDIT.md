# ACOS v1.2 — Phase E Adapter Audit

**Date:** 2026-09-04  
**Baseline:** `57f3cf0c6bdd3ab9755e1c7b505aff8649fc2ac7`  
**Authority:** `phase-E.md`, `registry/ADAPTERS.yaml`

---

## Architecture

Thin compatibility adapters translate platform loading conventions into ACOS.  
Canonical intelligence remains in master, core, registry, and skills — not in adapters.

```text
adapters/
├── claude/     ADAPTER-CLAUDE-01
├── cursor/     ADAPTER-CURSOR-01  + .cursor/rules/acos-bootstrap.mdc
├── codex/      ADAPTER-CODEX-01
└── local/      ADAPTER-LOCAL-01
registry/ADAPTERS.yaml   shared contract
```

---

## Canonical vs adapter authority

| Class | Examples | Authority level |
|---|---|---|
| Canonical | `ACOS_FINAL_CANONICAL_v1.2.md`, `AGENTS.md`, `core/*`, `registry/*`, `skills/*` | Supreme for ACOS semantics |
| Adapter | `adapters/*/BOOTSTRAP.md`, `.cursor/rules/acos-bootstrap.mdc` | Compatibility only — references canonical |

Platform files derive behavior from canonical authority. Adapters must not silently override constitutional policy.

---

## Shared contract

`registry/ADAPTERS.yaml` defines:

- Four adapters with required contract fields
- Shared instruction precedence (ACOS logical vs host platform)
- Progressive skill loading L1/L2/L3
- Context strategy sequence
- Tool status semantics
- Licensing preservation (EXT-FE-01/02)
- Phase F boundary (`adapters_must_not_implement`)

---

## Per-platform behavior

### Claude (ADAPTER-CLAUDE-01)

- Entry: `adapters/claude/BOOTSTRAP.md`
- Agent Skills L1/L2/L3 via registry paths
- MCP tool mapping in `TOOL_MAPPING.yaml`
- Host precedence documented separately from ACOS logical order

### Cursor (ADAPTER-CURSOR-01)

- Entry: `adapters/cursor/BOOTSTRAP.md`
- Thin rule: `.cursor/rules/acos-bootstrap.mdc` (references only)
- Workspace tools mapped in `TOOL_MAPPING.yaml` (Shell, MCP namespaces, Read/Write)

### Codex (ADAPTER-CODEX-01)

- Entry: `adapters/codex/BOOTSTRAP.md`
- Shared root `AGENTS.md` — not rewritten (`AGENTS_INTEGRATION.md`)

### Local (ADAPTER-LOCAL-01)

- Entry: `adapters/local/LOCAL_LLM_BOOTSTRAP.md`
- Bounded `TASK_PACKET.schema.yaml` for models without native skills
- `FALLBACK_BOUNDARY.md` defines orchestrator hook — **not** Phase F runtime

---

## Progressive skill loading

| Level | Content |
|---|---|
| L1 | Registry metadata |
| L2 | Activated `SKILL.md` only |
| L3 | References/scripts on demand |

Inventory from `registry/SKILLS.yaml` — 36 external + 14 proprietary.  
Future Phase F may supply `activated_skill_ids`; adapters do not implement routing.

---

## Model profile integration

- `registry/MODELS.yaml` remains **empty** — no invented benchmark results
- `templates/MODEL_PROFILE_TEMPLATE.md` compatible for future profiles
- Adapter != model profile

---

## Tool mapping

Each adapter `TOOL_MAPPING.yaml` maps canonical families → host examples with `runtime_status_source` health scripts.

Blender: `health_script_default: RESTRICTED`; `tcp_not_handshake` / `tcp_not_handshake: true` where applicable.  
Status semantics: AVAILABLE, RESTRICTED, BLOCKED, UNAVAILABLE, UNKNOWN.

---

## Security

Adapters are not permission escalators. They reference:

- `registry/TOOL_SECURITY.yaml`
- `tools/shell/shell-policy.yaml`
- Blender safe-mode guidance

No automatic shell, no bypass of Git destructive restrictions, no credential harvesting.

---

## Licensing boundaries

EXT-FE-01/02: `LICENSE_REVIEW_REQUIRED`, `blocked_pending_license_review` — adapters must not copy bodies.  
img2threejs: existing `restricted` status preserved.

---

## Phase F boundary

Adapters may declare consumption of `activated_skill_ids` from future routing layer.  
**Not implemented:** autonomous router, memory runtime, quality aggregation runtime, benchmark runner, orchestration engine.

---

## Validator coverage

`validation/validate_adapters.py`:

- Structural: 4 families, contract fields, entrypoints
- Thinness: line-overlap with Constitution/Quality Gates/proprietary skills
- Canonical references in entrypoints
- Phase F boundary scan
- Licensing guards
- Blender false verification claims
- Domain neutrality
- Cursor rule thinness
- MODELS.yaml empty registry preserved

Updated: `validate_cross_phase_consistency.py`, `validate_tools.py` (phase-aware Phase E boundaries)

---

## Static test matrix (Phase E)

| Test | Result |
|---|---|
| Claude bootstrap without copying canonical brain | PASS — references only |
| Cursor rules point to ACOS without duplicate authority | PASS — thin `.mdc` |
| Codex uses shared AGENTS.md | PASS — integration doc |
| Local bounded task packet without retraining | PASS — TASK_PACKET schema |
| Migration: delete adapters, canonical intact | PASS — by design |
| Context: one skill via L2 without all 50 | PASS — progressive loading contract |
| Tool absence: RESTRICTED/UNKNOWN without hallucination | PASS — TOOL_MAPPING semantics |
| Licensing: EXT-FE restricted | PASS — guards in contract |
| Phase boundary: no Phase F router | PASS — validator + boundary docs |

---

## Phase E certification correction — 2026-09-04

| Finding | Correction |
|---|---|
| Local adapter owned task classification/skill selection | Removed; consumes `routing.activated_skill_ids` from caller/Phase F |
| Claude precedence implied ACOS overrides host | Host technical hierarchy always applies; ACOS logical authority only within host-permitted behavior |
| Validators too phrase-based | `validate_routing_ownership` + `validate_host_precedence` in validate_adapters.py |

**Routing ownership:** Adapter consumes routing. Adapter does not own routing.

**Host precedence:** Host system/developer/platform/safety instructions apply; adapter cannot override.

---

## Evidence

- `validation/validate_adapters.py` — PASSED
- Full A–D validator chain — PASSED (post Phase E)
- Health checks unchanged — Blender RESTRICTED from health script

---

## Unresolved restrictions

- EXT-FE-01/02 license
- img2threejs restricted
- Blender protocol handshake not verified by health script
- FOUNDATION_READY undeclared until Phase G

---

## Phase state after E

```text
A COMPLETE | B COMPLETE | C COMPLETE | D COMPLETE | E COMPLETE
F NOT_STARTED | G NOT_STARTED | PF NOT_STARTED
FOUNDATION_READY = not declared
```
