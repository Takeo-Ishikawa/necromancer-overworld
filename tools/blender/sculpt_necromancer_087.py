"""Necromancer 0.8.7: hands, barefoot anatomy and softer muscle transitions.

Blender runs in GitHub Actions on the editable 0.8.6 project. Original
hand/foot components are preserved hidden inside the .blend, while new
continuous palms/fingers and feet/toes are built with quad lofts and voxel
unification. This is an artistically directed preview mesh, not production
retopology or a skinned animation asset.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene

def gauss(v,origin,spread):
    return math.exp(-((v-origin)/spread)**2)

def material(name,color):
    m=bpy.data.materials.get(name)
    if m is None:m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    shader=m.node_tree.nodes.get("Principled BSDF")
    if shader:shader.inputs["Base Color"].default_value=(*color,1)
    return m

skin=material("Skin | muted warm porcelain",(.69,.486,.417))
shade=material("Skin | warm shading",(.48,.30,.275))
nail=material("Anatomy 087 | natural fingernails",(.68,.52,.46))

def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name+" geometry")
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for face in me.polygons:face.use_smooth=True
    return ob

def loft(name, rings, mat, count=24):
    # Rings: (height, center_x, center_y, radius_x, radius_y), bottom to top.
    v=[]
    for z,cx,cy,rx,ry in rings:
        for j in range(count):
            angle=math.tau*j/count
            v.append((cx+rx*math.cos(angle),cy+ry*math.sin(angle),z))
    faces=[tuple(reversed(range(count)))]
    for i in range(len(rings)-1):
        for j in range(count):
            faces.append((i*count+j,i*count+(j+1)%count,
                (i+1)*count+(j+1)%count,(i+1)*count+j))
    faces.append(tuple((len(rings)-1)*count+j for j in range(count)))
    return mesh(name,v,faces,mat)

def ellipsoid(name,loc,scale,mat,segments=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=10,location=loc)
    ob=bpy.context.object
    ob.name=name
    ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    for face in ob.data.polygons:face.use_smooth=True
    return ob

def line(name,points,mat,radius=.0015):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    spline=cu.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p,xyz in zip(spline.points,points):
        p.co=(*xyz,1)
    ob=bpy.data.objects.new(name,cu)
    scene.collection.objects.link(ob)
    cu.materials.append(mat)
    return ob

source_collection=bpy.data.collections.new("Editable 0.8.7 predecessor hands and feet | hidden")
scene.collection.children.link(source_collection)

def preserve_and_remove(names):
    for name in names:
        obj=bpy.data.objects.get(name)
        if obj is None:continue
        old=obj.copy()
        old.data=obj.data.copy()
        source_collection.objects.link(old)
        old.name="SOURCE 086 | "+name
        old.hide_render=True
        old.hide_set(True)
        bpy.data.objects.remove(obj,do_unlink=True)

def unified_preview(parts,name,voxel=.0045):
    # A single surface avoids the disconnected-sausage appearance of separate
    # palm and finger shapes. Keep original parametric parts in hidden source.
    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    # Join must be applied to mesh-only parts.
    bpy.ops.object.join()
    joined=bpy.context.object
    joined.name=name
    joined.data.remesh_voxel_size=voxel
    bpy.ops.object.voxel_remesh()
    mod=joined.modifiers.new("Smooth knuckle and digit joins","SMOOTH")
    mod.factor=.65
    mod.iterations=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for polygon in joined.data.polygons:polygon.use_smooth=True
    bpy.ops.object.select_all(action="DESELECT")
    return joined

# Smoothed biceps, triceps and brachioradialis directly in unified body mesh.
body=bpy.data.objects.get("Anatomy | single torso and arms preview")
if body is None:
    raise RuntimeError("0.8.7 needs body from 0.8.6")
for vertex in body.data.vertices:
    x,y,z=vertex.co
    ax=abs(x)
    if .340<ax<.525 and 1.04<z<1.525:
        front=max(0,min(1,(-y-.007)/.086))
        back=max(0,min(1,(y-.005)/.085))
        biceps=.010*gauss(ax,.409,.075)*gauss(z,1.334,.085)
        triceps=.008*gauss(ax,.404,.070)*gauss(z,1.398,.085)
        forearm=.012*gauss(ax,.438,.067)*gauss(z,1.145,.078)
        vertex.co.y-=front*(biceps+forearm)
        vertex.co.y+=back*triceps
    if .155<ax<.29 and 1.21<z<1.49:
        # The anterior serratus joins thorax and waist without separate balls.
        front=max(0,min(1,(-y-.035)/.09))
        vertex.co.y-=front*.0035*gauss(ax,.22,.05)*gauss(z,1.31,.14)
body.data.update()

# New articulated-looking, relaxed finger silhouettes. Digits remain separate
# in parametric construction, then become a single surface with the palm.
for side,s in (("Left",-1),("Right",1)):
    preserve_and_remove(
        ["Hands | "+side+" palm","Hands | "+side+" thumb"]+
        ["Hands | "+side+" finger %d"%i for i in range(4)]
    )
    # The original fingerless glove was a floating cylindrical bracelet;
    # exposed hands match the reference better while forearm bracers remain.
    glove=bpy.data.objects.get("Armor | "+side+" fingerless glove")
    if glove is not None:
        bpy.data.objects.remove(glove,do_unlink=True)
    center=s*.466
    palm=loft("Hand 087 | "+side+" palm sections",[
        (.879,center,-.033,.034,.030),
        (.887,center,-.029,.041,.033),
        (.902,center,-.026,.042,.035),
        (.923,center,-.024,.043,.037),
        (.946,center,-.020,.040,.040),
        (.965,center,-.016,.039,.043),
        (.984,center,-.014,.036,.040)
    ],skin,28)
    components=[palm]
    # Fanned, subtly curved fingers with two knuckle shifts. Big middle
    # fingers are longer, little finger shorter; tips taper naturally.
    lengths=(.069,.090,.083,.062)
    starts=(-1.5,-.5,.5,1.5)
    for i,length in enumerate(lengths):
        fx=center+starts[i]*.021
        curve_y=-.030-.004*abs(starts[i])
        tip_z=.891-length
        components.append(loft("Hand 087 | "+side+" finger section %d"%i,[
            (tip_z,fx+s*.003*(i-1.5),curve_y-.012,.0075,.008),
            (tip_z+.009,fx+s*.003*(i-1.5),curve_y-.015,.0090,.010),
            (tip_z+.025,fx,curve_y-.009,.0108,.0110),
            (tip_z+.043,fx,curve_y-.003,.0115,.0118),
            (.909,fx,curve_y+.003,.012,.0125)
        ],skin,12))
    # Thumb rises out of the lateral hand, flexed gently inward.
    thumb_x=center+s*.045
    components.append(loft("Hand 087 | "+side+" opposable thumb",[
        (.867,thumb_x+s*.022,-.060,.010,.011),
        (.879,thumb_x+s*.020,-.056,.011,.012),
        (.894,thumb_x+s*.013,-.049,.014,.015),
        (.919,thumb_x,-.040,.019,.018),
        (.937,thumb_x-s*.009,-.030,.018,.020)
    ],skin,14))
    unified_preview(components,"Hand 087 | "+side+" continuous fingers and palm",.0034)
    # Nails and delicate tendon creases are deferred to the UV/texture stage.
    # Raised sphere nails and separate dark tendon wires looked pasted on.

    # Feet are built as varying-width organic oval sections from heel to
    # toes, then toes unify with the forefoot instead of looking like beads.
    preserve_and_remove(["Anatomy | "+side+" barefoot"]+
                        ["Anatomy | "+side+" toe "+str(i) for i in range(5)])
    # Section order follows heel at +Y toward toes at -Y.
    sections=[
        (.091,.043,.020,.088),
        (.055,.049,.017,.102),
        (.011,.048,.014,.094),
        (-.058,.052,.013,.087),
        (-.120,.061,.014,.087),
        (-.179,.067,.013,.076),
        (-.221,.061,.014,.063),
        (-.243,.051,.016,.048)
    ]
    # Each section: y, x-half-width, bottom_z, top_z.
    verts=[]
    count=24
    for y,r_x,zbottom,ztop in sections:
        zmid=(zbottom+ztop)*.5
        height=(ztop-zbottom)*.5
        for j in range(count):
            a=j*math.tau/count
            # Adjustable upper arch and stronger outer metatarsal flare.
            v_x=s*.153+r_x*math.cos(a)
            v_z=zmid+height*math.sin(a)
            verts.append((v_x,y,v_z))
    faces=[tuple(reversed(range(count)))]
    for j in range(len(sections)-1):
        for k in range(count):
            faces.append((j*count+k,j*count+(k+1)%count,
                          (j+1)*count+(k+1)%count,(j+1)*count+k))
    faces.append(tuple((len(sections)-1)*count+j for j in range(count)))
    foot=mesh("Foot 087 | "+side+" continuous instep and heel",verts,faces,skin)
    foot_parts=[foot]
    # Medial big toe is nearer body center: opposite of sign.
    # Toe locations continue the forefoot length with natural gradation.
    for i in range(5):
        fx=s*.153-s*.044+i*s*.022
        big=i==0
        ty=-.259+(0.012*i if i>=2 else 0.005*i)
        forward=.032 if big else (.029-.0035*i)
        rad=.017 if big else (.014-.0009*i)
        foot_parts.append(ellipsoid(
            "Foot 087 | "+side+" anatomical toe %d"%i,
            (fx,ty, .031 if big else .029),
            (rad,forward,.022 if big else .019),skin,14
        ))
    unified_preview(foot_parts,"Foot 087 | "+side+" unified barefoot with toes",.004)
    # Toenails are reserved for texture/UV work: the earlier raised caps
    # looked like glued-on beads at gameplay scale.
    x0=s*.153
    calf=bpy.data.objects.get("Anatomy | "+side+" bare calf and heel")
    if calf:
        # Smooth shin/calf silhouette: retain anatomical leg as base.
        for v in calf.data.vertices:
            x,y,z=v.co
            front=max(0,min(1,(-y-.01)/.08))
            if .14<z<.34:
                v.co.y-=front*.0075*gauss(z,.245,.082)
            # Very slight malleolus transitions from the actual calf surface;
            # no external ankle spheres that stick out like small knobs.
            if .075<z<.145:
                relative=(x-x0)*s
                v.co.x+=s*.004*gauss(relative,.044,.021)*gauss(z,.108,.025)
        calf.data.update()

# Blender source maintains editable curves, clothing, hair and anatomy.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))

# FBX export converts curves only after saving the editable .blend.
bpy.ops.object.select_all(action="DESELECT")
for ob in scene.objects:
    if ob.type=="CURVE" and not ob.hide_render:
        ob.hide_set(False)
        ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
    bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
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
print("0.8.7 anatomical hands, five-toed bare feet and arm transitions exported.")
