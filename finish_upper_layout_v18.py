import bpy,ast,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in src.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
data=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))
batch=Batch('V18_TEMP_上层转弯净空',None,'24')
for r in data['routes']:
 if r['kind']!='upper_landing_turn':continue
 for aa,bb in zip(r['points'],r['points'][1:]):
  a=Vector(aa);b=Vector(bb);direction=(b-a);horizontal=Vector((direction.x,direction.y,0)).normalized();side=Vector((-horizontal.y,horizontal.x,0))*.38
  off=len(batch.v)
  for dz in [-1.25,1.1]:
   batch.v.extend(tuple(p+q+Vector((0,0,dz))) for p,q in [(a,-side),(b,-side),(b,side),(a,side)])
  batch.f.extend(tuple(off+k for k in f) for f in cube_f)
for p in data['ports']:
 if p['bay'] not in [11,25]:continue
 a=p['angle'];e=Vector(p['entry']);e.z=p['height'];r=Vector((math.cos(a),math.sin(a),0));t=Vector((-r.y,r.x,0))
 batch.box(e+r*.12+Vector((0,0,1.25)),(.9,3.55,2.4),a)
cut=batch.finish();bpy.context.view_layer.update();ob=S.objects['三层看台_层3']
m=ob.modifiers.new('上层出口通行收口','BOOLEAN');m.object=cut;m.operation='DIFFERENCE';m.solver='EXACT'
dg=bpy.context.evaluated_depsgraph_get();ob.data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();bpy.data.objects.remove(cut,do_unlink=True)
for name in ['环廊混凝土柱.021','环廊混凝土柱.045']:
 ob=S.objects[name]
 c=sum((ob.matrix_world@Vector(v) for v in ob.bound_box),Vector())/8
 p=min(data['ports'],key=lambda p:(Vector(p['start'])-Vector((c.x,c.y,22.5))).length)
 tan=Vector((-math.sin(p['angle']),math.cos(p['angle']),0));d=(c-Vector(p['entry'])).dot(tan);shift=tan*((3.4-abs(d))*(1 if d>=0 else -1))
 ob.location+=shift
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Upper landing cuts and two peripheral column offsets completed')
