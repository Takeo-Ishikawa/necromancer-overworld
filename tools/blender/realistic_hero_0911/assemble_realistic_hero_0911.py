"""Necromancer Overworld v0.9.11 — fitted forearm leather cuffs and cloth drape.

Progressive study built from v0.9.10. Refines the OPEN EDGES of the genuine
CC0-derived forearm guards, replacing noisy scattered leather dashes with
small, measured, directly mesh-anchored rim panels and stitches. Smooths
only an independent garment shape key over the trouser pelvis. No CC0 body
or eyes are touched; Unity protagonist, rig and animations are unchanged.
"""
import os,runpy,bpy,math,json,statistics
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_0910_BUILD_ONLY"]="1"
p=runpy.run_path(str(ROOT.parent/"realistic_hero_0910"/"assemble_realistic_hero_0910.py"),
                 run_name="preserved_adult_0910_stage")
os.environ.pop("NECROMANCER_0910_BUILD_ONLY",None)
body=p["body"]
eyes=p["eyes"]
trousers=p["trousers"]
digest=p["digest"]
body_hash=digest(body)
eye_hashes=[digest(e) for e in eyes]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2

def smooth(a,b,v):
    t=max(0.0,min(1.0,(v-a)/(b-a)))
    return t*t*(3-2*t)
def gauss(v,c,w):
    return math.exp(-((v-c)/w)**2)
def make_mat(name,color,rough=.84):
    material=bpy.data.materials.new(name)
    material.use_nodes=True
    material.diffuse_color=(*color,1)
    bs=material.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return material
binding=make_mat("0911 | worn charcoal folded guard leather",(.073,.062,.073),.85)
binding_stitch=make_mat("0911 | subtle bone-grey stitching",(.225,.193,.180),.86)
small_bronze=make_mat("0911 | smoke-dark bronze belt keepers",(.195,.151,.101),.68)

def mesh_obj(name,verts,faces,material):
    data=bpy.data.meshes.new(name+" mesh")
    data.from_pydata(verts,[],faces)
    data.update()
    data.materials.append(material)
    obj=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(obj)
    for f in data.polygons:f.use_smooth=True
    return obj

def stroke(name,coords,material,bevel=.00055):
    c=bpy.data.curves.new(name,"CURVE")
    c.dimensions="3D"
    c.resolution_u=8
    c.bevel_depth=bevel
    c.bevel_resolution=2
    sp=c.splines.new("POLY")
    sp.points.add(len(coords)-1)
    for cp,pnt in zip(sp.points,coords):
        cp.co=(pnt.x,pnt.y,pnt.z,1)
    c.materials.append(material)
    obj=bpy.data.objects.new(name,c)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# The previous 16 little stitches had irregular placement. Keep them
# editable but hidden so a comparative Blender view remains possible.
old_stitches=p["bracer_stitches"]
for old in old_stitches:
    old.hide_render=True
    old.hide_set(True)

# Physically anchored top/bottom leather bindings, derived from boundary
# edges of the same two CC0-derived forearm GUARD shells (never from arms).
guards=p["original_guards"]
if len(guards)!=2:raise RuntimeError("Two original forearm guards expected")
rim_objs=[]
new_stitches=[]
edge_counts={}
max_rim_edge=0
max_stitch=0
for guard in guards:
    matrix=guard.matrix_world
    nm=matrix.to_3x3().inverted_safe().transposed()
    verts=[matrix@v.co for v in guard.data.vertices]
    normals=[(nm@v.normal).normalized() for v in guard.data.vertices]
    zmin=min(v.z for v in verts)
    zmax=max(v.z for v in verts)
    side="left" if statistics.mean(v.x for v in verts)<0 else "right"

    boundaries=Counter()
    for face in guard.data.polygons:
        ids=list(face.vertices)
        for ia,ib in zip(ids,ids[1:]+ids[:1]):
            boundaries[tuple(sorted((ia,ib)))]+=1

    side_counts={}
    for placement,target,delta in (
        ("wrist",zmin,1),
        ("forearm",zmax,-1)
    ):
        selected=[]
        for (ia,ib),freq in boundaries.items():
            if freq!=1:continue
            a,b=verts[ia],verts[ib]
            mid=(a+b)*.5
            length=(a-b).length
            if (abs(mid.z-target)>.042 or abs(a.z-b.z)>.023
                or length<.001 or length>.040):
                continue
            # Rim panel is copied from the actual seam of the GUARD
            # and inset by 6 mm along its longitudinal direction.
            n=(normals[ia]+normals[ib]).normalized()
            selected.append((ia,ib,length,mid,n))
        if len(selected)<5:
            raise RuntimeError("Insufficient cuff boundary edges for "+side+
                               " "+placement+": "+str(len(selected)))
        side_counts[placement]=len(selected)

        panel_verts=[]
        panel_faces=[]
        selected.sort(key=lambda e:math.atan2(e[3].y,e[3].x-
                 statistics.mean(v.x for v in verts)))
        for ia,ib,length,mid,n in selected:
            a,b=verts[ia],verts[ib]
            # Barely raised leather folded binding lies over the actual
            # bracer surface. 6-mm width and no metallic decorations.
            off=n*.0017
            inset=Vector((0,0,delta*.0060))
            index=len(panel_verts)
            panel_verts.extend([a+off,b+off,b+off+inset,a+off+inset])
            panel_faces.append((index,index+1,index+2,index+3))
            max_rim_edge=max(max_rim_edge,length)
        rim_objs.append(mesh_obj("0911 | "+side+" "+placement+
                                 " guard edge binding",
                                 panel_verts,panel_faces,binding))

        # Equidistant tiny stitches attach to alternate bound edge
        # elements. Unlike previous arbitrary meshes, these are isolated
        # 4mm surface-aligned marks whose end points share local normals.
        for k,(ia,ib,length,mid,n) in enumerate(selected):
            if k%4!=0:continue
            offset=n*.0028
            a=mid+offset+Vector((0,0,delta*.001))
            b=mid+offset+Vector((0,0,delta*.005))
            dash=(a-b).length
            max_stitch=max(max_stitch,dash)
            new_stitches.append(stroke(
                "0911 | "+side+" "+placement+" 4mm stitch %02d"%k,
                [a,b],binding_stitch,.00046))
    edge_counts[side]=side_counts

if len(rim_objs)!=4 or len(new_stitches)<8 or max_stitch>.006:
    raise RuntimeError("Forearm leather cuff edge protection failed")
if max_rim_edge>.04:
    raise RuntimeError("Oversized leather binding edge")

# Real render inspection rejected the protruding boundary panels:
# even source-anchored 6mm strips followed the jagged cloth perimeter and
# produced pointed projections near the wrist. Keep the editable prototype
# hidden; use a dark *face material border on the existing guard shell*.
for ob in [*rim_objs,*new_stitches]:
    ob.hide_render=True
    ob.hide_set(True)
visible_edge_faces=0
guard_face_counts={}
face_binding=make_mat("0911 | integrated leather cuff face border",
                      (.058,.051,.060),.92)
for guard in guards:
    slot=len(guard.data.materials)
    guard.data.materials.append(face_binding)
    gverts=[guard.matrix_world@v.co for v in guard.data.vertices]
    lower=min(v.z for v in gverts)
    upper=max(v.z for v in gverts)
    used=0
    for f in guard.data.polygons:
        pts=[gverts[j] for j in f.vertices]
        z=sum(v.z for v in pts)/len(pts)
        if z<lower+.028 or z>upper-.028:
            f.material_index=slot
            used+=1
    guard_face_counts[guard.name]=used
    visible_edge_faces+=used
if visible_edge_faces<25:
    raise RuntimeError("Too few integrated leather binding polygons")


# Re-evaluate the same genuinely connected pants. The fourth optional
# shape key is a small weighted Y-only Laplacian relaxation at the frontal
# pelvic cloth surface, not a new body sculpt. Changes are reversible.
source=trousers.data.shape_keys.key_blocks[-1]
for k in trousers.data.shape_keys.key_blocks:k.value=0
source.value=1
drape=trousers.shape_key_add(name="0911 | Relaxed pelvic fabric",from_mix=True)
for k in trousers.data.shape_keys.key_blocks:k.value=0
drape.value=1
neighbors=[set() for v in trousers.data.vertices]
for e in trousers.data.edges:
    i,j=e.vertices
    neighbors[i].add(j)
    neighbors[j].add(i)

changed=set()
for _ in range(5):
    previous=[v.co.copy() for v in drape.data]
    for i,v in enumerate(previous):
        if len(neighbors[i])<3:continue
        z=v.z
        if not .765<z<1.00:continue
        frontal=smooth(.045,.125,-v.y)
        mask=frontal*gauss(abs(v.x),.06,.11)*smooth(.765,.805,z)*(1-smooth(.96,1.0,z))
        if mask<.015:continue
        avg=sum((previous[k].y for k in neighbors[i]),0.0)/len(neighbors[i])
        drape.data[i].co.y=v.y+.24*mask*(avg-v.y)
        changed.add(i)

# Very slight fabric extra clearance around crotch, tapered to zero at
# waistband and knees. Avoid the pronounced groin bulge of prior attempts.
for i,vert in enumerate(drape.data):
    q=vert.co
    z=q.z
    if .79<z<.94 and q.y<-.05:
        factor=gauss(abs(q.x),.06,.09)*gauss(z,.86,.065)
        if factor>.08:
            q.y-=.0018*factor
            changed.add(i)
trousers.data.update()
if len(changed)<35:
    raise RuntimeError("Too few independently tailored garment vertices")
if len(trousers.data.polygons)!=1086:
    raise RuntimeError("Lost continuous garment topology")

# Minimal retention keepers on the existing belt, without changing waist
# anatomy or making large ornamental metal shapes.
belt_loops=[]
for sg,label in ((-1,"L"),(1,"R")):
    x=sg*.120
    y=-.147
    v=[(x+dx*.009,y+dy*.004,z) for z in (1.022,1.069)
       for dy in (-1,1) for dx in (-1,1)]
    f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),
       (2,3,7,6),(0,2,6,4),(1,5,7,3)]
    belt_loops.append(mesh_obj("0911 | "+label+" restrained belt keeper",
                               v,f,binding))
    # Bronze buckle remains from source model; no added shiny jewelry.

coll=bpy.data.collections.new("0911 | realistic leather cuffs and garment finishing")
bpy.context.scene.collection.children.link(coll)
for ob in [*rim_objs,*new_stitches,*belt_loops]:
    coll.objects.link(ob)
    for old in list(ob.users_collection):
        if old!=coll:old.objects.unlink(ob)

# Anatomic integrity gates, body and ocular meshes byte-for-byte same.
assert digest(body)==body_hash
assert [digest(e) for e in eyes]==eye_hashes
assert all(o.hide_render for o in old_stitches)
assert p["prior"]["stage"]["components"]==1

# Import-only mode for optional downstream revision; default 0.9.11 unchanged.
if os.environ.get('NECROMANCER_0911_BUILD_ONLY') != '1':
    metadata={
     "stage":"0.9.11 bounded bracer-edge leather binding and reversible pelvic drape",
     "license":"CC0-1.0","bundle_version":"1.4.1",
     "base_collection":"Body Male - Realistic",
     "body_vertices":len(body.data.vertices),
     "body_faces":len(body.data.polygons),
     "body_hash_before":body_hash,"body_hash_after":digest(body),
     "original_eye_hashes_unchanged":[digest(e) for e in eyes]==eye_hashes,
     "connected_trouser_components":p["prior"]["stage"]["components"],
     "trouser_vertices":len(trousers.data.vertices),
     "trouser_faces":len(trousers.data.polygons),
     "trouser_shape_keys":[k.name for k in trousers.data.shape_keys.key_blocks],
     "pelvis_vertices_adjusted":len(changed),
     "original_bracer_count":len(guards),
     "leather_binding_objects":len(rim_objs),
     "binding_edge_counts":edge_counts,
     "max_binding_edge_length_m":round(max_rim_edge,5),
     "visible_guard_material_border_faces":visible_edge_faces,
     "guard_face_border_counts":guard_face_counts,
     "rejected_raised_rim_hidden":all(o.hide_render for o in [*rim_objs,*new_stitches]),
      "new_guard_stitches":len(new_stitches),
     "max_guard_stitch_length_m":round(max_stitch,5),
     "old_guard_stitches_hidden":all(o.hide_render for o in old_stitches),
     "new_belt_keepers":len(belt_loops),
     "pouch_bodies_preserved":len(p["pouch_bodies"]),
     "rigged":False,"unity_character_replaced":False,
     "known_limitations":"Source bracer-boundary quads may still need artistic tailoring; no material UV production, full rig or facial reference. Original body meshes remain untouched."
    }
    (OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print("V0911_METADATA",json.dumps(metadata),flush=True)
    
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=22
    scene.cycles.use_denoising=True
    scene.render.image_settings.file_format="PNG"
    scene.render.resolution_percentage=100
    world=bpy.data.worlds.new("0911 | charcoal professional model review")
    world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.15,.15,.17,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.68
    scene.world=world
    for name,pos,power,size in (
     ("0911 | Key",(2.2,-3.5,4.2),630,4),
     ("0911 | Fill",(-2.8,-1.3,2.6),300,3.7),
     ("0911 | Rim",(-1.1,2.7,3.4),430,3.3)
    ):
        light=bpy.data.lights.new(name,"AREA")
        ob=bpy.data.objects.new(name,light)
        scene.collection.objects.link(ob)
        ob.location=pos
        light.energy=power
        light.shape="DISK"
        light.size=size
    camdata=bpy.data.cameras.new("0911 | orthographic technical inspection")
    camera=bpy.data.objects.new("0911 | orthographic technical inspection",camdata)
    scene.collection.objects.link(camera)
    scene.camera=camera
    camdata.type="ORTHO"
    
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_0911.blend"))
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
    assert len(bpy.context.selected_objects)>22
    bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_realistic_0911.fbx"),
        use_selection=True,object_types={"MESH"},
        apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
    
    def render(name,pos,target,scale,res=(640,840)):
        scene.render.resolution_x,scene.render.resolution_y=res
        camdata.ortho_scale=scale
        camera.location=pos
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("hero_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("RENDER_0911",name,flush=True)
    for name,pos in (
     ("front",(0,-4.6,1.24)),
     ("side",(4.6,0,1.25)),
     ("back",(0,4.6,1.25)),
     ("threequarter",(3,-4,1.30))
    ):render(name,pos,(0,0,1),2.27)
    render("bracer_front",(0,-2.3,1.11),(0,0,1.09),.80,(760,760))
    render("bracer_threequarter",(2,-2.5,1.10),(.45,0,1.10),.86,(760,760))
    render("pelvic_front",(0,-2.8,1.01),(0,0,.99),.93,(760,760))
    render("belt_details",(1.5,-2.8,1.04),(0,0,1.045),.78,(760,760))
    print("SUCCESS_0911",flush=True)
    