"""Render three orthographic inspection images from the editable character base.

Usage:
  blender -b tools/blender/character_base.blend --python tools/blender/render_character_turnaround.py

The renders are diagnostic images of a rough blockout, not polished concept art.
"""
import bpy
import os
from mathutils import Vector

root = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8
scene.world.color = (0.14, 0.14, 0.14)

for ob in bpy.data.objects:
    if ob.type == "MESH":
        for mat in ob.data.materials:
            if mat is not None and mat.use_nodes:
                shader = mat.node_tree.nodes.get("Principled BSDF")
                if shader is not None:
                    shader.inputs["Base Color"].default_value = mat.diffuse_color

light_data = bpy.data.lights.new("Inspection soft light", type="AREA")
light_object = bpy.data.objects.new("Inspection soft light", light_data)
scene.collection.objects.link(light_object)
light_object.location = (1.5, -2.5, 4.0)
light_data.energy = 650
light_data.shape = "DISK"
light_data.size = 5.0
scene.camera = None

camera_data = bpy.data.cameras.new("Turnaround orthographic camera")
camera = bpy.data.objects.new("Turnaround orthographic camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = "ORTHO"
camera_data.ortho_scale = 2.45

target = Vector((0, 0, 0.93))
views = {
    "front": (0, -4.5, 1.35),
    "side": (4.5, 0, 1.35),
    "back": (0, 4.5, 1.35),
}
for name, location in views.items():
    camera.location = location
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(root, "character_" + name + ".png")
    bpy.ops.render.render(write_still=True)
    print("Saved " + scene.render.filepath)
