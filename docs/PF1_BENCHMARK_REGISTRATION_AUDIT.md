# PF-1 — Benchmark Registration Audit

**Date:** 2026-09-05  
**Baseline SHA:** `525eeb02b8eecc88845e5ed1e8aecbbaa4393d7f`  
**Scope:** Post-foundation benchmark registration infrastructure only (no execution)

---

## Scope

PF-1 registers benchmark contracts before PF-2 execution. No benchmark output, scoring, routing overrides, or global memory promotion.

---

## Files added

| Path | Purpose |
|------|---------|
| `registry/BENCHMARKS.yaml` | Benchmark registry index |
| `benchmarks/README.md` | Scope and lifecycle documentation |
| `benchmarks/templates/*` | Registration schemas and templates |
| `validation/benchmark_scope.py` | PF-1 path allowlist for foundation validators |
| `validation/validate_benchmark_registration.py` | PF-1 registration validator |
| `validation/tests/benchmark/test_registration_adversarial.py` | PF1-A01..A12 adversarial tests |

---

## Registration architecture

- Stable benchmark IDs (`BM-001`, …)
- Operator input preserved separately from normalized brief
- Acceptance contract with applicable dimensions and deterministic weights
- Evidence plan frozen before execution
- Contract hash (`benchmark_contract_sha256`) excludes execution fields

---

## Immutability mechanism

- Status lifecycle: DRAFT → INPUT_REQUIRED → REGISTERED → FROZEN
- FROZEN requires contract hash, operator confirmation, evidence plan, hard failures
- Revision/version fields for contract changes (no silent mutation)

---

## Hash semantics

SHA-256 over canonical JSON of registration excluding: `contract_hash`, `benchmark_contract_sha256`, `execution_state`, scores, evidence outputs, frozen_at.

---

## Validator coverage

- Foundation ready gate
- PF phase state (PF-1 IN_PROGRESS; PF-2..5 NOT_STARTED)
- Infrastructure presence
- Registration file schema semantics
- No manual skill routing, license bypass, global aesthetic promotion
- No execution artifacts or pre-execution scores

---

## Adversarial tests

PF1-A01 through PF1-A12 implemented in `validation/tests/benchmark/`.

---

## Foundation regression

All A–G validators re-run after PF-1 changes — must remain PASS.

---

## Benchmark registration state

```text
BENCHMARK_INPUT_REQUIRED
```

No operator benchmark subject supplied. BM-001 not invented.

---

## Missing operator inputs

1. What should ACOS build/test?
2. What is the primary objective?
3. What references/assets are supplied?
4. What requirements are mandatory?
5. What must it specifically avoid?
6. Which target devices/viewports matter?

---

## PF-2 boundary

PF-2 NOT_STARTED. No benchmark execution, HTML/CSS, 3D production, or scoring.

---

## Phase state

```text
PF-1 = IN_PROGRESS / INPUT_REQUIRED
PF-2..PF-5 = NOT_STARTED
FOUNDATION_READY = VALID (unchanged tested_implementation_sha)
```
