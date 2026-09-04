---
name: acos-anti-generic-design
description: Activate to stress-test creative direction or design proposals for generic AI tropes, sameness, and unjustified default patterns before art or experience execution. Do not activate to invent house style, ban techniques universally, or replace Creative Director or Art Director ownership.
---

# acos-anti-generic-design (ACOS-03)

## Purpose

Detect and reject **interchangeable, template-like, or unjustified default design patterns** before they propagate into art direction, experience architecture, and implementation.

This skill is the **concept specificity challenger**: it proves whether a direction is truly project-specific or could belong to any client after superficial renaming.

Authority: `core/WORKFLOW.md` (Anti-Generic Review stage), `core/QUALITY_GATES.md` (hard reject: materially generic result), locked boundary in `phase-C.md` §ACOS-03.

## Activation / trigger conditions

Activate when **any** of the following are true:

1. `acos-creative-director` has produced a Creative Direction Artifact awaiting challenge.
2. A design proposal (concept, layout approach, motion/3D intent summary) is about to proceed to art or experience skills without prior genericness review.
3. Quality gate or critic routed a genericness defect upstream.
4. Stakeholder or agent explicitly requests differentiation / anti-template review.
5. A direction relies heavily on common AI-generated UI patterns (cards, centered heroes, glass effects, decorative 3D, random motion, gradient defaults) and justification is unclear.

## Do-not-activate conditions

Do **not** activate when:

- No creative direction or design proposal exists to evaluate.
- The task is to create the initial creative thesis (Creative Director).
- The task is final visual system specification (Art Director).
- The task is IA or journey design (Experience Architect).
- The request is to define permanent ACOS aesthetic rules or ban techniques globally.
- A technique is common but **explicitly justified** by brief and thesis—evaluate justification, do not auto-reject on technique name alone.
- Implementation debugging or technical QA is the primary need.

## Responsibility boundary

### Owns

- Detecting generic AI/design tropes and sameness.
- Concept specificity stress tests and differentiation tests.
- Challenging unjustified use of:
  - card-grid defaults, centered hero templates, glassmorphism without purpose
  - decorative gradients, stock visual language, random motion
  - decorative 3D, template-like section structure, interchangeable layouts
  - vague premium/minimal/modern labeling without mechanism
- Proving whether the concept is project-specific with documented test results.
- Pass/fail/challenge verdict with required corrections routed to responsible owner.

### Does NOT own

- Inventing a permanent ACOS house style.
- Banning a technique universally across all projects.
- Rejecting a technique solely because it is popular.
- Replacing Creative Director (does not write the thesis) or Art Director (does not write visual system).
- Final quality gate approval (routes to Creative Director or downstream skills; gate is ACOS-13).
- Choosing alternative creative territories (flags failures; Creative Director revises).

Common techniques are acceptable when justified by project context. This skill rejects **unjustified/default** use, not existence of the technique.

## Required inputs

Minimum:

| Input | Required | Notes |
|-------|----------|-------|
| Creative Direction Artifact or equivalent proposal | Yes | Must contain thesis and principles |
| Brief / project context | Yes | For specificity comparison |
| Prior anti-generic report | If re-test | After corrections |

Optional:

- Reference intelligence (to detect copy-vs-principle failures).
- Art direction draft (secondary review if leaked early).
- Competitor or category context from brief (not invented).

## Exact procedure / workflow

1. **Confirm activation.** Verify a evaluable direction or proposal exists. If not, emit `no_activation`.

2. **Ingest artifact.** Parse thesis, principles, constraints, territory rationale, and any visual/structure hints embedded in creative output.

3. **Run name-swap specificity test.** Replace project identity with a generic placeholder mentally. If thesis and principles still hold without modification, record **fail**.

4. **Run mechanism vs. adjective audit.** List descriptive adjectives in the artifact. For each, demand an underlying **mechanism** (what the experience *does* differently). Adjectives without mechanisms are flags.

5. **Run trope checklist scan.** Evaluate against common unjustified patterns (see trope categories below). For each hit: mark **justified** (traces to thesis/brief) or **unjustified** (default/template).

   Trope categories (non-exhaustive):
   - Layout: card grids as default structure, centered hero with single CTA only, symmetric template sections
   - Surface: glass blur, gradient meshes, neon accents without semantic role
   - Motion: scroll parallax, floating elements, entrance animations without hierarchy purpose
   - 3D: hero object with no narrative role, WebGL for novelty
   - Content structure: feature trio, testimonial carousel, pricing table defaults without brief mandate
   - Language: "premium", "modern", "clean", "innovative" as substitutes for decisions

6. **Run differentiation test.** Ask: "What would a competent generic AI output for this brief look like?" Document overlap. Require explicit differentiators from the proposal.

7. **Run constraint justification test.** For each hard creative constraint, verify it prevents generic drift—not merely restates brief keywords.

8. **Score and verdict.**

   - **PASS**: Specificity tests pass; tropes justified or absent.
   - **CHALLENGE**: Specific issues require revision but thesis may survive.
   - **FAIL**: Interchangeable concept; route to Creative Director for rework.

9. **Document required corrections.** Each item: failed test, evidence, severity, responsible owner, re-test requirement.

10. **Emit structured handoff.** On PASS, release to `acos-art-director` and `acos-experience-architect`. On FAIL/CHALLENGE, route to `acos-creative-director`.

## Required outputs / deliverables

Primary: **Anti-Generic Review Report** containing:

- Test results (name-swap, mechanism, trope, differentiation, constraint).
- Verdict: PASS | CHALLENGE | FAIL.
- Flagged patterns with justified/unjustified classification.
- Required corrections (if any) with severity and owner.
- Re-test requirements.
- Structured handoff block.

## Rejection / failure conditions

This skill **issues** rejection verdicts; it fails its own obligation when:

- Verdict issued without documented test evidence.
- Technique rejected without checking project justification.
- House-style rule proposed as global ACOS policy.
- Creative Director's job performed (rewriting thesis instead of challenging).
- PASS granted on interchangeable concept.
- Domain-specific bias injected (e.g., assuming 3D is always generic or always required).

Self-fail route: revise report or escalate to quality process owner.

## Handoff contract

```yaml
status: pass | challenge | fail | no_activation
inputs_used:
  - type: creative_direction | proposal | prior_report
    ref: "<artifact path or id>"
decisions:
  - test: name_swap | mechanism | trope | differentiation | constraint
    result: pass | fail
    evidence: "<observation>"
  - verdict: pass | challenge | fail
constraints:
  - "<correction downstream must satisfy before proceeding>"
open_risks:
  - "<residual genericness or justification gap>"
evidence:
  - type: test_result | trope_flag
    detail: "<specific finding>"
deliverables:
  - artifact: "<path to Anti-Generic Review Report>"
next_owner: acos-art-director | acos-experience-architect | acos-creative-director
rejection_route: acos-creative-director
```

On **pass**: `next_owner` may list both art and experience architects (parallel). On **fail/challenge**: `next_owner` is `acos-creative-director`.

## QA / evaluation contract

| Check | Pass criterion |
|-------|----------------|
| Test completeness | All five test types executed or marked N/A with reason |
| Justification fairness | No technique rejected without justification review |
| Evidence | Each fail flag cites artifact content |
| Scope | No rewritten thesis; corrections are actionable challenges |
| Neutrality | No ACOS house style promoted |

Re-test after Creative Director revision: full or targeted re-run of failed tests minimum.

Downstream skills should not treat direction as approved until this skill records **pass** (or explicit human override documented outside ACOS).

Aligns with `core/QUALITY_GATES.md` hard reject: materially generic/interchangeable result despite differentiated brief.

## Evidence requirements

| Type | Requirement |
|------|-------------|
| Planning evidence | Quotes or IDs from evaluated artifact |
| Visual evidence | Not required unless reviewing art drafts |
| Runtime evidence | Not required |

Distinguish: **observed generic pattern** vs. **inferred risk** (label confidence).

## Memory interaction

Per `core/MEMORY_POLICY.md`:

**May read:** project artifacts; `memory/failures/` entries tagged genericness for same domain patterns.

**May propose for project memory:** failed trope patterns and corrections with project scope.

**Must NOT promote to global:** "always avoid cards/gradients/glass" as ACOS law; technique bans without cross-project validation.

Do not populate memory during Phase C foundation.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|-------|--------------|
| `acos-creative-director` | Upstream producer; receives FAIL/CHALLENGE routes |
| `acos-art-director` | Downstream after PASS; may receive secondary review if visual drafts regress |
| `acos-experience-architect` | Downstream after PASS |
| `acos-creative-critic` | Independent later evaluation; not duplicate of this challenge pass |
| `acos-quality-gate` | Final gate; may reject genericness with route to creative/anti-generic |
| `acos-reference-analysis` | Supplies non-copy boundaries; anti-generic detects copy-disguised-as-inspiration |

**Overlap prevention:** This skill **challenges**; it does not **author** creative or visual direction. One failed test with correction list beats a rewritten concept.

## Non-goals

- Defining ACOS permanent visual style or global technique bans.
- Writing creative thesis or art direction specifications.
- Replacing critics or quality gate.
- Auto-failing common techniques without justification review.
- Running on projects with no evaluable creative content.
- Inventing competitor comparisons not grounded in brief.
