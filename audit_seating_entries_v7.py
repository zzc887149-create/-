import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
verts=[];faces=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
 if ob.type not in {'MESH','CURVE'}:continue
 if not any(m and m.name in ['concrete','外碗赭红混凝土','楼梯红色防滑涂层','栏杆细金属'] for m in ob.data.materials):continue
 me=ob.evaluated_get(dg).to_mesh();off=len(verts);verts.extend([ob.matrix_world@v.co for v in me.vertices])
 for f in me.polygons:faces.append([off+i for i in f.vertices]);names.append(ob.name)
 ob.evaluated_get(dg).to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);fail=[];samples=0
for p in ports:
 L=p['length'];run=p['step_run'];h=p['height'];z0=p['concourse'];n=p['step_count']
 ts=[-.14,-.05]+[i*.23 for i in range(int((L-run)/.23))]+[L-(i+.5)*.28 for i in range(n)]+[L+.05,L+.3]
 for t in ts:
  top=h if t<L-run else z0+(min(n,math.floor((L-t)/.28)+1))*(h-z0)/n if t<L else z0
  for w in [-.75,0,.75]:
   q=Vector(p['entry'])+Vector(p['rad'])*t+Vector(p['tan'])*w;q.z=top+.05;samples+=1
   hit,normal,idx,dist=tree.ray_cast(q,Vector((0,0,-1)),.1)
   if hit is None or abs(hit.z-top)>.025:fail.append({'bay':p['bay'],'level':p['level'],'t':round(t,3),'w':w,'issue':'floor','hit':names[idx] if hit is not None else None})
   hit,normal,idx,dist=tree.ray_cast(q,Vector((0,0,1)),2.1)
   if hit is not None:fail.append({'bay':p['bay'],'level':p['level'],'t':round(t,3),'w':w,'issue':'headroom','hit':names[idx],'clearance':round(dist,3)})
result={'samples':samples,'failures':len(fail),'details':fail}
(ROOT/'unity_enhanced/checks/seating_blender_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'samples':samples,'failures':len(fail),'examples':fail[:30]},ensure_ascii=False))
