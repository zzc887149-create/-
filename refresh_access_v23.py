"""Refresh access meshes and matching checks without regenerating seats/crowds."""
import bpy,math,json,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');CHECK=ROOT/'unity_enhanced/checks';PKG=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
S=bpy.context.scene;C=next(c for c in S.collection.children if c.name.startswith('27_'));N=24;PHASE=.03834;HALF=2.4;tables={}
M={n:bpy.data.materials[n] for n in ('concrete','栏杆细金属')}
tree=ast.parse((ROOT/'rebuild_seating_v23.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
for ob in list(S.objects):
    if ob.name.startswith(('V23_通道_','V23_围护_','V23_入口分流_','V23_洞口外梯道_','V23_洞口外扶手_','V23_上层水平环廊_','V23_环廊护栏_','V23_原楼梯向上续接_','V23_续接楼梯扶手_','V23_连续梯道_','V23_梯道扶手_')):bpy.data.objects.remove(ob,do_unlink=True)
data=json.loads((CHECK/'v23_layout.json').read_text(encoding='utf-8'))
samples=[];segments=[];cuts=[];portals=[];counts=[]
tierloop=next(n for n in tree.body if isinstance(n,ast.For) and ast.unparse(n.iter)=='enumerate(TIERS)')
exec(compile(ast.Module(body=[tierloop],type_ignores=[]),'tiers','exec'))
exec(compile((ROOT/'v23_access_geometry.py').read_text(encoding='utf-8'),'access','exec'))
data.update(samples=samples,segments=segments,portals=portals)
(CHECK/'v23_layout.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(PKG/'Editor/v23_checks.json').write_text(json.dumps({'samples':samples,'segments':segments},ensure_ascii=False),encoding='utf-8')
(PKG/'Editor/v23_portals.json').write_text(json.dumps({'portals':portals},ensure_ascii=False),encoding='utf-8')
vv=[];ff=[]
for cut in cuts:
    off=len(vv);vv.extend(cut.v);ff.extend(tuple(off+i for i in f) for f in cut.f)
(CHECK/'v23_cutters.json').write_text(json.dumps({'v':vv,'f':ff}),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
