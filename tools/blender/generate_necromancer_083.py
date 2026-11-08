"""Necromancer 0.8.3: new proportion-led parametric character mesh.

Runs without any local user tools via GitHub Actions / Blender 4.0.
Creates editable .blend, FBX and (in another script) orthographic renders.

This is a new 3D character *mesh*, NOT a sculpt-to-reference or animation rig.
Mesh construction uses designed cross-section surfaces instead of spheres for
the torso, face, arms, legs, trousers, hands and feet.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name != "Collection" and not col.objects:
        bpy.data.collections.remove(col)

def material(name, rgb, metal=0.0, rough=0.65):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    return mat

skin = material("Skin | muted warm porcelain", (0.72, 0.50, 0.44))
skin_depth = material("Skin | warm shading", (0.58, 0.35, 0.30))
iris = material("Eyes | dark amber", (0.16, 0.095, 0.075))
eyewhite = material("Eyes | ivory", (0.81, 0.71, 0.66))
hair = material("Hair | ash lavender", (0.37, 0.34, 0.43), rough=0.76)
hair_highlight = material("Hair | pale ash lilac", (0.54, 0.50, 0.60), rough=0.71)
hair_shadow = material("Hair | shadow lilac", (0.35, 0.32, 0.40), rough=0.77)
cloth = material("Trousers | midnight charcoal", (0.105, 0.091, 0.113))
cloth_folds = material("Trousers | dark charcoal cuffs", (0.085, 0.077, 0.093))
leather = material("Leather | black brown", (0.13, 0.083, 0.066))
leather_light = material("Leather | seams", (0.23, 0.14, 0.102))
bronze = material("Bronze | engraved aged gold", (0.58, 0.38, 0.15), metal=0.55, rough=0.40)

def make_mesh(name, vertices, faces, mat, smooth=True):
    data = bpy.data.meshes.new(name + " mesh")
    data.from_pydata(vertices, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = smooth
    return ob

def loft(name, rings, mat, count=32, deform=None):
    """rings: (height, center_x, center_y, radius_x, radius_y)"""
    verts = []
    for idx, (z,cx,cy,rx,ry) in enumerate(rings):
        for j in range(count):
            a = j * math.tau / count
            x = cx + rx * math.cos(a)
            y = cy + ry * math.sin(a)
            if deform:
                x,y,z2 = deform(idx,a,x,y,z)
            else:
                z2 = z
            verts.append((x,y,z2))
    faces = [tuple(reversed(tuple(range(count))))]
    for i in range(len(rings)-1):
        for j in range(count):
            k = (j+1)%count
            faces.append((i*count+j,i*count+k,(i+1)*count+k,(i+1)*count+j))
    faces.append(tuple((len(rings)-1)*count+j for j in range(count)))
    return make_mesh(name,verts,faces,mat)

def path_curve(name, points, mat, radius=0.003):
    cv = bpy.data.curves.new(name, 'CURVE')
    cv.dimensions = '3D'
    cv.resolution_u = 16
    cv.bevel_depth = radius
    cv.bevel_resolution = 3
    poly = cv.splines.new('POLY')
    poly.points.add(len(points)-1)
    for v, xyz in zip(poly.points, points):
        v.co = (*xyz, 1)
    ob = bpy.data.objects.new(name,cv)
    bpy.context.scene.collection.objects.link(ob)
    cv.materials.append(mat)
    return ob

def ellipsoid(name, center, scale, mat, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12, location=center)
    ob=bpy.context.object
    ob.name=name
    ob.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth=True
    return ob

def box(name, center, scale, mat, bevel=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob=bpy.context.object
    ob.name=name
    ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        m=ob.modifiers.new("Slight worn edges","BEVEL")
        m.width=bevel
        m.segments=2
        ob.modifiers.new("Weighted accessory normals","WEIGHTED_NORMAL")
    return ob

def ribbon_lock(name, points, mat):
    """Four-sided tapered organic hair lock with a continuous cross-section.
    points are (x,y,z,half_width); fringe geometry narrows to a sharp tip.
    """
    verts=[]
    for x,y,z,w in points:
        depth=max(0.0015, w*0.27)
        for dx,dy in ((-w,0),(0,-depth),(w,0),(0,depth)):
            verts.append((x+dx,y+dy,z))
    faces=[]
    for i in range(len(points)-1):
        for j in range(4):
            faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    faces.extend([(3,2,1,0),tuple((len(points)-1)*4+j for j in range(4))])
    return make_mesh(name,verts,faces,mat)

# 0.8.3 target: 1.92 m hero, elongated legs, realistic shoulder width.
# +X = character's left on screen; face towards -Y.
# No overlaid sphere "pectorals" or sphere deltoids. Muscle volume is
# integrated as subtle changes in the surface of the torso.
body_rings=[
    (1.025,0,0,0.200,0.127),
    (1.09,0,0,0.190,0.129),
    (1.15,0,0,0.190,0.132),
    (1.23,0,0,0.200,0.133),
    (1.31,0,0,0.225,0.146),
    (1.39,0,0,0.257,0.163),
    (1.46,0,0,0.303,0.164),
    (1.52,0,0,0.323,0.158),
    (1.57,0,0.007,0.286,0.140),
    (1.60,0,0.009,0.221,0.114),
    (1.625,0,0.013,0.118,0.094),
    (1.67,0,0.015,0.083,0.076),
    (1.705,0,0.014,0.082,0.074),
]
def muscle_surface(i,a,x,y,z):
    front=max(0.0,-math.sin(a))
    # Chest is a subtle frontward displacement, not an independent object.
    pec=(math.exp(-((abs(x)-0.155)/0.118)**2)
         * math.exp(-((z-1.465)/0.105)**2))
    y-=front*0.033*pec
    # Shallow abdominal planes; central sternum and linea alba stay recessed.
    for zh in (1.335,1.260,1.190):
        abs_shape=math.exp(-((abs(x)-0.075)/0.052)**2-((z-zh)/0.036)**2)
        y-=front*0.020*abs_shape
    # Center back muscle ridge.
    back=max(0.0,math.sin(a))
    y+=back*0.010*math.exp(-(x/0.035)**2-((z-1.41)/0.24)**2)
    return x,y,z
loft("Anatomy | continuous upper body",body_rings,skin,64,muscle_surface)
# Clavicle contour instead of the huge white spikes seen in 0.8.2.
for s,side in ((-1,"Left"),(1,"Right")):
    path_curve("Anatomy | "+side+" clavicle",[
        (s*0.02,-0.128,1.594),(s*0.085,-0.145,1.593),
        (s*0.19,-0.146,1.583),(s*0.275,-0.12,1.552)
    ],skin_depth,0.0017)
    path_curve("Anatomy | "+side+" subtle pectoral lower line",[
        (s*0.044,-0.171,1.414),(s*0.115,-0.186,1.402),
        (s*0.21,-0.183,1.418),(s*0.272,-0.146,1.448)
    ],skin_depth,0.0018)
# Navel is recessed and small.
ellipsoid("Anatomy | navel",(0,-0.142,1.18),(.006,.002,.005),skin_depth,12)

# Anatomically sloping adult face mesh (soft jaw, narrower chin).
head_rings=[
    (1.685,0,-0.022,0.055,0.054),
    (1.706,0,-0.017,0.077,0.072),
    (1.735,0,-0.010,0.093,0.092),
    (1.777,0,-0.006,0.107,0.098),
    (1.822,0,-0.002,0.118,0.103),
    (1.864,0,0,0.116,0.109),
    (1.898,0,0,0.103,0.107),
    (1.929,0,0.009,0.080,0.087),
    (1.946,0,0.020,0.038,0.052)
]
def face_form(i,a,x,y,z):
    front=max(0,-math.sin(a))
    y-=front*0.010*math.exp(-(x/0.022)**2-((z-1.784)/0.046)**2)
    return x,y,z
loft("Face | integrated jaw and forehead",head_rings,skin,48,face_form)
# Modest bridge and angular nose tip.
ellipsoid("Face | nose bridge",(0,-0.106,1.803),(.015,.012,.028),skin,20)
ellipsoid("Face | nose tip",(0,-0.116,1.772),(.018,.016,.011),skin,20)
path_curve("Face | restrained mouth",[
    (-0.029,-0.090,1.728),(-0.013,-0.099,1.726),
    (0,-0.101,1.726),(0.014,-0.099,1.726),
    (0.029,-0.090,1.729)],skin_depth,0.0015)
for s,side in ((-1,"L"),(1,"R")):
    ellipsoid("Face | "+side+" sculpted ear",
              (s*0.113,0.002,1.79),(.021,.026,.038),skin,16)
    # Large-but-narrow manga-style adult eyes with dark upper lash.
    eye_x=s*0.052
    path_curve("Face | "+side+" upper eyelid",[
        (eye_x-s*0.033,-0.101,1.824),
        (eye_x-s*0.010,-0.112,1.829),
        (eye_x+s*0.010,-0.112,1.827),
        (eye_x+s*0.035,-0.097,1.820)],hair_shadow,0.003)
    path_curve("Face | "+side+" lower eyelid",[
        (eye_x-s*0.030,-0.100,1.820),
        (eye_x,-0.114,1.817),
        (eye_x+s*0.032,-0.098,1.819)],skin_depth,0.0016)
    ellipsoid("Face | "+side+" iris",(eye_x,-0.116,1.821),
              (.009,.003,.011),iris,16)
    path_curve("Face | "+side+" eyebrow",[
        (eye_x-s*0.036,-0.099,1.852),
        (eye_x,-0.112,1.859),
        (eye_x+s*0.038,-0.099,1.852)],hair_shadow,0.004)

# Slim uninterrupted arms, naturally tapering down to bare hands.
for s,side in ((-1,"Left"),(1,"Right")):
    arm_rings=[
        # Deltoid begins as a narrow sloping root over the trapezius.
        # Extra upper rings prevent an artificial horizontal shoulder cap.
        (1.587,s*0.286,0.011,.038,.060),
        (1.556,s*0.311,0.012,.063,.077),
        (1.535,s*0.336,0.012,.079,.090),
        (1.505,s*0.355,0.010,.094,.102),
        (1.46,s*0.375,0.009,.100,.095),
        (1.41,s*0.390,0.008,.091,.091),
        (1.36,s*0.400,0.007,.084,.083),
        (1.30,s*0.415,0.005,.078,.081),
        (1.245,s*0.428,0.004,.067,.067),
        (1.20,s*0.432,0.002,.066,.065),
        (1.145,s*0.444,-0.004,.074,.071),
        (1.10,s*0.448,-0.009,.069,.064),
        (1.045,s*0.458,-0.013,.060,.056),
        (0.995,s*0.467,-0.016,.049,.049),
        (0.96,s*0.468,-0.018,.046,.044)
    ]
    loft("Anatomy | "+side+" arm",arm_rings,skin,28)
    # Deltoid is built into arm's top contours. Strap is narrow.
    loft("Armor | "+side+" etched upper arm band",[
        (1.387,s*0.395,0.008,.090,.089),
        (1.361,s*0.399,0.008,.089,.088)
    ],leather,28)
    path_curve("Armor | "+side+" upper band trim",[
        (s*0.487,-0.005,1.382),(s*0.489,-0.029,1.378),
        (s*0.485,-0.056,1.371)],bronze,0.0025)
    # The bracer covers the *forearm*, avoiding toy-like spherical cuffs.
    loft("Armor | "+side+" tapered bracer",[
        (1.177,s*0.439,-0.002,.075,.073),
        (1.137,s*0.446,-0.006,.078,.072),
        (1.089,s*0.449,-0.010,.071,.065),
        (1.032,s*0.460,-0.014,.058,.054),
        (1.018,s*0.461,-0.015,.056,.052)
    ],leather,28)
    for dz,rad in ((1.168,.077),(1.022,.058)):
        loft("Armor | "+side+" bronze bracer rim "+str(dz),[
            (dz+0.004,s*(0.440 if dz>1.1 else 0.461),-0.010,rad,rad*.94),
            (dz-0.004,s*(0.440 if dz>1.1 else 0.461),-0.010,rad,rad*.94)
        ],bronze,28)
    path_curve("Armor | "+side+" forearm filigree",[
        (s*0.448,-0.082,1.158),(s*0.452,-0.086,1.125),
        (s*0.460,-0.077,1.100),(s*0.465,-0.068,1.050)
    ],bronze,0.0032)
    # Separate glove and tapered bare digits.
    loft("Hands | "+side+" palm",[
        (0.978,s*0.466,-0.019,.046,.044),
        (0.937,s*0.467,-0.025,.044,.037),
        (0.901,s*0.465,-0.029,.040,.033)
    ],skin,20)
    loft("Armor | "+side+" fingerless glove",[
        (0.987,s*0.467,-0.019,.050,.049),
        (0.951,s*0.467,-0.019,.049,.044)
    ],leather,20)
    for finger in range(4):
        fx=s*0.466 + (finger-1.5)*0.019
        ln=0.048+0.006*(1-abs(finger-1.5)/2)
        loft("Hands | "+side+" finger "+str(finger),[
            (0.907,fx,-0.029,.010,.014),
            (0.891,fx,-0.035,.010,.012),
            (0.907-ln,fx,-0.042,.007,.009)
        ],skin,10)
    loft("Hands | "+side+" thumb",[
        (0.948,s*0.511,-0.037,.019,.017),
        (0.914,s*0.524,-0.052,.014,.013),
        (0.900,s*0.529,-0.057,.010,.011)
    ],skin,12)

# Trousers follow legs via smooth custom cloth surfaces, not cone + sphere joints.
loft("Garment | upper waist and seat",[
    (0.847,0,0.015,.234,.161),
    (0.912,0,0.012,.265,.173),
    (0.985,0,0,.258,.163),
    (1.062,0,0,.226,.139)
],cloth,48)
for s,side in ((-1,"Left"),(1,"Right")):
    rings=[]
    for i in range(23):
        z=0.500 + (0.980-0.500)*i/22
        u=(z-0.50)/0.48
        rx=0.146+0.008*math.sin(z*24)+0.015*u
        ry=0.141+0.010*math.sin(z*16+1)+0.009*u
        rings.append((z,s*(0.153-0.01*u),0.002,rx,ry))
    def fabric_wrinkles(i,a,x,y,z):
        factor=max(0.0,1.0-abs(z-0.72)*0.8)
        wave=0.006*math.sin(5*a+z*19)+0.004*math.cos(3*a-z*23)
        return x+math.cos(a)*wave*factor,y+math.sin(a)*wave*factor,z
    loft("Garment | "+side+" draped trouser leg",rings,cloth,32,fabric_wrinkles)
    loft("Garment | "+side+" rolled trouser cuff",[
        (0.505,s*0.153,0.002,.148,.142),
        (0.492,s*0.153,0.002,.150,.142),
        (0.473,s*0.153,0.002,.142,.136),
        (0.465,s*0.153,0.002,.134,.130)
    ],cloth_folds,32)
    # Calf is a tapered *leg*, not a thin stick.
    loft("Anatomy | "+side+" bare calf and heel",[
        (0.047,s*0.153,0.003,.043,.049),
        (0.095,s*0.153,0.005,.045,.049),
        (0.151,s*0.151,0.011,.050,.053),
        (0.24,s*0.147,0.014,.067,.069),
        (0.32,s*0.147,0.016,.073,.075),
        (0.41,s*0.149,0.013,.065,.065),
        (0.476,s*0.153,0.003,.055,.057)
    ],skin,24)
    # Foot horizontal cross-sections, toes point towards -Y.
    foot_sections=[
        (0.060,0.043,0.051),
        (0.021,0.045,0.046),
        (-0.053,0.048,0.039),
        (-0.135,0.062,0.036),
        (-0.199,0.066,0.032),
        (-0.240,0.056,0.027)
    ]
    verts=[]
    for yi,wx,h in foot_sections:
        for j in range(20):
            a=j*math.tau/20
            verts.append((s*0.153+wx*math.cos(a),yi,0.044+h*math.sin(a)))
    fs=[tuple(reversed(range(20)))]
    for j in range(len(foot_sections)-1):
        for k in range(20):
            n=(k+1)%20
            fs.append((j*20+k,j*20+n,(j+1)*20+n,(j+1)*20+k))
    fs.append(tuple((len(foot_sections)-1)*20+j for j in range(20)))
    make_mesh("Anatomy | "+side+" barefoot",verts,fs,skin)
    for t in range(5):
        # Visible distinct toes, decreasing gently to the outer edge.
        x=s*0.153+(t-2)*0.023
        reach=0.279-abs(t-1)*0.008
        ellipsoid("Anatomy | "+side+" toe "+str(t),
                  (x,-reach,0.032),(.012,.027,.018),skin,14)
    # Decorative golden lines, diagonal crossing motif and small diamond.
    xx=s*0.263
    path_curve("Embroidery | "+side+" winding stem",[
        (xx,-0.092,0.922),(xx-s*0.008,-0.108,0.864),
        (xx+s*0.009,-0.117,0.798),(xx-s*0.008,-0.119,0.734),
        (xx+s*0.005,-0.123,0.654),(xx,-0.122,0.564)
    ],bronze,0.0026)
    for z in (0.844,0.772,0.700,0.635):
        path_curve("Embroidery | "+side+" gothic leaf "+str(z),[
            (xx,-0.119,z+0.035),
            (xx+s*0.033,-0.128,z+0.015),
            (xx,-0.133,z-0.006),
            (xx-s*0.020,-0.124,z-0.029),
            (xx,-0.119,z-0.045)
        ],bronze,0.0021)
    path_curve("Embroidery | "+side+" hanging diamond",[
        (xx,-0.13,0.642),(xx+s*0.023,-0.131,0.612),
        (xx,-0.133,0.578),(xx-s*0.023,-0.130,0.612),
        (xx,-0.13,0.642)
    ],bronze,0.0027)

# Worn belt is compact and close to the waist; pouches are rectangular.
loft("Equipment | dark leather belt",[
    (1.068,0,0,.228,.145),
    (1.023,0,0,.231,.146)
],leather,48)
box("Equipment | rectangular bronze belt frame",(0,-0.150,1.046),
    (.084,.014,.056),bronze,0.010)
box("Equipment | inset black buckle",(0,-0.160,1.046),
    (.056,.008,.032),leather,0.006)
box("Equipment | belt prong",(-0.010,-0.168,1.046),
    (.035,.009,.008),bronze,0.002)
for s,side in ((-1,"Left"),(1,"Right")):
    box("Equipment | "+side+" leather hip pouch",
        (s*0.303,-0.023,1.002),(.096,.122,.148),leather,0.012)
    box("Equipment | "+side+" pouch flap",
        (s*0.304,-0.086,1.046),(.098,.026,.061),leather_light,0.008)
    box("Equipment | "+side+" brass clasp",
        (s*0.307,-0.104,1.037),(.016,.012,.024),bronze,0.003)
    for i in range(3):
        ellipsoid("Equipment | "+side+" belt stud "+str(i),
                  (s*(0.203+i*.026),-0.138,1.047),
                  (.005,.005,.005),bronze,12)
    path_curve("Equipment | "+side+" pouch stitched seam",[
        (s*.262,-.093,.950),(s*.258,-.094,1.001),
        (s*.258,-.091,1.028)
    ],leather_light,0.0018)

# Middle-parted ash-lavender haircut: chunky sculpted ribbons rather than
# many radial spikes; clearly visible ear, cheek and eyebrows.
ellipsoid("Hair | layered crown base",(0,0.016,1.916),
          (.126,.117,.066),hair,32)
for i in range(18):
    a=i*math.tau/18
    x=.096*math.cos(a)
    y=.090*math.sin(a)
    endx=x*1.33
    endy=y*1.40
    # Neck-level layers at rear; shorter at temples.
    zend=1.845+0.018*(i%3) if y<0 else 1.817+0.021*(i%4)
    ribbon_lock("Hair | textured crown lock %02d"%i,[
        (x*.50,y*.48,1.966,.020),
        (x,y,1.948,.033),
        (endx,endy,1.904,.024),
        (endx*1.12,endy*1.09,zend,.001)
    ],hair_highlight if i%4==0 else hair)
# Separate character-defining asymmetric parted fringe.
for s,side in ((-1,"Left"),(1,"Right")):
    for i in range(5):
        x=s*(.018+i*.023)
        end=s*(.032+i*.022)
        zend=1.827+(i%3)*.017
        ribbon_lock("Hair | "+side+" face-framing fringe "+str(i),[
            (x*.40,-0.062,1.962,.021),
            (x,-0.105,1.933,.028),
            (end,-0.123,1.881,.021),
            (end+s*.012,-0.120,zend,.001)
        ],hair_highlight if i in (0,3) else hair)
    for i in range(4):
        ribbon_lock("Hair | "+side+" nape feather "+str(i),[
            (s*(.075+i*.012),.060,1.919,.018),
            (s*(.107+i*.015),.097,1.867,.024),
            (s*(.129+i*.012),.121,1.812-i*.007,.001)
        ],hair_shadow if i%2 else hair)


# Hide editable source arm/torso sections and generate a single anatomically
# continuous shoulder region for inspection/export (not final retopology).
# This removes the visible capped shoulder cylinders while preserving editing
# access to the original surfaces in the .blend file.
anatomy_parts = [
    bpy.data.objects.get("Anatomy | continuous upper body"),
    bpy.data.objects.get("Anatomy | Left arm"),
    bpy.data.objects.get("Anatomy | Right arm")
]
if all(anatomy_parts):
    sources = bpy.data.collections.new("Editable anatomy source | hidden")
    bpy.context.scene.collection.children.link(sources)
    for part in anatomy_parts:
        replica = part.copy()
        replica.data = part.data.copy()
        sources.objects.link(replica)
        replica.name = "SOURCE | "+part.name
        replica.hide_render = True
        replica.hide_set(True)
    bpy.ops.object.select_all(action='DESELECT')
    for part in anatomy_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = anatomy_parts[0]
    bpy.ops.object.join()
    joint = bpy.context.object
    joint.name = "Anatomy | single torso and arms preview"
    joint.data.remesh_voxel_size = 0.009
    bpy.ops.object.voxel_remesh()
    smoothing = joint.modifiers.new("Blend shoulder junctions","SMOOTH")
    smoothing.factor=0.85
    smoothing.iterations=3
    bpy.context.view_layer.objects.active=joint
    bpy.ops.object.modifier_apply(modifier=smoothing.name)
    for face in joint.data.polygons:
        face.use_smooth=True

# The accessory meshes are deliberately separate and editable.
# Export all visible mesh and curve components; keep source in .blend.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type == 'CURVE' and not ob.hide_render:
        ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH' and not ob.hide_render:
        ob.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=os.path.join(ROOT,"character_base.fbx"),
    use_selection=True,
    object_types={'MESH'},
    apply_unit_scale=True,
    axis_forward='-Z', axis_up='Y'
)
print("Necromancer 0.8.3 silhouette mesh and editable assets generated.")
