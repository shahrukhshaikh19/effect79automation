---
name: acos-product-form-modeler
description: Activate after an approved industrial form specification exists. Orchestrates Blender blockout and primary-form development into multi-view clay evidence. Do not activate to invent product identity, apply beauty materials, export a production GLB, or build the website.
---

# acos-product-form-modeler (ACOS-16)

Orchestrates **form development in Blender** from an approved `form_specification.yaml`. Reuses canonical Blender skills. Does not duplicate boolean/bevel tutorials.

**Detail cannot rescue incorrect primary form.** Branding, grooves, screws, cinematic lighting, and expensive materials are forbidden until Product Form Gate APPROVED.

This is SubD / Blender form development — not Alias Class-A. Claims stay truthful: controlled curvature, clean highlight flow, intentional transitions, strong sections.

## Purpose

Turn the committed form specification into clay-readable geometry and multi-view neutral evidence.

Staged thinking (do not skip):

```
approved form specification
  → dimensioned / proportional blockout
  → primary surfaces
  → multi-angle clay
  → proportion correction
  → surface refinement
  → secondary construction
  → joints / interfaces / seams
  → tertiary only if the spec requires function
  → highlight / section inspection
  → final clay review
```

## Activation / trigger conditions

Activate only when:

1. `requires_industrial_form` is true
2. Design Gate is APPROVED
3. ACOS-15 artifacts exist and are contract-valid
4. Host stage is `FORM_AUTHORING` or the form gate has REJECTED back to form development

## Do-not-activate conditions

Do **not** activate to:

- Invent product identity (ACOS-15)
- Lookdev, beauty lighting, or chromatic materials
- Export a production GLB or write `implementation/index.html`
- Judge clay independently (ACOS-17) or ship (ACOS-13)
- Model landscapes or non-industrial heroes

## Responsibility boundary

### Owns

- `direction/form_model.yaml`
- Driving Blender via existing skills for **clay form only**
- Writing `evidence/form-clay/` required views
- Challenging primitive-derived primary volumes

### Delegates (do not rewrite)

| Need | Skill |
|---|---|
| Pipeline / MCP / collections | `blender-director` |
| Edit mode, modifiers, cleanup | `blender-modeler` |
| Boolean / bevel / panels after primary form reads | `hard-surface` |
| Everyday part logic / scale | `prop-artist` |

### Does NOT own

- Product identity (ACOS-15)
- Materials / lookdev / lighting beauty
- Production GLB / Three.js
- Industrial-design pass/fail (ACOS-17)
- Ship (ACOS-13)

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| `direction/product_design.yaml` | Yes | Contract-valid ACOS-15 |
| `direction/form_specification.yaml` | Yes | Envelope, parts, views |
| Live Blender MCP | Yes | Clay is authored in Blender |
| Prior form-critic fail | If re-entry | Correct form, not paint |

## Exact procedure / workflow

1. **ingest_spec** — Read both ACOS-15 files. If spec is adjective-only, return to ACOS-15.
2. **dimensioned_blockout** — Blockout matches envelope numbers. Default-named Cube/Sphere/Cylinder as the **hero** is a fail even as a start if left untransformed into specified sections.
3. **primary_forms** — Build the committed primary volumes. Challenge any mesh that still fits a UV-sphere or plane.
4. **clay_capture** — Neutral / clay / grey shader. No chromatic beauty, no crushed night studio, no bloom hide.
5. **proportion_correct** — Fix from clay, not from roughness maps.
6. **joints_and_seams** — Only after primary silhouette reads.
7. **handoff_clay** — Required views on disk. Production export is forbidden.

Required clay views under `evidence/form-clay/` (PNG > 4KB):

| File stem | View |
|---|---|
| `front` | Front elevation |
| `profile` | Side / profile |
| `rear` | Rear |
| `front34` | Front three-quarter |
| `rear34` | Rear three-quarter |
| `proportion` | Proportion-critical close-up that still shows envelope |

Add `top.png` when the spec envelope needs plan. Add `joint.png` when mechanics are not `none`.

## Required outputs

`direction/form_model.yaml` with `skill_id: ACOS-16`, live hash, and `procedure_evidence` for every required key.

Must record:

- `spec_ref` pointing at `direction/form_specification.yaml`
- `blockout_units` matching envelope
- `primary_forms` named to spec parts
- `primitive_challenge` — what was rejected as sphere/plane/cylinder-derived
- `clay_views` list matching files on disk
- `production_glb_exported: false`
- `beauty_lookdev_done: false`

## Rejection / failure conditions

Contract fail when:

- Lookdev or production GLB happens in this stage
- Primary form is decorated instead of corrected
- Clay views missing or are beauty/dark cinematic frames
- Hero remains two spheres and a rod
- Spec was not ingested (`spec_ref` missing)

## Handoff contract

```yaml
handoff:
  skill: acos-product-form-modeler
  status: ready_for_form_critic | return_to_product_design
  inputs_used: [direction/form_specification.yaml]
  decisions: [primary_forms, clay_views]
  constraints: [no_production_glb, no_beauty_lookdev]
  open_risks: []
  evidence: evidence/form-clay/
  deliverables:
    - direction/form_model.yaml
    - evidence/form-clay/
  next_owner: acos-industrial-design-critic
  rejection_route: acos-industrial-product-designer
```

On spec error: `next_owner: acos-industrial-product-designer`.

## QA / evaluation

Host `validate_form_model` plus `validate_clay_evidence` must pass. Product Form Gate re-checks primitives if a GLB leaked into `implementation/`. This skill cannot pass itself.

## Evidence requirements

Neutral clay PNGs under `evidence/form-clay/` with the required stems. Lookdev, viewports, and crushed studio frames are not clay. YAML listing views without files is a fail.

## Memory interaction

Do not store one product’s blockout recipe as a global ACOS mesh recipe. Record form-gate failures through `acos-failure-learning` after observed reject.

## Relationship to neighboring ACOS skills

| Skill | Relationship |
|---|---|
| `acos-industrial-product-designer` | Upstream spec; return here if adjective-only |
| `blender-director` / `blender-modeler` / `hard-surface` / `prop-artist` | Delegated craft; this skill orchestrates clay |
| `lookdev` / `materials` / `export-pipeline` | Locked until Product Form Gate APPROVED |
| `acos-industrial-design-critic` | Independent clay verdict |
| `acos-3d-critic` | Later lit/runtime, not clay |

## Non-goals

- Not product identity
- Not beauty lookdev
- Not production GLB or website
- Not Alias Class-A
- Not a critic or ship gate
