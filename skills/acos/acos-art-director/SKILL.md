---
name: acos-art-director
description: Activate when approved creative direction must become executable visual language—composition, typography direction, hierarchy, palette logic, surfaces, and DOM/WebGL visual cohesion. Do not activate for creative thesis, IA, implementation library choice, or final quality approval.
---

# acos-art-director (ACOS-04)

## Purpose

Translate approved creative direction into **executable visual rules** that production skills and implementers can apply consistently—without establishing a permanent ACOS aesthetic.

This skill owns the **visual language system** for the project: how composition, type, color, surfaces, imagery, lighting (where applicable), and rhythm cohere—including DOM/WebGL visual unity when both exist.

Authority: `core/WORKFLOW.md` (Art Direction stage), `core/QUALITY_GATES.md` (composition, typography, hierarchy), locked boundary in `phase-C.md` §ACOS-04.

## Activation / trigger conditions

Activate when **all** of the following are true:

1. Creative direction exists and has passed anti-generic review (PASS), or equivalent human-approved lock documented.
2. Visual language specification is required before design implementation, responsive direction, or visual production.
3. Task scope includes composition, typography, hierarchy, palette, surfaces, or visual cohesion—not merely conceptual thesis.

Also activate when:

- Experience architecture needs visual hierarchy rules to sequence content (collaborative input, Art Director owns visual rules).
- Defect routed from visual critic or quality gate for hierarchy/composition/typography failure.
- Responsive art direction needs upstream visual system (feeds ACOS-08 later).

## Do-not-activate conditions

Do **not** activate when:

- Creative thesis is unset or failed anti-generic review without override.
- Task is information architecture, journey, or section sequencing only (Experience Architect).
- Task is implementation, framework selection, or animation code.
- Task is 3D scene creative direction when 3D is primary medium (Cinematic 3D Director owns 3D-specific staging; Art Director may coordinate visual cohesion).
- Task is motion choreography (Motion Director).
- Task is final QA approval.
- Task is reference extraction only.

## Responsibility boundary

### Owns

- Visual language definition for the project.
- Composition system and layout logic (visual, not IA).
- Typography direction (roles, scale relationships, pairing logic—not necessarily final font files).
- Visual hierarchy rules across states and sections.
- Palette logic (semantic roles, contrast intent—not arbitrary decoration).
- Surface and material language (2D and applicable 3D surface intent).
- Image treatment direction where applicable.
- Lighting language where applicable to the medium.
- Visual rhythm and density rules.
- DOM/WebGL visual cohesion rules where both render layers exist.

### Does NOT own

- Site/application information architecture or content sequencing (Experience Architect).
- Implementation library or renderer selection.
- Motion for decoration without communicative purpose (Motion Director).
- Detailed 3D camera/scene staging when 3D-led (Cinematic 3D Director).
- Responsive breakpoint strategy detail (Responsive Art Director—consumes this system's rules).
- Final quality approval (critics and gate).
- Central creative thesis (Creative Director).

Output must be **project-specific visual rules**, not "the ACOS look."

## Required inputs

Minimum:

| Input | Required | Notes |
|-------|----------|-------|
| Approved Creative Direction Artifact | Yes | Thesis + principles + constraints |
| Anti-generic PASS | Yes | Or documented override |
| Brief constraints | Yes | Accessibility, brand legal, platform |

Conditional:

| Input | When |
|-------|------|
| Reference intelligence | Typography/composition/lighting principles |
| Experience Architecture draft | When IA exists; align hierarchy |
| Existing design system | When extending, not greenfield |
| Technical constraints | Performance, WebGL budget signals |

## Exact procedure / workflow

1. **Confirm activation.** Verify creative direction approved and visual specification in scope.

2. **Extract visual implications from thesis.** Map each experience principle to visual decision domains (hierarchy, tone, density, contrast, motion affordance hints only—not choreography).

3. **Define visual hierarchy model.** Primary/secondary/tertiary signals; how attention moves; what is never competing at same level.

4. **Define composition system.** Grid or anti-grid logic, alignment rules, whitespace philosophy, focal point rules, section transition visual grammar.

5. **Define typography direction.** Role map (display, heading, body, label, data); scale ratio logic; weight/contrast rules; readability constraints per `core/QUALITY_GATES.md` accessibility awareness.

6. **Define palette logic.** Semantic color roles (background, surface, text, accent, state, error); contrast intent; rules for accent restraint; dark/light strategy if relevant—without mandating global dark mode default.

7. **Define surface and material language.** Flat, textured, photographic, illustrative, 3D-surface intent; edge treatment; depth cues; consistency rules across DOM and WebGL if both present.

8. **Define imagery treatment.** Photography/illustration/abstract rules; cropping; overlay; consistency with hierarchy model.

9. **Define lighting language (if applicable).** For static, photographic, or 3D-coordinated work: key/fill/rim intent, contrast envelope—not engine settings.

10. **Define visual rhythm.** Spacing scale, density modes, repetition/variation rules, accent frequency limits.

11. **Define DOM/WebGL cohesion rules (if applicable).** Typography/color/surface continuity; when 3D subserves UI vs. stands alone; z-index/layering philosophy without implementation code.

12. **Cross-check against creative constraints and anti-generic pass.** Ensure visual system serves thesis, not template defaults.

13. **Document explicit non-rules.** What this project intentionally avoids visually and why.

14. **Produce Art Direction Specification artifact.**

15. **Emit handoff** to `acos-responsive-art-direction` (when responsive in scope), `acos-experience-architect` (if parallel), production/external skills, and critic pipeline.

## Required outputs / deliverables

Primary: **Art Direction Specification** containing:

- Visual hierarchy model.
- Composition system rules.
- Typography direction (roles + scale logic).
- Palette logic (semantic roles).
- Surface/material language.
- Imagery and lighting direction (if applicable).
- Visual rhythm and spacing scale.
- DOM/WebGL cohesion rules (if applicable).
- Non-rules (intentional avoids).
- Structured handoff.

Format: structured YAML/Markdown sections; predictable headings for validator and downstream parsing.

## Rejection / failure conditions

Fail artifact when:

- Visual system could apply unchanged to unrelated projects (thesis disconnect).
- Palette/typography chosen as undifferentiated defaults without thesis link.
- Rules contradict approved creative constraints without escalation.
- IA or journey decisions embedded (scope leak).
- Implementation code or library mandates included.
- Decorative motion or 3D prescribed without Motion/3D director ownership.
- Permanent ACOS aesthetic implied ("always use X type style").
- Accessibility contrast or readability ignored where text UI exists.

Route to: self-revision; `acos-creative-director` if thesis inadequately supports visual direction; `acos-experience-architect` if hierarchy conflicts with journey.

## Handoff contract

```yaml
status: complete | partial | rejected | no_activation
inputs_used:
  - type: creative_direction | anti_generic_pass | reference_intelligence | experience_draft
    ref: "<path or id>"
decisions:
  - domain: hierarchy | composition | typography | palette | surface | imagery | lighting | rhythm | cohesion
    rule: "<executable visual rule>"
    thesis_link: "<principle id or rationale>"
constraints:
  - "<visual constraint production must obey>"
open_risks:
  - "<feasibility, contrast, WebGL cohesion, asset availability>"
evidence:
  - type: thesis_derivation | constraint_check
    note: "<traceability>"
deliverables:
  - artifact: "<path to Art Direction Specification>"
next_owner: acos-responsive-art-direction | acos-experience-architect | external_production
rejection_route: acos-creative-director | acos-experience-architect | self
```

## QA / evaluation contract

Self-check before handoff:

| Dimension | Pass criterion |
|-----------|----------------|
| Traceability | Major rules link to creative thesis/principles |
| Executability | Implementer can apply without guessing aesthetic adjectives |
| Specificity | Project non-rules present; not generic design-system clone |
| Boundary | No IA, motion choreography, or code |
| Cohesion | DOM/WebGL rules consistent if both apply |
| Accessibility awareness | Text contrast and scale logic acknowledged |

Maps to `core/QUALITY_GATES.md`: composition, typography, visual hierarchy.

Independent review: `acos-visual-critic` at implementation stage.

## Evidence requirements

| Type | When |
|------|------|
| Planning evidence | Art Direction Specification, thesis links |
| Visual evidence | Not required at spec stage; required at implementation review |
| Runtime evidence | Not at this stage |

## Memory interaction

Per `core/MEMORY_POLICY.md`:

**May read:** project decisions; knowledge memory for validated accessibility/contrast patterns (not taste).

**May propose for project memory:** approved visual rules with project scope tag.

**Must NOT promote to taste/global:** project's palette/typography as ACOS default aesthetic.

Do not populate memory during Phase C foundation.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|-------|--------------|
| `acos-creative-director` | Upstream thesis; Art Director does not change thesis |
| `acos-anti-generic-design` | Gate before activation |
| `acos-experience-architect` | Parallel/prior; IA informs hierarchy; Art Director does not own section order |
| `acos-responsive-art-direction` | Downstream; adapts this system per viewport |
| `acos-cinematic-3d-director` | 3D staging owner; Art Director sets cohesion rules only |
| `acos-motion-director` | Motion owner; Art Director may hint affordances not choreography |
| `acos-visual-critic` | Evaluates implementation against this spec |
| External design/frontend skills | Execute within these rules |

**Overlap prevention:** Art Director owns **visual language rules**; Experience Architect owns **structure and flow**; Creative Director owns **conceptual thesis**. Hierarchy appears in both—Experience Architect sets content priority order; Art Director sets how priority is signaled visually.

## Non-goals

- Information architecture or interaction flow design.
- GSAP/Three.js/Blender selection or code.
- Motion choreography or 3D scene blocking.
- Final quality gate or critic replacement.
- Creating permanent ACOS house style.
- Responsive breakpoint specifics (defer to Responsive Art Director).
- Reference cloning or new creative thesis authoring.
