import bpy,bmesh,math,ast,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;COL={c.name[:2]:c for c in S.collection.children};c=COL['21']
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
for fn in ['build_concert.py','upgrade_full_stadium.py','repair_stair_junctions_v6.py']:
 t=ast.parse((ROOT/fn).read_text(encoding='utf-8'));h=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id in ['cube_v','cube_f'] for v in n.targets))];exec(compile(ast.Module(body=h,type_ignores=[]),fn,'exec'))
bays=[]
for i in range(12):
 a=i*math.tau/12+.11;bays.append((a,Vector((126.5*math.cos(a),143.5*math.sin(a),0)),Vector((math.cos(a),math.sin(a),0)),Vector((-math.sin(a),math.cos(a),0))))
for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
cut=Batch('V6_TEMP_楼梯井切割',None,'21')
for i,(a,center,rad,tan) in enumerate(bays):cut.box(localpoint(i,0,.05,14),(5.4,9.3,32),a)
cutter=cut.finish();bpy.context.view_layer.update()
for level,z in enumerate([7.5,15,22.5],2):
 old=S.objects['环形集散厅楼板_F'+str(level)];new=slab('TEMP_floor',84+1.42*z,110+1.1*z,133,150,z,.45,concrete)
 old.data=new.data;bpy.data.objects.remove(new,do_unlink=True);difference(old)
for ob in list(S.objects):
 if ob.name.startswith('环廊径向梁'):difference(ob)
src=(ROOT/'repair_stair_junctions_v6.py').read_text(encoding='utf-8')
exec(src[src.index('# Trim the landing edge'):src.index('bpy.data.objects.remove(cutter')])
bpy.data.objects.remove(cutter,do_unlink=True)
exec(src[src.index('# UVs in metres'):src.index('after=headroom_audit()')])
tree,names=obstruction_tree();seams=[]
for bay in range(12):
 for z in [7.5,15,22.5]:
  for x in [-1.8,-.6,.6,1.8]:
   for y in [-5.0,-4.65,-4.55,-4.2,-3.8]:
    p=localpoint(bay,x,y,z+.1);hit,normal,index,distance=tree.ray_cast(p,Vector((0,0,-1)),.15)
    if hit is None or abs(hit.z-z)>.005:seams.append({'bay':bay,'z':z,'x':x,'y':y,'hit':list(hit) if hit else None})
manifold=[]
for level in [2,3,4]:
 ob=S.objects['环形集散厅楼板_F'+str(level)];bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free();manifold.append({'floor':level,'nonmanifold_edges':bad})
rp=ROOT/'unity_enhanced/checks/stair_connection_audit.json';report=json.loads(rp.read_text(encoding='utf-8'));report['after']=headroom_audit();report['landing_seam_samples']=720;report['landing_seam_failures']=seams;report['slab_topology']=manifold;report['floor_opening_dimensions_m']=[5.4,9.3];rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_楼梯连通版.blend'))
print(json.dumps({'headroom':report['after'],'seam_failures':len(seams),'topology':manifold},ensure_ascii=False))
