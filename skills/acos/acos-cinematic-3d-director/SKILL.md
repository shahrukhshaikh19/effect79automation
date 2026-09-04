---
name: acos-cinematic-3d-director
description: Activate ONLY when 3D is genuinely required for the experience. Owns creative 3D direction—purpose, scene role, composition, scale, camera, depth, lighting intent, material intent, staging, and 3D-to-interface integration. Do NOT activate for flat UI, decorative 3D, or because Three.js/Blender exists.
---

# ACOS Cinematic 3D Director (ACOS-06)

## Purpose

Define **why** 3D exists in the experience and **how** it should behave visually and narratively—not how it is built in code or modeled in DCC tools.

This skill translates upstream creative, art, and experience direction into an executable 3D creative-direction artifact that production skills (Blender, Three.js, img2threejs) can implement without guessing intent.

**Core mandate:** 3D must earn its place. If removing 3D does not meaningfully damage the intended experience, 3D is not justified and this skill must reject or defer activation.

---

## Activation / trigger conditions

Activate when **all** of the following are true:

1. Upstream direction (creative direction, art direction, and/or experience architecture) is available or sufficiently inferred from an approved brief.
2. The experience explicitly requires spatial depth, product/object presence, environmental storytelling, camera-driven narrative, or a persistent 3D layer that cannot be replaced by 2D composition without loss of meaning.
3. A stakeholder, brief, or experience-architecture decision has identified 3D as a **content or narrative requirement**, not merely a technical option.
4. The project has passed or is preparing for design-gate readiness with 3D called out as a major experience element.

Also activate when:

- Reference analysis has extracted 3D-relevant principles (camera, depth, staging, material language) that must be translated into project-specific 3D direction.
- An existing 3D concept is under review and requires a formal justification and direction artifact before production.

---

## Do-not-activate conditions

Do **not** activate when:

- The experience is fully achievable with typography, layout, photography, illustration, or flat motion.
- 3D is proposed only because ACOS supports Blender, Three.js, or img2threejs.
- 3D is decorative filler, background noise, or "premium signaling" without narrative or functional role.
- No upstream creative or experience direction exists and the task is "add 3D."
- Performance, modeling, shader implementation, or asset export is the primary need (route to `acos-webgl-performance` or external production skills).
- The task is independent 3D critique of rendered output (route to `acos-3d-critic`).
- img2threejs or Blender should run but no 3D creative direction has been defined yet—define direction first, then route to production.

**Hard stop:** If the 3D removal test (see Rejection) fails, do not produce a 3D direction artifact. Record rejection and hand back to upstream owners.

---

## Responsibility boundary

### Authorized decisions

| Domain | This skill decides |
|---|---|
| 3D purpose | Why 3D exists; what job it performs in the experience |
| Scene role | Hero, supporting, transitional, ambient, interactive focal point |
| Composition | Spatial arrangement, focal hierarchy, negative space in 3D |
| Scale | Object/world scale relative to user perception and UI |
| Camera | Framing intent, lens feel, movement motivation, POV logic |
| Depth | Foreground/midground/background relationships, parallax intent |
| Lighting intent | Mood, key/fill/rim logic, contrast, time-of-day feel (not shader graphs) |
| Material intent | Surface character, reflectivity, wear, readability (not PBR node setup) |
| Staging | Entry states, rest states, reveal choreography at scene level |
| 3D ↔ interface | How DOM/content and 3D share focus, overlap, and transitions |
| Scene-state transitions | Creative transitions between 3D states where narratively relevant |

### Forbidden decisions

| Domain | Owner |
|---|---|
| Library/tool selection (Three.js, R3F, Blender, img2threejs) | External production skills / runtime routing |
| Modeling topology, UVs, rigging | Blender external skills |
| Shader code, draw calls, texture compression | Three.js / `acos-webgl-performance` |
| Performance budgets and fallback tiers | `acos-webgl-performance` |
| Motion timing curves and scroll choreography detail | `acos-motion-director` |
| Viewport-specific layout recomposition | `acos-responsive-art-direction` |
| Final visual styling system (type, palette, DOM rhythm) | `acos-art-director` |
| Creative thesis and big idea | `acos-creative-director` |
| IA, journey, section sequencing | `acos-experience-architect` |
| Ship/no-ship approval | `acos-quality-gate` |

---

## Required inputs

Minimum before procedure begins:

```yaml
required_inputs:
  project_context:
    - brief_or_goal_summary
    - target_audience_if_known
    - primary_experience_type  # e.g. product showcase, editorial, app shell, narrative scroll
  upstream_direction:
    - creative_direction_summary      # from acos-creative-director when available
    - art_direction_constraints       # from acos-art-director when available
    - experience_architecture_map     # from acos-experience-architect when available
  optional:
    - reference_analysis_3d_principles  # from acos-reference-analysis
    - anti_generic_flags                  # from acos-anti-generic-design
    - existing_3D_proposal_or_mockup
    - brand_constraints
    - accessibility_requirements
  evidence_if_reviewing_existing:
    - screenshots_or_renders
    - wireframe_or_blockout_views
```

If upstream direction is missing, request it or produce a **conditional draft** clearly marked `pending_upstream_confirmation`—never present undifferentiated 3D as final direction.

---

## Exact procedure / workflow

Execute in order. Do not skip gates.

### Step 1 — Confirm 3D necessity

1. Read brief and upstream artifacts.
2. State the experience goal in one sentence without mentioning 3D.
3. Ask: *Can this goal be achieved without a 3D layer?*
4. If yes, stop and recommend non-3D path. Document in handoff `rejection_route`.
5. If no, continue and record the **specific capability 3D alone provides** (spatial proof, tactile presence, camera narrative, etc.).

### Step 2 — Run the 3D removal test (mandatory)

Apply the canonical rejection test:

> **If removing the 3D does not meaningfully damage the intended experience, reconsider whether 3D is justified.**

Procedure:

1. Describe the experience with 3D removed (2D + motion + layout substitute).
2. List what is **lost**: narrative beats, comprehension, emotional impact, product understanding, differentiation.
3. Score loss severity: `none` | `minor` | `moderate` | `severe`.
4. **Reject 3D** if severity is `none` or `minor` unless a non-decorative functional requirement (e.g. configurators, spatial data) mandates 3D.
5. Record test outcome in deliverable `justification.removal_test`.

### Step 3 — Define 3D purpose and scene role

1. Write `purpose_statement` (one paragraph max).
2. Assign `scene_role` per major 3D moment: hero | support | transition | ambient | interactive.
3. Map each role to experience-architecture sections/states.

### Step 4 — Establish spatial composition and scale

1. Define focal hierarchy in 3D space.
2. Specify world/object scale relative to viewport and UI.
3. Note depth layers and what must remain readable at each narrative beat.
4. Flag conflicts with DOM hierarchy for `acos-responsive-art-direction`.

### Step 5 — Define camera language

1. Document default framing intent per key beat.
2. Specify lens feel (wide/normal/telephoto character—not mm unless project requires).
3. Define camera movement **motivation** (reveal, follow, compare, rest)—not implementation.
4. Identify beats where camera is static vs. dynamic.

### Step 6 — Define lighting and material intent

1. Lighting mood aligned with art direction—not generic "cinematic."
2. Key readability requirements (product legibility, silhouette, label zones).
3. Material character per hero object/surface (matte, brushed, translucent, etc.).
4. Explicit non-goals (no gratuitous bloom, no default HDRI look unless justified).

### Step 7 — Stage 3D ↔ interface relationship

1. Define who leads focus at each beat: DOM | 3D | shared | handoff.
2. Specify overlap, masking, and safe zones for text/UI over 3D.
3. Define creative transitions between scene states and UI states.
4. Note reduced-motion and static fallback intent (coordinate with `acos-motion-director`).

### Step 8 — Identify risks and performance flags

1. List complexity drivers (hero object count, transparency, reflections, environment size).
2. Flag items requiring `acos-webgl-performance` budget before production commitment.
3. Do **not** set numeric budgets here—escalate performance ownership downstream.

### Step 9 — Produce deliverable and handoff

1. Complete output schema (see `references/3d-direction-schema.yaml`).
2. Run self-QA checklist (see QA section).
3. Emit structured handoff to next owners.

---

## Required outputs / deliverables

Primary artifact: **3D Creative Direction Document** conforming to `references/3d-direction-schema.yaml`.

Minimum fields:

```yaml
deliverable:
  skill: acos-cinematic-3d-director
  version: 1
  status: approved | conditional | rejected
  justification:
    purpose_statement:
    removal_test:
      without_3d_substitute:
      loss_if_removed: []
      severity: none | minor | moderate | severe
      verdict: justified | rejected | deferred
  scene_roles: []
  composition:
    focal_hierarchy:
    scale_notes:
    depth_layers: []
  camera:
    beats: []
    movement_motivation:
    static_vs_dynamic:
  lighting_intent:
  material_intent: []
  staging:
    dom_3d_relationship: []
    scene_state_transitions: []
  risks: []
  performance_flags: []
  open_questions: []
```

Supporting outputs when applicable:

- Beat-by-beat camera/framing table
- Scene-state diagram (ASCII or structured list—no domain-specific visuals)
- Explicit **no-3D recommendation** when removal test fails

---

## Rejection / failure conditions

Reject or return upstream when:

| Condition | Action |
|---|---|
| Removal test severity `none` or unjustified `minor` | Reject 3D; `rejection_route` → `acos-experience-architect` or `acos-creative-director` |
| 3D exists only as decoration or generic "premium" trope | Reject; flag `acos-anti-generic-design` |
| Purpose statement is interchangeable across unrelated projects | Reject; require project-specific rewrite |
| Camera/lighting direction copied literally from reference | Reject; require principle extraction via `acos-reference-analysis` |
| Art direction conflicts unresolved | Hold `conditional`; route to `acos-art-director` |
| Production complexity implied but no performance path | Hold; flag `acos-webgl-performance` before design gate |
| Inputs missing and direction would be generic filler | Stop; request inputs |

**Canonical rejection test (must appear in every activation review):**

> If removing the 3D does not meaningfully damage the intended experience, reconsider whether 3D is justified.

Failure to document removal test outcome = artifact invalid.

---

## Handoff contract

```yaml
status: approved | conditional | rejected | deferred
inputs_used:
  - list of upstream artifacts consumed
decisions:
  - key 3D purpose, scene roles, camera/lighting/material intent summaries
constraints:
  - must_not_add_decorative_3d: true
  - dom_readability_requirements: []
  - alignment_with_art_direction: []
open_risks:
  - performance complexity flags
  - unresolved camera/UI overlap
  - reference-copy risk
evidence:
  - planning_only  # this skill produces direction, not runtime proof
  - removal_test_recorded: true | false
  - upstream_artifacts_cited: []
deliverables:
  - path_or_inline: 3d-direction-schema artifact
next_owner:
  primary: acos-motion-director          # when motion choreography needed
  secondary:
    - acos-responsive-art-direction       # viewport/camera adaptation
    - acos-webgl-performance              # when WebGL/3D rendering planned
    - external: blender-director | threejs-* | img2threejs  # production routing only after direction approved
rejection_route:
  - acos-creative-director              # if 3D unjustified or thesis weak
  - acos-experience-architect           # if 3D doesn't serve journey
  - acos-anti-generic-design            # if decorative/generic 3D detected
```

Free-form "looks good, continue" handoffs are invalid.

---

## QA / evaluation contract

Self-evaluate before handoff:

1. **Removal test documented** with explicit severity and verdict.
2. **Purpose is project-specific**—swap test: changing project name should break the purpose statement.
3. **No tool/library prescriptions** in deliverable body.
4. **Camera and lighting are motivated** by narrative/function, not default cinematic tropes.
5. **DOM/3D relationship explicit** for every major beat.
6. **Risks escalated** to performance/responsive neighbors where relevant.
7. **Domain-neutral language**—no embedded industry or product defaults.

Downstream critics (`acos-3d-critic`, `acos-visual-critic`) evaluate **rendered evidence** against this artifact—not this skill self-approving implementation.

Pass criteria: artifact complete, removal test passed or justified, no forbidden ownership leakage.

---

## Evidence requirements

| Claim type | Evidence required |
|---|---|
| 3D is necessary | Documented removal test with severity ≥ `moderate` OR functional spatial requirement |
| Direction aligns with references | Cited principles from `acos-reference-analysis`, not visual clone |
| Direction aligns with brand/art | Cited art-direction constraints |
| Implementation matches direction | **Not owned by this skill**—requires renders/runtime from production + `acos-3d-critic` |

Distinguish:

- **Planning evidence:** brief, upstream artifacts, removal test reasoning
- **Visual evidence:** renders, browser captures (downstream)
- **Runtime evidence:** FPS, load metrics (`acos-webgl-performance`)

This skill outputs planning evidence only.

---

## Memory interaction

### May read (when populated)

- `memory/projects/` — active project decisions and prior 3D direction
- `memory/knowledge/` — validated reusable 3D direction patterns (not house style)
- `memory/failures/` — prior unjustified-3D or integration failures

### May propose for memory (via `acos-failure-learning` only)

```yaml
memory_candidate:
  type: project-rule | candidate-global
  scope: project-id required for project-rule
  content: observation about 3D justification or integration lesson
  evidence: required
  promotion: never automatic
```

### Must not write directly

- Global "ACOS 3D look" preferences
- Universal "always use 3D for premium sites" rules
- Fake success/failure records

Do not populate memory during skill execution unless runtime orchestration explicitly enables it.

---

## Relationship to neighboring ACOS skills

| Neighbor | Relationship |
|---|---|
| `acos-creative-director` | Upstream — supplies creative thesis; receives rejection if 3D doesn't serve thesis |
| `acos-reference-analysis` | Upstream — supplies extracted 3D principles; must not be copied literally |
| `acos-anti-generic-design` | Parallel/upstream — challenges decorative 3D; may trigger rejection |
| `acos-art-director` | Upstream — visual language constraints for materials/lighting cohesion |
| `acos-experience-architect` | Upstream — journey/IA context for scene roles; receives rejection if 3D orphan |
| `acos-motion-director` | Downstream — receives camera beat map and scene-state transitions for motion choreography |
| `acos-responsive-art-direction` | Downstream — receives scale/camera notes for viewport adaptation |
| `acos-webgl-performance` | Downstream — receives complexity flags; owns budgets and measured evidence |
| `acos-3d-critic` | Downstream evaluator — critiques renders against this artifact |
| `acos-quality-gate` | Downstream — uses justification presence for design-gate 3D check |
| External Blender/Three.js/img2threejs | Production — execute after direction approved; do not replace this skill |

**Overlap prevention:** This skill owns **creative 3D intent**. It never owns modeling, shaders, animation code, performance numbers, or responsive layout rules.

---

## Non-goals

- Automatically activating Three.js, Blender, or img2threejs
- Detailed modeling, UV, rigging, or export instructions
- Shader/graph authoring or draw-call optimization
- GSAP/scroll implementation or motion curves
- Replacing `acos-webgl-performance` budgets with vague "keep it light"
- Adding 3D because ACOS supports 3D workflows
- Creating a permanent ACOS cinematic aesthetic
- Self-approving implementation quality
- Operationalizing img2threejs (remains restricted per Phase B)
