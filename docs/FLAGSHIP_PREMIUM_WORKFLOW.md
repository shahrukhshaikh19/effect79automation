# Flagship premium 3D — workflow locks

This is the production contract for a **clear premium 3D prompt** into Cursor, Claude Code, or Codex.

ACOS stays domain-neutral. A settings form does not get Blender. A cinematic / premium / physical-product / WebGL-hero prompt does.

The user does not name skills. The workflow does.

## What the host must do

```text
python tools/host_driver/run_stage.py init --prompt "<clear premium 3D request>"
```

Then follow `CURRENT_HOST_BRIEF.md` only. Invoke listed skills. Do not slash-pick. Do not skip Blender because a lathe is easier.

## Four locks

### 1. Intake

A flagship prompt is **authored 3D**, not a marketing adjective. It sets when the request needs Blender/GLB or cinematic/physical-hero 3D — even if the words “premium” / “cinematic” are absent. A locked still brief that says “Blender must model this and export GLB” is flagship.

- `deliverable_profile: interactive_3d`
- `quality_bar: flagship`
- `reconstruction_path: blender_authoring`
- `blender: AVAILABLE` when a Blender binary is on the machine (override with `ACOS_BLENDER_CAPABILITY`)

If Blender MCP/app is down, the host **tells the user and waits**. It does not skip. After the user connects, the host pings MCP, runs `confirm-blender --mcp-live`, then starts.

```text
python tools/host_driver/run_stage.py blender-status
python tools/host_driver/run_stage.py confirm-blender --mcp-live
```

### 2. Route

`interactive_3d` + `quality_bar: flagship` activates the craft pack, not only `threejs-core`:

- Three.js: core, materials, lighting, camera, loaders
- Motion: GSAP core + ScrollTrigger
- Blender: director, modeler, prop-artist, materials, lookdev, lighting, asset-optimization, export
- Then the existing cinematic / responsive / critic / gate skills

### 3. Production gate

`index.html` is not enough. `advance` stays on PRODUCTION until:

- a hero `glb` / `gltf` exists under `implementation/`
- `direction/blender_export.yaml` has `blender_used: true`
- materials / lighting / camera procedure artifacts exist
- production notes do not record a convenience Blender skip

A lathe, cube, or model-viewer as the hero is a blocked production, not a ship candidate.

### 4. Host brief

PRODUCTION **Invoke now** lists those native `/skill` names. The host reads each `SKILL.md` and executes it. Catalog presence is not activation.

### 5. Blender MCP wait

On a flagship prompt, if Blender MCP or the Blender app is off:

1. Stage is `WAITING_BLENDER`. No creative, no production, no lathe fallback.
2. The host must tell the user, in the chat: Blender MCP/app band hai. Skip nahi hoga. Connect karo, phir confirm.
3. After the user connects, the host calls Blender MCP `get_addon_status`.
4. Only if that ping succeeds: `python tools/host_driver/run_stage.py confirm-blender --mcp-live`
5. Then the workflow starts. `advance` while waiting does not skip this lock.

## Expected path

```text
clear prompt
  → flagship intake
  → if Blender MCP/app down: tell user, wait, confirm, then start
  → Design Gate on direction
  → if industrial form: product design spec → clay → form critic → Product Form Gate
  → Blender authors the hero (lookdev / production GLB only after form APPROVED)
  → export GLB
  → Three.js materials / lighting / camera load it
  → scroll / DOM integration
  → HTTP capture
  → independent critics (new chat)
  → quality gate
```

Premium is the bar for this prompt class. The conductor cannot invent beauty, but it can refuse a first-pass primitive as complete.

Lookdev lock: at least two PNGs under `evidence/lookdev/` before production advances. After browser capture, if the hero is a crushed night-silhouette and the mood reference is lit, `advance` returns to PRODUCTION. Files and a GLB are not enough.

Craft lock: export YAML is not skill execution. Director, modeler, prop-artist, materials, and lookdev must have artifacts + receipts. Physical products also require hard-surface. A sphere/cylinder/plane dump, an unchecked modeling checkbox, or a macro lookdev crop fails production.

Industrial-form lock: wearables, consumer electronics, appliances, and other manufacturable devices must pass Product Form Gate (`gate/product_form_gate.yaml`) before beauty lookdev or web. That gate is not Quality Gate and cannot SHIP. Landscapes are not industrial form.
