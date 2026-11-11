"""Editable landing, flanking aisles and guarded vomitory edges for the v7 model."""
import bpy,bmesh,ast,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('seating_entries_v7') and not S.get('seating_mouths_v8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_看台衔接精修版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children};C=bpy.data.collections.new('23_看台出口平台与分流梯道');S.collection.children.link(C);COL['23']=C
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
tiers=[(76,106,1.2,23,.9,.54,12),(99,128,17,16,1.02,.65,9)]
walk=[];routes=[];seat_links=[];cut=Batch('V8_TEMP_梯道与平台',None,'23')
def prism(batch,pts,low,high):
 off=len(batch.v);batch.v.extend([(v.x,v.y,z) for z in [low,high] for v in pts]);batch.f.extend(tuple(off+i for i in f) for f in cube_f)
def params(p):
 rx,ry,z,n,step,rise,mid=tiers[p['tier']-1];a=p['angle'];scale=math.hypot(rx*math.sin(a),ry*math.cos(a))
 def q(r,w,h):
  theta=a+w/scale;return Vector(((rx+step*.5+r)*math.cos(theta),(ry+step*.5+r)*math.sin(theta),h))
 return rx,ry,z,n,step,rise,mid,q
def tile(batch,q,r0,r1,w0,w1,low,high):prism(batch,[q(r0,w0,0),q(r1,w0,0),q(r1,w1,0),q(r0,w1,0)],low,high)
for p in ports:
 rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height']
 tile(cut,q,r-.51,r+.51,-3.2,3.2,h-.35,h+2.75)
 if p['row']==0:
  for side in [-1,1]:tile(cut,q,-.51,(n-1)*step+.51,side*2.4-.78,side*2.4+.78,z-.6,z+n*rise+3)
cutter=cut.finish();bpy.context.view_layer.update()
for name in ['三层看台_层1','三层看台_层2']:
 ob=S.objects[name];m=ob.modifiers.new('V8_看台梯道开槽','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
 dg=bpy.context.evaluated_depsgraph_get();data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob.modifiers.clear();ob.data=data
bpy.data.objects.remove(cutter,do_unlink=True)
for p in ports:
 rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height'];tag='F%d_B%02d'%(p['level'],p['bay'])
 deck=Batch('V8_出口分流平台_'+tag,concrete,'23');tile(deck,q,r-.5,r+.5,-3.2,3.2,h-.28,h+.008);deck.finish()
 # Guard the drop ahead while leaving both stair lanes open.
 width=3.15 if p['row']==0 else 1.5
 for hh in [.18,.55,1.1]:line('V8_出口前缘护栏_'+tag,[q(r-.48,-width,h+hh),q(r-.48,width,h+hh)],.03,metal,'23')
 for i in range(int(width*2/.6)+1):
  w=-width+i*width*2/int(width*2/.6);beam('V8_护栏立柱_'+tag,q(r-.48,w,h),q(r-.48,w,h+1.1),.045,.045,metal,'23')
 # Tall stepped cheeks close the exposed zig-zag sides of the opening.
 cheeks=Batch('V8_洞口阶梯栏板_'+tag,concrete,'23');edges=Batch('V8_洞口上缘_'+tag,metal,'23')
 length=(math.floor(3.02/rise)+.7)*step
 for k in range(math.ceil(length/step)):
  lo=max(.5,k*step);hi=min(length,(k+1)*step)
  if hi<=lo:continue
  top=h+(k+1)*rise+.95
  for side in [-1,1]:
   pos=Vector(p['entry'])+Vector(p['rad'])*((lo+hi)/2)+Vector(p['tan'])*(side*1.3);pos.z=(h-.2+top)/2
   cheeks.box(pos,(hi-lo,.24,top-(h-.2)),p['angle']);pos.z=top+.05;edges.box(pos,(hi-lo,.055,.055),p['angle'])
 cheeks.finish();edges.finish()
 for t in [-.3,0,.3]:
  for w in [-2.4,-1.2,0,1.2,2.4]:walk.append({'kind':'landing','bay':p['bay'],'level':p['level'],'point':list(q(r+t,w,h+.008))})
 for side in [-1,1]:routes.append({'kind':'landing_turn','points':[list(q(r,w*side,h+1.3)) for w in [0,.6,1.2,1.8,2.4]]})
 if p['row']!=0:continue
 # Aisle profiles have flat landings, plus half treads at each flight end.
 knots=[(-.5,z),(.5,z),(mid*step-.5,z+mid*rise),(mid*step+.5,z+mid*rise),((n-1)*step,z+(n-1)*rise)]
 for side in [-1,1]:
  stairs=Batch('V8_看台细分梯道_'+tag+'_'+str(side),concrete,'23');noses=Batch('V8_梯道踏边_'+tag+'_'+str(side),red,'23');path=[];profiles=[]
  for (r0,h0),(r1,h1) in zip(knots,knots[1:]):
   count=max(1,math.ceil((h1-h0)/.18-1e-5));run=(r1-r0)/count
   if abs(h1-h0)<.001:
    sections=[(r0,r1,h0)]
   else:sections=[(max(r0,r0+(i-.5)*run),min(r1,r0+(i+.5)*run),h0+i*(h1-h0)/count) for i in range(count+1)]
   for lo,hi,top in sections:
    tile(stairs,q,lo,hi,side*2.4-.8,side*2.4+.8,top-.3,top+.008)
    tile(noses,q,lo,lo+.025,side*2.4-.76,side*2.4+.76,top+.008,top+.014)
    for w in [side*2.4-.5,side*2.4,side*2.4+.5]:walk.append({'kind':'aisle','bay':p['bay'],'tier':p['tier'],'point':list(q((lo+hi)/2,w,top+.008))})
    path.append(list(q((lo+hi)/2,side*2.4,top+1.3)));profiles.append((lo,hi,top))
  # Each row gets a short, level lateral connection to its seating platform.
  for j in range(n):
   target=z+j*rise
   section=min(profiles,key=lambda s:abs(s[2]-target))
   lo,hi,top=section
   # Match exact row heights even where the .65 m row rise is divided into four treads.
   rj=(lo+hi)/2
   tile(stairs,q,rj-.10,rj+.10,min(side*3.02,side*3.6),max(side*3.02,side*3.6),min(target,top)-.25,max(target,top)+.008)
   seat_links.append({'bay':p['bay'],'tier':p['tier'],'row':j,'side':side,'height_difference':round(abs(top-target),4)})
  stairs.finish();noses.finish();routes.append({'kind':'aisle','points':path})
 # Small inspection viewpoint on the seating side of the upper mouth.
 if p['bay']==0 and p['tier']==1:
  upper=next(v for v in ports if v['bay']==0 and v['level']==2)
  for prefix,position in [('VIEW_',Vector(upper['entry'])-Vector(upper['rad'])*6+Vector(upper['tan'])*5+Vector((0,0,4))),('LOOK_',Vector(upper['entry'])+Vector(upper['rad'])+Vector((0,0,.5)))]:
   ob=link(bpy.data.objects.new(prefix+'15_SeatingJunction',None),'19');ob.location=position
# Texture coordinates and normals after all Boolean/new geometry work.
for ob in list(C.objects)+[S.objects['三层看台_层1'],S.objects['三层看台_层2']]:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
data={'landings':48,'flanking_aisles':48,'samples':walk,'routes':routes,'row_links':seat_links}
(ROOT/'unity_enhanced/checks/seating_junctions_v8.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
S['seating_mouths_v8']=True;bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Added 48 landings and 48 flanking aisles;',len(walk),'sample points')
