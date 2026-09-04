# ACOS Git Tool Contract (Phase D)

Git is **execution infrastructure**, not a skill. Models/adapters invoke git through classified operations; this contract defines allowed classes and safety boundaries.

## Operation classes

| Class | Examples | Default approval |
|---|---|---|
| **read-only inspection** | `status`, `diff`, `log`, `show`, branch inspection | none |
| **local mutation** | `add`, `commit`, `checkout`, `switch`, branch create | task-scoped |
| **remote mutation** | `push`, `fetch`, `pull` | explicit authorization for push |
| **high-risk / destructive** | `push --force`, `reset --hard`, `clean -fd`, history rewrite, branch delete | always requires human approval |

## Safety policy

1. Inspect before mutation (`status`, `diff`).
2. Do not discard unrelated user changes.
3. Do not force-push to shared branches.
4. Do not rewrite published history without explicit authorization.
5. Do not delete branches without explicit authorization.
6. Do not commit unrelated files.
7. Record commit SHA as evidence.
8. **Committed ≠ pushed** — prove push separately when required.

## Evidence outputs

- `git status` / `git diff` text
- commit SHA and message
- push result (remote ref update) when applicable

## Non-goals

- Git does not approve quality.
- Git does not replace code review or quality gate.

See `git-policy.yaml` for machine-readable classification.
