"""Necromancer Overworld v0.9.14 — rear leather gussets and 3D trouser pattern study.

Build upon v0.9.13 three-panel bracers and CC0 realistic adult base.
Add TWO independent, subdued leather backing gussets behind the real
rear lacing gap; retain all six panel meshes and 16 measured cords.
Create FOUR independent curved 3D trouser leg-pattern mockups plus a
waistband, all HIDDEN and EXCLUDED from the character's FBX. The existing
single connected active trousers remain unchanged and visible.
Body and original eyes are strictly unchanged. No Unity modifications.
"""
import os,runpy,math,json,statistics
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_0913_BUILD_ONLY"]="1"
previous=runpy.run_path(str(ROOT.parent/"realistic_hero_0913"/"assemble_realistic_hero_0913.py"),
    run_name="validated_0913_cc0_adult_scene")
os.environ.pop("NECROMANCER_0913_BUILD_ONLY",None)
body=previous["body"]
eyes=previous["eyes"]
trousers=previous["trousers"]
digest=previous["digest"]
body_before=digest(body)
eye_before=[digest(o) for o in eyes]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2
assert len(previous["panels"])==6
assert len(previous["back_laces"])==16
assert len(previous["source_guards"])==2

def make_mat(name,color,rough=.87):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m
inner_leather=make_mat("0914 | inner oxblood leather gusset",(.086,.067,.070),.94)
inner_edge=make_mat("0914 | dark fold at rear slit",(.049,.041,.045),.95)
fabric_mock=make_mat("0914 | grey violet independent trouser drape study",(.112,.106,.125),.93)
fabric_back=make_mat("0914 | shaded grey independent back trouser mock",(.078,.074,.091),.94)
waist_mat=make_mat("0914 | waistband mockup study",(.137,.119,.140),.9)

def make_mesh(name,verts,faces,materials):
    me=bpy.data.meshes.new(name+" | dedicated pattern mesh")
    me.from_pydata(verts,[],faces)
    me.update()
    for m in materials:me.materials.append(m)
    for face in me.polygons:face.use_smooth=True
    ob=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(ob)
    return ob
def collect(ob,coll):
    coll.objects.link(ob)
    for c in list(ob.users_collection):
        if c!=coll:c.objects.unlink(ob)
def hide(ob):
    ob.hide_render=True
    ob.hide_set(True)

gusset_collection=bpy.data.collections.new("0914 | backed forearm rear lacing gussets")
bpy.context.scene.collection.children.link(gusset_collection)
gussets=[]
gap_widths=[]
radial_clearances=[]
RADIAL=previous["RADIAL"]
RINGS=previous["RINGS"]
start_angle=previous["BACK_NEAR"][1]
end_angle=previous["BACK_FAR"][0]
assert abs((end_angle-start_angle)-.116)<.0001

# An inside, separately editable leather tongue behind the exposed X-lacing,
# following true 0.9.12 guard section positions. This leaves all three
# visible outer leather panels, and the full 16 short laces, intact.
for original in previous["source_guards"]:
    raw=[original.matrix_world@v.co for v in original.data.vertices]
    side="left" if statistics.mean(p.x for p in raw)<0 else "right"
    def sample(j,angle):
        t=((angle%(2*math.pi))/(2*math.pi))*RADIAL
        k=int(t)
        alpha=t-k
        return raw[j*RADIAL+k%RADIAL].lerp(raw[j*RADIAL+(k+1)%RADIAL],alpha)

    columns=9
    points=[]
    for j in range(RINGS):
        centre=(sample(j,0)+sample(j,math.pi))*.5
        for k in range(columns):
            # Backing is wider than the slit by 0.06 rad on each side,
            # and inset into the guard rather than outward as a raised plate.
            theta=(start_angle-.060)+((end_angle-start_angle)+.120)*k/(columns-1)
            surface=sample(j,theta)
            inset=.0030
            q=surface+(centre-surface).normalized()*inset
            points.append(q)
            radial_clearances.append((surface-q).length)
    faces=[]
    for j in range(RINGS-1):
        for k in range(columns-1):
            a=j*columns+k
            faces.append((a,a+1,a+columns+1,a+columns))
    gusset=make_mesh("0914 | "+side+" recessed leather lining under X laces",
                    points,faces,[inner_leather,inner_edge])
    collect(gusset,gusset_collection)
    for face in gusset.data.polygons:
        k=face.index%(columns-1)
        face.material_index=1 if k in (0,columns-2) else 0
    uv=gusset.data.uv_layers.new(name="0914 | individual lining UV")
    for poly in gusset.data.polygons:
        for loop in poly.loop_indices:
            vid=gusset.data.loops[loop].vertex_index
            j,k=divmod(vid,columns)
            uv.data[loop].uv=(k/(columns-1),j/(RINGS-1))
    solid=gusset.modifiers.new("0914 | soft recessed lining thickness","SOLIDIFY")
    solid.thickness=.0013
    solid.offset=0
    gussets.append(gusset)

    for j in (0,RINGS//2,RINGS-1):
        left=sample(j,start_angle)
        right=sample(j,end_angle)
        gap_widths.append((right-left).length)

if len(gussets)!=2 or any(len(o.data.vertices)!=RINGS*9 or
                              len(o.data.polygons)!=(RINGS-1)*8 for o in gussets):
    raise RuntimeError("Backing gussets not independently connected quads")
if max(gap_widths)>.028:
    raise RuntimeError("Gusset grew beyond normal lacing gap")
if not .0029<=statistics.mean(radial_clearances)<=.0031:
    raise RuntimeError("Recessed gusset no longer inset")

# 3D CLOTH PATTERN STUDY ONLY: sample the existing evaluated garment for
# rough thigh/calf clearance and generate four independent curved panels
# with natural front/back arcs, as if draped on a tailor's form.
# They are deliberately displayed OFF THE CHARACTER only in one
# isolated reference render; do not call them a sewn pair of trousers.
cloth_collection=bpy.data.collections.new(
    "0914 | five independent CURVED 3D trouser draft panels HIDDEN")
bpy.context.scene.collection.children.link(cloth_collection)
bpy.context.view_layer.update()
evaluated=trousers.evaluated_get(bpy.context.evaluated_depsgraph_get())
cloth=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
zmin,zmax=min(p.z for p in cloth),max(p.z for p in cloth)
if not .12<zmin<.24 or not 1.01<zmax<1.14:
    raise RuntimeError("Unexpected trouser cloth z bounds")
samples=27
around=12
patterns=[]
panel_records={}
all_widths=[]
for side,label in ((-1,"L"),(1,"R")):
    base=[]
    for i in range(samples):
        z=zmin+.010+(zmax-zmin-.035)*i/(samples-1)
        near=[v for v in cloth if side*v.x>.055 and abs(v.z-z)<.060]
        if len(near)<14:
            raise RuntimeError("Cannot measure independent cloth section: "+label+" z "+str(z))
        xs=sorted(p.x for p in near)
        ys=sorted(p.y for p in near)
        def interp(xs,q):
            t=q*(len(xs)-1)
            ix=int(t)
            return xs[ix]*(1-(t-ix))+xs[min(ix+1,len(xs)-1)]*(t-ix)
        center_x=(interp(xs,.10)+interp(xs,.90))*.5
        center_y=(interp(ys,.10)+interp(ys,.90))*.5
        rx=max(.050,min(.142,(interp(xs,.90)-interp(xs,.10))*.55+.013))
        ry=max(.045,min(.138,(interp(ys,.90)-interp(ys,.10))*.55+.013))
        base.append((z,center_x,center_y,rx,ry))
    for face_type,angle_a,angle_b,material,slot in (
        ("front",math.pi,2*math.pi,fabric_mock,0),
        ("back",0,math.pi,fabric_back,1)
    ):
        # Intentionally visible only in the isolated model pattern preview,
        # with panels separated in X. Preserves natural XY curved fabric.
        zbase=base[0][0]
        xdisplay=1.88+(0 if label=="L" else .67)+(0 if slot==0 else .34)
        verts=[]
        for j,(z,cx,cy,rx,ry) in enumerate(base):
            for k in range(around):
                t=k/(around-1)
                theta=angle_a+(angle_b-angle_a)*t
                # Use actual measured circumference, slight selective
                # fullness around knees, and avoid rigid straight strips.
                fullness=1+.035*math.exp(-((z-.51)/.22)**2)
                x=xdisplay+rx*math.cos(theta)*fullness
                y=cy+ry*math.sin(theta)*fullness
                verts.append((x,y,z))
                all_widths.append(rx)
        faces=[]
        for j in range(samples-1):
            for k in range(around-1):
                a=j*around+k
                faces.append((a,a+1,a+around+1,a+around))
        obj=make_mesh("0914 | "+label+" "+face_type+" 3D draped QUAD pattern mock",
                      verts,faces,[material])
        collect(obj,cloth_collection)
        uv=obj.data.uv_layers.new(name="0914 | independently unwrapped cloth panel")
        for p in obj.data.polygons:
            for loop in p.loop_indices:
                vertex=obj.data.loops[loop].vertex_index
                row,col=divmod(vertex,around)
                uv.data[loop].uv=(col/(around-1),row/(samples-1))
        modifier=obj.modifiers.new("0914 | preview textile thickness","SOLIDIFY")
        modifier.thickness=.002
        modifier.offset=0
        hide(obj)
        patterns.append(obj)
        panel_records[label+" "+face_type]={"vertices":len(verts),"quads":len(faces),
                                            "uv_layers":len(obj.data.uv_layers)}
# Curved belt-width cloth strip is a FIFTH independent non-worn mockup.
waist_verts=[]
belt_x=3.24
for j,z in enumerate((zmax-.065,zmax-.025)):
    for k in range(25):
        a=(k/24)*2*math.pi
        waist_verts.append((belt_x+.107*math.cos(a),.070*math.sin(a),z))
waist_faces=[]
for k in range(24):
    waist_faces.append((k,(k+1)%24,25+(k+1)%24,25+k))
band=make_mesh("0914 | curved 3D waistband draft, not sewn to legs",
               waist_verts,waist_faces,[waist_mat])
collect(band,cloth_collection)
hide(band)
patterns.append(band)
assert len(patterns)==5
assert all(o.hide_render for o in patterns)
assert all(len(o.data.polygons)>0 for o in patterns)
assert len(trousers.data.vertices)==1122 and len(trousers.data.polygons)==1086
assert previous["old"]["previous"]["p"]["prior"]["stage"]["components"]==1
assert len(trousers.data.shape_keys.key_blocks)==5
assert digest(body)==body_before
assert [digest(e) for e in eyes]==eye_before
assert all(not o.hide_render for o in previous["panels"])
assert all(not o.hide_render for o in previous["back_laces"])

metadata={
    "version":"0.9.14",
    "stage":"anatomically recessed rear leather gussets and independently curved 3D trouser drafts",
    "license":"CC0-1.0",
    "source":"Blender Studio Human Base Meshes 1.4.1 Body Male - Realistic",
    "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
    "body_hash_before":body_before,"body_hash_after":digest(body),
    "original_eyes_unchanged":[digest(e) for e in eyes]==eye_before,
    "prior_leather_panels_kept":len(previous["panels"]),
    "prior_cross_laces_kept":len(previous["back_laces"]),
    "rear_leather_gussets":len(gussets),
    "gusset_mesh_vertices":[len(g.data.vertices) for g in gussets],
    "gusset_quad_faces":[len(g.data.polygons) for g in gussets],
    "gusset_uvs":[len(g.data.uv_layers) for g in gussets],
    "mean_gusset_surface_inset_m":round(statistics.mean(radial_clearances),5),
    "max_source_rear_slit_width_m":round(max(gap_widths),5),
    "trouser_draft_3d_pieces":len(patterns),
    "trouser_draft_curved_leg_panels":len(panel_records),
    "trouser_draft_quads_per_leg_panel":{k:v["quads"] for k,v in panel_records.items()},
    "trouser_draft_hidden_for_character":all(o.hide_render for o in patterns),
    "active_trouser_components":previous["old"]["previous"]["p"]["prior"]["stage"]["components"],
    "active_trouser_vertices":len(trousers.data.vertices),
    "active_trouser_faces":len(trousers.data.polygons),
    "active_trouser_shape_keys":len(trousers.data.shape_keys.key_blocks),
    "rigged":False,"unity_character_replaced":False,
    "limitations":"Rear gussets are procedural leather backings; curved 3D trouser draft pieces are NOT sewn or wearable, not in FBX. Current active trousers remain unchanged and body-derived."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
print("V0914_VALIDATE",json.dumps(metadata),flush=True)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=22
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
world=bpy.data.worlds.new("0914 | charcoal model comparison environment")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.15,.17,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.68
scene.world=world
for name,loc,power,size in (
    ("0914 | Key",(2.2,-3.5,4.2),640,4.0),
    ("0914 | Fill",(-2.8,-1.3,2.6),305,3.7),
    ("0914 | Rim",(-1.1,2.7,3.4),430,3.3)
):
    light=bpy.data.lights.new(name,"AREA")
    obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj)
    obj.location=loc
    light.energy=power
    light.shape="DISK"
    light.size=size
camdata=bpy.data.cameras.new("0914 | true view orthographic")
camera=bpy.data.objects.new("0914 | true view orthographic",camdata)
scene.collection.objects.link(camera)
scene.camera=camera
camdata.type="ORTHO"

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_0914.blend"))
# FBX exports only the real character mesh, never hidden drafting geometry.
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
assert len(bpy.context.selected_objects)>23
bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_realistic_0914.fbx"),
    use_selection=True,object_types={"MESH"},
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
def shot(name,pos,target,scale,reso=(640,840)):
    scene.render.resolution_x,scene.render.resolution_y=reso
    camdata.ortho_scale=scale
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("V0914_RENDER",name,flush=True)

for name,loc in (
    ("front",(0,-4.6,1.24)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3,-4,1.30))
):shot(name,loc,(0,0,1),2.27)
shot("bracer_back",(0,2.5,1.12),(0,0,1.09),.82,(760,760))
shot("rear_lacing",(1.07,2.05,1.13),(.52,0,1.08),.53,(760,760))
shot("bracer_threequarter",(2,-2.5,1.10),(.45,0,1.10),.86,(760,760))
shot("pants_front",(0,-2.8,.75),(0,0,.75),1.17,(760,760))

# An explicit 9th view ONLY for the archived pattern mockup. Temporary
# per-view unhide never affects the already-exported FBX or saved .blend.
for obj in patterns:
    obj.hide_render=False
    obj.hide_set(False)
shot("pattern_3d_drafts",(2.58,-3.7,.68),(2.58,0,.65),1.95,(1000,760))
for obj in patterns:hide(obj)
print("SUCCESS_0914",flush=True)
