"""Enclose existing vomitories without closing circulation openings."""
import bpy,ast,json,math,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('rear_deck_v12') and not S.get('portal_enclosures_v14')
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
C=bpy.data.collections.new('26_看台入口完整围护');S.collection.children.link(C);COL['26']=C
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
for p in ports:
 e=Vector(p['entry']);r=Vector(p['rad']);t=Vector(p['tan']);h=p['height'];L=p['length'];a=p['angle']
 def q(d,w,z):
  v=e+r*d+t*w;v.z=z;return v
 # Start beyond the lateral turning landing; keep the existing 2.1 m clear width.
 start=.95;end=L-.05;top=h+2.65
 b=Batch('V14_入口侧壁及顶板_F%d_B%02d'%(p['level'],p['bay']),bpy.data.materials['concrete'],'26')
 for side in [-1,1]:
  b.box(q((start+end)/2,side*1.30,(p['concourse']-.22+top)/2),(end-start,.20,top-p['concourse']+.22),a)
 b.box(q((start+end)/2,0,top+.10),(end-start,2.8,.20),a)
 ob=b.finish()
 uv=ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
# Reuse the measured rear-deck clearance envelope for overlapping new walls.
src=(ROOT/'clear_rear_deck_headroom_v12.py').read_text(encoding='utf-8')
src=src.replace("ob.name.startswith('环形集散厅楼板_F3') or ob.name.startswith('环廊径向梁')", "ob.name.startswith('V14_')")
src=src.replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)', 'None')
exec(compile(src,'rear_deck_clearance','exec'))
S['portal_enclosures_v14']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_入口围护完善版.blend'))
print('48 passage enclosures: clear width 2.4m above existing low guards; soffit 2.65m above landing')
