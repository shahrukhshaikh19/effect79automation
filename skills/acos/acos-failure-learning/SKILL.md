---
name: acos-failure-learning
description: >
  Activate after observed project evidence exists — gate verdicts (APPROVE/REJECT/BLOCKED),
  critic defects, verified corrections, runtime failures, or notable successes — to record
  scoped learning, classify causes, track recurrence, and manage promotion lifecycle
  (observation→project-rule→candidate-global→validated-global→deprecated) per MEMORY_POLICY.
  Do not activate during planning, before evidence exists, to invent memory, auto-globalize
  lessons, or encode house-style taste.
---

# acos-failure-learning

Evidence-based memory procedure for ACOS. Owns learning **after** observed evidence — not creation, not gate judgment, not production.

**Authority:** `core/MEMORY_POLICY.md`  
**Schema reference:** `references/memory-record-schema.yaml`

---

## 1. Purpose

Convert **observed, evidenced outcomes** into structured, scoped memory proposals that improve future routing, skill effectiveness, and model compatibility — without fabricating history, auto-globalizing single events, or encoding an ACOS house style.

This skill handles:

- failure recording with cause and correction linkage
- success recording when reuse-relevant
- model-specific difficulty and quirk capture
- skill effectiveness signals
- recurrence tracking within and across projects
- project-scoped rule formation
- candidate reusable lesson identification
- promotion lifecycle management per canonical stages

Core principle:

```text
Claim != Evidence
One event != Global law
One project look != ACOS aesthetic
```

---

## 2. Activation / trigger conditions

Activate when **all** of the following are true:

1. A real project or benchmark run has produced **observable evidence** (not plans alone).
2. At least one trigger event exists:
   - `acos-quality-gate` verdict: APPROVE, REJECT, or BLOCKED / INSUFFICIENT EVIDENCE
   - critic defect report from `acos-visual-critic`, `acos-creative-critic`, or `acos-3d-critic`
   - verified correction after upstream rework (re-test evidence present)
   - runtime or measurement failure with artifacts
   - deliberate success worth scoped reuse (gate-approved or equivalent evidence)
   - model/tool behavior quirk affecting task outcome (with evidence)
3. The workflow phase is **post-inspection** — after QA, gate, or verified correction — not during ideation or pre-evidence design.
4. Memory write is **proposed**, not assumed: this skill defines what may be recorded and at what scope.

Also activate when:

- reviewing recurrence of a prior observation within the same project
- evaluating whether a project-rule may advance to candidate-global (only with cross-project evidence bundle)
- deprecating a stale validated-global or project-rule

---

## 3. Do-not-activate conditions

Do **not** activate when:

- no primary evidence exists (only intentions, specs, or compile success)
- the task is foundation implementation with empty memory stores and no project package (Phase C: define procedure only; **do not populate fake records**)
- learning is requested to justify a predetermined aesthetic or "ACOS look"
- a single failure is being pushed to global policy without recurrence and validation
- a single model run weakness should become universal routing law
- success is purely subjective with no linked evidence
- upstream gate or critic work is incomplete — learning follows judgment, does not replace it
- the request is to fine-tune models (out of scope)
- the request is to backfill fictional project history, model history, or taste preferences

Do **not** activate merely because other ACOS skills ran. Learning requires **outcome evidence**.

---

## 4. Responsibility boundary

### Owns

- structuring failure and success memory proposals
- root-cause classification (process, skill, model, tool, integration, evidence gap)
- linking evidence artifacts to learning records
- scope tagging: project / model / skill / reusable system / taste-scoped
- recurrence counting and cross-project deduplication checks
- promotion lifecycle state transitions **when criteria are met**
- deprecation proposals with retained reason/evidence
- read filtering guidance: what memory to retrieve for a given task context

### Does NOT own

- quality gate verdict (→ `acos-quality-gate`)
- critic evaluation (→ critic skills)
- creative, art, experience, or production decisions (→ upstream creator skills)
- runtime orchestration or routing engine implementation
- model adapter configuration (→ thin adapter / model profile layer)
- writing canonical foundation policy
- automatic skill rewrites based on one failure

### Boundary rules

| Concern | Owner |
|---|---|
| Ship / no-ship | `acos-quality-gate` |
| Defect identification | critic skills |
| Correction execution | responsible upstream skill |
| Learning record structure | `acos-failure-learning` |
| Global policy text | human-approved canonical docs |

---

## 5. Required inputs

Minimum inputs vary by trigger; collect all that apply.

```yaml
trigger_event: gate_verdict | critic_defect | correction_verified | runtime_failure | notable_success | model_quirk | recurrence_review | deprecation_review

project_context:
  project_id: string          # required for project-scoped records
  domain: string              # from brief — not a preset industry default
  phase: string               # e.g. post-gate, post-correction

evidence_bundle:              # required — at least one primary artifact
  - evidence_id: string
    evidence_type: planning | implementation | runtime | visual | measurement | gate_verdict | critic_report
    source_skill: string
    artifact_ref: string      # path, URL, screenshot ref, log excerpt pointer
    summary: string

gate_or_critic_payload:       # when applicable
  verdict: APPROVE | REJECT | BLOCKED
  failed_dimensions: []
  defects: []
  responsible_owner: string
  required_correction: string

outcome:
  problem_or_success: string
  correction_applied: string  # if any
  re_test_evidence: string    # if correction claimed

model_context:                # when model-specific
  provider: string
  model: string
  version: string

active_skills: []             # skills involved in the outcome

prior_records: []             # related observation/project-rule IDs for recurrence
```

Reject input bundles missing `evidence_bundle` or with placeholder-only artifacts.

---

## 6. Exact procedure / workflow

Execute steps in order. Do not skip classification or scope assignment.

### Step 1 — Evidence gate

1. Confirm at least one **primary** evidence item exists and is inspectable.
2. Classify each item: planning / implementation / runtime / visual / measurement / gate_verdict / critic_report.
3. If evidence is insufficient → output `BLOCKED — INSUFFICIENT EVIDENCE FOR LEARNING` and stop. Do not invent records.

### Step 2 — Event classification

Determine record type:

| Signal | Record type |
|---|---|
| Gate REJECT, critic defect, runtime failure | failure |
| Gate APPROVE + notable reusable mechanism | success (optional) |
| Unresolved hypothesis | observation only |
| Model/tool anomaly | observation or model_compatibility entry |

### Step 3 — Scope assignment (mandatory)

Assign exactly one **primary** scope:

- **project_specific** — lesson applies to this project only
- **model_specific** → `memory/model-compatibility/`
- **skill_specific** — tied to one skill's procedure or effectiveness
- **reusable_system** — technical/process lesson potentially cross-project
- **taste_scoped** — aesthetic preference with explicit boundary (never default global)

**House-style check (mandatory for taste or visual success):**

Answer explicitly:

1. Is this derived from one project's visual outcome?
2. Would promoting it create a default "ACOS look"?
3. If yes to (1) and yes to (2) → remain **project-rule** or **observation** only; do not promote to global taste.

### Step 4 — Root cause and correction linkage (failures)

Classify `root_cause`:

`process_gap | skill_procedure | model_limitation | tool_constraint | integration_error | evidence_missing | scope_mismatch | requirement_ambiguity | environmental | unknown`

Link:

- responsible upstream owner (from gate/critic routing)
- correction action and verification status
- affected skills and skill_effectiveness when known

### Step 5 — Draft memory record

Build record per `references/memory-record-schema.yaml`:

- Set `promotion_status: observation` for all new entries
- Set `confidence` from evidence strength (low / medium / high)
- Set `status: draft` until validated within procedure

**Phase C rule:** define the record structure in output; do **not** write to `memory/` directories during foundation implementation unless a real approved project run exists.

### Step 6 — Project-rule promotion (within same project)

Promote `observation → project-rule` only when:

- primary evidence linked
- root cause or success mechanism stated
- correction verified OR success mechanism documented
- scope and affected skills assigned

Update `promotion_status: project-rule` and route to appropriate store:

- failures → `memory/failures/`
- successes → `memory/successes/`
- project brief/history → `memory/projects/`

### Step 7 — Recurrence tracking

When a similar pattern appears:

1. Match on scope + problem/mechanism fingerprint (not merely keyword).
2. Increment recurrence count; append project_id if new project.
3. Store `first_seen`, `last_seen`, and linked record IDs.

Do not treat recurrence within **one** project as cross-project validation.

### Step 8 — Candidate-global proposal (cross-project)

Propose `project-rule → candidate-global` only when **all** true:

- same lesson pattern in **≥ 2 sufficiently different** project contexts
- complete evidence bundle per occurrence
- contradiction check against existing records passes
- house-style check passes (no universal aesthetic encoding)
- lesson is not benchmark-specific content masquerading as foundation

Output a **promotion_proposal** artifact; do not self-approve to validated-global.

### Step 9 — Validated-global promotion

Transition `candidate-global → validated-global` only when:

- designated human or validation authority approves
- recurrence and diversity requirements documented
- retrieval scope and review criteria defined
- record placed in `memory/knowledge/` (or `memory/taste/` for scoped taste with explicit boundaries)

### Step 10 — Deprecation

Move any stage → `deprecated` when:

- contradicting evidence documented
- tool/model/workflow context obsolete
- scope no longer applicable

Retain reason, superseding record ID if any, and historical evidence pointers.

### Step 11 — Retrieval guidance (read path)

When a future task needs memory:

1. Filter by current project_id, phase, active skills, and domain.
2. Pull only matching scope: project rules for this project, validated-global for reusable_system, model profile for current model.
3. Exclude deprecated and superseded records from active guidance.
4. Never dump entire memory stores into context.

---

## 7. Required outputs / deliverables

Every activation produces one or more structured artifacts:

### A. Learning record draft (YAML or JSON matching schema)

Minimum for failures:

```yaml
learning_record:
  id: mem-failure-{project}-{sequence}
  record_type: failure
  promotion_status: observation | project-rule
  project: {project_id}
  date: {ISO-8601}
  domain: {domain}
  scope: project_specific | model_specific | skill_specific | reusable_system | taste_scoped
  problem: string
  evidence: [{evidence_id, evidence_type, source_skill, artifact_ref, summary}]
  root_cause: string
  correction: {action_taken, responsible_owner, verified, re_test_evidence}
  affected_skills: []
  confidence: low | medium | high
  status: draft | active
  recurrence: {count, project_ids, first_seen, last_seen}  # when applicable
```

Minimum for successes (when recorded):

```yaml
learning_record:
  record_type: success
  outcome: string
  mechanism: string
  constraints: []
  reuse_scope: string
  promotion_status: observation | project-rule
  note: Success does not automatically become a global rule.
```

### B. Promotion proposal (when cross-project criteria met)

```yaml
promotion_proposal:
  proposal_id: string
  source_record_ids: []
  target_promotion_status: candidate-global | validated-global
  lesson_statement: string
  cross_project_evidence:
    minimum_distinct_projects: 2
    project_ids: []
    condition_diversity: string
  house_style_check:
    is_aesthetic: boolean
    would_create_acos_house_style: boolean
    passed: boolean
  contradiction_check:
    conflicting_record_ids: []
    resolution: string
  approver: pending | {authority}
```

### C. Learning handoff summary

See §9 Handoff contract.

### D. Insufficient-evidence notice (when blocked)

```yaml
learning_status: BLOCKED
reason: INSUFFICIENT_EVIDENCE_FOR_LEARNING
missing: []
next_owner: acos-quality-gate | responsible critic | upstream correction owner
```

---

## 8. Rejection / failure conditions

Reject or block learning work when:

| Condition | Result |
|---|---|
| No primary evidence | BLOCKED — do not create record |
| Evidence is placeholder or compile-only | REJECT record draft |
| Single event → global promotion requested | REJECT — remain observation or project-rule |
| Aesthetic lesson without taste scope | REJECT global promotion |
| Would encode ACOS house style | REJECT — project scope only |
| Benchmark content → canonical foundation | REJECT |
| Model single-run weakness → universal routing law | REJECT global promotion |
| Missing root_cause on failure | REJECT until filled or marked `unknown` with follow-up |
| Missing correction linkage when correction claimed | REJECT |
| Contradiction with validated-global unresolved | BLOCK promotion |
| Request to fabricate history for empty memory stores | REJECT — Phase C prohibited |

Learning skill failure does **not** override gate verdicts or reopen shipped work without new evidence.

---

## 9. Handoff contract

```yaml
status: complete | blocked | proposal_only
inputs_used:
  - trigger_event
  - evidence_bundle refs
  - gate_or_critic_payload refs
decisions:
  - record_type assigned
  - scope assigned
  - promotion_status assigned
  - promotion_proposal issued | not eligible
constraints:
  - no auto-globalization
  - no house-style encoding
  - schema version 1.2
open_risks:
  - unknown root cause
  - single-project recurrence only
  - pending human approval for validated-global
evidence:
  - linked artifact refs (not copies of entire stores)
deliverables:
  - learning_record draft
  - promotion_proposal (if any)
  - retrieval_notes (if read path executed)
next_owner:
  complete: project memory store / human validator for global promotion
  blocked: evidence-producing skill (gate, critic, upstream correction)
  proposal_only: human or designated validation authority
rejection_route:
  insufficient_evidence: return to acos-quality-gate or originating critic
  correction_unverified: return to responsible upstream owner
  premature_global: remain project-rule; no downstream canonical edit
```

Avoid free-form "noted for next time" without structured fields.

---

## 10. QA / evaluation contract

Evaluate each learning activation against:

| Criterion | Pass condition |
|---|---|
| Evidence linkage | Every record cites ≥1 inspectable primary evidence |
| Scope honesty | Scope matches actual applicability; no scope inflation |
| Promotion discipline | Lifecycle stage matches evidence tier |
| No fabrication | No invented projects, failures, or preferences |
| House-style guard | Visual/aesthetic entries cannot silently become global taste |
| Model scope | Model lessons stay in model-compatibility unless validated separately |
| Recurrence accuracy | Counts reflect distinct evidenced occurrences |
| Deprecation integrity | Deprecated records retain reason and pointers |
| Schema conformance | Fields match `memory-record-schema.yaml` |
| Retrieval safety | Read guidance is filtered, not exhaustive dump |

**Pass:** all applicable criteria met.  
**Fail:** any fabrication, auto-globalization, or missing mandatory field → revise or block.

---

## 11. Evidence requirements

### Acceptable primary evidence

- Gate verdict artifact from `acos-quality-gate` with failed dimension, owner, correction requirement
- Critic report with defect, severity, and evidence refs
- Rendered/browser/visual artifacts when claim is visual
- Runtime logs, measurements, or profiles when claim is performance or functional
- Re-test evidence after correction
- Model compatibility benchmark results per `core/MODEL_COMPATIBILITY.md`

### Not sufficient alone

- Source code compiles
- Creator self-assessment without inspection
- Planning documents without implementation/runtime/visual follow-through
- Single screenshot with no context
- Agent assertion without artifact ref

### Evidence discipline tiers

```text
planning evidence      → may inform observation only; weak promotion weight
implementation evidence → supports project-rule when linked to outcome
runtime evidence       → supports failure/success classification
visual evidence        → required for visual/taste-scoped lessons
measurement evidence   → required for performance claims
```

Claim != Evidence. Learning records cite evidence; they do not replace it.

---

## 12. Memory interaction

### Read (retrieval)

May read from (when stores exist and task warrants):

- `memory/projects/{project_id}/` — active project rules and history
- `memory/failures/` — matching scope, domain, skills, non-deprecated
- `memory/successes/` — matching reuse_scope and constraints
- `memory/knowledge/` — validated-global reusable_system and skill_specific
- `memory/taste/` — only when taste-scoped retrieval explicitly requested and scoped
- `memory/model-compatibility/` — current model profile

Retrieve **minimal relevant subset** for task, phase, and active skills. Do not load full history.

### Write (proposal)

May **propose** writes to:

| Store | Content | Max initial promotion_status |
|---|---|---|
| `memory/failures/` | evidenced failures | project-rule |
| `memory/successes/` | evidenced successes | project-rule |
| `memory/projects/` | project-local rules | project-rule |
| `memory/model-compatibility/` | model quirks/strengths/weaknesses | project-rule or candidate-global per policy |
| `memory/knowledge/` | reusable lessons | validated-global only after approval |
| `memory/taste/` | scoped aesthetic patterns | validated-global only after approval + explicit scope |

### Promotion lifecycle (authoritative)

```text
observation
→ project-rule
→ candidate-global
→ validated-global
→ deprecated
```

Rules:

- All new entries start at **observation**
- **candidate-global** requires cross-project recurrence
- **validated-global** requires human or designated validation authority
- **deprecated** retains history; excluded from active retrieval
- One failure ≠ global law; one success ≠ global rule; one project aesthetic ≠ ACOS house style

### Phase C prohibition

During foundation implementation: **define procedure and schema only**. Do not populate fake successes, failures, project history, model history, or taste preferences in `memory/`.

---

## 13. Relationship to neighboring ACOS skills

### Upstream (provide learning inputs)

| Skill | Provides |
|---|---|
| `acos-quality-gate` | Final verdict, failed dimensions, owners, corrections |
| `acos-visual-critic` | Visual defects and evidence |
| `acos-creative-critic` | Concept/originality defects |
| `acos-3d-critic` | 3D/integration defects |
| Creator and specialist skills | Corrections, re-test evidence |
| Thin model adapter layer | Model profile identifiers |

Typical chain:

```text
… → critics → acos-quality-gate → APPROVE | REJECT | BLOCKED
→ acos-failure-learning (post-evidence)
→ project memory / promotion proposals
```

### Downstream (consumers of learning)

- Future project routing (Phase D+) — filtered retrieval
- Human validators — candidate-global and validated-global approval
- Model compatibility reviews — model-scoped records
- Skill maintainers — skill_specific effectiveness signals

### Separation preserved

```text
Skill ≠ Tool ≠ Model ≠ Memory ≠ Adapter
```

Learning improves the system; it does not replace skills, gate, or adapters.

### Overlap prevention

- Gate owns ship decision; learning owns record structure post-decision
- Critics own defect truth; learning links defects to durable scoped lessons
- Creative/art skills own direction; learning does not rewrite direction from one failure
- External execution skills (Three.js, GSAP, Blender, etc.) are not modified by this skill

---

## 14. Non-goals

- Fine-tuning or training models
- Auto-globalizing single failures or successes
- Creating an ACOS house style via taste memory
- Writing benchmark-specific content into canonical foundation
- Fabricating memory records during Phase C or without evidence
- Replacing `acos-quality-gate` or critic skills
- Self-approving validated-global promotions
- Dumping all memory into agent context
- Modifying external skill bodies
- Implementing Phase D routing engine or memory persistence adapters
- Converting one model weakness into universal policy without validation
- Backfilling fictional project or model history

---

## Quick reference — scope vs store

| Scope | Typical store | Global promotion |
|---|---|---|
| project_specific | `memory/projects/` | Never global |
| model_specific | `memory/model-compatibility/` | Candidate with benchmark evidence |
| skill_specific | failures/successes/knowledge | Candidate-global with cross-project proof |
| reusable_system | `memory/knowledge/` | validated-global after approval |
| taste_scoped | `memory/taste/` | validated-global only with explicit scope; never default aesthetic |

---

## Eval cases (procedure checks)

1. **Gate REJECT with visual evidence** → failure record, scope project_specific or skill_specific, promotion_status observation; promote to project-rule only after correction verified.
2. **Same skill gap in two domains/projects** → candidate-global proposal; not validated-global without approver.
3. **Single APPROVE with strong visual** → optional success at project-rule; house-style check blocks taste-global.
4. **Model hallucinates tool API once** → model_specific observation; not global routing law.
5. **No evidence artifact** → BLOCKED; no record draft.
6. **Phase C empty memory** → schema and procedure output only; zero filesystem writes to `memory/`.
