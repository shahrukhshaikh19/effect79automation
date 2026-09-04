# ACOS Workflow v1.2

This is the canonical phase flow for a real project. Foundation implementation happens before any project package is introduced.

## A. Foundation implementation

1. Read canonical pack.
2. Create canonical repository structure.
3. Populate core policy files.
4. Import/pin approved external skills.
5. Implement 14 proprietary ACOS skills.
6. Configure tools separately.
7. Create thin adapters/model profiles.
8. Create memory stores.
9. Implement validation/routing checks.
10. Run foundation structural + operational validation.
11. Only after validation, accept an external project/benchmark package.

## B. Real project workflow

```text
PROJECT PACKAGE
→ BRIEF NORMALIZATION
→ REFERENCE ANALYSIS (when references exist)
→ CREATIVE DIRECTION (when creative direction is relevant)
→ ANTI-GENERIC REVIEW
→ ART DIRECTION
→ EXPERIENCE ARCHITECTURE
→ DESIGN GATE
→ TECHNICAL PLAN
→ SPECIALIST PRODUCTION
→ INTEGRATION
→ RENDER / BROWSER / RUNTIME INSPECTION
→ FUNCTIONAL QA
→ VISUAL QA
→ CREATIVE QA
→ DOMAIN QA (3D/motion/etc. only when relevant)
→ PERFORMANCE + ACCESSIBILITY QA
→ QUALITY GATE
→ APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE | ROUTE DEFECT UPSTREAM
→ PROJECT MEMORY
```

## Design Gate

Before full implementation of meaningful creative work verify:
- the concept belongs to this project;
- there is a clear hierarchy and experience thesis;
- references have been interpreted rather than copied;
- typography/composition are intentional;
- proposed 3D/motion has a reason to exist;
- technical feasibility is credible;
- responsive strategy exists;
- performance/accessibility constraints are acknowledged.

A failed Design Gate routes back to the responsible upstream skill.

## Specialist production

The router selects only relevant approved skills. No project automatically activates 3D, motion or Blender.

## QA loop

A failure is routed to the skill responsible for the defect:
- generic concept → creative/anti-generic;
- weak hierarchy → art director;
- broken journey → experience architect;
- geometry/material/camera issue → 3D route;
- purposeless motion → motion director;
- mobile composition issue → responsive art direction;
- WebGL budget issue → webgl-performance;
- implementation/runtime issue → engineering/testing route.

## Benchmark separation

Benchmarks are external project packages registered after foundation validation. They never define the canonical ACOS aesthetic or default workflow.
