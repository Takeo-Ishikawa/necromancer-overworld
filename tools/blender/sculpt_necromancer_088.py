"""Necromancer 0.8.8 — organic torso, continuous tailoring and material pass.

Executed after sculpt_necromancer_087.py by the GitHub Actions Blender
workflow. Retains the 0.8.7 meshes as hidden editable source, unifies the
trouser seat and legs for a single silhouette, models real fabric gathers,
projects restrained embroidery onto the final mesh, and sets procedural
micro-texture materials. Neither a manual final sculpt nor rigged asset.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene

def gauss(value,center,radius):
    return math.exp(-((value-center)/radius)**2)

def smoothstep(lo,hi,value):
    t=max(0,min(1,(value-lo)/(hi-lo)))
    return t*t*(3-2*t)

def need(name):
    ob=bpy.data.objects.get(name)
    if ob is None:
        raise RuntimeError("0.8.8 missing required object: "+name)
    return ob

def stroke(name,coordinates,material,thickness=.0018):
    if len(coordinates)<2:return None
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D"
    curve.resolution_u=16
    curve.bevel_depth=thickness
    curve.bevel_resolution=3
    spline=curve.splines.new("POLY")
    spline.points.add(len(coordinates)-1)
    for p,xyz in zip(spline.points,coordinates):
        p.co=(*xyz,1)
    obj=bpy.data.objects.new(name,curve)
    scene.collection.objects.link(obj)
    curve.materials.append(material)
    return obj

skin=bpy.data.materials["Skin | muted warm porcelain"]
cloth=bpy.data.materials["Trousers | midnight charcoal"]
cloth_dark=bpy.data.materials["Trousers | dark charcoal cuffs"]
leather=bpy.data.materials["Leather | black brown"]
bronze=bpy.data.materials["Bronze | engraved aged gold"]

# Part 1 — integrate muscle relief into the thorax mesh. The old rib cage
# had sharp front planes and geometric-looking abdominal highlights; these
# small organic shape corrections soften the transition from sternum to
# ribs/obliques and make the shoulder slope less mechanical.
body=need("Anatomy | single torso and arms preview")
for vertex in body.data.vertices:
    x,y,z=vertex.co
    ax=abs(x)
    anterior=max(0,min(1,(-y-.060)/.105))
    posterior=max(0,min(1,(y-.065)/.090))
    if ax<.305 and 1.125<z<1.575:
        # Continuous lower-pectoral bowl rather than hard upper shelf.
        under_pec=.011*gauss(ax,.157,.122)*gauss(z,1.433,.064)
        upper_pec=.009*gauss(ax,.145,.117)*gauss(z,1.529,.050)
        vertex.co.y+=anterior*(upper_pec-under_pec)
        # Soft tendinous separations: leave natural abdomen silhouette.
        for zz in (1.328,1.263,1.194):
            vertex.co.y+=anterior*.0045*gauss(ax,.070,.073)*gauss(z,zz-.033,.012)
        # Serratus flow and narrowing oblique flank.
        vertex.co.y-=anterior*.008*gauss(ax,.217,.052)*gauss(z,1.333,.13)
        if 1.12<z<1.36 and ax>.160:
            vertex.co.x-=math.copysign(.0055*gauss(z,1.236,.105)*gauss(ax,.220,.070),x)
    if 1.350<z<1.600 and ax<.290:
        # Gentle back latissimus contours.
        vertex.co.y+=posterior*.007*gauss(ax,.200,.075)*gauss(z,1.435,.14)
    if ax>.280 and 1.480<z<1.625:
        # Continuous downward outer-shoulder slope.
        blend=gauss(ax,.341,.090)*gauss(z,1.545,.060)
        vertex.co.z-=.007*blend
body.data.update()
# Clean tiny remeshing ripples from previous passes, preserving big shapes.
bpy.ops.object.select_all(action="DESELECT")
body.hide_set(False)
body.select_set(True)
bpy.context.view_layer.objects.active=body
smooth=body.modifiers.new("088 relax fascia transitions","SMOOTH")
smooth.factor=.35
smooth.iterations=2
bpy.ops.object.modifier_apply(modifier=smooth.name)
body.select_set(False)

# The earlier contour curves read as scratches over the skin at gameplay
# scale. Rely on the actual sculpted mesh and lighting for anatomy instead.
for obj in list(scene.objects):
    if obj.name.startswith("Sculpt |") or (
        obj.name.startswith("Anatomy |") and " clavicle" in obj.name
    ):
        if obj.type=="CURVE":
            bpy.data.objects.remove(obj,do_unlink=True)
# Retain dark upper-arm leather but reduce its floating tube silhouette.
for side in ("Left","Right"):
    armband=bpy.data.objects.get("Armor | "+side+" etched upper arm band")
    if armband:
        armband.scale.x*=.95
        armband.scale.y*=.95

# Part 2 — a *single* seam-free upper garment. Existing panels are kept
# hidden in .blend and their visible copies are voxel-joined. The previous
# detached seat and leg caps produced a very obvious triangular underwear
# appearance around the groin.
old_parts=[
    need("Garment | upper waist and seat"),
    need("Garment | Left draped trouser leg"),
    need("Garment | Right draped trouser leg"),
]
source_col=bpy.data.collections.new("Editable 0.8.8 original trouser panels | hidden")
scene.collection.children.link(source_col)
copies=[]
for original in old_parts:
    replica=original.copy()
    replica.data=original.data.copy()
    replica.name="Unified tailoring temp | "+original.name
    scene.collection.objects.link(replica)
    replica.hide_render=False
    replica.hide_set(False)
    copies.append(replica)
    # Relink editable original into named source collection and hide in
    # both .blend viewport and the final FBX selection.
    source_col.objects.link(original)
    original.hide_render=True
    original.hide_set(True)

# Bridge the open groin created by the separate seat and thigh generators.
# This anatomical fabric transition is joined into the same final voxel
# surface — no triangle overlay or flat underwear-shaped polygon.
bridge_rings=[
    (.718,.080,.071,-.018),
    (.762,.132,.103,-.018),
    (.810,.179,.137,-.017),
    (.872,.214,.156,-.011),
    (.937,.224,.162,-.007),
    (1.013,.215,.148,-.003),
]
bv=[]
bc=40
for z,rx,ry,cy in bridge_rings:
    for idx in range(bc):
        angle=math.tau*idx/bc
        bv.append((rx*math.cos(angle),cy+ry*math.sin(angle),z))
bf=[tuple(reversed(range(bc)))]
for ring in range(len(bridge_rings)-1):
    for idx in range(bc):
        j=(idx+1)%bc
        bf.append((ring*bc+idx,ring*bc+j,(ring+1)*bc+j,(ring+1)*bc+idx))
bf.append(tuple((len(bridge_rings)-1)*bc+j for j in range(bc)))
bridge_mesh=bpy.data.meshes.new("Garment 088 | crotch fabric bridge mesh")
bridge_mesh.from_pydata(bv,[],bf)
bridge_mesh.update()
bridge=bpy.data.objects.new("Garment 088 | crotch fabric bridge",bridge_mesh)
scene.collection.objects.link(bridge)
bridge.data.materials.append(cloth)
copies.append(bridge)

bpy.ops.object.select_all(action="DESELECT")
for copy in copies:copy.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.object.join()
garment=bpy.context.object
garment.name="Garment 088 | single draped trousers"
garment.data.remesh_voxel_size=.007
bpy.ops.object.voxel_remesh()
smooth=garment.modifiers.new("Tailor cloth seat and inseam","SMOOTH")
smooth.factor=.64
smooth.iterations=3
bpy.ops.object.modifier_apply(modifier=smooth.name)

# Create broad vertical pleats with varied wavelength, not stamped ripples.
# They are sculpted onto the garment surface, so they follow its silhouette.
for vertex in garment.data.vertices:
    x,y,z=vertex.co
    ax=abs(x)
    sign=1 if x>=0 else -1
    # Shape the hips toward a relatively slim waist and fuller thigh.
    # Keep the leather belt position unchanged.
    if .88<z<1.064:
        influence=gauss(z,.976,.080)
        vertex.co.x=x*(1-.045*influence)
        vertex.co.y=y*(1-.014*influence)
    if .36<z<.96 and ax>.018:
        leg_center=sign*.151
        theta=math.atan2(y-.002,x-leg_center)
        radial=Vector((math.cos(theta),math.sin(theta),0))
        front=max(0,-math.sin(theta))
        knee=gauss(z,.575,.190)
        hem=gauss(z,.420,.063)
        hip=gauss(z,.885,.100)
        # Back of trousers hangs a little looser than the front.
        volume=(.006*knee+.004*hip-.003*hem)
        # Sparse broad vertical folds, stronger near outside of legs.
        pleat=(
            .008*math.sin(3.1*theta+z*11.5+sign*.6)
           +.004*math.sin(5.3*theta-z*8.3+sign*.3)
        )*(.65+.30*front)
        # Horizontal compression at the gathered shin and raised knee.
        gathering=front*(.009*gauss(z,.443,.024)*math.sin(3*theta+1.2)
                          +.006*gauss(z,.662,.052)*math.cos(2.7*theta+.8))
        displacement=volume+pleat+gathering
        vertex.co.x+=radial.x*displacement
        vertex.co.y+=radial.y*displacement
        if z<.53:
            # Hem dips irregularly rather than ending as a perfect cylinder.
            vertex.co.z+=.0045*math.sin(3.4*theta+sign*.8)*gauss(z,.417,.065)
garment.data.update()
for poly in garment.data.polygons:poly.use_smooth=True

# Simplify the rolled cuffs: thin, fabric-toned bands closely follow the
# flared hem rather than thick toy-like ring sections.
for side in ("Left","Right"):
    cuff=need("Garment | "+side+" rolled trouser cuff")
    for v in cuff.data.vertices:
        s= -1 if side=="Left" else 1
        x,y,z=v.co
        v.co.x=s*.153+(x-s*.153)*.96
        v.co.y=y*.96
    cuff.data.update()

# Old leaf curves were projected on *separate* legs and now float above the
# merged garment: reconstruct only a few quiet motifs on the current surface.
for ob in list(scene.objects):
    if ob.name.startswith(("Embroidery 086 |","Garment | Left seam front","Garment | Right seam front")):
        bpy.data.objects.remove(ob,do_unlink=True)

def front_surface(x,z):
    direction=Vector((0,1,0))
    ok,point,normal,polygon=garment.ray_cast(
        Vector((x,-2.0,z)),direction,distance=4)
    if not ok:return None
    return point.y-.0025

def embroidery(side,name,xz,thickness=.0017):
    pts=[]
    for x,z in xz:
        y=front_surface(x,z)
        if y is not None:
            pts.append((x,y,z))
    if len(pts)>1:
        stroke("Embroidery 088 | "+side+" "+name,pts,bronze,thickness)

for side,sign in (("Left",-1),("Right",1)):
    # Gold ornamental stems near the *outer* front hem of each leg.
    for j,zc in enumerate((.791,.651,.521)):
        base_x=sign*(.231+.005*math.sin(zc*10))
        # Winding stem, lightly asymmetrical.
        stem=[(base_x+sign*.009*math.sin(t*math.pi*1.5),
               zc+.055-.110*t) for t in (i/20 for i in range(21))]
        embroidery(side,"tapered scroll %d"%j,stem,.0018)
        # Single stylized leaf for each scroll instead of a row of discs.
        leaf=[(base_x+sign*.027*math.sin(math.pi*t),
               zc+.030-.062*t) for t in (i/14 for i in range(15))]
        embroidery(side,"hand-woven leaf %d"%j,leaf,.0015)
    # Narrow vertical outer trim, stopped before the cuffs.
    embroidery(side,"outer running seam",[
        (sign*.271,.894),(sign*.274,.815),(sign*.276,.733),
        (sign*.277,.648),(sign*.276,.565),(sign*.270,.469)
    ],.0015)

# Part 3 — subtle procedural shading microtextures. Avoid asset-heavy image
# textures and preserve a compact editable .blend and FBX for Unity preview.
def texture_surface(mat, dark,light,scale,bump_distance,bump_strength):
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bsdf=nodes.get("Principled BSDF")
    if bsdf is None:return
    ramp=nodes.get("088 microcolor")
    if ramp is None:
        ramp=nodes.new("ShaderNodeValToRGB")
        ramp.name="088 microcolor"
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=(*dark,1)
    ramp.color_ramp.elements[1].position=.82
    ramp.color_ramp.elements[1].color=(*light,1)
    noise=nodes.get("088 color noise")
    if noise is None:
        noise=nodes.new("ShaderNodeTexNoise")
        noise.name="088 color noise"
    noise.inputs["Scale"].default_value=scale
    noise.inputs["Detail"].default_value=2.4
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    fine=nodes.get("088 tactile noise")
    if fine is None:
        fine=nodes.new("ShaderNodeTexNoise")
        fine.name="088 tactile noise"
    fine.inputs["Scale"].default_value=scale*5
    fine.inputs["Detail"].default_value=2
    bump=nodes.get("088 tactile bump")
    if bump is None:
        bump=nodes.new("ShaderNodeBump")
        bump.name="088 tactile bump"
    bump.inputs["Strength"].default_value=bump_strength
    bump.inputs["Distance"].default_value=bump_distance
    links.new(fine.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

texture_surface(skin,(.655,.456,.401),(.691,.485,.426),21,.00018,.07)
texture_surface(cloth,(.051,.046,.063),(.091,.079,.104),16,.0013,.18)
texture_surface(cloth_dark,(.047,.040,.058),(.075,.063,.084),18,.0012,.16)
texture_surface(leather,(.107,.069,.053),(.172,.110,.077),13,.0018,.20)

# Preserve the editable curved embroidery in the Blend source and export
# its mesh conversion only after Blender save.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"character_base.blend"))
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
print("Necromancer 0.8.8: torso sculpt, unified cloth, embroidery and shaders exported.")
