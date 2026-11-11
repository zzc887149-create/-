"""Upper-tier access following the existing saddle-deformed seating surface."""
import bpy,bmesh,ast,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('row_connections_v9') and not S.get('upper_tier_v10')
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children};C=bpy.data.collections.new('24_第三层看台连通');S.collection.children.link(C);COL['24']=C
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
ob=S.objects['三层看台_层3'];dg=bpy.context.evaluated_depsgraph_get();me=ob.evaluated_get(dg).to_mesh()
tier_tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.evaluated_get(dg).to_mesh_clear()
def surface(x,y):
 hit,_,_,_=tier_tree.ray_cast(Vector((x,y,70)),Vector((0,0,-1)),60)
 if hit is None:raise ValueError(('Outside upper seating',x,y))
 return hit.z
def prism(batch,points,low,tops):
 off=len(batch.v);batch.v.extend([(p.x,p.y,low) for p in points]+[(p.x,p.y,z) for p,z in zip(points,tops)]);batch.f.extend(tuple(off+i for i in f) for f in cube_f)
def tile(batch,q,r0,r1,w0,w1,low,top):
 ps=[q(r0,w0,0),q(r1,w0,0),q(r1,w1,0),q(r0,w1,0)]
 ts=[top(w0),top(w0),top(w1),top(w1)] if callable(top) else [top]*4
 prism(batch,ps,low,ts)
ports=[];samples=[];routes=[]
def sample(q,kind,bay):samples.append({'kind':kind,'bay':bay,'point':list(q)})
def route(points,kind):routes.append({'kind':kind,'points':[list(p+Vector((0,0,1.3))) for p in points]})
def makeq(a):
 scale=math.hypot(119*math.sin(a),144*math.cos(a))
 def q(r,w,z):
  t=a+w/scale;return Vector(((119.55+r)*math.cos(t),(144.55+r)*math.sin(t),z))
 return q
def cut(ob,cutter):
 m=ob.modifiers.new('V10_通路净空','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 ob.modifiers.clear();ob.data=me
for bay in range(12):
 # A radial stepped passage starts on F4 and rises inward to the upper front row.
 # Midway between the four-per-bay structural/legacy routes: avoids columns and F4 passages.
 a=bay*math.tau/12+.458;q=makeq(a);entry=q(0,0,0);h=surface(entry.x,entry.y)
 rad=Vector((math.cos(a),math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0))
 count=math.ceil((h-22.5)/.18);run=count*.28;start=entry+rad*run;start.z=22.5
 ports.append({'bay':bay,'angle':a,'height':h,'entry':list(entry),'start':list(start),'length':run,'step_count':count})
 floor=Batch('V10_上层接入楼梯_%02d'%bay,concrete,'24');nose=Batch('V10_上层接入踏边_%02d'%bay,red,'24');path=[]
 # Level F4 approach platform outside the first riser.
 ps=[start+rad*.8+tan*w for w in [-1.2,1.2]]+[start+tan*w for w in [1.2,-1.2]]
 prism(floor,ps,22.15,[22.508]*4)
 for k in range(count):
  outer=run-k*.28;inner=run-(k+1)*.28;top=22.5+(k+1)*(h-22.5)/count
  points=[entry+rad*inner+tan*(-1.2),entry+rad*outer+tan*(-1.2),entry+rad*outer+tan*1.2,entry+rad*inner+tan*1.2]
  prism(floor,points,22.15,[top]*4)
  edge=[entry+rad*inner+tan*(-1.15),entry+rad*(inner+.025)+tan*(-1.15),entry+rad*(inner+.025)+tan*1.15,entry+rad*inner+tan*1.15]
  prism(nose,edge,top,[top+.006]*4)
  for w in [-.75,0,.75]:sample(entry+rad*((inner+outer)/2)+tan*w+Vector((0,0,top)),'upper_access_stair',bay)
  path.append(entry+rad*((inner+outer)/2)+Vector((0,0,top)))
 floor.finish();nose.finish();route(list(reversed(path)),'upper_access')
 for side in [-1,1]:
  pts=[start+rad*.8+tan*(side*1.23)+Vector((0,0,1.1))]
  pts.extend(entry+rad*(run-k*.28)+tan*(side*1.23)+Vector((0,0,22.5+k*(h-22.5)/count+1.1)) for k in range(0,count+1,4))
  pts.append(entry+tan*(side*1.23)+Vector((0,0,h+1.1)));line('V10_接入楼梯扶手_%02d'%bay,pts,.035,metal,'24')
  for k in range(0,count+1,5):
   p=entry+rad*(run-k*.28)+tan*(side*1.23)+Vector((0,0,22.5+k*(h-22.5)/count));beam('V10_接入扶手立柱',p,p+Vector((0,0,1.1)),.045,.045,metal,'24')
# Cut aisles and entry tunnels separately to avoid overlapping cutter self-intersections.
for mode in ['aisles','portals']:
 cutterbatch=Batch('V10_TEMP_'+mode,None,'24')
 for p in ports:
  q=makeq(p['angle']);h=p['height'];entry=Vector(p['entry']);rad=Vector((math.cos(p['angle']),math.sin(p['angle']),0))
  if mode=='aisles':
   for side in [-1,1]:tile(cutterbatch,q,-.54,20.35,side*2.8-1.4,side*2.8+1.4,24,51)
  else:
   # One sloped tunnel solid is more reliable than a self-overlapping stack of step cutters.
   count=p['step_count'];run=p['length']
   outer=entry+rad*(run+1.2);inner=entry-rad*2;off=len(cutterbatch.v)
   cutterbatch.v.extend([tuple(outer+Vector((-rad.y,rad.x,0))*w+Vector((0,0,z))) for z,w in [(22.0,-1.8),(h-.5,-1.8),(h-.5,1.8),(22.0,1.8),(25.5,-1.8),(h+3,-1.8),(h+3,1.8),(25.5,1.8)]])
   cutterbatch.f.extend(tuple(off+i for i in face) for face in cube_f)
 cutter=cutterbatch.finish();bpy.context.view_layer.update();cut(S.objects['三层看台_层3'],cutter)
 for ob in list(S.objects):
  if ob.name.startswith('红色看台背壳_'):cut(ob,cutter)
 bpy.data.objects.remove(cutter,do_unlink=True)
# Pair of row-aligned aisles at every upper entrance. Heights come from the original mesh.
for p in ports:
 bay=p['bay'];q=makeq(p['angle']);h=p['height'];a=p['angle'];div=5;step=1.1;n=19
 def rowh(j,w):v=q(j*step,w,0);return surface(v.x,v.y)
 landing=Batch('V10_上层出口平台_%02d'%bay,concrete,'24')
 tile(landing,q,-.5,.12,-3.2,3.2,h-.4,lambda w:rowh(0,w)+.008);landing.finish()
 line('V10_上层前缘护栏',[q(-.48,w,rowh(0,w)+1.1) for w in [-3.2,0,3.2]],.035,metal,'24')
 for w in [-3.2,-1.6,0,1.6,3.2]:beam('V10_前缘护栏立柱',q(-.48,w,rowh(0,w)),q(-.48,w,rowh(0,w)+1.1),.05,.05,metal,'24')
 for side in [-1,1]:
  b=Batch('V10_上层逐排梯道_%02d_%s'%(bay,side),concrete,'24');nr=Batch('V10_上层踏步边_%02d_%s'%(bay,side),red,'24');path=[]
  for k in range((n-1)*div+1):
   j=min(k//div,n-2);f=(k-j*div)/div;r=k*step/div;lo=r-step/div/2 if k else -.5;hi=r+step/div/2 if k<(n-1)*div else r+.5
   def top(w):return rowh(j,w)*(1-f)+rowh(j+1,w)*f+.008
   tile(b,q,lo,hi,side*2.4-.8,side*2.4+.8,h-.45,top)
   if k%div:tile(nr,q,lo,lo+.025,side*2.4-.76,side*2.4+.76,h-.45,lambda w:top(w)+.006)
   for w in [side*2.4-.5,side*2.4,side*2.4+.5]:sample(q(r,w,top(w)),'upper_aisle',bay)
   path.append(q(r,side*2.4,top(side*2.4)))
  for j in range(n):
   r=j*step;tile(b,q,r-.1,r+.1,min(side*3.02,side*4.05),max(side*3.02,side*4.05),h-.45,lambda w:rowh(j,w)+.008)
   for dr in [-.08,0,.08]:
    for w in [3.05,3.18,3.21,3.4,3.64,3.7,3.85]:sample(q(r+dr,side*w,rowh(j,side*w)+.008),'upper_row_turn',bay)
   route([q(r,side*w,rowh(j,side*w)+.008) for w in [2.4,3.2,3.85]],'upper_row_turn')
  b.finish();nr.finish();route(path,'upper_aisle')
  route([q(0,w*side,rowh(0,w*side)+.008) for w in [0,.6,1.2,1.8,2.4]],'upper_landing_turn')
# UVs, outward normals and a dedicated viewing position.
for ob in list(C.objects)+[S.objects['三层看台_层3']]:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
p=ports[0];q=makeq(p['angle']);h=p['height']
for prefix,point in [('VIEW_',q(-6,6,h+4)),('LOOK_',q(1,0,h+1))]:
 o=link(bpy.data.objects.new(prefix+'16_UpperTier',None),'19');o.location=point
data={'ports':ports,'samples':samples,'routes':routes,'row_links':456}
(ROOT/'unity_enhanced/checks/upper_tier_v10.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
checks={'samples':samples,'segments':[{'kind':r['kind'],'a':a,'b':b} for r in routes for a,b in zip(r['points'],r['points'][1:])]}
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/upper_tier_checks.json').write_text(json.dumps(checks,ensure_ascii=False),encoding='utf-8')
S['upper_tier_v10']=True;bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_三层看台连通版.blend'))
print('Upper tier created:',len(samples),'samples',len(routes),'routes')
