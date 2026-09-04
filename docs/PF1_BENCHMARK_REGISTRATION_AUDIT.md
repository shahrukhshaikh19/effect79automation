# PF-1 — Benchmark Registration Audit

**Date:** 2026-09-05  
**Baseline SHA:** `525eeb02b8eecc88845e5ed1e8aecbbaa4393d7f` (final foundation attestation)  
**PF-1 framework SHA:** `65512f19f237d9b9481c9aab8cbc20d171e9623d`  
**PF-1 hardening SHA:** `e3d9988e26881c23aeb9acf93f3c0448dfba7981`  
**Scope:** Post-foundation benchmark registration infrastructure + integrity hardening (no execution)

---

## Hardening fixes (PF-1-fixes)

| Fix | Description |
|-----|-------------|
| F1 | Independent frozen lock in `registry/BENCHMARKS.yaml` — triple hash (computed = embedded = registry anchor) |
| F2 | `operator_input.original_text` is evidence only; policy scans target executable contract fields |
| F3 | Foundation immutability via `git diff` against `525eeb0` with explicit allowlist |
| F4 | PF1-A01 calls production `validate_registry_data()` |

---

## Remaining integrity fixes (PF-1_remaining-fixes)

| Fix | Description |
|-----|-------------|
| R1 | Historical freeze provenance via `frozen_source_commit_sha` + `git show` content lookup |
| R2 | Git diff / baseline lookup fail-closed (never treat unknown Git state as clean) |
| R3 | Foundation compatibility files content-anchored via `PF1_FOUNDATION_COMPATIBILITY_LOCK.yaml` |
| R4 | Schema/docs use `frozen_source_commit_sha` (not ambiguous `frozen_commit_sha`) |

## Freeze-attestation provenance (PF-1 p2)

Each frozen `benchmark_id + contract_version` anchors its **first registry freeze attestation** via Git history (`git log --reverse registry/BENCHMARKS.yaml`).

Validation proves:

```text
current frozen_source_commit_sha == first attestation frozen_source_commit_sha
current frozen_contract_sha256 == first attestation frozen_contract_sha256
```

Then independently verifies source commit → historical registration → hash chain.

Same-version source-commit repoint (A→B) or hash rewrite fails even when current registry and registration are internally consistent.

---

## Historical frozen contract anchoring

When a benchmark reaches FROZEN:

**Step A — frozen source commit:** Registration artifacts finalized in an existing Git commit (`frozen_source_commit_sha`).

**Step B — registry attestation:** A later commit records provenance in `registry/BENCHMARKS.yaml`.

Verification:

```text
git show <frozen_source_commit_sha>:<registration_path>
→ historical registration hash H(A)

H(A) == registry frozen_contract_sha256
H(A) == current registration hash (unless valid explicit revision)
H(A) == embedded benchmark_contract_sha256
```

Dual rewrite of current registration + registry hash cannot bypass: historical Git content still returns A while current tree holds B.

Registry attestation commit is inferred from Git history — not self-referential.

---

## Git fail-closed

`git_changed_paths()` returns `(paths, error)`. Any unknown commit, git diff failure, or missing baseline → validation FAIL.

---

## Foundation compatibility lock

Baseline content: `e3d9988` (approved PF-1 compatibility state).

Locked files (content SHA256):

- `validation/validate_foundation.py`
- `validation/validate_cross_phase_consistency.py`
- `validation/validate_runtime_integration.py`
- `validation/validate_external_skills.py`
- `validation/validate_proprietary_skills.py`
- `validation/validate_tools.py`
- `validation/validate_foundation_adversarial.py`
- `validation/certify_foundation.py`

PF-1-owned files (path-allowed, not content-locked): `validate_benchmark_registration.py`, `benchmarks/*`, `registry/BENCHMARKS.yaml`, tests, docs.

Unanchored foundation validator paths in allowlist → FAIL.

---

## Operator input model

- `operator_input.original_text` — immutable source evidence (may contain blocked requests)
- `constraint_evaluation[]` — classifies operator requests vs executable contract
- Executable fields scanned: `normalized_brief`, requirements, acceptance, tools, etc.

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
tested_implementation_sha = e0bd72b (unchanged)
```

---

## PF-2 boundary

No benchmark execution, scoring, or BM-001 creation.
