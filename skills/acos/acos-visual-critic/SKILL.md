---
name: acos-visual-critic
description: Activate after rendered or browser visual evidence exists for independent critique of hierarchy, composition, spacing, typography, polish, and viewport-specific visual defects. Do not activate for concept-only review, code-only inspection when render evidence is required, or when the same agent authored the work and no independent critic pass is possible.
---

# acos-visual-critic (ACOS-10)

Independent visual execution critic. Evaluates **what the user actually sees** in rendered or browser evidence — not creative thesis, not 3D geometry fidelity (unless surfaced as a visual integration defect), not functional correctness.

Authoritative policy references: `core/QUALITY_GATES.md`, `core/WORKFLOW.md`, `core/ROUTING.md`.

---

## 1. Purpose

Provide evidence-based, independent criticism of visual execution quality across applicable viewports and states. Identify concrete visual defects, assign severity, and route each defect to the responsible upstream owner so creators cannot self-approve visual quality.

This skill owns **visual execution critique**, not creative originality, not 3D-specific geometry/material analysis, and not final ship/no-ship authority.

---

## 2. Activation / trigger conditions

Activate when **all** of the following are true:

1. Meaningful visual output exists or is claimed complete for the evaluated scope (DOM UI, composed layouts, integrated WebGL canvas regions, motion frames when the critique target is visual state).
2. **Rendered or browser evidence** is available or can be collected at required viewports/states per project constraints.
3. An independent evaluation pass is required — typically after integration and before or alongside final quality gate.
4. The task requires judgment on hierarchy, composition, spacing, typography, balance, rhythm, polish, consistency, integration appearance, or viewport-specific visual problems.

Typical routing triggers:

- Post-integration visual QA phase in canonical workflow.
- Explicit request for independent visual critique.
- Upstream handoff marked `ready_for_visual_critique: true` with evidence attached.
- Quality gate requests visual critic findings before aggregation.

---

## 3. Do-not-activate conditions

Do **not** activate when:

- Only specifications, wireframes, or code exist and **no render/browser evidence** is available or obtainable — route as `BLOCKED / INSUFFICIENT EVIDENCE` via quality gate instead of inventing a visual verdict.
- The evaluating agent is the **sole creator** of the visual work and no independent critic boundary exists — escalate to quality gate as insufficient independence; do not self-approve.
- The primary question is **concept originality, brand distinctiveness, or creative thesis** — use `acos-creative-critic`.
- The primary question is **3D geometry, materials, lighting credibility, camera, or scene coherence** with 3D output present — use `acos-3d-critic` (may supplement this skill for integration-only visual seams).
- The primary question is **journey, IA, or interaction flow** without visual execution evidence — use `acos-experience-architect` or functional QA routes.
- The task is **final ship/no-ship aggregation** — use `acos-quality-gate`.
- The user only wants **implementation fixes** without critique — route to appropriate production skill; do not masquerade as critic.

---

## 4. Responsibility boundary

### Owns

- Independent critique of rendered/browser evidence for:
  - visual hierarchy and reading order
  - composition and balance
  - spacing and alignment consistency
  - typography execution (size, weight, line length, contrast within visual system)
  - visual rhythm and density
  - polish (edge cases, unfinished states, visual roughness)
  - cross-component visual inconsistency
  - DOM/WebGL/canvas **visual integration** defects visible in render evidence
  - viewport-specific visual breakage (required breakpoints, orientations, states)
  - motion **as visible visual outcome** when evaluating captured frames or paused states (not motion intent authoring)
- Defect severity classification: `critical`, `major`, `minor`, `observation`
- Responsible upstream owner assignment per defect
- Structured visual critique artifact and handoff

### Does NOT own

- Creative thesis, originality, or anti-generic judgment (`acos-creative-critic`, `acos-anti-generic-design`)
- Art direction specification or redesign (`acos-art-director`)
- 3D-specific geometry/material/lighting/camera credibility (`acos-3d-critic`)
- Responsive strategy authorship (`acos-responsive-art-direction`)
- Performance measurement (`acos-webgl-performance`, engineering QA)
- Accessibility compliance testing (external accessibility skills / functional QA)
- Final APPROVE / REJECT / BLOCKED decision (`acos-quality-gate`)
- Implementing fixes or rewriting UI code

---

## 5. Required inputs

Minimum inputs before proceeding:

| Input | Required | Notes |
|---|---|---|
| Project brief or normalized scope | Yes | Defines what "done" means visually |
| Art direction artifact or equivalent visual rules | When exists | Baseline for consistency checks |
| Render/browser evidence | **Yes** | Screenshots, captures, or inspectable live URL with stated viewport/DPR/state |
| Viewport/state matrix | When applicable | Which breakpoints, themes, interaction states were evaluated |
| Creative direction summary | Recommended | Distinguish execution vs concept issues; do not re-litigate thesis |
| Reference contract | When references exist | For integration mismatch visible in renders only |
| Prior critic reports | Optional | Avoid duplicate findings; verify fixes |

If required visual evidence is missing, **stop** and emit handoff with `status: blocked_insufficient_evidence` to `acos-quality-gate`. Do not infer visual quality from source code alone.

---

## 6. Exact procedure / workflow

Execute in order. Do not skip evidence verification.

### Step 1 — Independence check

1. Confirm this pass is independent from the creating agent/session when possible.
2. If independence cannot be established, record `open_risks: [creator_self_review_only]` and route to quality gate — do not issue `visual_pass: true` as sole authority.

### Step 2 — Evidence inventory

1. List all evidence artifacts: path/URL, viewport dimensions, DPR, theme, interaction state, capture timestamp if known.
2. Verify evidence covers **required viewports/states** from project constraints.
3. If coverage is incomplete, stop at Step 8 with blocked status and specify missing captures.

### Step 3 — Establish evaluation frame

1. Load art direction / visual rules if provided.
2. Define evaluation units (pages, scenes, components, flows) without expanding scope.
3. Ignore creative originality unless it manifests as visual execution confusion — flag for creative critic instead.

### Step 4 — Systematic visual scan

For each evaluation unit and viewport, inspect evidence for:

1. **First-read hierarchy** — Is focal order intentional and stable?
2. **Composition** — Balance, grouping, negative space, alignment grids.
3. **Spacing** — Internal padding, section rhythm, inconsistent gaps.
4. **Typography** — Scale steps, line length, truncation, weight misuse.
5. **Consistency** — Repeated patterns diverging without justification.
6. **Polish** — Half-finished edges, clipping, blur artifacts, placeholder styling.
7. **Integration** — Canvas/DOM seams, z-index stacking, overlay misregistration visible in render.
8. **State coverage** — Empty, loading, error, hover/focus if required and capturable visually.

### Step 5 — Defect recording

For each defect:

```yaml
defect_id: VC-###
description: specific observable issue in evidence
severity: critical | major | minor | observation
evidence_ref: artifact id + viewport/state
location: screen region / component / flow step
owner: upstream skill or role (see routing table)
correction: what must change visually
retest: viewport/state to re-capture after fix
```

### Step 6 — Severity rules

- **critical** — Required viewport unusable, primary content illegible, broken layout blocking comprehension, visible integration failure blocking task.
- **major** — Clear hierarchy/spacing/typography failure on required viewport; inconsistent system application; polish gap that undermines perceived quality on primary surfaces.
- **minor** — Localized inconsistency or polish issue not blocking primary tasks.
- **observation** — Improvement opportunity; not a fail on its own.

### Step 7 — Owner routing

| Defect type | Primary owner |
|---|---|
| Weak hierarchy, composition, type system execution | `acos-art-director` |
| Layout/spacing breakdown at specific breakpoint | `acos-responsive-art-direction` |
| Visual integration seam (DOM/WebGL/canvas) | engineering integration route + `acos-art-director` if system-level |
| Supposed 3D element looks wrong in form/material/light | `acos-3d-critic` (if 3D output exists) |
| Motion causes visual jank or unreadable states | `acos-motion-director` |
| Concept makes visual system incoherent | `acos-creative-critic` (not visual pass) |
| Generic trope visible but concept issue | `acos-creative-critic` / `acos-anti-generic-design` |

### Step 8 — Verdict and handoff

1. Compute `visual_critique_status`: `pass` | `pass_with_observations` | `fail` | `blocked_insufficient_evidence`
2. `fail` if any **critical** or policy-defined **major** threshold defects remain unresolved.
3. Emit structured critique artifact and YAML handoff (Section 9).
4. Never emit final ship approval — that belongs to `acos-quality-gate`.

---

## 7. Required outputs / deliverables

### Primary artifact: Visual Critique Report

Structured report containing:

- evidence inventory with coverage matrix
- per-defect records (Step 5 schema)
- summary counts by severity
- `visual_critique_status`
- explicit list of viewports/states requiring re-test after corrections

### Minimum handoff block

See Section 9.

---

## 8. Rejection / failure conditions

This skill **fails its own contract** (must not complete as valid critic output) when:

- Render/browser evidence was not used for visual claims.
- Defects lack evidence references or observable descriptions.
- Severity or owner routing is omitted.
- Output approves visual quality while critical/major defects are documented.
- Output redesigns the entire visual system by preference without defect linkage.
- Output conflates creative originality judgment with visual execution scoring.
- Output issues `APPROVE` for project ship — forbidden.

Treat as **critique fail** (route back to creators) when evaluated evidence shows unresolved critical/major visual defects per Step 6.

---

## 9. Handoff contract

Every completion must include a machine-readable handoff. Omit inapplicable fields; never leave status implicit.

```yaml
handoff:
  skill: acos-visual-critic
  status: pass | pass_with_observations | fail | blocked_insufficient_evidence
  inputs_used:
    - brief_ref
    - art_direction_ref
    - evidence_artifacts
  decisions:
    visual_critique_status: pass | pass_with_observations | fail | blocked_insufficient_evidence
    defect_count:
      critical: 0
      major: 0
      minor: 0
      observation: 0
  constraints:
    - evaluated_viewports_only
    - independent_critic_required
  open_risks:
    - missing_viewport_evidence
    - creator_self_review_only
  evidence:
    - id: EV-001
      type: browser_capture | render | recording_frame
      viewport: "1440x900"
      state: default
      uri_or_path: "<reference>"
  deliverables:
    - visual_critique_report
    - defect_register
  next_owner: acos-quality-gate
  rejection_route:
    - defect_id: VC-001
      owner: acos-art-director
      severity: major
      correction: "<required visual change>"
      retest: "<viewport/state>"
```

When `status: fail`, set `next_owner` to the highest-severity defect owner for correction loop; always copy `acos-quality-gate` when gate aggregation is pending.

When `status: blocked_insufficient_evidence`, set `next_owner: acos-quality-gate` with `rejection_route: []` and list missing evidence in `open_risks`.

---

## 10. QA / evaluation contract

### Scoring dimensions (when applicable)

Align with `core/QUALITY_GATES.md` visual dimensions — score only from evidence:

- composition (0–10)
- typography (0–10)
- visual hierarchy (0–10)
- responsive art direction appearance (0–10 when multi-viewport evidence exists)

Do not average scores into ship approval; scores inform gate aggregation.

### Pass criteria

- Required viewports/states covered by evidence.
- All critical defects = 0 for `pass`.
- Major defects = 0 for `pass`; allowed for `pass_with_observations` only if project policy explicitly permits waivable majors (document waiver rationale — gate decides).

### Independence criteria

- Critique references evidence IDs, not implementation intent.
- No phrase equivalent to "code looks fine therefore visual pass."

---

## 11. Evidence requirements

| Claim type | Required evidence |
|---|---|
| Hierarchy/composition/spacing/type defect | Browser/render capture at stated viewport |
| Viewport-specific breakage | Side-by-side or matrix captures per required breakpoint |
| Integration seam | Capture showing DOM/canvas boundary |
| Polish issue | Zoomed capture or annotated region |
| Motion-related visual defect | Frame capture or paused state screenshot |

**Forbidden:** approving visual quality from CSS/component source alone when render evidence is required.

Distinguish:

- **planning evidence** — art direction specs (inputs only)
- **implementation evidence** — code (not sufficient alone)
- **visual evidence** — renders/browser captures (**required**)
- **runtime evidence** — live URL inspection logs (supplement only)

---

## 12. Memory interaction

Phase C: do not write real memory records.

### May read later (when populated)

- `memory/projects/` — prior visual defects and fix outcomes for same project
- `memory/failures/` — recurring visual failure patterns (scoped)

### May propose for memory (via `acos-failure-learning` only)

- Recurring spacing/hierarchy failure patterns with evidence and scope tags
- Viewport-specific regression patterns

### Must NOT

- Promote one project's visual style as global taste
- Store critic scores as permanent house-style preferences
- Fabricate historical defect records

Promotion lifecycle: `observation → project-rule → candidate-global → validated-global → deprecated` per `core/MEMORY_POLICY.md`.

---

## 13. Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-art-director` | Upstream visual rules; receives hierarchy/composition/type execution defects |
| `acos-responsive-art-direction` | Upstream breakpoint strategy; receives viewport visual failures |
| `acos-creative-critic` | Parallel critic; receives concept/generic issues surfaced during visual review |
| `acos-3d-critic` | Parallel critic when 3D present; receives geometry/material/lighting credibility issues |
| `acos-motion-director` | Receives motion-caused visual readability defects |
| `acos-quality-gate` | Downstream aggregator; receives this handoff; sole final status authority |
| `acos-failure-learning` | Downstream after observed failures; consumes defect patterns with evidence |
| External frontend/testing skills | May supply captures; do not replace independent ACOS visual critique |

**Overlap prevention:** This skill judges **rendered visual execution**. Creative critic judges **concept**. 3D critic judges **3D credibility**. Quality gate **aggregates**; never duplicate their primary ownership.

---

## 14. Non-goals

- Not a creative director, art director, or implementer
- Not a pixel-perfect clone checker against references
- Not a personal aesthetic preference engine
- Not a replacement for browser automation tools — tools collect evidence; this skill judges it
- Not a final quality gate or ship authority
- Not a domain-specific style enforcer (no industry or brand defaults)
- Not an accessibility audit (may note visible contrast issues; route formal a11y QA separately)

---

## Reference

- `core/QUALITY_GATES.md` — dimensions and hard reject alignment
- `core/WORKFLOW.md` — visual QA phase placement
- `core/ROUTING.md` — defect routing patterns
