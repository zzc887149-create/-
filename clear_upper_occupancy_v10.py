import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
data=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'));ports=data['ports']
grid={}
for s in data['samples']:
 p=Vector(s['point']);grid.setdefault((math.floor(p.x),math.floor(p.y)),[]).append(p)
def delta(a,b):return (a-b+math.pi)%math.tau-math.pi
def overlaps(q):
 if not 22<q.z<52:return False
 for ix in range(math.floor(q.x)-1,math.floor(q.x)+2):
  for iy in range(math.floor(q.y)-1,math.floor(q.y)+2):
   for p in grid.get((ix,iy),[]):
    if (Vector((q.x,q.y))-Vector((p.x,p.y))).length<1.05 and p.z-.15<q.z<p.z+2.25:return True
 a=math.atan2(q.y/144.55,q.x/119.55);base=Vector((119.55*math.cos(a),144.55*math.sin(a),q.z));r=(q-base).dot(Vector((math.cos(a),math.sin(a),0)));scale=math.hypot(119*math.sin(a),144*math.cos(a))
 for p in ports:
  w=delta(a,p['angle'])*scale
  if -.8<r<20.5 and 1.25<abs(w)<4.5:return True
  entry=Vector(p['entry']);rad=Vector((math.cos(p['angle']),math.sin(p['angle']),0));tan=Vector((-rad.y,rad.x,0));d=q-entry
  if -2<d.dot(rad)<p['length']+2 and abs(d.dot(tan))<2.25:return True
 return False
D=bpy.data.scenes['UNITY_ENHANCED_V3'];source=[o for o in S.objects if o.type=='MESH' and (o.name.startswith(('看台座椅_','NEAR_')) or any(c.name.startswith('07_') for c in o.users_collection))]
export=[o for o in D.objects if o.type=='MESH' and o.name.startswith(('Chunk_SEATS_','Chunk_CROWD_','Chunk_PHONES_'))];report=[]
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
 if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);ob.data.update();report.append({'object':ob.name,'components':components,'vertices':len(remove)})
 bm.free()
geo=ROOT/'unity_enhanced/optimization_geometry.json';g=json.loads(geo.read_text(encoding='utf-8'))
for r in g['details']:
 if r['category'] not in ['SEATS','CROWD','PHONES']:continue
 for suffix,key in [('_L0','near_triangles'),('_L1','far_triangles')]:
  ob=D.objects.get(r['chunk']+suffix)
  if ob:r[key]=sum(len(f.vertices)-2 for f in ob.data.polygons)
g['near_triangles']=sum(r['near_triangles'] for r in g['details']);g['far_triangles']=sum(r['far_triangles'] for r in g['details']);geo.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'unity_enhanced/checks/upper_occupancy_cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Upper occupancy cleanup:',sum(r['components'] for r in report),'components in',len(report),'meshes')
# Independent upward ray check against remaining seats and crowd.
verts=[];faces=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in source:
 me=ob.evaluated_get(dg).to_mesh();off=len(verts);verts.extend(ob.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:faces.append([off+i for i in f.vertices]);names.append(ob.name)
 ob.evaluated_get(dg).to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);fail=[]
for s in data['samples']:
 q=Vector(s['point']);hit,_,i,_=tree.ray_cast(q+Vector((0,0,.04)),Vector((0,0,1)),2.1)
 if hit is not None:fail.append({'kind':s['kind'],'bay':s['bay'],'hit':names[i],'point':list(hit)})
check={'samples':len(data['samples']),'failures':len(fail),'details':fail};(ROOT/'unity_enhanced/checks/upper_occupancy_validation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
print('Upper occupancy validation:',len(fail),'failures',fail[:10])
