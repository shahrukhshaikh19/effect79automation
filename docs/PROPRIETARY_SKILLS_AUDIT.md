# ACOS v1.2 — Proprietary Skills Semantic Audit

**Phase:** C — Proprietary ACOS Skills  
**Date:** 2026-09-04  
**Authority:** `registry/SKILLS.yaml`, `phase-C.md` §21–22  
**Structural validation:** `validation/validate_proprietary_skills.py` — PASSED  
**Cross-skill review:** PASSED (no unresolved contradictions)

---

## Summary

All 14 proprietary skills under `skills/acos/` contain mandatory operational sections (activation, boundaries, procedure, handoff, evidence, memory, non-goals). No placeholder markers (`TODO`, `TBD`, etc.) detected. Domain-neutrality scan: no forbidden sample-project contamination (`coffee` keyword absent). External skills unmodified. Benchmarks/projects/tools remain empty.

---

## Per-skill audit

### ACOS-01 — acos-creative-director

| Field | Value |
|---|---|
| **Responsibility** | Central creative thesis, conceptual tension, experience-level principles, project-specific direction |
| **Activates when** | New project/redesign needs creative thesis; brief normalized; anti-generic or gate routed concept rework |
| **Must not activate when** | Direction locked; visual systems/IA/implementation tasks; no brief context |
| **Upstream inputs** | Normalized brief, project context, optional reference intelligence, anti-generic rejection |
| **Downstream handoff** | `acos-anti-generic-design` (primary); art/experience architects after pass |
| **Evidence type** | Creative direction artifact with thesis, principles, constraints, rejected territories |
| **Memory interaction** | Read prior direction for iteration; write project-scoped direction decisions only |
| **Nearest overlap risk** | Art Director (visual systems), Experience Architect (IA) |
| **Overlap prevention** | Explicit non-ownership of typography/palette/IA; thesis vs executable visual language |
| **References/templates** | `references/output-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-02 — acos-reference-analysis

| Field | Value |
|---|---|
| **Responsibility** | Extract reusable principles from supplied references without literal copying |
| **Activates when** | Reference assets supplied and interpretation required before direction/art/experience |
| **Must not activate when** | No references; clone request; direction locked; pure implementation |
| **Upstream inputs** | Reference assets/descriptions, brief, constraints |
| **Downstream handoff** | `acos-creative-director`, `acos-art-director`, or `acos-experience-architect` |
| **Evidence type** | Structured reference intelligence artifact (observation vs interpretation separated) |
| **Memory interaction** | Read prior analysis; write reference intelligence scoped to project |
| **Nearest overlap risk** | Creative Director (choosing thesis), Art Director (final visual language) |
| **Overlap prevention** | Stops when no references; does not choose final direction |
| **References/templates** | `references/output-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-03 — acos-anti-generic-design

| Field | Value |
|---|---|
| **Responsibility** | Stress-test proposals for generic AI tropes, sameness, unjustified defaults |
| **Activates when** | Creative direction or design proposal needs challenger review before execution |
| **Must not activate when** | Inventing house style; banning techniques globally; replacing CD/AD ownership |
| **Upstream inputs** | Creative direction or design proposal, brief, optional reference intelligence |
| **Downstream handoff** | Pass → art/experience architects; fail/challenge → `acos-creative-director` |
| **Evidence type** | Pass/challenge/fail report with specific genericness findings |
| **Memory interaction** | Read project context; may cite patterns; no global rule writes |
| **Nearest overlap risk** | Creative Critic (post-build concept review), Creative Director (thesis authorship) |
| **Overlap prevention** | Pre-execution challenger only; routes failures upstream to CD |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-04 — acos-art-director

| Field | Value |
|---|---|
| **Responsibility** | Executable visual language: composition, typography direction, hierarchy, palette logic, surfaces, DOM/WebGL cohesion |
| **Activates when** | Approved creative direction needs visual system specification |
| **Must not activate when** | Creative thesis undefined; IA-only tasks; implementation/library choice; final QA |
| **Upstream inputs** | Locked creative direction, experience architecture (if exists), reference intelligence |
| **Downstream handoff** | `acos-responsive-art-direction`, external production |
| **Evidence type** | Visual language specification artifact |
| **Memory interaction** | Read direction/IA; write project visual system decisions |
| **Nearest overlap risk** | Creative Director (thesis), Responsive Art Direction (viewport adaptation) |
| **Overlap prevention** | Owns base visual language; responsive skill owns per-viewport reframing |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-05 — acos-experience-architect

| Field | Value |
|---|---|
| **Responsibility** | User journey, IA, content progression, interaction hierarchy, experience pacing |
| **Activates when** | Journey/IA/progression must be defined for standard or immersive interfaces |
| **Must not activate when** | Final visual styling; stack choice; 3D-by-default without brief justification |
| **Upstream inputs** | Brief, creative direction, reference intelligence, constraints |
| **Downstream handoff** | Design gate readiness, responsive/3D/motion directors as applicable |
| **Evidence type** | Experience architecture artifact (sections, flows, hierarchy) |
| **Memory interaction** | Read brief/direction; write IA decisions scoped to project |
| **Nearest overlap risk** | Creative Director (concept), Art Director (visual hierarchy execution) |
| **Overlap prevention** | Owns structure/sequence; AD owns visual treatment of hierarchy |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-06 — acos-cinematic-3d-director

| Field | Value |
|---|---|
| **Responsibility** | Creative 3D direction when 3D genuinely required: scene role, composition, scale, camera, lighting/material intent, staging, 3D–UI integration |
| **Activates when** | Brief/experience requires real 3D; 3D role in experience must be defined |
| **Must not activate when** | Flat UI; decorative 3D without purpose; Three.js/Blender exists as default |
| **Upstream inputs** | Brief, creative direction, experience architecture, reference intelligence |
| **Downstream handoff** | `acos-motion-director`, `acos-responsive-art-direction`, external Blender/Three.js skills |
| **Evidence type** | 3D direction brief with purpose justification and integration plan |
| **Memory interaction** | Read direction/IA; write 3D creative decisions only |
| **Nearest overlap risk** | Blender/Three.js execution skills, WebGL Performance (budgets) |
| **Overlap prevention** | Creative intent only; execution delegated to external skills; budgets to ACOS-09 |
| **References/templates** | `references/3d-direction-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-07 — acos-motion-director

| Field | Value |
|---|---|
| **Responsibility** | Creative motion intent: purpose, choreography, pacing, hierarchy through movement, transitions, reduced-motion strategy |
| **Activates when** | Motion is a designed experience element with narrative or hierarchy role |
| **Must not activate when** | GSAP/tutorial tasks; micro-interaction code; motion not in scope |
| **Upstream inputs** | Creative direction, experience architecture, art direction, 3D direction (if applicable) |
| **Downstream handoff** | External `gsap-*` skills for execution |
| **Evidence type** | Motion intent specification (choreography, pacing, restraint rules) |
| **Memory interaction** | Read upstream direction; write motion intent scoped to project |
| **Nearest overlap risk** | GSAP external skills (implementation), Responsive Art Direction (viewport motion) |
| **Overlap prevention** | Explicit non-ownership of library APIs; intent vs code separation |
| **References/templates** | `references/motion-intent-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-08 — acos-responsive-art-direction

| Field | Value |
|---|---|
| **Responsibility** | Viewport-specific art direction: responsive composition, hierarchy shifts, re-framing, content priority, interaction adaptation, 3D/motion adaptation |
| **Activates when** | Multi-viewport experience design required |
| **Must not activate when** | Single fixed viewport only; base visual language undefined |
| **Upstream inputs** | Art direction, experience architecture, optional 3D/motion direction |
| **Downstream handoff** | Frontend implementation; `acos-webgl-performance` for simplification tiers |
| **Evidence type** | Per-breakpoint composition and priority strategy (not scale-down) |
| **Memory interaction** | Read base visual/IA; write viewport-specific decisions |
| **Nearest overlap risk** | Art Director (base language), WebGL Performance (adaptive quality) |
| **Overlap prevention** | Mobile ≠ desktop scaled down; performance budgets owned by ACOS-09 |
| **References/templates** | `references/viewport-strategy-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-09 — acos-webgl-performance

| Field | Value |
|---|---|
| **Responsibility** | WebGL/WebGPU/real-time 3D rendering budgets, asset limits, DPR strategy, adaptive quality, loading, GPU/memory awareness, fallback tiers |
| **Activates when** | WebGL, WebGPU, or real-time 3D rendering is in project scope |
| **Must not activate when** | DOM-only apps; non-WebGL performance; no 3D/real-time rendering |
| **Upstream inputs** | 3D direction, responsive strategy, target devices, art/asset constraints |
| **Downstream handoff** | External threejs/R3F skills; `acos-quality-gate` for ship evidence |
| **Evidence type** | Performance budget plan + measured evidence distinction |
| **Memory interaction** | Read project constraints; write budget decisions and measured results |
| **Nearest overlap risk** | Three.js performance external skill, Cinematic 3D Director (creative) |
| **Overlap prevention** | Only WebGL/real-time 3D scope; creative vs budget explicitly separated |
| **References/templates** | `references/performance-evidence-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-10 — acos-visual-critic

| Field | Value |
|---|---|
| **Responsibility** | Independent critique of rendered/browser visual evidence: hierarchy, composition, spacing, typography, polish, viewport defects |
| **Activates when** | Rendered or browser visual evidence exists for independent review |
| **Must not activate when** | Concept-only; code-only without render; same agent authored work without independence |
| **Upstream inputs** | Visual evidence (screenshots, browser captures), art direction spec, responsive strategy |
| **Downstream handoff** | `acos-quality-gate`; defect owners (AD, responsive) on fail |
| **Evidence type** | Visual critic report with evidence-linked defects |
| **Memory interaction** | Read specs; write critic findings; no auto-global rules |
| **Nearest overlap risk** | Creative Critic (concept), 3D Critic (geometry/materials) |
| **Overlap prevention** | Pixel/layout/hierarchy only; no concept originality judgment |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-11 — acos-creative-critic

| Field | Value |
|---|---|
| **Responsibility** | Independent judgment on originality, concept strength, project specificity, coherence, genericness |
| **Activates when** | Creative direction artifact exists and concept-level independent review required |
| **Must not activate when** | Render-only spacing defects; 3D geometry review; no creative claims in scope |
| **Upstream inputs** | Creative direction artifact, brief, reference intelligence, build context |
| **Downstream handoff** | `acos-quality-gate`; `acos-creative-director` on concept failures |
| **Evidence type** | Creative critic report with evidence-linked concept findings |
| **Memory interaction** | Read direction/brief; write critic findings scoped to evaluation |
| **Nearest overlap risk** | Visual Critic (pixel QA), Anti-Generic Design (pre-execution) |
| **Overlap prevention** | Post-direction/build concept review vs pre-execution challenger vs pixel QA |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-12 — acos-3d-critic

| Field | Value |
|---|---|
| **Responsibility** | Independent critique of actual 3D output: silhouette, geometry, materials, lighting, camera, scale, DOM/3D integration |
| **Activates when** | Runtime scene, renders, or inspectable 3D views exist |
| **Must not activate when** | DOM-only; code-only without 3D evidence; 2D layout QA |
| **Upstream inputs** | 3D evidence, 3D direction brief, integration context |
| **Downstream handoff** | `acos-quality-gate`; `acos-cinematic-3d-director` on 3D defects |
| **Evidence type** | 3D critic report with observable 3D defects |
| **Memory interaction** | Read 3D direction; write critic findings |
| **Nearest overlap risk** | Visual Critic (2D/layout), Cinematic 3D Director (creative authorship) |
| **Overlap prevention** | Requires actual 3D evidence; critic not creator |
| **References/templates** | — |
| **Review status** | PASS |

---

### ACOS-13 — acos-quality-gate

| Field | Value |
|---|---|
| **Responsibility** | Final ship/no-ship: APPROVED, REJECTED, or BLOCKED_INSUFFICIENT_EVIDENCE; HR-01..HR-10 artifact rejects; EB-01 evidence blocker |
| **Activates when** | Completion claimed; ship decision requested; evidence audit possible |
| **Must not activate when** | Mid-implementation; fix tasks; self-check only; design gate (pre-build) |
| **Upstream inputs** | Critic reports, domain evidence, `core/QUALITY_GATES.md` |
| **Downstream handoff** | APPROVED → `acos-failure-learning`; REJECTED → correction owners; BLOCKED_INSUFFICIENT_EVIDENCE → evidence collectors |
| **Evidence type** | Structured gate report (`references/gate-report-schema.yaml`) |
| **Memory interaction** | Read evidence/critic inputs; write gate outcome; no auto-global promotion |
| **Nearest overlap risk** | All critics (aggregation vs authorship) |
| **Overlap prevention** | Gate aggregates; never creates/fixes; missing evidence → BLOCKED_INSUFFICIENT_EVIDENCE not approval |
| **References/templates** | `references/gate-report-schema.yaml` |
| **Review status** | PASS |

---

### ACOS-14 — acos-failure-learning

| Field | Value |
|---|---|
| **Responsibility** | Record failures, corrections, and evidence-backed learnings; propose memory promotions with human validation |
| **Activates when** | Gate rejection, critic failures, correction loops complete, or approved outcome archival |
| **Must not activate when** | Mid-task speculation; writing global rules automatically; no evidence of failure/outcome |
| **Upstream inputs** | Gate report, critic reports, correction evidence, project scope |
| **Downstream handoff** | Project memory store; human validator for global promotion |
| **Evidence type** | Memory record proposals (`references/memory-record-schema.yaml`) |
| **Memory interaction** | Primary writer for failure/outcome records; global promotion requires explicit validation |
| **Nearest overlap risk** | Quality Gate (terminal decision), critics (finding authorship) |
| **Overlap prevention** | Never auto-promotes global rules; records and proposes only |
| **References/templates** | `references/memory-record-schema.yaml` |
| **Review status** | PASS |

---

## Cross-skill ownership matrix

Primary owner (P) vs consumer/critic (C) vs challenger (H) vs none (-).

| Concern | Primary | Secondary / Consumer |
|---|---|---|
| Reference extraction | **acos-reference-analysis (P)** | CD, AD, EA (C) |
| Creative thesis | **acos-creative-director (P)** | anti-generic (H), creative-critic (C) |
| Anti-generic challenge | **acos-anti-generic-design (P)** | CD (routes on fail) |
| Visual language (base) | **acos-art-director (P)** | visual-critic (C) |
| Experience / IA | **acos-experience-architect (P)** | AD (C), responsive (C) |
| 3D creative direction | **acos-cinematic-3d-director (P)** | 3d-critic (C), webgl-performance (C) |
| Motion creative direction | **acos-motion-director (P)** | gsap-* external (exec), responsive (C) |
| Responsive composition | **acos-responsive-art-direction (P)** | visual-critic (C), webgl-performance (C) |
| WebGL / real-time 3D performance | **acos-webgl-performance (P)** | threejs-* external (exec) |
| Visual (2D/layout) criticism | **acos-visual-critic (P)** | quality-gate (C) |
| Creative concept criticism | **acos-creative-critic (P)** | quality-gate (C) |
| 3D output criticism | **acos-3d-critic (P)** | quality-gate (C) |
| Final quality gate | **acos-quality-gate (P)** | all critics (inputs) |
| Learning / memory promotion | **acos-failure-learning (P)** | human validator (global) |

Each concern has exactly one primary owner. Critics consume upstream artifacts but do not co-own creative authorship.

---

## Cross-skill contradiction review (§22)

| Risk checked | Outcome |
|---|---|
| CD vs AD final visual authority | RESOLVED — CD owns thesis; AD owns executable visual language |
| AD vs EA both owning IA | RESOLVED — EA owns IA; AD owns visual treatment |
| Motion Director vs GSAP conflated | RESOLVED — intent vs external execution explicit |
| Cinematic 3D vs Blender/Three.js conflated | RESOLVED — creative direction vs production skills |
| Visual vs Creative critic duplication | RESOLVED — pixel/layout vs concept/originality split |
| 3D Critic on non-3D work | RESOLVED — requires actual 3D evidence |
| Quality Gate creating/fixing | RESOLVED — gate not creator; routes only |
| Failure Learning auto global rules | RESOLVED — proposal + human validation required |
| Responsive = scale-down | RESOLVED — explicit per-viewport reframing |
| WebGL Performance on non-WebGL | RESOLVED — activation gated to WebGL/WebGPU/RT3D |
| All 14 always activating | RESOLVED — each skill has explicit do-not-activate conditions |

**Review result:** No unresolved contradictions. Semantic audit PASS.

---

## Domain-neutrality

- Keyword scan (`coffee`): **CLEAN** across all 14 skills
- No embedded sample brands, default industries, or 3D-first assumptions detected
- Skills activate conditionally based on project scope, not ACOS defaults

---

## Implementation batches

| Batch | Skills | Files |
|---|---|---|
| 1 | reference-analysis, creative-director, anti-generic-design, art-director, experience-architect | 5 SKILL.md + 2 reference schemas |
| 2 | cinematic-3d-director, motion-director, responsive-art-direction, webgl-performance | 4 SKILL.md + 4 reference schemas |
| 3 | visual-critic, creative-critic, 3d-critic, quality-gate | 4 SKILL.md + 1 reference schema |
| 4 | failure-learning | 1 SKILL.md + 1 reference schema |

**Total:** 14 SKILL.md + 8 reference YAML files under `skills/acos/`

---

## Validator integration note

Phase A and Phase B validators updated with phase-aware proprietary skill check: zero skills (Phase A/B) or exactly 14 registry skills (Phase C+). Phase C validator chains A + B + proprietary structural/semantic checks.
