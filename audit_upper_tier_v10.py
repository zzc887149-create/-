import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
data=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))
def build_tree(predicate):
 verts=[];faces=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob in S.objects:
  if ob.type not in {'MESH','CURVE'} or not predicate(ob):continue
  me=ob.evaluated_get(dg).to_mesh();off=len(verts);verts.extend(ob.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:faces.append([off+i for i in f.vertices]);names.append(ob.name)
  ob.evaluated_get(dg).to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces),names
architecture,names=build_tree(lambda ob:any(m and m.name in ['concrete','外碗赭红混凝土','楼梯红色防滑涂层','栏杆细金属'] for m in ob.data.materials))
fail=[]
for s in data['samples']:
 q=Vector(s['point']);hit,_,i,_=architecture.ray_cast(q+Vector((0,0,.04)),Vector((0,0,-1)),.12)
 if hit is None or abs(hit.z-q.z)>.03:fail.append({'kind':s['kind'],'bay':s['bay'],'issue':'floor','hit':names[i] if hit else None,'point':list(q)})
 hit,_,i,d=architecture.ray_cast(q+Vector((0,0,.04)),Vector((0,0,1)),2.1)
 if hit is not None:fail.append({'kind':s['kind'],'bay':s['bay'],'issue':'headroom','hit':names[i],'clearance':round(d,3),'point':list(q)})
segments=0
for r in data['routes']:
 for a,b in zip(r['points'],r['points'][1:]):
  a,b=Vector(a),Vector(b);d=b-a;segments+=1
  hit,_,i,_=architecture.ray_cast(a,d.normalized(),max(0,d.length-.02)) if d.length>.03 else (None,None,None,None)
  if hit is not None:fail.append({'kind':r['kind'],'issue':'blocked','hit':names[i],'point':list(hit)})
report={'samples':len(data['samples']),'segments':segments,'failures':len(fail),'details':fail}
(ROOT/'unity_enhanced/checks/upper_tier_blender_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({**{k:v for k,v in report.items() if k!='details'},'examples':fail[:20]},ensure_ascii=False))
