import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'));ns=[n for n in src.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)];exec(compile(ast.Module(body=ns,type_ignores=[]),'helpers','exec'));COL={c.name[:2]:c for c in S.collection.children}
for o in list(S.objects):
 if o.name.startswith('V18_外接平台'):bpy.data.objects.remove(o,do_unlink=True)
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
checkpath=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/junction_checks.json';checks=json.loads(checkpath.read_text(encoding='utf-8'))
for p in ports:
 if p['level']!=4 or p['bay'] not in [9,23]:continue
 e=Vector(p['entry']);r=Vector(p['rad']);t=Vector(p['tan']);L=p['length'];h=p['concourse']
 def q(d,w,z):v=e+r*d+t*w;v.z=z;return v
 b=Batch('V18_外接平台侧向_'+str(p['bay']),bpy.data.materials['concrete'],'22');b.box(q(L+.4,1.8,h-.147),(1.0,6.0,.3),p['angle']);o=b.finish();uv=o.data.uv_layers.new(name='MetreUV')
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 rail=bpy.data.materials['栏杆细金属']
 for hh in [.55,1.1]:
  line('V18_外接平台外护栏',[q(L+.9,-1.2,h+hh),q(L+.9,4.8,h+hh)],.035,rail,'22')
  line('V18_外接平台内护栏',[q(L-.1,1.3,h+hh),q(L-.1,4.8,h+hh)],.035,rail,'22')
 for w in [-1.2,0,1.2,2.4,3.6,4.8]:beam('V18_外接平台护栏立柱',q(L+.9,w,h),q(L+.9,w,h+1.1),.045,.045,rail,'22')
 path=[]
 for w in [0,.5,1,1.5,2,2.5,3,3.5,4,4.5]:
  pos=q(L+.4,w,h+.003);checks['samples'].append({'kind':'bypass_landing','bay':p['bay'],'point':list(pos)});path.append(list(pos+Vector((0,0,1.3))))
 checks['segments'].extend({'kind':'bypass_landing','a':a,'b':b} for a,b in zip(path,path[1:]))
checkpath.write_text(json.dumps(checks,ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
