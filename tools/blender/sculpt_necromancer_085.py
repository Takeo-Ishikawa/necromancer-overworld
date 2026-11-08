"""Necromancer 0.8.5 — focused face / hairstyle reconstruction.

Run after generate_necromancer_083.py and sculpt_necromancer_084.py.
Designed for Blender 4.0 on GitHub Actions; no local modeling software needed.

Reference direction: adult anime male, angular eyes/eyebrows, narrow mature
jaw, small defined nose and mouth, voluminous short ash-lilac swept layers
with visible forehead and eyes. All hair and face components remain editable.
NOT a finished sculpt, rig or animation-ready facial topology.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene

def material(name, rgb, metallic=0, roughness=.74):
    m=bpy.data.materials.get(name)
    if m is None:
        m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value=(*rgb,1)
        bsdf.inputs["Metallic"].default_value=metallic
        bsdf.inputs["Roughness"].default_value=roughness
    return m

skin=material("Skin | muted warm porcelain",(.69,.486,.417))
shade=material("Skin | warm shading",(.48,.30,.275))
eyewhite=material("Face 085 | warm sclera",(.61,.525,.46))
iris=material("Face 085 | amber iris",(.43,.245,.125),.01)
pupil=material("Face 085 | dark pupil",(.082,.062,.062))
lash=material("Face 085 | dark slate lashes",(.075,.061,.080))
mouthcol=material("Face 085 | subtle lips",(.45,.272,.254))
hairbase=material("Hair 085 | silver lilac base",(.355,.317,.414))
hairl=material("Hair 085 | reflected silver",(.470,.423,.534))
hairm=material("Hair 085 | intermediate ash",(.390,.350,.451))
hairdark=material("Hair 085 | shaded underlayers",(.260,.228,.331))

def mesh(name, verts, faces, mat, smooth=True):
    data=bpy.data.meshes.new(name+" mesh")
    data.from_pydata(verts, [], faces)
    data.update()
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for f in data.polygons: f.use_smooth=smooth
    return obj

def stroke(name, coords, mat, radius=.0022):
    if len(coords)<2:
        return None
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions='3D'
    cu.resolution_u=16
    cu.bevel_depth=radius
    cu.bevel_resolution=3
    s=cu.splines.new("POLY")
    s.points.add(len(coords)-1)
    for p,v in zip(s.points,coords):p.co=(*v,1)
    o=bpy.data.objects.new(name,cu)
    scene.collection.objects.link(o)
    cu.materials.append(mat)
    return o

def oval(name,loc,radii,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc)
    obj=bpy.context.object
    obj.name=name
    obj.scale=radii
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    for p in obj.data.polygons:p.use_smooth=True
    return obj

def lock(name,coords,widths,mat,width_axis=(1,0,0)):
    """Mesh hair sweep, 8-vertex elliptical cross sections, fully tapered."""
    if len(coords)!=len(widths):
        raise ValueError("Hair sweep widths must match control points")
    axis=Vector(width_axis).normalized()
    # thickness orthogonal to both sweep and strand width.
    verts=[]
    n=8
    for i,(point,w) in enumerate(zip(coords,widths)):
        tangent=Vector(coords[min(i+1,len(coords)-1)])-Vector(coords[max(0,i-1)])
        if tangent.length<.00001:tangent=Vector((0,0,-1))
        tangent.normalize()
        orth=tangent.cross(axis)
        if orth.length<.001:orth=Vector((0,1,0))
        orth.normalize()
        for j in range(n):
            theta=j*math.tau/n
            p=Vector(point)+axis*math.cos(theta)*w+orth*math.sin(theta)*(w*.34)
            verts.append(tuple(p))
    faces=[tuple(reversed(range(n)))]
    for i in range(len(coords)-1):
        for j in range(n):
            k=(j+1)%n
            faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    faces.append(tuple((len(coords)-1)*n+j for j in range(n)))
    return mesh(name,verts,faces,mat)

def delete_named(prefixes):
    for ob in list(bpy.data.objects):
        if any(ob.name.startswith(prefix) for prefix in prefixes):
            bpy.data.objects.remove(ob,do_unlink=True)

# Remove the polygonal-bowl haircut, old dark, closed-looking eyelids and
# previous stylized ear coverings. The facial head mesh stays editable.
delete_named(("Hair |","Face | L ","Face | R ",
              "Face | restrained mouth","Face | sculpted angular nose"))

face=bpy.data.objects.get("Face | integrated jaw and forehead")
if face is None:
    raise RuntimeError("Missing 0.8.3 facial base; upstream generator changed.")

# Mature head planes (slightly sharper jaw / wider cheekbones / taper into chin).
for v in face.data.vertices:
    x,y,z=v.co
    front=max(0,min(1,(-y-.035)/.07))
    ax=abs(x)
    # defined cheekbone and the hollow beneath it, rather than round baby-face
    if 1.731<z<1.846:
        cheek=.008*math.exp(-((ax-.079)/.032)**2-((z-1.802)/.028)**2)
        hollow=.007*math.exp(-((ax-.064)/.042)**2-((z-1.743)/.027)**2)
        v.co.y-=front*(cheek-hollow)
    if z<1.770:
        taper=max(0,min(1,(1.77-z)/.088))
        v.co.x *= 1-.095*taper
        if y<-.026:v.co.y-=.006*taper
    # Slightly recessed sockets for deep-set, adult stylized eyes.
    if 1.818<z<1.853 and y<-.060:
        v.co.y+=.004*math.exp(-((ax-.059)/.041)**2-((z-1.834)/.018)**2)
face.data.update()

# Angular slender nasal bridge, with a small tip and a clean columella.
nose_verts=[
    (-.008,-.106,1.833),(.008,-.106,1.833),
    (-.009,-.113,1.807),(.009,-.113,1.807),
    (-.010,-.123,1.791),(.010,-.123,1.791),
    (-.016,-.112,1.783),(.016,-.112,1.783),
    (0,-.125,1.784),(0,-.105,1.816)
]
nose_faces=[
    (0,1,3,2),(2,3,5,4),(4,5,8),(4,8,6),(5,7,8),
    (0,2,9),(1,9,3),(6,8,7),(2,4,6,9),(3,9,7,5)
]
mesh("Face 085 | refined angular nose",nose_verts,nose_faces,skin)
# Natural, slightly closed lips and restrained cupid's bow.
stroke("Face 085 | fine mouth line",[
    (-.029,-.102,1.735),(-.019,-.110,1.732),
    (-.007,-.113,1.733),(0,-.114,1.731),
    (.009,-.113,1.733),(.021,-.110,1.732),
    (.030,-.102,1.735)],mouthcol,.0021)
stroke("Face 085 | lower lip hint",[
    (-.017,-.106,1.722),(0,-.109,1.720),(.018,-.106,1.722)],
    shade,.0008)

# Almond eye mesh, 6 stations each, with visible iris and angular lashes.
for side in (-1,1):
    side_name="L" if side<0 else "R"
    inner=.030
    outer=.100
    # Each lid has an asymmetric tilt: the outer eye corner is higher.
    upper=[]
    lower=[]
    verts=[]
    for j in range(9):
        t=j/8
        x=side*(inner+(outer-inner)*t)
        center=1.827 + .006*t
        aperture=math.sin(math.pi*t)
        top=center+.0075*aperture
        bottom=center-.006*aperture
        front_depth=-.119 + .0035*math.sin(math.pi*t)
        upper.append((x,front_depth-.005,top))
        lower.append((x,front_depth-.005,bottom))
        verts.append((x,front_depth,top))
    for j in range(9):
        t=j/8
        x=side*(inner+(outer-inner)*t)
        center=1.827+.006*t
        aperture=math.sin(math.pi*t)
        verts.append((x,-.120+.0035*math.sin(math.pi*t),
                      center-.006*aperture))
    faces=[(j,j+1,9+j+1,9+j) for j in range(8)]
    mesh("Face 085 | "+side_name+" visible ivory eye",verts,faces,eyewhite)
    stroke("Face 085 | "+side_name+" assertive upper eyeliner",
           upper,lash,.0031)
    stroke("Face 085 | "+side_name+" fine lower lid",
           lower,shade,.0014)
    # iris moves toward the nose for a focused confident expression
    iris_x=side*.062
    oval("Face 085 | "+side_name+" amber iris",
         (iris_x,-.128,1.828),(.010,.003,.009),iris)
    oval("Face 085 | "+side_name+" dark pupil",
         (iris_x,-.132,1.829),(.004,.002,.007),pupil)
    oval("Face 085 | "+side_name+" eye specular glint",
         (iris_x-side*.004,-.135,1.833),(.002,.0015,.003),eyewhite)
    # Inward-directed stern eyebrow, tapering to temple, not a thick band.
    brow=[
        (side*.028,-.107,1.861),
        (side*.046,-.116,1.866),
        (side*.070,-.114,1.865),
        (side*.100,-.100,1.868)
    ]
    stroke("Face 085 | "+side_name+" adult eyebrow",brow,hairdark,.0037)
    # Small, angular ear with narrow outer helix and inset concha.
    oval("Face 085 | "+side_name+" understated ear",
         (side*.118,.002,1.789),(.016,.020,.033),skin)
    stroke("Face 085 | "+side_name+" ear helix",[
        (side*.127,-.018,1.809),(side*.132,-.021,1.796),
        (side*.131,-.020,1.784),(side*.122,-.019,1.773)],shade,.0013)

# Rebuild the haircut to reflect the approved character:
# center-parted, wavy, short ash-lilac, 3D layered locks instead of a bowl.
# Fewer large shaped locks with roots embedded in a skull-hugging cap.
oval("Hair 085 | close-fitting scalp",
     (0,.012,1.938),(.115,.108,.048),hairbase)

# Back/temples: offset overlapping tapered clumps with gentle wavy S bends.
for i in range(25):
    a=math.tau*i/25+.08
    dx=math.cos(a);dy=math.sin(a)
    # Forehead locks are individually art-directed below; suppress the
    # evenly spaced radial spikes at the front of the head.
    if dy < -.24:
        continue
    tang=(-dy,dx,0)
    rear=max(0,dy)
    side_fraction=abs(dx)
    tip_z=1.857-.059*rear-.014*(i%3==0)
    # Less height and radial burst than previous versions.
    coords=[
        (.038*dx,.030*dy+.014,1.969),
        (.075*dx,.066*dy+.014,1.962),
        (.103*dx,.089*dy+.012,1.936),
        ((.113+.004*(i%3))*dx,(.104+.008*(i%3))*dy+.012,1.894),
        ((.120+.007*(i%3))*dx+.007*math.sin(i*2),
         (.113+.009*(i%3))*dy+.012,tip_z)
    ]
    color=hairl if i%8==0 else (hairdark if rear>.6 and i%3==0 else hairbase)
    lock("Hair 085 | shaped outer layer %02d"%i, coords,
         [.015,.021,.027,.021,.0009],color,tang)

# Frontal locks parted so that the eyes and eyebrows remain visible.
# Small grouped curtain fringe with asymmetry in length and direction.
for side in (-1,1):
    name="L" if side<0 else "R"
    for i in range(4):
        t=i/3
        start=side*(.018+.026*i)
        tip=side*(.041+.023*i)
        # Center locks lift above eyebrow; side locks descend toward temple.
        tz=1.896-.036*t + .011*math.sin(2.2*i)
        coords=[
            (start*.35,-.055,1.974),
            (start*.64,-.077,1.960),
            (start,-.093,1.936),
            ((start+tip)*.55,-.111,1.907),
            (tip,-.119,tz)
        ]
        lock("Hair 085 | "+name+" parted fringe %d"%i,
             coords,[.010,.018,.023,.017,.0009],
             hairl if i==1 else hairbase,(1,0,0))
    # Two deliberate layered temple locks, clear of the eyes.
    for i in range(3):
        xx=side*(.107+.009*i)
        coords=[
            (side*.087,-.025,1.959),
            (side*.110,-.035,1.932),
            (xx,-.041,1.887),
            (xx+side*.013,-.034,1.839-i*.018)
        ]
        lock("Hair 085 | "+name+" soft temple %d"%i,coords,
             [.012,.019,.018,.0008],
             hairdark if i==2 else hairm,(.70,0,.70))
    # Rear feathered layers hang toward the nape rather than forming a helmet.
    for i in range(4):
        xx=side*(.038+.021*i)
        coords=[
            (xx,.088,1.941),
            (xx+side*.012,.112,1.907),
            (xx+side*.018,.126,1.858),
            (xx+side*.012,.124,1.813-i*.006)
        ]
        lock("Hair 085 | "+name+" nape layer %d"%i,coords,
             [.014,.025,.024,.0006],
             hairdark if i%3==0 else hairm,(1,0,0))

# Preserve a newly editable .blend and export all visual mesh objects,
# with curves converted exclusively for FBX compatibility.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
bpy.ops.object.select_all(action="DESELECT")
for obj in scene.objects:
    if obj.type=="CURVE" and not obj.hide_render:
        obj.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for obj in scene.objects:
    if obj.type=="MESH" and not obj.hide_render:
        obj.hide_set(False)
        obj.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=os.path.join(ROOT,"character_base.fbx"),
    use_selection=True,
    object_types={'MESH'},
    apply_unit_scale=True,
    axis_forward='-Z',
    axis_up='Y'
)
print("0.8.5: expression, hair and face mesh built and exported.")
