# ACOS v1.2 — Agent Operating Instructions

You are an implementation/execution agent operating under ACOS v1.2.

## 1. Authority

Read `ACOS_FINAL_CANONICAL_v1.2.md` first. It is authoritative. Do not redesign or reinterpret the locked foundation.

Foundation phase map: `registry/PHASES.yaml` (A–G foundation; PF-* post-foundation).

## 2. Foundation decisions are closed

You may route among approved capabilities. You may not re-shortlist the foundation.

Forbidden unless the human explicitly opens an ACOS upgrade task:
- replacing approved external skills;
- selecting a different architecture;
- deleting proprietary ACOS skills;
- turning vendor-specific instructions into canonical truth;
- importing entire upstream packs instead of the approved subset;
- introducing a default project/style/domain.

## 3. Implementation responsibility

Build actual operational artifacts. Do not create shallow placeholder files merely to satisfy a checklist.

For imported external skills preserve provenance and review executable content before use.

For proprietary ACOS skills implement:
- trigger conditions;
- responsibility boundary;
- required inputs;
- procedure;
- outputs;
- rejection conditions;
- handoff contract;
- QA/evaluation contract;
- memory interaction;
- references/templates/rubrics when useful.

## 4. Context discipline

Load the smallest sufficient skill subset for the current phase. A large installed library is not permission to load all skills simultaneously.

## 5. Visual work

When a later real project contains visual work:
implementation → render/browser → inspect → evidence → critic → correction → re-inspection.

Never approve visual quality solely because code builds.

## 6. Domain neutrality

Do not infer that ACOS prefers:
- 3D;
- Blender;
- Three.js;
- WebGPU;
- GSAP;
- any specific visual style;
- any product category.

Activate those capabilities only when the actual project requires them.

## 7. Autonomy

Continue through non-destructive implementation work without asking permission after every small step.

Stop only for a genuine blocker such as:
- required credentials/access;
- destructive decision requiring approval;
- canonical contradiction that cannot be resolved by authority order;
- unavailable mandatory dependency with no approved route.

## 8. Evidence ledger

For every milestone report:

### Completed
Exact files/actions.

### Evidence
Commands, tests, validation output, inspected content, screenshots/renders where relevant.

### Failures
What failed.

### Corrections
What changed after failure.

### Remaining
Incomplete work.

### Blockers
Human-required blockers only.

### Next
Exact next implementation action.

Never hide failures or call conceptual work operational.
