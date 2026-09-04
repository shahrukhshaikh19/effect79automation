# ACOS — FINAL CANONICAL OPERATING SYSTEM

**Version:** 1.2  
**Date:** 2026-09-04  
**Status:** FINAL FOUNDATION / EXECUTION READY — domain-neutral  
**Source of truth:** THIS FILE

## v1.2 change
Removed project-specific benchmark examples from the canonical foundation. ACOS must remain domain-neutral and must not prime an implementation model toward 3D product websites, or any other sample project before the foundation is operational.

`img2threejs` remains an approved P0 external skill, but it is only activated when a real project requires that capability.

---

# 1. NORTH STAR

ACOS is a model-agnostic Creative Engineering Operating System for building distinctive, production-grade digital products, cinematic websites, interactive 3D experiences, Blender assets, motion systems, and high-quality frontend applications.

The model is replaceable. ACOS is not.

```text
ACOS
├── Constitution
├── Workflow
├── Approved Skill Library
├── Skill Router
├── Tools
├── Quality Gates
├── Memory
├── Benchmarks
├── Model Compatibility Profiles
└── Thin Platform Adapters
```

**Skill != Tool != Model != Memory**

- **Skill** = procedural/domain expertise.
- **Tool** = Blender MCP, browser, Playwright, shell, Git, renderer, etc.
- **Model** = Claude, Codex/GPT, Gemini, Qwen, DeepSeek, another open model, etc.
- **Memory** = verified project and ACOS learning.
- **Adapter** = compatibility instructions for a particular agent/client.

---

# 2. NON-NEGOTIABLE LAWS

1. ACOS intelligence must survive replacement of the underlying model.
2. No model migration may require rebuilding ACOS knowledge from zero.
3. Canonical knowledge remains external to model weights.
4. Fine-tuning is optional specialization, never ACOS's only memory.
5. Meaningful visual work requires creative direction before full implementation.
6. "Premium" does not automatically mean gradients, glassmorphism, glow, rounded cards, giant centered headings, or excessive animation.
7. Every meaningful project requires a brand-specific creative thesis.
8. 3D must serve product, narrative, spatial, interaction, or emotional purpose.
9. Motion must serve hierarchy, state, narrative, physicality, continuity, or emotion.
10. DOM, WebGL, typography, lighting, camera, transitions, and sound when used are one composition.
11. Mobile is independently art-directed when required; it is not merely desktop scaled down.
12. Functional correctness, visual quality, creative quality, 3D quality, motion quality, accessibility, performance, and engineering quality are separate gates.
13. Visual changes must not silently alter business logic.
14. External skills/scripts/tools are dependencies and must be pinned and reviewed before updates.
15. Agents load the smallest sufficient skill set; they do not dump the entire library into context.
16. A creator does not grade its own work as the only reviewer; critic/gate responsibilities stay independent.
17. ACOS changes require benchmark evidence.
18. Brand diversity is mandatory; ACOS must not create one recurring house style for every client.
19. A build passing compilation is not proof of visual correctness.
20. For visual work, rendered/browser evidence is mandatory before signoff.

---

# 3. FINAL APPROVED EXTERNAL SKILL SET

## 3.1 Frontend / Design / QA — APPROVED

These are foundation references/skills. ACOS proprietary creative skills remain the final authority over creative intent.

| ID | Skill | Decision | Priority | Purpose |
|---|---|---|---|---|
| EXT-FE-01 | OpenAI Frontend App Builder | FORK/REFERENCE | P0 | design-first frontend production and concept-to-implementation fidelity |
| EXT-FE-02 | OpenAI Frontend Testing & Debugging | FORK/KEEP | P0 | rendered browser validation, responsive/console/interaction QA |
| EXT-DES-01 | Anthropic Design Critique | FORK/REFERENCE | P0 | structured design critique foundation |
| EXT-A11Y-01 | Web Accessibility | KEEP/REFERENCE | P0 | accessibility standards and implementation review |

Approved sources:

- OpenAI Frontend App Builder: https://github.com/openai/plugins/blob/main/plugins/build-web-apps/skills/frontend-app-builder/SKILL.md
- OpenAI Frontend Testing & Debugging: https://github.com/openai/plugins/blob/main/plugins/build-web-apps/skills/frontend-testing-debugging/SKILL.md
- Anthropic Design Critique: https://github.com/anthropics/knowledge-work-plugins/blob/main/design/skills/design-critique/SKILL.md
- Web Accessibility: https://github.com/magnus919/agent-skills/blob/main/web-accessibility/SKILL.md

**Not selected as v1 runtime skills:** broad UI/UX mega-packs and duplicate generic design packs. They may remain research references, but must not compete with ACOS Creative Director.

---

## 3.2 Three.js / R3F — APPROVED

Source pack: https://github.com/alton47/threejs-skills

ACOS v1 selects these individual skills:

| ID | Skill | Priority | Use |
|---|---|---|---|
| EXT-3DWEB-01 | threejs-core | P0 | renderer, scene, resize, render loop |
| EXT-3DWEB-02 | threejs-materials | P0 | PBR materials/maps/environment response |
| EXT-3DWEB-03 | threejs-lighting | P0 | lights, shadows, HDRI |
| EXT-3DWEB-04 | threejs-camera | P0 | camera/framing/controls implementation |
| EXT-3DWEB-05 | threejs-animation | P0 | Three animation system and GSAP integration |
| EXT-3DWEB-06 | threejs-loaders | P0 | GLTF/DRACO/KTX2/loading pipeline |
| EXT-3DWEB-07 | threejs-react | P0 | React Three Fiber/Drei integration |
| EXT-3DWEB-08 | threejs-performance | P0 | draw calls, LOD, culling, texture/render profiling |
| EXT-3DWEB-09 | threejs-shaders | P1 | custom GLSL when the concept requires it |
| EXT-3DWEB-10 | threejs-postprocessing | P1 | post FX when justified |

Not loaded by default:
- physics
- XR
- audio
- generic geometry

They may be promoted for a project only when the brief explicitly requires them.

Additional R3F reference:
https://github.com/shreyam1008/shre-skills/blob/main/skills/react-three-fiber/SKILL.md

Decision: **MERGE useful production rules into ACOS/R3F practice; do not create a second competing R3F authority.**

---

## 3.3 GSAP / Motion Implementation — APPROVED

Source pack: https://github.com/greensock/gsap-skills

Selected:

| ID | Skill | Priority | Use |
|---|---|---|---|
| EXT-MOTION-01 | gsap-core | P0 | core tween implementation |
| EXT-MOTION-02 | gsap-timeline | P0 | choreographed sequences |
| EXT-MOTION-03 | gsap-scrolltrigger | P0 | scroll-linked storytelling |
| EXT-MOTION-04 | gsap-react | P0 | React integration/lifecycle |
| EXT-MOTION-05 | gsap-performance | P0 | animation performance |

GSAP decides **how** motion executes.  
`acos-motion-director` decides **why, when, how much, pacing, narrative role, and whether motion should exist at all.**

Known rule: external skills are pinned/reviewed before update; do not blindly auto-update runtime skill content.

---

## 3.4 Blender Production — APPROVED CURATED SUBSET

Source pack:
https://github.com/arjun988/blender-skills

Guide:
https://github.com/arjun988/blender-skills/blob/main/SKILLS_GUIDE.md

ACOS does **not** install/activate the entire 94-skill pack for normal work.

Approved v1 Blender production subset:

| ID | Skill | Priority | Role |
|---|---|---|---|
| EXT-BLD-01 | blender-director | P0 | Blender task routing/production brief |
| EXT-BLD-02 | blender-modeler | P0 | core modeling, modifiers, organization |
| EXT-BLD-03 | prop-artist | P0 | product/hero prop construction |
| EXT-BLD-04 | uv-workflow | P0 | UV preparation |
| EXT-BLD-05 | materials | P0 | material construction |
| EXT-BLD-06 | lookdev | P0 | appearance validation |
| EXT-BLD-07 | camera-cinematography | P0 | camera/framing/lens |
| EXT-BLD-08 | lighting | P0 | lighting design implementation |
| EXT-BLD-09 | rendering | P0 | render configuration/output |
| EXT-BLD-10 | qa-review | P0 | Blender-specific technical review |
| EXT-BLD-11 | asset-optimization | P0 | web/runtime asset optimization |
| EXT-BLD-12 | export-pipeline | P0 | reliable handoff/export |
| EXT-BLD-13 | hard-surface | P1 | only for mechanical/precision hard-surface work |
| EXT-BLD-14 | geometry-nodes | P1 | procedural systems only when justified |
| EXT-BLD-15 | compositing | P1 | final offline render/composite when required |

Direct verified modeler skill:
https://github.com/arjun988/blender-skills/blob/main/.claude/skills/blender-modeler/SKILL.md

Geometry Nodes:
https://github.com/arjun988/blender-skills/blob/main/.claude/skills/geometry-nodes/SKILL.md

**Explicitly deferred from ACOS v1 default runtime:** character, creature, rigging, sculpting, hair, game genre packs, environment genre packs, XR/game-specific pipelines unless a project actually needs them.

---


## 3.5 Reference Image → Procedural Three.js Reconstruction — APPROVED

### EXT-IMG3D-01 — img2threejs

**Decision:** KEEP/FORK  
**Priority:** P0  
**Runtime role:** Reference Image → Procedural Three.js Reconstruction Specialist  
**Source:** https://github.com/img2threejs/img2threejs  
**Canonical skill:** https://github.com/img2threejs/img2threejs/blob/main/SKILL.md  
**Demo/gallery:** https://img2threejs.io/

`img2threejs` is an approved external ACOS skill. It is not merely a gallery or repository reference: the upstream project contains a real `SKILL.md` and a procedural reconstruction workflow.

### ACOS responsibility

Use it when the task is to reconstruct a visually convincing, browser-native, procedural Three.js object from one or more reference images.

Typical suitable targets:
- cups
- bottles
- cans
- headphones
- product packaging
- stylized props
- mechanical/product hero objects
- objects intended for interactive browser experiences

### Routing

```text
Reference Image(s)
      ↓
acos-reference-analysis
      ↓
acos-creative-director / acos-cinematic-3d-director
      ↓
img2threejs
      ↓
selected Three.js implementation skills
      ↓
acos-3d-critic
      ↓
acos-webgl-performance
      ↓
acos-quality-gate
```

### Boundary with Blender

`img2threejs` does **not** replace Blender.

Use `img2threejs` when:
- browser-native procedural construction is advantageous;
- geometry can be credibly reconstructed with procedural/code-driven methods;
- interactive Three.js delivery is the primary target;
- fast reference-driven iteration is valuable.

Prefer Blender + Blender MCP when:
- high-fidelity sculpting/modeling is required;
- hidden geometry must be deliberately authored;
- complex organic forms dominate;
- topology/UV/baking/offline asset workflows matter;
- the model must become a reusable production asset outside the procedural Three.js implementation;
- Blender-specific simulation or advanced asset authoring is required.

### Combined route

A project may use both:

```text
Reference analysis
   ↓
img2threejs for rapid procedural exploration/blockout
   ↓
ACOS 3D critique
   ↓
if procedural route passes → production Three.js
if fidelity/asset requirements exceed route → Blender production
```

Do not automatically send every reference-image task to Blender.

### Gallery classification

`https://img2threejs.io/` is a demo/reference surface, **not a separate runtime skill**.

Inventory:

```yaml
- id: EXT-IMG3D-01
  name: img2threejs
  type: external-skill
  priority: P0
  decision: KEEP/FORK
  role: reference-image-to-procedural-threejs-reconstruction
  source_repo: https://github.com/img2threejs/img2threejs
  skill_url: https://github.com/img2threejs/img2threejs/blob/main/SKILL.md

- id: REF-IMG3D-01
  name: img2threejs-gallery
  type: reference-demo
  runtime_skill: false
  url: https://img2threejs.io/
```


# 4. FINAL APPROVED TOOLS

Tools are not skills.

## TOOL-01 — Blender MCP
Primary:
https://github.com/MCPBlender/blender-mcp

Purpose:
- inspect Blender scene
- manipulate objects/materials/scenes
- execute Blender/Python workflows
- obtain visual/scene evidence
- bridge the agent to Blender

Rule: Blender MCP is execution infrastructure. It never replaces Blender skills or ACOS 3D direction.

## TOOL-02 — Browser / Playwright
Purpose:
- rendered UI inspection
- interaction verification
- console/runtime inspection
- responsive validation
- screenshot evidence
- visual comparison

## TOOL-03 — Git
Purpose:
- version control
- baseline preservation
- benchmark reproducibility
- safe rollback

## TOOL-04 — Shell / deterministic scripts
Purpose:
- builds
- tests
- asset checks
- deterministic transformations
- performance tooling

Security: inspect unknown external scripts before execution.

---

# 5. FINAL PROPRIETARY ACOS v1 SKILLS

These are **not optional research candidates**. These are the skills ACOS itself must own.

| ID | Skill | Priority | Responsibility |
|---|---|---|---|
| ACOS-01 | acos-creative-director | P0 | creative thesis, territories, brand-specific big idea |
| ACOS-02 | acos-reference-analysis | P0 | extract principles from references without copying |
| ACOS-03 | acos-anti-generic-design | P0 | detect/reject interchangeable AI design patterns |
| ACOS-04 | acos-art-director | P0 | composition, typography, visual hierarchy, visual language |
| ACOS-05 | acos-experience-architect | P0 | scenes, journey, interaction narrative, DOM/WebGL responsibility |
| ACOS-06 | acos-cinematic-3d-director | P0 | 3D purpose, camera language, lighting/material direction, product integration |
| ACOS-07 | acos-motion-director | P0 | motion purpose, pacing, transitions, scroll choreography |
| ACOS-08 | acos-responsive-art-direction | P0 | independent mobile/tablet composition/camera/motion strategy |
| ACOS-09 | acos-webgl-performance | P0 | WebGL/R3F asset/render budgets and fallback strategy |
| ACOS-10 | acos-visual-critic | P0 | independent rendered visual critique |
| ACOS-11 | acos-creative-critic | P0 | independent originality/brand/concept critique |
| ACOS-12 | acos-3d-critic | P0 | independent geometry/material/lighting/camera/integration critique |
| ACOS-13 | acos-quality-gate | P0 | hard ship/no-ship decision |
| ACOS-14 | acos-failure-learning | P0 | evidence-based memory and skill improvement |

**v1 count: 14 proprietary ACOS skills.**

Do not ask Claude/Cursor/Codex/local LLM to decide whether these should exist. They are part of the architecture.

---

# 6. PROPRIETARY SKILL CONTRACT

Every proprietary skill must use an Agent Skills-compatible folder:

```text
skills/acos/<skill-name>/
├── SKILL.md
├── references/
├── assets/       # only when useful
└── scripts/      # only deterministic helpers when justified
```

Every `SKILL.md` must contain:

1. trigger conditions
2. responsibility boundary
3. required inputs
4. exact workflow
5. required outputs
6. rejection/failure conditions
7. handoff contract
8. QA/evaluation contract
9. memory interaction rules
10. examples/eval cases where useful

Never write weak instructions such as:
> "Act as a world-class creative director."

The skill must encode an operational procedure.

---

# 7. SKILL ROUTER — FINAL RULES

The agent is allowed to **route**, not to **shortlist the foundation**.

It must:

1. classify the task;
2. inspect approved skill metadata;
3. activate the smallest sufficient subset;
4. normally keep active specialist skills around 3–8 at one time;
5. load references only when needed;
6. unload/stop consulting irrelevant skills as the phase changes.

Examples:

### 3D product website
```text
acos-reference-analysis
acos-creative-director
acos-anti-generic-design
acos-art-director
acos-experience-architect
→ DESIGN GATE
acos-cinematic-3d-director
selected Blender skills
threejs-core/materials/lighting/camera/loaders/react/performance
gsap core/timeline/scrolltrigger/react/performance
acos-motion-director
acos-responsive-art-direction
acos-webgl-performance
→ browser QA
acos-visual-critic
acos-creative-critic
acos-3d-critic
acos-quality-gate
```

### Normal SaaS/product UI
Do not invoke Blender/Three.js just because ACOS has them.

```text
acos-reference-analysis
acos-creative-director
acos-anti-generic-design
acos-art-director
acos-experience-architect
frontend-app-builder
accessibility
frontend-testing-debugging
acos-responsive-art-direction
acos-visual-critic
acos-creative-critic
acos-quality-gate
```

---

# 8. PRODUCTION WORKFLOW — FINAL

```text
BRIEF
  ↓
REFERENCE ANALYSIS
  ↓
CREATIVE DIRECTION
  ↓
ANTI-GENERIC REVIEW
  ↓
ART DIRECTION
  ↓
EXPERIENCE ARCHITECTURE
  ↓
DESIGN GATE
  ↓
TECHNICAL PLAN
  ↓
SPECIALIST PRODUCTION
  ├── Frontend
  ├── Blender
  ├── Three.js / R3F
  └── GSAP / Motion
  ↓
INTEGRATION
  ↓
RENDER / BROWSER INSPECTION
  ↓
FUNCTIONAL QA
  ↓
VISUAL QA
  ↓
CREATIVE QA
  ↓
3D + MOTION QA
  ↓
PERFORMANCE + ACCESSIBILITY QA
  ↓
QUALITY GATE
  ├── REJECTED → route defect to responsible upstream skill
  ├── BLOCKED_INSUFFICIENT_EVIDENCE → collect/repair evidence
  └── APPROVED
  ↓
SHIP
  ↓
FAILURE/SUCCESS MEMORY
```

No full implementation before Design Gate for meaningful creative projects.

---

# 9. DESIGN GATE

Before production, answer:

- Could another brand use this concept almost unchanged?
- Is there one memorable/signature idea?
- Does the concept express the actual brand/product?
- Is hierarchy clear?
- Is typography intentional?
- Does 3D have a reason to exist?
- Does motion have a reason to exist?
- Are DOM and WebGL conceived together?
- Is mobile separately considered?
- Is it feasible inside performance/accessibility constraints?

Critical failure = revise before coding.

---

# 10. QUALITY GATES

Score relevant dimensions 0–10:

- creative originality
- brand distinctiveness
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

Scores are diagnostic. Hard failures override averages.

## Hard reject

`SHIP: REJECTED` if a relevant critical issue exists:

- broken primary flow
- serious console/runtime errors
- unusable target viewport
- critical accessibility blocker
- unacceptable frame rate/resource behavior on target class
- missing critical fallback
- major reference/product mismatch when fidelity is mandatory
- obvious 3D credibility defect
- visual work breaks existing business logic
- materially generic/interchangeable design despite differentiated brief

Evidence insufficiency is **not** an artifact hard reject — see Evidence Blockers.

## Evidence blockers

When required evidence is missing, invalid, stale, contradictory, or unverifiable:

- **EB-01** — required evidence insufficient → **BLOCKED_INSUFFICIENT_EVIDENCE**

EB blockers are evaluation-state failures, not artifact-quality rejection.

## Terminal gate status

Three terminal outcomes — hard failures override averages:

| Status | Meaning |
|---|---|
| **APPROVED** | Required evidence exists; applicable gates pass; may ship |
| **REJECTED** | Sufficient evidence to evaluate; critical/unacceptable failure demonstrated |
| **BLOCKED_INSUFFICIENT_EVIDENCE** | Cannot make reliable ship/no-ship judgment; evidence insufficient — nothing may ship |

BLOCKED is not approval. BLOCKED is not artifact-quality rejection.

---

# 11. MEMORY SYSTEM

Never use one giant unstructured memory dump.

```text
memory/
├── knowledge/
├── taste/
├── projects/
├── failures/
├── successes/
└── model-compatibility/
```

Failure record:

```yaml
id:
project:
date:
domain:
problem:
evidence:
root_cause:
correction:
affected_skills:
scope:
confidence:
status:
```

Promotion:

```text
observation
→ project-rule
→ candidate-global
→ validated-global
→ deprecated
```

One model's mistake is not automatically a universal ACOS rule.

---

# 12. MODEL INDEPENDENCE / ZERO-RETRAINING MIGRATION

The model is replaceable infrastructure.

```text
ACOS external brain
├── skills
├── memory
├── quality gates
├── benchmarks
├── project history
├── accepted/rejected examples
└── compatibility profiles
        ↓
    MODEL ADAPTER
        ↓
Claude / Codex / GPT / Gemini / Qwen / DeepSeek / future local model
```

When a model/version changes:

```text
REGISTER
→ CREATE COMPATIBILITY PROFILE
→ RUN BENCHMARKS
→ COMPARE WITH APPROVED BASELINE
→ IDENTIFY REGRESSIONS
→ ADAPT THIN ADAPTER / ROUTING / SKILL BATCHING
→ RE-RUN FAILED BENCHMARKS
→ APPROVE / RESTRICT / REJECT
```

**Never retrain ACOS from zero merely because the model changed.**

Model profile:

```yaml
id:
provider:
model:
version:
deployment:
acos_version:
adapter:
context_window:
tool_support:
skill_support:
strengths: []
weaknesses: []
known_quirks: []
required_overrides: []
benchmark_results: {}
resource_requirements: {}
status: candidate
last_tested:
```

Fine-tuning may later improve specialization, but current truth, skills, memory, procedures, project history, and benchmark evidence remain external.

---

# 13. PLATFORM ADAPTERS

Canonical intelligence lives in ACOS, not in platform-specific files.

```text
adapters/
├── claude/
├── cursor/
├── codex/
├── opencode/
└── generic-local/
```

Adapters are thin.

They may specify:
- where the platform discovers skills;
- how it reads canonical instructions;
- tool/MCP configuration;
- context limitations;
- model-specific workarounds.

They must **not** contain the only copy of important ACOS knowledge.

---

# 14. LOCAL / OPEN-SOURCE LLM BOOTSTRAP

A paid subscription is not required to preserve ACOS intelligence.

If a local agent supports Agent Skills, use the canonical skill tree.

If it does not, give it this bootstrap:

```text
You are operating under ACOS.

1. Read the canonical ACOS instructions.
2. Read the Constitution.
3. Read the current project brief.
4. Read the approved skill registry.
5. Classify the current task.
6. Activate only the approved skills relevant to this phase.
7. Load each selected SKILL.md.
8. Load references only when required.
9. Follow the ACOS production workflow.
10. Apply all relevant quality gates.
11. Do not invent or replace foundation skills.
12. Do not modify global ACOS memory from one observation.
13. Inspect external scripts before executing them.
14. For visual work, inspect rendered/browser evidence before signoff.
15. Report active skills, evidence, failures, and final gate status.
```

A smaller local model may require:
- smaller skill batches;
- shorter tasks;
- more deterministic scripts;
- explicit checkpoints;
- more frequent QA.

That is an adapter/routing issue, not a reason to rebuild ACOS.

---

# 15. CANONICAL REPOSITORY

```text
ACOS/
├── AGENTS.md
├── README.md
├── core/
│   ├── CONSTITUTION.md
│   ├── WORKFLOW.md
│   ├── ROUTING.md
│   ├── QUALITY_GATES.md
│   ├── MEMORY_POLICY.md
│   └── MODEL_MIGRATION.md
├── registry/
│   ├── SKILLS.yaml
│   └── MODELS.yaml
├── skills/
│   ├── external/
│   │   ├── frontend/
│   │   ├── threejs/
│   │   ├── img2threejs/
│   │   ├── gsap/
│   │   └── blender/
│   └── acos/
│       ├── acos-creative-director/
│       ├── acos-reference-analysis/
│       ├── acos-anti-generic-design/
│       ├── acos-art-director/
│       ├── acos-experience-architect/
│       ├── acos-cinematic-3d-director/
│       ├── acos-motion-director/
│       ├── acos-responsive-art-direction/
│       ├── acos-webgl-performance/
│       ├── acos-visual-critic/
│       ├── acos-creative-critic/
│       ├── acos-3d-critic/
│       ├── acos-quality-gate/
│       └── acos-failure-learning/
├── tools/
│   ├── blender-mcp/
│   ├── browser/
│   └── validation/
├── memory/
├── benchmarks/
├── adapters/
└── projects/
```

---

# 16. BENCHMARKS

ACOS benchmarks must be registered **after** the foundation is implemented and validated.

The canonical foundation must not prescribe a specific product, visual style, industry, or reference experience.

A benchmark should be introduced as a separate project package containing:
- brief
- references
- assets
- baseline implementation where applicable
- target constraints
- target devices
- performance expectations
- success criteria
- evaluation rubric
- accepted/rejected evidence

Recommended benchmark diversity:
- one non-3D product/interface project
- one interactive/3D project when required
- one visually different domain to test generalization

The purpose of benchmarks is to measure whether ACOS improves reasoning, originality, execution quality, consistency, and QA without overfitting the system to one aesthetic or product category.

Do not add project-specific benchmark content to the canonical ACOS foundation.


# 17. EXECUTION PLAN — NO MORE SHORTLISTING

## PHASE A — Foundation
1. Create canonical repo.
2. Commit this architecture.
3. Create registry and directory structure.
4. Pin approved external sources.
5. Security/license review before importing executable scripts.

## PHASE B — Import approved external skills
Import only the approved v1 list from Section 3, including `EXT-IMG3D-01 img2threejs`.

For `img2threejs`, pin/review the upstream `SKILL.md` and preserve its ACOS responsibility boundary with Blender.

Do **not** ask the implementation model:
- "Which skills should we use?"
- "Find the best skill pack."
- "Choose between these repositories."
- "Design an ACOS architecture."

Those decisions are already made.

## PHASE C — Build 14 proprietary skills
Create the 14 ACOS skills from Section 5 using the contract in Section 6.

## PHASE D — Tools
Configure:
- Blender MCP
- browser/Playwright
- Git
- deterministic validation scripts

## PHASE E — Thin platform/model adapters
Create thin:
- Claude adapter
- Cursor adapter
- Codex adapter
- generic local/open-source adapter

## PHASE F — Routing + memory + quality integration
Implement routing runtime, memory stores, and quality integration as one foundation phase.

## PHASE G — Foundation validation / certification
Run integrated foundation validation. Declare **FOUNDATION READY** only after Phase G passes.

---

## POST-FOUNDATION ROADMAP (PF-* — not Foundation phases)

Benchmarks and scale work occur **only after FOUNDATION READY**. Do not reuse Foundation phase letters.

| ID | Name |
|---|---|
| **PF-1** | Benchmark registration |
| **PF-2** | Correction from benchmark evidence |
| **PF-3** | Generalization benchmarks |
| **PF-4** | Scale infrastructure |
| **PF-5** | Fine-tuning (only if evidence warrants) |

Machine-readable phase map: `registry/PHASES.yaml`

---

# 18. WHAT WE ARE NOT DOING NOW

- not installing 90+ Blender skills into every context;
- not making an LLM shortlist its own foundation;
- not building a GetLayers competitor first;
- not fine-tuning before a dataset exists;
- not renting expensive GPU infrastructure before ACOS v1 proves value;
- not building a giant multi-agent hierarchy before the single-agent workflow works;
- not storing ACOS knowledge only in model weights;
- not making Claude/Cursor/Codex-specific files the source of truth;
- not blindly auto-updating external skills;
- not judging quality from compilation alone.

---

# 19. FINAL APPROVED COUNTS

ACOS v1 foundation contains:

- **4** external frontend/design/accessibility foundation skills
- **10** selected Three.js skills
- **5** selected GSAP skills
- **15** selected Blender skills (12 P0 + 3 P1)
- **1** additional R3F reference merged into practice
- **1** P0 `img2threejs` reference-image → procedural Three.js reconstruction skill
- **14** proprietary ACOS skills
- Blender MCP + Browser/Playwright + Git + Shell as tools

The router activates only the relevant subset for a task.

The implementation model does **not** shortlist these again.

---

# 20. FIRST COMMAND TO THE IMPLEMENTATION AGENT

Use this when execution begins:

```text
Implement ACOS v1 exactly from the canonical ACOS specification provided to you.

Important:
- The architecture and approved skill shortlist are already decided.
- Do not perform another skill-discovery or architecture-selection exercise.
- Do not substitute your own framework.
- Build the canonical repository structure first.
- Import/pin only the approved external v1 skills.
- Then implement the 14 proprietary ACOS skills using the required skill contract.
- Keep Skill, Tool, Model, Memory, and Adapter separate.
- Keep platform adapters thin.
- Preserve model independence and zero-retraining migration.
- Do not start the redesign until the ACOS v1 foundation passes structural validation.
- Maintain a progress ledger with completed, blocked, and next items.
- Stop and report only for a genuine blocker requiring human input; otherwise continue through the execution plan.
```

---

# 21. FINAL STATUS

**Architecture:** LOCKED  
**External skill shortlist:** LOCKED for ACOS v1  
**Proprietary skill list:** LOCKED for ACOS v1  
**Tools:** LOCKED for initial implementation  
**Model independence:** LOCKED  
**Zero-retraining migration:** LOCKED  
**First benchmark:** NOT PREDEFINED IN FOUNDATION  
**Next action:** IMPLEMENT FOUNDATION, not research.
