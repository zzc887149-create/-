"""Rebuild upper tier from its pre-cut height field, eliminating Boolean cutter walls."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
with bpy.data.libraries.load(str(ROOT/'赵雷2026_鸟巢_楼梯连通版.blend'),link=False) as (a,b):b.objects=['三层看台_层3']
old=b.objects[0];me=old.data
tree=BVHTree.FromPolygons([old.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);bpy.data.objects.remove(old,do_unlink=True)
ports=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))['ports']
angles=[i*math.tau/720 for i in range(720)]
for p in ports:
 scale=math.hypot(119*math.sin(p['angle']),144*math.cos(p['angle']))
 angles.extend((p['angle']+w/scale)%math.tau for w in [-3.2,-1.6,1.6,3.2])
angles=sorted(set(angles));vs=[];fs=[];cube=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def delta(a,b):return (a-b+math.pi)%math.tau-math.pi
def height(j,a):
 rx=119+(j+.5)*1.1;ry=144+(j+.5)*1.1
 hit,_,_,_=tree.ray_cast(Vector((rx*math.cos(a),ry*math.sin(a),60)),Vector((0,0,-1)),60)
 if hit is None:raise RuntimeError(('Missing uncut tier surface',j,a))
 return hit.z
for j in range(19):
 rx=119+j*1.1;ry=144+j*1.1
 for i,a in enumerate(angles):
  b=angles[i+1] if i+1<len(angles) else angles[0]+math.tau;c=(a+b)/2
  p=min(ports,key=lambda p:abs(delta(c,p['angle'])));w=abs(delta(c,p['angle'])*math.hypot(119*math.sin(p['angle']),144*math.cos(p['angle'])))
  if 1.6<w<3.2 or j<4 and w<1.6:continue
  ha=height(j,a);hb=height(j,b);outer=1.1 if j<18 else 1.1
  corners=[(rx*math.cos(a),ry*math.sin(a),ha),((rx+outer)*math.cos(a),(ry+outer)*math.sin(a),ha),((rx+outer)*math.cos(b),(ry+outer)*math.sin(b),hb),(rx*math.cos(b),ry*math.sin(b),hb)]
  off=len(vs);vs.extend([(x,y,z-.95) for x,y,z in corners]+corners);fs.extend(tuple(off+k for k in f) for f in cube)
me=bpy.data.meshes.new('V18_上层洁净阶梯壳');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['concrete']);me.update();uv=me.uv_layers.new(name='MetreUV')
for f in me.polygons:
 axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
S.objects['三层看台_层3'].data=me
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Clean upper tier, maximum height:',max(v.co.z for v in me.vertices))
