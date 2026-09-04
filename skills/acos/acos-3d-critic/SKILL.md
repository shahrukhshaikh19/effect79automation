---
name: acos-3d-critic
description: Activate only when actual 3D output exists (runtime scene, renders, or inspectable 3D views) and independent critique of silhouette, geometry, materials, lighting, camera, scale, and DOM/3D integration is required. Do not activate for DOM-only applications, code-only review without 3D evidence, or pixel-level 2D layout QA.
---

# acos-3d-critic (ACOS-12)

Independent 3D credibility critic. Evaluates **rendered or runtime 3D evidence** for form, materials, lighting, camera, scale, scene coherence, and integration with surrounding interface — only when 3D output actually exists.

Authoritative policy references: `core/QUALITY_GATES.md`, `core/WORKFLOW.md`, `core/ROUTING.md`.

---

## 1. Purpose

Provide evidence-based, independent criticism of 3D-specific quality and credibility. Identify concrete 3D defects, assign severity, and route each defect to the responsible upstream 3D creative, technical, or art-direction stage.

This skill activates **conditionally** — only when 3D output is present. It does not replace visual critic for general 2D layout, nor creative critic for thesis judgment.

---

## 2. Activation / trigger conditions

Activate when **all** of the following are true:

1. **Actual 3D output exists** — runtime WebGL/Three.js/R3F scene, authored asset in context, or multi-angle renders of 3D content integrated in the deliverable.
2. 3D is in scope for the project phase being evaluated (not merely planned).
3. Independent 3D credibility review is required before or during final gate.
4. **Rendered or runtime 3D evidence** is available or obtainable (multiple angles/views when credibility requires).

Typical routing triggers:

- Post-integration 3D QA in canonical workflow.
- After cinematic 3D direction + production integration.
- Quality gate requests 3D critic findings when 3D dimension is applicable.
- Visual critic escalates visible 3D credibility issues.

---

## 3. Do-not-activate conditions

Do **not** activate when:

- The project is **DOM-only** with no 3D output — not applicable; skip entirely.
- 3D is proposed in direction docs but **not yet implemented** — route to production or block at gate for missing evidence.
- Only **source code or scene files** exist without renders/runtime views — insufficient; emit blocked handoff unless live inspection evidence can be collected.
- The task is **general 2D visual QA** — use `acos-visual-critic`.
- The task is **creative thesis or genericness** — use `acos-creative-critic`.
- The task is **WebGL performance budgets/measurements** — use `acos-webgl-performance` and engineering QA.
- The task is **modeling, lookdev, or scene authoring** — external Blender/Three.js production skills.
- The evaluating agent is the **sole 3D author** without independence — escalate; do not self-approve 3D credibility.
- The task is **final ship decision** — use `acos-quality-gate`.

---

## 4. Responsibility boundary

### Owns

Independent critique of rendered/runtime 3D evidence for:

- silhouette and form readability
- proportion and scale believability
- geometry defects (holes, shading breaks, bad normals, visible low-poly errors where fidelity is required)
- material response (albedo, roughness, metalness, transparency, texture resolution)
- lighting believability and shadow/reflection coherence
- camera framing, focal intent, and motion sickness risk from camera behavior (when visible in evidence)
- object intersections, floating, attachment, and grounding errors
- scene coherence (asset style consistency, staging clarity)
- DOM/3D integration (scale, parallax, masking, depth ordering, interaction handoff)
- reference mismatch when a **reference contract** exists for 3D fidelity

### Does NOT own

- 3D creative direction authorship (`acos-cinematic-3d-director`)
- Modeling, rigging, baking, export (`external Blender skills`)
- Scene implementation (`external Three.js/R3F skills`)
- Performance optimization policy (`acos-webgl-performance`)
- 2D typography/spacing/hierarchy (`acos-visual-critic`)
- Concept originality (`acos-creative-critic`)
- Final APPROVE / REJECT / BLOCKED (`acos-quality-gate`)
- Fixing geometry, shaders, or assets

---

## 5. Required inputs

| Input | Required | Notes |
|---|---|---|
| Evidence of 3D output | **Yes** | Renders, runtime captures, inspectable URL with scene state |
| Multiple views/angles | When credibility requires | Front, side, detail, in-context |
| Cinematic 3D direction artifact | When exists | Intent for scale, camera, materials, staging |
| Reference contract | When references govern 3D | Allowed interpretation bounds |
| Art direction / integration rules | Recommended | DOM/3D cohesion expectations |
| Asset manifest | Recommended | Expected models, materials, LOD |
| Prior 3D critic report | Optional | Regression checking |

If 3D is claimed but evidence is missing, **stop** with `blocked_insufficient_evidence` to `acos-quality-gate`.

---

## 6. Exact procedure / workflow

### Step 1 — Applicability gate

1. Confirm 3D output exists in evidence — not merely planned.
2. If no 3D output, **do not run** this skill; document N/A for gate.
3. Confirm independence from 3D author when possible.

### Step 2 — Evidence inventory

1. List captures: view angle, viewport, DPR, scene state, lighting preset, animation frame if relevant.
2. Verify coverage of **in-context integration** (3D with surrounding UI/content).
3. If required views missing, block with explicit capture list.

### Step 3 — Establish 3D intent frame

1. Load cinematic 3D direction and reference contract if present.
2. Define fidelity tier expected (hero asset vs background prop) from brief/direction — without assuming domain defaults.

### Step 4 — Systematic 3D scan

For each scene/asset and view:

1. **Silhouette/form** — Readable shape at intended display size?
2. **Proportion/scale** — Believable relative to scene and UI context?
3. **Geometry** — Visible errors, broken shading, unintended holes, bad booleans?
4. **Materials** — Flat/incorrect response, texture swimming, resolution inadequate for camera distance?
5. **Lighting** — Inconsistent shadow direction, blown exposure, missing contact shadows?
6. **Reflections/refractions** — Broken or incoherent with environment?
7. **Camera** — Framing supports intent; distortion/uncomfortable angles?
8. **Physical errors** — Floating, intersection, misaligned attachments?
9. **Scene coherence** — Style/quality mismatch across assets?
10. **DOM/3D integration** — Scale seam, depth clash, interaction boundary visible in evidence?
11. **Reference mismatch** — When contract exists, material/form/camera deviation beyond allowed interpretation?

### Step 5 — Defect records

```yaml
defect_id: 3DC-###
description: observable 3D issue
severity: critical | major | minor | observation
evidence_ref: capture id + view/state
location: asset / scene region / integration boundary
owner: upstream skill or route
correction: required 3D or integration fix
retest: views/states to re-capture
```

### Step 6 — Severity rules

- **critical** — Visible 3D credibility defect on primary hero/content; broken integration blocking comprehension; major reference contract violation when 3D fidelity is required.
- **major** — Clear material/lighting/scale/camera failure on required views; floating/intersection errors in hero focus.
- **minor** — Background prop issues not affecting primary credibility.
- **observation** — Improvement opportunity.

Align **visible 3D credibility defect** with hard reject in `core/QUALITY_GATES.md`.

### Step 7 — Owner routing

| Defect type | Primary owner |
|---|---|
| Wrong 3D purpose, staging, camera intent | `acos-cinematic-3d-director` |
| Geometry/topology/authored asset defects | Blender production route / modeling owner |
| Shader/material/lighting implementation | Three.js/materials/lighting skills + integration engineering |
| Scale/integration with DOM | engineering integration + `acos-art-director` for visual cohesion |
| Performance-driven visual downgrade | `acos-webgl-performance` (if policy tradeoff documented) |
| Reference misinterpretation | `acos-reference-analysis` |
| 2D overlay/hierarchy issues only | `acos-visual-critic` |

### Step 8 — Verdict and handoff

1. Set `3d_critique_status`: `pass` | `pass_with_observations` | `fail` | `blocked_insufficient_evidence` | `not_applicable`
2. Use `not_applicable` only when gate confirms zero 3D output — document evidence check.
3. Hand off to `acos-quality-gate`; never final APPROVE alone.

---

## 7. Required outputs / deliverables

### Primary artifact: 3D Critique Report

- applicability confirmation
- evidence/view inventory
- defect register
- severity summary
- `3d_critique_status`
- retest view matrix

### Minimum handoff block

See Section 9.

---

## 8. Rejection / failure conditions

Contract failure when:

- Activated without 3D output evidence.
- Approves 3D from code/scene files alone without rendered/runtime proof.
- Performs modeling or fixes instead of routing.
- Replaces visual critic for pure 2D layout issues.
- Issues ship APPROVE — forbidden.

3D **fail** when unresolved critical/major 3D credibility defects remain.

---

## 9. Handoff contract

```yaml
handoff:
  skill: acos-3d-critic
  status: pass | pass_with_observations | fail | blocked_insufficient_evidence | not_applicable
  inputs_used:
    - cinematic_3d_direction_ref
    - reference_contract_ref
    - evidence_artifacts
  decisions:
    3d_critique_status: pass | pass_with_observations | fail | blocked_insufficient_evidence | not_applicable
    defect_count:
      critical: 0
      major: 0
      minor: 0
      observation: 0
  constraints:
    - requires_3d_output
    - independent_critic_required
  open_risks:
    - missing_angle_coverage
    - creator_self_review_only
  evidence:
    - id: 3DE-001
      type: runtime_capture | render | inspection_log
      view: front_in_context
      viewport: "1440x900"
      uri_or_path: "<reference>"
  deliverables:
    - 3d_critique_report
    - defect_register
  next_owner: acos-quality-gate
  rejection_route:
    - defect_id: 3DC-001
      owner: acos-cinematic-3d-director
      severity: major
      correction: "<required fix>"
      retest: "<views/states>"
```

When `not_applicable`, set `defect_count` all zero and document applicability check in `decisions`.

---

## 10. QA / evaluation contract

### Scoring dimensions (when applicable)

From `core/QUALITY_GATES.md`:

- 3D quality (0–10)
- 3D/UI integration (0–10)
- lighting/material quality (0–10)

Score only from 3D evidence. Gate aggregates.

### Pass criteria

- Required views and in-context integration covered.
- Zero critical defects for `pass`.
- Reference contract violations explicitly flagged when contract exists.

---

## 11. Evidence requirements

| Claim type | Required evidence |
|---|---|
| Geometry/material/lighting defect | Render or runtime capture from relevant angle |
| Scale/integration issue | In-context capture with UI/DOM visible |
| Camera/framing issue | Capture or recording showing framing |
| Reference mismatch | Contract + comparison captures |
| Floating/intersection | Capture highlighting contact region |

**Required for 3D dimension:** relevant views, geometry/material/lighting/camera checks, runtime inspection when applicable — per `core/QUALITY_GATES.md`.

Forbidden: approving 3D credibility from source alone.

---

## 12. Memory interaction

Phase C: do not write real memory records.

### May read later

- `memory/projects/` — prior 3D defects and fix evidence
- `memory/failures/` — recurring 3D credibility patterns

### May propose (via `acos-failure-learning`)

- Recurring material/lighting/integration failures with scope
- Model/tool-specific 3D authoring weaknesses with evidence

### Must NOT

- Store one project's 3D aesthetic as global default
- Fabricate defect history

---

## 13. Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-cinematic-3d-director` | Upstream 3D intent; receives direction-level routes |
| `acos-visual-critic` | Parallel; 2D layout vs 3D credibility split |
| `acos-webgl-performance` | Performance tradeoffs vs fidelity; not duplicate of credibility review |
| `acos-art-director` | Visual cohesion at integration boundary |
| `acos-reference-analysis` | Reference contract interpretation |
| External Blender/Three.js skills | Production execution; receive technical defect routes |
| `acos-quality-gate` | Aggregates 3D dimension when applicable |
| `acos-failure-learning` | Post-failure learning |

**Overlap prevention:** Only activates when **3D output exists**. Visual critic does not own geometry credibility. Performance skill does not waive visible 3D defects.

---

## 14. Non-goals

- Not a DOM-only reviewer
- Not a modeler, lighter, or shader author
- Not a WebGL performance engineer
- Not a creative thesis judge (unless reference contract scope)
- Not a replacement for Blender QA external skills — ACOS owns independent gate-facing 3D credibility verdict
- Not a final quality gate
- Not a default activator for all ACOS projects
- Not a domain-specific 3D style template

---

## Reference

- `core/QUALITY_GATES.md` — 3D dimensions and visible credibility hard reject
- `core/WORKFLOW.md` — Domain QA placement
- `core/ROUTING.md` — 3D production and critic routes
