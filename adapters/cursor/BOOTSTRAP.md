# ACOS Phase E — Cursor Adapter Bootstrap

**Adapter ID:** ADAPTER-CURSOR-01  
**Contract:** `registry/ADAPTERS.yaml`  
**Minimal rule:** `.cursor/rules/acos-bootstrap.mdc`

## Entrypoint behavior

1. Cursor agent reads `.cursor/rules/acos-bootstrap.mdc` (thin pointer only).
2. Follow references to `ACOS_FINAL_CANONICAL_v1.2.md` and `AGENTS.md`.
3. Load `core/*` and registries per task — `registry/SKILLS.yaml`, `registry/TOOLS.yaml`.
4. Progressive skill loading: `SKILL_LOADING.md`.
5. Tool mapping: `TOOL_MAPPING.yaml`.

## Authority

Cursor rules are **compatibility surfaces**, not constitutional authority.  
If rule text conflicts with canonical master, canonical master wins.

## Workspace behavior

- Operate inside repository workspace scope
- Use validation scripts for evidence — do not skip gates
- Shell/filesystem per `registry/TOOL_SECURITY.yaml`

## MCP / tools in Cursor

Map host MCP namespaces (e.g. `user-blender`) to canonical families via `TOOL_MAPPING.yaml`.  
Blender MCP: RESTRICTED from health script until protocol verified; live MCP is separate evidence.

## Phase F boundary

Adapter does not implement routing or memory runtime.
