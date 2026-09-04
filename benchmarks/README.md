# ACOS Benchmark Registration (PF-1)

Post-foundation benchmark contracts live under `benchmarks/` and `registry/BENCHMARKS.yaml`.

## Scope boundary

Benchmark-specific intent, references, acceptance criteria, and evidence plans belong **only** in benchmark registration artifacts.

They must **not** be copied into:

- `core/`
- canonical master / `AGENTS.md` universal rules
- `skills/acos/` universal behavior
- global routing or memory policy

## Lifecycle

```text
DRAFT → INPUT_REQUIRED → REGISTERED → FROZEN → (PF-2) EXECUTION_STARTED → COMPLETED
```

PF-1 ends at **FROZEN** only when operator input, validation, and confirmation are complete.

## Registration layout

```text
benchmarks/templates/          # PF-1 schemas and templates (infrastructure)
benchmarks/BM-001/             # First benchmark (operator-supplied, not invented)
  REGISTRATION.yaml
  ORIGINAL_INPUT.md
  ACCEPTANCE_CONTRACT.yaml
  EVIDENCE_PLAN.yaml
```

## Operator input required

Until the operator supplies benchmark subject and requirements, status remains `INPUT_REQUIRED`.

Do not invent company, product, aesthetic, or deliverable content in PF-1.
