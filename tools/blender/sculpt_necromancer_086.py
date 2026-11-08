"""Necromancer 0.8.6 — silhouette, draped trouser and equipment pass.

Run on the 0.8.5 saved .blend, then render the actual 3D scene.
Keeps body, equipment and clothing source objects individually editable.
The procedural geometry is a preview asset, NOT final sculpt or rig.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene

def gaussian(x, center, radius):
    return math.exp(-((x-center)/radius)**2)

def smoothstep(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)

def get(name):
    ob=bpy.data.objects.get(name)
    if ob is None:
        raise RuntimeError("0.8.6 expected upstream object: " + name)
    return ob

def erase(prefixes):
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(p) for p in prefixes):
            bpy.data.objects.remove(obj,do_unlink=True)

def curve(name,points,mat,radius=.0021,closed=False):
    if len(points)<2: return None
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.bevel_depth=radius
    cu.bevel_resolution=3
    spl=cu.splines.new("POLY")
    spl.points.add(len(points)-1)
    for p,coord in zip(spl.points,points):
        p.co=(*coord,1)
    spl.use_cyclic_u=closed
    obj=bpy.data.objects.new(name,cu)
    scene.collection.objects.link(obj)
    cu.materials.append(mat)
    return obj

bronze=bpy.data.materials["Bronze | engraved aged gold"]
leather=bpy.data.materials["Leather | black brown"]
leather_seam=bpy.data.materials["Leather | seams"]
cloth=bpy.data.materials["Trousers | midnight charcoal"]
cloth_dark=bpy.data.materials["Trousers | dark charcoal cuffs"]
skin=bpy.data.materials["Skin | muted warm porcelain"]

# 1. Shoulder and torso silhouette: the concept shows a smooth transition
# from trapezius to rounded deltoid. The previous cap had a toy-like ledge.
body=get("Anatomy | single torso and arms preview")
for v in body.data.vertices:
    x,y,z=v.co
    ax=abs(x)
    sign=1 if x>0 else -1
    # Gradual narrowing from the top chest into the shoulder and arm.
    shoulder=gaussian(z,1.494,.172)*smoothstep(.24,.43,ax)
    arm=smoothstep(.345,.49,ax)*smoothstep(1.025,1.30,z)
    narrowing=.036*shoulder+.012*arm
    v.co.x=x-sign*narrowing
    # Round top of deltoid downward subtly; avoid the horizontal shelf.
    if ax>.255 and 1.46<z<1.625:
        topmask=gaussian(z,1.560,.064)*smoothstep(.275,.48,ax)
        v.co.z=z-.014*topmask
    # Lift anterior deltoid shape without creating separate visible lumps.
    if ax>.30 and 1.37<z<1.55 and y<-.030:
        v.co.y-=.009*gaussian(z,1.465,.077)*gaussian(ax,.39,.10)
    # Remove the harsh inflated flat-shelf chest plane.
    if ax<.28 and 1.39<z<1.55 and y<-.10:
        v.co.y+=.011*gaussian(z,1.49,.065)*(1-ax/.38)
body.data.update()
# Small smoothing relaxation is applied to the whole model mesh.
bpy.ops.object.select_all(action="DESELECT")
body.hide_set(False)
body.select_set(True)
bpy.context.view_layer.objects.active=body
modifier=body.modifiers.new("Relax shoulder facet transitions","SMOOTH")
modifier.factor=.53
modifier.iterations=2
bpy.ops.object.modifier_apply(modifier=modifier.name)
body.select_set(False)

# Equipment was built around the old arm centerline; follow the actual
# sculpted arm to prevent the leather band and its brass trim from floating.
for side,sgn in (("Left",-1),("Right",1)):
    band=get("Armor | "+side+" etched upper arm band")
    band.location.x -= sgn*.023
    trim=bpy.data.objects.get("Armor | "+side+" upper band trim")
    if trim is not None:
        trim.location.x -= sgn*.030

# Older clavicle and pectoral curves were too sharp and were read as seams.
for ob in scene.objects:
    if ob.type=="CURVE" and (
       "clavicle" in ob.name.lower() or
       "pectoral lower" in ob.name.lower() or
       "pectoral sternum" in ob.name.lower()
    ):
        ob.data.bevel_depth=min(.0011,ob.data.bevel_depth)

# 2. Give the adult face slightly more presence in relation to the shoulders,
# while retaining existing coordinates and editable objects.
for obj in scene.objects:
    if obj.name.startswith(("Face |","Face 085 |","Hair 085 |")):
        if obj.type in {"MESH","CURVE"}:
            obj.location.x*=1.06
            obj.scale.x*=1.06
# The rest of the face/hair sculpt remains intact.

# 3. Replace rigid trouser cylinders with intentional cloth weight, a shaped
# knee volume, asymmetry and depth-varying folds. Geometry is still separate
# and the embroidered pattern is laid exactly onto its actual 3D surface.
for side,sign in (("Left",-1),("Right",1)):
    trouser=get("Garment | "+side+" draped trouser leg")
    for v in trouser.data.vertices:
        x,y,z=v.co
        center=sign*.152
        dx=x-center
        dy=y-.002
        a=math.atan2(dy,dx)
        u=smoothstep(.355,.970,z)
        # More natural hip shape, broader knee, visibly gathered hem.
        shape=1-.055*u+.018*gaussian(z,.515,.15)
        v.co.x=center+dx*shape
        v.co.y=.002+dy*shape
        # Vertical fabric creases taper along the leg and move with the cloth.
        pleat=(
            .015*math.sin(a*4.0+z*8.2)+
            .008*math.sin(a*7.0-z*13.0)+
            .006*math.cos(a*2.0+z*25.0)
        )
        front=max(0,-math.sin(a))
        pleat*=.40+.60*front
        v.co.x+=math.cos(a)*pleat
        v.co.y+=math.sin(a)*pleat
        # Gathered front fold above cuff and one relaxed knee crease.
        if front>.20:
            v.co.y-=front*.011*gaussian(z,.515,.038)*gaussian(math.cos(a),.45,.46)
            v.co.y+=front*.006*gaussian(z,.708,.075)*math.sin(a*5.0+1.2)
        if z<.46:
            v.co.z+=.009*math.sin(5*a+sign*.65)*smoothstep(.45,.365,z)*-1
    trouser.data.update()
    cuff=get("Garment | "+side+" rolled trouser cuff")
    for v in cuff.data.vertices:
        x,y,z=v.co
        a=math.atan2(y-.002,x-sign*.153)
        # Break perfectly circular cuffs and give a sewn gather.
        v.co.x+=.008*math.cos(a)*math.sin(4*a+sign)*.65
        v.co.y+=.008*math.sin(a)*math.sin(4*a+sign)*.65
        v.co.z+=.006*math.cos(3*a+sign*.7)
    cuff.data.update()

seat=get("Garment | upper waist and seat")
for v in seat.data.vertices:
    x,y,z=v.co
    # Pull the front upper pant inward so it no longer resembles underwear.
    front=max(0,min(1,(-y-.055)/.10))
    v.co.y+=front*(.030*gaussian(z,.972,.12)+.018*gaussian(z,.870,.085))
    if abs(x)>.200 and z>1.010:
        v.co.x-=math.copysign(.007*gaussian(z,1.045,.07),x)
seat.data.update()

# Remove the old ribbon-like zigzag motifs. Instead produce winding gold
# embroidery following the *front surface* of the pants, never floating.
erase(("Embroidery |","Garment | Left seam front","Garment | Right seam front",
       "Garment | Left cuff decorative lip","Garment | Right cuff decorative lip"))

def rayfront(obj,x,z,extra=.003):
    # The trouser mesh is authored in local coordinates, with identity matrix.
    hit,pos,norm,face=obj.ray_cast(Vector((x,-2.0,z)),Vector((0,1,0)),distance=4)
    if not hit:return None
    return pos.y-extra

for side,sign in (("Left",-1),("Right",1)):
    pant=get("Garment | "+side+" draped trouser leg")
    def embroidered_curve(label,xz,thickness=.0022):
        xyz=[]
        for x,z in xz:
            y=rayfront(pant,x,z)
            if y is not None: xyz.append((x,y,z))
        if len(xyz)>1:curve("Embroidery 086 | "+side+" "+label,xyz,bronze,thickness)
    # Position near outer front thigh to mimic fine hand-embroidered vines.
    samples=[]
    for i in range(65):
        t=i/64
        z=.865-t*.445
        x=sign*(.239+.012*math.sin(t*math.tau*1.65)+.004*math.sin(t*math.tau*4))
        samples.append((x,z))
    embroidered_curve("continuous wandering gilt vine",samples,.0021)
    # Vine ornaments are irregular, tapered, with asymmetric leaf clusters.
    for j,zc in enumerate((.833,.720,.602,.490) if side=="Right" else (.807,.665,.536)):
        x0=sign*(.239+.010*math.sin((.865-zc)/.445*math.tau*1.65))
        for k in ((-1,) if j%2 else (1,)):
            points=[]
            for i in range(9):
                t=i/8
                z=zc+.041*(t-.5)
                reach=.029*math.sin(math.pi*t)
                x=x0+sign*k*reach
                points.append((x,z))
            embroidered_curve("leaf %d.%d"%(j,k),points,.00175)
        embroidered_curve("leaf vein %d"%j,[
            (x0,zc+.031),(x0+sign*.009,zc+.005),
            (x0+sign*.004,zc-.030)],.00135)
    # Diamond below the vine; angled and long like the concept's sigil.
    x0=sign*.24
    embroidered_curve("lower woven diamond",[
       (x0,.526),(x0+sign*.025,.488),
       (x0,.451),(x0-sign*.025,.488),(x0,.526)],.00235)
    # Cloth seam only where the geometry exists.
    xseam=sign*.282
    embroidered_curve("subtle vertical outer seam",[
        (xseam,.910),(xseam,.825),(xseam,.735),
        (xseam,.650),(xseam,.535),(xseam,.425)],.00115)

# 4. Equipment should not resemble two identical rectangular toy bags.
# Right-hand satchel remains practical; left pouch becomes a belt attachment.
left=get("Equipment | Left leather hip pouch")
left.dimensions=(.086,.093,.115)
left.location=(-.278,-.035,1.006)
lf=get("Equipment | Left pouch flap")
lf.dimensions=(.086,.023,.051)
lf.location=(-.278,-.084,1.051)
right=get("Equipment | Right leather hip pouch")
right.dimensions=(.121,.132,.200)
right.location=(.305,-.032,.973)
rf=get("Equipment | Right pouch flap")
rf.dimensions=(.123,.030,.072)
rf.location=(.305,-.106,1.034)
for side,sign in (("Left",-1),("Right",1)):
    pouch=get("Equipment | "+side+" leather hip pouch")
    # Round corner bevel already present from 0.8.3.
    yfront=pouch.location.y-pouch.dimensions.y/2-.003
    z0=pouch.location.z
    xmin=sign*(.304-.043 if side=="Right" else .278-.029)
    xmax=sign*(.304+.043 if side=="Right" else .278+.029)
    curve("Equipment 086 | "+side+" pouch leather stitch",[
        (xmin,yfront,z0-.058),(xmin,yfront,z0+.036),
        (xmax,yfront,z0+.036),(xmax,yfront,z0-.058)
    ],leather_seam,.0018)
# Cross-body is deliberately absent: the protagonist is bare-chested.
# Left hip gets one small angled strap and aged bronze clasp.
curve("Equipment 086 | belt diagonal stitched tab",[
    (-.225,-.139,1.075),(-.281,-.118,1.037),(-.317,-.105,.982)
],leather_seam,.0032)
for i in range(3):
    x=-.245-i*.025
    curve("Equipment 086 | bronze tab stud %d"%i,[
        (x,-.147,1.049),(x+.007,-.149,1.049)
    ],bronze,.0025)

# Preserve .blend before converting editable curves to FBX mesh only.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
bpy.ops.object.select_all(action="DESELECT")
for obj in scene.objects:
    if obj.type=="CURVE" and not obj.hide_render:
        obj.hide_set(False)
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
    use_selection=True,object_types={"MESH"},apply_unit_scale=True,
    axis_forward="-Z",axis_up="Y"
)
print("Necromancer 0.8.6: silhouette, trouser folds, embroidery and satchels exported.")
