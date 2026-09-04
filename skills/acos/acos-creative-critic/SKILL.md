---
name: acos-creative-critic
description: Activate when a creative direction artifact and project context exist and independent judgment is needed on originality, concept strength, project specificity, coherence, and genericness — not pixel-level visual QA. Do not activate for render-only spacing/typography defects, 3D geometry review, or when no creative claims are in scope.
---

# acos-creative-critic (ACOS-11)

Independent creative and conceptual critic. Evaluates whether the work is **specific to this project**, **conceptually coherent**, and **non-interchangeable** — and whether execution supports the central creative thesis.

Authoritative policy references: `core/QUALITY_GATES.md`, `core/WORKFLOW.md`, `core/ROUTING.md`, `core/MEMORY_POLICY.md`.

---

## 1. Purpose

Provide evidence-informed, independent criticism of creative quality: originality, concept strength, project specificity, idea coherence, creative consistency, genericness, and thesis–execution alignment.

Classify problems as **concept**, **art-direction**, **experience**, or **execution** problems and route each to the responsible upstream owner. This skill does not perform pixel-level visual QA and does not hold final ship authority.

---

## 2. Activation / trigger conditions

Activate when **all** of the following are true:

1. A creative scope exists — brief, creative direction artifact, experience thesis, or shipped/candidate output claiming creative intent.
2. Independent creative evaluation is required (post-direction, pre-gate, or post-implementation creative QA).
3. The question concerns **concept, specificity, coherence, or genericness** — not primary ownership of spacing, typography polish, or geometry fidelity.

Typical routing triggers:

- Canonical workflow **Creative QA** phase.
- After `acos-creative-director` output before Design Gate or production.
- After implementation when creative thesis vs result must be compared.
- Quality gate requests creative critic findings before aggregation.
- `acos-anti-generic-design` escalates unresolved sameness for independent verdict.

---

## 3. Do-not-activate conditions

Do **not** activate when:

- The task is **pixel-level visual QA** (alignment, spacing, typography rendering) — use `acos-visual-critic` with render evidence.
- The task is **3D geometry, materials, lighting, or camera credibility** — use `acos-3d-critic` when 3D output exists.
- **No creative claims** are in scope (pure bugfix, refactor, mechanical implementation with unchanged thesis).
- Only references exist with **no creative direction or output** to evaluate — use `acos-reference-analysis` upstream first.
- The evaluating agent is the **sole author** of the creative thesis with no independence boundary — escalate to quality gate; do not self-approve creative quality.
- The task is **final ship/no-ship** — use `acos-quality-gate`.
- The goal is to **impose personal taste** or reject unfamiliar but coherent aesthetics without project-specific failure evidence.

---

## 4. Responsibility boundary

### Owns

- Independent evaluation of:
  - originality relative to brief and context
  - concept strength and clarity of central idea
  - project specificity (would this survive a name/logo swap test?)
  - idea coherence across touchpoints
  - creative consistency (thesis vs artifacts vs implementation)
  - genericness / interchangeability
  - whether execution supports or undermines the creative thesis
- Problem classification:
  - `concept_problem`
  - `art_direction_problem`
  - `experience_problem`
  - `execution_problem`
- Severity and upstream routing per finding
- Structured creative critique artifact

### Does NOT own

- Defining the creative thesis (`acos-creative-director`)
- Reference extraction (`acos-reference-analysis`)
- Anti-generic stress tests authorship (`acos-anti-generic-design` — may consume its findings)
- Visual language specification (`acos-art-director`)
- Journey/IA design (`acos-experience-architect`)
- Pixel-level hierarchy/spacing/type defects in renders (`acos-visual-critic`)
- 3D credibility (`acos-3d-critic`)
- Final APPROVE / REJECT / BLOCKED decision (`acos-quality-gate`)
- Rewriting creative direction or implementing fixes

---

## 5. Required inputs

| Input | Required | Notes |
|---|---|---|
| Normalized project brief | Yes | Goals, audience, constraints, differentiation intent |
| Creative direction artifact | When exists | Thesis, territories, principles |
| Anti-generic review output | When exists | Prior sameness flags |
| Art direction / experience artifacts | Recommended | Coherence checks |
| Implementation or candidate output | When evaluating execution | Screens, flows, copy, structure — not code alone |
| Reference contract | When references exist | Interpretation vs copy boundary |
| Render/browser evidence | When judging execution support | Required to claim execution failure |

If evaluating **execution support**, some observable output evidence is mandatory. If evaluating **concept only**, direction artifacts may suffice; state evidence type explicitly.

---

## 6. Exact procedure / workflow

### Step 1 — Independence check

1. Confirm critic independence from creative author when possible.
2. If only self-review is possible, record risk and defer final creative approval to `acos-quality-gate`.

### Step 2 — Frame the thesis

1. Extract stated central creative thesis from artifacts (quote or paraphrase with source ref).
2. List project-specific constraints that must appear in a non-generic outcome.
3. If no thesis exists, fail early: `creative_critique_status: fail` with `concept_problem` routed to `acos-creative-director`.

### Step 3 — Specificity and genericness tests

Apply in order:

1. **Swap test** — Could this concept serve an unrelated project with superficial renaming? If yes → genericness finding.
2. **Trope audit** — Are visible patterns justified by brief or default decoration? Unjustified tropes → route `acos-anti-generic-design` / `acos-creative-director`.
3. **Constraint satisfaction** — Does the concept address stated constraints uniquely?
4. **Coherence scan** — Do art direction, experience architecture, motion/3D proposals align with thesis?

### Step 4 — Execution alignment (when output exists)

1. Compare observable output to thesis without pixel QA.
2. Ask: Does execution **express**, **dilute**, or **contradict** the thesis?
3. Separate:
   - **execution_problem** — thesis clear but delivery wrong (may overlap visual critic — route visual defects there)
   - **concept_problem** — thesis weak regardless of polish
   - **art_direction_problem** — visual language fails to embody thesis
   - **experience_problem** — journey/pacing undermines thesis

### Step 5 — Finding records

```yaml
finding_id: CC-###
classification: concept_problem | art_direction_problem | experience_problem | execution_problem
description: specific, evidence-linked statement
severity: critical | major | minor | observation
evidence_ref: artifact id or quoted direction section
owner: upstream skill
correction: required creative change
retest: what artifact/output to re-evaluate
```

### Step 6 — Severity rules

- **critical** — Materially generic/interchangeable despite differentiated brief; thesis absent or contradictory; creative incoherence blocks project intent.
- **major** — Meaningful specificity gap, weak central idea, or execution clearly undermines thesis on primary surfaces.
- **minor** — Localized coherence drift fixable without thesis change.
- **observation** — Strengthening opportunity; not a standalone fail.

Align **critical genericness** with hard reject in `core/QUALITY_GATES.md`.

### Step 7 — Owner routing

| Classification | Primary owner |
|---|---|
| concept_problem | `acos-creative-director` |
| art_direction_problem | `acos-art-director` |
| experience_problem | `acos-experience-architect` |
| execution_problem (visual) | `acos-visual-critic` if render evidence needed |
| execution_problem (3D) | `acos-3d-critic` when 3D exists |
| genericness / trope | `acos-anti-generic-design` + relevant director |
| reference misuse | `acos-reference-analysis` |

### Step 8 — Verdict and handoff

1. Set `creative_critique_status`: `pass` | `pass_with_observations` | `fail` | `blocked_insufficient_evidence`
2. `blocked_insufficient_evidence` when thesis or output claims cannot be evaluated from available artifacts.
3. Never issue final ship APPROVE — hand off to `acos-quality-gate`.

---

## 7. Required outputs / deliverables

### Primary artifact: Creative Critique Report

- stated thesis extraction
- specificity/genericness test results
- finding register (Step 5)
- classification summary counts
- `creative_critique_status`
- explicit retest requirements

### Minimum handoff block

See Section 9.

---

## 8. Rejection / failure conditions

Contract failure (invalid critic output) when:

- Findings rely on personal taste without project-specific criteria.
- Pixel-level visual defects are adjudicated here instead of routed.
- Unfamiliar aesthetics rejected without coherence/specificity failure evidence.
- Creative pass issued while critical genericness or thesis failure documented.
- Ship APPROVE issued — forbidden.

Creative **fail** when critical/major concept/specificity/coherence findings remain per Step 6 and project policy.

---

## 9. Handoff contract

```yaml
handoff:
  skill: acos-creative-critic
  status: pass | pass_with_observations | fail | blocked_insufficient_evidence
  inputs_used:
    - brief_ref
    - creative_direction_ref
    - output_evidence_refs
  decisions:
    creative_critique_status: pass | pass_with_observations | fail | blocked_insufficient_evidence
    thesis_summary: "<one sentence>"
    finding_count:
      critical: 0
      major: 0
      minor: 0
      observation: 0
    classifications:
      concept_problem: 0
      art_direction_problem: 0
      experience_problem: 0
      execution_problem: 0
  constraints:
    - no_pixel_qa
    - independent_critic_required
  open_risks:
    - missing_thesis_artifact
    - missing_output_evidence
  evidence:
    - id: CE-001
      type: creative_direction | brief | render | flow_capture
      ref: "<reference>"
  deliverables:
    - creative_critique_report
    - finding_register
  next_owner: acos-quality-gate
  rejection_route:
    - finding_id: CC-001
      classification: concept_problem
      owner: acos-creative-director
      severity: major
      correction: "<required change>"
      retest: "<artifact or output scope>"
```

On `fail`, set correction loop owner from highest-severity finding. Always provide gate-readable summary.

---

## 10. QA / evaluation contract

### Scoring dimensions (when applicable)

From `core/QUALITY_GATES.md`:

- creative originality (0–10)
- brand/project distinctiveness (0–10)
- concept strength (0–10)
- storytelling/experience flow (0–10) — when experience artifacts/output in scope

Scores inform gate; do not self-approve from averages.

### Pass criteria

- Thesis identifiable and project-specific for `pass`.
- No unresolved **critical** genericness or thesis failure.
- Classifications and owners present for all major/critical findings.

### Anti-bias checks

- Document why unfamiliar aesthetics pass or fail using brief/specificity criteria.
- Separate "not my taste" from "fails project specificity."

---

## 11. Evidence requirements

| Claim type | Required evidence |
|---|---|
| Weak/absent thesis | Creative direction artifact or its documented absence |
| Generic/interchangeable | Brief differentiation requirements + output/direction comparison |
| Incoherence | Cross-artifact references (CD vs AD vs EA) |
| Execution undermines thesis | Observable output (render, flow, copy structure) — not code alone |
| Reference copy vs interpret | Reference contract + output comparison |

Distinguish planning artifacts from implementation evidence. Execution claims require observable output.

---

## 12. Memory interaction

Phase C: do not write real memory records.

### May read later

- `memory/projects/` — prior creative decisions and outcomes
- `memory/failures/` — recurring genericness patterns (scoped)

### May propose (via `acos-failure-learning`)

- Recurring concept specificity failures with scope tags
- Model-specific creative weakness observations with evidence

### Must NOT

- Encode project aesthetics as global ACOS taste
- Promote single success as universal creative rule
- Fabricate learning records

---

## 13. Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-creative-director` | Upstream thesis owner; receives concept_problem routes |
| `acos-anti-generic-design` | Upstream/downstream sameness tests; may feed findings here |
| `acos-art-director` | Receives art_direction_problem routes |
| `acos-experience-architect` | Receives experience_problem routes |
| `acos-visual-critic` | Parallel; receives pixel-level execution defects |
| `acos-3d-critic` | Parallel when 3D present |
| `acos-quality-gate` | Aggregates; final status authority |
| `acos-failure-learning` | Records validated post-failure lessons |

**Overlap prevention:** Creative critic owns **concept/specificity/coherence**. Visual critic owns **rendered execution quality**. Anti-generic owns **trope/sameness stress tests**; this skill delivers **independent verdict** on creative quality.

---

## 14. Non-goals

- Not pixel-level visual QA or spacing/typography policing
- Not a replacement for creative director or anti-generic skill authorship
- Not a ban-list of design techniques globally
- Not a personal aesthetic authority
- Not a 3D or motion technical reviewer
- Not a final quality gate
- Not a domain-specific creative template library
- Not an implementer or copywriter

---

## Reference

- `core/QUALITY_GATES.md` — creative dimensions and hard reject for generic results
- `core/WORKFLOW.md` — Creative QA placement
- `core/ROUTING.md` — defect routing
