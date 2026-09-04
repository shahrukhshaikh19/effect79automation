---
name: acos-webgl-performance
description: Activate ONLY when WebGL, WebGPU, or real-time 3D rendering is in scope. Owns rendering budgets, asset limits, DPR strategy, adaptive quality, loading strategy, GPU/memory awareness, fallback tiers, and target-device evidence requirements. Distinguish planned budget vs measured evidence vs optimization decision vs visual compromise.
---

# ACOS WebGL Performance (ACOS-09)

## Purpose

Define **experience-level WebGL/real-time 3D performance policy**—what the experience may cost on target devices, how it degrades gracefully, and what evidence proves claims—without choosing creative concept or writing Three.js implementation.

This skill bridges creative 3D/motion/responsive direction and technical production by making budgets, fallbacks, and measurement requirements explicit before and after implementation.

**Core mandate:** Distinguish **planned budget**, **measured evidence**, **optimization decision**, and **visual compromise**. Never claim achieved performance from source inspection alone when runtime evidence is required.

---

## Activation / trigger conditions

Activate **only when** WebGL, WebGPU, or real-time 3D rendering is relevant to the project:

1. `acos-cinematic-3d-director` or experience architecture commits to a live 3D layer in browser.
2. Three.js/R3F/WebGL production is planned or in progress.
3. Performance risk flags exist from creative direction (transparency, reflections, large environments, high poly heroes).
4. Responsive simplification tiers (`acos-responsive-art-direction`) require performance validation.
5. Quality gate or critics require performance evidence before ship.

Do **not** activate for flat DOM-only experiences with no real-time GPU rendering path.

---

## Do-not-activate conditions

Do **not** activate when:

- No WebGL/WebGPU/3D runtime rendering is planned or present.
- The task is general site performance (LCP, bundle size) with no GPU pipeline.
- Creative 3D direction has not been justified and project may still reject 3D (wait for `acos-cinematic-3d-director` or confirm 3D scope first).
- The ask is Three.js API/how-to implementation (route to external Three.js skills).
- Independent visual critique of aesthetics is primary (route to critics).

**Hard stop:** If rendering scope is undefined, defer until 3D scope is confirmed or explicitly marked exploratory with `conditional` status.

---

## Responsibility boundary

### Authorized decisions

| Domain | This skill decides |
|---|---|
| Rendering budgets | Poly, texture, material, draw-call, and scene complexity ceilings (planned) |
| Asset budgets | Max sizes, LOD intent, texture resolution tiers |
| DPR strategy | Device pixel ratio caps and when to reduce |
| Adaptive quality | Tier definitions and triggers for downgrade/upgrade |
| Loading strategy | Progressive load, idle/defer, placeholder intent |
| GPU pressure awareness | Effects/classes of work that stress mobile GPUs |
| Memory awareness | Texture/geometry memory risk flags |
| Fallback strategy | Static image, simplified scene, DOM substitute, disable 3D |
| Target-device evidence requirements | What must be measured, on which device classes |
| Performance degradation strategy | Ordered compromises before removing essential experience elements |
| Escalation | When creative elements must not be cut without upstream approval |

### Forbidden decisions

| Domain | Owner |
|---|---|
| Creative concept, 3D purpose, camera narrative | `acos-cinematic-3d-director` |
| Removing important experience elements unilaterally | Escalate to creative/experience owners |
| Shader/node implementation | External Three.js skills |
| GSAP animation implementation | External GSAP skills |
| Art direction and visual language | `acos-art-director` |
| Responsive composition rules | `acos-responsive-art-direction` |
| Ship/no-ship final verdict | `acos-quality-gate` (uses this skill's evidence) |

**Boundary rule:** This skill owns **policy, budgets, and evidence requirements**. Three.js performance skills own **implementation-specific technical practice**.

---

## Required inputs

```yaml
required_inputs:
  project_context:
    - brief_or_goal_summary
    - target_device_classes    # e.g. mid mobile, low mobile, desktop discrete GPU
    - network_context_if_known
  rendering_scope:
    - confirmed_webgl_in_scope: true
    - scene_description_summary
    - expected_user_session_length
  upstream_direction:
    - cinematic_3d_direction       # when available
    - responsive_simplification_tiers
    - motion_direction_summary     # when motion affects render load
  optional:
    - asset_inventory_estimates
    - existing_profiler_exports
    - prior_performance_incidents from memory/failures
  evidence_when_reviewing:
    - runtime_fps_samples
    - load_time_measurements
    - memory_profiler_snapshots
    - device_lab_results
```

---

## Exact procedure / workflow

### Step 1 — Confirm rendering scope

1. Verify WebGL/WebGPU/3D runtime is in scope; if not, stop and do not activate.
2. Summarize scene complexity drivers from 3D/responsive direction.
3. List target device classes and priority (which devices must pass vs. best-effort).

### Step 2 — Establish planned budgets (not claims)

Define **planned budgets** as upper bounds for production—clearly labeled `planned`, not `achieved`:

1. Geometry budget (hero + environment + instancing strategy intent)
2. Texture/material budget (resolution tiers, channel count intent)
3. Draw-call / batching awareness flags
4. Post-processing / transparency / reflection allowance
5. DPR cap policy per device class
6. Initial load vs. lazy-load asset split

Use `references/performance-evidence-schema.yaml` for structure.

### Step 3 — Define adaptive quality tiers

1. Tier 0: full experience (reference devices)
2. Tier 1–N: ordered reductions (lower DPR, fewer lights, simpler materials, reduced particles, static camera)
3. Trigger signals for tier change (FPS threshold intent, thermal hint, user preference)—implementation elsewhere
4. Map tiers to viewport classes when `acos-responsive-art-direction` defines simplification

### Step 4 — Loading and memory strategy

1. Define what loads first vs. deferred.
2. Flag memory-heavy assets and eviction intent.
3. Specify placeholder/skeleton behavior during load.

### Step 5 — Fallback strategy

1. Define graceful degradation terminus: simplified 3D → static render → DOM/2D substitute.
2. Specify when 3D must **not** silently fail (show explicit fallback UI).
3. Coordinate with reduced-motion and accessibility—fallback must preserve essential information.

### Step 6 — Evidence requirements matrix

For each budget and tier, specify:

```yaml
evidence_requirement:
  claim:                    # e.g. "Tier 1 holds 30fps on mid mobile"
  type: planned | measured
  required_measurement:     # e.g. 10s interaction trace, cold load
  device_class:
  pass_threshold:
  owner:                    # who captures evidence
```

**Rule:** Mark `achieved` claims only when `measured` evidence exists. Source review alone is insufficient for achieved FPS/load claims.

### Step 7 — Optimization vs. visual compromise log

When production proposes cuts:

1. Classify each item:
   - `optimization_decision` — no meaningful visual loss
   - `visual_compromise` — visible quality reduction
   - `experience_reduction` — removes creative element
2. `experience_reduction` requires escalation to `acos-cinematic-3d-director` / `acos-creative-director`—never silent removal.

### Step 8 — Produce deliverable and handoff

1. Complete performance policy artifact.
2. Run self-QA distinguishing planned vs measured.
3. Emit handoff to production and gate.

---

## Required outputs / deliverables

Primary artifact: **WebGL Performance Policy** per `references/performance-evidence-schema.yaml`.

```yaml
deliverable:
  skill: acos-webgl-performance
  version: 1
  status: approved | conditional | rejected
  rendering_scope_confirmed: true
  target_device_classes: []
  planned_budgets:
    geometry:
    textures:
    materials:
    draw_calls_awareness:
    dpr_caps: []
    post_processing_allowance:
  adaptive_quality_tiers: []
  loading_strategy:
  memory_flags: []
  fallback_strategy:
    tiers: []
    terminal_fallback:
  evidence_requirements: []
  optimization_log: []    # optimization_decision | visual_compromise | experience_reduction
  open_risks: []
  measured_results: []    # empty until runtime capture; clearly labeled when populated
```

---

## Rejection / failure conditions

| Condition | Action |
|---|---|
| WebGL not in scope | Do not activate; reject artifact if produced |
| Achieved performance claimed without measurement | Reject claim; downgrade to `planned` |
| Budget absent for confirmed 3D scope | Hold conditional until budgets defined |
| Fallback strategy missing | Reject |
| Experience elements removed without escalation | Reject; restore and route upstream |
| Source-only review presented as device proof | Reject evidence |
| Budgets copy generic defaults unrelated to scene | Reject; tie to scene drivers |
| Conflicts with responsive simplification unresolved | Hold; coordinate `acos-responsive-art-direction` |

**Four-way distinction (mandatory in artifact):**

| Label | Meaning |
|---|---|
| `planned_budget` | Pre-implementation ceiling |
| `measured_evidence` | Runtime/profile capture on target device class |
| `optimization_decision` | Change that preserves intent |
| `visual_compromise` | Visible quality trade accepted with documentation |

---

## Handoff contract

```yaml
status: approved | conditional | rejected
inputs_used: []
decisions:
  - planned budget summary
  - tier and fallback summary
  - evidence requirements list
constraints:
  - no_achieved_claims_without_measurement: true
  - experience_reduction_requires_escalation: true
open_risks:
  - mobile GPU pressure
  - texture memory
  - load time on slow networks
evidence:
  - planned_budgets_documented: true
  - measured_results_attached: false | true
  - distinction_four_way_maintained: true
deliverables:
  - performance-evidence-schema artifact
next_owner:
  primary: external threejs-* / R3F production skills
  secondary:
    - acos-quality-gate           # ship evidence check
    - acos-3d-critic              # visual integration may affect perf perception
    - acos-cinematic-3d-director  # experience_reduction escalations only
rejection_route:
  - acos-cinematic-3d-director    # if scope unjustified or too heavy for targets
  - acos-responsive-art-direction # if simplification tiers inadequate
  - production owner              # if measured evidence fails thresholds
```

---

## QA / evaluation contract

Before handoff:

1. **Scope confirmed** — WebGL/rendering genuinely in project.
2. All budgets labeled **`planned`**, not **`achieved`**, unless measurements attached.
3. **Fallback chain** complete to non-WebGL substitute.
4. **Evidence requirements** specify device class and measurement method.
5. **Four-way distinction** present in optimization log entries.
6. No creative direction rewritten—only constraints and compromises documented.
7. **Domain-neutral** — no embedded demo scene or product defaults.

`acos-quality-gate` checks evidence completeness before ship.

---

## Evidence requirements

| Claim type | Required evidence |
|---|---|
| Planned budget | This artifact; scene driver rationale |
| Achieved FPS/load/memory | Measured runtime on stated device class |
| Adaptive tier works | Tier transition trace or test session log |
| Fallback acceptable | Capture of fallback state + visual critic pass on essential info |
| Optimization sufficient | Before/after measurement pair |

**Prohibited:** Inferring achieved performance from code review, poly count in source alone, or developer machine smoke test as mobile proof.

Distinguish:

- **Planning evidence** — budgets, tiers, requirements (this skill)
- **Implementation evidence** — build artifacts, asset sizes (production)
- **Runtime evidence** — FPS traces, profiler, device lab (required for achieved claims)
- **Visual evidence** — compromise visibility (`acos-visual-critic`, `acos-3d-critic`)

---

## Memory interaction

### May read

- `memory/projects/` — prior budget decisions and measurement baselines
- `memory/knowledge/` — validated budget templates scoped by scene type (not universal law)
- `memory/failures/` — GPU OOM, mobile thermal throttling, false performance claims

### May propose (via `acos-failure-learning`)

```yaml
memory_candidate:
  type: project-rule | candidate-global
  scope: required
  content: budget miss, false claim pattern, effective tier strategy
  evidence: measured_data_required_for_global_candidates
```

### Must not write

- Fake profiler results
- Global "always cap at X fps" without scope
- One project's budget as ACOS default for all 3D

---

## Relationship to neighboring ACOS skills

| Neighbor | Relationship |
|---|---|
| `acos-cinematic-3d-director` | Upstream creative 3D intent; receives escalation for experience reduction |
| `acos-responsive-art-direction` | Bidirectional — simplification tiers vs. budget feasibility |
| `acos-motion-director` | Upstream — motion load flags |
| `acos-art-director` | Consult when visual compromise affects language |
| External Three.js / `threejs-performance` | Downstream implementation of policy |
| `acos-3d-critic` | Visual integration issues may imply perf perception problems |
| `acos-visual-critic` | Fallback and compromise visibility |
| `acos-quality-gate` | Enforces evidence before ship |
| `acos-failure-learning` | Records false claims and effective mitigations |

**Overlap prevention:** Creative 3D lives in cinematic director. Implementation tricks live in Three.js skills. This skill owns **budgets, degradation policy, and evidence discipline**.

---

## Non-goals

- Choosing the creative concept or rejecting 3D outright (escalate to cinematic/creative skills)
- Removing important experience elements without approval
- Replacing Three.js production or shader authoring
- Claiming performance from source inspection alone when runtime proof is required
- General DOM/bundle performance with no GPU pipeline
- Activating on non-WebGL projects
- Creating fake measurements or benchmark screenshots
- Operationalizing img2threejs or Blender MCP
