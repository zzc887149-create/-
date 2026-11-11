"""Independent headless geometry audit with a single static BVH."""
import bpy,json,collections,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
data=json.loads((ROOT/'unity_enhanced/checks/v23_layout.json').read_text(encoding='utf-8'))
verts=[];faces=[];owners=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
    if ob.type not in ('MESH','CURVE','FONT') or ob.hide_render:continue
    if any(c.name[:2] in ('04','07','10','11','12','16','20') for c in ob.users_collection) or ob.name.startswith(('看台座椅_','NEAR_','内场折叠椅_')):continue
    me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));off=len(verts);oi=len(names);names.append(ob.name)
    verts.extend(tuple(ob.matrix_world@v.co) for v in me.vertices)
    faces.extend(tuple(off+i for i in p.vertices) for p in me.polygons);owners.extend([oi]*len(me.polygons));bpy.data.meshes.remove(me)
tree=BVHTree.FromPolygons(verts,faces);del verts,faces
up=Vector((0,0,1));fails=[];summary=collections.Counter()
for s in data['samples']:
    p=Vector(s['point']);hit,n,idx,dist=tree.ray_cast(p+up*.05,-up,.14)
    if hit is None or abs(hit.z-p.z)>.045:
        fails.append({'type':'floor','sample':s,'hit':names[owners[idx]] if idx is not None else None,'delta':hit.z-p.z if hit is not None else None});summary['floor']+=1
    hit,n,idx,dist=tree.ray_cast(p+up*.06,up,2.08)
    if hit is not None and hit.z-p.z>.15:fails.append({'type':'head','sample':s,'hit':names[owners[idx]],'height':hit.z-p.z});summary['head']+=1
for s in data['segments']:
    a=Vector(s['a']);b=Vector(s['b']);d=b-a
    if d.length<1e-6:continue
    hit,n,idx,dist=tree.ray_cast(a,d.normalized(),d.length)
    if hit is not None:fails.append({'type':'body','segment':s,'hit':names[owners[idx]]});summary['body']+=1
out={'sample_count':len(data['samples']),'segment_count':len(data['segments']),'failures':dict(summary),'by_object':dict(collections.Counter(f['hit'] for f in fails)),'all_failures':fails}
(ROOT/'unity_enhanced/checks/v23_audit_fast.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='all_failures'},ensure_ascii=False))
if fails:raise RuntimeError('v23 circulation geometry failed; inspect v23_audit_fast.json')


