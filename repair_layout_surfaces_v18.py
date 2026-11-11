"""Build clean row solids around the new aisles instead of re-cutting open legacy meshes."""
import bpy,math,json,ast,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children};ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
def delta(a,b):return (a-b+math.pi)%math.tau-math.pi
for ti,(rx,ry,z,n,step,rise,mid) in enumerate([(76,106,1.2,23,.9,.54,12),(99,128,17,16,1.02,.65,9)],1):
 ps=[p for p in ports if p['tier']==ti];angles=[i*math.tau/480 for i in range(480)]
 for p in ps:
  scale=math.hypot(rx*math.sin(p['angle']),ry*math.cos(p['angle']))
  angles.extend((p['angle']+w/scale)%math.tau for w in [-3.2,-1.6,-1.55,1.55,1.6,3.2])
 angles=sorted(set(angles));batch=Batch('V18_洁净座席基座_%d'%ti,bpy.data.materials['concrete'],'02')
 for j in range(n):
  top=z+j*rise;inner=rx+j*step;outer=inner+step
  for i,a in enumerate(angles):
   b=angles[i+1] if i+1<len(angles) else angles[0]+math.tau;c=(a+b)/2
   p=min(ps,key=lambda p:abs(delta(c,p['angle'])));scale=math.hypot(rx*math.sin(p['angle']),ry*math.cos(p['angle']));w=abs(delta(c,p['angle'])*scale)
   if 1.6<w<3.2:continue
   low=top-rise-.1
   if j>=mid and w<1.55:
    low=p['height']+2.70
    if top<=low:continue
   pts=[Vector((r*math.cos(ang),(r+ry-rx)*math.sin(ang),0)) for r,ang in [(inner,a),(outer,a),(outer,b),(inner,b)]]
   off=len(batch.v);batch.v.extend([(p.x,p.y,h) for h in [low,top] for p in pts]);batch.f.extend(tuple(off+k for k in f) for f in cube_f)
 old=S.objects['三层看台_层%d'%ti];temp=batch.finish();old.data=temp.data;bpy.data.objects.remove(temp,do_unlink=True)
 uv=old.data.uv_layers.new(name='MetreUV')
 for f in old.data.polygons:
  axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
  for li in f.loop_indices:
   v=old.data.vertices[old.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Rebuilt two seating tiers as closed solids with 56 aligned aisle pairs')
