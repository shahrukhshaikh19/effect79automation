# ACOS Shell Tool Contract (Phase D)

Shell access is **high privilege**. ACOS does not provide a blind "execute anything" wrapper.

## Command risk classes

| Class | Description | Approval |
|---|---|---|
| `read_only` | Inspection, listing, echo, version checks | none |
| `workspace_write` | Create/modify files within approved workspace paths | task-scoped |
| `dependency_install` | npm/pip/uv install operations | explicit |
| `network_access` | curl, wget, remote fetch | explicit |
| `destructive` | rm -rf, del /s, overwrite without backup | human required |
| `privileged` | sudo, admin, system modification | human required |

## Rules

1. Prefer deterministic scripts (`validation/*.py`, `tools/browser/scripts/*.mjs`) over ad-hoc shell.
2. Every command must be classifiable before execution.
3. Scripts must declare inputs, outputs, exit codes, and dependencies.
4. No hidden destructive side effects.
5. Do not mutate unrelated files.

## Non-goals

- Shell is not a substitute for ACOS skills or critics.
- Shell does not auto-approve its own output.

See `shell-policy.yaml` for machine-readable classes and examples.
