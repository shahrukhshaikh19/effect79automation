# Cursor Adapter — Context Budget Strategy

Identical ACOS logical sequence to other adapters (see `registry/ADAPTERS.yaml`).

## Cursor-specific notes

- IDE context includes open files — do not treat open tabs as implicit skill activation
- Prefer `@` references to canonical files over pasting large policy blocks into chat
- Use `validation/*` scripts for structural evidence
- Context limits: defer to model profiles in `registry/MODELS.yaml` when populated with benchmark evidence

## Under pressure

- Smaller skill batches
- Stage bounded tasks with explicit YAML/handoff outputs
- Re-read canonical authority between stages instead of expanding adapter files
