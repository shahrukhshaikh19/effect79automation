# BM-001 — OPERATOR INPUT

## What to build/test

Build a production-quality, premium interactive digital experience for a fictional high-end technology product.

The benchmark must test whether ACOS can take a high-level creative brief and produce an original, polished, responsive, visually distinctive web experience without falling into generic AI-generated design patterns.

This is a benchmark of the complete ACOS creative-production workflow, not a template recreation exercise.

## Primary objective

Evaluate whether ACOS can produce work that feels intentionally art-directed, technically polished, premium, memorable, and suitable for a real high-end commercial website.

The result should demonstrate strong:

* creative direction
* visual hierarchy
* art direction
* typography
* composition
* interaction design
* motion design
* responsive art direction
* technical implementation quality
* performance awareness
* visual consistency

3D may be used only if the system determines that it materially improves the experience.

3D is NOT mandatory.

## Creative freedom

ACOS has freedom to determine:

* visual concept
* page structure
* layout
* typography direction
* color system
* interaction language
* motion language
* transitions
* visual storytelling
* whether 2D, 3D, WebGL, shaders, or conventional web techniques are appropriate

The system must make these decisions through its normal routing and creative workflow.

Do not manually prescribe ACOS skill IDs.

## Product

Use a fictional premium technology product.

The exact fictional product identity, name, positioning, and visual concept may be created specifically for this benchmark as part of the creative process.

It must not imitate an existing commercial brand.

## Mandatory requirements

The final experience must:

1. be an actual functional web experience, not a static mockup;
2. have a clearly intentional creative concept;
3. contain multiple meaningful content/experience sections;
4. have a strong hero experience;
5. use deliberate typography and visual hierarchy;
6. include meaningful interaction or motion;
7. maintain visual coherence throughout the experience;
8. work responsively across required viewports;
9. avoid obvious layout breakage;
10. avoid obvious console/runtime errors;
11. maintain usable navigation and interaction;
12. demonstrate production-quality implementation rather than prototype-quality shortcuts;
13. provide evidence sufficient for ACOS quality gates to judge the result.

## Avoid

Do NOT:

* copy an existing website;
* recreate a supplied commercial design;
* imitate Apple, Nothing, Tesla, Stripe, Linear, Awwwards sites, or another recognizable brand;
* use a generic SaaS landing-page template;
* default to predictable gradient-heavy AI aesthetics;
* use arbitrary glassmorphism;
* use excessive glow merely to appear premium;
* use random floating cards;
* use meaningless decorative animation;
* force 3D into the experience;
* sacrifice usability for visual effects;
* sacrifice performance without a justified creative reason;
* treat desktop as the only designed viewport;
* use placeholder-quality visual assets in the final accepted result.

## References / assets

No visual reference website is supplied.

No existing design is supplied.

No brand identity is supplied.

No production asset pack is supplied.

This is intentional.

The benchmark should test ACOS's ability to originate an appropriate creative direction rather than reproduce a reference.

Any generated or internally created benchmark assets must have their provenance recorded.

## Target viewports

Required evaluation viewports:

Desktop:
1440 × 900

Laptop:
1280 × 800

Tablet:
768 × 1024

Mobile:
390 × 844

Also verify that the experience does not catastrophically break between these fixed evaluation sizes.

## Browser

Primary benchmark browser:

Chromium

## Interaction

The experience may use:

* scroll interaction
* pointer interaction
* hover
* transitions
* cinematic sequencing
* WebGL
* shaders
* 3D
* conventional DOM/CSS animation

Only when justified by the creative concept.

Reduced-motion behavior must be considered where applicable.

## Quality expectation

This benchmark is intentionally demanding.

The target is not merely:

"technically working."

The target is:

"production-quality creative work that could credibly be presented as premium professional digital work."

Generic, visually weak, incoherent, unfinished, broken, or unjustifiably derivative output should not pass merely because the application runs.

## Acceptance principle

ACOS's existing certified Quality Gate remains authoritative.

The benchmark must not create a weaker parallel quality system.

Benchmark-specific acceptance criteria may make requirements more measurable, but they must not bypass or override ACOS hard-reject rules or evidence requirements.

## Evidence

Evidence should be sufficient to evaluate at minimum:

* required viewport renders
* responsive behavior
* visual consistency
* interaction behavior
* browser/runtime health
* console errors
* failed network requests where applicable
* reduced-motion behavior where applicable
* implementation completion
* relevant performance evidence
* quality-gate decision provenance

## Benchmark independence

Do not promote the resulting visual style, fictional brand, layout, colors, typography, motion style, or aesthetic decisions into global ACOS memory simply because BM-001 succeeds.

Only genuinely generalizable lessons may become memory candidates through the existing certified memory process.

## Execution status

This input authorizes **PF-1 registration and freezing only**.

Do NOT execute BM-001 yet.

Do NOT start PF-2.

Register this input faithfully, derive measurable acceptance/evidence contracts without inventing unsupported product requirements, perform the certified two-step freeze, run PF-1/foundation regression validation, commit and push, then STOP.

# BM-001 REPOSITORY LOCATION — MANDATORY

BM-001 must remain **inside the existing `effect79automation` repository**.

Repository root:

`C:\Shahrukh\Effect79\effect79automation`

Canonical benchmark directory:

```text
C:\Shahrukh\Effect79\effect79automation\
└── benchmarks\
    └── BM-001\
        ├── ORIGINAL_INPUT.md
        ├── REGISTRATION.yaml
        ├── ACCEPTANCE_CONTRACT.yaml
        └── EVIDENCE_PLAN.yaml
```

For PF-1, create only the registration/freeze artifacts above.

Do NOT create BM-001:

* outside `effect79automation`
* in a sibling repository
* in a separate standalone project
* on Desktop/Documents/temp folders
* inside `projects/`
* inside `apps/`
* inside `runtime/`

All BM-001 benchmark registration artifacts must be tracked by the **same `effect79automation` Git repository**.

When future phases authorize actual benchmark execution, its implementation/evidence locations must follow the canonical ACOS benchmark structure defined by the repository at that phase. Do not invent an external project location now.

Before committing, verify:

`git rev-parse --show-toplevel`

must resolve to:

`C:\Shahrukh\Effect79\effect79automation`

Then perform the certified PF-1 source commit → freeze-attestation commit process and STOP.

PF-2 must remain NOT_STARTED.
