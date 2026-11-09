"""Necromancer Overworld 0.9.3 — targeted CC0 sculpt, layered groom, cloth tailoring.

This stage reuses the real Blender Studio Body Male – Stylized quad topology,
with 0.9.2 as its editable starting point. Clothing is reshaped over those
topological loops rather than replaced by cylinders or spheres. No rig, no
changes in Unity, no replacement of the active player.
"""
import os
import math
import json
import random
import runpy
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_092_BUILD_ONLY"]="1"
stage=runpy.run_path(str(ROOT/"sculpt_character_092.py"),run_name="necromancer_stage_093")
os.environ.pop("NECROMANCER_092_BUILD_ONLY",None)

body=stage["body"]
scalp=stage["scalp"]
trousers=stage["trousers"]
hair=stage["hair"]
bracers=stage["bracers"]
skin=stage["skin"]
base=stage["base"]
source_entry=stage["source_entry"]
bpy.context.view_layer.update()
assert len(body.data.vertices)==stage["original_vertex_count"]==12502
assert len(body.data.polygons)==stage["original_face_count"]==12500

def gauss(v,c,s):
    return math.exp(-((v-c)/s)**2)
def smoother(a,b,v):
    x=max(0.0,min(1.0,(v-a)/(b-a)))
    return x*x*(3.0-2.0*x)
def mat(name,rgb,rough=.65,metal=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    shader=m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value=(*rgb,1)
    shader.inputs["Roughness"].default_value=rough
    shader.inputs["Metallic"].default_value=metal
    return m
def microtexture(m,scale=90,dist=.001,strength=.1):
    nodes=m.node_tree.nodes
    links=m.node_tree.links
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=2.5
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=strength
    bump.inputs["Distance"].default_value=dist
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],nodes.get("Principled BSDF").inputs["Normal"])

skin_new=mat("093 | cool desaturated alabaster skin",(.40,.36,.37),.85)
microtexture(skin_new,82,.0015,.14)
body.data.materials.clear()
body.data.materials.append(skin_new)
cloth=mat("093 | dark violet-charcoal heavy cloth",(.072,.068,.084),.9)
microtexture(cloth,46,.004,.24)
trousers.data.materials.clear()
trousers.data.materials.append(cloth)
root_mat=mat("093 | understated dark roots",(.20,.19,.24),.86)
smoke=mat("093 | silver-ash strands",(.32,.32,.39),.81)
lilac=mat("093 | cool lilac accents",(.29,.265,.36),.82)
shadow=mat("093 | muted graphite hair",(.23,.22,.29),.80)
upperlid=mat("093 | graphite eyelashes",(.15,.13,.16),.89)
iris=mat("093 | desaturated slate irises",(.21,.26,.31),.55)
pupil=mat("093 | small dark pupils",(.028,.029,.039),.51)
sclera=mat("093 | warm soft offwhite sclera",(.50,.48,.46),.63)
gold=mat("093 | aged gold thread",(.32,.22,.095),.68,.35)

# --- ADULT FACIAL IDENTITY: vertex-preserving, localized surface sculpt ---
# The original anatomy remains a single contiguous artist-authored quad mesh.
to_local=body.matrix_world.inverted_safe()
for vert in body.data.vertices:
    p=body.matrix_world@vert.co
    x,y,z=p
    a=abs(x)
    if 1.633<z<1.833 and a<.165:
        # Narrow the childish upper cheek/temples without a pinched jaw.
        p.x*=1-.050*gauss(z,1.755,.044)
        p.x*=1+.115*gauss(z,1.672,.040)*smoother(.035,.105,a)
        # Slightly square the lower jaw and project the chin.
        p.y-=.0065*gauss(z,1.654,.033)*gauss(a,0,.080)
        # Sharper nose bridge and subdued nasolabial/cheek transitions.
        if y<-.040:
            p.y-=.006*gauss(z,1.734,.034)*gauss(a,.014,.026)
            p.y-=.004*gauss(z,1.745,.035)*gauss(a,.074,.028)
            p.y+=.002*gauss(z,1.696,.014)*gauss(a,.052,.033)
        if a>.097 and z<1.805:
            p.x-=math.copysign(.023*gauss(z,1.738,.058)*smoother(.097,.139,a),x)
        # Restrict the large stylized eyelid openings with smooth vertex edits.
        if y<-.065 and .019<a<.094 and 1.680<z<1.771:
            socket=gauss(a,.055,.039)*gauss(z,1.725,.039)*smoother(.045,.115,-y)
            p.z=1.725+(p.z-1.725)*(1-.19*socket)
    if 1.32<z<1.55:
        # Raise the centre of the pectoral mass and strengthen deltoids.
        if y<-.02 and a<.27:
            p.y-=.010*gauss(z,1.442,.082)*gauss(a,.143,.082)
        if .26<a<.42:
            p.x+=math.copysign(.008*gauss(z,1.470,.075),x)
    vert.co=to_local@p
body.data.update()
for poly in body.data.polygons:poly.use_smooth=True

# Reduce the prominent childlike eye proportions on the actual source
# eyeball meshes. Keep both meshes editable and separate from the body.
eye_sources=[]
for ob in base["selected_objects"]:
    if ob.type=="MESH" and ob!=body and ".eye." in ob.name.lower():
        local=ob.matrix_world.inverted_safe()
        pts=[ob.matrix_world@v.co for v in ob.data.vertices]
        centre=sum(pts,Vector())/len(pts)
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            p.x=centre.x+(p.x-centre.x)*.80
            p.z=centre.z+(p.z-centre.z)*.69
            p.y=centre.y+(p.y-centre.y)*.91+.006
            v.co=local@p
        ob.data.materials.clear()
        ob.data.materials.append(sclera)
        ob.data.update()
        eye_sources.append(ob.name)
if len(eye_sources)!=2:
    raise RuntimeError("Expected two imported sculpted CC0 eyes; got %r"%eye_sources)
bpy.context.view_layer.update()

# Reposition the previously constructed iris geometry on the RESCALED eyes.
for ob in bpy.context.scene.objects:
    if ob.type!="MESH" or not ("muted iris" in ob.name or "deep pupil" in ob.name):
        continue
    points=[ob.matrix_world@v.co for v in ob.data.vertices]
    centre=sum(points,Vector())/len(points)
    new_front=stage["front_hit"](centre.x,centre.z)
    if new_front is None:
        raise RuntimeError("No new surface hit for iris "+ob.name)
    is_pupil="deep pupil" in ob.name
    mat_target=pupil if is_pupil else iris
    ob.data.materials.clear()
    ob.data.materials.append(mat_target)
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co
        p.x=centre.x+(p.x-centre.x)*.78
        p.z=centre.z+(p.z-centre.z)*.75
        p.y=new_front.y-(.0052 if is_pupil else .0035)
        v.co=ob.matrix_world.inverted_safe()@p
    ob.data.update()

# Fitted shaded upper eyelids and eyebrows, projected onto actual face.
# These are thin curves, not replacement geometry for the head.
def projected_line(name,coords,material,width=.0018,front_mesh=False):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=width
    curve.bevel_resolution=2
    line=curve.splines.new("POLY")
    line.points.add(len(coords)-1)
    for idx,(point,(x,z)) in enumerate(zip(line.points,coords)):
        t=idx/max(1,len(coords)-1)
        point.radius=.36+.64*math.sin(math.pi*t)
        if front_mesh:
            hit=stage["front_hit"](x,z)
        else:
            src=body.matrix_world.inverted_safe()@Vector((x,-.55,z))
            ray=(body.matrix_world.inverted_safe().to_3x3()@Vector((0,1,0))).normalized()
            ok,location,normal,face=body.ray_cast(src,ray)
            hit=(body.matrix_world@location) if ok else None
        if hit is None:
            raise RuntimeError("Line projection missed face: "+name)
        point.co=(x,hit.y-.0034,z,1)
    ob=bpy.data.objects.new(name,curve)
    bpy.context.scene.collection.objects.link(ob)
    curve.materials.append(material)
    return ob
eyelid_lines=0
for side,side_name in ((-1,"L"),(1,"R")):
    coords=[]
    for i in range(15):
        t=i/14
        coords.append((side*(.031+.046*t),1.7375+.0038*math.sin(math.pi*t)))
    projected_line("093 | "+side_name+" upper eyelid",coords,upperlid,.0014,True)
    eyelid_lines+=1
    brow=[]
    for i in range(15):
        t=i/14
        brow.append((side*(.026+.060*t),1.776+.0044*math.sin(math.pi*t)-.005*t))
    projected_line("093 | "+side_name+" ash eyebrow",brow,shadow,.0019)
    eyelid_lines+=1

# --- GARMENT TAILORING ---
# Flatten the anatomical knee and gastrocnemius lumps while keeping *the
# garment's inherited quad topology*. Regularize x/y cross-sections over the
# lower leg, and fade the operation to zero near hips/ankle.
world_pts=[trousers.matrix_world@v.co for v in trousers.data.vertices]
cache={}
def percentile(vals,p):
    v=sorted(vals)
    return v[int(p*(len(v)-1))]
def source_slice(z,sgn):
    index=(round(z/.040),sgn)
    if index in cache:return cache[index]
    candidates=[p for p in world_pts if p.x*sgn>0 and abs(p.z-z)<.085]
    if len(candidates)<16:
        candidates=[p for p in world_pts if p.x*sgn>0 and abs(p.z-z)<.135]
    if len(candidates)<12:raise RuntimeError("Insufficient leg vertices for cloth cross-section")
    xs=[p.x for p in candidates]
    ys=[p.y for p in candidates]
    centre_x=(percentile(xs,.06)+percentile(xs,.94))*.5
    centre_y=(percentile(ys,.06)+percentile(ys,.94))*.5
    radius_x=max(.02,(percentile(xs,.94)-percentile(xs,.06))*.5)
    radius_y=max(.02,(percentile(ys,.94)-percentile(ys,.06))*.5)
    cache[index]=(centre_x,centre_y,radius_x,radius_y)
    return cache[index]
def lerp_profile(z,table):
    if z<=table[0][0]:return table[0][1]
    for i in range(1,len(table)):
        zl,rl=table[i-1];zr,rr=table[i]
        if z<=zr:
            t=smoother(zl,zr,z)
            return rl*(1-t)+rr*t
    return table[-1][1]
width_profile=[(.15,.082),(.29,.087),(.47,.099),(.62,.106),(.79,.122),(.95,.134)]
depth_profile=[(.15,.082),(.29,.085),(.47,.101),(.62,.117),(.79,.132),(.95,.141)]
tailored=0
for v in trousers.data.vertices:
    p=trousers.matrix_world@v.co
    if p.z>=.970 or p.z<.150 or abs(p.x)<.016:
        continue
    sign=1 if p.x>0 else -1
    cx,cy,rx,ry=source_slice(p.z,sign)
    xr=(p.x-cx)/rx
    yr=(p.y-cy)/ry
    # Taper only the LOWER portion; protect pelvis and crotch shape.
    fade=smoother(.15,.20,p.z)*(1-smoother(.82,.97,p.z))
    ideal_rx=lerp_profile(p.z,width_profile)
    ideal_ry=lerp_profile(p.z,depth_profile)
    # Clamp extreme normalized coordinates before cutting folds.
    xr=max(-1.15,min(1.15,xr))
    yr=max(-1.15,min(1.15,yr))
    natural_fold=.0028*math.sin(25*p.z+8*math.atan2(yr,xr))
    target_x=cx+xr*(ideal_rx+natural_fold)
    target_y=cy+yr*(ideal_ry+natural_fold*.8)
    p.x=p.x*(1-fade)+target_x*fade
    p.y=p.y*(1-fade)+target_y*fade
    v.co=trousers.matrix_world.inverted_safe()@p
    tailored+=1
trousers.data.update()
# Horizontal-only Laplacian relaxation: remove residual source kneecap and
# calf lumps without changing vertex count, garment seams or height.
adj=[set() for _ in trousers.data.vertices]
for e in trousers.data.edges:
    a,b=e.vertices
    adj[a].add(b);adj[b].add(a)
for iteration in range(9):
    original_coords=[v.co.copy() for v in trousers.data.vertices]
    for idx,v in enumerate(trousers.data.vertices):
        z=original_coords[idx].z
        if z<.205 or z>.88 or len(adj[idx])<3:
            continue
        mean=sum((original_coords[k] for k in adj[idx]),Vector())/len(adj[idx])
        weight=.44*gauss(z,.56,.38)
        # x/y smoothing only; all z positions and cuffs remain unchanged.
        v.co.x=original_coords[idx].x*(1-weight)+mean.x*weight
        v.co.y=original_coords[idx].y*(1-weight)+mean.y*weight
trousers.data.update()
print("TAILORED_CLOTH_VERTICES",tailored,"slices",len(cache),"relaxation",9,flush=True)
if tailored<900:raise RuntimeError("Unexpectedly few cloth vertices tailored")

# Replace bright V/arrows with sparse stitched outer seam and hems, following
# the new cloth surface. Curves stay editable in the saved Blender file.
old_gold=[]
for ob in list(bpy.context.scene.objects):
    if ob.type=="CURVE" and ("thigh gold arc" in ob.name or "cuff gold stitch" in ob.name):
        old_gold.append(ob.name)
        bpy.data.objects.remove(ob,do_unlink=True)
def trouser_hit(x,z):
    ok,loc,no,face=trousers.ray_cast(Vector((x,-.65,z)),Vector((0,1,0)))
    if not ok:return None
    return Vector((x,loc.y-.003,z))
def stitch(name,coordinates):
    positions=[trouser_hit(x,z) for x,z in coordinates]
    positions=[p for p in positions if p is not None]
    if len(positions)<6:return None
    cr=bpy.data.curves.new(name,"CURVE")
    cr.dimensions="3D"
    cr.bevel_depth=.0014
    cr.bevel_resolution=2
    line=cr.splines.new("POLY")
    line.points.add(len(positions)-1)
    for point,loc in zip(line.points,positions):point.co=(*loc,1)
    ob=bpy.data.objects.new(name,cr)
    bpy.context.scene.collection.objects.link(ob)
    cr.materials.append(gold)
    return ob
embroidery=0
for sign,label in ((-1,"L"),(1,"R")):
    for offset in (0,.010):
        points=[(sign*(.139+offset+.008*math.sin(i/47*math.pi*1.4)),
                 .335+.53*i/47) for i in range(48)]
        if stitch("093 | "+label+" subdued outer gold thread "+str(offset),points):
            embroidery+=1
    for height in (.183,.202):
        points=[(sign*(.065+.102*i/26),height+.003*math.sin(i/26*math.pi)) for i in range(27)]
        if stitch("093 | "+label+" cuff woven edge "+str(height),points):
            embroidery+=1
print("EMBROIDERY_093",embroidery,flush=True)

# --- GROOM REBUILD ---
# Unlike the previous helmet-with-spikes, keep a dark non-reflective scalp
# extracted from the OFFICIAL head surface and lay curved, tapered locks over it.
scalp.data.materials.clear()
scalp.data.materials.append(root_mat)
for v in scalp.data.vertices:
    # Inset source scalp *slightly* to remove its raised hard-edged cap.
    p=scalp.matrix_world@v.co
    p.z-=.0025
    v.co=scalp.matrix_world.inverted_safe()@p
scalp.data.update()

rng=random.Random(9303)
scalp_points=[scalp.matrix_world@v.co for v in scalp.data.vertices]
crown=[p for p in scalp_points if p.z>1.837]
fringe=[p for p in scalp_points if p.y<-.042 and p.z>1.811]
temples=[p for p in scalp_points if abs(p.x)>.066 and p.z>1.795]
if min(len(crown),len(fringe),len(temples))<10:
    raise RuntimeError("Not enough actual scalp topology for layered hairstyle")
verts=[]
faces=[]
material_indices=[]
strand_count=0
def lock(root,end,width,material_index,arc=.012):
    global strand_count
    strand_count+=1
    start=len(verts)
    travel=end-root
    sideways=Vector((-travel.y,travel.x,0))
    if sideways.length<.001:sideways=Vector((1,0,0))
    sideways.normalize()
    for i in range(7):
        t=i/6
        # Quadratic sweep; strand goes through a small raised crown arc.
        p=root.lerp(end,t)+Vector((0,0,arc*4*t*(1-t)))
        p+=sideways*(.003*math.sin(math.pi*t)*rng.choice((-1,1)))
        tangent=travel+Vector((0,0,4*arc*(1-2*t)))
        cross=Vector((-tangent.y,tangent.x,0))
        if cross.length<.001:cross=sideways.copy()
        cross.normalize()
        w=width*((1-t)**.58)+.00035
        verts.extend([p-cross*w*.5,p+cross*w*.5])
    for i in range(6):
        faces.append((start+2*i,start+2*i+1,start+2*i+3,start+2*i+2))
        material_indices.append(material_index)

for i in range(260):
    root=rng.choice(crown).copy()
    root+=Vector((rng.uniform(-.003,.003),rng.uniform(-.003,.003),.003))
    # From the crown flow predominantly forward and slightly left, tapering
    # naturally over the source skull instead of radiating as rigid spikes.
    direction=Vector((-.29+rng.uniform(-.26,.26),-.82+rng.uniform(-.16,.22),
                      rng.uniform(-.38,-.11))).normalized()
    length=rng.uniform(.040,.086)
    lock(root,root+direction*length,
         rng.uniform(.007,.014),rng.choices((0,1,2),weights=(8,2,3))[0],
         arc=rng.uniform(.003,.011))
for i in range(130):
    root=rng.choice(fringe).copy()+Vector((0,-.001,.003))
    direction=Vector((rng.uniform(-.23,.18),-1.0,rng.uniform(-.72,-.35))).normalized()
    length=rng.uniform(.035,.072)
    lock(root,root+direction*length,
         rng.uniform(.006,.012),rng.choices((0,1,2),weights=(7,2,2))[0],
         arc=rng.uniform(.003,.009))
for i in range(95):
    root=rng.choice(temples).copy()+Vector((0,0,.002))
    sign=-1 if root.x<0 else 1
    direction=Vector((sign*.24,rng.uniform(-.2,.4),rng.uniform(-1,-.54))).normalized()
    length=rng.uniform(.028,.063)
    lock(root,root+direction*length,
         rng.uniform(.005,.011),rng.choices((0,1,2),weights=(6,2,3))[0],
         arc=rng.uniform(.002,.008))
new_mesh=bpy.data.meshes.new("093 | source-scalp anchored layered ash hair")
new_mesh.from_pydata(verts,[],faces)
new_mesh.update()
for m in (smoke,lilac,shadow):new_mesh.materials.append(m)
for poly,mi in zip(new_mesh.polygons,material_indices):
    poly.material_index=mi
    poly.use_smooth=True
old_mesh=hair.data
hair.data=new_mesh
hair.name="093 | layered ash-lilac haircut (editable cards)"
if old_mesh.users==0:bpy.data.meshes.remove(old_mesh)
hair.modifiers.clear()
sol=hair.modifiers.new("Fine double-sided layered card thickness","SOLIDIFY")
sol.thickness=.00075
scalp.name="093 | shaded sculpt-head scalp underlay"
print("GROOM_093",strand_count,len(new_mesh.polygons),flush=True)

# Scene organization: explicit collections allow independent editing.
for label,keywords in (
    ("093 | anatomical sculpture",("body • CC0",)),
    ("093 | hair grooming",("haircut","scalp underlay")),
    ("093 | tailoring",("trousers","bracer","waist leather","belt pouch","buckle","woven edge","gold thread")),
    ("093 | face accents",("eyelid","eyebrow","muted iris","deep pupil")),
):
    group=bpy.data.collections.new(label)
    bpy.context.scene.collection.children.link(group)
    for ob in list(bpy.context.scene.objects):
        if ob.type not in {"MESH","CURVE"}:continue
        if not any(s in ob.name for s in keywords):continue
        group.objects.link(ob)
        for original_group in list(ob.users_collection):
            if original_group!=group:
                original_group.objects.unlink(ob)

# The 0.9.4 sculpt may reuse the fully generated 0.9.3 scene without export.
if os.environ.get("NECROMANCER_093_BUILD_ONLY") != "1":
    # Export and review target should never touch Unity or overwrite 0.9.2 source.
    for ob in bpy.context.scene.objects:
        if ob.name.startswith("092 |"):
            ob.name=ob.name.replace("092 |","093 |",1)
    body.name="093 | Blender Studio Body Male Stylized — adult sculpt CC0"
    bpy.context.view_layer.update()
    metadata={
      "stage":"0.9.3 - adult facial adjustment, eyebrow/eye proportion, layered scalp-anchored groom, trouser silhouette",
      "source":base["SOURCE"],"license":"CC0-1.0","bundle_version":"1.4.1",
      "asset_file":source_entry["file"],"asset_datablock":stage["source_name"],
      "blender_version":bpy.app.version_string,
      "base_vertices":stage["original_vertex_count"],
      "base_faces":stage["original_face_count"],
      "body_vertices_after_sculpt":len(body.data.vertices),
      "body_faces_after_sculpt":len(body.data.polygons),
      "tailored_cloth_vertices":tailored,"trouser_quads":len(trousers.data.polygons),
      "bracer_quads":sum(len(b.data.polygons) for b in bracers),
      "scalp_quads":len(scalp.data.polygons),
      "hair_strand_count":strand_count,"hair_cards":len(new_mesh.polygons),
      "eyebrow_eyelid_curves":eyelid_lines,
      "embroidered_curve_count":embroidery,
      "source_eye_objects":eye_sources,
      "rigged":False,"unity_character_replaced":False,
      "known_limitations":"Model still requires direct comparison with unversioned approved reference. Hair cards, cloth silhouette and face remain generated drafts; not hand sculpted production art."
    }
    (OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    (OUT/"asset_catalog.json").write_text(json.dumps(base["entries"],indent=2),encoding="utf-8")
    
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=20
    scene.cycles.use_denoising=True
    scene.render.resolution_x=620
    scene.render.resolution_y=840
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    world=bpy.data.worlds.new("093 | sculpt review studio")
    world.use_nodes=True
    bg=world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(.16,.16,.18,1)
    bg.inputs["Strength"].default_value=.6
    scene.world=world
    for name,pos,power,size in (
        ("093 key",(2.2,-3.5,4),520,4.4),
        ("093 fill",(-2.8,-1.1,3),270,3.7),
        ("093 rim",(-1.0,2.7,3.0),430,3.1),
    ):
        ld=bpy.data.lights.new(name,"AREA")
        ob=bpy.data.objects.new(name,ld)
        scene.collection.objects.link(ob)
        ob.location=pos
        ld.energy=power
        ld.shape="DISK"
        ld.size=size
    camdata=bpy.data.cameras.new("093 | orthographic review camera")
    camera=bpy.data.objects.new("093 | orthographic review camera",camdata)
    scene.collection.objects.link(camera)
    scene.camera=camera
    camdata.type="ORTHO"
    camdata.ortho_scale=2.23
    
    # Save original editable curves/hair, BEFORE temporary FBX conversion.
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_character_093.blend"))
    for cr in [ob for ob in bpy.context.scene.objects if ob.type=="CURVE" and not ob.hide_render]:
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
    assert len(bpy.context.selected_objects)>=8
    bpy.ops.export_scene.fbx(
        filepath=str(OUT/"necromancer_character_093.fbx"),
        use_selection=True,object_types={"MESH"},
        apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
    
    def render(name,loc,target,scale,res=(620,840)):
        scene.render.resolution_x=res[0]
        scene.render.resolution_y=res[1]
        camdata.ortho_scale=scale
        camera.location=loc
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("character_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("RENDER_093",name,scene.render.filepath,flush=True)
    
    for name,loc in (
        ("front",(0,-4.6,1.25)),
        ("side",(4.6,0,1.25)),
        ("back",(0,4.6,1.25)),
        ("threequarter",(3.0,-4.0,1.30)),
    ):
        render(name,loc,(0,0,1.0),2.23)
    render("face_front",(0,-2.6,1.77),(0,0,1.75),.49,(760,760))
    render("face_threequarter",(1.5,-2.3,1.8),(0,0,1.75),.50,(760,760))
    render("trousers_detail",(1.3,-3.0,.73),(0,0,.60),.99,(760,760))
    print("SUCCESS_093",json.dumps(metadata),flush=True)
    