from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'audit_seating_entries_v7.py').read_text(encoding='utf-8')
exec(src[:src.index('tree=BVHTree')]);tree=BVHTree.FromPolygons(verts,faces);fail=[];segments=0
for p in ports:
 L=p['length'];run=p['step_run'];h=p['height'];z0=p['concourse'];n=p['step_count']
 ts=[-.14,-.05]+[i*.23 for i in range(int((L-run)/.23))]+[L-(i+.5)*.28 for i in range(n)]+[L+.05,L+.3];ts.sort()
 for w in [-.75,0,.75]:
  previous=None
  for t in ts:
   top=h if t<L-run else z0+(min(n,math.floor((L-t)/.28)+1))*(h-z0)/n if t<L else z0
   q=Vector(p['entry'])+Vector(p['rad'])*t+Vector(p['tan'])*w;q.z=top+1.3
   if previous is not None:
    d=q-previous;segments+=1;hit,_,i,_=tree.ray_cast(previous,d.normalized(),max(0,d.length-.01))
    if hit is not None:fail.append({'bay':p['bay'],'level':p['level'],'t':round(t,3),'w':w,'hit':names[i],'point':list(hit)})
   previous=q
result={'segments':segments,'failures':len(fail),'details':fail};(ROOT/'unity_enhanced/checks/legacy_routes_v10.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'segments':segments,'failures':len(fail),'examples':fail[:30]},ensure_ascii=False))
