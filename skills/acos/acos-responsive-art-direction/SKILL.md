---
name: acos-responsive-art-direction
description: Owns viewport-specific art direction—responsive composition strategy, hierarchy shifts, re-framing, content priority changes, interaction adaptation, typography scale relationships, and 3D/motion adaptation where relevant. Activate when multi-viewport experience design is required. Mobile is NOT desktop scaled down.
---

# ACOS Responsive Art Direction (ACOS-08)

## Purpose

Define **how the experience intentionally changes across viewport classes**—composition, hierarchy, camera/framing, motion, and interaction—not how CSS breakpoints are implemented.

This skill ensures mobile, tablet, and desktop receive **independent art-direction decisions** where the experience requires them, rather than uniform scaling of a desktop layout.

**Core mandate:** Mobile is not "desktop but smaller." Materially different compositions are explicitly allowed and often required.

---

## Activation / trigger conditions

Activate when **any** of the following apply:

1. The experience targets more than one viewport class (mobile, tablet, desktop, large desktop).
2. Upstream art direction or experience architecture exists and must be translated into viewport-specific rules.
3. 3D direction (`acos-cinematic-3d-director`) or motion direction (`acos-motion-director`) requires per-viewport adaptation.
4. Content priority, typography scale, or interaction patterns must change by device context.
5. Performance-aware visual simplification by viewport is needed (coordinate with `acos-webgl-performance`).

Activate for standard product UI and immersive experiences alike when responsive behavior is non-trivial.

---

## Do-not-activate conditions

Do **not** activate when:

- The deliverable is a fixed-size artifact (single viewport spec, print, kiosk with fixed resolution) and brief confirms no adaptation.
- The task is pure CSS/grid implementation without art-direction decisions.
- The ask is only "make it responsive" with no upstream direction to adapt.
- WebGL performance budgeting is the sole need (route to `acos-webgl-performance`).
- Visual critique of rendered responsive screenshots is needed (route to `acos-visual-critic`).

**Hard stop:** If the proposed strategy is uniform proportional scaling of desktop, reject and rewrite.

---

## Responsibility boundary

### Authorized decisions

| Domain | This skill decides |
|---|---|
| Responsive composition strategy | Independent layouts vs. shared structure per viewport class |
| Viewport-specific hierarchy | What leads visually on mobile vs. desktop |
| Re-framing | Crop, stack, reorder, hide, or promote content spatially |
| Content priority changes | Which messages/actions dominate per viewport |
| Interaction adaptation | Tap vs. hover, gesture affordances, sticky behavior intent |
| Typography scale relationships | Relative type roles across breakpoints (not px implementation) |
| 3D camera adaptation | Framing, FOV feel, object prominence per viewport when 3D exists |
| Motion adaptation | Reduced choreography density, alternate scroll behavior intent |
| Performance-aware simplification | Visual degradation tiers by viewport when necessary |

### Forbidden decisions

| Domain | Owner |
|---|---|
| Global creative thesis | `acos-creative-director` |
| Base visual language (palette, type family, core rhythm) | `acos-art-director` |
| IA and section sequencing | `acos-experience-architect` |
| 3D purpose and base camera motivation | `acos-cinematic-3d-director` |
| Motion purpose and core choreography | `acos-motion-director` |
| CSS/framework implementation, media query syntax | Frontend / external skills |
| Numeric WebGL budgets and FPS targets | `acos-webgl-performance` |
| Ship/no-ship | `acos-quality-gate` |

---

## Required inputs

```yaml
required_inputs:
  project_context:
    - brief_or_goal_summary
    - target_viewport_classes    # mobile, tablet, desktop, etc.
    - primary_device_priority    # mobile-first | desktop-first | balanced
  upstream_direction:
    - art_direction_summary
    - experience_architecture_map
  optional:
    - cinematic_3d_direction
    - motion_direction
    - reference_responsive_principles
    - accessibility_requirements
    - performance_constraints_from_webgl
  evidence_if_reviewing_existing:
    - multi-viewport screenshots or captures
    - device lab notes
```

---

## Exact procedure / workflow

### Step 1 — Define viewport classes and priorities

1. List supported viewport classes for this project.
2. Declare `primary_device_priority` and rationale tied to audience/task—not habit.
3. Identify non-negotiable content/actions per class.

### Step 2 — Reject "scale-down desktop" default

1. Document why proportional shrink is insufficient for this project.
2. List at least one **material composition difference** per major section (stack vs. side-by-side, hero crop, navigation model change, etc.).
3. If no material differences exist, justify why single-composition strategy is valid (rare).

### Step 3 — Per-section responsive strategy

For each major section/state:

1. Define desktop composition intent (reference from art direction).
2. Define mobile/tablet composition ** independently **—not as a percentage scale.
3. Document hierarchy shifts: primary → secondary element changes.
4. Mark `content_priority_changes` explicitly.

### Step 4 — Typography and spacing relationships

1. Define type role relationships per viewport (display vs. body dominance).
2. Specify readability constraints (line length intent, minimum tap targets at intent level).
3. Do not output CSS values unless project tooling requires; prefer relational rules.

### Step 5 — Interaction adaptation

1. Map hover-dependent patterns to touch equivalents.
2. Define navigation pattern changes (drawer, bottom bar, persistent nav) at intent level.
3. Specify sticky/fixed behavior differences if any.

### Step 6 — 3D and motion adaptation (conditional)

**Only when 3D or motion direction exists:**

1. Define camera/framing adjustments per viewport for 3D beats.
2. Define motion density changes (what simplifies on small screens).
3. Coordinate reduced-motion with `acos-motion-director` output—do not contradict.

### Step 7 — Performance-aware simplification (conditional)

**When WebGL/3D or heavy media exists:**

1. Define visual simplification tiers by viewport (fewer effects, static hero, simplified environment).
2. Flag decisions requiring `acos-webgl-performance` confirmation—do not invent FPS claims.

### Step 8 — Produce deliverable and handoff

1. Complete `references/viewport-strategy-schema.yaml`.
2. Run self-QA including anti-scale-down check.
3. Emit structured handoff.

---

## Required outputs / deliverables

Primary artifact: **Responsive Art Direction Document** per `references/viewport-strategy-schema.yaml`.

```yaml
deliverable:
  skill: acos-responsive-art-direction
  version: 1
  status: approved | conditional | rejected
  viewport_classes: []
  primary_device_priority:
  anti_scale_down_rationale:
  sections:
    - id:
      desktop:
        composition:
        hierarchy:
      mobile:
        composition:          # must differ materially where required
        hierarchy:
        content_priority_changes: []
      tablet:                 # omit or inherit with explicit deltas
  typography_relationships: []
  interaction_adaptation: []
  three_d_adaptation: []      # conditional
  motion_adaptation: []       # conditional
  simplification_tiers: []    # conditional
  open_questions: []
```

---

## Rejection / failure conditions

| Condition | Action |
|---|---|
| Strategy is desktop scaled down only | Reject; rewrite with independent mobile composition |
| Mobile hierarchy identical to desktop with no justification | Reject section or artifact |
| Hidden critical content on mobile without alternative access | Reject; route `acos-experience-architect` |
| 3D camera unchanged on mobile despite unreadable framing | Hold; revise 3D adaptation |
| Motion density unchanged on low-power viewport without rationale | Hold; coordinate motion/performance |
| Typography relationships break art direction | Reject; route `acos-art-director` |
| Implementation CSS passed off as art direction | Invalid artifact |

**Canonical test:**

> Would a user on mobile receive the same **priority of information and action** as desktop, through an composition designed for their context—not a shrunken desktop?

If no, artifact fails.

---

## Handoff contract

```yaml
status: approved | conditional | rejected
inputs_used: []
decisions:
  - viewport class list and priority
  - per-section composition deltas
  - interaction adaptation summary
constraints:
  - mobile_not_desktop_scaled_down: true
  - material_composition_differences_required: true
open_risks:
  - 3D readability on small viewports
  - motion/scroll complexity on mobile
  - content truncation risks
evidence:
  - planning_only
  - anti_scale_down_documented: true
deliverables:
  - viewport-strategy-schema artifact
next_owner:
  primary: frontend implementation / design system execution
  secondary:
    - acos-webgl-performance      # simplification tiers need budget confirmation
    - acos-motion-director        # if motion deltas need refinement
    - acos-cinematic-3d-director  # if camera adaptation affects 3D intent
rejection_route:
  - acos-art-director
  - acos-experience-architect
  - acos-visual-critic            # when rendered multi-viewport evidence fails
```

---

## QA / evaluation contract

Verify before handoff:

1. **Anti-scale-down rationale** present and credible.
2. Each major section has **explicit mobile composition**, not only width percentages.
3. **Content priority changes** documented where hierarchy shifts.
4. **Interaction adaptation** covers hover→touch and navigation model changes.
5. 3D/motion sections present **only when upstream artifacts exist**.
6. **No CSS tutorial** masquerading as art direction.
7. **Domain-neutral** — no default industry layout templates.

`acos-visual-critic` validates **rendered multi-viewport evidence** against this artifact.

---

## Evidence requirements

| Claim | Evidence |
|---|---|
| Mobile composition is independent | Side-by-side intent descriptions or wireframe-level captures |
| Hierarchy appropriate per device | Planning artifact + later screenshot proof |
| 3D readable on mobile | Renders per viewport (downstream, `acos-3d-critic`) |
| Performance simplification sufficient | Planned tier + measured runtime (`acos-webgl-performance`) |

Planning evidence from this skill; visual/runtime evidence from downstream QA.

---

## Memory interaction

### May read

- `memory/projects/` — prior responsive decisions
- `memory/knowledge/` — validated responsive patterns (scoped)
- `memory/failures/` — mobile truncation, unreadable 3D framing failures

### May propose (via `acos-failure-learning`)

```yaml
memory_candidate:
  type: project-rule | candidate-global
  scope: required
  content: responsive pattern or failure lesson
  evidence: required
```

### Must not write

- Universal "ACOS mobile nav is always X" rules
- Fake multi-device QA results

---

## Relationship to neighboring ACOS skills

| Neighbor | Relationship |
|---|---|
| `acos-art-director` | Upstream base visual language; this skill adapts per viewport |
| `acos-experience-architect` | Upstream IA; receives rejection if mobile loses critical journey steps |
| `acos-cinematic-3d-director` | Upstream 3D intent; this skill adapts camera/framing |
| `acos-motion-director` | Upstream motion intent; this skill adapts density/choreography |
| `acos-webgl-performance` | Bidirectional — simplification tiers vs. measured budgets |
| `acos-visual-critic` | Evaluates viewport-specific rendered defects |
| `acos-quality-gate` | Confirms responsive consideration at gate |

**Overlap prevention:** Base art direction is not duplicated here—only **delta strategy per viewport**. Implementation code lives in frontend/external skills.

---

## Non-goals

- Treating mobile as desktop scaled down
- Writing CSS/media-query tutorials
- Owning global palette/typography system creation
- Replacing WebGL performance engineering
- Owning motion purpose (only adaptation)
- Creating a single ACOS responsive template for all projects
- Approving final responsive QA without rendered evidence
