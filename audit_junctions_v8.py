from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'audit_seating_entries_v7.py').read_text(encoding='utf-8')
exec(src[:src.index('tree=BVHTree')])
tree=BVHTree.FromPolygons(verts,faces)
data=json.loads((ROOT/'unity_enhanced/checks/seating_junctions_v8.json').read_text(encoding='utf-8'));fail=[]
for s in data['samples']:
 q=Vector(s['point'])+Vector((0,0,.04))
 hit,normal,i,d=tree.ray_cast(q,Vector((0,0,-1)),.10)
 if hit is None or abs(hit.z-s['point'][2])>.025:fail.append({'sample':s,'issue':'floor','hit':names[i] if hit else None})
 hit,normal,i,d=tree.ray_cast(q,Vector((0,0,1)),2.1)
 if hit is not None:fail.append({'sample':s,'issue':'headroom','hit':names[i]})
segments=0
for r in data['routes']:
 for a,b in zip(r['points'],r['points'][1:]):
  a,b=Vector(a),Vector(b);delta=b-a;segments+=1
  if delta.length<.001:continue
  hit,normal,i,d=tree.ray_cast(a,delta.normalized(),delta.length)
  if hit is not None:fail.append({'route':r['kind'],'issue':'blocked','hit':names[i],'point':list(hit)})
report={'samples':len(data['samples']),'segments':segments,'failures':len(fail),'details':fail}
(ROOT/'unity_enhanced/checks/junction_blender_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({**{k:v for k,v in report.items() if k!='details'},'examples':fail[:12]},ensure_ascii=False))
