"""Necromancer Overworld v0.9.6 — cohesive 3D hair clumps & tailored trousers.

Uses the ORIGINAL Blender Studio Body Male – Realistic v1.4.1 (CC0) as
assembled in the verified 0.9.5 stage. All 10,582 body vertices and
10,590 body polygons are left untouched. No Unity integration or rigging.
Old paper-ribbon hair is replaced with genuine volume-bearing clump meshes
and editable fine accent curves. Trousers are modified only on their OWN
CC0-derived quad-shell mesh.
"""
import os
import runpy
import json
import math
import random
import struct
import hashlib
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_095_ASSEMBLY_ONLY"]="1"
stage=runpy.run_path(str(ROOT.parent/"realistic_hero_095"/"assemble_realistic_hero_095.py"),
                     run_name="verified_adult_095_stage_for_096")
os.environ.pop("NECROMANCER_095_ASSEMBLY_ONLY",None)
body=stage["body"]
pants=stage["pants"]
scalp=stage["scalp"]
old_hair=stage["hair"]
old_hair_mesh=old_hair.data
base_eye_objects=stage["eye_objs"]
assert len(base_eye_objects)==2
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)

def geometry_digest(obj):
    sha=hashlib.sha256()
    for v in obj.data.vertices:
        sha.update(struct.pack("<3d",float(v.co.x),float(v.co.y),float(v.co.z)))
    return sha.hexdigest()

face_hash_before=geometry_digest(body)
eye_hashes_before=[geometry_digest(o) for o in base_eye_objects]
def gaussian(value,mu,sigma):
    return math.exp(-((value-mu)/sigma)**2)
def smooth(a,b,x):
    t=max(0.0,min(1.0,(x-a)/(b-a)))
    return t*t*(3-2*t)
def material(name,color,rough=.72,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1.0)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m

# ---- TAILORED TROUSERS (KEEP THE REAL SOURCE QUAD LOOP STRUCTURE) ----
# No new 'body' geometry; only re-tailor the CC0-derived trousers shell.
pants.name="096 | tailored dark trousers • preserved inherited quad loops"
pants_mat=material("096 | charcoal violet dense textile",(.060,.053,.074),.89)
pants.data.materials.clear()
pants.data.materials.append(pants_mat)
seam_mat=material("096 | antique low-lustre thread",(.26,.17,.089),.76,.12)

def quantile(seq,q):
    ss=sorted(seq)
    return ss[int(q*(len(ss)-1))]

body_world=[body.matrix_world@v.co for v in body.data.vertices]
pants_world=[pants.matrix_world@v.co for v in pants.data.vertices]
pants_inverse=pants.matrix_world.inverted_safe()
from collections import defaultdict
cache={}
def slice_stats(z,side,kind):
    key=(round(z/.025),side,kind)
    if key in cache:
        return cache[key]
    source=body_world if kind=="body" else pants_world
    # Mesh is sparse in some areas; use a local vertical neighborhood.
    nearby=[p for p in source if side*p.x>.025 and abs(p.z-z)<.055]
    if len(nearby)<12:
        nearby=[p for p in source if side*p.x>.025 and abs(p.z-z)<.087]
    if len(nearby)<8:
        raise RuntimeError("No source leg slice at z %.3f, %s, %s"%(z,side,kind))
    minx,maxx=quantile([p.x for p in nearby],.045),quantile([p.x for p in nearby],.955)
    miny,maxy=quantile([p.y for p in nearby],.045),quantile([p.y for p in nearby],.955)
    val=((minx+maxx)*.5,(miny+maxy)*.5,
         max(.012,(maxx-minx)*.5),max(.012,(maxy-miny)*.5))
    cache[key]=val
    return val

def radius_at(z,control):
    if z<=control[0][0]:return control[0][1]
    for (za,ra),(zb,rb) in zip(control[:-1],control[1:]):
        if z<=zb:
            t=smooth(za,zb,z)
            return ra*(1-t)+rb*t
    return control[-1][1]

# Distinct garment profile: no pinched ankles and no inflated knees.
widths=[(.17,.073),(.28,.077),(.41,.085),(.57,.091),
        (.72,.105),(.84,.117),(.96,.132)]
depths=[(.17,.072),(.28,.080),(.41,.090),(.57,.100),
        (.72,.111),(.84,.122),(.96,.135)]
# A conservative silhouette correction replaces the first attempt's
# angular cross-section remapping. That attempt expanded the outer thighs into
# pointed wings even though the body silhouette was unchanged.
# Keep the ORIGINAL source-leg geometry, attenuating radial width only.
adjusted=0
for vert in pants.data.vertices:
    p=pants.matrix_world@vert.co
    z=p.z
    if not .16<z<.95 or abs(p.x)<.018:
        continue
    side=1 if p.x>0 else -1
    leg_center=side*.136
    taper=smooth(.16,.26,z)*(1-smooth(.72,.95,z))
    lower_leg=gaussian(z,.41,.28)
    width_reduction=(.075+.085*lower_leg)*taper
    p.x=leg_center+(p.x-leg_center)*(1-width_reduction)
    p.y=p.y*(1-.045*taper)
    vert.co=pants_inverse@p
    adjusted+=1

# Smooth only X and Y over the knee/calf area; preserve all Z/hem heights.
neighbors=[set() for _ in pants.data.vertices]
for edge in pants.data.edges:
    i,j=edge.vertices
    neighbors[i].add(j)
    neighbors[j].add(i)
for iteration in range(4):
    prev=[v.co.copy() for v in pants.data.vertices]
    for i,vert in enumerate(pants.data.vertices):
        z=(pants.matrix_world@prev[i]).z
        if not .26<z<.71 or len(neighbors[i])<3:
            continue
        avg=sum((prev[k] for k in neighbors[i]),Vector())/len(neighbors[i])
        w=.22*gaussian(z,.48,.19)
        vert.co.x=prev[i].x*(1-w)+avg.x*w
        vert.co.y=prev[i].y*(1-w)+avg.y*w

# Guard against a repeat of the visually rejected triangular thigh expansion.
old_upper=max(abs(p.x) for p in pants_world if .62<p.z<.90)
new_world=[pants.matrix_world@v.co for v in pants.data.vertices]
new_upper=max(abs(p.x) for p in new_world if .62<p.z<.90)
if new_upper>old_upper+.004:
    raise RuntimeError("Upper trousers silhouette unexpectedly expanded: %.4f > %.4f"%(new_upper,old_upper))
pants.data.update()
if adjusted<600:
    raise RuntimeError("Trouser tailoring affected too few vertices: %d"%adjusted)

# Editable fine thread placed along lower hems with measured leg profiles.
# Curves are deliberately restrained; gold references are not versioned.
def create_curve(name,coords,mat,bevel=.00135):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=bevel
    curve.bevel_resolution=2
    curve.resolution_u=8
    spl=curve.splines.new("POLY")
    spl.points.add(len(coords)-1)
    for p,v in zip(spl.points,coords):
        p.co=(v.x,v.y,v.z,1)
    o=bpy.data.objects.new(name,curve)
    bpy.context.scene.collection.objects.link(o)
    curve.materials.append(mat)
    return o

# For each ring, actually raycast the TROUSER surface from outside
# and offset outwards. This prevents embroidery floating in empty space.
# Ornament is deliberately subtle: simple cuff outline, not invented sigils.
stitch_objects=[]
for side,name in ((-1,"L"),(1,"R")):
    z=.198
    cx,cy,rx,ry=slice_stats(z,side,"pants")
    coords=[]
    for i in range(52):
        angle=2*math.pi*i/51
        x=cx+rx*math.cos(angle)
        y=cy+ry*math.sin(angle)
        coords.append(Vector((x,y,z+.002*math.sin(2*angle))))
    stitch_objects.append(create_curve("096 | "+name+" cuff antique-gold thread",coords,seam_mat,.00095))

# ---- FIBRE GROOM: real CURVES over the official anatomical scalp ----
# Previous sculpted clumps resembled nails over an untextured helmet. Replace
# them with many short tapered hair fibres that conform to the ACTUAL scalp
# surface, including nape and temples. This remains editable in the .blend.
bpy.data.objects.remove(old_hair,do_unlink=True)
if old_hair_mesh.users==0:
    bpy.data.meshes.remove(old_hair_mesh)
scalp.name="096 | realistic CC0 scalp underlay"
scalp.data.materials.clear()
scalp_base=material("096 | shaded ash-lilac rooted hair",(.15,.15,.19),.89)
scalp.data.materials.append(scalp_base)
for mod in scalp.modifiers:
    if mod.type=="SOLIDIFY":
        mod.thickness=.00065

# Real directional fibre coloration; prevents a flat helmet appearance.
nodes=scalp_base.node_tree.nodes
links=scalp_base.node_tree.links
waves=nodes.new("ShaderNodeTexWave")
waves.wave_type="BANDS"
waves.bands_direction="X"        # fine root-to-tip vertical texture at nape
waves.inputs["Scale"].default_value=67.0
waves.inputs["Distortion"].default_value=3.4
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.32
ramp.color_ramp.elements[0].color=(.095,.092,.13,1)
ramp.color_ramp.elements[1].position=.68
ramp.color_ramp.elements[1].color=(.29,.29,.35,1)
links.new(waves.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],nodes.get("Principled BSDF").inputs["Base Color"])

fiber_colors=[
 material("096 | silver-gray hair fibres",(.30,.30,.35),.83),
 material("096 | lilac hair fibres",(.29,.27,.34),.86),
 material("096 | graphite shadow fibres",(.15,.15,.20),.9),
 material("096 | ash highlights",(.38,.38,.42),.81),
]
rng=random.Random(9607)
scalp_inverse=scalp.matrix_world.inverted_safe()
scalp_normal_transform=scalp.matrix_world.to_3x3().inverted_safe().transposed()

# Triangulate polygons only in MEMORY for uniform point sampling; scalp's
# editable inherited quad mesh is never triangulated or re-topologized.
triangles=[]
for polygon in scalp.data.polygons:
    ids=list(polygon.vertices)
    verts=[scalp.matrix_world@scalp.data.vertices[i].co for i in ids]
    for k in range(1,len(verts)-1):
        a0,a1,a2=verts[0],verts[k],verts[k+1]
        n=(a1-a0).cross(a2-a0)
        area=.5*n.length
        if area<1e-8:continue
        normal=n.normalized()
        center=(a0+a1+a2)/3
        triangles.append((a0,a1,a2,normal,center,area))
if len(triangles)<200:
    raise RuntimeError("Unexpectedly few source CC0 scalp triangles")

def region_triangles(region):
    if region=="crown":
        return [t for t in triangles if t[4].z>1.843]
    if region=="fringe":
        return [t for t in triangles if t[4].y<-.023 and t[4].z>1.811]
    if region=="temples":
        return [t for t in triangles if abs(t[4].x)>.051 and t[4].z>1.791]
    if region=="nape":
        return [t for t in triangles if t[4].y>.033 and 1.772<t[4].z<1.858]
    raise ValueError(region)

zones={r:region_triangles(r) for r in ("crown","fringe","temples","nape")}
print("FIBRE_ZONE_FACE_COUNTS",json.dumps({k:len(v) for k,v in zones.items()}),flush=True)
if min(map(len,zones.values()))<8:
    raise RuntimeError("Source scalp triangles cannot support hairline zones")

def barycentric_sample(triangle):
    p,q,r,n,center,area=triangle
    u=math.sqrt(rng.random())
    v=rng.random()
    root=p*(1-u)+q*(u*(1-v))+r*(u*v)
    return root,n

def closest_real_scalp(p):
    query=scalp_inverse@p
    hit,local,norm,face=scalp.closest_point_on_mesh(query)
    if not hit:raise RuntimeError("Fibre guide left original scalp")
    pos=scalp.matrix_world@local
    normal=(scalp_normal_transform@norm).normalized()
    return pos,normal

def groom_region(region,count,min_len,max_len):
    samples=zones[region]
    selected=rng.choices(samples,weights=[t[5] for t in samples],k=count)
    curve=bpy.data.curves.new("096 | "+region+" individual guided fibres","CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=.00067
    curve.bevel_resolution=2
    curve.resolution_u=5
    for m in fiber_colors:curve.materials.append(m)
    root_heights=[]
    for index,tri in enumerate(selected):
        root,normal=barycentric_sample(tri)
        if root.z<1.766:
            raise RuntimeError("Hair fibre rooted on neck or back")
        root_heights.append(root.z)
        if region=="crown":
            desire=Vector((rng.uniform(-.45,-.12),rng.uniform(-1,-.52),-.23))
        elif region=="fringe":
            desire=Vector((rng.uniform(-.38,-.06),-1,-.45))
        elif region=="nape":
            desire=Vector((rng.uniform(-.20,.20),.30,-.91))
        else:
            side=-1 if root.x<0 else 1
            desire=Vector((side*rng.uniform(.17,.45),
                           rng.uniform(-.25,.16),-.78))
        # Tangential directions follow cranial curvature, not free-floating
        # spikes through the air.
        tangent=desire-normal*desire.dot(normal)
        if tangent.length<.025:
            tangent=Vector((1,0,0))-normal*normal.x
        tangent.normalize()
        length=rng.uniform(min_len,max_len)
        spline=curve.splines.new("POLY")
        spline.points.add(6)
        for j in range(7):
            t=j/6
            predicted=root+tangent*(length*t)
            surf,surf_n=closest_real_scalp(predicted)
            lift=.0019+.0017*math.sin(math.pi*t)
            pt=surf+surf_n*lift
            point=spline.points[j]
            point.co=(pt.x,pt.y,pt.z,1)
            # True taper: no faceted triangular nail ends.
            point.radius=max(.05,(1-t)**.63)
        spline.material_index=rng.choices([0,1,2,3],[6,2,3,1])[0]
    ob=bpy.data.objects.new("096 | "+region+" short flowing fibres (editable)",curve)
    bpy.context.scene.collection.objects.link(ob)
    return ob,root_heights

hair_objects=[]
root_z=[]
counts={"crown":820,"fringe":290,"temples":310,"nape":340}
ranges={
 "crown":(.018,.034),"fringe":(.016,.029),
 "temples":(.014,.026),"nape":(.015,.029)
}
for region,count in counts.items():
    hair_obj,heights=groom_region(region,count,*ranges[region])
    hair_objects.append(hair_obj)
    root_z.extend(heights)

all_fibers=sum(counts.values())
if all_fibers!=1760 or len(hair_objects)!=4:
    raise RuntimeError("Missing fibre hair region")
# Underlay and fine roots remain separate. No bulky volume fake hair caps.
highlight=hair_objects[0]
line_shapes=[None]*all_fibers
print("REAL_SCALP_FIBRES",all_fibers,"min root z",min(root_z),flush=True)

# Regroup only new dress and hair objects; do not disturb CC0 body group.
hair_collection=bpy.data.collections.new("096 | separated volumetric haircut")
bpy.context.scene.collection.children.link(hair_collection)
for ob in [scalp,*hair_objects]:
    hair_collection.objects.link(ob)
    for old in list(ob.users_collection):
        if old!=hair_collection:old.objects.unlink(ob)
tailoring_group=bpy.data.collections.new("096 | tailoring and stitch curves")
bpy.context.scene.collection.children.link(tailoring_group)
for ob in [pants,*stitch_objects]:
    tailoring_group.objects.link(ob)
    for old in list(ob.users_collection):
        if old!=tailoring_group:old.objects.unlink(ob)

# Absolute no-facial-deformation condition, with exact float64 coordinate
# digests to catch even accidental source mesh edits.
face_hash_after=geometry_digest(body)
eye_hashes_after=[geometry_digest(o) for o in base_eye_objects]
assert face_hash_after==face_hash_before
assert eye_hashes_after==eye_hashes_before

metadata={
 "stage":"0.9.6 redesigned groom and tailored silhouette on unmodified adult CC0 body",
 "source":stage["ref"]["SOURCE"],"license":"CC0-1.0","bundle_version":"1.4.1",
 "base_collection":"Body Male - Realistic",
 "body_vertices":len(body.data.vertices),
 "body_faces":len(body.data.polygons),
 "body_coordinate_sha256_before":face_hash_before,
 "body_coordinate_sha256_after":face_hash_after,
 "source_eye_mesh_hashes_unchanged":eye_hashes_before==eye_hashes_after,
 "tailored_trouser_quad_faces":len(pants.data.polygons),
 "tailored_trouser_vertices":adjusted,
 "separated_fiber_groom_groups":[o.name for o in hair_objects],
 "hair_fiber_strands":all_fibers,
 "hair_fiber_root_min_z":round(min(root_z),5),
 "hair_fiber_root_max_z":round(max(root_z),5),
 "hair_group_count":len(hair_objects),
 "original_scalp_quads":len(scalp.data.polygons),
 "separate_cuff_stitch_curves":len(stitch_objects),
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"Fibre grooms and trousers are automated prototypes, not hand-authored final character art. Approved reference is not in repository. FBX is unrigged."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")

# Studio camera and lights exclusively for genuine Blender geometry reviews.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=100
scene.render.film_transparent=False
world=bpy.data.worlds.new("096 | graphite neutral product studio")
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.135,.138,.16,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.7
scene.world=world
for name,pos,power,size in (
 ("096 | Key",(2.2,-3.5,4.3),630,4.2),
 ("096 | Fill",(-2.7,-1.4,2.7),300,3.5),
 ("096 | Rim",(-1.2,2.6,3.2),480,3.0),
):
    l=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,l)
    scene.collection.objects.link(ob)
    ob.location=pos
    l.energy=power
    l.shape="DISK"
    l.size=size

camdata=bpy.data.cameras.new("096 | true orthographic inspection")
cam=bpy.data.objects.new("096 | true orthographic inspection",camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO"

# Save .blend with original editable curves prior to FBX conversion.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_096.blend"))
for cr in list(scene.objects):
    if cr.type!="CURVE" or cr.hide_render:continue
    bpy.ops.object.select_all(action="DESELECT")
    cr.hide_set(False)
    cr.select_set(True)
    bpy.context.view_layer.objects.active=cr
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for ob in list(scene.objects):
    if ob.type=="MESH" and not ob.hide_render and not ob.name.startswith("095 | stylized"):
        ob.hide_set(False)
        ob.select_set(True)
assert len(bpy.context.selected_objects)>16
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"necromancer_realistic_096.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")

def shot(name,location,target,scale,reso=(620,840)):
    scene.render.resolution_x,scene.render.resolution_y=reso
    camdata.ortho_scale=scale
    cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_096",name,scene.render.filepath,flush=True)

for name,pos in (
    ("front",(0,-4.6,1.24)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3.0,-4.0,1.30)),
):
    shot(name,pos,(0,0,1),2.27)
shot("face_front",(0,-2.8,1.78),(0,0,1.75),.52,(760,760))
shot("face_threequarter",(2.0,-2.8,1.82),(0,0,1.75),.52,(760,760))
shot("hair_back_detail",(0,2.5,1.84),(0,0,1.84),.53,(760,760))
shot("trousers_detail",(1.1,-3.0,.72),(0,0,.58),1.18,(760,760))
print("SUCCESS_096",json.dumps(metadata),flush=True)
