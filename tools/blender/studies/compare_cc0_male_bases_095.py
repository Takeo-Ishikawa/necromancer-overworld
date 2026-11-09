"""0.9.5 independent CC0 adult-face base study (no new face sculpt).

Compare the authentic, artist-modelled Body Male - Stylized and
Body Male - Realistic objects from the SAME official Blender Studio
Human Base Meshes v1.4.1 CC0 package.

Intentionally does NOT reuse the increasingly distorted 0.9.4 face.
Does NOT create a hero replacement, rig, or modify any Unity scene.
"""
import bpy
import math
import json
from pathlib import Path
from mathutils import Matrix,Vector

BASE=Path(__file__).resolve().parent.parent / "anatomical"
BUNDLE=BASE/"_source_bundle"
OUT=Path(__file__).resolve().parent/"output"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE="https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip"
assets=list(BUNDLE.rglob("human_base_meshes_bundle.blend"))
if len(assets)!=1:
    raise RuntimeError("Expected one official Human Base Meshes .blend from ZIP, got %d"%len(assets))
asset_file=assets[0]
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.render.engine="CYCLES"
scene=bpy.context.scene
scene.cycles.samples=20
scene.cycles.device="CPU"
scene.cycles.use_denoising=True
scene.render.image_settings.file_format="PNG"
scene.render.resolution_x=640
scene.render.resolution_y=800
scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX"
scene.render.film_transparent=False

def clay(name,color):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=.76
    return mat

skin=clay("095 | equalized matte neutral adult/base complexion",(.53,.45,.43))
variants={}
for name,collection_name in (
    ("stylized","Body Male - Stylized"),
    ("realistic","Body Male - Realistic"),
):
    with bpy.data.libraries.load(str(asset_file),link=False) as (src,dst):
        if collection_name not in src.collections:
            raise RuntimeError("Official source missing "+collection_name)
        dst.collections=[collection_name]
    group=dst.collections[0]
    if group is None:
        raise RuntimeError("Blender CC0 library returned empty "+collection_name)
    group.name="095 | "+collection_name+" (CC0 imported; unmodified topology)"
    scene.collection.children.link(group)
    objects=list(group.all_objects)
    meshes=[o for o in objects if o.type=="MESH" and len(o.data.vertices)>100]
    if not meshes:
        raise RuntimeError("No genuine artist-authored mesh in "+collection_name)
    body=max(meshes,key=lambda o:len(o.data.vertices))
    # Normalize height independently, preserving source proportions and pose.
    corners=[body.matrix_world@Vector(p) for p in body.bound_box]
    bounds_min=[min(v[i] for v in corners) for i in range(3)]
    bounds_max=[max(v[i] for v in corners) for i in range(3)]
    source_height=bounds_max[2]-bounds_min[2]
    if not .15<source_height<8:
        raise RuntimeError("Invalid CC0 body height "+str(source_height))
    scale=1.90/source_height
    shift=Vector((-(bounds_min[0]+bounds_max[0])*.5,
                  -(bounds_min[1]+bounds_max[1])*.5,-bounds_min[2]))
    normalize=Matrix.Scale(scale,4)@Matrix.Translation(shift)
    object_set=set(objects)
    for o in objects:
        if o.parent not in object_set:
            o.matrix_world=normalize@o.matrix_world
        if o.type not in {"MESH"}:
            o.hide_render=True
    body.name="095 | "+name+" | official CC0 male (comparison only)"
    body.data=body.data.copy()
    body.data.materials.clear()
    body.data.materials.append(skin)
    for polygon in body.data.polygons:
        polygon.use_smooth=True
    bpy.context.view_layer.update()
    pts=[body.matrix_world@v.co for v in body.data.vertices]
    facepts=[p for p in pts if 1.64<p.z<1.86 and abs(p.x)<.35]
    if len(facepts)<200:
        raise RuntimeError("Insufficient real face verts in "+name)
    head_width=max(p.x for p in facepts)-min(p.x for p in facepts)
    eyeobjs=[o for o in objects if o.type=="MESH" and o!=body and
             ("eye" in o.name.lower() or "iris" in o.name.lower() or "sclera" in o.name.lower())]
    variants[name]={"name":name,"collection":group,"objects":objects,"body":body,
                    "source_height":source_height,"scale":scale,
                    "n_vertices":len(body.data.vertices),"n_faces":len(body.data.polygons),
                    "face_vertices":len(facepts),"head_width_m":round(head_width,4),
                    "eyes":[{"name":o.name,"vertices":len(o.data.vertices)} for o in eyeobjs]}
    print("OFFICIAL_BASE",name,"body",body.name,"verts",len(body.data.vertices),
          "faces",len(body.data.polygons),"headwidth",round(head_width,4),
          "eyes",len(eyeobjs),flush=True)

# Strong invariant: only if polygon loops AND vertex numbering match can we
# even attempt a topologically meaningful full-face morph in a future pass.
a=variants["stylized"]["body"].data
b=variants["realistic"]["body"].data
compatible=(len(a.vertices)==len(b.vertices) and len(a.polygons)==len(b.polygons))
same_loops=False
if compatible:
    same_loops=all(tuple(p.vertices)==tuple(q.vertices)
                   for p,q in zip(a.polygons,b.polygons))
compatible=bool(compatible and same_loops)
print("TOPOLOGY_IDENTICAL_LOOP_ORDER",compatible,flush=True)

def set_variant(name):
    for key,v in variants.items():
        for ob in v["objects"]:
            if ob.type=="MESH":
                ob.hide_render=(key!=name)

world=bpy.data.worlds.new("095 | neutral comparison world")
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.18,.18,.20,1)
bg.inputs["Strength"].default_value=.55
scene.world=world
for name,pos,power,size in (
    ("095 | key",(2.1,-3.2,3.8),680,3.5),
    ("095 | fill",(-2.4,-1.0,2.8),330,3.4),
    ("095 | rim",(-1.4,2.5,3.1),460,3.1),
):
    lamp=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,lamp)
    scene.collection.objects.link(ob)
    ob.location=pos
    lamp.energy=power
    lamp.shape="DISK"
    lamp.size=size

camdata=bpy.data.cameras.new("095 | standardized orthographic inspection")
cam=bpy.data.objects.new("095 | standardized orthographic inspection",camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO"

def shot(variant,name,where,target,scale,res):
    set_variant(variant)
    scene.render.resolution_x,scene.render.resolution_y=res
    camdata.ortho_scale=scale
    cam.location=where
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    filename=OUT/(variant+"_"+name+".png")
    scene.render.filepath=str(filename)
    bpy.ops.render.render(write_still=True)
    print("RENDER_CC0",variant,name,filename,flush=True)

for variant in ("stylized","realistic"):
    shot(variant,"front",(0,-4.4,1.20),(0,0,1.0),2.26,(620,840))
    shot(variant,"face_front",(0,-2.9,1.77),(0,0,1.76),.53,(760,760))
    shot(variant,"face_profile",(3.2,0,1.78),(0,0,1.75),.54,(760,760))
    shot(variant,"face_threequarter",(2.0,-2.7,1.81),(0,0,1.75),.54,(760,760))

metadata={
    "stage":"0.9.5 controlled comparison: unmodified official adult-realistic vs stylized CC0 source",
    "source":SOURCE,
    "license":"CC0-1.0",
    "bundle_version":"1.4.1",
    "topology_identical_loop_order":compatible,
    "caution":"Matching polygon counts alone never proves morph compatibility; do not transfer 0.9.4 sculpt offsets blindly.",
    "variants":{
        key:{k:v for k,v in item.items() if k in ("name","source_height","scale","n_vertices","n_faces","face_vertices","head_width_m","eyes")}
        for key,item in variants.items()
    },
    "preview_images":8,
    "unity_character_replaced":False,
    "rigged":False,
    "recommendation":"Decide only after inspecting real rendered profiles and face; current comparison is a diagnostic not an approved replacement."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
# Save both editable source collections, non-destruction, only the realistic
# variant visible by default; can toggle stylized visibility in .blend.
set_variant("realistic")
scene.render.filepath=""
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"official_CC0_male_face_comparison_095.blend"))
# Separate CC0 realistic FBX is a candidate for study, NOT a Unity replacement.
bpy.ops.object.select_all(action="DESELECT")
for o in variants["realistic"]["objects"]:
    if o.type=="MESH":
        o.hide_set(False)
        o.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"official_realistic_male_CC0_candidate_095.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
print("FINISHED_OFFICIAL_CC0_COMPARISON",json.dumps(metadata),flush=True)
