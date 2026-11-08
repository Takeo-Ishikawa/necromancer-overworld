"""Necromancer 0.9.2 — identity and silhouette pass on the REAL CC0 human mesh.

The Blender Studio 1.4.1 stylized male remains the only anatomical source.
No sphere/cylinder body reconstruction, remesh, rig or Unity scene modification.
Clothing shells reuse polygons from the official body topology; hair and accessories
are independently editable meshes/curves. This is a visual prototype, not a final
hand-sculpted hero mesh.
"""
import os
import runpy
import json
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

# Reuse the 0.9.1 importer BEFORE its exporter/render stage. Source and
# topology selection are deliberately unchanged, not recreated from primitives.
os.environ["NECROMANCER_IMPORT_ONLY"] = "1"
base = runpy.run_path(str(ROOT / "import_sculpt_091.py"), run_name="cc0_import_092")
os.environ.pop("NECROMANCER_IMPORT_ONLY", None)
body = base["body"]
source_entry = base["entry"]
source_name = base["asset_name"]
original_vertex_count = len(body.data.vertices)
original_face_count = len(body.data.polygons)
assert original_vertex_count > 10000 and original_face_count > 10000
body.name = "092 | body • CC0 sculpt — unrigged"
body.data.name = "Blender Studio stylized male: vertex-preserving 0.9.2"
body.data.use_fake_user = True

def bell(value, centre, radius):
    return math.exp(-((value-centre)/radius)**2)

def smoothstep(a, b, x):
    u = max(0.0, min(1.0, (x-a)/(b-a)))
    return u*u*(3.0-2.0*u)

def material(name, rgb, metal=0.0, rough=0.67):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*rgb, 1.0)
    bs.inputs["Metallic"].default_value = metal
    bs.inputs["Roughness"].default_value = rough
    return m

skin = material("092 | pale cool ivory skin", (.55, .47, .45), rough=.79)
pants_mat = material("092 | graphite woven cloth", (.073, .067, .095), rough=.89)
pants_seam = material("092 | shaded cloth folds", (.055, .053, .074), rough=.88)
hair_base = material("092 | ash silver hair roots", (.25, .25, .33), rough=.68)
hair_silver = material("092 | silver smoke hair", (.43, .43, .51), rough=.57)
hair_lilac = material("092 | subtle lilac hair", (.36, .32, .46), rough=.62)
hair_shadow = material("092 | deep lavender hair shadow", (.20, .19, .28), rough=.78)
leather = material("092 | dark walnut leather", (.095, .061, .059), rough=.76)
leather_lit = material("092 | saddle leather edge", (.21, .13, .11), rough=.68)
gold = material("092 | antique engraved gold", (.58, .37, .135), metal=.75, rough=.38)
iris_mat = material("092 | blue-grey iris", (.27, .33, .38), rough=.37)
pupil_mat = material("092 | charcoal pupil", (.026, .024, .039), rough=.35)

body.data.materials.clear()
body.data.materials.append(skin)
world_inv = body.matrix_world.inverted_safe()

# Broad proportions first, then anatomy in the SAME quad basemesh.
# World coordinates refer to the normalized 1.90 m CC0 source.
for vertex in body.data.vertices:
    p = body.matrix_world @ vertex.co
    x, y, z = p
    ax = abs(x)
    # Athletic V silhouette, without widening the head or deforming hands/feet.
    if .96 < z < 1.62:
        shoulder = .120 * bell(z, 1.48, .16)
        torso = .045 * bell(z, 1.33, .23)
        waist = -.035 * bell(z, 1.06, .12)
        p.x *= 1 + shoulder + torso + waist
        p.y *= 1 + .062*bell(z, 1.40, .16)
    if .27 < z < .94 and ax < .32:
        p.x *= 1 + .049*bell(z, .63, .29)
        p.y *= 1 + .043*bell(z, .60, .33)
    # Correct the youthful/rounded jaw on the real face geometry.
    if 1.645 < z < 1.755 and ax < .14:
        jaw = bell(z, 1.698, .053)
        p.x *= 1 + .081*jaw
        if y < -.045:
            p.y -= .007*bell(ax, .0, .075)*bell(z, 1.666, .045)
    # Browser screenshot comparison shows an overly gentle eyebrow ridge.
    if 1.755 < z < 1.821 and ax < .13 and y < -.065:
        p.y -= .0085*bell(z, 1.788, .014)*bell(ax, .055, .027)
    # Muscular form is low amplitude and works with the inherited anatomy.
    front = smoothstep(.035, .10, -y)
    back = smoothstep(.035, .11, y)
    if 1.12 < z < 1.59 and ax < .33:
        pec = bell(ax, .153, .087)*bell(z, 1.445, .091)
        sternum = bell(x, 0, .019)*bell(z, 1.385, .15)
        serratus = bell(ax, .213, .043)*bell(z, 1.312, .074)
        ab = sum(bell(ax, .072, .044)*bell(z, t, .032) for t in (1.31,1.235,1.16))
        linea = bell(x, 0, .013)*bell(z, 1.246, .115)
        p.y -= front*(.013*pec + .004*serratus + .005*ab - .0038*sternum - .0019*linea)
        p.y += back*(.008*bell(ax,.14,.08)*bell(z,1.43,.17))
    if 1.20 < z < 1.56 and .27 < ax < .57:
        # Deltoid, upper arm and triceps; anatomy remains contiguous.
        p.x += math.copysign(.008*bell(z,1.455,.085),x)
    # Tuck oversized ears in without rebuilding their sculpted loops.
    if 1.68 < z < 1.81 and ax > .095 and -.04 < y < .075:
        ear = bell(z,1.742,.049)*smoothstep(.095,.142,ax)
        p.x -= math.copysign(.019*ear,x)
    vertex.co = world_inv @ p
body.data.update()
for poly in body.data.polygons:
    poly.use_smooth = True

# Precompute the actual body surface. Shells are extracted from the already
# altered source polygons, never constructed as cylinders over the limbs.
world_verts = [body.matrix_world @ v.co for v in body.data.vertices]
normal_matrix = body.matrix_world.to_3x3().inverted_safe().transposed()
world_normals = [(normal_matrix @ v.normal).normalized() for v in body.data.vertices]

def extracted_shell(name, predicate, mat, offset, drape=None, subdivision=1):
    chosen = []
    for poly in body.data.polygons:
        pts = [world_verts[i] for i in poly.vertices]
        center = sum(pts, Vector()) / len(pts)
        if predicate(center, pts):
            chosen.append(tuple(poly.vertices))
    if not chosen:
        raise RuntimeError("Empty sculpted surface region: " + name)
    original_ids = sorted({i for face in chosen for i in face})
    id_map = {v:i for i,v in enumerate(original_ids)}
    new_points = []
    for vid in original_ids:
        p = world_verts[vid].copy()
        n = world_normals[vid]
        extra = drape(p,n) if drape else 0.0
        p += n*(offset+extra)
        new_points.append(p)
    mesh=bpy.data.meshes.new(name+" mesh")
    mesh.from_pydata(new_points, [], [[id_map[i] for i in face] for face in chosen])
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    for poly in mesh.polygons:poly.use_smooth=True
    thickness=obj.modifiers.new("Sewn shell thickness","SOLIDIFY")
    thickness.thickness=.0025
    thickness.offset=0
    if subdivision:
        sm=obj.modifiers.new("Smooth inherited quad loops","SUBSURF")
        sm.levels=subdivision
        sm.render_levels=subdivision
    print("SURFACE",name,len(mesh.vertices),len(mesh.polygons),flush=True)
    return obj

# Loose trousers, down to ankles, body-derived quads and procedural cloth drape.
def pants_region(center, points):
    return (.142 < center.z < 1.064 and
            abs(center.x) < .305 and
            all(abs(p.x) < .335 for p in points))

def trouser_drape(p,n):
    z=p.z
    # Low-frequency folds, coherent in z; wider thigh and calf silhouettes.
    expansion=.017*bell(z,.72,.28)+.010*bell(z,.31,.18)
    wrinkle=.006*math.sin(z*31 + p.x*19 + p.y*4)*bell(z,.43,.36)
    return expansion+wrinkle

trousers=extracted_shell("092 | trousers • editable quad shell",pants_region,
                        pants_mat,.024,trouser_drape)
# Forearm leather is taken directly from anatomy, retaining the arm direction.
bracers=[]
for sign,label in ((-1,"L"),(1,"R")):
    def arm_region(c,pts,sign=sign):
        return (1.005 < c.z < 1.227 and sign*c.x > .305 and
                all(sign*p.x > .280 for p in pts))
    bracers.append(extracted_shell("092 | "+label+" leather bracer",arm_region,
                                   leather,.012,subdivision=1))

# Scalp made from the very same upper-head source topology. Vary hairline
# threshold front-to-back rather than making a featureless spherical helmet.
def scalp_region(c,pts):
    threshold = (1.823 + .013*math.sin(27*c.x+1.0) if c.y < -.034
                 else 1.793 + .013*math.sin(24*c.x+3.2))
    return c.z > threshold and all(p.z > threshold-.008 for p in pts)
scalp=extracted_shell("092 | anatomical scalp hair foundation",scalp_region,
                      hair_base,.009,subdivision=1)

# Layered tapered ribbon strands; each strand has independent shape, direction
# and width. Combined into one editable object with three hair material slots.
rng=random.Random(9202)
hair_v=[]
hair_f=[]
hair_m=[]
def ribbon(points, width, mat_idx):
    # End-width zero prevents square cut-off, curved midline avoids spiky rods.
    first=len(hair_v)
    n=len(points)
    for i,p in enumerate(points):
        u=i/(n-1)
        tangent=(points[min(i+1,n-1)]-points[max(i-1,0)]).normalized()
        side=Vector((-tangent.y,tangent.x,0))
        if side.length < .15:side=Vector((1,0,0))
        side.normalize()
        w=width*(.23+.77*math.sin(math.pi*(.11+.83*u)))
        if i==n-1:w=.0007
        hair_v.extend([p-side*w*.5, p+side*w*.5])
    for i in range(n-1):
        hair_f.append((first+2*i,first+2*i+1,first+2*i+3,first+2*i+2))
        hair_m.append(mat_idx)

# Crown: different sweeps/lengths, warm/cool alternating highlights.
for k in range(115):
    a=2*math.pi*(k+.37*rng.random())/115
    r=.027+.070*rng.random()
    x=r*math.cos(a)
    y=r*math.sin(a)
    root=Vector((x,y,1.911-.27*r))
    direction=Vector((.32*math.sin(a+1.8),-.58+.23*math.sin(a),-.22))
    length=.052+.048*rng.random()
    mid=root+direction*length*.52+Vector((0,0,.010))
    tip=root+direction*length
    ribbon([root,root.lerp(mid,.5),mid,mid.lerp(tip,.55),tip],
           .005+.005*rng.random(), k%5==0 and 2 or (k%3==0 and 1 or 0))

# Fringe follows the face rather than forming a solid forward visor.
for k in range(33):
    f=(k+.45)/33
    x=-.101+f*.202
    root=Vector((x*.78,-.061,1.882-.13*abs(x)))
    tip=Vector((x + .012*math.sin(2.8*k),-.122-.004*rng.random(),
                1.827+.025*rng.random()+.085*abs(x)))
    mid=root.lerp(tip,.49)+Vector((0,-.007,.012))
    ribbon([root,root.lerp(mid,.5),mid,mid.lerp(tip,.5),tip],
           .005+.005*rng.random(), k%4==0 and 1 or 0)

# Temple / nape locks keep a visible short, layered cut from side and rear.
for sign in (-1,1):
    for k in range(24):
        q=k/23
        root=Vector((sign*(.093+.010*rng.random()),-.026+q*.091,
                     1.848-.015*q))
        tip=Vector((sign*(.099+.018*rng.random()),-.075+q*.111,
                    1.794+.040*rng.random()))
        mid=root.lerp(tip,.58)+Vector((sign*.011,0,.014))
        ribbon([root,mid,tip],.005+.005*rng.random(), (k+1)%4==0 and 2 or 1)

hair_mesh=bpy.data.meshes.new("Asymmetric short layered ribbons • 0.9.2")
hair_mesh.from_pydata(hair_v,[],hair_f)
hair_mesh.materials.append(hair_silver)
hair_mesh.materials.append(hair_lilac)
hair_mesh.materials.append(hair_shadow)
hair_mesh.update()
hair=bpy.data.objects.new("092 | short ash-lilac hair strands",hair_mesh)
bpy.context.scene.collection.objects.link(hair)
for poly, idx in zip(hair_mesh.polygons,hair_m):
    poly.material_index=idx
    poly.use_smooth=True
hair_thick=hair.modifiers.new("Thin double-sided hair ribbons","SOLIDIFY")
hair_thick.thickness=.0012

def object_from_mesh(name, pts, faces, mat, bevel=0):
    m=bpy.data.meshes.new(name+" geom")
    m.from_pydata(pts,[],faces)
    m.update()
    ob=bpy.data.objects.new(name,m)
    bpy.context.scene.collection.objects.link(ob)
    m.materials.append(mat)
    for face in m.polygons:face.use_smooth=True
    if bevel:
        be=ob.modifiers.new("Soft accessory corners","BEVEL")
        be.width=bevel
        be.segments=3
        ob.modifiers.new("Accessory weighted normals","WEIGHTED_NORMAL")
    return ob

def box_mesh(name,center,size,mat,bevel=0):
    x,y,z=center
    w,d,h=[n*.5 for n in size]
    v=[(x+dx*w,y+dy*d,z+dz*h) for dz in (-1,1)
       for dy in (-1,1) for dx in (-1,1)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),
           (2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return object_from_mesh(name,v,faces,mat,bevel)

def ellipsoid_band(name,z,rx,ry,width,mat,cx=0):
    # Elliptical leather webbing, not a body primitive.
    N=48
    verts=[]
    for zz in (z-width/2,z+width/2):
        for i in range(N):
            a=2*math.pi*i/N
            verts.append((cx+rx*math.cos(a),ry*math.sin(a),zz))
    faces=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return object_from_mesh(name,verts,faces,mat)

belt=ellipsoid_band("092 | separate waist leather belt",1.050,.190,.127,.044,leather)
buckle=box_mesh("092 | antique gold square buckle",(0,-.136,1.050),
                (.072,.014,.052),gold,.006)
inset=box_mesh("092 | buckle inset leather",(0,-.147,1.050),
               (.047,.011,.028),leather,.004)
pin=box_mesh("092 | metal buckle tongue",(.014,-.157,1.050),
             (.024,.008,.005),gold,.002)

pouches=[]
for sign,label in ((-1,"L"),(1,"R")):
    x=sign*.177
    pouches.append(box_mesh("092 | "+label+" leather belt pouch",
          (x,-.079,1.010),(.077,.079,.110),leather,.014))
    box_mesh("092 | "+label+" pouch top flap",
          (x,-.126,1.035),(.082,.012,.044),leather_lit,.006)
    box_mesh("092 | "+label+" pouch clasp",
          (x,-.137,1.016),(.013,.007,.021),gold,.002)

# Place embroidered gold strokes onto the actual FRONT trouser surface.
# This avoids floating decoration and respects the CC0-derived leg shape.
def on_surface(mesh_obj,x,z):
    src=Vector((x,-.65,z))
    hit,loc,norm,face=mesh_obj.ray_cast(src,Vector((0,1,0)))
    if not hit:
        return None
    return Vector((x,loc.y-.0042,z))

def trace(name,coords,mat,thickness=.0023):
    positions=[]
    for x,z in coords:
        p=on_surface(trousers,x,z)
        if p is not None:positions.append(p)
    if len(positions)<3:return None
    cr=bpy.data.curves.new(name,"CURVE")
    cr.dimensions="3D"
    cr.resolution_u=16
    cr.bevel_depth=thickness
    cr.resolution_u=16
    cr.bevel_resolution=2
    spline=cr.splines.new("POLY")
    spline.points.add(len(positions)-1)
    for point,v in zip(spline.points,positions):
        point.co=(*v,1)
    obj=bpy.data.objects.new(name,cr)
    bpy.context.scene.collection.objects.link(obj)
    cr.materials.append(mat)
    return obj

strokes=0
for sign,label in ((-1,"L"),(1,"R")):
    for row in range(3):
        z=.71+row*.075
        path=[(sign*(.110+.027*t/20),z+.024*math.sin(t/20*math.pi))
              for t in range(21)]
        if trace("092 | "+label+" thigh gold arc "+str(row),path,gold):strokes+=1
    # Gold thread on the lower outer leg, separate from bare feet.
    for row in range(2):
        z=.230+row*.038
        path=[(sign*(.106+.027*math.sin(t/20*math.pi)),z)
              for t in range(21)]
        if trace("092 | "+label+" cuff gold stitch "+str(row),path,gold):strokes+=1

# Bring life to the existing sculpted eyes without replacing its face topology.
def front_hit(x,z):
    # body.ray_cast is local-space. Translate ray and hit back to world-space.
    from_world=body.matrix_world.inverted_safe()
    o=from_world@Vector((x,-.6,z))
    d=(from_world.to_3x3()@Vector((0,1,0))).normalized()
    ok,loc,no,index=body.ray_cast(o,d)
    return (body.matrix_world@loc) if ok else None

def eye_disc(name,x,z,r,mat,depth):
    hit=front_hit(x,z)
    if hit is None:
        raise RuntimeError("Cannot project iris on CC0 face: "+name)
    cy=hit.y-depth
    verts=[(x,cy,z)]
    for i in range(24):
        a=2*math.pi*i/24
        verts.append((x+r*math.cos(a),cy,z+r*math.sin(a)))
    return object_from_mesh(name,verts,
          [(0,1+i,1+(i+1)%24) for i in range(24)],mat)

for sign,label in ((-1,"L"),(1,"R")):
    # Anchor to measured head position, keep asymmetric but anatomically paired.
    x=sign*.053
    eye_disc("092 | "+label+" muted iris",x,1.725,.0125,iris_mat,.0022)
    eye_disc("092 | "+label+" deep pupil",x,1.725,.0052,pupil_mat,.0040)

# Clean source is saved hidden for future sculpt passes; not exported.
for ob in base["selected_objects"]:
    if ob.type!="MESH":ob.hide_render=True

# Honest topology, source and outfit metadata, checked by CI.
metadata={
  "stage":"0.9.2 - silhouette, initial facial landmarks and distinct editable clothing/hair",
  "source":base["SOURCE"],"license":"CC0-1.0","bundle_version":"1.4.1",
  "asset_file":source_entry["file"],"asset_datablock":source_name,
  "blender_version":bpy.app.version_string,
  "base_vertices":original_vertex_count,"base_faces":original_face_count,
  "body_vertices_after_sculpt":len(body.data.vertices),
  "body_faces_after_sculpt":len(body.data.polygons),
  "anatomy_method":"proportional deformation of original Blender Studio vertices/quads",
  "hair_cards":len(hair_f),"hair_strand_count":115+33+2*24,
  "trouser_quads":len(trousers.data.polygons),
  "bracer_quads":sum(len(b.data.polygons) for b in bracers),
  "scalp_quads":len(scalp.data.polygons),
  "embroidered_curve_count":strokes,
  "rigged":False,"unity_character_replaced":False,
  "known_limitations":"Identity/ref face still needs side-by-side review against approved concept; no hand sculpt, UV authoring, retopology, rigging or animation. Hair/cards and tailoring are provisional."
}
(OUT/"source_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
(OUT/"asset_catalog.json").write_text(json.dumps(base["entries"],indent=2),encoding="utf-8")

# Set up genuine multi-view lighting BEFORE saving .blend (editable cameras).
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
world=bpy.data.worlds.new("092 | neutral dark studio")
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.14,.14,.17,1)
bg.inputs["Strength"].default_value=.75
scene.world=world
for name,pos,power,size in (
  ("Key",(2.4,-3,4.3),680,4.2),
  ("Fill",(-3,-1.5,2.5),350,3.3),
  ("Rim",(-1.3,2.4,3.3),570,3.0),
):
    ld=bpy.data.lights.new(name,"AREA")
    lo=bpy.data.objects.new(name,ld)
    scene.collection.objects.link(lo)
    lo.location=pos
    ld.energy=power
    ld.shape="DISK"
    ld.size=size
camdata=bpy.data.cameras.new("092 | inspection orthographic lens")
cam=bpy.data.objects.new("092 | inspection orthographic lens",camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO"
camdata.ortho_scale=2.23

# Save both editable Blender and FBX; no active Unity character changed.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"necromancer_character_092.blend"))
# Convert curves only in FBX scene: editable versions are already in .blend.
for curve_obj in [o for o in bpy.context.scene.objects if o.type=="CURVE" and not o.hide_render]:
    bpy.ops.object.select_all(action="DESELECT")
    curve_obj.hide_set(False)
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active=curve_obj
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type=="MESH" and not o.hide_render and not o.name.startswith("SOURCE"):
        o.hide_set(False)
        o.select_set(True)
if len(bpy.context.selected_objects)<8:
    raise RuntimeError("0.9.2 FBX export has unexpectedly few components")
bpy.ops.export_scene.fbx(filepath=str(OUT/"necromancer_character_092.fbx"),
       use_selection=True,object_types={"MESH"},apply_unit_scale=True,
       axis_forward="-Z",axis_up="Y",bake_space_transform=False)

def shot(name,location,target,scale,res_x=620,res_y=840):
    scene.render.resolution_x=res_x
    scene.render.resolution_y=res_y
    camdata.ortho_scale=scale
    cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/("character_"+name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_092",name,scene.render.filepath,flush=True)

for name,loc in (
    ("front",(0,-4.6,1.25)),
    ("side",(4.6,0,1.25)),
    ("back",(0,4.6,1.25)),
    ("threequarter",(3.0,-4.0,1.30)),
):
    shot(name,loc,(0,0,1.0),2.23)
shot("face_front",(0,-2.6,1.77),(0,0,1.75),.49,760,760)
shot("face_threequarter",(1.5,-2.3,1.8),(0,0,1.75),.50,760,760)
print("SUCCESS 0.9.2",json.dumps(metadata),flush=True)
