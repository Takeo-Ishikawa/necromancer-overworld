"""Necromancer Overworld 0.9.4 — facial-sculpt refinement on the CC0 hero.

Loads 0.9.3 as an editable, non-exported build stage, then changes original
artist-authored anatomy vertices, imported eye geometry, and editable brows.
There is NO replacement of the head with primitives, no remesh, no rigging,
and absolutely no change to the active Unity protagonist.
"""
import os
import runpy
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
os.environ["NECROMANCER_093_BUILD_ONLY"] = "1"
previous = runpy.run_path(str(ROOT / "sculpt_character_093.py"), run_name="stage_094")
os.environ.pop("NECROMANCER_093_BUILD_ONLY", None)

body = previous["body"]
base = previous["base"]
eyes = [ob for ob in base["selected_objects"]
        if ob.type=="MESH" and ob!=body and ".eye." in ob.name.lower()]
assert len(eyes)==2
assert len(body.data.vertices)==12502 and len(body.data.polygons)==12500
original = [v.co.copy() for v in body.data.vertices]
face_modified=0
ear_modified=0

def bell(v,c,r):
    return math.exp(-((v-c)/r)**2)
def ease(a,b,v):
    t=max(0.0,min(1.0,(v-a)/(b-a)))
    return t*t*(3-2*t)
def new_material(name,colour,rough=.75):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    mat.diffuse_color=(*colour,1)
    p=mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*colour,1)
    p.inputs["Roughness"].default_value=rough
    return mat

ash=new_material("094 | soft layered slate brow hairs",(.11,.11,.15),.90)
skin=new_material("094 | pale cool desaturated skin",(.45,.395,.405),.83)
body.data.materials.clear()
body.data.materials.append(skin)

# Pass 1: adult face architecture — restrict to face, keep 1.90m CC0 body,
# fingers, torso and back untouched. Deformations are continuous, not Boolean.
inv=body.matrix_world.inverted_safe()
for vert in body.data.vertices:
    p=body.matrix_world@vert.co
    original_p=p.copy()
    x,y,z=p
    a=abs(x)
    if 1.627<z<1.840 and a<.218:
        # Narrow the rounded cheek plane, keeping nose/lips neutral.
        cheek=bell(z,1.715,.055)*ease(.045,.112,a)
        p.x*=1.0-.205*cheek
        if y<-.030:
            p.y+=.0040*bell(z,1.713,.050)*bell(a,.097,.032)
        # Square the lower jaw more strongly, stop at central chin.
        jaw=bell(z,1.652,.028)*ease(.031,.094,a)
        p.x*=1+.032*jaw
        # Remove lateral cheek inflation inherited from the original cartoon base.
        if a>.058:
            p.x*=1-.095*bell(z,1.697,.045)*ease(.058,.126,a)
        if y<-.033:
            p.y-=.008*bell(z,1.645,.025)*bell(a,.025,.055)
        # Suppress youthful bulbous cheeks and soften protruding lips.
        if y<-.045:
            p.y+=.0042*bell(z,1.672,.026)*bell(a,0,.055)
            p.y-=.0040*bell(z,1.718,.031)*bell(a,.012,.019)
        # Stronger upper orbital ridge / more grown-up eye aperture.
        if y<-.059 and .019<a<.104:
            socket=bell(a,.054,.038)*bell(z,1.725,.044)*ease(.060,.125,-y)
            p.z=1.726+(p.z-1.726)*(1-.36*socket)
            # Eye socket sides recessed for a less wide-eyed appearance.
            p.y+=.0045*socket*bell(z,1.724,.019)
            p.y-=.0050*bell(z,1.781,.018)*bell(a,.057,.032)
        # Visibly narrower nose bridge and more refined nose root.
        if y<-.067 and .004<a<.059:
            p.x*=1-.070*bell(z,1.729,.036)*bell(a,.023,.023)
            p.x*=1-.055*bell(z,1.708,.027)*bell(a,.032,.027)
        # The original stylized ears protrude far beyond the face;
        # narrow their lateral and vertical extent, preserving ear loops.
        if a>.119 and -.064<y<.125:
            ear_fade=ease(.115,.162,a)*bell(z,1.733,.075)
            p.x-=math.copysign(.033*ear_fade,x)
            p.z=1.738+(p.z-1.738)*(1-.21*ear_fade)
            if ear_fade>.03:ear_modified+=1
        # Slightly thicker neck under a mature jaw.
    if 1.515<z<1.655 and a<.134 and y>-.035:
        p.x*=1+.08*bell(z,1.594,.068)
    if (p-original_p).length>1e-6:face_modified+=1
    vert.co=inv@p
body.data.update()
for polygon in body.data.polygons:polygon.use_smooth=True
if face_modified<350 or ear_modified<16:
    raise RuntimeError("Face/ear sculpt did not reach expected CC0 regions: %r %r"%(face_modified,ear_modified))

# Pass 2: reshape both actual imported eyeball meshes (not separately built
# eyeballs). The previous passes compressed them but they still dominate face.
eye_metrics=[]
for ob in eyes:
    inverse=ob.matrix_world.inverted_safe()
    old_world=[ob.matrix_world@v.co for v in ob.data.vertices]
    center=sum(old_world,Vector())/len(old_world)
    before_height=max(p.z for p in old_world)-min(p.z for p in old_world)
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        p.x=center.x+(p.x-center.x)*.86
        p.y=center.y+(p.y-center.y)*.83+.005
        p.z=center.z+(p.z-center.z)*.72
        vertex.co=inverse@p
    ob.data.update()
    new_world=[ob.matrix_world@v.co for v in ob.data.vertices]
    after_height=max(p.z for p in new_world)-min(p.z for p in new_world)
    eye_metrics.append({"name":ob.name,"height_before":round(before_height,5),
                        "height_after":round(after_height,5)})
    if not .70<after_height/before_height<.74:
        raise RuntimeError("Eye scaling not applied to true CC0 mesh")

# Re-anchor the previously extruded iris and pupil onto the new ocular surface.
# A world-space vertical reference avoids a detached / floating appearance.
iris_count=0
for ob in bpy.context.scene.objects:
    if ob.type!="MESH" or not ("muted iris" in ob.name or "deep pupil" in ob.name):
        continue
    inverse=ob.matrix_world.inverted_safe()
    old_world=[ob.matrix_world@v.co for v in ob.data.vertices]
    center=sum(old_world,Vector())/len(old_world)
    hit=previous["stage"]["front_hit"](center.x,center.z)
    if hit is None:
        raise RuntimeError("Cannot anchor 0.9.4 ocular detail: "+ob.name)
    pupils="deep pupil" in ob.name
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co
        p.x=center.x+(p.x-center.x)*.85
        p.z=center.z+(p.z-center.z)*.79
        p.y=hit.y-(.0050 if pupils else .0036)
        v.co=inverse@p
    ob.data.update()
    iris_count+=1
if iris_count!=4:raise RuntimeError("0.9.4 expected four iris/pupil objects")

# Pass 3: eyebrows. 0.9.3 brows were uniform pencil-like strokes.
# Replace just the two old brow curves with broad, tapered sculpt-following
# surfaces. Each side is a mesh derived by raycasting against the real head.
old_brows=[ob for ob in list(bpy.context.scene.objects)
           if "093 |" in ob.name and "ash eyebrow" in ob.name]
if len(old_brows)!=2:raise RuntimeError("Expected the original two eyebrows")
for ob in old_brows:bpy.data.objects.remove(ob,do_unlink=True)

def face_surface(x,z):
    inverse=body.matrix_world.inverted_safe()
    start=inverse@Vector((x,-.62,z))
    direction=(inverse.to_3x3()@Vector((0,1,0))).normalized()
    ok,local,norm,index=body.ray_cast(start,direction)
    return body.matrix_world@local if ok else None

brow_objects=[]
for sign,label in ((-1,"L"),(1,"R")):
    vertices=[]
    faces=[]
    n=24
    for i in range(n):
        t=i/(n-1)
        x=sign*(.026+.062*t)
        z=1.777+.0045*math.sin(math.pi*t)-.0065*t
        half_width=.0005+.00175*(math.sin(math.pi*t)**.8)
        for dz in (-half_width,half_width):
            surface=face_surface(x,z+dz)
            if surface is None:raise RuntimeError("Eyebrow does not project on face")
            vertices.append((x,surface.y-.0033,z+dz))
    for i in range(n-1):
        faces.append((i*2,i*2+1,i*2+3,i*2+2))
    mesh=bpy.data.meshes.new("094 | "+label+" tapered eyebrow quad sheet")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    mesh.materials.append(ash)
    ob=bpy.data.objects.new("094 | "+label+" shaded tapered eyebrow",mesh)
    bpy.context.scene.collection.objects.link(ob)
    for polygon in mesh.polygons:polygon.use_smooth=True
    brow_objects.append(ob)

# The overlapping straight 0.9.3 upper eyelid line is retained: it remains an
# editable line; newly projected brow stays separately editable.
face_collection=bpy.data.collections.get("093 | face accents")
if face_collection:
    for ob in brow_objects:
        face_collection.objects.link(ob)
        if bpy.context.scene.collection in ob.users_collection:
            bpy.context.scene.collection.objects.unlink(ob)

# A small measured change to the neutral color and hair reflectance improves
# visibility in a deterministic studio without hiding underlying geometry.
hair=previous["hair"]
for material in hair.data.materials:
    if material is None or not material.use_nodes:continue
    bsdf=material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value=.81

meta={
 "stage":"0.9.4 focused adult facial sculpt, using 0.9.3 CC0 character",
 "source":base["SOURCE"],"license":"CC0-1.0","bundle_version":"1.4.1",
 "asset_file":previous["source_entry"]["file"],
 "asset_datablock":previous["stage"]["source_name"],
 "blender_version":bpy.app.version_string,
 "base_vertices":12502,"base_faces":12500,
 "body_vertices_after_sculpt":len(body.data.vertices),
 "body_faces_after_sculpt":len(body.data.polygons),
 "facial_vertices_modified":face_modified,"ear_vertices_modified":ear_modified,
 "original_cc0_eye_meshes":eye_metrics,
 "iris_pupil_meshes":iris_count,"shaped_brow_meshes":len(brow_objects),
 "hair_strand_count":485,"trouser_quads":len(previous["trousers"].data.polygons),
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"Visual identity is not approved. Reference turnarounds are not versioned in the repository. This is vertex-level procedural sculpting, not a human sculpt artist's final retopology."
}
(OUT/"source_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
(OUT/"asset_catalog.json").write_text(json.dumps(base["entries"],indent=2),encoding="utf-8")
bpy.context.view_layer.update()

# Geometry inspection lighting: slightly stronger key / weaker fill to reveal
# brows, cheek planes and jaw angle. Identical true orthographic view directions.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=26
scene.cycles.use_denoising=True
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=100
scene.render.film_transparent=False
world=bpy.data.worlds.new("094 | graphite neutral sculpt studio")
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.16,.16,.19,1)
bg.inputs["Strength"].default_value=.65
scene.world=world
for name,where,power,size in (
    ("094 | key",(2.3,-3.7,4.3),560,3.4),
    ("094 | fill",(-2.8,-1.0,2.7),180,4.0),
    ("094 | rim",(-1.0,2.2,3.0),450,3.1),
):
    l=bpy.data.lights.new(name,"AREA")
    o=bpy.data.objects.new(name,l)
    scene.collection.objects.link(o)
    o.location=where
    l.energy=power
    l.shape="DISK"
    l.size=size

camdata=bpy.data.cameras.new("094 | orthographic anatomical inspection")
camera=bpy.data.objects.new("094 | orthographic anatomical inspection",camdata)
scene.collection.objects.link(camera)
scene.camera=camera
camdata.type="ORTHO"
camdata.ortho_scale=2.23

# Save EDITABLE file before converting curve strokes to meshes for FBX.
bpy.ops.object.select_all(action="DESELECT")
blend=OUT/"necromancer_character_094.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
for cr in list(bpy.context.scene.objects):
    if cr.type!="CURVE" or cr.hide_render:continue
    bpy.ops.object.select_all(action="DESELECT")
    cr.hide_set(False)
    cr.select_set(True)
    bpy.context.view_layer.objects.active=cr
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and not ob.hide_render and not ob.name.startswith("SOURCE"):
        ob.hide_set(False)
        ob.select_set(True)
assert len(bpy.context.selected_objects)>=12
fbx=OUT/"necromancer_character_094.fbx"
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,
                         object_types={"MESH"},apply_unit_scale=True,
                         axis_forward="-Z",axis_up="Y")

def shot(name,where,target,scale,res=(620,840)):
    scene.render.resolution_x=res[0]
    scene.render.resolution_y=res[1]
    camdata.ortho_scale=scale
    camera.location=where
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("character_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_094",name,scene.render.filepath,flush=True)
for name,where in (
 ("front",(0,-4.6,1.25)),
 ("side",(4.6,0,1.25)),
 ("back",(0,4.6,1.25)),
 ("threequarter",(3,-4,1.30))
):
    shot(name,where,(0,0,1.0),2.23)
shot("face_front",(0,-2.6,1.77),(0,0,1.75),.49,(760,760))
shot("face_threequarter",(1.5,-2.3,1.8),(0,0,1.75),.50,(760,760))
shot("face_profile",(3.0,0,1.78),(0,0,1.75),.49,(760,760))
shot("eye_detail",(0,-2.2,1.73),(0,0,1.735),.245,(800,600))
shot("trousers_detail",(1.3,-3.0,.73),(0,0,.60),.99,(760,760))
print("SUCCESS_094",json.dumps(meta),flush=True)
