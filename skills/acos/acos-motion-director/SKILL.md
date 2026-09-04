---
name: acos-motion-director
description: Owns creative motion intent—purpose, choreography, pacing, hierarchy through movement, narrative progression, transition logic, interaction feedback, restraint, and reduced-motion strategy. Activate when motion is a designed experience element. Do NOT become a GSAP tutorial or mandate animation libraries.
---

# ACOS Motion Director (ACOS-07)

## Purpose

Define **why motion exists**, **what it communicates**, and **how movement relates across the experience**—not how tweens are coded or which animation library to install.

This skill produces a motion-direction artifact that external motion skills (GSAP and others) implement as faithful executors of creative intent.

**Core mandate:** Motion must have communicative, spatial, narrative, or interaction purpose. Motion without purpose is a defect to reject or remove.

---

## Activation / trigger conditions

Activate when **any** of the following apply:

1. The experience includes designed transitions, scroll-linked narrative, state changes, or micro-interactions where timing and choreography affect comprehension or feel.
2. Upstream art direction or experience architecture specifies motion as part of the language (enter/exit, emphasis, pacing).
3. A 3D direction artifact (`acos-cinematic-3d-director`) includes scene-state transitions requiring motion choreography.
4. Interaction feedback language (hover, press, success, error, loading) must be defined at experience level before implementation.
5. Reduced-motion and accessibility strategy for movement must be specified.

Activate for both immersive experiences and standard interfaces when motion is intentional—not only for "cinematic" projects.

---

## Do-not-activate conditions

Do **not** activate when:

- The interface is intentionally static and brief confirms no meaningful motion.
- The task is purely technical: "fix GSAP bug," "optimize animation FPS," "implement ScrollTrigger syntax."
- Motion is requested as random decoration without narrative or functional role.
- No upstream direction exists and the ask is "add animations to make it premium."
- Library selection or API usage is the primary question (route to external GSAP skills).
- Independent critique of rendered motion in browser is needed (route to `acos-visual-critic` after evidence exists).

**Hard stop:** If motion purpose cannot be stated in one sentence per major motion group, do not approve motion—reject or defer.

---

## Responsibility boundary

### Authorized decisions

| Domain | This skill decides |
|---|---|
| Motion purpose | Why movement exists; what user understands/feels because of it |
| Choreography | Sequence relationships, simultaneous vs. staggered intent |
| Timing relationships | Relative pacing between groups (fast/slow, pause, acceleration feel) |
| Hierarchy through motion | What moves first, what follows, what stays still |
| Narrative progression | How motion advances story, section logic, or task flow |
| Transition logic | Enter/exit/morph/handoff rules between states and sections |
| Interaction feedback | Hover, focus, press, toggle, success/error motion language |
| Motion restraint | What must **not** move; maximum motion density |
| Reduced-motion intent | What simplifies, replaces, or disables under `prefers-reduced-motion` |
| Scroll choreography (creative) | What scroll **means** narratively—not scroll plugin config |

### Forbidden decisions

| Domain | Owner |
|---|---|
| GSAP/API syntax, plugin choice, React lifecycle hooks | External GSAP skills |
| Animation performance profiling and GPU layer hacks | `gsap-performance` / frontend |
| 3D camera animation implementation | Three.js / Blender external skills |
| 3D scene purpose and camera motivation | `acos-cinematic-3d-director` |
| Layout, typography, color, composition rules | `acos-art-director` |
| IA, section order, content priority | `acos-experience-architect` |
| Viewport-specific layout recomposition | `acos-responsive-art-direction` |
| WebGL frame budgets | `acos-webgl-performance` |
| Ship/no-ship | `acos-quality-gate` |

**Boundary rule:** GSAP decides **how** motion executes. This skill decides **why, when, how much, pacing, narrative role, and whether motion should exist at all.**

---

## Required inputs

```yaml
required_inputs:
  project_context:
    - brief_or_goal_summary
    - experience_type
    - interaction_model  # scroll, click, drag, hybrid
  upstream_direction:
    - creative_direction_summary
    - art_direction_summary          # rhythm, hierarchy, visual tempo
    - experience_architecture_map    # sections, states, transitions
  optional:
    - cinematic_3d_direction         # scene-state transitions from acos-cinematic-3d-director
    - reference_motion_principles    # from acos-reference-analysis
    - anti_generic_flags
    - accessibility_requirements
    - brand_motion_constraints_if_any
  evidence_if_reviewing_existing:
    - screen recordings or prototype captures
    - interaction flow diagrams
```

---

## Exact procedure / workflow

### Step 1 — Inventory motion demand

1. List every experience beat that implies change over time (section enters, modal opens, 3D state shift, form feedback).
2. Mark each: `required` | `optional` | `unnecessary`.
3. Remove `unnecessary` items unless upstream mandates them with purpose.

### Step 2 — Define motion principles (project-specific)

1. Write 3–5 motion principles tied to project thesis—not generic "smooth and premium."
2. Define default **tempo** character: urgent | measured | playful | solemn | neutral.
3. Define **density ceiling**: max concurrent moving elements per viewport.

### Step 3 — Purpose test per motion group

For each group (page transitions, hero reveal, scroll beats, micro-interactions, 3D handoffs):

1. Write `purpose` in one sentence.
2. Classify primary role: `communicative` | `spatial` | `narrative` | `interaction` | `decorative`.
3. **Reject** if primary role is `decorative` unless art direction explicitly treats decoration as branded language with justification.

### Step 4 — Choreography and hierarchy

1. Define order of operations for multi-element sequences.
2. Specify what anchors ( stays static ) to preserve readability.
3. Map motion hierarchy to visual hierarchy from art direction.

### Step 5 — Transition logic

1. Document enter/exit rules between major sections and UI states.
2. Define continuity devices (shared element, fade, hard cut, spatial slide) at intent level.
3. Specify forbidden transitions (e.g. gratuitous spin, random bounce) when they violate direction.

### Step 6 — Scroll and narrative pacing (when applicable)

1. Define what each scroll phase **reveals or emphasizes**—not scroll distances in pixels.
2. Specify pause points and acceleration intent.
3. Hand off viewport-specific scroll behavior differences to `acos-responsive-art-direction`.

### Step 7 — Interaction feedback language

1. Define feedback for primary interactions: hover, focus-visible, active, disabled, loading, success, error.
2. Ensure feedback is distinguishable without relying on motion alone (accessibility).
3. Keep feedback consistent across the experience.

### Step 8 — Restraint and reduced-motion

1. List elements that must never animate.
2. Define `prefers-reduced-motion` strategy: substitute (crossfade/instant), simplify (opacity only), or disable.
3. Confirm essential information is available with motion off.

### Step 9 — Produce deliverable and handoff

1. Complete `references/motion-intent-schema.yaml`.
2. Run self-QA.
3. Emit structured handoff—**no GSAP code, no API names as requirements**.

---

## Required outputs / deliverables

Primary artifact: **Motion Direction Document** per `references/motion-intent-schema.yaml`.

Minimum structure:

```yaml
deliverable:
  skill: acos-motion-director
  version: 1
  status: approved | conditional | rejected
  motion_principles: []
  tempo_character:
  density_ceiling:
  groups:
    - id:
      purpose:
      role: communicative | spatial | narrative | interaction
      choreography:
      timing_relationship:
      hierarchy_notes:
      transition_logic:
      restraint_notes:
  scroll_choreography:        # omit if N/A
  interaction_feedback: []
  reduced_motion:
    strategy:
    substitutes: []
  rejected_motion: []         # decorative or unjustified items removed
  open_questions: []
```

---

## Rejection / failure conditions

| Condition | Action |
|---|---|
| Motion group purpose is decorative without justification | Reject group or entire motion scope |
| Purpose statement generic across projects | Reject; rewrite project-specific |
| Motion competes with readability/hierarchy | Reject or reduce; coordinate `acos-art-director` |
| Motion mandated "for premium feel" only | Reject; route `acos-anti-generic-design` |
| Choreography copied literally from reference | Reject; require principle-based direction |
| Reduced-motion strategy missing | Hold conditional until complete |
| Deliverable contains GSAP/tutorial implementation | Invalid artifact; strip and rewrite as intent |
| Motion density exceeds density ceiling without narrative reason | Reject excess |

---

## Handoff contract

```yaml
status: approved | conditional | rejected
inputs_used: []
decisions:
  - motion principles summary
  - group purposes and choreography intent
  - reduced-motion strategy
constraints:
  - no_gratuitous_motion: true
  - density_ceiling:
  - forbidden_patterns: []   # e.g. random bounce on all elements
open_risks:
  - scroll complexity on mobile
  - 3D/motion synchronization
  - accessibility gaps
evidence:
  - planning_only
  - purpose_tests_documented: true
deliverables:
  - motion-intent-schema artifact
next_owner:
  primary: external gsap-* skills   # execution after intent approved
  secondary:
    - acos-responsive-art-direction  # viewport motion adaptation
    - acos-cinematic-3d-director   # if 3D scene-state sync needed
    - acos-webgl-performance         # if motion affects render load
rejection_route:
  - acos-art-director
  - acos-experience-architect
  - acos-anti-generic-design
  - acos-creative-director
```

---

## QA / evaluation contract

Before handoff, verify:

1. Every motion group has a **one-sentence purpose** and non-decorative role (or justified exception).
2. **No library mandates**—GSAP mentioned only as example executor in neighbor notes, not in deliverable requirements.
3. **Restraint documented**—explicit "do not animate" list exists.
4. **Reduced-motion** strategy is complete and testable.
5. **Scroll choreography** describes meaning, not plugin configuration.
6. **Swap test** — principles break if project name changes.
7. Artifact is **domain-neutral**.

`acos-visual-critic` evaluates motion **in rendered browser evidence** against this artifact later.

---

## Evidence requirements

| Claim | Evidence |
|---|---|
| Motion serves narrative/interaction | Documented purpose per group |
| Motion aligns with art/experience direction | Cited upstream artifacts |
| Motion feels correct in product | Screen recordings, prototype captures (downstream) |
| Performance-safe motion | Planning flags only; measured evidence via `acos-webgl-performance` / `gsap-performance` |

Distinguish planning evidence (this skill) from runtime/visual evidence (critics, QA).

---

## Memory interaction

### May read

- `memory/projects/` — prior motion decisions for active project
- `memory/knowledge/` — validated choreography patterns (scoped, not house style)
- `memory/failures/` — over-animation, accessibility motion failures

### May propose (via `acos-failure-learning`)

```yaml
memory_candidate:
  type: project-rule | candidate-global
  scope: required
  content: motion restraint lesson or reduced-motion pattern
  evidence: required
```

### Must not write

- Global "ACOS always staggers hero" preferences
- Library-specific canonical snippets as ACOS law
- Fake motion QA records

---

## Relationship to neighboring ACOS skills

| Neighbor | Relationship |
|---|---|
| `acos-creative-director` | Upstream thesis informs motion principles |
| `acos-art-director` | Upstream visual rhythm and hierarchy constraints |
| `acos-experience-architect` | Upstream section/state map drives transition logic |
| `acos-cinematic-3d-director` | Bidirectional — 3D scene transitions inform motion; motion syncs 3D state changes |
| `acos-responsive-art-direction` | Downstream — adapts choreography per viewport |
| `acos-anti-generic-design` | Challenges gratuitous motion tropes |
| `acos-reference-analysis` | Supplies motion language principles, not clones |
| `acos-webgl-performance` | Receives flags when motion affects render cost |
| External GSAP skills | Downstream executors — **how**, not **why** |
| `acos-visual-critic` | Evaluates rendered motion against this intent |
| `acos-quality-gate` | Confirms motion justification at gate |

**Overlap prevention:** Creative motion intent lives here. Implementation syntax, performance profiling, and 3D camera rigging live elsewhere.

---

## Non-goals

- GSAP tutorial, API reference, or plugin configuration
- Mandating GSAP or any specific animation library
- Random movement, ornamental bounce/spin defaults
- Replacing frontend or GSAP performance skills
- Owning 3D camera or lighting direction
- Defining responsive layout (only motion adaptation intent; layout is `acos-responsive-art-direction`)
- Creating permanent ACOS motion house style
- Self-approving final motion quality in browser
