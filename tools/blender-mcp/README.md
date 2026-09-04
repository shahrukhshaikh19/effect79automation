# ACOS Blender MCP Tool Configuration (Phase D)

Blender MCP is **execution infrastructure** — not an ACOS skill.

```text
ACOS proprietary 3D skills → creative direction / criticism
external Blender skills → modeling / materials / rendering procedures
Blender MCP → execution bridge into Blender
```

## Upstream (pinned)

See `UPSTREAM.yaml` for immutable commit `5866814479b4e2ca674d8d44969a9a2a78fdc8bb` (v1.9.1).

Install (explicit, not via validators):

```bash
uvx --from git+https://github.com/ahujasid/blender-mcp@5866814479b4e2ca674d8d44969a9a2a78fdc8bb blender-mcp
```

## ACOS policy

- Set `BLENDER_MCP_SAFE_MODE=1` for model-authored `execute_blender_code` validation
- Human approval required for destructive/high-impact operations (see `destructive-action-policy.yaml`)
- MCP does not approve its own visual output

## Handoff

```text
Blender MCP → scene/render/export evidence → 3D Critic / Visual Critic → Quality Gate
```

## Health check

`validation/check_blender_tool.py` — structural always; runtime when Blender available.

Do not build demo/branded 3D scenes in Phase D.
