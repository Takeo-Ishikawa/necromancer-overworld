"""Necromancer Overworld 0.8: editable Blender character blockout.

Run in Blender 4.x:
    blender -b --python tools/blender/generate_necromancer_base.py

Produces character_base.blend and character_base.fbx in the script directory.
This is a *modeling foundation*, not a final high-fidelity sculpt.
All clothing, hair and accessories remain separate editable objects.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgba, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

skin = material("01 - pale warm skin", (0.72, 0.49, 0.42, 1))
shadow_skin = material("02 - skin muscle definition", (0.58, 0.36, 0.32, 1))
hair = material("03 - ash lavender hair", (0.48, 0.43, 0.52, 1))
hair_light = material("04 - hair highlights", (0.68, 0.62, 0.72, 1))
cloth = material("05 - charcoal trousers", (0.12, 0.105, 0.14, 1))
cloth_light = material("06 - trouser seams", (0.19, 0.16, 0.19, 1))
leather = material("07 - worn dark leather", (0.16, 0.105, 0.075, 1))
gold = material("08 - aged bronze embroidery", (0.55, 0.37, 0.16, 1), 0.43, 0.65)
eye = material("09 - dark eyes", (0.12, 0.09, 0.11, 1))

def uv(name, location, scale, mat, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    return ob

def link(name, a, b, width_a, width_b, mat, vertices=16):
    a, b = Vector(a), Vector(b)
    axis = b-a
    mid = (a+b)*0.5
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=width_a, radius2=width_b,
                                    depth=axis.length, location=mid)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = axis.to_track_quat('Z','Y').to_euler()
    ob.data.materials.append(mat)
    for poly in ob.data.polygons: poly.use_smooth = True
    return ob

# Anatomical coordinates: 1.80 m, standing at z=0, facing -Y.
uv("Torso - chest", (0, 0, 1.38), (0.32, 0.175, 0.245), skin)
uv("Torso - waist", (0, 0.008, 1.15), (0.235, 0.15, 0.23), skin)
uv("Pelvis under trousers", (0, 0, 0.98), (0.265, 0.17, 0.15), cloth)
uv("Neck", (0, 0, 1.66), (0.09, 0.09, 0.12), skin)
uv("Head - face", (0, -0.015, 1.765), (0.115, 0.105, 0.145), skin)
uv("Chin - defined", (0, -0.072, 1.681), (0.068, 0.061, 0.037), skin)
uv("Lower lip", (0, -0.124, 1.712), (0.034, 0.008, 0.009), shadow_skin)
uv("Upper lip", (0, -0.123, 1.725), (0.032, 0.007, 0.007), shadow_skin)
uv("Jaw", (0, -0.058, 1.706), (0.095, 0.072, 0.08), skin)
uv("Nose", (0, -0.122, 1.761), (0.021, 0.032, 0.034), skin)
for side in (-1, 1):
    tag = "L" if side < 0 else "R"
    x = side
    uv(tag+" ear", (x*0.119, 0, 1.76), (0.025, 0.025, 0.043), skin)
    uv(tag+" eye", (x*0.048, -0.112, 1.786), (0.024, 0.009, 0.010), eye)
    uv(tag+" brow ridge", (x*0.05, -0.109, 1.814), (0.052, 0.018, 0.016), skin)
    uv(tag+" cheekbone", (x*0.082, -0.085, 1.752), (0.046, 0.029, 0.026), skin)
    uv(tag+" clavicle", (x*0.185, -0.148, 1.574), (0.13, 0.025, 0.023), skin)
    uv(tag+" oblique", (x*0.196, -0.107, 1.236), (0.065, 0.043, 0.105), skin)
    uv(tag+" pectoral", (x*0.165, -0.153, 1.435), (0.155, 0.07, 0.095), skin)
    # Layered muscle volumes are editable, not sculpt-quality topology.
    for row in range(3):
        uv(tag+" abdominal "+str(row), (x*0.067, -0.149 + row*0.006, 1.33-row*0.09),
           (0.064, 0.029, 0.042), skin)
    uv(tag+" deltoid", (x*0.37, 0, 1.505), (0.125, 0.12, 0.13), skin)
    link(tag+" upper arm", (x*0.385, 0, 1.48), (x*0.43, -0.005, 1.19), 0.095, 0.073, skin)
    uv(tag+" elbow", (x*0.43, -0.005, 1.19), (0.075, 0.073, 0.065), skin)
    link(tag+" forearm", (x*0.43, -0.005, 1.19), (x*0.47, -0.055, 0.98), 0.075, 0.048, skin)
    uv(tag+" palm", (x*0.47, -0.065, 0.965), (0.055, 0.042, 0.064), skin)
    for finger in range(4):
        fx = x*0.47 + (finger-1.5)*0.023
        link(tag+" finger %d"%finger, (fx, -0.067, 0.929), (fx, -0.092, 0.895), 0.013, 0.009, skin, 10)
    uv(tag+" thumb", (x*0.53, -0.086, 0.958), (0.022, 0.026, 0.039), skin)
    link(tag+" upper armband", (x*0.399, 0, 1.395), (x*0.405, 0, 1.36), 0.100, 0.099, leather)
    link(tag+" bracer", (x*0.447, -0.023, 1.14), (x*0.463, -0.048, 1.015), 0.078, 0.058, leather)
    link(tag+" bracer bronze edge", (x*0.447, -0.023, 1.14), (x*0.449, -0.025, 1.125), 0.081, 0.079, gold)
    uv(tag+" hip pouch", (x*0.285, -0.02, 0.985), (0.092, 0.083, 0.115), leather)
    uv(tag+" pouch buckle", (x*0.34, -0.084, 0.995), (0.023, 0.01, 0.026), gold)
    uv(tag+" pouch flap", (x*0.285, -0.097, 1.039), (0.072, 0.018, 0.036), leather)
    # Cropped loose trousers and bare lower legs.
    link(tag+" trouser thigh", (x*0.14, 0, 0.96), (x*0.18, 0.005, 0.56), 0.17, 0.145, cloth)
    uv(tag+" trouser knee folds", (x*0.18, 0.005, 0.55), (0.15, 0.15, 0.12), cloth_light)
    for fold in range(3):
        uv(tag+" trouser fabric fold %d"%fold, (x*0.16, -0.137, 0.69-fold*0.085), (0.11, 0.012, 0.016), cloth_light, 16, 8)
    link(tag+" trouser cuff", (x*0.18, 0.005, 0.53), (x*0.18, 0.005, 0.48), 0.135, 0.13, cloth)
    link(tag+" bare shin", (x*0.18, 0.005, 0.48), (x*0.19, -0.015, 0.115), 0.085, 0.045, skin)
    uv(tag+" ankle", (x*0.19, -0.015, 0.10), (0.047, 0.048, 0.07), skin)
    uv(tag+" bare foot", (x*0.19, -0.085, 0.045), (0.075, 0.17, 0.045), skin)
    for toe in range(5):
        uv(tag+" toe "+str(toe), (x*0.19 + x*(toe-2)*0.018, -0.222+abs(toe-2)*0.01, 0.033),
           (0.013, 0.033, 0.019), skin, 12, 8)
    # Embroidery: ornamental metallic strips down outer trouser leg.
    for i in range(7):
        z = 0.88-i*0.058
        uv(tag+" gold trouser motif "+str(i), (x*0.295, -0.079, z),
           (0.012, 0.014, 0.035), gold, 12, 8)

link("Leather waist belt", (0, 0, 1.015), (0, 0, 1.075), 0.268, 0.266, leather, 32)
uv("Central bronze belt buckle", (0, -0.172, 1.045), (0.045, 0.013, 0.036), gold)
uv("Belt hanging leather strap", (0.11, -0.17, 0.975), (0.028, 0.018, 0.11), leather)

# Short tousled hair, asymmetric tapered locks, separate strands.
uv("Hair cap", (0, 0.018, 1.875), (0.125, 0.116, 0.078), hair)
for i in range(36):
    angle = i*math.tau/36
    x, y = math.cos(angle), math.sin(angle)
    start = (x*0.092, y*0.09, 1.89)
    end = (x*(0.14+0.018*(i%3)), y*(0.125+0.01*(i%4)), 1.78+0.025*(i%5))
    link("Hair lock %02d"%i, start, end, 0.031, 0.001,
         hair_light if i%5==0 else hair, 8)
for i in range(7):
    x = (i-3)*0.032
    link("Forehead fringe %d"%i, (x, -0.09, 1.91), (x-0.026, -0.14, 1.79+(i%2)*0.035),
         0.032, 0.002, hair, 8)

# Ground-independent asset root. Individual mesh objects deliberately remain separate.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "character_base.blend"))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT, "character_base.fbx"),
    use_selection=True, object_types={'MESH'}, apply_unit_scale=True, axis_forward='-Z', axis_up='Y')
print("Generated refined character blockout; sculpt, retopology, UV, and rigging are still required.")
