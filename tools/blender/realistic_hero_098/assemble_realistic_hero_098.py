"""Necromancer 0.9.8 — a SINGLE continuous editable trouser surface.

Build from the validated, CC0-derived, *continuous* 0.9.7 garment topology.
This is an independent new cloth mesh object, not separate thigh/pelvis lofts.
A subtle textile sculpt, UV guide and stitch curves are editable. The original
adult CC0 Body Male - Realistic and both original eyes remain bit-for-bit
unchanged; no Unity change, rigging, or animations.

The rejected 0.9.7 experimental tubes/bridges remain hidden in the .blend
for study, but cannot leak into FBX export or render.
"""
import os
import json
import runpy
import math
import struct
import hashlib
from collections import defaultdict
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_097_BUILD_ONLY"]="1"
base=runpy.run_path(
    str(ROOT.parent/"realistic_hero_097"/"assemble_realistic_hero_097.py"),
    run_name="adult_097_continuous_baseline")
os.environ.pop("NECROMANCER_097_BUILD_ONLY",None)

body=base["body"]
eyes=base["eyes"]
original=base["old_pants"]
assert len(eyes)==2
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
digest=base["previous"]["geometry_digest"]
body_before=digest(body)
eyes_before=[digest(o) for o in eyes]
orig_verts=len(original.data.vertices)
orig_faces=len(original.data.polygons)

def bell(z,c,width):
    return math.exp(-((z-c)/width)**2)
def smooth(lo,hi,z):
    t=max(0,min(1,(z-lo)/(hi-lo)))
    return t*t*(3-2*t)
def make_mat(name,color,rough=.87):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m

# Clone the ORIGINAL fully joined cloth *mesh topology* rather than adding
# unconnected new leg geometry. The copy has an independent mesh datablock.
trousers=original.copy()
trousers.data=original.data.copy()
trousers.name="098 | continuous woven tailored trousers"
bpy.context.scene.collection.objects.link(trousers)
trousers.hide_render=False
trousers.hide_set(False)
original.hide_render=True
original.hide_set(True)
original.name="097 | older continuous-cloth comparison (hidden)"

# This is one connected quad-shell. Fail instead of creating the same old
# shorts-over-leggings visual regression with disconnected objects.
adjacent=defaultdict(set)
used_vertices=set()
for f in trousers.data.polygons:
    ids=list(f.vertices)
    used_vertices.update(ids)
    for i,j in zip(ids,ids[1:]+ids[:1]):
        adjacent[i].add(j)
        adjacent[j].add(i)
components=0
unvisited=set(used_vertices)
component_sizes=[]
while unvisited:
    components+=1
    first=next(iter(unvisited))
    unvisited.remove(first)
    stack=[first]
    count=0
    while stack:
        i=stack.pop()
        count+=1
        for j in adjacent[i]:
            if j in unvisited:
                unvisited.remove(j)
                stack.append(j)
    component_sizes.append(count)
if components!=1:
    raise RuntimeError("Pants baseline is not a continuous connected cloth surface: %s" % component_sizes)
if any(len(f.vertices)!=4 for f in trousers.data.polygons):
    raise RuntimeError("Expected a CC0-derived garment of editable QUADS")

# Retain original coordinate array to enable a genuine Before/After shape key.
# This new mesh is independently editable, including when the old body is
# hidden from the Blender viewport. No changes to anatomical coordinates.
original_points=[v.co.copy() for v in trousers.data.vertices]
trousers.shape_key_add(name="098 | Reference continuous source",from_mix=False)
tailor_key=trousers.shape_key_add(name="098 | Soft cloth tailored",from_mix=False)
inv=trousers.matrix_world.inverted_safe()
worlds=[trousers.matrix_world@p for p in original_points]
p_vertices=len(worlds)

# Morph conservatively: flatten anatomical pelvis relief through cloth
# surface, add low-amplitude directional fabric folds and taper at mid-calf.
# Never introduce upper thigh spikes or shorts-like separate bands.
affected=0
for i,v in enumerate(tailor_key.data):
    p=worlds[i].copy()
    x,y,z=p.x,p.y,p.z
    if .76<z<1.05:
        front=smooth(.012,.085,-y)
        central=bell(abs(x),.045,.075)
        p.y+=.0095*front*central*bell(z,.855,.12)
        # Reduced front pelvic geometry tracing, gradual fade into waistband.
        p.y+=.003*front*central*bell(z,.960,.045)
    if .22<z<.75 and abs(x)>.045:
        side=1 if x>0 else -1
        shift=.0038*bell(z,.43,.25)*math.sin(4.2*z+abs(x)*6.2)
        p.x+=side*shift
        p.y+=.0020*bell(z,.52,.23)*math.sin(10*z+abs(x)*5)
    v.co=inv@p
    if (v.co-original_points[i]).length>1e-7:
        affected+=1
tailor_key.value=1
trousers.data.update()
if affected<400:
    raise RuntimeError("Tailoring pass failed to change enough cloth coordinates: "+str(affected))

# Render geometric changes as a shape key (also editable in .blend), and
# leave source topology present as the reference key.
# Do NOT run a remesh or triangulate anatomical body/garment.
if len(trousers.data.polygons)!=orig_faces or len(trousers.data.vertices)!=orig_verts:
    raise RuntimeError("Continuous garment lost source quad topology")

# Cloth UV space is created on the NEW independent garment; it is not
# projected back onto or written into the CC0 body. Each side is normalized
# cylindrical cloth UV, with a separate atlas zone for waist and crotch.
uv=trousers.data.uv_layers.get("098 | independent garment textile UV")
if uv is None:
    uv=trousers.data.uv_layers.new(name="098 | independent garment textile UV")
for face in trousers.data.polygons:
    ids=list(face.vertices)
    ps=[worlds[i] for i in ids]
    centroid=sum(ps,Vector())/len(ps)
    side=1 if centroid.x>=0 else -1
    circum=[]
    for p in ps:
        cx=side*(.136+.017*smooth(.67,.96,p.z))
        u=(math.atan2(p.y,(p.x-cx)) + math.pi)/(2*math.pi)
        circum.append(u)
    if max(circum)-min(circum)>.5:
        circum=[u+1 if u<.5 else u for u in circum]
    for idx,loop_index in enumerate(face.loop_indices):
        p=ps[idx]
        # mirrored sides are placed in separate nonoverlapping U halves
        u=(circum[idx]%1)*.46+(.51 if side>0 else .02)
        v=max(0,min(1,p.z/1.10))
        uv.data[loop_index].uv=(u,v)

textile=make_mat("098 | violet-black woven linen charcoal",(.060,.054,.069),.91)
texnodes=textile.node_tree.nodes
texlinks=textile.node_tree.links
tex=texnodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value=185.0
tex.inputs["Detail"].default_value=2.1
tex.inputs["Roughness"].default_value=.61
bump=texnodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.075
bump.inputs["Distance"].default_value=.0009
texlinks.new(tex.outputs["Fac"],bump.inputs["Height"])
texlinks.new(bump.outputs["Normal"],
              texnodes.get("Principled BSDF").inputs["Normal"])
trousers.data.materials.clear()
trousers.data.materials.append(textile)

stitchmat=make_mat("098 | charcoal thread seam highlight",(.155,.131,.145),.82)
# Two subtle outer seam lines derived from actual *cloth vertices* at each
# z station, rather than arbitrary circles that can float off the garment.
def create_curve(name,points):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=.00078
    curve.bevel_resolution=2
    sp=curve.splines.new("POLY")
    sp.points.add(len(points)-1)
    for v,p in zip(sp.points,points):
        v.co=(p.x,p.y,p.z,1)
    curve.materials.append(stitchmat)
    ob=bpy.data.objects.new(name,curve)
    bpy.context.scene.collection.objects.link(ob)
    return ob
seams=[]
seam_lengths=[]
for sign,label in ((-1,"left"),(1,"right")):
    points=[]
    for k in range(46):
        z=.255+(.982-.255)*k/45
        # Search a narrow band of actual source garment verts. Since source
        # body samples are relatively sparse, nearby station bins overlap.
        candidates=[(i,p) for i,p in enumerate(worlds) if sign*p.x>.035
                    and abs(p.z-z)<.053]
        if len(candidates)<8:
            raise RuntimeError("Cloth seam lacks actual source verts at z %.3f"%z)
        # Outer seam tracks the farthest side of a physically existing cloth
        # surface, with mild z-average to avoid obvious jagged stitches.
        idx,p=max(candidates,key=lambda iv:sign*iv[1].x)
        point=trousers.matrix_world@tailor_key.data[idx].co
        point.x+=sign*.0018
        points.append(point)
    # Smooth only small local fluctuations; avoid straight rulers.
    filtered=[]
    for i,p in enumerate(points):
        near=points[max(0,i-2):min(len(points),i+3)]
        filtered.append(Vector((sum(q.x for q in near)/len(near),
                                sum(q.y for q in near)/len(near),p.z)))
    seams.append(create_curve("098 | "+label+" dark textile vertical seam",filtered))
    seam_lengths.append(sum((a-b).length for a,b in zip(filtered[1:],filtered[:-1])))

# Keep the bootless feet & short-ash coiffure, but subtly reduce the
# high-contrast extra layer hair sheen without altering fibre geometry.
for hair in base["hair_layers"]:
    if hair.type!="CURVE":continue
    hair.data.bevel_depth*=.92
    for mat in hair.data.materials:
        if mat and mat.use_nodes:
            bs=mat.node_tree.nodes.get("Principled BSDF")
            bs.inputs["Roughness"].default_value=.93

# Existing 0.9.7 duplicate loft geometry and its accessory bridge remain
# hidden and are EXCLUDED from render and exported FBX via selection.
hidden_loft=base["experimental_components"]
assert len(hidden_loft)>=8
assert all(o.hide_render for o in hidden_loft)
# Old .096 cuff curves are from a different shape shell and remain excluded.
assert all(o.hide_render for o in base["previous"]["stitch_objects"])

group=bpy.data.collections.new("098 | one-piece textile garment and editable seams")
bpy.context.scene.collection.children.link(group)
for ob in [trousers,*seams]:
    group.objects.link(ob)
    for old in list(ob.users_collection):
        if old!=group:old.objects.unlink(ob)

body_after=digest(body)
eyes_after=[digest(o) for o in eyes]
assert body_after==body_before
assert eyes_after==eyes_before

metadata={
 "stage":"0.9.8 independent one-piece source-derived cloth quad mesh, no disconnected loft tubes",
 "source":base["previous"]["stage"]["ref"]["SOURCE"],
 "license":"CC0-1.0","bundle_version":"1.4.1",
 "base_collection":"Body Male - Realistic",
 "body_vertices":len(body.data.vertices),
 "body_faces":len(body.data.polygons),
 "body_coordinate_sha256_before":body_before,
 "body_coordinate_sha256_after":body_after,
 "source_eye_hashes_unchanged":eyes_after==eyes_before,
 "garment_quad_faces":len(trousers.data.polygons),
 "garment_vertices":len(trousers.data.vertices),
 "garment_connected_components":components,
 "garment_component_vertex_counts":component_sizes,
 "garment_shape_key_names":[k.name for k in trousers.data.shape_keys.key_blocks],
 "garment_vertices_modified":affected,
 "garment_uv_layers":[l.name for l in trousers.data.uv_layers],
 "separate_seam_curves":len(seams),
 "seam_lengths_m":[round(v,3) for v in seam_lengths],
 "hidden_rejected_experimental_components":len(hidden_loft),
 "base_swept_fiber_count":base["hair_count"],
 "original_short_fibers":base["previous"]["all_fibers"],
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"Single connected editable cloth is re-sculpted from original source quad topology, not independently pattern-cut and sim-sewn. Fabric still requires professional clothing sculpt, UV production, rig and visual reference."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
print("CONTINUOUS_TROUSERS_V098",json.dumps(metadata),flush=True)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=25
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format="PNG"
world=bpy.data.worlds.new("098 | studio charcoal blue soft light")
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.15,.15,.175,1)
bg.inputs["Strength"].default_value=.65
scene.world=world
for name,pos,power,size in (
 ("098 | neutral key",(2.2,-3.5,4.2),640,4.0),
 ("098 | soft fill",(-2.8,-1.3,2.6),270,3.7),
 ("098 | reverse rim",(-1.1,2.7,3.4),430,3.3)
):
    l=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,l)
    scene.collection.objects.link(ob)
    ob.location=pos
    l.energy=power
    l.shape="DISK"
    l.size=size
camera_data=bpy.data.cameras.new("098 | real orthographic inspection")
camera=bpy.data.objects.new("098 | real orthographic inspection",camera_data)
scene.collection.objects.link(camera)
camera_data.type="ORTHO"
scene.camera=camera
# Original curves retained in Blender; conversion ONLY after save for FBX.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_098.blend"))
for obj in list(scene.objects):
    if obj.type!="CURVE" or obj.hide_render:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for obj in list(scene.objects):
    if obj.type=="MESH" and not obj.hide_render and not obj.name.startswith("095 | stylized"):
        obj.hide_set(False)
        obj.select_set(True)
assert len(bpy.context.selected_objects)>18
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"necromancer_realistic_098.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
def render(name,pos,target,scale,reso=(640,840)):
    scene.render.resolution_x,scene.render.resolution_y=reso
    camera_data.ortho_scale=scale
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_098",name,flush=True)
for name,pos in (
 ("front",(0,-4.6,1.24)),
 ("side",(4.6,0,1.25)),
 ("back",(0,4.6,1.25)),
 ("threequarter",(3,-4,1.3))
):render(name,pos,(0,0,1),2.27)
render("face_threequarter",(2,-2.8,1.82),(0,0,1.75),.52,(760,760))
render("trousers_front",(0,-3,.70),(0,0,.66),1.16,(760,760))
render("trousers_side",(2.4,-.7,.7),(0,0,.64),1.16,(760,760))
render("hair_back",(0,2.5,1.84),(0,0,1.84),.53,(760,760))
print("SUCCESS_098",json.dumps(metadata),flush=True)
