# ACOS v1.2 Production Implementation Checklist

A checked box requires evidence.

**Phase map authority:** `registry/PHASES.yaml` — Foundation A–G; post-foundation PF-1..PF-5.

## A — Canonical foundation
- [x] repository created
- [x] canonical master committed
- [x] `AGENTS.md` committed
- [x] core policies committed
- [x] registry committed
- [x] tools/memory/benchmarks/adapters/model-profiles/projects structures created
- [x] exactly one canonical authority declared

## B — External skill import
- [x] 4 frontend/design/accessibility foundation entries handled
- [x] 10 selected Three.js skills handled
- [x] R3F production reference handled
- [x] 5 selected GSAP skills handled
- [x] 15 selected Blender skills handled
- [x] img2threejs P0 handled
- [x] no unapproved mega-pack import
- [x] provenance recorded
- [x] upstream revision/pin recorded where practical
- [x] license reviewed (34/36 explicit; EXT-FE-01/02 remain `LICENSE_REVIEW_REQUIRED` — `blocked_pending_license_review`)
- [x] executable scripts reviewed before execution
- [x] network/filesystem/tool permissions reviewed where relevant

## C — 14 proprietary ACOS skills
For every proprietary skill:
- [x] folder exists
- [x] valid `SKILL.md`
- [x] trigger conditions
- [x] responsibility boundary
- [x] required inputs
- [x] exact procedure
- [x] required outputs
- [x] rejection conditions
- [x] handoff contract
- [x] QA/evaluation contract
- [x] memory interaction
- [x] references/templates/rubrics when useful

Skills:
- [x] acos-creative-director
- [x] acos-reference-analysis
- [x] acos-anti-generic-design
- [x] acos-art-director
- [x] acos-experience-architect
- [x] acos-cinematic-3d-director
- [x] acos-motion-director
- [x] acos-responsive-art-direction
- [x] acos-webgl-performance
- [x] acos-visual-critic
- [x] acos-creative-critic
- [x] acos-3d-critic
- [x] acos-quality-gate
- [x] acos-failure-learning

## D — Production tool layer
- [x] Blender MCP classified/configured as tool
- [x] browser/Playwright classified/configured as tool
- [x] Git workflow
- [x] deterministic validation scripts
- [x] tools do not masquerade as skills
- [x] A–D certification hardening (DPR integrity, gate semantics, cross-phase validator)

## E — Thin platform/model adapters (NOT STARTED)
- [ ] Claude adapter
- [ ] Cursor adapter
- [ ] Codex adapter
- [ ] generic local/open-source adapter
- [ ] adapters thin
- [ ] model profile template
- [ ] migration workflow
- [ ] canonical intelligence not trapped in adapter/model

## F — Routing + memory + quality integration (NOT STARTED)
- [ ] knowledge memory runtime
- [ ] taste memory runtime
- [ ] projects memory runtime
- [ ] failures memory runtime
- [ ] successes memory runtime
- [ ] model-compatibility memory runtime
- [ ] promotion lifecycle implemented
- [ ] scoped retrieval strategy
- [ ] standard application task does not activate 3D unnecessarily
- [ ] interactive 3D task activates relevant route
- [ ] reference-image procedural object route can select img2threejs
- [ ] high-fidelity authored 3D route can select Blender
- [ ] active skill set remains scoped
- [ ] defects can route back to responsible skill

## G — Foundation validation / certification (NOT STARTED)
- [ ] integrated foundation validation pass
- [ ] hard reject + evidence blocker rules validated end-to-end
- [ ] creator/critic separation validated operationally
- [ ] visual signoff requires render/browser evidence (runtime)
- [ ] domain-neutrality audit pass
- [ ] no benchmark/project contamination in foundation
- [ ] foundation ready marker (FOUNDATION_READY) declared with evidence

## POST-FOUNDATION — PF roadmap (NOT STARTED)

Do not reuse Foundation phase letters for these items.

### PF-1 — Benchmark registration
- [ ] first real benchmark registered outside canonical foundation

### PF-2 — Correction from benchmark evidence
- [ ] ACOS corrections from benchmark evidence

### PF-3 — Generalization benchmarks
- [ ] additional benchmarks across domains/styles

### PF-4 — Scale infrastructure
- [ ] scale/orchestration infrastructure (if warranted)

### PF-5 — Fine-tuning (if evidence warrants)
- [ ] fine-tuning only with sufficient accepted/rejected examples
