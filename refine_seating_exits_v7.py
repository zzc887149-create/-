import bpy,json,ast,math,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
code=(ROOT/'connect_seating_entries_v7.py').read_text(encoding='utf-8')
exec(code[code.index('tree=ast.parse'):code.index("COL={")])
COL={c.name[:2]:c for c in S.collection.children};C=COL['22'];concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
exec(code[code.index('def point('):code.index('for bay in range(12):')])
path=ROOT/'unity_enhanced/checks/seating_entries.json';data=json.loads(path.read_text(encoding='utf-8'));ports=data['ports']
for p in ports:p['length']+=2
for ob in list(C.objects):bpy.data.objects.remove(ob,do_unlink=True)
cuts=Batch('V7_TEMP_出口净空',None,'22')
for p in ports:cuts.box(point(p,(p['length']+.7)/2,0,p['height']+1.14),(p['length']+.9,2.4,3.12),p['angle'])
cutter=cuts.finish();bpy.context.view_layer.update()
exec(code[code.index('def cut_object('):code.index("for name in ['三层看台_")])
for ob in list(S.objects):
 if ob.name.startswith('红色看台背壳_'):cut_object(ob)
bpy.data.objects.remove(cutter,do_unlink=True)
exec(code[code.index('for p in ports:\n tag='):code.index('# Open the front safety rail')])
for ob in C.objects:
 if ob.type!='MESH' or concrete not in list(ob.data.materials):continue
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
p=next(p for p in ports if p['bay']==0 and p['level']==2)
S.objects['VIEW_14_SeatingEntry'].location=point(p,p['length']+1,2.7,p['concourse']+1.8)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Extended exits to clear shaft edges and cut the sloped back-wall overhang')
