"""Necromancer 0.9.1 — official CC0 human base mesh, first anatomy sculpture.

Loads a real Blender Studio Human Base Meshes 1.4.1 *stylized male* from the
official downloaded asset bundle. Creates the first non-destructive,
anatomically guided digital sculpt and orthographic review images.

Unlike the old primitive-based 0.8.x generator, this script preserves the
imported, artist-authored quad topology and only displaces existing vertices.
No fake generated anatomical skeleton or voxel body is substituted.

This is a sculpting BASE and assessment, not a finished dressed or rigged
protagonist. Blender 4.5 LTS and the official CC0 ZIP are obtained in CI.
"""
import bpy
import json
import math
import os
import re
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent
BUNDLE=ROOT/"_source_bundle"
OUT=ROOT/"output"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE="https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip"
LICENSE="CC0-1.0"

# Introspect the true bundle; never assume a .blend name or silently fall back
# to the old geometric blockout.
entries=[]
for path in sorted(BUNDLE.rglob("*.blend")):
    try:
        with bpy.data.libraries.load(str(path), link=False) as (src, dst):
            collections=list(src.collections)
            objects=list(src.objects)
    except Exception as exc:
        entries.append({"file":str(path.relative_to(BUNDLE)), "error":str(exc)})
        continue
    entries.append({
        "file":str(path.relative_to(BUNDLE)),
        "collections":collections,
        "objects":objects,
    })

def candidate_score(entry, kind, name):
    f=entry["file"].lower()
    n=name.lower()
    if "male" not in f+" "+n or "female" in n:
        return -10000
    score=0
    if "male" in n and "body" in n:score+=120
    if "stylized" in n:score+=95
    if "stylized" in f:score+=40
    if "realistic" in n:score+=10
    if "primitive" in n or "primitve" in n:score-=180
    if "primitive" in f or "primitve" in f:score-=120
    if kind=="collection":score+=25
    if "body" in f:score+=20
    return score

candidates=[]
for entry in entries:
    if "error" in entry:continue
    for c in entry["collections"]:
        score=candidate_score(entry,"collection",c)
        if score>0:
            candidates.append((score,entry,"collection",c))
    for c in entry["objects"]:
        score=candidate_score(entry,"object",c)
        if score>0:
            candidates.append((score,entry,"object",c))
candidates.sort(key=lambda v:v[0],reverse=True)
if not candidates:
    with open(OUT/"asset_catalog.json","w") as f:
        json.dump(entries,f,indent=2)
    raise RuntimeError("Official package downloaded but no matching male body asset found")
score,entry,kind,asset_name=candidates[0]
asset_path=BUNDLE/entry["file"]
print("SELECTED OFFICIAL HUMAN BASE:", entry["file"],kind,asset_name,"score",score,flush=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
selected_objects=[]
if kind=="collection":
    with bpy.data.libraries.load(str(asset_path), link=False) as (src,dst):
        dst.collections=[asset_name]
    group=dst.collections[0]
    if group is None:raise RuntimeError("Collection append returned None")
    bpy.context.scene.collection.children.link(group)
    selected_objects=list(group.all_objects)
else:
    with bpy.data.libraries.load(str(asset_path), link=False) as (src,dst):
        dst.objects=[asset_name]
    ob=dst.objects[0]
    if ob is None:raise RuntimeError("Object append returned None")
    bpy.context.scene.collection.objects.link(ob)
    selected_objects=[ob]

meshes=[ob for ob in selected_objects if ob.type=="MESH" and len(ob.data.vertices)>30]
if not meshes:
    raise RuntimeError("Official male asset collection contains no mesh objects")
body=max(meshes,key=lambda obj:len(obj.data.vertices))
print("BODY",body.name,"verts",len(body.data.vertices),"faces",len(body.data.polygons),
      "source objects",len(selected_objects),flush=True)
# The body must be a genuine detailed mesh; reject primitives / toy blocks.
if len(body.data.vertices)<1000:
    raise RuntimeError("Selected body has too few vertices for anatomical sculpt")

# Determine source bounds in world space and normalize height to 1.9 m;
# preserve the asset's pose, its quads and any subsidiary mesh objects.
world_corners=[body.matrix_world @ Vector(c) for c in body.bound_box]
minimum=[min(v[i] for v in world_corners) for i in range(3)]
maximum=[max(v[i] for v in world_corners) for i in range(3)]
height=maximum[2]-minimum[2]
if not 0.1<height<10:
    raise RuntimeError("Unreasonable bounding box of official body: %r"%height)
scale=1.90/height
centerx=(minimum[0]+maximum[0])*.5
centery=(minimum[1]+maximum[1])*.5
xf=Matrix.Scale(scale,4) @ Matrix.Translation(Vector((-centerx,-centery,-minimum[2])))
selected_set=set(selected_objects)
for ob in selected_objects:
    if ob.parent not in selected_set:
        ob.matrix_world=xf@ob.matrix_world
# Important: original imported body remains a true contiguous asset mesh.
original=body.copy()
original.data=body.data.copy()
original.name="SOURCE | Blender Studio original male anatomy CC0"
hidden=bpy.data.collections.new("Editable unmodified CC0 source (hidden)")
bpy.context.scene.collection.children.link(hidden)
hidden.objects.link(original)
original.hide_render=True
original.hide_set(True)

# Body mesh is deformed only by small anatomical adjustments on its vertices,
# preserving its original artist topology. These are preliminary sculpt passes.
# Coordinates measured in normalized world space (1.90m character height).
body.data=body.data.copy()
inverse=body.matrix_world.inverted_safe()
for vert in body.data.vertices:
    p=body.matrix_world @ vert.co
    x,y,z=p
    # Torso relief is low amplitude and fades smoothly to avoid "muscle balls".
    front=max(0.0,min(1.0,(-y-.015)/.11))
    if 1.12<z<1.59 and abs(x)<.28:
        pec=math.exp(-((abs(x)-.148)/.090)**2-((z-1.440)/.105)**2)
        linea=math.exp(-(x/.018)**2-((z-1.34)/.17)**2)
        oblique=math.exp(-((abs(x)-.19)/.051)**2-((z-1.28)/.090)**2)
        delta=.0090*pec-.0025*linea+.003*oblique
        for row_z in (1.28,1.215,1.148):
            belly=math.exp(-((abs(x)-.067)/.045)**2-((z-row_z)/.034)**2)
            delta+=.0040*belly
        p.y-=front*delta
        vert.co=inverse@p
body.data.update()
body.name="Necromancer | CC0 anatomical sculpt base v0.9.1"

# Neutral matte clay skin for anatomy review (not final textures).
skin=bpy.data.materials.new("Necromancer | anatomical clay")
skin.diffuse_color=(.62,.46,.42,1)
skin.use_nodes=True
pbr=skin.node_tree.nodes.get("Principled BSDF")
pbr.inputs["Base Color"].default_value=(.62,.46,.42,1)
pbr.inputs["Roughness"].default_value=.74
body.data.materials.clear()
body.data.materials.append(skin)
# Subdivision is non-destructive so the official quad basemesh stays editable.
if len(body.data.polygons)<60000:
    sub=body.modifiers.new("Preview sculpt subdivisions (non-destructive)","SUBSURF")
    sub.subdivision_type="CATMULL_CLARK"
    sub.levels=1
    sub.render_levels=1
# Remove extra lights, cameras or non-mesh references imported with the asset.
for ob in selected_objects:
    if ob.type not in {"MESH"}:
        ob.hide_render=True

# Save model and export real topology in FBX.
metadata={
    "source":SOURCE,
    "license":LICENSE,
    "bundle_version":"1.4.1",
    "blender_version":bpy.app.version_string,
    "asset_file":entry["file"],
    "asset_datablock":asset_name,
    "asset_kind":kind,
    "anatomical_object":body.name,
    "vertices":len(body.data.vertices),
    "faces":len(body.data.polygons),
    "height_m":1.90,
    "topology_source":"Blender Studio Human Base Meshes",
    "stage":"0.9.1 source import + nondestructive anatomy sculpt, no rig",
    "known_limitations":"character not yet dressed; silhouette, hair and face pending",
}
with open(OUT/"source_metadata.json","w") as f:json.dump(metadata,f,indent=2)
with open(OUT/"asset_catalog.json","w") as f:json.dump(entries,f,indent=2)
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_anatomy_091.blend"))
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and not ob.hide_render and len(ob.data.vertices)>25:
        ob.hide_set(False)
        ob.select_set(True)
if not bpy.context.selected_objects:raise RuntimeError("No visible anatomical meshes for FBX export")
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"necromancer_anatomy_091.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y"
)

# Compact Cycles studio setup — no camera tricks, front/side/back genuine views.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=12
scene.cycles.use_denoising=False
for layer in scene.view_layers:
    if hasattr(layer,"cycles"):
        layer.cycles.use_denoising=False
scene.render.resolution_x=620
scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
world=bpy.data.worlds.new("Soft charcoal studio")
world.use_nodes=True
background=world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.17,.17,.19,1)
background.inputs["Strength"].default_value=.75
scene.world=world
for name,loc,power,size in (
    ("Softbox key",(2,-3,4.2),780,4.4),
    ("Softbox fill",(-3,-1,3.0),320,3.2),
    ("Rim",(-1,2.4,3.3),480,3.0),
):
    lamp=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,lamp)
    scene.collection.objects.link(ob)
    ob.location=loc
    lamp.energy=power
    lamp.shape="DISK"
    lamp.size=size
camdata=bpy.data.cameras.new("Anatomy inspection orthographic")
cam=bpy.data.objects.new("Anatomy inspection orthographic",camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO"
camdata.ortho_scale=2.27
for name,location in (
    ("front",(0,-4.5,1.20)),
    ("side",(4.5,0,1.20)),
    ("back",(0,4.5,1.20)),
    ("threequarter",(3.0,-4.0,1.30)),
):
    cam.location=location
    direction=Vector((0,0,1.0))-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("anatomy_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER",scene.render.filepath,flush=True)
print("COMPLETED CC0 ANATOMICAL BASE import/sculpt/render: ",json.dumps(metadata),flush=True)
