"""Necromancer 0.8.9 — rebuild trousers as a single continuous implicit surface.

The previous pelvis + two thigh meshes created a deep triangular shadow in the
crotch even after remeshing. This step discards that *visible* composite and
generates a new closed trouser garment from a smooth union of three analytic
volumes, reconstructed with surface nets (quad-dominant). No added libraries
are needed besides system numpy, already installed in the GitHub Actions job.

Run after sculpt_necromancer_088.py with Blender 4.x on GitHub Actions.
The earlier cloth remains hidden/editable in the .blend, while FBX contains
only the new visible trouser mesh. This is not rig-ready retopology.
"""
import bpy
import math
import os
import numpy as np
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
cloth=bpy.data.materials["Trousers | midnight charcoal"]
gold=bpy.data.materials["Bronze | engraved aged gold"]

old=bpy.data.objects.get("Garment 088 | single draped trousers")
if old is None:
    raise RuntimeError("Expected 0.8.8 garment missing")
hidden=bpy.data.collections.new("Editable 0.8.8 cloth predecessor | hidden")
scene.collection.children.link(hidden)
hidden.objects.link(old)
old.hide_render=True
old.hide_set(True)

for ob in list(scene.objects):
    if ob.name.startswith(("Embroidery 088 |","Embroidery 086 |")):
        bpy.data.objects.remove(ob,do_unlink=True)

# SDF definitions use meters; garment spans the high waist to below knee.
step=.009
xx=np.arange(-.360,.360+step*.5,step,dtype=np.float32)
yy=np.arange(-.233,.233+step*.5,step,dtype=np.float32)
zz=np.arange(.305,1.095+step*.5,step,dtype=np.float32)
X=xx[:,None,None]
Y=yy[None,:,None]
Z=zz[None,None,:]

def smin(a,b,k):
    h=np.maximum(k-np.abs(a-b),0.0)/k
    return np.minimum(a,b)-h*h*k*.25

# Continuous waist/seat profile, tapered from full hips to fitted waist.
pelvis_rx=(.200+.038*np.exp(-((Z-.918)/.140)**2)
           -.008*np.exp(-((Z-1.055)/.035)**2))
pelvis_ry=(.122+.035*np.exp(-((Z-.907)/.145)**2))
pelvis_radius=(np.sqrt((X/pelvis_rx)**2+(Y/pelvis_ry)**2)-1.0)*.143
# Pelvis blends into upper thighs while retaining a natural crotch rise.
pelvis=np.maximum(np.maximum(pelvis_radius,.748-Z),Z-1.071)

# Two leg volumes overlap the pelvis, but not one another near the ankles.
# Front pleats influence the surface directly rather than floating overlays.
def leg_field(sign):
    center=sign*(.160-.015*np.clip((Z-.38)/.63,0,1))
    rx=.132+.017*np.clip((Z-.35)/.65,0,1)
    ry=.130+.012*np.clip((Z-.35)/.65,0,1)
    fold=(.004*np.sin(Z*26+sign*.7)+.003*np.sin(Z*48-sign*.8))
    rx=rx+fold
    ry=ry+fold*.55
    radial=(np.sqrt(((X-center)/rx)**2+(Y/ry)**2)-1)*.131
    return np.maximum(np.maximum(radial,.352-Z),Z-.972)

legs=smin(leg_field(-1),leg_field(1),.026)
field=smin(pelvis,legs,.078)

# Fill the front central gusset gently: smooth rounded fabric fold, not a
# protruding triangular polygon. Closes the deep front valley in 0.8.8.
gusset=(np.sqrt((X/.127)**2+((Y+.023)/.118)**2+
                ((Z-.803)/.085)**2)-1)*.105
field=smin(field,gusset,.028).astype(np.float32)

# Surface nets: one vertex per cell straddling the zero isosurface, derived
# from the mean of all crossing-edge intersections. Adjacent cells produce
# quad faces, avoiding disconnected pelvis/thigh overlap surfaces.
nx,ny,nz=field.shape
corners=((0,0,0),(1,0,0),(0,1,0),(1,1,0),
         (0,0,1),(1,0,1),(0,1,1),(1,1,1))
edges=((0,1),(2,3),(4,5),(6,7),
       (0,2),(1,3),(4,6),(5,7),
       (0,4),(1,5),(2,6),(3,7))
mins=np.minimum.reduce([field[a:nx-1+a,b:ny-1+b,c:nz-1+c]
                        for a,b,c in corners])
maxs=np.maximum.reduce([field[a:nx-1+a,b:ny-1+b,c:nz-1+c]
                        for a,b,c in corners])
active=(mins<0)&(maxs>=0)
cell_indices=np.argwhere(active)
vertex_ids=np.full((nx-1,ny-1,nz-1),-1,dtype=np.int32)
verts=[]
for i,j,k in cell_indices:
    values=[float(field[i+a,j+b,k+c]) for a,b,c in corners]
    intersections=[]
    for u,v in edges:
        fu,fv=values[u],values[v]
        if (fu<0)==(fv<0):
            continue
        t=fu/(fu-fv)
        au,bu,cu=corners[u]
        av,bv,cv=corners[v]
        intersections.append((
            float(xx[i]+step*(au+t*(av-au))),
            float(yy[j]+step*(bu+t*(bv-bu))),
            float(zz[k]+step*(cu+t*(cv-cu)))
        ))
    if not intersections:
        continue
    vertex_ids[i,j,k]=len(verts)
    n=len(intersections)
    verts.append(tuple(sum(pos[d] for pos in intersections)/n
                       for d in range(3)))
del cell_indices
faces=[]
def quad(cells,inner_at_start):
    ids=[int(vertex_ids[a,b,c]) for a,b,c in cells]
    if any(idx<0 for idx in ids):
        return
    if len(set(ids))==4:
        faces.append(tuple(ids if inner_at_start else reversed(ids)))

# X-aligned lattice edges: edge normal +X when inside is at x-min.
xedges=np.argwhere((field[:-1,:,:]<0)!=(field[1:,:,:]<0))
for i,j,k in xedges:
    if j<1 or k<1 or j>=ny-1 or k>=nz-1:
        continue
    quad(((i,j-1,k-1),(i,j,k-1),(i,j,k),(i,j-1,k)),
         bool(field[i,j,k]<0))
# Y lattice edges: normals +Y when inside is at y-min.
yedges=np.argwhere((field[:,:-1,:]<0)!=(field[:,1:,:]<0))
for i,j,k in yedges:
    if i<1 or k<1 or i>=nx-1 or k>=nz-1:
        continue
    quad(((i-1,j,k-1),(i-1,j,k),(i,j,k),(i,j,k-1)),
         bool(field[i,j,k]<0))
# Z lattice edges: normals +Z when inside is below.
zedges=np.argwhere((field[:,:,:-1]<0)!=(field[:,:,1:]<0))
for i,j,k in zedges:
    if i<1 or j<1 or i>=nx-1 or j>=ny-1:
        continue
    quad(((i-1,j-1,k),(i,j-1,k),(i,j,k),(i-1,j,k)),
         bool(field[i,j,k]<0))
if len(verts)<5000 or len(faces)<5000:
    raise RuntimeError("Surface nets produced too few trouser faces: %d, %d" %
                       (len(verts),len(faces)))

mesh=bpy.data.meshes.new("Garment 089 | quad dominant surface")
mesh.from_pydata(verts,[],faces)
mesh.update()
pant=bpy.data.objects.new("Garment 089 | anatomically joined trousers",mesh)
scene.collection.objects.link(pant)
mesh.materials.append(cloth)
for face in mesh.polygons:face.use_smooth=True

bpy.ops.object.select_all(action="DESELECT")
pant.select_set(True)
bpy.context.view_layer.objects.active=pant
smoother=pant.modifiers.new("Tailoring subtle relaxation","SMOOTH")
smoother.factor=.44
smoother.iterations=2
bpy.ops.object.modifier_apply(modifier=smoother.name)
pant.select_set(False)

# Visual regression: the center front of the pelvis and crotch must have an
# uninterrupted visible fabric surface at several heights.
# In the previous garment z=.77-.89 had an unnaturally deep V-shaped recess.
for elevation in (.76,.82,.88,.94):
    hit,point,normal,face=pant.ray_cast(
        Vector((0,-1.3,elevation)),Vector((0,1,0)),distance=3)
    if not hit or point.y>-.075:
        raise RuntimeError("Trouser front has a recessed crotch at z=%.2f"%
                           elevation)
    print("Fabric front check z=%.2f y=%.3f"%(elevation,point.y))

# Rebuild a smaller number of embroidered vines against *this* final mesh.
def embroidered(name,positions,thickness=.00175):
    mapped=[]
    for x,z in positions:
        hit,pos,normal,index=pant.ray_cast(
            Vector((x,-2,z)),Vector((0,1,0)),distance=4)
        if hit:
            mapped.append((x,pos.y-.002,z))
    if len(mapped)<2:return
    cv=bpy.data.curves.new(name,"CURVE")
    cv.dimensions="3D"
    cv.bevel_depth=thickness
    cv.bevel_resolution=2
    sp=cv.splines.new("POLY")
    sp.points.add(len(mapped)-1)
    for target,coordinate in zip(sp.points,mapped):
        target.co=(*coordinate,1)
    ob=bpy.data.objects.new(name,cv)
    scene.collection.objects.link(ob)
    cv.materials.append(gold)

for sign,side in ((-1,"Left"),(1,"Right")):
    # Narrow vines near the outer-front seam, with alternating leaf motifs.
    base=.245
    path=[(sign*(base+.009*math.sin(t*math.pi*3)),.866-.420*t)
          for t in (i/45 for i in range(46))]
    embroidered("Embroidery 089 | "+side+" thin side vine",path,.00165)
    for leaf,at in enumerate((.813,.716,.615,.513)):
        leafpoints=[(sign*(base+(.020 if leaf%2 else -.020)
                           *math.sin(math.pi*i/12)),
                     at+.027-.054*i/12) for i in range(13)]
        embroidered("Embroidery 089 | "+side+" leaf %d"%leaf,
                    leafpoints,.00135)

# Keep independent cuffs, pouches, belt and all rest of outfit untouched.
# Save editable Blender scene before converting decorative curves for FBX.
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
    apply_unit_scale=True,axis_forward="-Z",axis_up="Y")
print("Necromancer 0.8.9: continuous SDF trousers, center-front checks, FBX exported.")
