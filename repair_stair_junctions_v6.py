"""Open genuine stair wells and connect all twelve switchback bays to concourses.
Uses existing editable architecture; dimensions are reconstruction choices, not surveyed plans.
"""
import bpy,bmesh,math,ast,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene
assert S.get('band_v5') and not S.get('stairs_connected_v6')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_楼梯连通版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
helpers=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
c=bpy.data.collections.new('21_楼梯洞口与环廊连接');S.collection.children.link(c);COL['21']=c
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
bays=[]
for i in range(12):
 a=i*math.tau/12+.11
 bays.append((a,Vector((126.5*math.cos(a),143.5*math.sin(a),0)),Vector((math.cos(a),math.sin(a),0)),Vector((-math.sin(a),math.cos(a),0))))
def localpoint(bay,x,y,z):
 a,center,rad,tan=bays[bay];p=center+rad*x+tan*y;p.z=z;return p
def in_well(p,margin=0):
 for a,center,rad,tan in bays:
  d=Vector(p)-center;x=d.dot(rad);y=d.dot(tan)
  if abs(x)<2.7+margin and -4.6-margin<y<4.7+margin:return True
 return False
def bounds(ob):
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box]
 return [min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]
def obstruction_tree():
 vs=[];fs=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
 prefixes=('环形集散厅楼板','环廊径向梁','环廊混凝土柱','红色看台背壳','外廊楼梯','楼梯连续底板','V6_洞口结构','环廊灯具外壳','管线支架')
 for ob in S.objects:
  if ob.type not in {'MESH','CURVE'} or not ob.name.startswith(prefixes):continue
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg)
  off=len(vs);vs.extend(tuple(ob.matrix_world@v.co) for v in me.vertices)
  for poly in me.polygons:fs.append(tuple(off+i for i in poly.vertices));names.append(ob.name)
  bpy.data.meshes.remove(me)
 return BVHTree.FromPolygons(vs,fs),names
def headroom_audit():
 tree,names=obstruction_tree();failures=[];samples=0
 for bay in range(12):
  for flight in range(6):
   direction=1 if flight%2==0 else -1;lane=(flight%2)*2.6-1.3
   for j in range(25):
    # Two walking strips, on either side of the photographed central handrail.
    for side in [-.55,.55]:
     z=flight*3.75+(j+1)*.15+.04
     p=localpoint(bay,lane+side,(j*.28-3.4)*direction,z)
     hit,normal,index,distance=tree.ray_cast(p,Vector((0,0,1)),2.1)
     samples+=1
     if hit is not None:failures.append({'bay':bay,'flight':flight,'step':j,'side':side,'obstacle':names[index],'clearance':round(distance+.04,4)})
 return {'sample_count':samples,'blocked_samples':len(failures),'examples':failures[:30]}
before=headroom_audit()
# One manifold cutter per bay; a disconnected union is valid for Exact Boolean.
cut=Batch('V6_TEMP_楼梯井切割',None,'21')
for i,(a,center,rad,tan) in enumerate(bays):cut.box(localpoint(i,0,.05,14),(5.4,9.3,32),a)
cutter=cut.finish();bpy.context.view_layer.update()
def difference(ob):
 mod=ob.modifiers.new('V6_楼梯井净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 # Bake only the evaluated result of this authored solid; never mutate unrelated meshes.
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob.modifiers.clear();ob.data=me
 return len(me.polygons)
floor_reports=[]
for level in [2,3,4]:
 ob=S.objects['环形集散厅楼板_F'+str(level)];old=len(ob.data.polygons);new=difference(ob)
 floor_reports.append({'floor':level,'before_faces':old,'after_faces':new})
trimmed=[]
for ob in list(S.objects):
 if ob.name.startswith('环廊径向梁'):
  old=[tuple(v.co) for v in ob.data.vertices];difference(ob)
  if old!=[tuple(v.co) for v in ob.data.vertices]:trimmed.append(ob.name)
# Remove tiny fixture boxes that would hang inside the newly open shafts.
fixture_removed=0
for ob in list(S.objects):
 if ob.type!='MESH' or not ob.name.startswith(('环廊灯具外壳','环廊灯罩_F','管线支架_F')):continue
 bm=bmesh.new();bm.from_mesh(ob.data);seen=set();remove=[]
 for vertex in list(bm.verts):
  if vertex in seen:continue
  todo=[vertex];component=[];seen.add(vertex)
  while todo:
   v=todo.pop();component.append(v)
   for edge in v.link_edges:
    q=edge.other_vert(v)
    if q not in seen:seen.add(q);todo.append(q)
  p=sum((ob.matrix_world@v.co for v in component),Vector())/len(component)
  if in_well(p,.2):remove.extend(component);fixture_removed+=1
 bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);bm.free()
# Trim the landing edge to meet the final tread without coincident top faces.
for bay in range(12):
 ob=S.objects['外廊楼梯_%02d'%bay];a,center,rad,tan=bays[bay]
 for base in [3.75,11.25,18.75]:
  # Original landing vertices are at z=base+3.55 and base+3.75.
  for v in ob.data.vertices:
   d=v.co-center;x=d.dot(rad);y=d.dot(tan)
   if abs(abs(x)-2.7)<.001 and abs(y+3.2)<.001 and (abs(v.co.z-(base+3.55))<.001 or abs(v.co.z-(base+3.75))<.001):v.co-=tan*.28
 ob.data.update()
 # Half-level platforms meet the opposite end of the first flight.
 for base in [0,7.5,15]:
  for v in ob.data.vertices:
   d=v.co-center;x=d.dot(rad);y=d.dot(tan)
   if abs(abs(x)-2.7)<.001 and abs(y-3.2)<.001 and (abs(v.co.z-(base+3.55))<.001 or abs(v.co.z-(base+3.75))<.001):v.co+=tan*.28
 ob.data.update()
# Footings and level landings already exist in the original concrete stair mesh.
# Add perimeter trimmers and open-ended guards, never a barrier across the arrival.
for bay,(a,center,rad,tan) in enumerate(bays):
 guards=Batch('V6_洞口栏杆_%02d'%bay,red,'21')
 trimmers=Batch('V6_洞口结构_%02d'%bay,concrete,'21')
 for level,z in enumerate([7.5,15,22.5],2):
  for x in [-2.95,2.95]:
   trimmers.box(localpoint(bay,x,.05,z-.64),(.4,9.7,.4),a)
   # Keep the level landing arrival at y=-4.6 open to the gallery.
   for y in [-4.4+i*.7 for i in range(14)]:guards.box(localpoint(bay,x,y,z+.55),(.045,.045,1.1),a)
   for h in [.18,.55,1.1]:guards.box(localpoint(bay,x,.05,z+h),(.055,9.3,.055),a)
  trimmers.box(localpoint(bay,0,4.9,z-.64),(6.3,.4,.4),a)
  for x in [-2.8+i*.7 for i in range(9)]:guards.box(localpoint(bay,x,4.9,z+.55),(.045,.045,1.1),a)
  for h in [.18,.55,1.1]:guards.box(localpoint(bay,0,4.9,z+h),(5.9,.055,.055),a)
 # A half-level landing must have an end guard, not an unguarded edge.
 for z in [3.75,11.25,18.75]:
  for x in [-2.6+i*.65 for i in range(9)]:guards.box(localpoint(bay,x,4.55,z+.55),(.035,.035,1.1),a)
  for h in [.18,.55,1.1]:guards.box(localpoint(bay,0,4.55,z+h),(5.3,.05,.05),a)
 guards.finish();trimmers.finish()
bpy.data.objects.remove(cutter,do_unlink=True)
# UVs in metres for newly cut slabs and added concrete trimmers.
for ob in list(c.objects)+[S.objects['环形集散厅楼板_F'+str(i)] for i in [2,3,4]]:
 if ob.type!='MESH' or concrete not in list(ob.data.materials):continue
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for face in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in face.loop_indices:
   p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]])
bpy.context.view_layer.update()
after=headroom_audit()
S['stairs_connected_v6']=True
report={'scope':'12 repeated stair bays, F2/F3/F4 connections; no first-person controller added','before':before,'after':after,'floor_openings':36,'floors':floor_reports,'trimmed_beams':trimmed,'removed_fixture_boxes':fixture_removed}
(ROOT/'unity_enhanced/checks/stair_connection_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_楼梯连通版.blend'))
print(json.dumps(report,ensure_ascii=False))
