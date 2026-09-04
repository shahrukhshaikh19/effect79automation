# ACOS Blender MCP — Runtime Blocker Correction

**Date:** 2026-09-04  
**Tool:** TOOL-BLENDER-01  
**Authority:** Phase D operational evidence (post-structural completion)

---

## Original blocker (Phase D evidence)

Phase D structural implementation completed with truthful runtime status **BLOCKED**:

| Symptom | Cause |
|---|---|
| `check_blender_tool.py` → BLOCKED | `blender.exe` not on system PATH (installed under `Program Files` only) |
| MCP not verified | Health check did not probe MCP socket; only PATH lookup |
| Live MCP warning | Addon protocol **4** behind MCP server expected **5** (`addon_version` 1.5) |
| Transient handshake error | `[WinError 10053]` connection aborted during first probe |

Structural contracts (`tools/blender-mcp/`) were always valid. Runtime was blocked/misreported, not missing configuration.

---

## What was fixed (how)

### 1. Addon protocol sync

```bash
# Windows: UTF-8 required to avoid cp1252 print crash on arrow chars
set PYTHONIOENCODING=utf-8
uvx blender-mcp install-addon
```

**Result:** Addon installed/updated at:

```text
%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons\blender_mcp.py
```

After Blender reloaded the addon:

| Field | Before | After |
|---|---|---|
| `up_to_date` | false | **true** |
| `protocol_version` | 4 | **5** |
| `addon_version` | 1.5 | **1.6** |
| `warning` | protocol behind | **null** |
| `blender_version` | 5.2.0 LTS | 5.2.0 LTS |

Live MCP verification (Cursor `user-blender`):

- `get_addon_status` → PASS
- `get_scene_info` → PASS
- `get_object_info` → PASS
- `get_viewport_screenshot` → PASS

### 2. Health check hardening

Updated `validation/check_blender_tool.py` to:

1. Discover `blender.exe` on Windows standard install paths when not on PATH  
   (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`)
2. Probe MCP addon socket `localhost:9876` (neutral TCP reachability)
3. Report:
   - **AVAILABLE** — executable found + MCP socket reachable
   - **RESTRICTED** — executable found, MCP server not running
   - **BLOCKED** — no executable discovered

This separates **installed** from **running with MCP started**.

---

## Current expected runtime (when Blender + MCP Server active)

```json
{
  "runtime": "AVAILABLE",
  "blender_executable": "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe",
  "blender_version": "Blender 5.2.0 LTS",
  "mcp_socket_reachable": true
}
```

If Blender is closed or MCP Server not started → **RESTRICTED** (not a regression).

---

## Operational notes

- ACOS upstream pin remains `5866814479b4e2ca674d8d44969a9a2a78fdc8bb` (blender-mcp 1.9.1) in repo contracts
- Live Cursor MCP may run newer `uvx blender-mcp` for addon install — addon file on disk is authoritative for Blender-side protocol
- Recommend `BLENDER_MCP_SAFE_MODE=1` for model-authored `execute_blender_code` per ACOS policy
- Re-run after Blender/MCP changes: `python validation/check_blender_tool.py`

---

## Not changed

- Phase B external skills
- Phase C proprietary skills
- Phase E adapters (not started)
- No sample 3D scenes or benchmark content added
