"""Connect the existing F1-F4 circulation floors to lower/middle seating entries.
Indicative reconstruction, not a surveyed vomitory plan. Existing upper-tier access is outside this patch.
"""
import bpy,bmesh,math,ast,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('stairs_connected_v6') and not S.get('seating_entries_v7')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_看台接通版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children};C=bpy.data.collections.new('22_看台入口与环廊接通');S.collection.children.link(C);COL['22']=C
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
tiers=[(76,106,1.2,23,.9,.54),(99,128,17,16,1.02,.65)]
specs=[(0,0,.08),(0,12,7.5),(1,0,15),(1,9,22.5)]
ports=[]
def point(p,t,w,z):return Vector(p['entry'])+Vector(p['rad'])*t+Vector(p['tan'])*w+Vector((0,0,z-p['height']))
for bay in range(12):
 # Offset one aisle from the exterior stair bay so the passage never bridges its open shaft.
 a=(round((bay*math.tau/12+.11-.0105)/(math.tau/40))+1)*math.tau/40+.0105
 ca,sa=math.cos(a),math.sin(a);rad=Vector((ca,sa,0));tan=Vector((-sa,ca,0))
 for level,(tier,row,zfloor) in enumerate(specs):
  rx,ry,z,n,step,rise=tiers[tier];h=z+row*rise
  entry=Vector(((rx+(row+.5)*step)*ca,(ry+(row+.5)*step)*sa,h))
  # End the passage on the solid concourse, beyond both its inner edge and the red back wall.
  length=4.0
  while length<40:
   q=entry+rad*length
   inside=((q.x/(84+1.42*zfloor+4))**2+(q.y/(110+1.1*zfloor+4))**2)>=1
   if h<13.1:f=(h-.15)/(13.1-.15);wrx=92+9.5*f;wry=120+11*f
   else:f=(h-13.1)/(28-13.1);wrx=101.5+16.5*f;wry=131+13.5*f
   outside_wall=(q.x/(wrx+3))**2+(q.y/(wry+3))**2>=1
   if inside and outside_wall:break
   length+=.25
  length+=2;q=entry+rad*length
  assert (q.x/132.7)**2+(q.y/149.7)**2<1,(bay,level,'outside concourse')
  count=math.ceil((h-zfloor)/.18);run=count*.28
  p={'bay':bay,'level':level+1,'tier':tier+1,'row':row,'entry':list(entry),'rad':list(rad),'tan':list(tan),'angle':a,'height':h,'concourse':zfloor,'length':length,'step_count':count,'step_run':run,'row_step':step,'row_rise':rise,'clear_width':2.1,'outer_width':2.4}
  ports.append(p)
cuts=Batch('V7_TEMP_看台入口切割',None,'22')
for p in ports:cuts.box(point(p,(p['length']+.7)/2,0,p['height']+1.14),(p['length']+.9,2.4,3.12),p['angle'])
cutter=cuts.finish();bpy.context.view_layer.update()
def cut_object(ob):
 m=ob.modifiers.new('V7_入口净空','BOOLEAN');m.object=cutter;m.operation='DIFFERENCE';m.solver='EXACT'
 dg=bpy.context.evaluated_depsgraph_get();data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob.modifiers.clear();ob.data=data
for name in ['三层看台_层1','三层看台_层2']:cut_object(S.objects[name])
for ob in list(S.objects):
 if not ob.name.startswith('红色看台背壳_'):continue
 # Only panels crossed by an entry shaft need an expensive Boolean evaluation.
 pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];ctr=sum(pts,Vector())/8
 cut_object(ob)
bpy.data.objects.remove(cutter,do_unlink=True)
for p in ports:
 tag='F%d_B%02d'%(p['level'],p['bay']);L=p['length'];h=p['height'];zfloor=p['concourse'];count=p['step_count'];run=p['step_run'];a=p['angle']
 floor=Batch('V7_入口地面_'+tag,concrete,'22');walls=Batch('V7_入口侧墙_'+tag,concrete,'22');rails=Batch('V7_入口扶手_'+tag,metal,'22');noses=Batch('V7_入口踏步边_'+tag,red,'22')
 floor.box(point(p,(L-run-.1)/2,0,h-.14),(L-run+.1,2.4,.28),a)
 for j in range(count):
  top=zfloor+(j+1)*(h-zfloor)/count;t=L-(j+.5)*.28
  depth=top-zfloor+.28
  floor.box(point(p,t,0,top-depth/2),(.28,2.4,depth),a)
  for side in [-1,1]:walls.box(point(p,t,side*1.125,top+.335),(.28,.15,.95),a)
  noses.box(point(p,L-j*.28-.018,0,top+.008),(.035,2.1,.016),a)
 # Low walls seal cut slab edges; their open ends meet the aisle and concourse.
 for side in [-1,1]:
  walls.box(point(p,(L-run-.1)/2,side*1.125,h+.42),(L-run+.1,.15,1.12),a)
  pts=[point(p,-.1,side*1.125,h+1.1),point(p,L-run,side*1.125,h+1.1),point(p,L,side*1.125,zfloor+1.1)]
  line('V7_连接扶手_'+tag,[tuple(v) for v in pts],.035,metal,'22')
  for j in range(int((L-run)/1.5)+1):rails.box(point(p,j*1.5,side*1.125,h+.98),(.045,.045,.24),a)
 floor.finish();walls.finish();rails.finish();noses.finish()
# Open the front safety rail only where the route reaches a front-row entry.
for tier in [0,1]:
 ob=S.objects['看台栏杆_'+str(tier)];cv=ob.data;old=[Vector(v.co[:3]) for v in cv.splines[0].points];cv.splines.clear();runs=[];run=[]
 for i in range(len(old)+1):
  q=old[i%len(old)];blocked=any(p['tier']==tier+1 and p['row']==0 and abs((q-Vector(p['entry'])).dot(Vector(p['tan'])))<1.25 and abs((q-Vector(p['entry'])).dot(Vector(p['rad'])))<2 for p in ports)
  if blocked:
   if len(run)>1:runs.append(run)
   run=[]
  else:run.append(q)
 if len(run)>1:runs.append(run)
 for run in runs:
  sp=cv.splines.new('POLY');sp.points.add(len(run)-1)
  for v,q in zip(sp.points,run):v.co=(*q,1)
# World-space concrete UVs on new and cut architecture.
for ob in list(C.objects)+[S.objects['三层看台_层1'],S.objects['三层看台_层2']]:
 if ob.type!='MESH' or concrete not in list(ob.data.materials):continue
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
# The new inspection viewpoint is stored with existing detail viewpoints.
p=next(p for p in ports if p['bay']==0 and p['level']==2)
for prefix,position in [('VIEW_',point(p,p['length']+1,0,p['concourse']+1.8)),('LOOK_',point(p,-3,0,p['height']+1.5))]:
 ob=link(bpy.data.objects.new(prefix+'14_SeatingEntry',None),'19');ob.location=position
(ROOT/'unity_enhanced/checks/seating_entries.json').write_text(json.dumps({'scope':'48 connections from existing F1-F4 floors to lower/middle seating; upper-tier circulation is not added','ports':ports},ensure_ascii=False,indent=2),encoding='utf-8')
S['seating_entries_v7']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_看台接通版.blend'))
print('Created',len(ports),'seating-concourse connections')
