---
name: acos-experience-architect
description: Activate when user journey, information architecture, content progression, interaction hierarchy, and experience-level pacing must be defined for standard or immersive interfaces. Do not activate for final visual styling, implementation stack choice, or 3D-by-default experiences.
---

# acos-experience-architect (ACOS-05)

## Purpose

Define **how the experience is structured and sequenced** at the journey level: information architecture, content/section progression, interaction hierarchy, narrative pacing, state/flow relationships, and content priority.

This skill ensures the user path is intentional—for standard applications and immersive experiences alike—with **no 3D-first or cinematic-first assumption**.

Authority: `core/WORKFLOW.md` (Experience Architecture stage), `core/ROUTING.md`, locked boundary in `phase-C.md` §ACOS-05.

## Activation / trigger conditions

Activate when **any** of the following are true:

1. Approved creative direction exists (anti-generic PASS) and experience structure is required before implementation planning.
2. Task requires IA, user journey, section sequencing, or interaction hierarchy definition.
3. New product surface, multi-step flow, or narrative experience needs architectural specification.
4. Defect routed for broken journey, unclear flow, or wrong content priority.
5. Design Gate readiness requires explicit experience architecture evidence.

Works for: dashboards, forms, marketing sites, apps, immersive scroll experiences, configurators—medium-agnostic.

## Do-not-activate conditions

Do **not** activate when:

- Creative direction unset or failed anti-generic without override.
- Task is final visual styling, typography, or palette (Art Director).
- Task is implementation, API design, or library selection.
- Task is 3D scene direction because tools exist (must be justified at experience level first).
- Task overrides explicit business requirements without documented escalation.
- Task is only visual composition without structural change.
- Task is quality gate or criticism only.

## Responsibility boundary

### Owns

- User journey mapping (entry → progression → outcomes).
- Information architecture (sections, entities, navigation model).
- Content and section progression order with rationale.
- Interaction hierarchy (primary/secondary/tertiary actions).
- Narrative pacing at experience level (not motion timing detail).
- State and flow relationships (views, modes, transitions between states).
- Sequencing logic and content priority rules.
- DOM vs. WebGL/content responsibility split at experience level (who owns what user-facing job—not implementation).

### Does NOT own

- Final visual styling, typography, color, or composition grids (Art Director).
- GSAP, Three.js, Blender, or any implementation technology.
- Creating 3D because tools exist; 3D must earn a role in journey narrative.
- Overriding business requirements or compliance mandates.
- Motion choreography timing (Motion Director).
- 3D camera/scene creative direction (Cinematic 3D Director).
- Final quality approval.

Must work for **standard interfaces** as well as immersive experiences.

## Required inputs

Minimum:

| Input | Required | Notes |
|-------|----------|-------|
| Approved Creative Direction Artifact | Yes | Thesis guides journey |
| Anti-generic PASS | Yes | Or documented override |
| Brief: goals, audience, required flows | Yes | Business requirements sacred |

Conditional:

| Input | When |
|-------|------|
| Art Direction Specification | When exists; align interaction hierarchy with visual signals |
| Reference intelligence | Interaction/narrative principles only |
| Existing product constraints | Legacy IA, URL structure, CMS limits |
| Accessibility requirements | Flow must accommodate keyboard, screen reader, reduced motion intent |

## Exact procedure / workflow

1. **Confirm activation.** Verify creative direction approved and structural design in scope.

2. **State experience intent from thesis.** One paragraph: what journey should accomplish emotionally and functionally (derived from creative direction, not new thesis).

3. **Inventory user types and entry points.** Primary/secondary audiences; how they arrive; what they need first.

4. **Define success outcomes.** Per audience, what "done" looks like (conversion, comprehension, completion, exploration).

5. **Map core user journey.** Stages: discover → orient → evaluate → act → confirm/retain (adapt labels to project). For each stage: user goal, system response, content need.

6. **Define information architecture.**

   - Top-level sections/modules and their purpose.
   - Navigation model (global, local, contextual, none for linear narrative).
   - Content entities and relationships.
   - Rules for what is always visible vs. progressive disclosure.

7. **Define content/section progression.** Order sections/states with rationale tied to thesis. Document alternative paths (returning users, skip paths, error recovery).

8. **Define interaction hierarchy.** Primary actions per stage; secondary/support; destructive actions; constraints on competing CTAs.

9. **Define narrative pacing (experience level).** Where tension builds, releases, or pauses—without motion timing specs. Mark optional immersive beats vs. essential functional beats.

10. **Define state/flow relationships.** State diagram or equivalent: modes, transitions, guards (what must happen before advance), back-navigation rules.

11. **Define content priority rules.** When space or attention is limited (mobile, overlay, loading), what survives—feeds responsive art direction later.

12. **Define DOM/WebGL responsibility split (if applicable).** Which user jobs each layer owns (e.g., forms in DOM, spatial metaphor in WebGL)—experience-level only, no engine choice.

13. **3D/motion necessity check.** For any proposed 3D or motion-heavy beat: document communicative role. If removing it does not damage journey intent, mark optional or remove. Flag `acos-cinematic-3d-director` / `acos-motion-director` only when justified.

14. **Cross-check business requirements.** Every mandatory flow present; conflicts escalated, not silently dropped.

15. **Cross-check with art direction (if available).** Visual hierarchy supports content priority; resolve conflicts via documented tradeoff.

16. **Produce Experience Architecture Artifact.**

17. **Emit handoff** toward Design Gate readiness, responsive art direction, specialized directors, and technical planning.

## Required outputs / deliverables

Primary: **Experience Architecture Artifact** containing:

- Experience intent summary (from thesis).
- User types and entry points.
- Journey map with stages and outcomes.
- IA structure and navigation model.
- Section/state progression with rationale.
- Interaction hierarchy per major stage.
- Narrative pacing notes (experience level).
- State/flow relationships (diagram or structured equivalent).
- Content priority rules.
- DOM/WebGL responsibility split (if applicable).
- 3D/motion necessity flags with justification.
- Business requirement traceability matrix.
- Structured handoff.

## Rejection / failure conditions

Fail when:

- Journey contradicts mandatory business flows without escalation.
- IA is generic template (feature trio, default footer sitemap) without brief/thesis link.
- 3D or immersive layers assigned without journey role (tool-driven architecture).
- Creative thesis replaced or rewritten (scope leak to Creative Director).
- Visual styling prescribed (scope leak to Art Director).
- Single viewport or desktop-only assumptions without priority rules for adaptation.
- No primary user outcome defined.
- Interaction hierarchy leaves competing primary actions unresolved.

Route to: self-revision; `acos-creative-director` if thesis insufficient; stakeholder for business conflict.

## Handoff contract

```yaml
status: complete | partial | rejected | no_activation
inputs_used:
  - type: creative_direction | art_direction | reference_intelligence | brief
    ref: "<path or id>"
decisions:
  - domain: journey | ia | progression | interaction | pacing | state | priority | layer_split
    decision: "<architectural decision>"
    thesis_link: "<principle or requirement id>"
constraints:
  - "<flow or business constraint downstream must preserve>"
open_risks:
  - "<complexity, compliance, technical feasibility unknown>"
evidence:
  - type: requirement_trace | thesis_derivation | necessity_check
    note: "<support>"
deliverables:
  - artifact: "<path to Experience Architecture Artifact>"
next_owner: design_gate_readiness | acos-responsive-art-direction | acos-cinematic-3d-director | acos-motion-director | technical_planning
rejection_route: acos-creative-director | stakeholder | self
```

## QA / evaluation contract

Self-check:

| Check | Pass criterion |
|-------|----------------|
| Business traceability | Every mandatory brief flow mapped |
| Thesis alignment | Journey expresses creative thesis, not parallel concept |
| Hierarchy clarity | One primary action per stage/context defined |
| Medium neutrality | Valid for standard UI; 3D not assumed |
| Necessity | 3D/motion beats have documented communicative role |
| Boundary | No visual styling or implementation mandates |
| Adaptation | Content priority rules exist for constrained viewports |

Maps to `core/QUALITY_GATES.md`: storytelling/experience flow; hard reject: broken primary flow.

Design Gate reads this artifact for hierarchy and experience thesis evidence per `core/WORKFLOW.md`.

## Evidence requirements

| Type | When |
|------|------|
| Planning evidence | Journey map, IA, state model, requirement matrix |
| Visual evidence | Not required at architecture stage |
| Runtime evidence | Not at this stage; required later for flow QA |

## Memory interaction

Per `core/MEMORY_POLICY.md`:

**May read:** project brief/decisions; failures tagged journey/IA for similar product types.

**May propose for project memory:** approved IA and flow decisions with project scope.

**Must NOT promote globally:** one project's journey pattern as ACOS default for all interfaces.

Do not populate memory during Phase C foundation.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|-------|--------------|
| `acos-creative-director` | Upstream thesis; Architect structures, does not re-author thesis |
| `acos-anti-generic-design` | Must PASS before authoritative use |
| `acos-art-director` | Parallel/sequential; visual hierarchy aligns with content priority |
| `acos-responsive-art-direction` | Downstream; uses content priority rules |
| `acos-cinematic-3d-director` | Activated only when 3D necessity flag justified |
| `acos-motion-director` | Activated only when motion necessity flag justified |
| `acos-visual-critic` | Does not evaluate IA; flow QA is functional/creative gate domain |
| External frontend skills | Implement flows within this architecture |

**Overlap prevention:** Experience Architect owns **order, flow, and priority**; Art Director owns **visual signaling**; Creative Director owns **why**. If Art Direction prescribes section order, reject as IA leak.

## Non-goals

- Final visual styling or design system specification.
- Choosing implementation libraries or 3D engines.
- Adding 3D/motion by default.
- Overriding business or compliance requirements.
- Motion timing or 3D staging detail.
- Quality gate approval.
- Standard template IA without project rationale.
- Populating memory during foundation phase.
