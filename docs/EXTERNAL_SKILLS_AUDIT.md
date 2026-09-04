# ACOS v1.2 — External Skills Import Audit (Phase B)

**Date:** 2026-09-04  
**Authority:** `registry/SKILLS.yaml`  
**Lockfile:** `registry/EXTERNAL_SKILLS_LOCK.yaml`  
**Phase status:** COMPLETE (pending human review)

---

## Inventory summary

| Category | Expected | Imported | Status |
|---|---:|---:|---|
| Frontend / Design / Accessibility | 4 | 4 | ✓ |
| Three.js selected | 10 | 10 | ✓ |
| R3F merge reference | 1 | 1 | ✓ |
| GSAP selected | 5 | 5 | ✓ |
| Blender curated subset | 15 | 15 | ✓ |
| img2threejs | 1 | 1 | ✓ |
| **Total locked entries** | **36** | **36** | ✓ |

No unapproved Three.js, GSAP, or Blender skills were imported.

---

## Upstream sources and pinned SHAs

| Repository | Commit SHA | Retrieval date |
|---|---|---|
| `openai/plugins` | `1e285826e604f66f7208f7ac4dba0fe8341d1f57` | 2026-09-04 |
| `anthropics/knowledge-work-plugins` | `9e2bcbc55b70d5c3cdc04a9789cb00c030bf7fc1` | 2026-09-04 |
| `magnus919/agent-skills` | `de968dfdfb5ac92336a4915dad4bb56a27fe0207` | 2026-09-04 |
| `alton47/threejs-skills` | `7b8e25638cff83a6be4926d8f05001022cc80ac3` | 2026-09-04 |
| `shreyam1008/shre-skills` | `412c49746b8bbbb59b7e823b0d5126f866050314` | 2026-09-04 |
| `greensock/gsap-skills` | `aed9cfd3277740755f6bfc1155c7aa645403b760` | 2026-09-04 |
| `arjun988/blender-skills` | `8f778d2405a214b508d4c7d80742be8e43acdd52` | 2026-09-04 |
| `img2threejs/img2threejs` | `d6815db757c1eb435ae55f91fb375a7a98ddf28b` | 2026-09-04 |

Floating `main` / `latest` references were **not** used.

---

## License status

| Source | License | Evidence | Notes |
|---|---|---|---|
| OpenAI frontend skills (2) | `LICENSE_REVIEW_REQUIRED` | No LICENSE in `build-web-apps` path at pinned commit | Repo root also lacks root LICENSE |
| Anthropic design-critique | Apache-2.0 | `anthropic-kwp/LICENSE` | Skill imported; shared `CONNECTORS.md` copied |
| web-accessibility | MIT | `UPSTREAM_LICENSE.md` copied into skill | From magnus919/agent-skills repo LICENSE |
| threejs-skills (10) | MIT | `skills/external/threejs/UPSTREAM_LICENSE` | Repo LICENSE |
| R3F reference | MIT | `.../UPSTREAM_LICENSE` | shre-skills repo LICENSE |
| gsap-skills (5) | MIT | `skills/external/gsap/UPSTREAM_LICENSE` | Repo LICENSE |
| blender-skills (15) | MIT | `skills/external/blender/UPSTREAM_LICENSE` | Repo LICENSE |
| img2threejs | Apache-2.0 | `skills/external/img2threejs/LICENSE` | SKILL frontmatter also declares Apache-2.0 |

---

## Copied resources (high level)

### Frontend
- `openai-frontend-app-builder/` — SKILL.md, references/, agents/
- `openai-frontend-testing-debugging/` — SKILL.md, agents/
- `anthropic-design-critique/` — SKILL.md
- `web-accessibility/` — SKILL.md, references/, assets/, evals/, README.md
- Shared: `skills/external/CONNECTORS.md` (required by design-critique upstream link)

### Three.js + R3F
- 10 selected skills under `skills/external/threejs/<name>/`
- R3F merge reference: `skills/external/threejs/references/react-three-fiber-production-rules/`

### GSAP
- 5 selected skills under `skills/external/gsap/<name>/`

### Blender
- 15 selected skills under `skills/external/blender/<name>/`
- Shared references: `skills/external/blender/references/` (9 files — asset-pipeline, mcp-integration, validation-checklist, etc.)

### img2threejs (minimum operational subset)
- `SKILL.md`, `forge/`, `grimoire/`, `docs/`, `scripts/`, `steps.json`, `.gitignore`, `LICENSE`
- **Not copied:** full repo root extras (`integrations/`, `assets/` gallery, plugin packaging) — not required for core workflow per import inspection

---

## Script review

| Domain | Scripts | Review status |
|---|---|---|
| Frontend / Three.js / GSAP / Blender | **0** executable scripts in imported subset | n/a |
| img2threejs | **213** Python/shell files | **Static review complete — not executed** |

### img2threejs notable scripts (not executed)

| Script | Language | Purpose (declared) | FS | Network | Subprocess | Review |
|---|---|---|---:|---:|---:|---|
| `forge/*.py`, `forge/stage*/*.py` | Python | Workflow state, spec/build/review pipeline | ✓ | some modules | some modules | Inspected; stdlib-oriented tooling |
| `scripts/capture_threejs_playwright.py` | Python | Browser capture bridge | ✓ | — | ✓ | **Not executed** — requires Node/Playwright setup |
| `scripts/issue_triage.py` | Python | GitHub issue triage helper | ✓ | ✓ | — | **Not executed** — network-capable |
| `scripts/character_audit.sh` | Shell | Audit helper | — | — | — | **Not executed** |

No installation scripts were executed during import.

---

## Upstream test evidence (img2threejs)

Command (inspection only, at pinned snapshot):

```text
python -m pytest forge/tests/test_workflow_state.py forge/tests/test_pipeline.py -q
```

Result at pinned commit `d6815db7`:

- **83 passed**
- **2 failed**
  1. `test_cs2_assessment_embeds_local_spec_search_results` — `UnicodeDecodeError` on Windows cp1252 (environment encoding)
  2. `test_cs2_textures_gitignored_and_never_tracked` — failed before `.gitignore` copied; **passes after** `.gitignore` included in import subset

**Operational classification:** `restricted`  
Reason: large scripted workflow surface; Playwright bridge not validated here; one environment-sensitive upstream test failure recorded.

---

## Missing / broken references

| Item | Status |
|---|---|
| Anthropic `../../CONNECTORS.md` | **Resolved** — copied to `skills/external/CONNECTORS.md` |
| Blender `../references/*` | **Resolved** — shared `blender/references/` directory |
| img2threejs runtime state `.img2threejs/state.json` | **Expected runtime artifact** — created during project use, not import |
| OpenAI frontend LICENSE file | **Missing at source** — flagged `LICENSE_REVIEW_REQUIRED` |

No broken required static files detected by Phase B validator after import.

---

## Local modifications / fork notes

- No content edits to upstream `SKILL.md` bodies
- Added upstream license copies where repo-level LICENSE applies (`UPSTREAM_LICENSE*`)
- img2threejs imported as immutable reviewed snapshot, not live `main`
- R3F stored under `threejs/references/` as **merge reference only** — must not become competing authority

---

## Operational status by entry type

| Status | Count | IDs |
|---|---:|---|
| operational | 31 | EXT-FE-02, EXT-3DWEB-01..10, EXT-MOTION-01..05, EXT-BLD-01..15 |
| reference | 4 | EXT-FE-01, EXT-DES-01, EXT-A11Y-01, EXT-R3F-01 |
| restricted | 1 | EXT-IMG3D-01 |
| blocked | 0 | — |

---

## Validation evidence

```text
python validation/validate_foundation.py     → PASSED
python validation/validate_external_skills.py → PASSED (36 entries)
```

Phase A re-validation after Phase B imports: **PASSED**

---

## Phase boundary confirmation

- Proprietary ACOS skills (`skills/acos/*/SKILL.md`): **NOT STARTED**
- Blender MCP configuration: **NOT STARTED**
- Browser / Playwright tool configuration: **NOT STARTED**
- Benchmark / project implementation: **NOT STARTED**

---

## Next action

**Await human review/authorization for Phase C.**
