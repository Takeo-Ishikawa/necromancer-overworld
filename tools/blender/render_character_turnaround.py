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
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 640
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
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
