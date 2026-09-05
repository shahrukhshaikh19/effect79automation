---
name: acos-industrial-product-designer
description: Activate for flagship physical consumer or industrial products that must be designed before Blender production. Owns product architecture, scale, proportions, silhouette directions, parts, joints, seams, and CMF intent. Do not activate for landscapes, UI-only work, or to model meshes.
---

# acos-industrial-product-designer (ACOS-15)

Proprietary industrial / product-design reasoning. Translates a physical-product brief into an **approved form specification** before detailed Blender geometry, materials, or web integration.

This is **not** Blender modeling. A modeler who knows bevels can still design a bad product. This skill owns the missing layer: archetype → package → proportion → part architecture → mechanical interfaces → multi-view spec.

Authority: `core/ROUTING.md`, `docs/FLAGSHIP_PREMIUM_WORKFLOW.md`. Host Product Form Gate consumes this spec.

## Purpose

Produce a manufacturable, original product-design specification that a form modeler can execute without guessing identity or proportions.

For any applicable product (wearable, consumer electronic, appliance, vehicle-as-object, other authored industrial good) reason about:

- product archetype and functional architecture
- human / physical scale and package envelope
- ergonomics where the product touches a body or hand
- primary proportions and silhouette
- at least two form directions before committing one
- primary / secondary / tertiary form hierarchy
- recognizable original product identity (not a category cliché)
- part architecture and assembly splits
- articulation, hinges, pivots, interfaces
- seams and material transitions
- manufacturing plausibility
- CMF intent (not shader graphs)
- multi-view form specification for modeling

## Activation / trigger conditions

Activate when routing sets `requires_industrial_form: true` on a flagship / authored-3D task and Design Gate is APPROVED (host stage `PRODUCT_DESIGN`).

Also activate when Product Form Gate REJECTED the spec itself (adjective-only, missing parts, illegal primitive-as-hero instruction).

## Do-not-activate conditions

Do **not** activate when:

- The brief is a landscape, interior, environment, or abstract hero
- The work is UI-only, settings, or thin decorative 3D
- The task is to model meshes, lookdev, or export GLB
- The task is cinematic scene/camera direction after form is already specified (`acos-cinematic-3d-director`)
- The task is clay critique (`acos-industrial-design-critic`) or ship (`acos-quality-gate`)
- Industrial form is not in the routed signals

## Responsibility boundary

### Owns

Product design reasoning and `direction/product_design.yaml` + `direction/form_specification.yaml`.

### Does NOT own

- Mesh, modifiers, UVs (`acos-product-form-modeler`, Blender skills)
- Lookdev, production GLB, Three.js
- Lit 3D critique (`acos-3d-critic`)
- Industrial-design verdict on clay (`acos-industrial-design-critic`)
- Ship decision (`acos-quality-gate`)

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Project request / brief | Yes | Physical product, not environment |
| Creative / art direction (if planned) | After Design Gate | Identity language, not mesh |
| Prior form-gate reject | If re-entry | Spec defects only |

Do not invent a product category the brief did not ask for.

## Exact procedure / workflow

1. **confirm_activation** — Verify industrial-form route. If the brief is an environment, stop.
2. **archetype_and_architecture** — Name the product type, what must move, what must be held or worn, what must be sealed.
3. **scale_and_envelope** — Real dimensions or justified ranges. Human scale when relevant.
4. **form_directions** — At least two distinct silhouette directions. Pick one with a written reason. Do not skip exploration.
5. **form_hierarchy** — Primary volumes, secondary construction, tertiary only as function (not decoration).
6. **parts_and_mechanics** — Named parts, joints, pivots, travel, clamp or hinge logic, assembly splits, material boundaries.
7. **cmf_intent** — Finish families and transitions. Not Principled graphs.
8. **multi_view_spec** — What front, profile, rear, ¾, and joint views must prove.
9. **handoff** — Form specification locked for `acos-product-form-modeler`. No mesh yet.

## Required outputs

`direction/product_design.yaml` and `direction/form_specification.yaml` must include:

- `skill_id: ACOS-15` and live `skill_md_sha256`
- `procedure_evidence` for every required procedure key (unique prose)
- `archetype`, `committed_direction`, `rejected_directions` (≥1 rejected)
- `envelope` with numeric or bounded dimensions
- `part_architecture` as a list of named parts with job + interface
- `mechanics` (pivots / travel / constraints) or explicit `mechanics: none` with reason
- `form_hierarchy.primary` that a clay silhouette can test
- `cmf_intent`
- `modeling_views` listing required clay views

Adjectives without mechanism (`premium`, `sculpted`, `flagship`) are not a spec.

## Rejection / failure conditions

Fail this skill’s contract when:

- Only one form direction exists
- Parts are unnamed (“left blob”, “metal bit”)
- Spec tells Blender to start from a UV sphere / cylinder / torus as the hero volume
- CMF or branding is used to invent identity the silhouette lacks
- Meshes or lookdev are produced here
- Envelope or modeling views are missing

## Handoff contract

```yaml
handoff:
  skill: acos-industrial-product-designer
  status: ready_for_form_modeling | blocked | not_applicable
  inputs_used: [brief, design_gate_artifacts]
  decisions: [committed_direction, envelope, part_architecture]
  constraints: [no_mesh, no_lookdev, no_production_glb]
  open_risks: []
  evidence: [direction/product_design.yaml, direction/form_specification.yaml]
  deliverables:
    - direction/product_design.yaml
    - direction/form_specification.yaml
  next_owner: acos-product-form-modeler
  rejection_route: acos-industrial-product-designer
```

## QA / evaluation

Host `validate_product_design` must pass before FORM_AUTHORING. Thin adjective YAML is a fail. Product Form Gate re-checks the spec. This skill cannot APPROVE form or ship.

## Evidence requirements

Written spec files only. No clay, no lookdev, no implementation. Procedure evidence must be unique prose per required key. A boolean is not proof.

## Memory interaction

Do not promote one product’s ID language to global ACOS style. Propose failures via `acos-failure-learning` only after an observed form-gate reject.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-creative-director` / `acos-art-director` | Upstream thesis and visual language; this skill owns product architecture |
| `acos-cinematic-3d-director` | Scene/camera after form is specified; does not invent the product |
| `acos-product-form-modeler` | Executes this spec as clay |
| `acos-industrial-design-critic` | Judges clay against this spec |
| `acos-3d-critic` | Lit/runtime 3D after form gate |
| `acos-quality-gate` | Ship only; never a form substitute |

## Non-goals

- Not a Blender modeler
- Not lookdev or CMF shader graphs
- Not a website or Three.js skill
- Not Alias Class-A surfacing
- Not a ship gate
- Not a landscape or environment designer
