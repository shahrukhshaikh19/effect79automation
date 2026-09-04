---
name: acos-creative-director
description: Activate when a project needs a central creative thesis, conceptual tension, experience-level creative principles, and project-specific direction synthesized from brief and optional reference intelligence. Do not activate for final visual systems, IA, implementation, or when the task is purely technical execution with creative direction already locked.
---

# acos-creative-director (ACOS-01)

## Purpose

Establish the **central creative thesis** and **project-specific creative direction** that downstream ACOS skills can execute without ambiguity.

This skill decides what the experience means at a conceptual level: the big idea, creative tension, experience-level principles, constraints, and which concept earns priority—aligned to brief, context, and reference intelligence when available.

Authority: `core/WORKFLOW.md` (Creative Direction stage), `core/QUALITY_GATES.md` (distinctiveness), locked boundary in `phase-C.md` §ACOS-01.

## Activation / trigger conditions

Activate when **any** of the following are true:

1. A new project or major redesign requires a creative thesis before art direction or experience architecture.
2. Brief normalization is complete and creative direction is explicitly in scope.
3. Reference intelligence exists or brief stands alone, and a decisive creative direction is needed.
4. Anti-generic review or quality gate routed a defect upstream requiring concept rework.
5. Stakeholder requests concept territories, creative principles, or a prioritized big idea.

## Do-not-activate conditions

Do **not** activate when:

- Creative direction is already locked and documented; only execution or visual specification remains.
- The task is final typography, palette, composition rules, or layout grids (Art Director).
- The task is site structure, IA, or journey sequencing (Experience Architect).
- The task is implementation, library selection, animation code, or 3D production.
- The task is only reference extraction with no direction decision requested.
- The task is quality gate approval or independent criticism.
- No brief or task context exists to anchor project specificity.

If only reference analysis is needed and no references exist, defer to brief clarification—not creative direction invention without context.

## Responsibility boundary

### Owns

- Central creative thesis and conceptual tension / big idea.
- Project-specific creative direction (not interchangeable across projects).
- Experience-level creative principles (why the experience feels the way it should).
- Creative constraints derived from brief, context, and reference intelligence.
- Prioritization of the strongest viable idea among explored territories.
- Alignment between brief, reference intelligence, brand/context, and concept.
- Rejection of generic concepts that could fit unrelated projects by renaming alone.

### Does NOT own

- Final typography, material, or color system (Art Director).
- Information architecture, section order, or interaction hierarchy (Experience Architect).
- Implementation technology, frameworks, or libraries.
- Detailed animation code or Three.js/Blender production.
- Motion choreography specifics (Motion Director).
- 3D scene creative direction when 3D is in scope (Cinematic 3D Director—may receive thesis inputs).
- Final QA approval (critics and quality gate).
- Anti-generic stress testing as primary procedure (Anti-Generic Design runs as challenger; Creative Director responds to failures).

## Required inputs

Minimum:

| Input | Required | Notes |
|-------|----------|-------|
| Normalized brief or task statement | Yes | Goals, audience, constraints, success criteria |
| Project context | Yes | Domain constraints without embedding ACOS defaults |
| Stakeholder priorities | Preferred | Must-have vs. negotiable |

Conditional:

| Input | When |
|-------|------|
| Reference intelligence artifact | When references were analyzed |
| Prior creative direction | When iterating, not greenfield |
| Anti-generic rejection report | When routed from ACOS-03 |
| Business requirements | When explicit; must not be overridden |

## Exact procedure / workflow

1. **Confirm activation.** Verify creative direction is in scope and not already locked. If locked, emit no-activation handoff.

2. **Ingest inputs.** Parse brief, context, constraints, and reference intelligence (if present). List explicit gaps.

3. **Extract creative problem.** State the core problem the experience must solve for its audience—not a feature list, but the communicative/job-to-be-done tension.

4. **Define evaluation criteria.** Before generating ideas, lock how concepts will be judged: project specificity, brief alignment, feasibility signal, distinctiveness, constraint compliance.

5. **Explore concept territories (controlled).** Generate 2–4 distinct territories. Each territory must differ in **mechanism**, not just adjectives. Record why each could work and primary risk.

6. **Apply project-specificity test to each territory.** For each, ask: "If the client name and domain changed but the structure stayed, would this still work?" If yes, territory is too generic—revise or discard.

7. **Select prioritized thesis.** Choose one primary direction with explicit rationale. Document rejected territories and why.

8. **Articulate central creative thesis.** One clear statement of the big idea plus conceptual tension (what forces are in play—e.g., clarity vs. density, trust vs. surprise—stated abstractly).

9. **Define experience-level creative principles.** 3–7 principles that guide downstream decisions without prescribing visual execution details.

10. **Set creative constraints.** Hard boundaries (must/not) and soft preferences (should/prefer) derived from brief and reference intelligence non-copy rules.

11. **Flag specialized direction needs.** Note whether 3D, motion, or immersive treatment may be relevant—without deciding implementation. Defer to conditional skills.

12. **Produce Creative Direction Artifact** per `references/output-schema.yaml`.

13. **Emit handoff** to `acos-anti-generic-design` for challenge pass before art and experience skills consume as authoritative.

## Required outputs / deliverables

Primary: **Creative Direction Artifact** conforming to `references/output-schema.yaml`.

Must include:

- Central creative thesis (single prioritized statement).
- Conceptual tension articulation.
- Experience-level creative principles.
- Creative constraints (hard/soft).
- Territory exploration summary with rejection rationale.
- Project-specificity justification.
- Specialized direction flags (3D/motion/immersive: yes/no/conditional with reason).
- Structured handoff.

## Rejection / failure conditions

Fail and do not hand off to downstream execution when:

- Thesis is interchangeable across unrelated projects (name-swap test fails).
- Thesis contradicts stated business requirements without documented stakeholder acceptance.
- Direction depends on copying reference identity (violates reference non-copy boundaries).
- Principles are vague aesthetic labels without decision power ("bold", "clean", "innovative" alone).
- No prioritized choice among territories when multiple were explored.
- 3D or motion is mandated without communicative justification in the thesis layer.
- Output prescribes final visual system details (palette, typefaces, grid)—scope leak to Art Director.

Route defects to: self-revision; if inputs insufficient, brief owner.

## Handoff contract

```yaml
status: complete | partial | rejected | no_activation
inputs_used:
  - type: brief | reference_intelligence | prior_direction | rejection_report
    ref: "<identifier or path>"
decisions:
  - id: thesis-primary
    statement: "<central creative thesis>"
  - id: principle-<n>
    statement: "<experience-level principle>"
constraints:
  hard: ["<must/not boundary>"]
  soft: ["<should/prefer guidance>"]
open_risks:
  - "<feasibility, stakeholder, or specificity risk>"
evidence:
  - type: brief_alignment | reference_derivation | specificity_test
    note: "<supporting rationale>"
deliverables:
  - artifact: "<path to Creative Direction Artifact>"
next_owner: acos-anti-generic-design
rejection_route: brief_owner | self | acos-reference-analysis
```

After anti-generic pass: downstream primary consumers are `acos-art-director` and `acos-experience-architect` (parallel consumption of approved thesis).

## QA / evaluation contract

Pre-handoff self-check:

| Check | Pass criterion |
|-------|----------------|
| Specificity | Name-swap test passed with documented reasoning |
| Prioritization | Exactly one primary thesis selected |
| Principle actionability | Each principle informs a downstream decision class |
| Boundary respect | No final visual/IA/implementation prescriptions |
| Reference alignment | Non-copy boundaries honored when reference intel present |
| Constraint clarity | Hard vs. soft constraints separated |

Aligns with `core/QUALITY_GATES.md` dimensions: creative originality, brand/project distinctiveness, concept strength.

Internal threshold: any critical check fails → revise. Partial artifacts allowed only with explicit `partial` status and listed blockers.

Independent validation: `acos-anti-generic-design` (challenge), later `acos-creative-critic` and Design Gate.

## Evidence requirements

| Type | Requirement |
|------|-------------|
| Planning evidence | Brief citations, reference principle IDs used, specificity test results |
| Visual evidence | Not required at this stage |
| Runtime evidence | Not required |

Claims about audience or market must trace to brief inputs, not model assumptions.

## Memory interaction

Per `core/MEMORY_POLICY.md`:

**May read:** project brief/decisions in `memory/projects/`; validated process knowledge in `memory/knowledge/`.

**May propose for project memory:** approved thesis, principles, constraints with project scope.

**Must NOT write to taste/global memory:** project aesthetic as reusable style; successful thesis as mandatory ACOS pattern.

Do not populate memory during Phase C foundation.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|-------|--------------|
| `acos-reference-analysis` | Upstream supplier of principles; Creative Director does not re-analyze references |
| `acos-anti-generic-design` | Mandatory challenger before downstream trust; Creative Director revises on fail |
| `acos-art-director` | Downstream; translates thesis into visual language—not co-owner of thesis |
| `acos-experience-architect` | Downstream; structures journey aligned to thesis—not co-owner of thesis |
| `acos-cinematic-3d-director` | Conditional; receives thesis + justification flag for 3D relevance |
| `acos-motion-director` | Conditional; receives thesis + motion relevance flag |
| `acos-creative-critic` | Independent evaluator later; not involved in thesis creation |

**Overlap prevention:** Creative Director owns **why** and **what idea**; Art Director owns **how it looks**; Experience Architect owns **how it is structured and sequenced**. If IA or layout structure appears in creative output, remove and hand off.

## Non-goals

- Defining typography, color, composition grids, or material specs.
- Choosing GSAP, Three.js, Blender, or any implementation stack.
- Writing motion or 3D scene direction beyond relevance flags.
- Approving quality or passing anti-generic review on own output without ACOS-03.
- Creating ACOS house style or domain-default aesthetics.
- Activating on every project regardless of need.
