import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'));ns=[n for n in src.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)];exec(compile(ast.Module(body=ns,type_ignores=[]),'helpers','exec'));COL={c.name[:2]:c for c in S.collection.children}
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
for p in ports:
 e=Vector(p['entry']);r=Vector(p['rad']);t=Vector(p['tan']);h=p['height']
 def q(d,w,z):v=e+r*d+t*w;v.z=z;return v
 b=Batch('V18_洞口收边_F%d_B%02d'%(p['level'],p['bay']),bpy.data.materials['concrete'],'26')
 for side in [-1,1]:b.box(q(.74,side*1.30,h+1.325),(.46,.20,2.65),p['angle'])
 b.box(q(.74,0,h+2.75),(.46,2.8,.20),p['angle'])
 rise=p['row_rise'];b.box(q(-.46,0,h-(rise+.1)/2),(.12,3.2,rise+.1),p['angle'])
 ob=b.finish();uv=ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
