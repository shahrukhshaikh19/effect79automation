# ACOS v1.2 — Tools Audit (Phase D)

**Date:** 2026-09-04  
**Authority:** `phase-D.md`, `registry/TOOLS.yaml`  
**Structural validation:** `validation/validate_tools.py` — PASSED  
**Phase C housekeeping:** `validate_foundation.py` stale messaging corrected

---

## Capability families

| Family | Tool ID | Structural | Runtime (this environment) |
|---|---|---|---|
| browser | TOOL-BROWSER-01 | CONFIGURED | **AVAILABLE** — Playwright 1.49.1, Chromium, multi-viewport capture |
| blender | TOOL-BLENDER-01 | CONFIGURED | **RESTRICTED** (health script) — see Blender evidence dimensions below |
| git | TOOL-GIT-01 | CONFIGURED | **AVAILABLE** — git 2.32.0 |
| shell | TOOL-SHELL-01 | CONFIGURED | **AVAILABLE** — PowerShell |
| filesystem | TOOL-FS-01 | CONFIGURED | **AVAILABLE** — dedicated `check_filesystem_tool.py` |

---

## Browser — TOOL-BROWSER-01

| Field | Value |
|---|---|
| **Purpose** | Rendered experience inspection; screenshot/console/page-error evidence for critics |
| **Implementation** | Playwright 1.49.1 + Node scripts under `tools/browser/` |
| **Version/pin** | `playwright@1.49.1` in `tools/browser/package.json` |
| **Capabilities** | Multi-viewport capture (per-viewport browser context + deviceScaleFactor), full-page/viewport/element screenshots, console/page errors, network failures, reduced-motion, readiness waits, YAML manifest + console_log.json |
| **Not capabilities** | Visual quality approval, design judgments, arbitrary crawling, credential storage |
| **Filesystem** | yes — explicit `--output` dir; local fixtures |
| **Network** | yes — only to supplied target URL |
| **Subprocess** | yes — Chromium via Playwright |
| **Destructive actions** | overwrites files in explicit output directory |
| **Approval boundary** | authenticated remote targets; non-workspace output paths |
| **Evidence outputs** | `manifest.yaml`, PNG screenshots, `console_log.json` |
| **DPR integrity** | Requested vs effective DPR measured via `window.devicePixelRatio`; mismatch → `runtime_healthy=false` |
| **Health status** | structural CONFIGURED; runtime **AVAILABLE** (Chromium launch + neutral capture succeeded) |
| **Risks** | Requires explicit `npm ci` + bootstrap; not installed by validators |
| **Review status** | PASS |

### Browser → critic handoff

```text
Browser/Playwright → render/runtime evidence → Visual/Creative/3D Critics → Quality Gate
```

Browser must NOT output: "approved", "premium", quality scores.

### Browser capability audit (2026-09-04 hardening)

| Capability | Implementation | Evidence | Status |
|---|---|---|---|
| open_local_or_authorized_target | `resolveTarget()` in capture-evidence.mjs | manifest `target` field | PASS |
| viewport_controlled_render | per-viewport `browser.newContext({ deviceScaleFactor })` | capture `viewport.requested/effective_device_scale_factor` | PASS |
| deterministic_screenshot | Playwright `page.screenshot()` | PNG paths in manifest | PASS |
| full_page_screenshot | `fullPage: true` when `capture.full_page` | `full_page.png` per viewport | PASS |
| element_region_screenshot | `page.locator(selector).screenshot()`; fails if missing | `element.png` + selector in manifest | PASS |
| multi_viewport_capture | iterates `config.viewports` with separate contexts | multiple capture records | PASS |
| console_error_capture | `page.on("console")` type error | `console_errors` array per capture | PASS |
| page_error_capture | `page.on("pageerror")` | `page_errors` array per capture | PASS |
| network_failure_capture | `page.on("requestfailed")` | `network_failures` array per capture | PASS |
| reduced_motion_emulation | `reducedMotion: "reduce"` in context | manifest `reduced_motion` | PASS |
| readiness_wait_conditions | `page.goto` waitUntil + optional settle | `readiness_condition` in manifest | PASS |
| evidence_manifest_generation | writes `manifest.yaml` | manifest file | PASS |
| console_log_json (evidence output) | writes `console_log.json` | manifest `console_log_json` path | PASS |

---

## Blender MCP — TOOL-BLENDER-01

| Field | Value |
|---|---|
| **Purpose** | Execution bridge to Blender via MCP (inspect/mutate/render/export evidence) |
| **Implementation** | Upstream `blender-mcp` pinned at `5866814479b4e2ca674d8d44969a9a2a78fdc8bb` (v1.9.1) |
| **Version/pin** | Commit SHA + package 1.9.1 — see `tools/blender-mcp/UPSTREAM.yaml` |
| **Capabilities** | See `tools/blender-mcp/capabilities.yaml`: native MCP inspection/integrations; material/render/export derived via `execute_blender_code`; restricted arbitrary Python |
| **Not capabilities** | Creative direction, quality gate, critic judgments, ACOS skill knowledge |
| **Filesystem** | yes — temp screenshots; bpy file ops via execute_blender_code |
| **Network** | yes — localhost socket; external asset APIs; optional telemetry |
| **Subprocess** | yes — MCP server; Blender external |
| **Destructive actions** | delete objects, overwrite .blend/exports, arbitrary Python execution |
| **Approval boundary** | execute_blender_code, deletes, overwrites, external downloads — human required |
| **Evidence outputs** | `blender-evidence.schema.yaml` manifest fields |
| **Health status** | structural CONFIGURED; TCP socket probe only (not MCP protocol handshake) — see check_blender_tool.py fields |
| **Risks** | High privilege; safe mode recommended; RESTRICTED until live MCP handshake verified |
| **Review status** | RESTRICTED |

### Blender runtime evidence dimensions

| Dimension | Status (this environment) |
|---|---|
| Structural configuration | CONFIGURED |
| Health-script runtime | RESTRICTED |
| TCP socket (localhost:9876) | REACHABLE when MCP server running |
| Protocol handshake (health script) | NOT VERIFIED |
| Live MCP client evidence | VERIFIED separately when Cursor MCP + Blender active — see BLENDER_RUNTIME_CORRECTION.md |

Do not collapse these into a single "AVAILABLE" claim from the health script alone.

### Blender → critic handoff

```text
Blender MCP → scene/render/export evidence → 3D Critic / Visual Critic → Quality Gate
```

---

## Git — TOOL-GIT-01

| Field | Value |
|---|---|
| **Purpose** | Version control inspection and controlled mutation |
| **Implementation** | Git CLI contract (`tools/git/`) |
| **Version/pin** | Environment git executable |
| **Capabilities** | read-only, local mutation, remote mutation (classified) |
| **Not capabilities** | Quality approval; normalizing force-push/reset |
| **Filesystem** | yes — repository working tree |
| **Network** | optional — remote operations only |
| **Subprocess** | yes — git executable |
| **Destructive actions** | force push, hard reset, clean -fd, history rewrite, branch delete |
| **Approval boundary** | all destructive + push require explicit/human approval |
| **Evidence outputs** | status, diff, log, commit SHA, push result |
| **Review status** | PASS (contract) |

---

## Shell — TOOL-SHELL-01

| Field | Value |
|---|---|
| **Purpose** | Classified shell execution for mechanical operations |
| **Implementation** | Policy contract (`tools/shell/`) |
| **Capabilities** | read_only, workspace_write, classified install/network/destructive |
| **Not capabilities** | Blind arbitrary model-generated execution |
| **Filesystem** | yes — workspace scoped |
| **Network** | classified only |
| **Subprocess** | yes |
| **Destructive actions** | classified — human approval required |
| **Review status** | PASS (contract) |

---

## Filesystem — TOOL-FS-01

| Field | Value |
|---|---|
| **Purpose** | Workspace-scoped file operations with explicit classification |
| **Implementation** | Policy contract (`tools/filesystem/`) |
| **Capabilities** | read, create, modify, delete, move, copy within approved roots |
| **Not capabilities** | Machine-wide traversal, credential harvesting |
| **Evidence output root** | `validation/evidence/` |
| **Health check** | `validation/check_filesystem_tool.py` (dedicated; not shell) |
| **Review status** | PASS (contract + runtime probe) |

### Phase D audit correction (2026-09-04)

Independent audit found `TOOL-FS-01` incorrectly pointed to `validation/check_shell_tool.py`. Corrected with dedicated filesystem health check performing neutral temp-file CRUD under `validation/evidence/fs-health-*` only.

---

## Tool → memory boundary

Tools produce evidence only. No automatic global memory promotion from tool errors.

```text
evidence → critic/gate → failure-learning → scoped memory
```

---

## Security self-review (§43)

| Check | Result |
|---|---|
| Arbitrary shell without classification | NO — shell policy forbids default arbitrary execution |
| Delete arbitrary files | NO — classified destructive; approval required |
| Silent asset overwrite | NO — explicit paths and policies |
| Outside workspace access | NO — default workspace scope |
| Secrets in repo | NO — scanned; `.env` gitignored |
| Execute downloaded code unreviewed | NO — upstream pinned + security inventory |
| Blender arbitrary Python | YES — RESTRICTED; safe mode + approval |
| Browser unintended remote actions | NO — explicit target only |
| Package installs explicit | YES — bootstrap separate from validators |
| Network documented | YES — TOOL_SECURITY.yaml + audits |

Unresolved high-risk unknowns → RESTRICTED (Blender MCP runtime).

---

## Domain neutrality

- No sample product/site/brand in tool fixtures
- Neutral `blank.html` health fixture only
- `benchmarks/` and `projects/` remain empty
- Phase B external skills unmodified
- Phase C proprietary skills unmodified

---

## Environment limitations (§47)

Runtime availability depends on local installation of Node deps, Playwright browsers, and Blender. Structural completion does not imply runtime tested. Blender health script reports RESTRICTED unless protocol handshake is verified by the defined health contract.
