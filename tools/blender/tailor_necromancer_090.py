"""Necromancer 0.9.0 — garment drape and waist tailoring, not a new blockout.

Works on the continuous 0.8.9 surface. Adjusts the waist/hip silhouette,
builds restrained directional cloth folds in the leg surfaces, removes
excessively thick hems, resizes the overly large belt pouch and maps subtle
stitched details to the edited mesh. The central crotch region is deliberately
left nearly untouched, preserving 0.8.9's successful topology rebuild.

The original 0.8.9 mesh stays editable in a hidden collection in .blend.
Produces .blend, .fbx and JSON metrics via GitHub Actions. No rig or retopo.
"""
import bpy
import math
import os
import json
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
def clamp(x):return max(0.0,min(1.0,x))
def gauss(v,c,w):return math.exp(-((v-c)/w)**2)
def ss(a,b,v):
    t=clamp((v-a)/(b-a))
    return t*t*(3-2*t)
def need(name):
    ob=bpy.data.objects.get(name)
    if ob is None:raise RuntimeError("0.9.0 missing object "+name)
    return ob
def stroke(name,points,mat,thickness=.0015):
    if len(points)<2:return None
    data=bpy.data.curves.new(name,"CURVE")
    data.dimensions="3D"
    data.bevel_depth=thickness
    data.bevel_resolution=2
    spline=data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p,coords in zip(spline.points,points):p.co=(*coords,1)
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    data.materials.append(mat)
    return obj

cloth=bpy.data.materials["Trousers | midnight charcoal"]
gold=bpy.data.materials["Bronze | engraved aged gold"]
seam=bpy.data.materials["Trousers | dark charcoal cuffs"]
leather=bpy.data.materials["Leather | black brown"]

pant=need("Garment 089 | anatomically joined trousers")
src_collection=bpy.data.collections.new("Editable 0.8.9 garment before tailoring | hidden")
scene.collection.children.link(src_collection)
backup=pant.copy()
backup.data=pant.data.copy()
backup.name="SOURCE 089 | untailored unified trousers"
src_collection.objects.link(backup)
backup.hide_render=True
backup.hide_set(True)

# Shape the silhouette without creating hidden inner intersections. We edit
# actual surface vertices; a waist-suppressing falloff transitions gradually
# into the thigh volume while the pelvis/crotch remains continuous.
for vert in pant.data.vertices:
    x,y,z=vert.co
    side=1 if x>=0 else -1
    ax=abs(x)
    # Remove the balloon-like drop from fitted belt to oversized hip.
    hip_factor=.077*gauss(z,.927,.098)+.037*gauss(z,1.034,.039)
    thigh_factor=.040*gauss(z,.690,.150)
    hem_factor=.006*gauss(z,.401,.075)
    factor=1.0-hip_factor-thigh_factor-hem_factor
    vert.co.x=x*factor
    # Keep the front near crotch in place, do not recreate the V-shaped hole.
    front=ss(.015,.160,-y)
    central_guard=1-.97*gauss(x,0,.089)*gauss(z,.813,.115)
    # Vertical cloth folds, with four unequal panels that taper into fabric.
    leg_center=side*.153
    fold_profile=(
       .0105*gauss(ax,.217+.025*math.sin((z-.4)*7.1),.029)
      -.0075*gauss(ax,.148+.024*math.sin((z-.36)*7.7),.025)
      +.0065*gauss(ax,.091+.022*math.sin((z-.43)*9),.021)
      -.0045*gauss(ax,.266+.011*math.sin(z*8),.019)
    )
    fold_window=ss(.370,.505,z)*(1-ss(.880,1.013,z))
    front_fold=front*central_guard*fold_window*fold_profile
    # Angular compression around the knee and above rolled hem.
    horizontal=(
        .0065*gauss(z,.617+side*.017*(x-leg_center),.038)
       -.0050*gauss(z,.563-side*.023*(x-leg_center),.027)
       +.007*gauss(z,.430+.013*math.sin(ax*20),.022)
    )*front*central_guard
    # Upper thigh tension creates a small slant from the pocket/hip.
    slant=.0065*gauss(z,.864-.28*(ax-.14),.053)*gauss(ax,.175,.11)
    # All folds are minor raised/recessed surface variations, not attached
    # dark strings. The x/y profile is still produced by one single mesh.
    vert.co.y=y-front_fold-horizontal*central_guard*fold_window-slant*front*central_guard
pant.data.update()

# Narrow the old large round trouser cuffs, bringing them toward the new
# fitted leg without losing the rolled cloth silhouette.
for side,sign in (("Left",-1),("Right",1)):
    cuff=need("Garment | "+side+" rolled trouser cuff")
    for vert in cuff.data.vertices:
        x,y,z=vert.co
        center=sign*.153
        vert.co.x=center+(x-center)*.945
        vert.co.y=y*.952
        vert.co.z=z + .003*math.sin(math.atan2(y,x-center)*3+sign)
    cuff.data.update()

# Practical equipment scale: original hip satchel looked like a large
# protruding cube and obscured the top of the right thigh.
pouch=need("Equipment | Right leather hip pouch")
pouch.dimensions=(.112,.097,.160)
pouch.location=(.304,-.020,.992)
flap=need("Equipment | Right pouch flap")
flap.dimensions=(.115,.025,.061)
flap.location=(.304,-.077,1.051)
for name in ("Equipment | Right brass clasp",):
    obj=bpy.data.objects.get(name)
    if obj:obj.location.y+=.016
# Existing old pouch stitches no longer align; remove just those curves.
for ob in list(scene.objects):
    if ob.name.startswith(("Equipment 086 | Right pouch leather stitch",
                           "Embroidery 089 |",
                           "Embroidery 088 |",
                           "Garment 090 |")):
        bpy.data.objects.remove(ob,do_unlink=True)

# Recreate fine embroidery and dark fabric stitching against the *updated*
# geometry. Thin sparse scrolls suit the reference better than wide zigzags.
def surface(x,z):
    hit,loc,norm,idx=pant.ray_cast(
        Vector((x,-2.0,z)),Vector((0,1,0)),distance=3.6)
    return (loc.y-.0022) if hit else None
def projected(name,xzs,mat,thickness):
    pts=[]
    for x,z in xzs:
        y=surface(x,z)
        if y is not None:pts.append((x,y,z))
    if len(pts)>=2:stroke(name,pts,mat,thickness)

for side,sign in (("Left",-1),("Right",1)):
    # Shaped golden edge filigree on the OUTER front of both leg panels.
    # Follow a gentle S instead of straight vertical metallic ribbons.
    base_x=.248
    main=[(sign*(base_x+.007*math.sin(2.3*math.pi*i/46)),
           .869-.423*i/46) for i in range(47)]
    projected("Garment 090 | "+side+" curved gilt side stem",
              main,gold,.00155)
    for j,(zbase,sideways) in enumerate(((.799,1),(.680,-1),(.552,1))):
        leaf=[(sign*(base_x+sideways*.020*math.sin(math.pi*i/12)),
               zbase+.033-.066*i/12) for i in range(13)]
        projected("Garment 090 | "+side+" narrow leaf "+str(j),
                  leaf,gold,.0013)
    # Slightly asymmetric front fabric dart, subtly shaded like a seam.
    dart_x=sign*.090
    projected("Garment 090 | "+side+" woven inner dart",[
        (dart_x,.904),(dart_x+sign*.010,.844),(dart_x+sign*.022,.796),
        (dart_x+sign*.035,.748)
    ],seam,.00125)

# Darken/remove strong procedural noise contrast: reference is illustrated
# and fabric should read as textile, not mottled stone.
ramp=cloth.node_tree.nodes.get("088 microcolor") if cloth.use_nodes else None
if ramp is not None:
    ramp.color_ramp.elements[0].color=(.062,.057,.077,1)
    ramp.color_ramp.elements[1].color=(.086,.079,.108,1)
noise=cloth.node_tree.nodes.get("088 tactile bump") if cloth.use_nodes else None
if noise is not None:
    noise.inputs["Strength"].default_value=.095
    noise.inputs["Distance"].default_value=.0007

# Structural regression tests from actual model geometry. These are not
# artistic approval: inspect the rendered views before integration.
def front_y(x,z):
    return surface(x,z)
front_samples={}
for z in (.765,.825,.885,.945):
    y=front_y(0,z)
    if y is None or y>-.065:
        raise RuntimeError("0.9.0 front fabric regression at %.3f: %s"%(z,y))
    front_samples[f"{z:.3f}"]=round(y,5)
width_samples={}
for z in (.405,.635,.845,.965):
    verts_at_height=[abs(v.co.x) for v in pant.data.vertices if abs(v.co.z-z)<.006]
    if len(verts_at_height)<10:
        raise RuntimeError("No trouser vertices near height %.3f"%z)
    width_samples[f"{z:.3f}"]=round(max(verts_at_height),5)
if width_samples["0.965"]>width_samples["0.845"]*1.18:
    raise RuntimeError("Waist expanded relative to hips")
metrics={
    "version":"0.9.0",
    "mesh":"Garment 089 | anatomically joined trousers",
    "vertices":len(pant.data.vertices),
    "faces":len(pant.data.polygons),
    "front_surface_y_by_height_m":front_samples,
    "half_width_by_height_m":width_samples,
    "note":"structural checks only; not animation or artistic acceptance"
}
with open(os.path.join(ROOT,"character_090_metrics.json"),"w") as fh:
    json.dump(metrics,fh,indent=2)
print("TAILORING QA "+json.dumps(metrics))

# Save an editable .blend, retaining the hidden 0.8.9 source for rollback.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
# Convert decorative curves only for FBX; do not destroy editable Blender file.
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
    use_selection=True,
    object_types={"MESH"},
    apply_unit_scale=True,
    axis_forward="-Z",axis_up="Y"
)
print("Necromancer 0.9.0: organic garment tailoring exported.")
