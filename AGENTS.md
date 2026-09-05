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

If `runtime/host/CURRENT_HOST_BRIEF.md` exists, it is the active host packet. Invoke only those native `/skill` names. Do not select from the full discovered catalog.

On a new product request (not a foundation-edit task), run the host loop instead of guessing skills:

```text
python tools/host_driver/run_stage.py init --prompt "<user request>"
```

Then read `runtime/host/CURRENT_HOST_BRIEF.md` and `runtime/host/CURRENT_HOST_TODO.md`, execute only `invoke_now`, write artifacts under the listed project dir, then `python tools/host_driver/run_stage.py advance`. On EVIDENCE run `capture`. Repeat until SHIP, REJECTED, or a real BLOCKED reason.

Do not slash-pick skills. Do not skip Design Gate. Copy `skill_md_sha256` and fill `procedure_evidence` from the brief; a boolean is not skill execution. Flagship lookdev needs `evidence/lookdev/` screenshots; a crushed dump versus a lit reference is a fail. Flagship production also needs director/modeler/prop/materials/lookdev receipts — export YAML is not craft. A sphere/cylinder dump or macro lookdev crop fails. Physical products require `/hard-surface`. Do not self-attest critic independence if this chat produced the implementation. A new chat with a distinct `ACOS_HOST_CONTEXT_ID` runs `python tools/host_driver/run_stage.py critic-pass`. `python tools/host_driver/run_stage.py check` is the mechanical audit. A clear premium 3D prompt follows `docs/FLAGSHIP_PREMIUM_WORKFLOW.md` — Blender authors the hero; do not ship a convenience primitive. If Blender MCP/app is down, tell the user, wait, confirm after connect (`confirm-blender --mcp-live`), then start. Never skip.

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
