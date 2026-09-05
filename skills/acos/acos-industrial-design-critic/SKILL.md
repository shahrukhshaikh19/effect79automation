---
name: acos-industrial-design-critic
description: Activate after multi-view clay evidence exists for a flagship physical product. Judges whether the product itself is professionally designed. Do not activate for lit lookdev, website visual QA, or if this chat modeled the form.
---

# acos-industrial-design-critic (ACOS-17)

Independent **industrial-design** critic. Distinct from `acos-3d-critic`.

`acos-3d-critic` asks: is this a credible 3D render / runtime mesh?

This skill asks: **is the physical product itself professionally designed?**

A technically clean mesh with good lighting can still FAIL.

## Purpose

Inspect **neutral clay / multi-view evidence** and challenge product form before materials, production GLB, or web integration.

Must challenge:

- silhouette
- proportions
- form hierarchy
- primitive-derived appearance
- generic product archetype
- ergonomics
- product identity
- mechanical plausibility
- articulation
- joints / interfaces
- surface transitions
- inconsistent thickness
- manufacturing credibility
- part architecture
- arbitrary detailing
- details used to hide weak primary form
- close-up credibility

## Activation / trigger conditions

Activate when host stage is `FORM_CRITICS`, clay views exist, and a form critic pass is open (`form-critic-pass` with a distinct `ACOS_HOST_CONTEXT_ID`).

## Do-not-activate conditions

Do **not** activate:

- to approve lookdev or browser captures
- if this session authored the form (record independence fail; do not `pass`)
- for landscapes or non-industrial tasks
- as a substitute for Quality Gate or `acos-3d-critic`
- before the required clay set exists

## Responsibility boundary

### Owns

`critics/industrial_design.yaml` and a `pass` | `fail` | `blocked_insufficient_evidence` verdict from clay pixels.

### Does NOT own

- Rewriting the spec (ACOS-15)
- Remodeling (ACOS-16)
- Lit runtime 3D QA (ACOS-12)
- DOM QA (ACOS-10)
- Ship (ACOS-13 / Product Form Gate aggregates this verdict)

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| `evidence/form-clay/` required views | Yes | Inspect pixels, not YAML |
| `direction/form_specification.yaml` | Yes | Archetype and parts to test |
| Open `form_critic_pass_id` | Yes | From `form-critic-pass` |
| Distinct host context | Yes | `pass` illegal otherwise |

Ignore `evidence/lookdev/` and viewport beauty.

## Exact procedure / workflow

1. **independence** — Confirm distinct `ACOS_HOST_CONTEXT_ID` / form critic pass. If same as producer, verdict cannot be `pass`.
2. **inspect_clay** — Open every required file in `evidence/form-clay/`. Ignore `evidence/lookdev/` and viewport beauty.
3. **silhouette_proportion** — Does the product read as the spec archetype from front and profile?
4. **primitive_derived** — Earcups/bodies that are still spheres, panels that are still planes, yokes that are still unarticulated cylinders → fail.
5. **mechanics_and_identity** — Joints exist if spec requires them. Identity is not a logo on a generic volume.
6. **detail_hiding_form** — Grooves, screws, fins, anisotropy used to disguise unresolved primary → fail.
7. **handoff** — `verdict: pass` only with zero critical/major form defects.

## Required outputs

`critics/industrial_design.yaml`:

- `skill_id: ACOS-17`, live `skill_md_sha256`
- `form_critic_pass_id` matching the open pass
- `inspected_rendered_output: true`
- `independence` not `same_host_session_as_producer`
- `evidence_refs` listing clay paths only
- `findings[]` with `id`, `severity` (`critical|major|minor|observation`), `view`, `owner` (`acos-industrial-product-designer` or `acos-product-form-modeler`)
- `verdict: pass|fail|blocked_insufficient_evidence`
- `procedure_evidence` for every required key

## Rejection / failure conditions

- **critical** — Not readable as the specified product; primitive hero; missing required articulation
- **major** — Proportion or joint failure on a required view; generic archetype; detail hiding form
- **minor** — Localized construction note
- **observation** — Taste, not fail

`fail` if any critical or major remains. `pass` with same-session independence is illegal. Citing lookdev as form evidence is a fail.

Never emit ship `APPROVED`.

## Handoff contract

```yaml
handoff:
  skill: acos-industrial-design-critic
  status: pass | fail | blocked_insufficient_evidence
  inputs_used: [evidence/form-clay/, direction/form_specification.yaml]
  decisions: [verdict]
  constraints: [clay_only, no_lookdev_citations]
  open_risks: []
  evidence: critics/industrial_design.yaml
  deliverables:
    - critics/industrial_design.yaml
  next_owner: product_form_gate
  rejection_route:
    - owner: acos-product-form-modeler
    - owner: acos-industrial-product-designer
```

## QA / evaluation

Host `validate_form_critic` requires DISTINCT form critic context for `pass`. Product Form Gate consumes the verdict. This skill cannot unlock lookdev or SHIP.

## Evidence requirements

Clay PNGs only. `evidence_refs` must include `evidence/form-clay/` and must not cite lookdev or viewports. Findings must name the view inspected.

## Memory interaction

Do not store one product’s ID taste as a global ACOS form style. Route observed form-gate rejects through `acos-failure-learning` after the gate writes.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-industrial-product-designer` | Spec owner; receives spec defects |
| `acos-product-form-modeler` | Form owner; receives clay defects |
| `acos-3d-critic` | Later lit/runtime credibility — not this skill |
| `acos-visual-critic` | DOM/layout — not clay |
| `acos-quality-gate` | Ship only after form gate and later critics |

**Overlap prevention:** Clay vs beauty. This skill never substitutes for ACOS-12 or ACOS-13.

## Non-goals

- Not a modeler
- Not lookdev QA
- Not website visual QA
- Not a ship gate
- Not a same-session self-approve
