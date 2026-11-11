from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'audit_junctions_v8.py').read_text(encoding='utf-8').replace('seating_junctions_v8.json','seating_junctions_v9.json').replace('junction_blender_validation.json','junction_v9_blender_validation.json')
exec(compile(src,'architecture_audit','exec'))
assert not fail, 'Architectural clearance check failed'
verts=[];faces=[];names=[]
for ob in S.objects:
 if ob.type!='MESH':continue
 if not (ob.name.startswith(('看台座椅_','NEAR_')) or any(c.name.startswith('07_') for c in ob.users_collection)):continue
 me=ob.evaluated_get(dg).to_mesh();off=len(verts);verts.extend(ob.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:faces.append([off+i for i in f.vertices]);names.append(ob.name)
 ob.evaluated_get(dg).to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);fail=[]
for s in data['samples']:
 hit,normal,i,d=tree.ray_cast(Vector(s['point'])+Vector((0,0,.04)),Vector((0,0,1)),2.1)
 if hit is not None:fail.append({'sample':s,'hit':names[i]})
report={'samples':len(data['samples']),'failures':len(fail),'details':fail}
(ROOT/'unity_enhanced/checks/row_occupancy_v9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Seat and crowd clearance:',len(data['samples']),'samples;',len(fail),'failures',fail[:5])
