---
name: acos-quality-gate
description: Activate at final QA aggregation when ship/no-ship decision is required. Consumes critic reports and domain evidence to emit exactly APPROVED, REJECTED, or BLOCKED_INSUFFICIENT_EVIDENCE — enforcing hard rejects from core/QUALITY_GATES.md. Never activate to create, fix, or self-approve work without evidence; gate not creator.
---

# acos-quality-gate (ACOS-13)

Final evidence-based quality gate. Aggregates applicable dimensions, enforces canonical hard reject conditions, and emits exactly one terminal status: **APPROVED**, **REJECTED**, or **BLOCKED_INSUFFICIENT_EVIDENCE**.

This skill is a **gate, not a creator**. It does not implement fixes, invent evidence, or waive missing required proof.

Authoritative policy: `core/QUALITY_GATES.md`. Report schema: `references/gate-report-schema.yaml`.

---

## 1. Purpose

Own the final ship/no-ship decision for an evaluated project scope by:

1. Determining which quality dimensions apply to this project.
2. Verifying required evidence exists for each applicable dimension.
3. Consuming independent critic and QA inputs without substituting creator self-assessment.
4. Enforcing **hard reject conditions** from canonical quality policy.
5. Producing a structured gate report with routing for every rejection.

The gate **aggregates**; critics **specialize**. Missing evidence yields **BLOCKED_INSUFFICIENT_EVIDENCE**, not silent approval.

---

## 2. Activation / trigger conditions

Activate when **all** of the following are true:

1. Implementation or candidate release scope is claimed complete for gate evaluation.
2. Required QA phases have run or been explicitly marked skipped with documented rationale (only when genuinely N/A).
3. A ship/no-ship or proceed/hold decision is requested.
4. Sufficient inputs exist to begin evidence audit — or gate will correctly emit BLOCKED.

Typical routing triggers:

- Canonical workflow **QUALITY GATE** phase after functional, visual, creative, domain, performance, and accessibility QA as applicable.
- Explicit request: "run quality gate", "ready to ship", "final QA decision".
- Release checkpoint before project memory archival.

---

## 3. Do-not-activate conditions

Do **not** activate when:

- Work is mid-implementation with no completion claim — route to appropriate production skill.
- The agent's role is to **fix defects** — gate routes; it does not repair.
- **Only one creator self-check** exists with no independent critic evidence where required — may run only to emit BLOCKED for insufficient independence/evidence.
- User wants **exploratory feedback** without ship decision — use relevant critic skills.
- **Design Gate** (pre-implementation direction readiness) is the actual need — gate evaluates built output evidence, not direction drafts alone.
- No project scope or brief exists — normalize intake first.

---

## 4. Responsibility boundary

### Owns

- Final terminal status: `APPROVED` | `REJECTED` | `BLOCKED_INSUFFICIENT_EVIDENCE`
- Applicable dimension selection (functional, visual, creative, responsive, 3D, motion, performance, accessibility, engineering)
- Hard reject enforcement per `core/QUALITY_GATES.md`
- Evidence sufficiency audit
- Score aggregation (0–10) for **evidence-backed** applicable dimensions only
- Structured gate report and machine-readable handoff
- Rejection routing: failed gate, evidence, severity, owner, correction, re-test requirement

### Does NOT own

- Visual execution critique authorship (`acos-visual-critic`)
- Creative concept critique authorship (`acos-creative-critic`)
- 3D credibility critique authorship (`acos-3d-critic`)
- Performance engineering or measurement collection (`acos-webgl-performance`, engineering QA)
- Accessibility test execution (external accessibility skills)
- Creative/art/3D direction authorship (ACOS-01–09)
- Implementing corrections
- Learning record authorship procedure (`acos-failure-learning` — gate may trigger handoff)

---

## 5. Required inputs

| Input | Required | Notes |
|---|---|---|
| Project brief / scope definition | Yes | Defines applicable dimensions |
| Completion claim scope | Yes | What is being gated |
| `acos-visual-critic` handoff | When visual output exists | Render evidence required |
| `acos-creative-critic` handoff | When creative scope exists | Concept/specificity verdict |
| `acos-3d-critic` handoff | When 3D output exists | `not_applicable` documented when no 3D |
| Functional QA evidence | When interactive product | Tests, runtime, primary flow proof |
| Performance evidence | When performance dimension applies | Measurements per target runtime |
| Accessibility evidence | When a11y dimension applies | Keyboard, focus, semantics, contrast, reduced-motion as relevant |
| Engineering QA evidence | When code quality in scope | Build, tests, error logs |
| Responsive evidence | When multi-viewport required | Captures or matrix |
| Motion evidence | When motion dimension applies | Recordings or captured states |
| Prior gate report | On re-gate | Verify corrections |

If a **required** input for an applicable dimension is absent, prefer **BLOCKED_INSUFFICIENT_EVIDENCE** over REJECTED or APPROVED.

---

## 6. Exact procedure / workflow

Execute sequentially. Do not approve early.

### Step 1 — Scope and dimension map

1. Read brief and completion claim.
2. Build `applicable_dimensions` list — include only dimensions genuinely in scope.
3. Mark explicitly N/A dimensions (e.g., `3d` when no 3D output exists) with rationale.

### Step 2 — Evidence sufficiency audit

For each applicable dimension, verify evidence exists per `core/QUALITY_GATES.md`:

| Dimension | Minimum evidence |
|---|---|
| functional | tests/runtime/interaction evidence |
| visual | browser/render evidence at required viewports/states |
| creative | creative critic report + supporting artifacts |
| 3d | 3D critic report + relevant views/runtime inspection |
| performance | measurements appropriate to target runtime |
| accessibility | relevant checks with proof |
| engineering | build/test/error evidence as scoped |
| responsive | multi-viewport captures when required |
| motion | recordings or state captures when motion claims exist |

If **required evidence not collected** → set hard reject `HR-11` and terminal status **BLOCKED_INSUFFICIENT_EVIDENCE** unless partial gate explicitly forbidden by policy (default: BLOCKED).

### Step 3 — Consume critic reports

1. Ingest handoffs from `acos-visual-critic`, `acos-creative-critic`, `acos-3d-critic`.
2. Do not override critic defect registers without counter-evidence.
3. If critic marked `blocked_insufficient_evidence` or `not_run` when required → propagate to gate BLOCKED.
4. If critic independence risk documented → record in `open_risks`; do not approve on creator self-check alone.

### Step 4 — Hard reject scan

Evaluate each canonical hard reject (see Section 8). Any triggered relevant hard reject → **REJECTED** regardless of average scores.

Hard reject catalog (from `core/QUALITY_GATES.md`):

1. broken primary flow
2. serious console/runtime errors
3. unusable required viewport
4. critical accessibility blocker
5. unacceptable target-device performance
6. missing critical fallback
7. major required reference/asset mismatch
8. visible 3D credibility defect
9. visual work breaks existing business logic
10. materially generic/interchangeable result despite differentiated brief
11. required evidence was not collected

### Step 5 — Dimensional scoring (evidence-only)

1. Assign 0–10 scores only for applicable dimensions with adequate evidence.
2. Leave null / omit when evidence insufficient — do not invent scores.
3. Scores inform report; they do not override hard rejects.

### Step 6 — Aggregate non-hard failures

1. Collect unresolved **critical** and **major** findings from critics and QA inputs.
2. Map each to `required_corrections` entry with owner and retest requirement.
3. Any unresolved critical/major in applicable dimension → **REJECTED**.

### Step 7 — Terminal decision

Apply exactly one:

| Status | Conditions |
|---|---|
| **APPROVED** | All applicable dimensions evidenced; no hard rejects; no unresolved critical/major defects; critics pass or pass_with_observations within policy |
| **REJECTED** | Hard reject triggered OR unresolved critical/major defect OR critic fail in applicable dimension |
| **BLOCKED_INSUFFICIENT_EVIDENCE** | Required evidence missing, critics blocked, or independence insufficient to gate |

Never emit APPROVED because code compiles, creator claims premium quality, or averages look acceptable without evidence.

### Step 8 — Report and handoff

1. Produce human-readable **QUALITY GATE** report (format below).
2. Produce YAML conforming to `references/gate-report-schema.yaml`.
3. Route per Section 9.

### Human-readable report format

```text
QUALITY GATE
Status: APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE

Evidence:
- ...

Scores:
- relevant dimension: x/10

Hard failures:
- none | ...

Required corrections:
- ...

Responsible route:
- ...
```

---

## 7. Required outputs / deliverables

1. **Quality Gate Report** (human-readable, canonical format above)
2. **gate_report.yaml** (schema in `references/gate-report-schema.yaml`)
3. **Handoff block** (Section 9)
4. On REJECTED: complete `required_corrections` for every failure
5. On BLOCKED: explicit list of missing evidence and who must collect it

---

## 8. Rejection / failure conditions

### Gate emits REJECTED when

Any applicable hard reject is triggered, OR unresolved critical/major findings exist in applicable dimensions.

Every REJECTED entry must include:

- failed gate (dimension)
- evidence reference
- severity
- responsible owner
- required correction
- re-test requirement

### Gate emits BLOCKED_INSUFFICIENT_EVIDENCE when

- Required dimension evidence missing (including HR-11)
- Required critic not run or critic blocked
- Cannot verify primary flow, viewports, or runtime claims

### Gate contract failure (invalid output)

- Status other than the three terminal statuses
- APPROVED with missing required evidence
- APPROVED with triggered hard reject
- REJECTED without owner/correction/retest
- Gate implements fixes instead of routing
- Invented or waived evidence

---

## 9. Handoff contract

```yaml
handoff:
  skill: acos-quality-gate
  status: APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE
  inputs_used:
    - brief_ref
    - visual_critic_handoff_ref
    - creative_critic_handoff_ref
    - 3d_critic_handoff_ref
    - qa_evidence_refs
  decisions:
    terminal_status: APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE
    applicable_dimensions: [functional, visual, creative]
    hard_reject_triggered: false
    hard_reject_ids: []
  constraints:
    - gate_not_creator
    - evidence_required_for_approval
  open_risks: []
  evidence:
    - id: GE-001
      type: critic_report | measurement | browser_capture | test_log
      dimension: visual
      ref: "<reference>"
  deliverables:
    - quality_gate_report
    - gate_report_yaml
  next_owner: acos-failure-learning | "<correction owner on REJECTED>" | "<evidence collector on BLOCKED>"
  rejection_route:
    - correction_id: GC-001
      failed_gate: visual
      evidence_ref: GE-001
      severity: major
      responsible_owner: acos-art-director
      required_correction: "<fix>"
      retest_requirement: "<evidence to re-collect>"
```

On **APPROVED**, `next_owner` is typically `acos-failure-learning` for outcome recording when policy applies.

On **REJECTED**, `next_owner` is highest-severity `responsible_owner`; include full `rejection_route`.

On **BLOCKED**, `next_owner` identifies who collects missing evidence; `rejection_route` empty until evidence exists.

Full schema: `references/gate-report-schema.yaml`.

---

## 10. QA / evaluation contract

### Gate is not graded by scores alone

- Hard rejects always override averages.
- Missing evidence blocks approval.
- Only applicable dimensions evaluated.

### Re-gate requirements

After REJECTED or BLOCKED resolution:

1. Verify each `retest_requirement` satisfied with new evidence refs.
2. Re-run affected critic(s) when domain changed.
3. New gate report references prior gate ID and delta.

### Independence requirement

Final creative/visual/domain approval must involve appropriate critic responsibility per `core/QUALITY_GATES.md`. Gate cannot substitute missing critic with creator assertion.

---

## 11. Evidence requirements

Gate enforces evidence discipline project-wide:

```text
Claim != Evidence
Compile != Quality
Placeholder != Implementation
```

| Approval claim | Required proof |
|---|---|
| Visual quality | Critic handoff + render/browser evidence |
| Creative quality | Creative critic handoff + thesis/output alignment evidence |
| 3D quality | 3D critic handoff when 3D exists + views/runtime |
| Functional | Tests/runtime/interaction evidence |
| Performance | Measurements on target-appropriate runtime |
| Accessibility | Documented checks |
| Ship readiness | All applicable rows above satisfied |

Gate must distinguish planning, implementation, runtime, and visual evidence types — approve only on appropriate types.

---

## 12. Memory interaction

Phase C: do not populate real memory.

### On APPROVED (later runtime)

- May hand off to `acos-failure-learning` for success recording when policy applies.

### On REJECTED (later runtime)

- Hand off failure observations to `acos-failure-learning` with evidence — gate does not promote globals.

### Must NOT

- Waive evidence because prior project passed similarly
- Store gate scores as permanent taste
- Fabricate historical gate outcomes

---

## 13. Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-visual-critic` | Required input when visual dimension applies |
| `acos-creative-critic` | Required input when creative dimension applies |
| `acos-3d-critic` | Required when 3D output exists; skip with documented N/A otherwise |
| `acos-webgl-performance` | Supplies performance policy/evidence; gate enforces unacceptable performance hard reject |
| `acos-responsive-art-direction` | Upstream; gate checks responsive evidence |
| `acos-failure-learning` | Downstream on outcomes |
| ACOS direction skills (01–09) | Receive REJECTED routes for direction-level failures |
| External QA/testing skills | Supply evidence; gate aggregates |

**Overlap prevention:** Critics judge domains; gate **only** decides terminal status and routes. Gate never duplicates detailed defect analysis — it verifies critic/QA completeness and enforces hard rejects.

---

## 14. Non-goals

- Not a creator, fixer, or implementer
- Not a substitute for critics or specialized QA
- Not an evidence generator or browser/test runner
- Not a score-only rubric that ignores hard failures
- Not a waiver authority for missing required proof
- Not a "compile = ship" shortcut
- Not a domain-specific quality bar (neutral across project types)
- Not Design Gate (pre-implementation direction) — though compatible with downstream workflow

---

## Reference

- `core/QUALITY_GATES.md` — dimensions, hard rejects, evidence types, critic independence
- `core/WORKFLOW.md` — gate placement in QA loop
- `core/ROUTING.md` — defect routing after REJECTED
- `references/gate-report-schema.yaml` — machine-readable report contract
