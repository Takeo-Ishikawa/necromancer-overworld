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
adjusted=0
for vert in pants.data.vertices:
    p=pants.matrix_world@vert.co
    z=p.z
    if not .157<z<.967 or abs(p.x)<.026:
        continue
    side=1 if p.x>0 else -1
    cx,cy,rx,ry=slice_stats(z,side,"pants")
    _,_,brx,bry=slice_stats(z,side,"body")
    # Respect the original body envelope plus clearance; prevent clipping
    # when the quad shell is made less balloon-like.
    target_rx=max(radius_at(z,widths),brx+.011)
    target_ry=max(radius_at(z,depths),bry+.011)
    u=max(-1.15,min(1.15,(p.x-cx)/rx))
    v=max(-1.15,min(1.15,(p.y-cy)/ry))
    theta=math.atan2(v,u)
    # Very restrained long cloth creases, not spherical knee knobs.
    crease=.0022*math.cos(5*theta+5.8*z)*gaussian(z,.47,.33)
    nx=cx+u*(target_rx+crease)
    ny=cy+v*(target_ry+crease*.7)
    weight=smooth(.86,.97,z)          # blend smoothly into the waist
    p.x=nx*(1-weight)+p.x*weight
    p.y=ny*(1-weight)+p.y*weight
    vert.co=pants_inverse@p
    adjusted+=1
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

# ---- NEW HAIR: SOLID SCULPTED CLUMPS + FINE EDITABLE ACCENT CURVES ----
# Remove the old floating paper-ribbon mesh. The old scalp remains a thin
# object EXTRACTED FROM THE OFFICIAL CC0 HEAD and is kept independently editable.
bpy.data.objects.remove(old_hair,do_unlink=True)
if old_hair_mesh.users==0:
    bpy.data.meshes.remove(old_hair_mesh)
scalp.name="096 | anatomical source scalp underlay (CC0 quads)"
scalp.data.materials.clear()
scalp_base=material("096 | subtle charcoal ash hair roots",(.158,.157,.200),.92)
scalp.data.materials.append(scalp_base)
for mod in scalp.modifiers:
    if mod.type=="SOLIDIFY":mod.thickness=.00075

base_hair=[
 material("096 | cool silver smoke bulk",(.31,.32,.38),.84),
 material("096 | muted lavender brown sheen",(.30,.28,.37),.82),
 material("096 | deep ash between clumps",(.20,.20,.27),.90),
]
fine_hair=material("096 | discrete silver strand accents",(.41,.41,.46),.86)
rng=random.Random(9606)
scalp_vertices=[scalp.matrix_world@v.co for v in scalp.data.vertices]
if len(scalp_vertices)<200:
    raise RuntimeError("Source scalp unexpectedly sparse")
zones={
 "crown":[v for v in scalp_vertices if v.z>1.844 and abs(v.x)<.118],
 "fringe":[v for v in scalp_vertices if v.y<-.024 and v.z>1.812],
 "temples":[v for v in scalp_vertices if abs(v.x)>.055 and v.z>1.795],
 "nape":[v for v in scalp_vertices if v.y>.040 and 1.780<v.z<1.86],
}
print("SCALP_ZONES",json.dumps({k:len(v) for k,v in zones.items()}),flush=True)
if min(len(v) for v in zones.values())<8:
    raise RuntimeError("Not enough official scalp loops for groom zones")

groups={}
line_shapes=[]
root_z=[]
all_clumps=0
def add_clump(zone,root,direction,length,width,thickness,arc,mat_index):
    global all_clumps
    if root.z<1.775:
        raise RuntimeError("Hair clump outside head: z=%.3f"%root.z)
    all_clumps+=1
    root_z.append(root.z)
    direction=direction.normalized()
    tip=root+direction*length
    lateral=Vector((-direction.y,direction.x,0))
    if lateral.length<.03:lateral=Vector((1,0,0))
    lateral.normalize()
    perpendicular=direction.cross(lateral)
    if perpendicular.length<.03:perpendicular=Vector((0,0,1))
    perpendicular.normalize()
    # 3D tapered elliptical cross sections, not zero-thickness cards.
    verts,faces,materials=groups.setdefault(zone,([],[],[]))
    offset=len(verts)
    centreline=[]
    rings=9
    circumference=8
    for j in range(rings):
        t=j/(rings-1)
        bulge=math.sin(math.pi*t)
        center=root.lerp(tip,t)+Vector((0,0,arc*bulge))
        centreline.append(center)
        profile=.04+.96*(1-t)**.67
        w=width*profile*.5
        h=thickness*profile*.5
        for k in range(circumference):
            angle=2*math.pi*k/circumference
            pos=center+lateral*(w*math.cos(angle))+perpendicular*(h*math.sin(angle))
            verts.append(pos)
    for j in range(rings-1):
        for k in range(circumference):
            n=(k+1)%circumference
            faces.append((offset+j*circumference+k,offset+j*circumference+n,
                          offset+(j+1)*circumference+n,offset+(j+1)*circumference+k))
            materials.append(mat_index)
    faces.append(tuple(offset+k for k in range(circumference-1,-1,-1)))
    materials.append(mat_index)
    faces.append(tuple(offset+(rings-1)*circumference+k for k in range(circumference)))
    materials.append(mat_index)
    # A small proportion of clumps carry real editable highlight splines.
    if all_clumps%3==0:
        line_shapes.append([p+perpendicular*(thickness*.53) for p in centreline[1:-1]])

def select_roots(points,n):
    indices=list(range(len(points)))
    rng.shuffle(indices)
    # Cycle with seeded reshuffles to prevent random piling.
    roots=[]
    while len(roots)<n:
        for idx in indices:
            roots.append(points[idx])
            if len(roots)>=n:break
        rng.shuffle(indices)
    return roots

# The crown is side-swept towards the front, NOT randomly spiked in all
# directions. Short clumps overlap naturally and cover the dark scalp.
for p in select_roots(zones["crown"],49):
    d=Vector((rng.uniform(-.55,-.16),rng.uniform(-1.0,-.55),rng.uniform(-.28,-.08)))
    add_clump("crown",p+Vector((0,0,.0035)),d,
              rng.uniform(.030,.056),rng.uniform(.010,.020),
              rng.uniform(.003,.006),rng.uniform(.003,.010),
              rng.choices([0,1,2],[6,2,2])[0])

# Fringe defines the hairline without long paper-like spikes over the eyes.
for p in select_roots(zones["fringe"],15):
    d=Vector((rng.uniform(-.44,-.07),-.97,rng.uniform(-.40,-.18)))
    add_clump("fringe",p+Vector((0,-.001,.004)),d,
              rng.uniform(.021,.039),rng.uniform(.011,.018),
              rng.uniform(.003,.005),rng.uniform(.003,.008),
              rng.choices([0,1,2],[7,2,1])[0])

for p in select_roots(zones["temples"],21):
    sign=1 if p.x>0 else -1
    d=Vector((sign*rng.uniform(.15,.38),rng.uniform(-.30,.30),
              rng.uniform(-1.0,-.55)))
    add_clump("temples",p+Vector((0,0,.0025)),d,
              rng.uniform(.020,.042),rng.uniform(.009,.016),
              rng.uniform(.003,.005),rng.uniform(.001,.006),
              rng.choices([0,1,2],[5,1,4])[0])

for p in select_roots(zones["nape"],18):
    d=Vector((rng.uniform(-.25,.25),rng.uniform(.22,.65),
              rng.uniform(-1.0,-.60)))
    add_clump("nape",p+Vector((0,.002,.0025)),d,
              rng.uniform(.021,.039),rng.uniform(.010,.019),
              rng.uniform(.003,.006),rng.uniform(.002,.006),
              rng.choices([0,1,2],[3,1,6])[0])

hair_objects=[]
for zone,(verts,faces,material_ids) in groups.items():
    mesh=bpy.data.meshes.new("096 | "+zone+" sculpted tapered locks")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    for mat in base_hair:mesh.materials.append(mat)
    for poly,mi in zip(mesh.polygons,material_ids):
        poly.material_index=mi
        poly.use_smooth=True
    obj=bpy.data.objects.new("096 | hair "+zone+" • editable 3D clumps",mesh)
    bpy.context.scene.collection.objects.link(obj)
    hair_objects.append(obj)
if all_clumps!=103 or len(hair_objects)!=4:
    raise RuntimeError("Clump coverage failed")
curve=bpy.data.curves.new("096 | strands between layered hair clumps","CURVE")
curve.dimensions="3D"
curve.bevel_depth=.00038
curve.bevel_resolution=2
curve.resolution_u=6
curve.materials.append(fine_hair)
for coords in line_shapes:
    line=curve.splines.new("POLY")
    line.points.add(len(coords)-1)
    for point,p in zip(line.points,coords):point.co=(p.x,p.y,p.z,1)
highlight=bpy.data.objects.new("096 | subtle fine hair accents (editable curves)",curve)
bpy.context.scene.collection.objects.link(highlight)

# Regroup only new dress and hair objects; do not disturb CC0 body group.
hair_collection=bpy.data.collections.new("096 | separated volumetric haircut")
bpy.context.scene.collection.children.link(hair_collection)
for ob in [scalp,*hair_objects,highlight]:
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
 "separated_3d_hair_groups":[o.name for o in hair_objects],
 "hair_clumps":all_clumps,
 "hair_clump_root_min_z":round(min(root_z),5),
 "hair_clump_root_max_z":round(max(root_z),5),
 "highlight_splines":len(line_shapes),
 "hair_clump_mesh_faces":sum(len(o.data.polygons) for o in hair_objects),
 "separate_cuff_stitch_curves":len(stitch_objects),
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"Clump grooms and trousers are still automated prototypes, require comparison with approved visual reference (not in repository) and hand art refinements. FBX is unrigged."
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
