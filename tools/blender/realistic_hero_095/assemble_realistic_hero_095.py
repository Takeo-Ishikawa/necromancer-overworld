"""Necromancer 0.9.5: adult-realistic hero study with independently editable outfit.

Starts from original Blender Studio Body Male - Realistic CC0: NOT from any
distorted stylized-body sculpt (0.9.2, 0.9.3, 0.9.4).
No primitive-built anatomy; no rig, no animation, no Unity scene replacement.
"""
import bpy,math,os,json,runpy,random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_095_LOAD_ONLY"]="1"
ref=runpy.run_path(str(ROOT.parent/"studies"/"compare_cc0_male_bases_095.py"),run_name="cc0_realistic_import")
os.environ.pop("NECROMANCER_095_LOAD_ONLY",None)
v=ref["variants"]
body=v["realistic"]["body"]
objects=v["realistic"]["objects"]
original_faces=len(body.data.polygons)
original_vertices=len(body.data.vertices)
assert original_vertices==10582 and original_faces==10590
for o in v["stylized"]["objects"]:
    if o.type=="MESH":o.hide_render=True
body.name="095 | official CC0 realistic adult male • source topology untouched"

def bell(x,m,w):return math.exp(-((x-m)/w)**2)
def mat(name,color,rough=.7,metal=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m

skin=mat("095 | pale ivory skin",(.49,.40,.42),.82)
cloth=mat("095 | charcoal plum textile",(.073,.065,.083),.85)
leather=mat("095 | smoked brown leather",(.13,.078,.064),.72)
leather_edge=mat("095 | worn leather highlights",(.20,.12,.095),.68)
gold=mat("095 | aged dull gold",(.44,.29,.11),.49,.57)
scalp_mat=mat("095 | hair dark roots",(.19,.19,.25),.86)
hair_col=[mat("095 | ash silver main",(.27,.28,.33),.82),
          mat("095 | silver lilac tones",(.35,.33,.40),.82),
          mat("095 | cool graphite underlayers",(.17,.17,.22),.87)]
iris=mat("095 | understated grey eye iris",(.31,.32,.34),.72)
pupil=mat("095 | soft dark pupil",(.085,.081,.094),.66)
body.data.materials.clear()
body.data.materials.append(skin)
bpy.context.view_layer.update()
pworld=[body.matrix_world@v.co for v in body.data.vertices]
nmat=body.matrix_world.to_3x3().inverted_safe().transposed()
normals=[(nmat@v.normal).normalized() for v in body.data.vertices]

# Tailoring directly extracts existing QUAD loops from original realistic
# anatomy. Clothing is separate editable geometry, never an invented body.
def shell(name,accept,material,offset,drape=None,minimum=100):
    faces=[]
    for f in body.data.polygons:
        verts=[pworld[i] for i in f.vertices]
        center=sum(verts,Vector())/len(verts)
        if accept(center,verts):
            faces.append(tuple(f.vertices))
    if len(faces)<minimum:
        raise RuntimeError("Insufficient source faces for "+name+": "+str(len(faces)))
    ids=sorted(set(i for f in faces for i in f))
    lookup={k:i for i,k in enumerate(ids)}
    pts=[]
    for i in ids:
        p=pworld[i].copy()
        p+=normals[i]*(offset+(drape(p,normals[i]) if drape else 0))
        pts.append(p)
    mesh=bpy.data.meshes.new(name+" editable inherited topology")
    mesh.from_pydata(pts,[],[tuple(lookup[i] for i in f) for f in faces])
    mesh.update()
    mesh.materials.append(material)
    for f in mesh.polygons:f.use_smooth=True
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(ob)
    solid=ob.modifiers.new("Actual garment cloth thickness","SOLIDIFY")
    solid.thickness=.003
    sub=ob.modifiers.new("Source quads smoothing","SUBSURF")
    sub.levels=1
    sub.render_levels=1
    print("REALISTIC_SHELL",name,len(mesh.vertices),len(mesh.polygons),flush=True)
    return ob

def pant_drape(p,n):
    z=p.z
    # More fabric clearance below the hips; ankle remains bare.
    return .021*bell(z,.64,.36)+.020*bell(z,.29,.16)+.003*math.sin(z*18+p.x*14)

pants=shell("095 | separate dark trousers",
     lambda c,pts:.155<c.z<1.055 and abs(c.x)<.325 and
                 all(abs(q.x)<.36 for q in pts),
     cloth,.028,pant_drape,minimum=800)
# Conservative lower-leg taper on the extracted cloth only. Keep
# ankle clearance and the source body entirely untouched.
for vertex in pants.data.vertices:
    p=pants.matrix_world@vertex.co
    if .17<p.z<.68 and abs(p.x)>.015:
        t=((.68-p.z)/(.68-.17))**1.3
        sg=1 if p.x>0 else -1
        p.x=sg*.169+(p.x-sg*.169)*(1-.11*t)
        p.y*=1-.075*t
        vertex.co=pants.matrix_world.inverted_safe()@p
pants.data.update()

bracers=[]
for sign,label in ((-1,"left"),(1,"right")):
    b=shell("095 | "+label+" dark leather forearm guard",
       lambda c,pts,sgn=sign: .93<c.z<1.215 and sgn*c.x>.335 and
         all(sgn*p.x>.32 for p in pts),
       leather,.012,minimum=40)
    bracers.append(b)

def cap_mask(c,pts):
    threshold=(1.837 if c.y<-.026 else (1.806 if c.y<.032 else 1.766))
    return c.z>threshold and all(p.z>threshold-.009 for p in pts)
scalp=shell("095 | editable scalp foundation from CC0 head",
            cap_mask,scalp_mat,.003,minimum=60)
# Thin roots avoid a thick helmet rim.
for mod in scalp.modifiers:
    if mod.type=="SOLIDIFY":mod.thickness=.0008

# Hair anchored to the REAL human head geometry. Individual locks are
# curved, with tapered width and overlapping offset lengths rather than
# rigid radial spikes; a hand-authored groom is still pending approval.
rng=random.Random(95)
headpoints=[p.copy() for p in pworld if abs(p.x)<.14 and p.z>1.79]
crown=[p for p in headpoints if p.z>1.855]
fringe=[p for p in headpoints if p.z>1.83 and p.y<-.023]
side=[p for p in headpoints if abs(p.x)>.055 and p.z>1.805]
nape=[p for p in pworld if p.y>.045 and 1.775<p.z<1.86 and abs(p.x)<.13]
if min(len(crown),len(fringe),len(side),len(nape))<20:
    raise RuntimeError("Realistic scalp sampling missing: "+repr((len(crown),len(fringe),len(side))))
hverts=[];hfaces=[];mi=[];hair_count=0
def strand(root,tip,width,mat_index,arc):
    global hair_count
    hair_count+=1
    start=len(hverts)
    travel=tip-root
    lateral=Vector((-travel.y,travel.x,0))
    if lateral.length<1e-5:lateral=Vector((1,0,0))
    lateral.normalize()
    for i in range(7):
        t=i/6
        p=root.lerp(tip,t)+Vector((0,0,arc*4*t*(1-t)))
        p+=lateral*.0025*math.sin(t*math.pi)
        tangent=travel+Vector((0,0,4*arc*(1-2*t)))
        perp=Vector((-tangent.y,tangent.x,0))
        if perp.length<.001:perp=lateral.copy()
        perp.normalize()
        w=(1-t)**.54*width+.00032
        hverts.extend([p-perp*w*.5,p+perp*w*.5])
    for i in range(6):
        hfaces.append((start+2*i,start+2*i+1,start+2*i+3,start+2*i+2))
        mi.append(mat_index)

for k in range(150):
    p=rng.choice(crown).copy()
    p.z+=.003
    direction=Vector((rng.uniform(-.65,-.14),rng.uniform(-.94,-.50),rng.uniform(-.18,-.04))).normalized()
    length=rng.uniform(.027,.058)
    strand(p,p+direction*length,rng.uniform(.012,.020),
           rng.choices((0,1,2),(7,2,2))[0],rng.uniform(.003,.011))
for k in range(55):
    p=rng.choice(fringe).copy()
    p.z+=.003
    direction=Vector((rng.uniform(-.73,-.13),-1.0,rng.uniform(-.34,-.09))).normalized()
    length=rng.uniform(.021,.046)
    strand(p,p+direction*length,rng.uniform(.011,.018),
           rng.choices((0,1,2),(7,3,2))[0],rng.uniform(.001,.006))
for k in range(45):
    p=rng.choice(side).copy()
    p.z+=.003
    s=1 if p.x>0 else -1
    direction=Vector((s*rng.uniform(.08,.4),rng.uniform(-.2,.3),rng.uniform(-1.0,-.4))).normalized()
    length=rng.uniform(.022,.042)
    strand(p,p+direction*length,rng.uniform(.010,.017),
           rng.choices((0,1,2),(7,2,3))[0],rng.uniform(.002,.008))
# Nape: short tapered back locks anchored on the real posterior scalp.
# Without these, the back of the head appears bald from the game camera.
for k in range(90):
    p=rng.choice(nape).copy()
    p.z+=.003
    direction=Vector((rng.uniform(-.18,.18),rng.uniform(.05,.4),
                      rng.uniform(-1.0,-.50))).normalized()
    length=rng.uniform(.022,.050)
    strand(p,p+direction*length,rng.uniform(.012,.021),
           rng.choices((0,1,2),(4,1,6))[0],rng.uniform(.001,.006))

hairmesh=bpy.data.meshes.new("095 | editable ash lilac layered hair ribbons")
hairmesh.from_pydata(hverts,[],hfaces)
hairmesh.update()
for m in hair_col:hairmesh.materials.append(m)
for face,m in zip(hairmesh.polygons,mi):
    face.material_index=m
    face.use_smooth=True
hair=bpy.data.objects.new("095 | short ash silver lilac hairstyle",hairmesh)
bpy.context.scene.collection.objects.link(hair)
solid=hair.modifiers.new("Fine lock thickness","SOLIDIFY")
solid.thickness=.001
print("HAIR_REALISTIC",hair_count,len(hfaces),flush=True)

# Accessories: separate garment objects only, never substituting anatomy.
def mesh_obj(name,points,faces,material):
    data=bpy.data.meshes.new(name+" geometry")
    data.from_pydata(points,[],faces)
    data.update()
    ob=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(ob)
    data.materials.append(material)
    for p in data.polygons:p.use_smooth=True
    return ob
def soft_box(name,at,sizes,material,bevel=.008):
    x,y,z=at
    sx,sy,sz=[v/2 for v in sizes]
    corners=[(x+dx*sx,y+dy*sy,z+dz*sz)
             for dz in (-1,1) for dy in (-1,1) for dx in (-1,1)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),
           (2,3,7,6),(0,2,6,4),(1,5,7,3)]
    obj=mesh_obj(name,corners,faces,material)
    mod=obj.modifiers.new("Leather soft corners","BEVEL")
    mod.width=bevel;mod.segments=3
    obj.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return obj
def ellipse_band(name,z,rx,ry,h,material):
    N=64;verts=[]
    for zz in (z-h/2,z+h/2):
        for i in range(N):
            theta=2*math.pi*i/N
            verts.append((rx*math.cos(theta),ry*math.sin(theta),zz))
    faces=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh_obj(name,verts,faces,material)

belt=ellipse_band("095 | editable dark waist belt",1.044,.204,.145,.049,leather)
buckle=soft_box("095 | aged gold buckle",(0,-.161,1.044),(.073,.012,.051),gold,.003)
inset=soft_box("095 | buckle leather inset",(0,-.170,1.044),(.044,.008,.028),leather,.002)
pouches=[]
for sign,label in ((-1,"left"),(1,"right")):
    pouches.append(soft_box("095 | "+label+" belt pouch",(sign*.191,-.098,1.010),
                   (.076,.085,.112),leather,.013))
    soft_box("095 | "+label+" pouch flap",(sign*.191,-.145,1.040),
             (.080,.011,.039),leather_edge,.003)
    soft_box("095 | "+label+" pouch metal catch",(sign*.191,-.152,1.029),
             (.010,.010,.020),gold,.002)

# Correct eye colour on original realistic CC0 eyeball objects by projection
# to their real surface; avoid floating pasted-on disc placements.
eye_objs=[ob for ob in objects if ob.type=="MESH" and ob!=body and "eye." in ob.name.lower()]
if len(eye_objs)!=2:raise RuntimeError("Expected two CC0 realistic eyes")
def iris_disk(obj,scale,material,name):
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    centre=sum(pts,Vector())/len(pts)
    inv=obj.matrix_world.inverted_safe()
    origin=inv@Vector((centre.x,-.5,centre.z))
    direction=(inv.to_3x3()@Vector((0,1,0))).normalized()
    hit,loc,norm,polygon=obj.ray_cast(origin,direction)
    if not hit:raise RuntimeError("CC0 ocular surface inaccessible")
    front=obj.matrix_world@loc
    cy=front.y-.0025-(.002 if "pupil" in name else 0)
    points=[(centre.x,cy,centre.z)]
    for i in range(24):
        a=2*math.pi*i/24
        points.append((centre.x+scale*math.cos(a),cy,centre.z+scale*math.sin(a)))
    return mesh_obj(name,points,[(0,i+1,(i+1)%24+1) for i in range(24)],material)
for eye in eye_objs:
    suffix="L" if eye.name.endswith(".L") else "R"
    iris_disk(eye,.0055,iris,"095 | "+suffix+" muted steel iris")
    iris_disk(eye,.0025,pupil,"095 | "+suffix+" small pupil")

# Group components for easy future editing.
groups={
    "095 | body CC0 (adult anatomy)": [body,*eye_objs],
    "095 | hair and underlay":[hair,scalp],
    "095 | dark cloth and leather":[pants,*bracers,belt,buckle,inset,*pouches],
}
for name,items in groups.items():
    coll=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for ob in items:
        coll.objects.link(ob)
        for old in list(ob.users_collection):
            if old!=coll:old.objects.unlink(ob)

# 0.9.6 can reuse the official 0.9.5 adult anatomy, garment and accessory
# objects without producing redundant export/renders or altering that stage.
if os.environ.get("NECROMANCER_095_ASSEMBLY_ONLY") != "1":
    metadata={
        "stage":"0.9.5 independently authored adult-realistic CC0 hero clothing study",
        "source":ref["SOURCE"],"license":"CC0-1.0","bundle_version":"1.4.1",
        "base_collection":"Body Male - Realistic",
        "body_vertices":original_vertices,"body_faces":original_faces,
        "body_vertices_after":len(body.data.vertices),"body_faces_after":len(body.data.polygons),
        "outfit_trouser_faces":len(pants.data.polygons),
        "bracer_faces":sum(len(o.data.polygons) for o in bracers),
        "hair_cards":len(hfaces),"hair_locks":hair_count,
        "source_eye_meshes":len(eye_objs),"scalp_faces":len(scalp.data.polygons),
        "comparison_source_topology_identical":False,
        "rigged":False,"unity_character_replaced":False,
        "known_limitations":"No original reference turnaround versioned. Initial hair and cloth are editable approximations; requires artistic approval. Adult anatomy is unmodified original CC0, not prior 0.9.4 face."
    }
    (OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=22
    scene.cycles.use_denoising=True
    scene.render.resolution_x=620
    scene.render.resolution_y=840
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    world=bpy.data.worlds.new("095 | dark neutral protagonist studio")
    world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.15,.15,.17,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.65
    scene.world=world
    for name,xyz,power,size in (
     ("095 Key",(2.2,-3.4,4.1),690,4.1),
     ("095 Fill",(-2.9,-1.2,2.8),300,3.5),
     ("095 Rim",(-1.0,2.7,3.2),460,3.0),
    ):
        light=bpy.data.lights.new(name,"AREA")
        obj=bpy.data.objects.new(name,light)
        scene.collection.objects.link(obj)
        obj.location=xyz
        light.energy=power
        light.shape="DISK"
        light.size=size
    camdata=bpy.data.cameras.new("095 | orthographic realistic hero")
    camera=bpy.data.objects.new("095 | orthographic realistic hero",camdata)
    scene.collection.objects.link(camera)
    scene.camera=camera
    camdata.type="ORTHO"
    camdata.ortho_scale=2.27
    
    # Store original CC0 variants in Blender, but only the realistic hero visible.
    for o in v["stylized"]["objects"]:
        if o.type=="MESH":o.hide_render=True
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_095.blend"))
    for cr in list(scene.objects):
        if cr.type!="CURVE" or cr.hide_render:continue
        bpy.ops.object.select_all(action="DESELECT")
        cr.hide_set(False);cr.select_set(True)
        bpy.context.view_layer.objects.active=cr
        bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")
    for ob in list(scene.objects):
        if (ob.type=="MESH" and not ob.hide_render and
            not ob.name.startswith("095 | stylized")):
            ob.hide_set(False)
            ob.select_set(True)
    if len(bpy.context.selected_objects)<10:
        raise RuntimeError("Unexpectedly few realistic hero FBX meshes")
    bpy.ops.export_scene.fbx(
        filepath=str(OUT/"necromancer_realistic_095.fbx"),
        use_selection=True,object_types={"MESH"},
        apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
    
    def shot(name,where,target,scale,res=(620,840)):
        scene.render.resolution_x,scene.render.resolution_y=res
        camdata.ortho_scale=scale
        camera.location=where
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("hero_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("REALISTIC_HERO_RENDER",name,flush=True)
    for name,where in (
        ("front",(0,-4.6,1.24)),
        ("side",(4.6,0,1.25)),
        ("back",(0,4.6,1.25)),
        ("threequarter",(3.0,-4.0,1.30)),
    ):
        shot(name,where,(0,0,1.0),2.27)
    shot("face_front",(0,-2.8,1.78),(0,0,1.75),.52,(760,760))
    shot("face_threequarter",(2.0,-2.8,1.82),(0,0,1.75),.52,(760,760))
    print("REALISTIC_HERO_COMPLETE",json.dumps(metadata),flush=True)
    