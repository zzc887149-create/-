import bpy,json,collections,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
data=json.loads((ROOT/'unity_enhanced/checks/v20_layout.json').read_text(encoding='utf-8'))
dg=bpy.context.evaluated_depsgraph_get();up=Vector((0,0,1));fails=[];summary=collections.Counter()
for i,s in enumerate(data['samples']):
    p=Vector(s['point']);ok,hit,n,idx,ob,m=S.ray_cast(dg,p+up*.05,-up,distance=.14)
    if not ok or abs(hit.z-p.z)>.045:
        fails.append({'type':'floor','sample':s,'hit':ob.name if ok else None,'delta':hit.z-p.z if ok else None});summary['floor']+=1
    ok,hit,n,idx,ob,m=S.ray_cast(dg,p+up*.06,up,distance=2.08)
    if ok:fails.append({'type':'head','sample':s,'hit':ob.name,'height':hit.z-p.z});summary['head']+=1
for s in data['segments']:
    a=Vector(s['a']);b=Vector(s['b']);d=b-a
    if d.length<1e-6:continue
    ok,hit,n,idx,ob,m=S.ray_cast(dg,a,d.normalized(),distance=d.length)
    if ok:fails.append({'type':'body','segment':s,'hit':ob.name});summary['body']+=1
out={'sample_count':len(data['samples']),'segment_count':len(data['segments']),'failures':dict(summary),'by_object':dict(collections.Counter(f['hit'] for f in fails)),'examples':fails[:500],'all_failures':fails}
(ROOT/'unity_enhanced/checks/v20_audit.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('examples','all_failures')},ensure_ascii=False))
