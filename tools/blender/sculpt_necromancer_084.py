"""Necromancer 0.8.4 — reference-driven anatomical and styling pass.

Run against the generated 0.8.3 blend, before rendering, on GitHub Actions:
 blender -b tools/blender/character_base.blend --python tools/blender/sculpt_necromancer_084.py

Improves body relief by editing the actual unified anatomical surface;
rebuilds hair into tapered layered sweeps, refines the adult face,
lengthens/tapers trouser legs and adds restrained engraved ornaments.
All generated objects remain editable; no local Blender installation needed.
This is a geometry iteration, not final hand-sculpt/rig/retopology.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene

def mat_color(name, rgb):
    m=bpy.data.materials.get(name)
    if m is None:
        raise RuntimeError("Expected material missing: "+name)
    m.diffuse_color=(*rgb,1.0)
    if m.use_nodes:
        shader=m.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Base Color"].default_value=(*rgb,1.0)
    return m

skin=mat_color("Skin | muted warm porcelain",(.67,.455,.387))
skinshade=mat_color("Skin | warm shading",(.46,.275,.245))
bronze=mat_color("Bronze | engraved aged gold",(.59,.365,.155))
hairmat=mat_color("Hair | ash lavender",(.425,.386,.473))
hairlight=mat_color("Hair | pale ash lilac",(.57,.525,.616))
hairdark=mat_color("Hair | shadow lilac",(.305,.277,.355))
cloth=mat_color("Trousers | midnight charcoal",(.070,.061,.082))
clothshade=mat_color("Trousers | dark charcoal cuffs",(.057,.052,.070))
leather=bpy.data.materials.get("Leather | black brown")

def gauss(a, c, w):
    return math.exp(-((a-c)/w)**2)

def clamp(v,a=0,b=1):
    return max(a,min(b,v))

def mesh(name, vertices, faces, material):
    me=bpy.data.meshes.new(name+" mesh")
    me.from_pydata(vertices, [], faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    scene.collection.objects.link(ob)
    ob.data.materials.append(material)
    for polygon in me.polygons: polygon.use_smooth=True
    return ob

def line(name, positions, material, thickness=.0019):
    data=bpy.data.curves.new(name,"CURVE")
    data.dimensions="3D"
    data.bevel_depth=thickness
    data.bevel_resolution=3
    spline=data.splines.new("POLY")
    spline.points.add(len(positions)-1)
    for p,xyz in zip(spline.points,positions):
        p.co=(*xyz,1)
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    data.materials.append(material)
    return obj

def drop(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            bpy.data.objects.remove(ob,do_unlink=True)

# The new central anatomical mesh from 0.8.3, already remeshed to remove joins.
body=bpy.data.objects.get("Anatomy | single torso and arms preview")
if not body:
    raise RuntimeError("Missing 0.8.3 torso/arm mesh; run 0.8.3 generator first")

# Actual silhouette displacement, not muscle balls glued onto the surface.
# Carefully restrict sculpt to the front so the back is not inadvertently moved.
for vert in body.data.vertices:
    x,y,z=vert.co
    front=clamp((-y-.062)/.083)
    back=clamp((y-.065)/.085)
    ax=abs(x)
    if 1.145<=z<=1.575 and ax < .320:
        relief=0.0
        # Anatomically broad clavicular / sternal pectorals.
        pec=gauss(ax,.172,.120)*gauss(z,1.468,.074)
        relief+=.042*pec*(.75+.25*gauss(ax,.155,.08))
        # Inner-sternal valley and lower pectoral attachment.
        relief-=.013*gauss(x,0,.028)*gauss(z,1.465,.09)
        relief-=.010*gauss(ax,.165,.12)*gauss(z,1.392,.014)
        # Three paired abdominal bellies; gradually flatten lower abdomen.
        for row_z,size in ((1.332,.026),(1.260,.031),(1.195,.025)):
            relief+=size*gauss(ax,.074,.050)*gauss(z,row_z,.034)
        # Central linea alba and tendon intersections.
        relief-=.010*gauss(x,0,.016)*gauss(z,1.267,.18)
        for row_z in (1.298,1.224):
            relief-=.009*gauss(ax,.076,.080)*gauss(z,row_z,.009)
        # Obliques/serratus at the lateral rib cage.
        for oz in (1.346,1.281,1.223):
            relief+=.009*gauss(ax,.184,.054)*gauss(z,oz,.023)
        vert.co.y -= relief*front
    # Trapezius, rear deltoid and latissimus: visible from behind.
    if 1.26 < z < 1.62 and ax<.310:
        back_relief=(.021*gauss(ax,.135,.070)*gauss(z,1.56,.11)
                   + .011*gauss(ax,.23,.055)*gauss(z,1.45,.12))
        vert.co.y+=back*back_relief
    # Taper extreme barrel shoulders slightly, retaining athletic silhouette.
    if .345 < ax < .51 and 1.40 < z < 1.585:
        shoulder_softening=.015*gauss(ax,.44,.065)*gauss(z,1.535,.055)
        vert.co.x-=math.copysign(shoulder_softening,x)
body.data.update()

def surface_y(x,z,reverse=False):
    origin=Vector((x,2.0 if reverse else -2.0,z))
    vec=Vector((0,-1 if reverse else 1,0))
    hit, loc,normal, idx=body.ray_cast(origin,vec, distance=5.0)
    if not hit: return None
    return loc.y+(.003 if reverse else -.003)

def contour(name, xzs, mat, r=.0017, reverse=False):
    points=[]
    for x,z in xzs:
        y=surface_y(x,z,reverse)
        if y is not None:
            points.append((x,y,z))
    if len(points)>=2: line(name,points,mat,r)

# Subtle muscular insets follow the surface; no protruding spheres.
for s,side in ((-1,"L"),(1,"R")):
    contour("Sculpt | "+side+" pectoral lower shadow",
        [(s*x,z) for x,z in ((.035,1.409),(.080,1.404),(.146,1.403),
                              (.207,1.415),(.260,1.437))],skinshade,.0016)
    contour("Sculpt | "+side+" pectoral sternum",
        [(s*x,z) for x,z in ((.020,1.512),(.024,1.490),
                              (.030,1.465),(.033,1.433))],skinshade,.00115)
    for row,(ztop,zbottom) in enumerate(((1.359,1.310),(1.289,1.239),(1.221,1.170))):
        contour("Sculpt | "+side+" abdominal groove "+str(row),
            [(s*x,z) for x,z in ((.116,ztop),(.132,(ztop+zbottom)*.5),
                                  (.113,zbottom))],skinshade,.00105)
    contour("Sculpt | "+side+" oblique diagonals",[
        (s*.225,1.327),(s*.198,1.300),(s*.203,1.282),
        (s*.177,1.258),(s*.196,1.242)],skinshade,.0011)
    contour("Sculpt | "+side+" scapula line",
        [(s*.055,1.588),(s*.121,1.556),(s*.155,1.504),
         (s*.205,1.468)],skinshade,.0012,True)

# Replace cartoonish round nose with a restrained polygonal nose bridge.
for name in ("Face | nose bridge","Face | nose tip"):
    ob=bpy.data.objects.get(name)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)
nose_verts=[
    (-.012,-.106,1.837),(.012,-.106,1.837),
    (-.011,-.116,1.805),(.011,-.116,1.805),
    (-.013,-.134,1.782),(.013,-.134,1.782),
    (-.019,-.117,1.771),(.019,-.117,1.771),
    (0,-.129,1.768),(0,-.101,1.810)
]
nose_faces=[
    (0,1,3,2),(2,3,5,4),(4,5,8),(4,8,6),(5,7,8),
    (0,2,9),(1,9,3),(6,8,7),(2,4,6,9),(3,9,7,5)
]
mesh("Face | sculpted angular nose",nose_verts,nose_faces,skin)
face=bpy.data.objects.get("Face | integrated jaw and forehead")
if face:
    for v in face.data.vertices:
        x,y,z=v.co
        if z<1.775:
            # adult tapered chin, sharper cheek transition
            strength=clamp((1.775-z)/.077)
            v.co.x *= (1-.14*strength)
            v.co.y -= .006*strength if y<0 else 0
        if 1.810<z<1.851 and y<-.062:
            # ocular socket plane, makes adult eyes sit in the skull
            v.co.y += .009*gauss(abs(x),.056,.038)*gauss(z,1.828,.019)
    face.data.update()
# Eyebrow contours become finer, less severe than original solid sticks.
for ob in list(bpy.data.objects):
    if "eyebrow" in ob.name and ob.type=="CURVE":
        ob.data.bevel_depth=.0032

# Replace the radial short spikes with a layered center-parted cut, styled
# in sweeping locks and feathered sides, matching the original visual concept.
drop("Hair |")
def ellipsoid(name, loc, radii, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
    ob=bpy.context.object
    ob.name=name
    ob.scale=radii
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth=True
    return ob

def strand(name, coords, widths, material, direction=None):
    """Smooth layered cross-section strand, 8 sides, tapering toward tip."""
    n=9
    v=[]
    if direction is None:
        vx=coords[-1][0]-coords[0][0]
        vy=coords[-1][1]-coords[0][1]
        ll=max(.0001,math.hypot(vx,vy))
        # For frontal hair mostly use X-axis strip width.
        tangent=Vector((-vy/ll,vx/ll,0))
    else:
        tangent=Vector(direction)
    for (x,y,z),w in zip(coords,widths):
        for j in range(n):
            a=j*math.tau/n
            point=Vector((x,y,z))+tangent*(w*math.cos(a))+Vector((0,0,1))*(w*.26*math.sin(a))
            v.append(tuple(point))
    f=[tuple(reversed(range(n)))]
    for ring in range(len(coords)-1):
        for j in range(n):
            k=(j+1)%n
            f.append((ring*n+j,ring*n+k,(ring+1)*n+k,(ring+1)*n+j))
    f.append(tuple((len(coords)-1)*n+j for j in range(n)))
    return mesh(name,v,f,material)

ellipsoid("Hair | closely fitted crown",(0,.016,1.924),(.115,.113,.051),hairmat)
# Layered hair tufts curve down to the nape and sweep around ears.
for i in range(28):
    a=math.tau*i/28
    x=math.cos(a)
    y=math.sin(a)
    xx=.102*x
    yy=.091*y
    long_at_back=1 if y>0.05 else 0
    endz=1.855 + .022*((i*7)%5)/5.0 - .055*long_at_back
    # inward crowns and outward tapered tips, not right-angle spikes
    coords=[
        (.045*x,.037*y,1.963),
        (.077*x,.066*y,1.953),
        (xx,yy,1.922),
        (x*(.123+.007*(i%3)),y*(.117+.009*(i%3)),1.890),
        (x*(.129+.007*(i%3)),y*(.124+.008*(i%3)),endz)
    ]
    strand("Hair | crown layered wave %02d"%i,coords,
           [.017,.024,.027,.020,.0015],
           hairlight if i%6==0 else (hairdark if i%5==0 else hairmat))
# Character-defining curtain fringe with an open center and asymmetric flow.
for s,side in ((-1,"Left"),(1,"Right")):
    for i in range(7):
        root=s*(.016+i*.015)
        end=s*(.035+i*.017)
        # Fringe rests above eyes at center, then drops toward sideburns.
        ztip=1.870-.024*(i/6)+(.006 if (i%3)==0 else 0)
        coords=[
            (root*.62,-.046,1.961),
            (root*.91,-.078,1.960),
            (root,-.103,1.934),
            ((root+end)/2,-.125,1.886),
            (end,-.120,ztip)
        ]
        strand("Hair | "+side+" parted fringe %d"%i,coords,
               [.020,.029,.033,.023,.0008],
               hairlight if i in (1,5) else hairmat,
               Vector((1,0,0)))
    for j in range(4):
        x=s*(.123+j*.006)
        strand("Hair | "+side+" temple sweep %d"%j,[
            (s*.097,-.019,1.946),
            (x,-.008,1.909),
            (x+s*.010,-.030,1.876),
            (x+s*.008,-.042,1.815-j*.008)
        ],[.019,.027,.019,.001],hairmat)
    for j in range(6):
        x=s*(.037+j*.013)
        strand("Hair | "+side+" layered nape %d"%j,[
            (x,.080,1.934),
            (s*(.052+j*.013),.112,1.903),
            (s*(.063+j*.015),.133,1.854),
            (s*(.065+j*.014),.133,1.808-(j%3)*.009)
        ],[.013,.025,.023,.001],hairdark if j%3==0 else hairmat)

# The image has long trousers to below the knees with slender bare calves,
# rather than short cylinder-like bloomers.
for side in ("Left","Right"):
    leg=bpy.data.objects.get("Garment | "+side+" draped trouser leg")
    cuff=bpy.data.objects.get("Garment | "+side+" rolled trouser cuff")
    calf=bpy.data.objects.get("Anatomy | "+side+" bare calf and heel")
    if not all((leg,cuff,calf)):
        raise RuntimeError("Missing lower-body section for "+side)
    for v in leg.data.vertices:
        x,y,z=v.co
        # extend trousers ~12 cm lower while maintaining hip position
        zn=.365+(z-.500)*(.980-.365)/(.980-.500)
        # narrow upper thighs, open pant cuff, sculpt longitudinal creases
        k=clamp((zn-.365)/(.980-.365))
        cx=(-1 if side=="Left" else 1)*(.153-.010*clamp((z-.50)/.48))
        factor=.95-.10*k
        wave=(.012*gauss(zn,.435,.065)+.005)*math.sin(4.8*math.atan2(y-.002,x-cx)+zn*14)
        v.co.x=cx+(x-cx)*factor + .50*wave*math.cos(math.atan2(y-.002,x-cx))
        v.co.y=(y-.002)*factor+.002+.50*wave*math.sin(math.atan2(y-.002,x-cx))
        v.co.z=zn
    for v in cuff.data.vertices: v.co.z-=.122
    for v in calf.data.vertices:
        # hide top of calf inside the newly extended trouser cuff
        z=v.co.z
        if z>.09:
            v.co.z=.09+(z-.09)*(.352-.09)/(.476-.09)
    # Cloth side seams and upper/lower stitched edges.
    sign=-1 if side=="Left" else 1
    line("Garment | "+side+" seam front",[
        (sign*.289,-.059,.917),(sign*.293,-.08,.827),
        (sign*.287,-.104,.715),(sign*.293,-.111,.585),
        (sign*.293,-.106,.453)
    ],clothshade,.0022)
    # Slim cuff piping
    line("Garment | "+side+" cuff decorative lip",[
        (sign*.153-.110,-.092,.371),
        (sign*.153-.07,-.128,.366),
        (sign*.153,-.142,.364),
        (sign*.153+.07,-.124,.367),
        (sign*.153+.110,-.090,.370)
    ],bronze,.0019)

# Larger, hanging side satchel silhouette rather than tiny cubical blocks.
for side in ("Left","Right"):
    pouch=bpy.data.objects.get("Equipment | "+side+" leather hip pouch")
    flap=bpy.data.objects.get("Equipment | "+side+" pouch flap")
    if pouch:
        pouch.dimensions=(.118,.120,.190)
        pouch.location.z=.970
    if flap:
        flap.dimensions=(.121,.028,.070)
        flap.location.z=1.037
    # Etched golden scroll on wrist-guard; heavy enough to remain legible.
    sign=-1 if side=="Left" else 1
    line("Armor | "+side+" bronze floral scroll",[
        (sign*.435,-.082,1.145),
        (sign*.445,-.091,1.122),
        (sign*.467,-.076,1.105),
        (sign*.455,-.074,1.092),
        (sign*.440,-.072,1.107),
        (sign*.451,-.068,1.067)
    ],bronze,.0033)
# Save editable file. Curves are kept as curves in Blender then converted
# exclusively for the final FBX (Unity exports mesh objects only).
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=="CURVE" and not ob.hide_render:
        ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=="MESH" and not ob.hide_render:
        ob.hide_set(False)
        ob.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=os.path.join(ROOT,"character_base.fbx"),
    use_selection=True,
    object_types={"MESH"},
    apply_unit_scale=True,
    axis_forward="-Z",axis_up="Y"
)
print("Necromancer 0.8.4 reference-driven geometry, editable .blend and FBX exported.")
