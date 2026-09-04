# PF-1 — Benchmark Registration Audit

**Date:** 2026-09-05  
**Baseline SHA:** `525eeb02b8eecc88845e5ed1e8aecbbaa4393d7f` (final foundation attestation)  
**PF-1 framework SHA:** `65512f19f237d9b9481c9aab8cbc20d171e9623d`  
**Scope:** Post-foundation benchmark registration infrastructure + hardening (no execution)

---

## Hardening fixes (PF-1-fixes)

| Fix | Description |
|-----|-------------|
| F1 | Independent frozen lock in `registry/BENCHMARKS.yaml` — triple hash (computed = embedded = registry anchor) |
| F2 | `operator_input.original_text` is evidence only; policy scans target executable contract fields |
| F3 | Foundation immutability via `git diff` against `525eeb0` with explicit allowlist |
| F4 | PF1-A01 calls production `validate_registry_data()` |

---

## Frozen contract anchoring

When a benchmark reaches FROZEN:

```text
computed hash(REGISTRATION.yaml)
== REGISTRATION.yaml benchmark_contract_sha256
== registry/BENCHMARKS.yaml frozen_contract_sha256
```

Registry also records `contract_version`, optional `versions[]` history, `frozen_commit_sha`, `frozen_at`.

Silent same-version mutation with recomputed local hash fails because registry anchor does not match.

---

## Operator input model

- `operator_input.original_text` — immutable source evidence (may contain blocked requests)
- `constraint_evaluation[]` — classifies operator requests vs executable contract
- Executable fields scanned: `normalized_brief`, requirements, acceptance, tools, etc.

---

## Foundation immutability

Baseline: `525eeb02b8eecc88845e5ed1e8aecbbaa4393d7f`  
Forbidden changes: `core/`, `skills/acos/`, `runtime/`, `adapters/`, routing/runtime policies, canonical master, AGENTS.md  
Allowed: PF-1 registration infrastructure + narrowly scoped validator compatibility files.

`tested_implementation_sha` remains `e0bd72b` (unchanged).

---

## Benchmark registration state

```text
BENCHMARK_INPUT_REQUIRED
benchmarks registered = 0
BM-001 absent
```

---

## Phase state

```text
PF-1 = IN_PROGRESS / INPUT_REQUIRED
PF-2..PF-5 = NOT_STARTED
FOUNDATION_READY = VALID
```

---

## PF-2 boundary

No benchmark execution, scoring, or BM-001 creation.
