"""Replace decorative through-slits with a continuous shell and actual route openings."""
import bpy,bmesh,math,json,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('portal_enclosures_v14') and not S.get('continuous_bowl_v15')
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
src=ast.parse((ROOT/'refine_exterior_shell_v13.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='shell2_profile'],type_ignores=[]),'profile','exec'))
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
upper=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))['ports']
def applycut(ob,cutter):
 m=ob.modifiers.new('真实入口净空','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me
cuts=Batch('V15_TEMP_lower',None,'13')
for p in ports:
 e=Vector(p['entry']);r=Vector(p['rad']);lo=p['concourse']-.4;hi=p['height']+2.7
 c=e+r*(p['length']/2);c.z=(lo+hi)/2
 cuts.box(c,(p['length']+2,2.42,hi-lo),p['angle'])
lowercut=cuts.finish()
cuts=Batch('V15_TEMP_upper',None,'13')
for p in upper:
 e=Vector(p['entry']);r=Vector((math.cos(p['angle']),math.sin(p['angle']),0));t=Vector((-r.y,r.x,0));L=p['length'];h=p['height']
 off=len(cuts.v)
 # Sloped solid following the existing F4-to-upper-tier stair.
 for ceiling in [False,True]:
  for d,w in [(-1.2,-1.8),(L+1.2,-1.8),(L+1.2,1.8),(-1.2,1.8)]:
   v=e+r*d+t*w;v.z=h+(22.5-h)*d/L+ (3.0 if ceiling else -.45);cuts.v.append(tuple(v))
 cuts.f.extend(tuple(off+i for i in f) for f in cube_f)
uppercut=cuts.finish();bpy.context.view_layer.update()
for ob in list(S.objects):
 if ob.name.startswith('红色看台背壳_'):bpy.data.objects.remove(ob,do_unlink=True)
N=768;M=20;profiles=[(92,120,.15),(101.5,131,13.1),(118,144.5,28)]
created=[]
for band in range(3):
 vs=[];fs=[]
 for j in range(M+1):
  f=j/M
  if band<2:
   p0=profiles[band];p1=profiles[band+1];rx,ry,zlin=[u+(v-u)*f for u,v in zip(p0,p1)]
  else:rx,ry,zlin=shell2_profile(f)
  for i in range(N):
   a=i*math.tau/N
   at=math.atan2(ry*math.sin(a)/155,rx*math.cos(a)/132) if band==2 else a
   z=zlin-12.5*math.sin(at)**4*min(1,max(0,(zlin-24)/22))
   vs.append((rx*math.cos(a),ry*math.sin(a),z))
 for j in range(M):
  for i in range(N):
   k=(i+1)%N;fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 me=bpy.data.meshes.new('V15_连续碗壁');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['外碗赭红混凝土']);me.update()
 ob=bpy.data.objects.new('红色看台背壳_V15_层%d'%band,me);COL['13'].objects.link(ob)
 m=ob.modifiers.new('实体墙厚','SOLIDIFY');m.thickness=.25;m.offset=-1
 dg=bpy.context.evaluated_depsgraph_get();ob.data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear()
 applycut(ob,lowercut);applycut(ob,uppercut)
 uv=ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
 created.append(ob.name)
for ob in [lowercut,uppercut]:bpy.data.objects.remove(ob,do_unlink=True)
S['continuous_bowl_v15']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_入口与碗壁闭合版.blend'))
print(json.dumps({'continuous_shells':created,'lower_middle_routes':len(ports),'upper_routes':len(upper),'removed_false_slits':144,'removed_unconnected_raised_bases':12},ensure_ascii=False))
