"""Necromancer Overworld 0.9.10: continuous seams, rounded leather gear.

Progressive Blender scene from verified 0.9.9. The source adult CC0 Body
Male - Realistic and its original two eyes retain exact coordinate hashes.
No replacement of Unity protagonist, no animation, rigging or Unity edit.
"""
import bpy, math, json, os, runpy, statistics, hashlib, struct
from pathlib import Path
from mathutils import Vector
from collections import defaultdict

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["NECROMANCER_099_BUILD_ONLY"]="1"
prior=runpy.run_path(str(ROOT.parent/"realistic_hero_099"/"assemble_realistic_hero_099.py"),
                    run_name="cc0_adult_garment_099_import")
os.environ.pop("NECROMANCER_099_BUILD_ONLY",None)

body=prior["body"]
eyes=prior["eyes"]
trousers=prior["trousers"]
digest=prior["digest"]
body_before=digest(body)
eyes_before=[digest(e) for e in eyes]
assert (len(body.data.vertices),len(body.data.polygons))==(10582,10590)
assert len(eyes)==2

def smoothstep(a,b,x):
    t=max(0.0,min(1.0,(x-a)/(b-a)))
    return t*t*(3-2*t)
def mat(name,color,rough=.82,metal=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m
leather=mat("0910 | aged dark oxblood leather",(.105,.070,.069),.84)
flap=mat("0910 | desaturated leather edge and flap",(.14,.092,.085),.79)
deep=mat("0910 | deeper leather recessed seams",(.050,.036,.042),.90)
bracer_mat=mat("0910 | ash-black reinforced bracers",(.087,.074,.081),.87)
bracer_trim=mat("0910 | subdued grey leather stitch",(.22,.185,.18),.82)
metal=mat("0910 | low glint aged bronze",(.29,.215,.115),.60,.46)
seam_mat=mat("0910 | near-black single stitched cloth line",(.155,.143,.146),.88)

def curve_obj(name,points,material,radius=.00065,bezier=True):
    c=bpy.data.curves.new(name,"CURVE")
    c.dimensions="3D"
    c.resolution_u=16
    c.bevel_depth=radius
    c.bevel_resolution=2
    spline=c.splines.new("BEZIER" if bezier else "POLY")
    if bezier:
        spline.bezier_points.add(len(points)-1)
        for bp,p in zip(spline.bezier_points,points):
            bp.co=p
            bp.handle_left_type="AUTO"
            bp.handle_right_type="AUTO"
    else:
        spline.points.add(len(points)-1)
        for cp,p in zip(spline.points,points):
            cp.co=(p.x,p.y,p.z,1)
    c.materials.append(material)
    o=bpy.data.objects.new(name,c)
    bpy.context.scene.collection.objects.link(o)
    return o

# ===== 1. SIDE SEAMS: SMOOTH CURVES AT THE ACTUAL CLOTH HEM =====
# 0.9.9 used y-offset dependent ray casts, which could jump between the
# front and rear of a calf. Sample a fixed "outer side" silhouette from
# each physical cross-section, fit a smoothed path, then SNAP back to
# the continuously evaluated garment via closest point. No leg lofting.
for old in prior["seams"]:
    old.hide_render=True
    old.hide_set(True)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
evaluated=trousers.evaluated_get(deps)
inv=evaluated.matrix_world.inverted_safe()
N=evaluated.matrix_world.to_3x3().inverted_safe().transposed()
eval_points=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
zmin=min(p.z for p in eval_points)
zmax=max(p.z for p in eval_points)
# Hem target 7 mm above the bottom cut and top just below the belt.
bottom=zmin+.007
top=min(zmax-.055,.986)
if not (.15<bottom<.23 and top>.91):
    raise RuntimeError("Unexpected garment cutoff: "+repr((zmin,zmax)))
seams=[]
profiles={}
jump_max=0
ends=[]
for side,label in ((-1,"left"),(1,"right")):
    coords=[]
    station_count=91
    for k in range(station_count):
        z=bottom+(top-bottom)*k/(station_count-1)
        samples=[p for p in eval_points
                 if side*p.x>.054 and abs(p.z-z)<.044]
        if len(samples)<12:
            samples=[p for p in eval_points
                     if side*p.x>.054 and abs(p.z-z)<.072]
        if len(samples)<10:
            raise RuntimeError("Not enough real garment vertices near "+label+" z="+str(z))
        # Use the outer side of the leg, not a point on the front seam
        # or an arbitrary 'nearest vertex' that produces jagged line jumps.
        ranked=sorted(samples,key=lambda p:side*p.x,reverse=True)
        outer=ranked[:max(5,int(len(ranked)*.17))]
        y=statistics.median(p.y for p in outer)
        x=statistics.median(p.x for p in outer)
        coords.append(Vector((x,y,z)))
    # 9-sample low-pass in X/Y suppresses knee/calf oscillations without
    # shifting the top/hem in Z; smooth also suppresses sample transitions
    # between body quad loop rows.
    filtered=[]
    for i,p in enumerate(coords):
        select=[]
        for j in range(max(0,i-8),min(len(coords),i+9)):
            wt=math.exp(-((i-j)/4.0)**2)
            select.append((wt,coords[j]))
        den=sum(w for w,q in select)
        filtered.append(Vector((sum(w*q.x for w,q in select)/den,
                                sum(w*q.y for w,q in select)/den,p.z)))
    guide=[]
    for p in filtered:
        query=Vector((p.x+side*.012,p.y,p.z))
        hit,loc,normal,polygon=evaluated.closest_point_on_mesh(inv@query)
        if not hit:
            raise RuntimeError("Couldn't project seam onto continuous garment: "+label)
        real=evaluated.matrix_world@loc
        if side*real.x<.03 or abs(real.z-p.z)>.038:
            raise RuntimeError("Side seam drifted to unrelated surface: "+label+" z="+str(p.z))
        norm=(N@normal).normalized()
        guide.append(real+norm*.00120)
    # Choose a few well-spaced controls and gently restrain horizontal path.
    # Bézier auto handles preserve continuity without 90-point zigzags.
    sampled=[guide[i] for i in range(0,len(guide),6)]
    if (sampled[-1]-guide[-1]).length>.001:
        sampled.append(guide[-1])
    for a,b in zip(sampled[:-1],sampled[1:]):
        jump_max=max(jump_max,(a-b).length)
    # Endpoints must be within 2 cm of the true cloth lower boundary.
    delta=abs(sampled[0].z-zmin)
    if delta>.026:
        raise RuntimeError("Seam does not reach garment hem: "+label+" distance "+str(delta))
    ends.append(round(delta,5))
    seams.append(curve_obj("0910 | "+label+" full-length tailored side seam",
                           sampled,seam_mat,.00062))
    profiles[label]=len(sampled)
if jump_max>.12:raise RuntimeError("Suspicious seam control jump: "+str(jump_max))

# ===== 2. ROUNDED UTILITY POUCHES, SEPARATE PANELS AND SMALL BRONZE CLASPS =====
# Hide previous square construction without deleting any source art.
archived_pouches=[]
for o in list(bpy.context.scene.objects):
    if o.name.startswith("095 |") and any(t in o.name for t in (
        "belt pouch","pouch flap","pouch metal catch"
    )):
        o.hide_render=True
        o.hide_set(True)
        archived_pouches.append(o)
if len(archived_pouches)<6:
    raise RuntimeError("Expected archival pouch body/flap/catches: "+str(len(archived_pouches)))

def mesh_object(name,verts,faces,material,bevel=.005):
    me=bpy.data.meshes.new(name+" | mesh")
    me.from_pydata(verts,[],faces)
    me.update()
    me.materials.append(material)
    ob=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(ob)
    for f in me.polygons:f.use_smooth=True
    if bevel>0:
        mod=ob.modifiers.new("Soft bevels on sewn leather","BEVEL")
        mod.width=bevel
        mod.segments=3
        ob.modifiers.new("Weighted shading","WEIGHTED_NORMAL")
    return ob
def rounded_box(name,center,dims,material,bevel=.006):
    x,y,z=center;rx,ry,rz=[v/2 for v in dims]
    verts=[(x+dx*rx,y+dy*ry,z+dz*rz) for dz in (-1,1)
           for dy in (-1,1) for dx in (-1,1)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),
           (2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return mesh_object(name,verts,faces,material,bevel)

gear=[]
pouch_bodies=[]
for side,label in ((-1,"L"),(1,"R")):
    cx=side*.190
    cz=.994
    # 10-sided soft asymmetric pouch silhouette with curved front and
    # one continuous sidewall. Scale is restrained, avoiding 'giant cubes'.
    outline=[
       (-.033,-.051),(.031,-.051),(.044,-.038),
       (.043,.025),(.029,.045),(0,.048),
       (-.026,.046),(-.042,.029),(-.042,-.036)
    ]
    n=len(outline)
    verts=[]
    for layer in (0,1):
        for dx,dz in outline:
            x=cx+dx
            z=cz+dz
            front=-.159-(.004*(1-abs(dx)/.05))*layer
            y=(-.112 if layer==0 else front)
            verts.append((x,y,z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for j in range(n):
        nxt=(j+1)%n
        faces.append((j,nxt,n+nxt,n+j))
    body_o=mesh_object("0910 | "+label+" rounded utility leather pouch",
                       verts,faces,leather,.007)
    pouch_bodies.append(body_o)
    gear.append(body_o)
    # Separately editable curved flap and thong at the upper third.
    flap_pts=[]
    flap_outline=[(-.038,.031),(.037,.031),(.037,.010),
                  (.028,.002),(-.030,.002),(-.038,.013)]
    for xx,zz in flap_outline:
        flap_pts.append((cx+xx,-.171,cz+zz))
    flap_o=mesh_object("0910 | "+label+" inset pouch flap",flap_pts,
                      [tuple(range(len(flap_pts)))],flap,.0017)
    gear.append(flap_o)
    catch=rounded_box("0910 | "+label+" aged brass flap clasp",
                      (cx,-.175,cz+.005),(.011,.005,.022),metal,.0013)
    gear.append(catch)
    # Low-profile loop of exposed stitching around leather pouch face.
    outline_stitch=[
       Vector((cx+dx*.88,-.167,cz+dz*.89))
       for dx,dz in outline
    ]
    outline_stitch.append(outline_stitch[0].copy())
    gear.append(curve_obj("0910 | "+label+" pouch perimeter sewing",
                          outline_stitch,deep,.00062,False))
    strap=rounded_box("0910 | "+label+" short belt retention tab",
                      (cx,-.114,1.052),(.030,.009,.048),deep,.002)
    gear.append(strap)
assert len(pouch_bodies)==2

# ===== 3. BRACER MATERIAL AND CONTOUR STITCHING =====
original_guards=[o for o in bpy.context.scene.objects if
  o.type=="MESH" and o.name.startswith("095 |") and "dark leather forearm guard" in o.name]
if len(original_guards)!=2:
    raise RuntimeError("Original anatomical forearm leather shell pair missing")
# Decorative stitches are now short marks on ACTUAL existing mesh edges.
# Earlier long Bézier paths unintentionally connected distant guard faces,
# creating wire-like spikes in renders. Per-dash maximum is 2.7cm.
bracer_stitches=[]
bracer_dash_lengths=[]
for guard in original_guards:
    guard.data.materials.clear()
    guard.data.materials.append(bracer_mat)
    ns=bracer_mat.node_tree.nodes
    if ns.get("0910 | leather grain") is None:
        tex=ns.new("ShaderNodeTexNoise")
        tex.name="0910 | leather grain"
        tex.inputs["Scale"].default_value=125
        tex.inputs["Detail"].default_value=2
        bump=ns.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.05
        bump.inputs["Distance"].default_value=.0006
        links=bracer_mat.node_tree.links
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],ns.get("Principled BSDF").inputs["Normal"])
    pworld=[guard.matrix_world@v.co for v in guard.data.vertices]
    y_front=sorted(p.y for p in pworld)[int(len(pworld)*.34)]
    zmin_guard,zmax_guard=min(p.z for p in pworld),max(p.z for p in pworld)
    xmean=statistics.mean(p.x for p in pworld)
    name="left" if xmean<0 else "right"
    target_zs=[zmin_guard+(zmax_guard-zmin_guard)*a for a in (.26,.73)]
    for pass_no,target_z in enumerate(target_zs):
        edges=[]
        for e in guard.data.edges:
            i,j=e.vertices
            a,b=pworld[i],pworld[j]
            length=(a-b).length
            center=(a+b)*.5
            if (.003<length<.022 and abs(center.z-target_z)<.043
                and center.y<y_front+.025
                and abs(a.z-b.z)<.019):
                edges.append((abs(center.z-target_z)+
                              .12*abs(center.x-xmean),a,b,length))
        edges.sort(key=lambda item:item[0])
        selected=[]
        for score,a,b,length in edges:
            mid=(a+b)*.5
            if all((mid-(p+q)*.5).length>.023 for p,q,_ in selected):
                selected.append((a,b,length))
                if len(selected)==4:break
        for k,(a,b,length) in enumerate(selected):
            offset=Vector((0,-.0013,0))
            bracer_stitches.append(curve_obj(
                "0910 | "+name+" short guard stitch "+str(pass_no)+"."+str(k),
                [a+offset,b+offset],bracer_trim,.00062,False))
            bracer_dash_lengths.append(length)
if not bracer_dash_lengths or max(bracer_dash_lengths)>.027:
    raise RuntimeError("Leather stitch exceeded its actual short mesh edge")
if len(bracer_stitches)<2:
    raise RuntimeError("Not enough real-surface bracer stitched contours")

# All additions are separate and Blender-editable collections.
coll=bpy.data.collections.new("0910 | refined leather gear and garment seams")
bpy.context.scene.collection.children.link(coll)
for ob in [*seams,*gear,*bracer_stitches]:
    coll.objects.link(ob)
    for old in list(ob.users_collection):
        if old!=coll:old.objects.unlink(ob)

# Final critical invariants: never deform the adult anatomical source.
assert digest(body)==body_before
assert [digest(x) for x in eyes]==eyes_before
assert len(trousers.data.polygons)==1086 and len(trousers.data.vertices)==1122
assert prior["stage"]["components"]==1
assert all(x.hide_render for x in prior["seams"])
assert all(x.hide_render for x in prior["stage"]["hidden_loft"])

metadata={
 "stage":"0.9.10 garment full-length seams and rounded utility gear",
 "license":"CC0-1.0","bundle_version":"1.4.1",
 "base_collection":"Body Male - Realistic",
 "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
 "body_digest_before":body_before,"body_digest_after":digest(body),
 "original_eye_hashes_unchanged":[digest(x) for x in eyes]==eyes_before,
 "connected_garment_mesh_count":prior["stage"]["components"],
 "trousers_vertices":len(trousers.data.vertices),
 "trousers_faces":len(trousers.data.polygons),
 "side_seam_count":len(seams),
 "seam_control_points":profiles,
 "max_control_jump_m":round(jump_max,5),
 "hem_seam_endpoint_distances_m":ends,
 "prior_seams_hidden":all(x.hide_render for x in prior["seams"]),
 "previous_pouch_parts_hidden":len(archived_pouches),
 "rounded_pouch_count":len(pouch_bodies),
 "pouch_gear_parts":len(gear),
 "original_bracer_count":len(original_guards),
 "new_bracer_stitch_curves":len(bracer_stitches),
 "max_bracer_stitch_m":round(max(bracer_dash_lengths),5),
 "rigged":False,"unity_character_replaced":False,
 "known_limitations":"Costumes/accessories are still procedural prototypes; no final character concept turnaround, full garment UV tailoring, rigging or animation."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
print("V0910_METADATA",json.dumps(metadata),flush=True)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=23
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
world=bpy.data.worlds.new("0910 | neutral studio")
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.15,.15,.175,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.65
scene.world=world
for name,pos,power,size in (
 ("0910 Key",(2.2,-3.5,4.2),650,4.0),
 ("0910 Fill",(-2.8,-1.3,2.6),280,3.6),
 ("0910 Rim",(-1.1,2.7,3.4),430,3.3)
):
    l=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,l)
    scene.collection.objects.link(ob)
    ob.location=pos
    l.energy=power
    l.shape="DISK"
    l.size=size
cdata=bpy.data.cameras.new("0910 | orthographic views")
camera=bpy.data.objects.new("0910 | orthographic views",cdata)
scene.collection.objects.link(camera)
cdata.type="ORTHO"
scene.camera=camera

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_realistic_0910.blend"))
for o in list(scene.objects):
    if o.type!="CURVE" or o.hide_render:continue
    bpy.ops.object.select_all(action="DESELECT")
    o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for o in list(scene.objects):
    if o.type=="MESH" and not o.hide_render and not o.name.startswith("095 | stylized"):
        o.hide_set(False);o.select_set(True)
if len(bpy.context.selected_objects)<20:
    raise RuntimeError("FBX lost required sculpt and accessory pieces")
bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_realistic_0910.fbx"),
    use_selection=True,object_types={"MESH"},apply_unit_scale=True,axis_forward="-Z",axis_up="Y")

def shot(name,location,target,scale,reso=(640,840)):
    scene.render.resolution_x,scene.render.resolution_y=reso
    cdata.ortho_scale=scale
    camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("hero_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("V0910_RENDER",name,flush=True)
for name,location in (
    ("front",(0,-4.6,1.24)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3,-4,1.30))
):shot(name,location,(0,0,1),2.27)
shot("hip_front",(0,-2.8,1.01),(0,0,1.0),.90,(760,760))
shot("pouch_threequarter",(1.5,-2.8,1.03),(0,0,1.045),.75,(760,760))
shot("seam_side",(2.4,-.05,.67),(0,0,.65),1.06,(760,760))
shot("bracer_detail",(2,-2.5,1.10),(.45,0,1.10),.86,(760,760))
print("SUCCESS_0910",flush=True)
