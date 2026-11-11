import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
ports=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))['ports']
angles=[p['angle'] for p in ports]
def delta(a,b):return (a-b+math.pi)%math.tau-math.pi
ob=S.objects['三层看台_层3'];bm=bmesh.new();bm.from_mesh(ob.data);remove=[]
for f in bm.faces:
 c=ob.matrix_world@f.calc_center_median();a=math.atan2(c.y/144.55,c.x/119.55);base=Vector((119.55*math.cos(a),144.55*math.sin(a),c.z));r=(c-base).dot(Vector((math.cos(a),math.sin(a),0)))
 scale=math.hypot(119*math.sin(a),144*math.cos(a));w=min(abs(delta(a,p)*scale) for p in angles)
 if -.8<r<4.8 and w<2.05:remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
shell_faces=0
for ob in list(S.objects):
 if ob.type!='MESH' or not ob.name.startswith('红色看台背壳_2_'):continue
 bm=bmesh.new();bm.from_mesh(ob.data);remove=[]
 for f in bm.faces:
  c=ob.matrix_world@f.calc_center_median()
  for p in ports:
   entry=Vector(p['entry']);rad=Vector((math.cos(p['angle']),math.sin(p['angle']),0));tan=Vector((-rad.y,rad.x,0));d=c-entry
   if -2<d.dot(rad)<p['length']+2 and abs(d.dot(tan))<2.25:remove.append(f);break
 shell_faces+=len(remove);bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Upper portal cleanup:',len(remove),'last shell faces;',shell_faces,'total shell faces')
