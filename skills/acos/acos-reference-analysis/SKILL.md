---
name: acos-reference-analysis
description: Activate when the project supplies reference assets (images, URLs, videos, prior work, competitor examples) and reusable principles must be extracted without literal copying. Do not activate when no references exist, when final creative direction is already decided, or when the task is pure implementation without reference interpretation.
---

# acos-reference-analysis (ACOS-02)

## Purpose

Extract observable characteristics and reusable principles from supplied reference assets so downstream ACOS skills can make informed, project-specific decisions without cloning reference aesthetics.

This skill converts reference material into structured intelligence: what is observed, what it implies, what principle transfers to the current project, and what must not be copied literally.

Authority: `core/WORKFLOW.md` (Reference Analysis stage), `core/ROUTING.md`, locked boundary in `phase-C.md` §ACOS-02.

## Activation / trigger conditions

Activate when **all** of the following are true:

1. One or more reference assets or reference descriptions are supplied (images, URLs, video, motion captures, prior deliverables, annotated screenshots, written descriptions of existing work).
2. The current phase requires understanding reference characteristics before creative direction, art direction, or experience decisions.
3. Reference interpretation—not reproduction—is the authorized task.

Also activate when:

- A brief explicitly asks to learn from references without copying.
- Downstream skills request reference intelligence as a prerequisite.
- A defect route indicates reference was misinterpreted or copied literally (re-analysis authorized).

## Do-not-activate conditions

Do **not** activate when:

- No references exist and none are expected for this task.
- The task is to clone, pixel-match, or reproduce a reference as the deliverable.
- Final creative direction is already locked and only implementation remains.
- The request is to establish ACOS global taste or a permanent house style from references.
- References are mentioned only as vague inspiration with no analytical need ("make it feel premium").
- Production execution (modeling, layout coding, asset creation) is requested without reference analysis being in scope.
- Anti-generic review or creative thesis work is the primary need and no reference material is present.

If no references exist, **stop**. Do not fabricate reference analysis to satisfy workflow completeness.

## Responsibility boundary

### Owns

- Analysis of supplied references/assets.
- Extraction of reusable principles across applicable dimensions:
  - composition, hierarchy, typography characteristics, spacing/rhythm
  - lighting, camera/framing, materials, surface treatment
  - motion language, interaction language, narrative progression
  - depth, responsive behavior, distinctive characteristics
- Separating observation from interpretation.
- Identifying non-copy boundaries (what must not transfer literally).
- Project relevance assessment for each extracted principle.
- Structured reference intelligence artifact for downstream consumption.

### Does NOT own

- Choosing final creative direction or the central creative thesis.
- Cloning or mandating reproduction of reference aesthetics.
- Assuming references are mandatory for every project.
- Converting reference preferences into global ACOS taste.
- Final typography/material/color system selection (Art Director).
- Information architecture or journey design (Experience Architect).
- Implementation technology, 3D production, or motion code.
- Quality gate approval or anti-generic verdict (those are separate skills).

## Required inputs

Minimum:

| Input | Required | Notes |
|-------|----------|-------|
| Reference assets or verifiable descriptions | Yes | At least one; mark gaps explicitly |
| Project brief or task context | Yes | What the project is trying to achieve |
| Known constraints | Preferred | Platform, accessibility, performance, brand rules |
| Prior reference analysis | If exists | Extend, do not contradict without evidence |

Optional but valuable:

- User annotations on what they admire or reject in references.
- Viewport or device context for responsive references.
- Comparison set (multiple references showing range vs. single target).

If reference quality is too low to analyze (broken links, unreadable images), record the gap and request better input or proceed with limited-confidence observations only where defensible.

## Exact procedure / workflow

1. **Confirm activation eligibility.** Verify references exist and analysis—not cloning—is requested. If not, emit a no-activation handoff and stop.

2. **Inventory references.** List each asset with identifier, type, source, and role (e.g., layout reference, motion reference, typography reference). Note missing or inaccessible items.

3. **Establish analysis scope.** From brief + references, determine which dimensions apply (not every dimension exists in every reference). Mark N/A dimensions explicitly.

4. **Record observations (fact layer).** For each reference and applicable dimension, document only what is directly observable. Use neutral language. No aesthetic judgment yet.

5. **Record interpretations (meaning layer).** State what the observations likely achieve (e.g., establishes hierarchy, signals urgency, creates depth). Mark confidence: high / medium / low.

6. **Extract reusable principles.** Convert interpretations into transferable rules phrased generically (not tied to the reference's brand/domain). Each principle must answer: "What decision does this inform?"

7. **Assess project relevance.** For each principle, rate relevance to the current brief: direct / adapted / not applicable. Explain adaptation when the reference context differs from the project.

8. **Define non-copy boundaries.** For each reference, list specific elements that must **not** be copied literally (logos, distinctive marks, proprietary layouts, trademarked patterns, exact color codes unless brief requires, recognizable competitor identity).

9. **Cross-reference consistency check.** If multiple references conflict, document the conflict and do not silently merge incompatible principles.

10. **Confidence and gap summary.** State overall analysis confidence, unresolved questions, and inputs needed for higher confidence.

11. **Produce deliverable artifact** using schema in `references/output-schema.yaml`.

12. **Emit structured handoff** to primary downstream owner (typically `acos-creative-director`; may be `acos-art-director` or `acos-experience-architect` when creative direction is already set).

## Required outputs / deliverables

Primary deliverable: **Reference Intelligence Artifact** conforming to `references/output-schema.yaml`.

Must include:

- Reference inventory with access status.
- Per-dimension analysis where applicable (observation → interpretation → principle → relevance).
- Non-copy boundary list per reference.
- Confidence ratings and explicit gaps.
- Structured handoff block.

Secondary: routing recommendation for which downstream skills should consume which sections.

## Rejection / failure conditions

Reject or fail the analysis (do not pass downstream) when:

- Analysis recommends literal cloning as the project direction.
- Observations are invented without reference support (Claim != Evidence).
- Principles are stated as global ACOS preferences rather than project-scoped intelligence.
- Non-copy boundaries are omitted when references contain distinctive third-party identity.
- Reference dimensions are asserted without observable basis.
- The artifact conflates observation and final creative decision.
- Domain-specific defaults are embedded (e.g., assuming immersive 3D because reference used 3D).

Route rejection to: requesting agent or brief owner if inputs insufficient; self-correction if analysis quality defect.

## Handoff contract

Every completion or rejection must include a machine-readable handoff:

```yaml
status: complete | partial | rejected | no_activation
inputs_used:
  - ref: "<reference identifier>"
    type: "<image|url|video|document|description>"
    role: "<why this reference was analyzed>"
decisions:
  - id: "<principle-id>"
    principle: "<reusable principle statement>"
    relevance: direct | adapted | not_applicable
    confidence: high | medium | low
constraints:
  - "<non-copy or scope constraint downstream must respect>"
open_risks:
  - "<ambiguous reference, low-quality asset, conflicting references>"
evidence:
  - type: observation | interpretation
    source_ref: "<reference identifier>"
    note: "<what was seen or inferred>"
deliverables:
  - path: "skills/acos/acos-reference-analysis/references/output-schema.yaml"
    artifact: "<project-relative path to produced artifact>"
next_owner: acos-creative-director | acos-art-director | acos-experience-architect | none
rejection_route: "<skill or role if status is rejected or no_activation>"
```

Field omission: use empty lists or `null` only when genuinely not applicable; never omit `status` or `next_owner`.

## QA / evaluation contract

Self-evaluate before handoff:

| Check | Pass criterion |
|-------|----------------|
| Separation | Observations, interpretations, principles, and relevance are in distinct sections |
| Non-copy | At least one explicit non-copy boundary per reference with distinctive elements |
| Neutrality | No reference aesthetic promoted as ACOS default |
| Specificity | Principles are actionable decisions, not adjectives ("premium", "modern") |
| Evidence | Each principle traces to at least one observation |
| Scope | N/A dimensions marked; no false completeness |

Scoring guidance (internal, 0–10): reference fidelity, principle clarity, project relevance mapping, boundary explicitness. Score below 6 on any critical check → revise before handoff.

Downstream consumers (`acos-creative-director`, critics) may reject reference intelligence that fails these checks.

## Evidence requirements

| Evidence type | When required |
|---------------|---------------|
| Planning evidence | Reference inventory, observation notes tied to source |
| Visual evidence | Reference asset identifiers or accessible URLs/paths cited |
| Runtime evidence | Not required at this stage |

Distinguish clearly:

- **Observation evidence**: directly visible in reference.
- **Interpretation evidence**: reasoned inference labeled as such.
- **Not evidence**: model assumptions about unstated project goals.

Per `core/QUALITY_GATES.md`: Claim != Evidence.

## Memory interaction

During foundation phase: do not write to memory stores.

When operational on real projects (per `core/MEMORY_POLICY.md`):

**May read:**

- `memory/projects/` — prior decisions for same project.
- `memory/knowledge/` — validated analysis patterns (not taste defaults).

**May propose for project memory:**

- Reference inventory and approved principles with project scope tag.
- Non-copy boundaries agreed for the project.

**Must NOT promote to global/taste memory:**

- Reference aesthetics as reusable style.
- Competitor-specific patterns as ACOS defaults.

Promotion lifecycle: observation → project-rule only unless `acos-failure-learning` validates broader reuse.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|-------|--------------|
| `acos-creative-director` | Primary consumer; uses principles for thesis, does not receive cloned aesthetics |
| `acos-art-director` | May consume typography/composition/lighting principles; does not receive final palette from references alone |
| `acos-experience-architect` | May consume interaction/narrative/pacing principles from references |
| `acos-anti-generic-design` | Uses creative output, not raw references; may flag if reference analysis enabled copying |
| `acos-cinematic-3d-director` | Consumes camera/depth/lighting principles only when 3D is in scope |
| `acos-visual-critic` | May verify implementation did not violate non-copy boundaries |
| External Blender reference template | Production tool; ACOS reference analysis is upstream and domain-neutral |

**Overlap prevention:** This skill extracts intelligence only. It never selects the winning concept, visual system, or IA. If asked to "pick the direction from references," defer to `acos-creative-director`.

## Non-goals

- Cloning references or producing reproduction specs.
- Setting final creative direction, art direction, or experience architecture.
- Defining ACOS house style from admired references.
- Running when no references exist.
- Replacing specialized 3D/motion production skills.
- Quality gate approval or genericness verdict.
- Populating memory during Phase C foundation work.
