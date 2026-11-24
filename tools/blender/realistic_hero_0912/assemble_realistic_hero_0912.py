"""Necromancer Overworld v0.9.12 — independently patterned smooth leather bracers.

Reuse validated 0.9.11 CC0 realistic adult model. The old body-derived
guards are kept as hidden editing references; instead, model fully independent
open-ended smooth leather tubes from stable arm section estimates, with
controlled flat cuffs, quad topology, UVs, sober material zoning and subtle
sewing on physical rings. The adult body and its original eyes are unchanged.
A conservative extra drape shape key modifies TROUSER CLOTH ONLY.
No animation, Unity scene integration, or rigging.
"""
import bpy
import os
import runpy
import math
import json
import statistics
from pathlib import Path
from mathutils import Vector
from collections import defaultdict

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_0911_BUILD_ONLY"]="1"
previous=runpy.run_path(
    str(ROOT.parent/"realistic_hero_0911"/"assemble_realistic_hero_0911.py"),
    run_name="preserved_cc0_realistic_adult_0911")
os.environ.pop("NECROMANCER_0911_BUILD_ONLY",None)
body=previous["body"]
eyes=previous["eyes"]
guards=previous["guards"]
trousers=previous["trousers"]
digest=previous["digest"]
body_hash=digest(body)
eye_hashes=[digest(o) for o in eyes]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2 and len(guards)==2

def smooth(lo,hi,x):
    t=max(0.0,min(1.0,(x-lo)/(hi-lo)))
    return t*t*(3-2*t)
def gauss(x,c,w):
    return math.exp(-((x-c)/w)**2)
def pct(sorted_nums,q):
    if not sorted_nums:raise RuntimeError("No cross section points")
    at=(len(sorted_nums)-1)*q
    a=int(at)
    b=min(a+1,len(sorted_nums)-1)
    return sorted_nums[a]*(1-(at-a))+sorted_nums[b]*(at-a)
def make_material(name,color,rough=.89):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    mat.diffuse_color=(*color,1)
    bs=mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return mat

leather=make_material("0912 | charcoal smoked leather",(.093,.078,.087),.89)
trim=make_material("0912 | darker leather cuff bindings",(.066,.058,.068),.92)
spine=make_material("0912 | quiet back-stitched seam",(.071,.063,.069),.94)
stitches_mat=make_material("0912 | muted ash thread",(.17,.151,.142),.92)
source_collection=bpy.data.collections.new("0912 | original body-based guard shells ARCHIVED")
bpy.context.scene.collection.children.link(source_collection)
visible_collection=bpy.data.collections.new("0912 | independent 2-piece patterned forearm leather")
bpy.context.scene.collection.children.link(visible_collection)

# Every original shell stays in Blender, but is prevented from rendering and
# FBX export. This deliberately avoids the sharp forearm contours observed
# in the 0.9.11 render inspections.
for guard in guards:
    guard.hide_render=True
    guard.hide_set(True)
    source_collection.objects.link(guard)
    for old in list(guard.users_collection):
        if old!=source_collection:
            old.objects.unlink(guard)

# A ring-based leather pattern with open, smoothly contoured cuffs.
# Radii and longitudinal centerline are measured from the actual original
# forearm leather source. No generalized primitive capsule or arm sculpt.
RADIAL=32
RINGS=22
new_guards=[]
section_stats={}
rim_curves=[]
max_reconstruction_gap=0.0
for guard in guards:
    raw=[guard.matrix_world@v.co for v in guard.data.vertices]
    zlow,zup=min(p.z for p in raw),max(p.z for p in raw)
    side="left" if statistics.mean(p.x for p in raw)<0 else "right"
    if not .14<zup-zlow<.34:
        raise RuntimeError("Unusual real forearm guard source length "+str((side,zlow,zup)))

    # Independent smooth top and bottom. Keep 1.5 cm inside jagged original
    # boundary to avoid protruding spurs at the wrist/upper arm.
    lo=zlow+.015
    hi=zup-.014
    cuts=[]
    for j in range(RINGS):
        z=lo+(hi-lo)*j/(RINGS-1)
        # Select a real vertical slice, widening only for sparse sections.
        near=[p for p in raw if abs(p.z-z)<.018]
        if len(near)<12:near=[p for p in raw if abs(p.z-z)<.038]
        if len(near)<12:
            raise RuntimeError("Missing source wrist cross section "+side+" z="+str(z))
        xs=sorted(p.x for p in near)
        ys=sorted(p.y for p in near)
        # Quantiles reject stray vertices at shoulders and wrists; the
        # center follows natural arm tilt from inner elbow to wrist.
        lowx,highx=pct(xs,.035),pct(xs,.965)
        lowy,highy=pct(ys,.035),pct(ys,.965)
        cx=(lowx+highx)*.5
        cy=(lowy+highy)*.5
        rx=(highx-lowx)*.5+.006
        ry=(highy-lowy)*.5+.006
        cuts.append((z,cx,cy,rx,ry))

    # Smooth the 3D center and radii across the original mesh loop strata.
    # Open hems lie on real stable section contours, not jagged source edges.
    sections=[]
    for j,row in enumerate(cuts):
        local=[]
        for k in range(max(0,j-3),min(RINGS,j+4)):
            w=math.exp(-((j-k)/1.7)**2)
            local.append((w,cuts[k]))
        den=sum(w for w,r in local)
        z,cx,cy,rx,ry=(
            row[0],*[sum(w*r[col] for w,r in local)/den for col in (1,2,3,4)]
        )
        rx=max(.025,min(.09,rx))
        ry=max(.025,min(.09,ry))
        # Subtle taper near both cuffs, without hard flat bands or spikes.
        edge=min(j,RINGS-1-j)
        taper=.96+.04*smooth(0,3,edge)
        rx*=taper
        ry*=taper
        sections.append((z,cx,cy,rx,ry))
    section_stats[side]={
        "source_vertices":len(raw),
        "source_z_min_m":round(zlow,5),"source_z_max_m":round(zup,5),
        "new_z_min_m":round(sections[0][0],5),
        "new_z_max_m":round(sections[-1][0],5),
        "mean_radius_x_m":round(statistics.mean(x[3] for x in sections),5),
        "mean_radius_y_m":round(statistics.mean(x[4] for x in sections),5)
    }

    # Each quad is between adjacent radial loops. The exact same ordered
    # vertices form both flat end contours: no disconnected rim patches.
    vertices=[]
    for j,(z,cx,cy,rx,ry) in enumerate(sections):
        for k in range(RADIAL):
            theta=2*math.pi*k/RADIAL
            # Real leather is not perfectly spherical: a small symmetric
            # longitudinal waviness makes a subtle flexible-cut silhouette.
            ripple=1+.007*math.sin(3*theta+.5*j/RINGS)
            vertices.append((cx+rx*math.cos(theta)*ripple,
                             cy+ry*math.sin(theta)*ripple,z))
    faces=[]
    categories=[]
    for j in range(RINGS-1):
        for k in range(RADIAL):
            a=j*RADIAL+k
            b=j*RADIAL+(k+1)%RADIAL
            c=(j+1)*RADIAL+(k+1)%RADIAL
            d=(j+1)*RADIAL+k
            faces.append((a,b,c,d))
            categories.append(1 if j<2 or j>=RINGS-3 else
                              (2 if k in (0,1,31) else 0))

    me=bpy.data.meshes.new("0912 | "+side+" contiguous leather pattern")
    me.from_pydata(vertices,[],faces)
    me.update()
    for material in (leather,trim,spine):
        me.materials.append(material)
    for polygon,category in zip(me.polygons,categories):
        polygon.material_index=category
        polygon.use_smooth=True

    uv=me.uv_layers.new(name="0912 | cylinder cloth pattern UV")
    for polygon in me.polygons:
        for loopidx in polygon.loop_indices:
            vid=me.loops[loopidx].vertex_index
            vz,va=divmod(vid,RADIAL)
            uv.data[loopidx].uv=(va/RADIAL,vz/(RINGS-1))

    obj=bpy.data.objects.new("0912 | "+side+" clean-cut independent leather bracer",me)
    bpy.context.scene.collection.objects.link(obj)
    visible_collection.objects.link(obj)
    for c in list(obj.users_collection):
        if c!=visible_collection:c.objects.unlink(obj)
    shell=obj.modifiers.new("0912 | real leather thickness","SOLIDIFY")
    shell.thickness=.0025
    shell.offset=0
    shell.use_rim=True
    bevel=obj.modifiers.new("0912 | softly rolled edges","BEVEL")
    bevel.width=.0015
    bevel.segments=2
    new_guards.append(obj)

    # The two circular seam lines are evaluated directly from ordered
    # ring points, exactly 2 rows inside the new CLEAN geometry.
    for idx,tag in ((2,"wrist"),(RINGS-3,"upper")):
        z,cx,cy,rx,ry=sections[idx]
        cdat=bpy.data.curves.new("0912 | "+side+" "+tag+" leather stitch","CURVE")
        cdat.dimensions="3D"
        cdat.bevel_depth=.00038
        cdat.bevel_resolution=2
        spline=cdat.splines.new("POLY")
        spline.points.add(RADIAL-1)
        for k,cp in enumerate(spline.points):
            theta=2*math.pi*k/RADIAL
            cp.co=(cx+(rx+.0010)*math.cos(theta),
                   cy+(ry+.0010)*math.sin(theta),z,1)
        spline.use_cyclic_u=True
        cdat.materials.append(stitches_mat)
        st=bpy.data.objects.new("0912 | "+side+" "+tag+" measured sewing",cdat)
        bpy.context.scene.collection.objects.link(st)
        visible_collection.objects.link(st)
        for c in list(st.users_collection):
            if c!=visible_collection:c.objects.unlink(st)
        rim_curves.append(st)

    if len(me.vertices)!=RADIAL*RINGS or len(me.polygons)!=RADIAL*(RINGS-1):
        raise RuntimeError("Independent bracer pattern is not a quad loft")
    for poly in me.polygons:
        if len(poly.vertices)!=4:raise RuntimeError("Non-quad leather face")

if len(new_guards)!=2 or len(rim_curves)!=4:
    raise RuntimeError("Missing symmetric forearm patterns")
if any(not g.hide_render for g in guards):
    raise RuntimeError("Old pointy source bracers leaked into render")

# Reversible extra cloth panel relaxation; no overlapped shorts or bodysuit.
# Work on the SAME original connected 0.9.11 trouser topology, with a fifth
# shape key. This does not claim physically sewn garment production.
for key in trousers.data.shape_keys.key_blocks:key.value=0
previous_key=trousers.data.shape_keys.key_blocks[-1]
previous_key.value=1
drape=trousers.shape_key_add(name="0912 | Relaxed wool forward drape study",from_mix=True)
for key in trousers.data.shape_keys.key_blocks:key.value=0
drape.value=1
adjacent=[set() for _ in trousers.data.vertices]
for e in trousers.data.edges:
    ia,ib=e.vertices
    adjacent[ia].add(ib)
    adjacent[ib].add(ia)
changed=set()
for _ in range(5):
    old=[v.co.copy() for v in drape.data]
    for i,q in enumerate(old):
        if len(adjacent[i])<3 or not .75<q.z<1.0:continue
        front=smooth(.035,.115,-q.y)
        upper=smooth(.77,.815,q.z)*(1-smooth(.95,1.0,q.z))
        horizontal=gauss(abs(q.x),.095,.16)
        factor=front*upper*horizontal
        if factor<.035:continue
        avg=sum(old[k].y for k in adjacent[i])/len(adjacent[i])
        drape.data[i].co.y=q.y+.17*factor*(avg-q.y)
        changed.add(i)
for i,v in enumerate(drape.data):
    q=v.co
    if .79<q.z<.95:
        front=smooth(.045,.13,-q.y)
        across=gauss(abs(q.x),.075,.10)
        amount=.0024*front*across*gauss(q.z,.86,.09)
        if amount>0.0001:
            q.y-=amount
            changed.add(i)
trousers.data.update()
assert len(trousers.data.vertices)==1122 and len(trousers.data.polygons)==1086
assert previous["p"]["prior"]["stage"]["components"]==1
assert len(changed)>=45

assert digest(body)==body_hash and [digest(e) for e in eyes]==eye_hashes

meta={
 "version":"0.9.12",
 "stage":"new self-contained forearm leather patterns and reversible frontal cloth drape",
 "source":"Blender Studio Human Base Meshes v1.4.1, Body Male - Realistic",
 "license":"CC0-1.0",
 "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
 "body_digest_before":body_hash,"body_digest_after":digest(body),
 "eye_hashes_unchanged":[digest(e) for e in eyes]==eye_hashes,
 "old_body_derived_guard_count":len(guards),
 "old_body_derived_guards_hidden":all(g.hide_render for g in guards),
 "separately_modelled_leather_guards":len(new_guards),
 "radial_vertices_per_ring":RADIAL,
 "longitudinal_rings":RINGS,
 "bracer_vertices":[len(g.data.vertices) for g in new_guards],
 "bracer_quad_faces":[len(g.data.polygons) for g in new_guards],
 "bracer_pattern_uv_layers":[len(g.data.uv_layers) for g in new_guards],
 "bracer_source_section_statistics":section_stats,
 "curved_sew_rings":len(rim_curves),
 "trouser_connected_components":previous["p"]["prior"]["stage"]["components"],
 "trouser_vertices":len(trousers.data.vertices),
 "trouser_faces":len(trousers.data.polygons),
 "trouser_shape_keys":[key.name for key in trousers.data.shape_keys.key_blocks],
 "new_cloth_vertices_modified":len(changed),
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"New bracers are procedural section-fitted leather tubes, not scanned production patterns. Body source preserved. Trouser changes remain a source-derived one-piece cloth sculpt, not pattern cut."
}
(OUT/"source_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print("VALIDATE_0912",json.dumps(meta),flush=True)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=22
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
world=bpy.data.worlds.new("0912 | neutral material presentation")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.15,.17,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.68
scene.world=world
for name,loc,power,size in (
    ("0912 key",(2.2,-3.5,4.2),640,4),
    ("0912 fill",(-2.8,-1.3,2.6),310,3.7),
    ("0912 rim",(-1.1,2.7,3.4),430,3.3)
):
    light=bpy.data.lights.new(name,"AREA")
    obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj)
    obj.location=loc
    light.energy=power
    light.shape="DISK"
    light.size=size
camdata=bpy.data.cameras.new("0912 | orthographic 3D model review")
cam=bpy.data.objects.new("0912 | orthographic 3D model review",camdata)
scene.collection.objects.link(cam)
camdata.type="ORTHO"
scene.camera=cam
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_0912.blend"))

for obj in list(scene.objects):
    if obj.type!="CURVE" or obj.hide_render:continue
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
if len(bpy.context.selected_objects)<23:
    raise RuntimeError("FBX is missing intended source anatomy and geometry")
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"necromancer_realistic_0912.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")

def render(name,where,focus,scale,res=(640,840)):
    scene.render.resolution_x,scene.render.resolution_y=res
    camdata.ortho_scale=scale
    cam.location=where
    cam.rotation_euler=(Vector(focus)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_0912",name,flush=True)
for name,loc in (
    ("front",(0,-4.6,1.24)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3,-4,1.30))
):render(name,loc,(0,0,1),2.27)
render("bracer_front",(0,-2.3,1.11),(0,0,1.09),.80,(760,760))
render("bracer_threequarter",(2,-2.5,1.10),(.45,0,1.10),.86,(760,760))
render("bracer_side",(3,-.25,1.1),(.50,0,1.1),.84,(760,760))
render("pelvis_front",(0,-2.8,1.01),(0,0,.99),.93,(760,760))
print("SUCCESS_0912",flush=True)
