"""Necromancer Overworld 0.9.13: shaped leather panels & rear lacing.

Uses 0.9.12 verified adult CC0 body. Replaces the visible tubular
forearm shells with independently editable FRONT panel and TWO BACK half
panels for each arm, leaving an actual rear lacing gap. Original tubes
remain archived, hidden, and excluded from FBX. Establishes FIVE genuine
flat trouser pattern-template meshes as a HIDDEN independent modelling
study; the 0.9.12 single connected wearable trouser remains visible.
No modifications to anatomical body or eyes, Unity, rigs, animations.
"""
import os,runpy,math,json,statistics
from pathlib import Path
from mathutils import Vector
import bpy

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_0912_BUILD_ONLY"]="1"
old=runpy.run_path(str(ROOT.parent/"realistic_hero_0912"/"assemble_realistic_hero_0912.py"),
                   run_name="cc0_adult_0912_panel_source")
os.environ.pop("NECROMANCER_0912_BUILD_ONLY",None)
body=old["body"]
eyes=old["eyes"]
trousers=old["trousers"]
digest=old["digest"]
before=digest(body)
before_eyes=[digest(o) for o in eyes]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2
source_guards=old["new_guards"]
assert len(source_guards)==2
RINGS=old["RINGS"]
RADIAL=old["RADIAL"]
assert (RINGS,RADIAL)==(22,32)

def make_mat(name,color,rough=.87,metallic=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metallic
    return m
front_mat=make_mat("0913 | tailored matte oxblood charcoal leather",(.086,.062,.068),.89)
back_mat=make_mat("0913 | slightly darker split rear leather",(.066,.054,.061),.91)
edge_mat=make_mat("0913 | folded leather trim dark",(.052,.044,.048),.94)
cord_mat=make_mat("0913 | matte leather lacing",(.154,.120,.113),.86)
pattern_mat=make_mat("0913 | flat fabric mockup pattern (archived)",(.072,.068,.078),.96)

# Fine leather surface pore variation without glossy metallic accents.
tex=front_mat.node_tree.nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value=115.0
tex.inputs["Detail"].default_value=2.0
bump=front_mat.node_tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.033
bump.inputs["Distance"].default_value=.00034
front_mat.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
front_mat.node_tree.links.new(bump.outputs["Normal"],
    front_mat.node_tree.nodes.get("Principled BSDF").inputs["Normal"])

def mesh_obj(name,points,faces,mats):
    me=bpy.data.meshes.new(name+" | editable quad panel")
    me.from_pydata(points,[],faces)
    me.update()
    for mat in mats:me.materials.append(mat)
    for poly in me.polygons:poly.use_smooth=True
    ob=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

def cord(name,points,radius=.00063):
    if not 2<=len(points)<=RINGS:
        raise RuntimeError("Bad leather cord coordinates")
    c=bpy.data.curves.new(name,"CURVE")
    c.dimensions="3D"
    c.resolution_u=8
    c.bevel_depth=radius
    c.bevel_resolution=2
    sp=c.splines.new("POLY")
    sp.points.add(len(points)-1)
    for cp,p in zip(sp.points,points):
        cp.co=(p.x,p.y,p.z,1)
    c.materials.append(cord_mat)
    ob=bpy.data.objects.new(name,c)
    bpy.context.scene.collection.objects.link(ob)
    return ob

collection=bpy.data.collections.new("0913 | three-panel fitted forearm leather and rear lacing")
bpy.context.scene.collection.children.link(collection)
def move(ob,dest):
    dest.objects.link(ob)
    for old_collection in list(ob.users_collection):
        if old_collection!=dest:old_collection.objects.unlink(ob)
def hide(o):
    o.hide_render=True
    o.hide_set(True)

# All older full-cylinder shells and their four circular sewing guides
# stay in the .blend for comparison, but never show in the finished render.
for obj in [*source_guards,*old["rim_curves"]]:
    hide(obj)

FRONT=[math.pi+.025,2*math.pi-.025,19]
BACK_NEAR=[.025,math.pi/2-.058,11]
BACK_FAR=[math.pi/2+.058,math.pi-.025,11]
panels=[]
panels_by_side={}
back_laces=[]
edge_guides=[]
lengths=[]
panel_quads={}
panel_vertices={}
side_source_radii={}
for source in source_guards:
    world=[source.matrix_world@v.co for v in source.data.vertices]
    side="left" if statistics.mean(v.x for v in world)<0 else "right"
    # World coordinates of ring vertices are the measured, tapered 0.9.12
    # anatomy-fitted model. Linear interpolation stays on its real facets.
    def ring(j,angle):
        a=(angle%(2*math.pi))/(2*math.pi)*RADIAL
        k=int(a)
        t=a-k
        left=world[j*RADIAL+k%RADIAL]
        right=world[j*RADIAL+(k+1)%RADIAL]
        return left.lerp(right,t)

    parts=[]
    specs=[("front cuir",FRONT,front_mat),
           ("rear near",BACK_NEAR,back_mat),
           ("rear far",BACK_FAR,back_mat)]
    for label,(a0,a1,n),material in specs:
        points=[]
        for j in range(RINGS):
            for k in range(n):
                theta=a0+(a1-a0)*k/(n-1)
                p=ring(j,theta)
                # A small, gradual shaping change in frontal leather,
                # reducing the tubular silhouette without pressing into
                # wrist tissue or changing the underlying adult model.
                if label=="front cuir":
                    at=(k/(n-1)-.5)*2
                    centre=1-at*at
                    p.y+=.0015*max(0,centre)*math.sin(math.pi*j/(RINGS-1))
                points.append(p)
        faces=[]
        for j in range(RINGS-1):
            for k in range(n-1):
                a=j*n+k
                faces.append((a,a+1,a+n+1,a+n))
        name="0913 | "+side+" "+label+" independent leather panel"
        ob=mesh_obj(name,points,faces,[material,edge_mat])
        move(ob,collection)
        for poly in ob.data.polygons:
            k=poly.index%(n-1)
            j=poly.index//(n-1)
            if j in (0,RINGS-2) or k in (0,n-2):
                poly.material_index=1
        uv=ob.data.uv_layers.new(name="0913 | independently cut panel UV")
        for poly in ob.data.polygons:
            for loop in poly.loop_indices:
                vid=ob.data.loops[loop].vertex_index
                jj,kk=divmod(vid,n)
                uv.data[loop].uv=(kk/(n-1),jj/(RINGS-1))
        solid=ob.modifiers.new("0913 | flexible dyed leather thickness","SOLIDIFY")
        solid.thickness=.0019
        solid.offset=0
        solid.use_rim=True
        bevel=ob.modifiers.new("0913 | rounded panel leather edge","BEVEL")
        bevel.width=.00085
        bevel.segments=2
        panels.append(ob)
        parts.append(ob)
        panel_quads[side+" "+label]=len(faces)
        panel_vertices[side+" "+label]=len(points)

    # Four vertical stitch guides anchored to the actual cut edges.
    # A gap stays visible: the rear lacings, not these guides, close it.
    for label,angle in (("front left",FRONT[0]),("front right",FRONT[1]),
                        ("rear slit left",BACK_NEAR[1]),
                        ("rear slit right",BACK_FAR[0])):
        path=[ring(j,angle) for j in range(2,RINGS-2)]
        # No exaggerated outward offset, stitches hug original panel.
        guide=cord("0913 | "+side+" "+label+" edge sewing",path,.00030)
        move(guide,collection)
        edge_guides.append(guide)

    # Back opening is deliberately centered at theta=pi/2 (+Y), never
    # on the front, on the hands or on the exposed inner arm.
    for j in (4,8,12,16):
        L1=ring(j,BACK_NEAR[1])
        R1=ring(j+1,BACK_FAR[0])
        L2=ring(j+1,BACK_NEAR[1])
        R2=ring(j,BACK_FAR[0])
        # Every lace is short, slightly lifted off rear leather; use
        # actual measured bridge endpoints, not floating block primitives.
        for idx,(a,b) in enumerate(((L1,R1),(L2,R2))):
            outward=Vector((0,.0019,0))
            points=[a+outward,a.lerp(b,.5)+Vector((0,.0030,0)),b+outward]
            length=sum((v-u).length for u,v in zip(points[:-1],points[1:]))
            lengths.append(length)
            lace=cord("0913 | "+side+" crossed back lacing "+str(j)+"."+str(idx),
                      points,.00053)
            move(lace,collection)
            back_laces.append(lace)
    panels_by_side[side]=[p.name for p in parts]
    side_source_radii[side]=old["section_stats"][side]
if len(panels)!=6 or len(back_laces)!=16 or len(edge_guides)!=8:
    raise RuntimeError("Missing back-laced leather pattern pieces")
if any(len(g.data.uv_layers)!=1 for g in panels):
    raise RuntimeError("Each leather panel needs its own editable UV")
if any(length>.055 for length in lengths):
    raise RuntimeError("Long misplaced rear lacing detected: "+str(max(lengths)))
if not all(o.hide_render for o in [*source_guards,*old["rim_curves"]]):
    raise RuntimeError("Retired one-piece tube is visible")

# PHASE-ONE INDEPENDENT TROUSER PATTERN PROTOTYPE:
# Five separate 2D fabric pattern pieces, with a distinct waist and two
# front and two rear legs; intentionally NOT WORN and NOT exported. This
# starts pattern-cut modelling rather than once again morphing the original
# anatomy-derived cloth (that remains the only visible trousers).
pattern_collection=bpy.data.collections.new(
    "0913 | five flat trouser cutting patterns HIDDEN STUDY - not stitched")
bpy.context.scene.collection.children.link(pattern_collection)
cloth_points=[trousers.matrix_world@v.co for v in trousers.data.vertices]
hem=min(p.z for p in cloth_points)
waist=max(p.z for p in cloth_points)
pattern_parts=[]
for half in ("left","right"):
    for face_type in ("front","back"):
        # Each panel has independent seam allowance and 20 quad rows.
        # Flat pieces live outside the character in X and are hidden.
        n=21
        off_x=1.8+(.3 if half=="right" else 0)+(.15 if face_type=="back" else 0)
        verts=[]
        for j in range(n):
            t=j/(n-1)
            z=hem+(waist-hem)*t
            panel_width=.063+.022*t+.016*math.exp(-((t-.75)/.18)**2)
            centre_shift=.009*math.sin(2.4*math.pi*t)
            verts.append((off_x+centre_shift-panel_width,0,z))
            verts.append((off_x+centre_shift+panel_width,0,z))
        faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(n-1)]
        ob=mesh_obj("0913 | "+half+" "+face_type+" flat leg panel with seam allowance",
                    verts,faces,[pattern_mat])
        move(ob,pattern_collection)
        hide(ob)
        pattern_parts.append(ob)
# A fifth pattern strip for waistband, also flat and invisible in renders.
wb=mesh_obj("0913 | full flat waistband drafting template",
   [(2.16,0,waist+.01),(2.72,0,waist+.01),
    (2.72,0,waist+.065),(2.16,0,waist+.065)],
   [(0,1,2,3)],[pattern_mat])
move(wb,pattern_collection)
hide(wb)
pattern_parts.append(wb)
assert len(pattern_parts)==5
assert all(o.hide_render for o in pattern_parts)
assert len(trousers.data.vertices)==1122 and len(trousers.data.polygons)==1086
assert len(trousers.data.shape_keys.key_blocks)==5
assert old["previous"]["p"]["prior"]["stage"]["components"]==1
assert digest(body)==before
assert [digest(e) for e in eyes]==before_eyes

# Import-only mode for downstream leather and garment study.
if os.environ.get('NECROMANCER_0913_BUILD_ONLY') != '1':
    metadata={
     "stage":"0.9.13 anatomical leather panel cutting, rear laces, and separate hidden trouser patterns",
     "license":"CC0-1.0","source":"Body Male - Realistic Blender Studio v1.4.1",
     "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
     "body_hash_before":before,"body_hash_after":digest(body),
     "eye_hashes_unchanged":[digest(e) for e in eyes]==before_eyes,
     "source_full_cylinder_bracers_hidden":all(g.hide_render for g in source_guards),
     "original_095_guards_hidden":all(g.hide_render for g in old["guards"]),
     "leather_panel_count":len(panels),"leather_panels_per_arm":panels_by_side,
     "leather_panel_quads":panel_quads,"leather_panel_vertices":panel_vertices,
     "panel_uv_layers":[len(x.data.uv_layers) for x in panels],
     "rear_cross_lacing_count":len(back_laces),
     "rear_lacing_max_length_m":round(max(lengths),5),
     "leather_edge_stitch_guides":len(edge_guides),
     "source_arm_radius_reference":side_source_radii,
     "flat_2d_trouser_pattern_count":len(pattern_parts),
     "flat_patterns_hidden":all(x.hide_render for x in pattern_parts),
     "active_trouser_connected_meshes":old["previous"]["p"]["prior"]["stage"]["components"],
     "active_trouser_vertices":len(trousers.data.vertices),
     "active_trouser_faces":len(trousers.data.polygons),
     "active_trouser_shape_keys":len(trousers.data.shape_keys.key_blocks),
     "rigged":False,"unity_character_replaced":False,
     "limitations":"Three leather panels per arm are procedurally fitted, not hand-sculpted or simulated. Flat trousers are 2D pattern templates only, not sewn into wearable draped trousers."
    }
    (OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print("VALIDATED_0913",json.dumps(metadata),flush=True)
    
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=22
    scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    world=bpy.data.worlds.new("0913 | soft neutral professional studio")
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.15,.17,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.68
    scene.world=world
    for name,pos,power,size in (
        ("0913 | key",(2.2,-3.5,4.2),640,4.0),
        ("0913 | fill",(-2.8,-1.3,2.6),305,3.7),
        ("0913 | rim",(-1.1,2.7,3.4),430,3.3)
    ):
        light=bpy.data.lights.new(name,"AREA")
        obj=bpy.data.objects.new(name,light)
        scene.collection.objects.link(obj)
        obj.location=pos
        light.energy=power
        light.shape="DISK"
        light.size=size
    camdata=bpy.data.cameras.new("0913 | ortho inspection camera")
    camera=bpy.data.objects.new("0913 | ortho inspection camera",camdata)
    scene.collection.objects.link(camera)
    scene.camera=camera
    camdata.type="ORTHO"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_0913.blend"))
    for obj in list(scene.objects):
        if obj.type!="CURVE" or obj.hide_render:continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.hide_set(False);obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(scene.objects):
        if obj.type=="MESH" and not obj.hide_render and not obj.name.startswith("095 | stylized"):
            obj.hide_set(False);obj.select_set(True)
    assert len(bpy.context.selected_objects)>23
    bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_realistic_0913.fbx"),
       use_selection=True,object_types={"MESH"},
       apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
    def render(name,pos,target,scale,reso=(640,840)):
        scene.render.resolution_x,scene.render.resolution_y=reso
        camdata.ortho_scale=scale
        camera.location=pos
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("hero_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("RENDER_0913",name,flush=True)
    for name,loc in (
        ("front",(0,-4.6,1.24)),
        ("side",(4.6,0,1.25)),
        ("back",(0,4.6,1.25)),
        ("threequarter",(3,-4,1.30))
    ):render(name,loc,(0,0,1),2.27)
    render("bracer_front",(1.05,-2.3,1.13),(.52,0,1.07),.55,(760,760))
    render("bracer_threequarter",(2,-2.5,1.10),(.45,0,1.10),.86,(760,760))
    render("bracer_back",(0,2.5,1.1),(0,0,1.09),.82,(760,760))
    render("rear_lacing",(1.07,2.05,1.13),(.52,0,1.08),.53,(760,760))
    print("SUCCESS_0913",flush=True)
    