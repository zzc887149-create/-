import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
for p in ports:
 p['entry']=Vector(p['entry']);p['rad']=Vector(p['rad']);p['tan']=Vector(p['tan'])
def overlaps(q):
 for p in ports:
  if not p['height']-.4<q.z<p['height']+4.8:continue
  d=q-p['entry'];t=d.dot(p['rad'])
  if -.65<t<min(p['length'],(math.floor(3.02/p['row_rise'])+.7)*p['row_step']) and abs(d.dot(p['tan']))<1.65:return True
 return False
report=[]
source=[o for o in S.objects if o.type=='MESH' and (o.name.startswith(('看台座椅_','NEAR_')) or any(c.name.startswith('07_') for c in o.users_collection))]
D=bpy.data.scenes['UNITY_ENHANCED_V3']
export=[o for o in D.objects if o.type=='MESH' and o.name.startswith(('Chunk_SEATS_','Chunk_CROWD_','Chunk_PHONES_'))]
for ob in source+export:
 bm=bmesh.new();bm.from_mesh(ob.data);seen=set();remove=[];components=0
 for vertex in list(bm.verts):
  if vertex in seen:continue
  todo=[vertex];part=[];seen.add(vertex)
  while todo:
   v=todo.pop();part.append(v)
   for edge in v.link_edges:
    q=edge.other_vert(v)
    if q not in seen:seen.add(q);todo.append(q)
  center=ob.matrix_world@(sum((v.co for v in part),Vector())/len(part))
  if overlaps(center):remove.extend(part);components+=1
 if remove:
  bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);ob.data.update()
  report.append({'object':ob.name,'removed_components':components,'vertices':len(remove)})
 bm.free()
geo=ROOT/'unity_enhanced/optimization_geometry.json';data=json.loads(geo.read_text(encoding='utf-8'))
for r in data['details']:
 if r['category'] not in ['SEATS','CROWD','PHONES']:continue
 for suffix,key in [('_L0','near_triangles'),('_L1','far_triangles')]:
  ob=D.objects.get(r['chunk']+suffix)
  if ob:r[key]=sum(len(f.vertices)-2 for f in ob.data.polygons)
data['near_triangles']=sum(r['near_triangles'] for r in data['details']);data['far_triangles']=sum(r['far_triangles'] for r in data['details'])
geo.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'unity_enhanced/checks/seating_clearance_cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
S['seating_occupancy_cleared_v7']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Cleaned',len(report),'meshes;',sum(r['removed_components'] for r in report),'disconnected components across source and exported LODs')
