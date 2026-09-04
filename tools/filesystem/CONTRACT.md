# ACOS Filesystem Tool Contract (Phase D)

Filesystem operations are scoped to **approved workspace roots** by default.

## Operation types

| Operation | Description | Risk |
|---|---|---|
| `read` | Read file contents/metadata | low |
| `create` | Create new files/directories | medium |
| `modify` | Update existing files | medium |
| `delete` | Remove files/directories | high |
| `move` | Relocate paths | high |
| `copy` | Duplicate paths | medium |

## Workspace boundaries

Default approved roots (relative to repository root):

- `skills/`
- `tools/`
- `registry/`
- `validation/`
- `docs/`
- `core/`
- `templates/`
- `validation/evidence/` (runtime evidence only — not canonical definitions)

## Prohibited

- Credential harvesting
- Hidden home-directory scanning
- Arbitrary machine-wide traversal
- Writing secrets into tracked files
- Mixing generated runtime evidence into skill definitions

## Evidence

All filesystem mutations for ACOS tooling should record:

- operation type
- source path(s)
- destination path(s)
- timestamp
- actor (tool/script id)

See `filesystem-policy.yaml` for machine-readable policy.
