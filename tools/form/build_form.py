#!/usr/bin/env python3
"""Re-runnable industrial form builder.

Envelope in → named parts + clay cameras out.
Edit direction/form_specification.yaml and re-run this file.
Do not write _clay_iterN.py novels.

Plan only:
  python tools/form/build_form.py --project <project_dir> --plan-only

Blender (MCP can execute the same functions, or):
  blender --background --python tools/form/build_form.py -- --project <project_dir> --render
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.host.form_builder import build_plan, write_plan


def _argv_after_dash(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def _look_at(obj, target: tuple[float, float, float]) -> None:
    import bpy
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _new_mesh(name: str, primitive: str, **kwargs):
    import bpy

    if primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5, location=(0, 0, 0))
    elif primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.5, depth=1.0, location=(0, 0, 0))
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    return obj


def _apply_scale(obj) -> None:
    import bpy

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def _clay_material():
    import bpy

    mat = bpy.data.materials.get("CLAY_Form") or bpy.data.materials.new("CLAY_Form")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.42, 0.42, 0.40, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.62
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _assign(obj, mat) -> None:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def build_in_blender(plan: dict) -> None:
    import bpy

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    mat = _clay_material()
    built = {}
    for part in plan.get("parts") or []:
        name = str(part.get("name") or "Part")
        size = [float(v) for v in part.get("size_mm") or [20, 20, 20]]
        loc = [float(v) for v in part.get("location_mm") or [0, 0, 0]]
        kind = str(part.get("kind") or "")
        if kind == "in_ear_three_volume":
            housing = _new_mesh(f"{name}_Housing", "uv_sphere")
            housing.scale = (size[0] * 0.55, size[1] * 0.38, size[2] * 0.48)
            housing.location = (loc[0], loc[1], loc[2])
            _apply_scale(housing)
            tip = _new_mesh(f"{name}_Tip", "uv_sphere")
            tip.scale = (size[0] * 0.22, size[1] * 0.22, size[2] * 0.22)
            tip.location = (loc[0], loc[1] - size[1] * 0.28, loc[2] - size[2] * 0.08)
            _apply_scale(tip)
            stem = _new_mesh(f"{name}_Stem", "cylinder")
            stem.scale = (size[0] * 0.09, size[0] * 0.09, size[1] * 0.28)
            stem.rotation_euler = (math.radians(90), 0.0, 0.0)
            stem.location = (loc[0], loc[1] + size[1] * 0.18, loc[2] + size[2] * 0.04)
            _apply_scale(stem)
            for piece in (housing, tip, stem):
                _assign(piece, mat)
            bpy.ops.object.select_all(action="DESELECT")
            housing.select_set(True)
            tip.select_set(True)
            stem.select_set(True)
            bpy.context.view_layer.objects.active = housing
            bpy.ops.object.join()
            housing.name = name
            built[name] = housing
            continue
        obj = _new_mesh(name, "uv_sphere" if "case" in name.lower() else "cube")
        obj.scale = (size[0], size[1], size[2])
        obj.location = loc
        _apply_scale(obj)
        _assign(obj, mat)
        built[name] = obj
    if "Case_Lid" in built and "Case_Base" in built:
        hinge = bpy.data.objects.new("Hinge_Pin", None)
        bpy.context.collection.objects.link(hinge)
        base = built["Case_Base"]
        lid = built["Case_Lid"]
        hinge.location = (0.0, base.location.y - (base.dimensions.y * 0.42), lid.location.z - lid.dimensions.z * 0.45)
        lid.parent = None
        bpy.context.view_layer.update()
        lid.location = lid.location.copy()
        hinge.empty_display_type = "PLAIN_AXES"
        lid.parent = hinge
    for cam in plan.get("cameras") or []:
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = f"CAM_{cam['name']}"
        camera.location = tuple(float(v) for v in cam["location_mm"])
        _look_at(camera, tuple(float(v) for v in cam["target_mm"]))
        camera.data.lens = 50 if cam["name"] != "proportion" else 70
    sun = bpy.data.objects.new("LGT_ClaySun", bpy.data.lights.new("LGT_ClaySun", "SUN"))
    sun.data.energy = 2.4
    sun.rotation_euler = (math.radians(48), 0.0, math.radians(35))
    bpy.context.collection.objects.link(sun)
    fill = bpy.data.objects.new("LGT_ClayFill", bpy.data.lights.new("LGT_ClayFill", "AREA"))
    fill.data.energy = 40
    fill.data.size = 80
    fill.location = (40, -60, 50)
    bpy.context.collection.objects.link(fill)
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.22, 0.22, 0.21, 1.0)
        bg.inputs[1].default_value = 0.35


def render_clay(project_dir: Path, plan: dict) -> None:
    import bpy

    out = project_dir / "evidence" / "form-clay"
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = -0.35
    for cam in plan.get("cameras") or []:
        name = str(cam["name"])
        obj = bpy.data.objects.get(f"CAM_{name}")
        if not obj:
            continue
        scene.camera = obj
        scene.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Re-runnable form builder")
    parser.add_argument("--project", required=True, help="Host project directory")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args(_argv_after_dash(argv if argv is not None else sys.argv))
    project = Path(args.project).resolve()
    plan = build_plan(project)
    write_plan(project, plan)
    if args.plan_only:
        print(f"wrote {project / 'direction' / 'form_plan.yaml'}")
        return 0
    try:
        import bpy  # noqa: F401
    except ImportError:
        print("bpy missing — wrote plan only. Run inside Blender via tools/form/blender_build.py.")
        return 0
    from tools.form.blender_build import build_and_render

    written = build_and_render(project)
    print(f"built named parts; clay {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
