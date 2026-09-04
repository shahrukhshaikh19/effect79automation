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

## E — Thin platform/model adapters
- [x] Claude adapter (`adapters/claude/`, ADAPTER-CLAUDE-01)
- [x] Cursor adapter (`adapters/cursor/`, `.cursor/rules/acos-bootstrap.mdc`)
- [x] Codex adapter (`adapters/codex/`)
- [x] generic local/open-source adapter (`adapters/local/`)
- [x] shared contract `registry/ADAPTERS.yaml`
- [x] adapters thin — reference canonical authority, no skill body duplication
- [x] model profile template compatible; `registry/MODELS.yaml` remains empty pending benchmarks
- [x] migration path documented — canonical ACOS unchanged if platform removed
- [x] `validation/validate_adapters.py` PASSED

## F — Routing + memory + quality integration
- [x] knowledge memory runtime
- [x] taste memory runtime
- [x] projects memory runtime
- [x] failures memory runtime
- [x] successes memory runtime
- [x] model-compatibility memory runtime
- [x] promotion lifecycle implemented
- [x] scoped retrieval strategy
- [x] standard application task does not activate 3D unnecessarily
- [x] interactive 3D task activates relevant route
- [x] reference-image procedural object route can select img2threejs
- [x] high-fidelity authored 3D route can select Blender
- [x] active skill set remains scoped
- [x] defects can route back to responsible skill
- [x] `runtime/` integration modules + schemas
- [x] `registry/ROUTING_POLICY.yaml` + `registry/RUNTIME_POLICY.yaml`
- [x] `validation/validate_runtime_integration.py` PASSED
- [x] `validation/tests/runtime/test_scenarios.py` T1–T18 PASSED

## G — Foundation validation / certification (COMPLETE)
- [x] integrated foundation validation pass
- [x] hard reject + evidence blocker rules validated end-to-end
- [x] creator/critic separation validated operationally
- [x] visual signoff requires render/browser evidence (runtime)
- [x] domain-neutrality audit pass
- [x] no benchmark/project contamination in foundation
- [x] foundation ready marker (FOUNDATION_READY) declared with evidence

## POST-FOUNDATION — PF roadmap

### PF-1 — Benchmark registration (IN PROGRESS — operator contract approval pending)
- [x] registration framework (registry, templates, validator)
- [x] BM-001 v1.0 registered and frozen (historical — integrity defect in operator_confirmation)
- [ ] BM-001 v1.1 operator confirmation + freeze

### PF-2 — Correction from benchmark evidence (NOT STARTED)
- [ ] ACOS corrections from benchmark evidence

### PF-3 — Generalization benchmarks
- [ ] additional benchmarks across domains/styles

### PF-4 — Scale infrastructure
- [ ] scale/orchestration infrastructure (if warranted)

### PF-5 — Fine-tuning (if evidence warrants)
- [ ] fine-tuning only with sufficient accepted/rejected examples
