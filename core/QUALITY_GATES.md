# ACOS Quality Gates v1.2

Quality is multi-dimensional. Only score dimensions relevant to the actual project, but hard failures always override averages.

## Evaluation dimensions

0–10 when applicable:
- creative originality
- brand/project distinctiveness
- concept strength
- composition
- typography
- visual hierarchy
- 3D quality
- 3D/UI integration
- lighting/material quality
- motion choreography
- storytelling/experience flow
- responsive art direction
- performance
- accessibility
- engineering quality

## Hard reject conditions

`SHIP: REJECTED` when a relevant critical defect exists:
- broken primary flow;
- serious console/runtime errors;
- unusable required viewport;
- critical accessibility blocker;
- unacceptable target-device performance;
- missing critical fallback;
- major required reference/asset mismatch;
- visible 3D credibility defect;
- visual work breaks existing business logic;
- materially generic/interchangeable result despite a differentiated brief.

Evidence insufficiency is **not** an artifact hard reject — see Evidence Blockers below.

## Evidence blockers (evaluation-state)

When required evidence is missing, invalid, stale, contradictory, or unverifiable, the gate cannot make a reliable ship/no-ship judgment:

- **EB-01** — required evidence insufficient → terminal status **BLOCKED_INSUFFICIENT_EVIDENCE**

EB blockers are not artifact-quality rejection. Nothing may ship while BLOCKED.

## Terminal gate status

Exactly one terminal outcome per gate evaluation:

| Status | Meaning | May ship? |
|---|---|---|
| **APPROVED** | Required evidence exists; applicable gates pass | Yes |
| **REJECTED** | Sufficient evidence to evaluate; hard failure or unacceptable quality demonstrated | No — route corrections |
| **BLOCKED_INSUFFICIENT_EVIDENCE** | Reliable ship/no-ship judgment impossible — evidence missing, invalid, stale, contradictory, or unverifiable | No — collect/repair evidence |

**BLOCKED_INSUFFICIENT_EVIDENCE is not approval.** It is not a quality rejection of the artifact itself; it is an evaluation-state failure.

```text
APPROVED → may ship
REJECTED → route defects → correct → regenerate evidence → re-evaluate
BLOCKED_INSUFFICIENT_EVIDENCE → collect/repair evidence → re-evaluate
```

## Evidence requirements

Functional:
- tests/runtime/interaction evidence.

Visual:
- browser/render evidence at required viewports/states.

3D:
- relevant views, geometry/material/lighting/camera checks, runtime inspection.

Performance:
- measurements appropriate to target runtime; for WebGL consider draw calls, triangles, textures, DPR, shader/postprocessing cost, asset size, loading and target-device behavior.

Accessibility:
- keyboard/focus/semantics/contrast/reduced-motion and other relevant checks.

## Product Form Gate (not ship)

When routing sets `requires_industrial_form`, a **Product Form Gate** runs after clay and the industrial-design critic, and **before** lookdev, production GLB, and web.

- File: `gate/product_form_gate.yaml`
- Statuses: APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE | NOT_APPLICABLE
- APPROVED unlocks production craft. It does **not** SHIP.
- Quality Gate (ACOS-13) remains the only ship/no-ship decision.

## Critic independence

The implementation skill may self-check, but final creative/visual/domain approval must involve the appropriate critic/gate responsibility.

## Final format

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
