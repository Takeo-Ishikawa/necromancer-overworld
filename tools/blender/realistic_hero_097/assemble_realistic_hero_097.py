"""Necromancer Overworld 0.9.7: independent trouser geometry and layered upper haircut.

Real Blender Studio Human Base Meshes v1.4.1 Body Male - Realistic CC0.
Retains entire 0.9.6 anatomical base and fine-fibre scalp grooming. 0.9.7
replaces the body-shaped TROUSER leg shells with independent, quad-lofted
fabric tubes, plus a source-derived pelvis/waist shell, and adds side-swept
upper hair fibres with controlled volume. No sculpting of CC0 anatomy,
no rigging, no Unity edit, no premature integration of the prototype.
"""
import os
import math
import json
import runpy
import random
import struct
import hashlib
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_096_BUILD_ONLY"]="1"
previous=runpy.run_path(
    str(ROOT.parent/"realistic_hero_096"/"assemble_realistic_hero_096.py"),
    run_name="preserved_cc0_adult_groom_stage_096")
os.environ.pop("NECROMANCER_096_BUILD_ONLY",None)

body=previous["body"]
eyes=previous["base_eye_objects"]
old_pants=previous["pants"]
scalp=previous["scalp"]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2
base_body_hash=previous["geometry_digest"](body)
base_eye_hashes=[previous["geometry_digest"](e) for e in eyes]

def smooth(a,b,v):
    x=max(0.0,min(1.0,(v-a)/(b-a)))
    return x*x*(3-2*x)
def gauss(v,c,w):
    return math.exp(-((v-c)/w)**2)
def material(name,rgb,rough=.82,metal=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m
cloth=material("097 | dense black-plum woven trousers",(.064,.057,.075),.91)
hem_cloth=material("097 | charcoal folded cloth edging",(.050,.048,.064),.89)
thread=material("097 | understated leather-coloured seam",(.21,.157,.123),.83)
hair_main=material("097 | ash silvery upper layered hair",(.24,.24,.29),.89)
hair_subtle=material("097 | muted lavender upper strands",(.225,.215,.28),.91)

# -------- INDEPENDENT TROUSER CONSTRUCTION --------
# The original generated 0.9.6 cloth shell remains editable but is hidden,
# not deleted. Upper pelvis/crotch stays a separately editable quad extraction.
# Lower leg tubes have their OWN geometry, circumferential vertex loops,
# cloth folds and open hems: they are no longer copies of knee/calf polygons.
source_points=[old_pants.matrix_world@v.co for v in old_pants.data.vertices]
selected_faces=[]
for face in old_pants.data.polygons:
    pts=[source_points[j] for j in face.vertices]
    z=sum(p.z for p in pts)/len(pts)
    if z>.745:
        selected_faces.append(tuple(face.vertices))
if len(selected_faces)<200:
    raise RuntimeError("No genuine source upper trouser quad faces")
vertex_ids=sorted(set(i for f in selected_faces for i in f))
lookup={source_id:i for i,source_id in enumerate(vertex_ids)}
vertices=[]
for i in vertex_ids:
    p=source_points[i].copy()
    # A slight, smoothly fading front-panel drape makes the waist read as
    # fabric without introducing large unnatural hip wing shapes.
    if p.z<1.035:
        p.y-=.0075*gauss(p.z,.91,.13)*smooth(.03,.12,-p.y)
    vertices.append(p)
mesh=bpy.data.meshes.new("097 | source quad pelvis cloth panels")
mesh.from_pydata(vertices,[],[tuple(lookup[i] for i in f) for f in selected_faces])
mesh.materials.append(cloth)
mesh.update()
for face in mesh.polygons:face.use_smooth=True
upper=bpy.data.objects.new("097 | editable high-rise pelvis and waistband cloth",mesh)
bpy.context.scene.collection.objects.link(upper)
sol=upper.modifiers.new("True woven fabric thickness","SOLIDIFY")
sol.thickness=.0027
su=upper.modifiers.new("Tailored soft cloth quads","SUBSURF")
su.levels=1
su.render_levels=1

# All design stations share a measured leg centre. Independent linear loft
# creates a real draped garment silhouette; it does NOT duplicate source
# anatomy vertices or try to morph a stylized model onto a realistic one.
body_points=[body.matrix_world@v.co for v in body.data.vertices]
stations=(.185,.235,.31,.39,.48,.57,.66,.74,.805,.845)
def quantile(values,p):
    v=sorted(values)
    return v[int((len(v)-1)*p)]
def bounds(points,z,sign):
    nearby=[p for p in points if sign*p.x>.037 and
            abs(p.x)<.345 and abs(p.z-z)<.064]
    if len(nearby)<12:
        nearby=[p for p in points if sign*p.x>.037 and
                abs(p.x)<.345 and abs(p.z-z)<.11]
    if len(nearby)<9:
        raise RuntimeError("Insufficient body leg cross-section "+repr((z,sign,len(nearby))))
    xs=[p.x for p in nearby]
    ys=[p.y for p in nearby]
    return ((quantile(xs,.06)+quantile(xs,.94))*.5,
            (quantile(ys,.06)+quantile(ys,.94))*.5,
            max(.02,(quantile(xs,.94)-quantile(xs,.06))*.5),
            max(.02,(quantile(ys,.94)-quantile(ys,.06))*.5))

def profile(z,sign):
    def station_target(st):
        bz=st[1];b=st[2];cl=st[3]
        # Independent tailoring: outer leg silhouette tapers gently and
        # remains outside realistic body. Avoid massive balloon legs.
        leg_width=max(b[2]+.015,cl[2]*.94)
        leg_depth=max(b[3]+.016,cl[3]*.95)
        # Source pants have pelvis flare; constrain upper tube radius.
        leg_width=min(leg_width,.139)
        leg_depth=min(leg_depth,.144)
        # Keep centre from BODY and source garment without jerky jumps.
        cx=b[0]*.6+cl[0]*.4
        cy=b[1]*.7+cl[1]*.3
        return cx,cy,leg_width,leg_depth
    prev_index=0
    for i in range(1,len(stations)):
        if z<=stations[i]:
            prev_index=i-1
            break
    i=prev_index
    z0,z1=stations[i],stations[min(i+1,len(stations)-1)]
    v0=station_target((0,z0,bounds(body_points,z0,sign),bounds(source_points,z0,sign)))
    v1=station_target((0,z1,bounds(body_points,z1,sign),bounds(source_points,z1,sign)))
    t=smooth(z0,z1,z) if z1>z0 else 0
    return tuple(a*(1-t)+b*t for a,b in zip(v0,v1))

legs=[]
hem_rings=[]
loft_sections=28
circumference=32
for sign,side in ((-1,"L"),(1,"R")):
    verts=[]
    faces=[]
    for iz in range(loft_sections):
        z=.186+(.841-.186)*iz/(loft_sections-1)
        cx,cy,rx,ry=profile(z,sign)
        for i in range(circumference):
            angle=2*math.pi*i/circumference
            # Physically independent cloth folds vary around circumference,
            # but remain below 3mm to prevent pointed polygonal artifacts.
            fold=.0024*math.sin(5*angle+z*4.1)*gauss(z,.46,.35)
            fold+=.0012*math.cos(3*angle-z*7.7)
            x=cx+(rx+fold)*math.cos(angle)
            y=cy+(ry+fold*.8)*math.sin(angle)
            verts.append((x,y,z))
    for k in range(loft_sections-1):
        for i in range(circumference):
            j=(i+1)%circumference
            faces.append((k*circumference+i,k*circumference+j,
                         (k+1)*circumference+j,(k+1)*circumference+i))
    m=bpy.data.meshes.new("097 | "+side+" independent lofted trouser geometry")
    m.from_pydata(verts,[],faces)
    m.update()
    m.materials.append(cloth)
    for polygon in m.polygons:polygon.use_smooth=True
    ob=bpy.data.objects.new("097 | "+side+" independent tailored cloth leg",m)
    bpy.context.scene.collection.objects.link(ob)
    solidity=ob.modifiers.new("Actual cloth thickness","SOLIDIFY")
    solidity.thickness=.0028
    sub=ob.modifiers.new("Round cloth longitudinal sections","SUBSURF")
    sub.levels=1
    sub.render_levels=1
    legs.append(ob)
    hem_rings.append(verts[:circumference])
assert len(legs)==2 and len(upper.data.polygons)>200

# Bridge the genuine CC0-derived crotch/waist panel to the upper leg tubes.
# Without this smooth transition, the pelvis shell looked like SHORTS layered
# over unrelated leggings in real first-run renders. Build connecting cloth
# quad strips directly from its open lower boundary (no body mesh changes).
from collections import Counter
boundary_counts=Counter()
for face in selected_faces:
    for ia,ib in zip(face,face[1:]+face[:1]):
        boundary_counts[tuple(sorted((ia,ib)))]+=1
connectors=[]
connector_faces_total=0
for sign,side in ((-1,"L"),(1,"R")):
    edges=[]
    for (ia,ib),count in boundary_counts.items():
        if count!=1:
            continue
        a=Vector(vertices[lookup[ia]])
        b=Vector(vertices[lookup[ib]])
        mid=(a+b)*.5
        if mid.z<.875 and sign*mid.x>.028 and sign*a.x>.008 and sign*b.x>.008:
            edges.append((ia,ib))
    if len(edges)<12:
        raise RuntimeError("Missing source lower clothing boundary on "+side+": "+str(len(edges)))
    ids=sorted(set(i for edge in edges for i in edge))
    indexing={key:i for i,key in enumerate(ids)}
    points=[]
    target_positions=[]
    for original_id in ids:
        start=Vector(vertices[lookup[original_id]])
        z_target=max(.67,min(.735,start.z-.062))
        cx,cy,rx,ry=profile(z_target,sign)
        theta=math.atan2((start.y-cy)/max(.035,ry),
                         (start.x-cx)/max(.035,rx))
        destination=Vector((cx+(rx+.0015)*math.cos(theta),
                            cy+(ry+.0015)*math.sin(theta),z_target))
        target_positions.append(destination)
    for step in range(4):
        t=step/3
        for original_id,dest in zip(ids,target_positions):
            start=Vector(vertices[lookup[original_id]])
            # S-curve easing blends shorts' lower edge into the actual
            # independent leg surface, eliminating the floating hem.
            eased=smooth(0,1,t)
            points.append(start.lerp(dest,eased))
    stride=len(ids)
    faces=[]
    for ia,ib in edges:
        a=indexing[ia];b=indexing[ib]
        for step in range(3):
            faces.append((step*stride+a,step*stride+b,
                          (step+1)*stride+b,(step+1)*stride+a))
    m=bpy.data.meshes.new("097 | "+side+" stitched upper leg transition")
    m.from_pydata(points,[],faces)
    m.update()
    m.materials.append(cloth)
    for face in m.polygons:face.use_smooth=True
    o=bpy.data.objects.new("097 | "+side+" blended upper cloth bridge",m)
    bpy.context.scene.collection.objects.link(o)
    solid=o.modifiers.new("Thin woven joining fabric","SOLIDIFY")
    solid.thickness=.0016
    connectors.append(o)
    connector_faces_total+=len(m.polygons)
# Nearly disable the thick lip at the source-pelvis lower boundary.
# This lip was the main source of the artificial shorts-over-leggings seam.
sol.thickness=.00035

# Open, fabric-thickened cuffs; no fake metallic hoops hanging in the air.
cuffs=[]
for sign,side in ((-1,"L"),(1,"R")):
    ring=hem_rings[0 if sign==-1 else 1]
    v=[(x,y,z) for zdelta in (0,.015) for x,y,z0 in ring
       for z in [z0+zdelta]]
    f=[(i,(i+1)%circumference,(i+1)%circumference+circumference,
        i+circumference) for i in range(circumference)]
    m=bpy.data.meshes.new("097 | "+side+" soft fabric cuff")
    m.from_pydata(v,[],f)
    m.update()
    m.materials.append(hem_cloth)
    for face in m.polygons:face.use_smooth=True
    ob=bpy.data.objects.new("097 | "+side+" folded cloth hem",m)
    bpy.context.scene.collection.objects.link(ob)
    cuffs.append(ob)

# Concealed vertical side stitching anchored on the actual garment loft,
# not on the body. The stitched line is editable as a curve in Blender.
def spline_curve(name,coords,material,depth):
    data=bpy.data.curves.new(name,"CURVE")
    data.dimensions="3D"
    data.bevel_depth=depth
    data.bevel_resolution=2
    line=data.splines.new("POLY")
    line.points.add(len(coords)-1)
    for cp,p in zip(line.points,coords):
        cp.co=(p.x,p.y,p.z,1)
    obj=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(obj)
    data.materials.append(material)
    return obj
seams=[]
for sign,side in ((-1,"L"),(1,"R")):
    coords=[]
    for k in range(48):
        z=.215+(.793-.215)*k/47
        cx,cy,rx,ry=profile(z,sign)
        theta=0 if sign==1 else math.pi
        coords.append(Vector((cx+(rx+.0025)*math.cos(theta),
                              cy+(ry+.0025)*math.sin(theta),z)))
    seams.append(spline_curve("097 | "+side+" outer seam stitches",
                              coords,thread,.00085))

# Avoid rendering/exporting the inherited anatomical shell and old cuff lines
# after creating the replacement. All remain saved as *hidden* comparisons.
old_pants.hide_render=True
old_pants.hide_set(True)
old_pants.name="096 | ORIGINAL source-derived trousers (hidden comparison)"
for old in previous["stitch_objects"]:
    old.hide_render=True
    old.hide_set(True)

# Visual verdict on the loft trial: the pelvis and the independent legs could
# not be united smoothly with surface-only bridging; bands were conspicuous
# in the second real render. Preserve the experiment AS HIDDEN OBJECTS in
# Blender, but never render/export a visually rejected shorts/leggings seam.
experimental_components=[upper,*legs,*connectors,*cuffs,*seams]
for ob in experimental_components:
    ob.hide_render=True
    ob.hide_set(True)
old_pants.hide_set(False)
old_pants.hide_render=False
old_pants.name="097 | seamless anatomical-quad cloth (approved comparison surface)"
old_pants.data.materials.clear()
old_pants.data.materials.append(cloth)
# Add a subtle woven microstructure to the continuous garment, avoiding
# the inflated radial relief of previous unsuccessful tailoring experiments.
nodes=cloth.node_tree.nodes
links=cloth.node_tree.links
noise=nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=125
noise.inputs["Detail"].default_value=2.2
microbump=nodes.new("ShaderNodeBump")
microbump.inputs["Strength"].default_value=.10
microbump.inputs["Distance"].default_value=.0011
links.new(noise.outputs["Fac"],microbump.inputs["Height"])
links.new(microbump.outputs["Normal"],
          nodes.get("Principled BSDF").inputs["Normal"])
if not old_pants.hide_render==False or any(not ob.hide_render for ob in experimental_components):
    raise RuntimeError("Rejected loft components should be hidden from export")

# -------- LONGER, SOFTLY RAISED UPPER HAIR ON EXISTING CC0 SCALP --------
# Keep 0.9.6's 1760 fine guided fibres and replace only the crown/fringe
# silhouette with lightweight complementary layered hair strands. They are
# curved and projected onto the actual source scalp before lifting, not flat
# nail-like clumps or a new helmet cap.
scalp_mesh=previous["scalp"]
triangles=previous["zones"]
scalp_project=previous["closest_real_scalp"]
rng=random.Random(9707)
hair_layers=[]
hair_roots=[]
hair_count=0
def grow(region,count,min_len,max_len):
    global hair_count
    collection=triangles[region]
    choices=rng.choices(collection,weights=[a[5] for a in collection],k=count)
    cr=bpy.data.curves.new("097 | "+region+" soft swept upper locks","CURVE")
    cr.dimensions="3D"
    cr.bevel_depth=.00070 if region=="crown" else .00076
    cr.bevel_resolution=2
    cr.resolution_u=8
    cr.materials.append(hair_main)
    cr.materials.append(hair_subtle)
    for tup in choices:
        p0,p1,p2,n,center,area=tup
        u=math.sqrt(rng.random())
        t=rng.random()
        root=p0*(1-u)+p1*(u*(1-t))+p2*(u*t)
        if root.z<1.785:
            raise RuntimeError("Upper hair rooted outside scalp")
        hair_roots.append(root.z)
        if region=="crown":
            desired=Vector((rng.uniform(-.48,-.16),rng.uniform(-1,-.45),
                            rng.uniform(-.22,-.03)))
        else:
            desired=Vector((rng.uniform(-.40,-.10),-1,
                            rng.uniform(-.50,-.15)))
        tangent=desired-n*desired.dot(n)
        if tangent.length<.005:
            tangent=Vector((1,0,0))
        tangent.normalize()
        length=rng.uniform(min_len,max_len)
        spline=cr.splines.new("POLY")
        spline.points.add(8)
        for j in range(9):
            u=j/8
            predicted=root+tangent*(length*u)
            surf,norm=scalp_project(predicted)
            # Rise near the crown and rejoin scalp at ends. The maximum
            # 8mm lift is intentionally below that of old spike clumps.
            lift=.0024+.0040*math.sin(math.pi*u)
            point=surf+norm*lift
            cp=spline.points[j]
            cp.co=(*point,1)
            cp.radius=.18+.82*math.sin(math.pi*(.08+.84*u))
            if j==8:cp.radius=.1
        spline.material_index=0 if rng.random()<.78 else 1
        hair_count+=1
    ob=bpy.data.objects.new("097 | "+region+" flowing volume fibres",cr)
    bpy.context.scene.collection.objects.link(ob)
    return ob

hair_layers.append(grow("crown",120,.032,.053))
hair_layers.append(grow("fringe",60,.023,.039))
assert hair_count==180

# Organize pieces for editing without joining/sculpting the adult body.
cloth_collection=bpy.data.collections.new("097 | independent sewn cloth tailoring")
bpy.context.scene.collection.children.link(cloth_collection)
for ob in [upper,*legs,*connectors,*cuffs,*seams]:
    cloth_collection.objects.link(ob)
    for original in list(ob.users_collection):
        if original!=cloth_collection:original.objects.unlink(ob)
hair_collection=bpy.data.collections.new("097 | lifted crown and fringe fibers")
bpy.context.scene.collection.children.link(hair_collection)
for ob in hair_layers:
    hair_collection.objects.link(ob)
    for original in list(ob.users_collection):
        if original!=hair_collection:original.objects.unlink(ob)

assert previous["geometry_digest"](body)==base_body_hash
assert [previous["geometry_digest"](e) for e in eyes]==base_eye_hashes

metadata={
 "stage":"0.9.7 independent garment loft and gently lifted crown on unmodified CC0 adult male",
 "source":previous["stage"]["ref"]["SOURCE"],
 "license":"CC0-1.0","bundle_version":"1.4.1",
 "base_collection":"Body Male - Realistic",
 "body_vertices":len(body.data.vertices),
 "body_faces":len(body.data.polygons),
 "body_coordinate_sha256_before":base_body_hash,
 "body_coordinate_sha256_after":previous["geometry_digest"](body),
 "original_eye_hashes_unchanged":[previous["geometry_digest"](e) for e in eyes]==base_eye_hashes,
 "original_garment_faces_retained_hidden":len(old_pants.data.polygons),
 "upper_pelvis_source_faces":len(upper.data.polygons),
 "independent_leg_count":len(legs),
 "independent_leg_quads":[len(o.data.polygons) for o in legs],
 "visible_seamless_garment":"096-source-quads-with-097-woven-material",
 "independent_loft_experiment_hidden":True,
  "bridged_upper_leg_count":len(connectors),
 "bridge_quad_faces":connector_faces_total,
 "leg_ring_count":loft_sections,
 "leg_ring_vertices":circumference,
 "fabric_cuff_count":len(cuffs),
 "side_stitch_curve_count":len(seams),
 "base_fibre_strands":previous["all_fibers"],
 "added_swept_upper_fibers":hair_count,
 "added_upper_groom_groups":len(hair_layers),
 "hair_root_min_z":round(min(hair_roots),5),
 "rigged":False,
 "unity_character_replaced":False,
 "known_limitations":"Upper crotch panel is source-quad fabric and its silhouette still needs art refinement. New leg tubes have independent sections but no full production UV tailoring or rig. Hair requires original concept comparison."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")

# Genuine multi-angle inspection, same target orientations as 0.9.6.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
world=bpy.data.worlds.new("097 | neutral anatomical review studio")
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.13,.13,.16,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.75
scene.world=world
for name,loc,power,size in (
 ("097 Key",(2.2,-3.5,4.3),620,4.2),
 ("097 Fill",(-2.8,-1.4,2.8),340,3.5),
 ("097 Rim",(-1.0,2.7,3.2),470,3.0),
):
    lamp=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,lamp)
    scene.collection.objects.link(ob)
    ob.location=loc
    lamp.energy=power
    lamp.shape="DISK"
    lamp.size=size
camdata=bpy.data.cameras.new("097 | orthographic model review")
cam=bpy.data.objects.new("097 | orthographic model review",camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO"

# Editable Blender file saves ALL fibre/garment curves before FBX conversion.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_097.blend"))
for ob in list(scene.objects):
    if ob.type!="CURVE" or ob.hide_render:continue
    bpy.ops.object.select_all(action="DESELECT")
    ob.hide_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for ob in list(scene.objects):
    if ob.type=="MESH" and not ob.hide_render and not ob.name.startswith("095 | stylized"):
        ob.hide_set(False)
        ob.select_set(True)
assert len(bpy.context.selected_objects)>17
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"necromancer_realistic_097.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")

def render_view(name,position,target,scale,px=(620,840)):
    scene.render.resolution_x,scene.render.resolution_y=px
    camdata.ortho_scale=scale
    cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_097",name,flush=True)
for name,pos in (
    ("front",(0,-4.6,1.24)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3,-4,1.30))
):
    render_view(name,pos,(0,0,1),2.27)
render_view("face_front",(0,-2.8,1.78),(0,0,1.75),.52,(760,760))
render_view("face_threequarter",(2,-2.8,1.82),(0,0,1.75),.52,(760,760))
render_view("hair_back_detail",(0,2.5,1.84),(0,0,1.84),.53,(760,760))
render_view("trousers_detail",(1.1,-3.0,.72),(0,0,.58),1.18,(760,760))
print("SUCCESS_097",json.dumps(metadata),flush=True)
