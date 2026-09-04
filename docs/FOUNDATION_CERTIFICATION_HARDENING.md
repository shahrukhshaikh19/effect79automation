# ACOS v1.2 — Foundation Certification Hardening

**Date:** 2026-09-04  
**Scope:** Phase A–D integrity corrections (NOT Phase E)  
**Authority:** `corrections.md` independent expert audit findings

---

## 1. Baseline

| Field | Value |
|---|---|
| Baseline HEAD (pre-hardening) | `dc60ac0065642c665a96627e5cd2ba0003c12073` |
| Branch | `master` |
| Reason | Cross-phase semantic drift and evidence-truthfulness defects found during independent audit |

---

## 2. Independent audit findings and corrections

### Finding 1 — Quality Gate semantic contradiction

**Previous contradiction:** Canonical/core used `APPROVED`/`REJECTED` while quality-gate skill/schema used `APPROVE`/`REJECT`/`BLOCKED_INSUFFICIENT_EVIDENCE` without explicit distinction.

**Chosen model:**

| Status | Meaning | May ship |
|---|---|---|
| APPROVED | Required evidence exists; gates pass | Yes |
| REJECTED | Evidence sufficient; hard/unacceptable failures demonstrated | No — route corrections |
| BLOCKED_INSUFFICIENT_EVIDENCE | Cannot make reliable judgment; evidence missing/invalid | No — collect evidence |

**Changes:**

- `ACOS_FINAL_CANONICAL_v1.2.md` — terminal status table + workflow diagram
- `core/QUALITY_GATES.md` — explicit BLOCKED is not approval
- `core/WORKFLOW.md` — gate routing
- `skills/acos/acos-quality-gate/SKILL.md` — APPROVED/REJECTED/BLOCKED_INSUFFICIENT_EVIDENCE
- `skills/acos/acos-quality-gate/references/gate-report-schema.yaml`
- `docs/PROPRIETARY_SKILLS_AUDIT.md`

**Validator enforcement:** `validation/validate_cross_phase_consistency.py` — gate contract across authority files.

---

### Finding 2 — Browser DPR integrity

**Previous defect:** Manifest recorded `device_scale_factor` from config without verifying Playwright applied it.

**Correction:** `tools/browser/scripts/capture-evidence.mjs`:

- Creates per-viewport browser context with `deviceScaleFactor`
- Measures `window.devicePixelRatio` as effective DPR
- Sets `dpr_integrity` per capture; `runtime_healthy=false` on mismatch
- Generates standalone `console_log.json`

**Schema:** `tools/browser/schemas/browser-evidence.schema.yaml` — requested/effective DPR fields.

**Config example:** `tools/browser/viewport-config.example.yaml` — dpr1 + dpr3 viewports.

---

### Browser capability audit

See `docs/TOOLS_AUDIT.md` — all 12 registered capabilities + `console_log_json` evidence output mapped to implementation with PASS status.

---

### Finding 3 — OpenAI licensing (EXT-FE-01, EXT-FE-02)

| Skill ID | Pinned SHA | Evidence inspected | License status | Commercial redistribution |
|---|---|---|---|---|
| EXT-FE-01 | `1e285826e604f66f7208f7ac4dba0fe8341d1f57` | repo root, plugins/build-web-apps/, README | LICENSE_REVIEW_REQUIRED | blocked_pending_license_review |
| EXT-FE-02 | `1e285826e604f66f7208f7ac4dba0fe8341d1f57` | same | LICENSE_REVIEW_REQUIRED | blocked_pending_license_review |

GitHub API at pin: `license: null`. No LICENSE invented.

**Lockfile:** `registry/EXTERNAL_SKILLS_LOCK.yaml` — reinspection metadata added.

---

### Finding 4 — Blender health evidence semantics

**Previous defect:** TCP socket reachability could be misread as full MCP verification.

**Correction:** `validation/check_blender_tool.py` reports:

- `tcp_socket_probe_attempted`, `tcp_socket_reachable`
- `protocol_handshake_attempted: false`, `protocol_handshake_verified: false`
- `addon_runtime_verified: false`

Runtime **RESTRICTED** when executable found (script does not claim AVAILABLE from socket alone).

Live MCP evidence documented separately in `docs/BLENDER_RUNTIME_CORRECTION.md`.

---

### Finding 5 — Blender capability precision

**Correction:** `tools/blender-mcp/capabilities.yaml` — `native_capabilities`, `derived_via_execute_blender_code`, `restricted_capabilities`.

**Registry:** `registry/TOOLS.yaml` — `capability_taxonomy` pointer; notes clarify material/render/export are derived, not native MCP.

---

## 3. Files changed

| Area | Files |
|---|---|
| Quality Gate | ACOS_FINAL_CANONICAL_v1.2.md, core/QUALITY_GATES.md, core/WORKFLOW.md, acos-quality-gate/*, PROPRIETARY_SKILLS_AUDIT.md |
| Browser | capture-evidence.mjs, browser-evidence.schema.yaml, viewport-config.example.yaml, TOOLS.yaml, TOOL_SECURITY.yaml, TOOLS_AUDIT.md |
| OpenAI license | EXTERNAL_SKILLS_LOCK.yaml, EXTERNAL_SKILLS_AUDIT.md |
| Blender | check_blender_tool.py, capabilities.yaml, TOOLS.yaml, BLENDER_RUNTIME_CORRECTION.md, TOOLS_AUDIT.md |
| Validators | validate_cross_phase_consistency.py (new), validate_proprietary_skills.py, validate_external_skills.py, validate_tools.py |
| Documentation | IMPLEMENTATION_CHECKLIST.md, PROGRESS_LEDGER.md, this file |

**Not modified:** `skills/external/**` bodies, unrelated proprietary skills, Phase E adapters, benchmarks, projects.

---

## 4. Validators added/updated

| Validator | Change |
|---|---|
| validate_cross_phase_consistency.py | **NEW** — gate contract, checklist/ledger, capability truth, domain neutrality, phase boundaries |
| validate_proprietary_skills.py | Stale Phase D+ messaging removed |
| validate_external_skills.py | Stale Phase C messaging removed |
| validate_tools.py | Browser schema/DPR structural checks; stale Phase E+ messaging removed |

---

## 5. Security impact

`registry/TOOL_SECURITY.yaml` — capture-evidence.mjs note updated for console_log.json and DPR integrity. No new privileged operations introduced.

---

## 6. Runtime health (post-hardening)

Run separately from structural validators:

```bash
python validation/check_browser_tool.py
python validation/check_blender_tool.py
python validation/check_git_tool.py
python validation/check_shell_tool.py
python validation/check_filesystem_tool.py
```

Browser DPR runtime test:

```bash
node tools/browser/scripts/capture-evidence.mjs --config tools/browser/viewport-config.example.yaml --output validation/evidence/browser-dpr-hardening
```

---

## 7. Unresolved restrictions

| Item | Status |
|---|---|
| EXT-FE-01/02 license | LICENSE_REVIEW_REQUIRED — commercial redistribution blocked |
| Blender MCP protocol | Health script does not perform MCP handshake; live MCP verified separately when server running |
| img2threejs | restricted (pre-existing) |

---

## 8. Phase E+ confirmation

Phase E (adapters), F–J remain **NOT STARTED**. No benchmarks, sample projects, orchestration, or memory runtime added.

---

## 9. Certification sequence

```bash
python validation/validate_foundation.py
python validation/validate_external_skills.py
python validation/validate_proprietary_skills.py
python validation/validate_tools.py
python validation/validate_cross_phase_consistency.py
```

All must PASS before commit.
