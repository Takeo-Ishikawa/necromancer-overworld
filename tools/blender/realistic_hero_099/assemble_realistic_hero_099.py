"""Necromancer v0.9.9: smooth garment seams & subtle pelvic fabric refinement.

Source is original CC0 Realistic Male (10,582 verts / 10,590 faces);
never edit body or eyes. Continue from validated single-component garment
v0.9.8. The 0.9.8 jagged vertex-chasing seams remain hidden in the
editable Blend; use surface-raycast continuous seams instead.
"""
import os,runpy,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_098_BUILD_ONLY"]="1"
stage=runpy.run_path(str(ROOT.parent/"realistic_hero_098"/"assemble_realistic_hero_098.py"),run_name="adult_cc0_realistic_098")
os.environ.pop("NECROMANCER_098_BUILD_ONLY",None)
body=stage["body"]
eyes=stage["eyes"]
trousers=stage["trousers"]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2
digest=stage["digest"]
before=digest(body)
eyes_before=[digest(o) for o in eyes]

def smooth(a,b,v):
    t=max(0.0,min(1.0,(v-a)/(b-a)))
    return t*t*(3-2*t)
def bell(z,c,w):
    return math.exp(-((z-c)/w)**2)

# 0.9.8 already created a continuous 1086-quad, independently editable
# garment with base and tailored shape keys. Add a *third* shape key that
# smooths transverse pelvis relief rather than pinching the groin.
source_key=trousers.data.shape_keys.key_blocks[-1]
source_key.value=1
pelvic=trousers.shape_key_add(name="099 | Woven fabric front drape",from_mix=True)
for key in trousers.data.shape_keys.key_blocks:
    key.value=0
pelvic.value=1

old=[v.co.copy() for v in pelvic.data]
neighbors=[set() for _ in old]
for edge in trousers.data.edges:
    i,j=edge.vertices
    neighbors[i].add(j)
    neighbors[j].add(i)
# A local Laplacian filter is applied ONLY to x/y within a masked pelvis
# region: no broad body reshaping, no visible upper-thigh rings.
modified=set()
for _ in range(7):
    prev=[v.co.copy() for v in pelvic.data]
    for i,p in enumerate(prev):
        z=p.z
        if not .75<z<1.025 or len(neighbors[i])<3:
            continue
        # front is negative y in the source Blender Studio coordinates
        front=smooth(.005,.090,-p.y)
        vertical=smooth(.76,.82,z)*(1-smooth(.985,1.025,z))
        centre=bell(abs(p.x),.10,.125)
        weight=.29*front*vertical*centre
        if weight<.002:
            continue
        average=sum((prev[j] for j in neighbors[i]),Vector())/len(neighbors[i])
        pelvic.data[i].co.x=p.x+(average.x-p.x)*weight
        pelvic.data[i].co.y=p.y+(average.y-p.y)*weight
        modified.add(i)

# Slightly increase textile stand-off on the frontal anatomical crease, but
# nowhere near the massive silhouette changes rejected in v0.9.6.
for i,v in enumerate(pelvic.data):
    p=v.co
    z=p.z
    if .77<z<.97:
        front=smooth(.035,.11,-p.y)
        centre=bell(abs(p.x),.047,.077)
        v.co.y-=.0035*front*centre*bell(z,.855,.09)
        if front*centre>.09:modified.add(i)
trousers.data.update()
if len(modified)<90:
    raise RuntimeError("Pelvis fabric refinement mask too small: "+str(len(modified)))

# Hide original 0.9.8 point-to-point seams, which zigzagged between vertices.
for seam in stage["seams"]:
    seam.hide_render=True
    seam.hide_set(True)

# Surface-following seam: send a ray from outside each leg at fixed y=0,
# choose the actual garment's *evaluated shape-key surface* as hit point.
# Unlike nearest-vertex sampling, x/y vary continuously with z.
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
obj=trousers.evaluated_get(deps)
inv=obj.matrix_world.inverted_safe()
normal_matrix=obj.matrix_world.to_3x3().inverted_safe().transposed()
seam_mat=stage["stitchmat"]
seam_mat.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=.92

def make_curve(name,coords):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.bevel_depth=.00064
    curve.bevel_resolution=2
    spline=curve.splines.new("BEZIER")
    spline.bezier_points.add(len(coords)-1)
    for i,(bp,p) in enumerate(zip(spline.bezier_points,coords)):
        bp.co=p
        bp.handle_left_type="AUTO"
        bp.handle_right_type="AUTO"
        bp.radius=.75
    curve.materials.append(seam_mat)
    out=bpy.data.objects.new(name,curve)
    bpy.context.scene.collection.objects.link(out)
    return out

seams=[]
samples_per_side=82
max_segment_jump=0.0
rays_hit=0
for sign,name in ((-1,"left"),(1,"right")):
    guide=[]
    for k in range(samples_per_side):
        z=.245+(.965-.245)*k/(samples_per_side-1)
        # Search the outer cloth along X at multiple Y offsets; trouser
        # knees do not stay centered at world Y=0 throughout the full leg.
        inward=Vector((-sign,0,0))
        hit=False
        for y in (0,-.025,.025,-.05,.05,-.08,.08,-.12,.12,-.17,.17,-.24,.24):
            origin=Vector((sign*.50,y,z))
            found,loc,norm,face=obj.ray_cast(
                inv@origin,(inv.to_3x3()@inward).normalized())
            if found:
                hit=True
                break
        if not hit:
            # Project onto actual cloth surface as fallback for stations
            # without a straight horizontal intersection.
            found,loc,norm,face=obj.closest_point_on_mesh(
                inv@Vector((sign*.18,0,z)))
            if not found or sign*(obj.matrix_world@loc).x<.035:
                raise RuntimeError("Garment projection failed on "+name+" z="+str(z))
        rays_hit+=1
        normal=(normal_matrix@norm).normalized()
        p=obj.matrix_world@loc+normal*.00115
        guide.append(p)
    # Preserve the exact surface hit for each station, with a C2-ish
    # Bézier spline through sparse samples; no polyline of jagged vertices.
    # Every point is actually raycast on evaluated cloth, no invented hoop.
    reduced=[guide[i] for i in range(0,len(guide),5)]
    if reduced[-1]!=guide[-1]:reduced.append(guide[-1])
    max_segment_jump=max(max_segment_jump,max((a-b).length for a,b in zip(reduced,reduced[1:])))
    seams.append(make_curve("099 | "+name+" smooth surface seam",reduced))

if len(seams)!=2 or rays_hit!=164:
    raise RuntimeError("Missing side garment seams")
if max_segment_jump>.10:
    raise RuntimeError("Anomalously large seam jump "+str(max_segment_jump))

coll=bpy.data.collections.new("099 | anatomically untouched, refined cloth seams")
bpy.context.scene.collection.children.link(coll)
for o in seams:
    coll.objects.link(o)
    for c in list(o.users_collection):
        if c!=coll:c.objects.unlink(o)

assert digest(body)==before
assert [digest(e) for e in eyes]==eyes_before

# Reusable finished geometry and seam scene for v0.9.10 (without older exports).
if os.environ.get('NECROMANCER_099_BUILD_ONLY') != '1':
    metadata={
     "stage":"0.9.9 continuous cloth pelvis smoothing and surface raycast cubic side seams",
     "license":"CC0-1.0","bundle_version":"1.4.1","base_collection":"Body Male - Realistic",
     "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
     "body_digest_before":before,"body_digest_after":digest(body),
     "eye_digests_unchanged":[digest(e) for e in eyes]==eyes_before,
     "garment_faces":len(trousers.data.polygons),
     "garment_vertices":len(trousers.data.vertices),
     "garment_components":stage["components"],
     "garment_shape_keys":[k.name for k in trousers.data.shape_keys.key_blocks],
     "pelvic_vertices_refined":len(modified),
     "seam_curve_count":len(seams),
     "seam_total_raycast_hits":rays_hit,
     "max_seam_control_segment_m":round(max_segment_jump,6),
     "old_zigzag_seams_hidden":all(o.hide_render for o in stage["seams"]),
     "old_disconnected_garments_hidden":all(o.hide_render for o in stage["hidden_loft"]),
     "uv_layers":len(trousers.data.uv_layers),
     "rigged":False,"unity_character_replaced":False,
     "known_limitations":"CC0 derived continuous garment remains a body-surface approximation, not pattern-cut cloth. Side seams are guide curves, not finished stitch topology."
    }
    (OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print("V099_VALIDATE",json.dumps(metadata),flush=True)
    
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=23
    scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    world=bpy.data.worlds.new("099 | neutral review studio")
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.15,.175,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65
    scene.world=world
    for name,position,power,size in (
     ("099 Key",(2.2,-3.5,4.2),650,4.1),
     ("099 Fill",(-2.8,-1.3,2.6),280,3.6),
     ("099 Rim",(-1.1,2.7,3.4),430,3.3)
    ):
        light=bpy.data.lights.new(name,"AREA")
        ob=bpy.data.objects.new(name,light)
        scene.collection.objects.link(ob)
        ob.location=position
        light.energy=power
        light.shape="DISK"
        light.size=size
    cdata=bpy.data.cameras.new("099 | orthographic review")
    camera=bpy.data.objects.new("099 | orthographic review",cdata)
    scene.collection.objects.link(camera)
    scene.camera=camera
    cdata.type="ORTHO"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_099.blend"))
    for o in list(scene.objects):
        if o.type!="CURVE" or o.hide_render:continue
        bpy.ops.object.select_all(action="DESELECT")
        o.hide_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")
    for o in list(scene.objects):
        if o.type=="MESH" and not o.hide_render and not o.name.startswith("095 | stylized"):
            o.hide_set(False)
            o.select_set(True)
    assert len(bpy.context.selected_objects)>18
    bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_realistic_099.fbx"),
        use_selection=True,object_types={"MESH"},
        apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
    
    def shot(name,where,target,scale,res=(640,840)):
        scene.render.resolution_x,scene.render.resolution_y=res
        cdata.ortho_scale=scale
        camera.location=where
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("hero_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("V099_RENDER",name,flush=True)
    for name,loc in (
     ("front",(0,-4.6,1.24)),
     ("side",(4.6,0,1.25)),
     ("back",(0,4.6,1.25)),
     ("threequarter",(3,-4,1.30))
    ):shot(name,loc,(0,0,1),2.27)
    shot("face_threequarter",(2,-2.8,1.82),(0,0,1.75),.52,(760,760))
    shot("trousers_front",(0,-3,.70),(0,0,.66),1.16,(760,760))
    shot("trousers_side",(2.4,-.7,.7),(0,0,.64),1.16,(760,760))
    shot("seam_side",(2.4,-.05,.67),(0,0,.65),1.06,(760,760))
    print("SUCCESS_099",flush=True)
    