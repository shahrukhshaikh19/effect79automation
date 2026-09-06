"""Blender-only form build. No PyYAML. Reads direction/form_plan.json.

Readable clay: one tray case, two cups, two three-volume buds, lid on a rear pin.
No through-boolean. No _clay_iterN novels.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


def build_and_render(project_dir: str | Path) -> list[str]:
    import bpy
    from mathutils import Vector

    project = Path(project_dir)
    plan = json.loads((project / "direction" / "form_plan.json").read_text(encoding="utf-8"))
    width, depth, height = [float(v) for v in plan["envelope_mm"]]
    base_h = 12.0
    lid_h = 8.0
    seam = base_h

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    mat = bpy.data.materials.get("CLAY_Form") or bpy.data.materials.new("CLAY_Form")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.48, 0.48, 0.46, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.72
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def assign(obj):
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    def apply(obj):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

    def bevel(obj, width_mm: float = 4.5, segs: int = 4):
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = width_mm
        mod.segments = segs
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier="bevel")
        obj.select_set(False)

    def look_at(obj, target):
        direction = Vector(target) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, base_h / 2))
    base = bpy.context.active_object
    base.name = "Case_Base"
    base.scale = (width, depth, base_h)
    apply(base)
    bevel(base, 5.0, 5)
    assign(base)

    cups = []
    for side, x in (("L", -12.2), ("R", 12.2)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5, location=(x, 0.0, base_h - 1.2))
        cup = bpy.context.active_object
        cup.name = f"Well_{side}"
        cup.scale = (14.4, 13.2, 8.8)
        apply(cup)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(plane_co=(x, 0.0, base_h + 1.6), plane_no=(0.0, 0.0, 1.0), clear_outer=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        apply(cup)
        assign(cup)
        cups.append(cup)

    bpy.ops.object.select_all(action="DESELECT")
    base.select_set(True)
    for cup in cups:
        cup.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = "Case_Base"

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, seam + lid_h / 2))
    lid = bpy.context.active_object
    lid.name = "Case_Lid"
    lid.scale = (width, depth, lid_h)
    apply(lid)
    bevel(lid, 5.0, 5)
    assign(lid)

    def bud(name, x):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5)
        housing = bpy.context.active_object
        housing.name = f"{name}_Housing"
        housing.scale = (10.0, 9.0, 9.2)
        housing.location = (x, 0.6, 12.2)
        apply(housing)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.5)
        tip = bpy.context.active_object
        tip.name = f"{name}_Tip"
        tip.scale = (5.0, 4.6, 4.2)
        tip.location = (x, -6.4, 8.6)
        apply(tip)
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.5, depth=1.0)
        stem = bpy.context.active_object
        stem.name = f"{name}_Stem"
        stem.scale = (1.7, 1.7, 11.0)
        stem.rotation_euler = (math.radians(72), 0.0, 0.0)
        stem.location = (x, 6.2, 12.2)
        apply(stem)
        for piece in (housing, tip, stem):
            assign(piece)
        bpy.ops.object.select_all(action="DESELECT")
        housing.select_set(True)
        tip.select_set(True)
        stem.select_set(True)
        bpy.context.view_layer.objects.active = housing
        bpy.ops.object.join()
        housing.name = name
        return housing

    left = bud("Earbud_Left", -12.2)
    right = bud("Earbud_Right", 12.2)

    hinge = bpy.data.objects.new("Hinge_Pin", None)
    bpy.context.collection.objects.link(hinge)
    hinge.empty_display_type = "PLAIN_AXES"
    hinge.location = (0.0, -depth / 2 + 1.2, seam)
    bpy.context.view_layer.update()
    bpy.context.scene.cursor.location = hinge.location
    bpy.ops.object.select_all(action="DESELECT")
    lid.select_set(True)
    bpy.context.view_layer.objects.active = lid
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    lid.parent = hinge
    lid.matrix_parent_inverse = hinge.matrix_world.inverted()
    hinge.rotation_euler = (math.radians(-55), 0.0, 0.0)

    target = (0.0, 0.0, 14.0)
    span = max(width, depth, 36.0)
    dist = span * 2.15
    cams = {
        "front": (0.0, -dist, 28.0),
        "profile": (dist, -8.0, 28.0),
        "rear": (0.0, dist, 28.0),
        "front34": (dist * 0.78, -dist * 0.78, 34.0),
        "rear34": (dist * 0.78, dist * 0.78, 34.0),
        "proportion": (0.0, -span * 1.6, 24.0),
        "joint": (22.0, -span * 1.35, seam + 14.0),
    }
    for name, loc in cams.items():
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = f"CAM_{name}"
        camera.location = loc
        look_at(camera, (0.0, -4.0, seam) if name == "joint" else target)
        camera.data.lens = 60

    sun = bpy.data.objects.new("LGT_ClaySun", bpy.data.lights.new("LGT_ClaySun", "SUN"))
    sun.data.energy = 1.8
    sun.rotation_euler = (math.radians(52), 0.0, math.radians(28))
    bpy.context.collection.objects.link(sun)
    fill = bpy.data.objects.new("LGT_ClayFill", bpy.data.lights.new("LGT_ClayFill", "AREA"))
    fill.data.energy = 22
    fill.data.size = 100
    fill.location = (24, -40, 36)
    bpy.context.collection.objects.link(fill)
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.28, 0.28, 0.27, 1.0)
        bg.inputs[1].default_value = 0.45

    out = project / "evidence" / "form-clay"
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = -0.15
    written = []
    for name in cams:
        obj = bpy.data.objects.get(f"CAM_{name}")
        if not obj:
            continue
        scene.camera = obj
        scene.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        written.append(name)
    _ = (left, right, height)
    return written
