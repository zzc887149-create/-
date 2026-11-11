import bpy,math,json,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
M={n:bpy.data.materials[n] for n in ('concrete','栏杆细金属')}
src=(ROOT/'rebuild_seating_v20.py').read_text(encoding='utf-8');tree=ast.parse(src)
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
for ob in list(S.objects):
    if ob.name.startswith(('V20_绕行护栏_','V20_上层折返核_','V20_上层折返护栏_','V20_通道_','V20_围护_','V20_后排分流_','V20_中层分流_','V20_上层洞口平台_')):bpy.data.objects.remove(ob,do_unlink=True)
samples=[];segments=[];portals=[];cuts=[]
part=src[src.index('for b in range(N):\n    # Lower tier'):src.index('# Fascias are closed')]
part=part.replace("if band!='upper_middle':passage(2,b,r0+.15,10.05,z,z,", "passage(2,b,r0+.15,14.8 if band=='upper_middle' else 10.05,z,z,")
part=part.replace('nf=max(2,math.ceil((high-low)/5.0)*2)','nf=max(2,math.ceil((high-low)/5.0)*2)\n        if high==levels[-1]:nf=3')
part=part.replace('outward=flight%2==0;wc=-.61 if outward else .61','outward=flight%2==0;wc=(-1.12+f*1.12) if high==levels[-1] else (-.61 if outward else .61)')
part=part.replace('math.ceil((zhi-zlow)/.17)', 'math.ceil((zhi-zlow)/.19)')
part=part.replace('for z in levels:', 'for z in levels[:-1]:')
exec(part)
for b in range(0):
    z=H(2,15,b);floor=Mesh('V20_通道_L3_upper_middle_%02d'%b,M['concrete']);rail=Mesh('V20_绕行护栏_%02d'%b,M['栏杆细金属'])
    tile(floor,2,b,9.25,17.55,-3.8,-1.4,z)
    tile(floor,2,b,9.25,10.25,-2.6,1.2,z)
    tile(floor,2,b,16.65,17.55,-2.6,1.2,z)
    for offset in [-.55,0,.55]:
        path=[q(2,b,9.75,-.6,z),q(2,b,9.75,-2.6+offset,z)]+[q(2,b,r,-2.6+offset,z) for r in [10+i*.23 for i in range(31)]]+[q(2,b,17.1,-2.6+offset,z),q(2,b,17.1,0,z)]
        for p in path:sample(p,'L3_upper_middle_%02d'%b,b)
        route(path,'L3_upper_middle_%02d'%b)
    for w in [-3.8,-1.4]:track(rail,[q(2,b,r,w,z) for r in [10.3+i*.4 for i in range(16)]])
    floor.finish();rail.finish()
data=json.loads((ROOT/'unity_enhanced/checks/v20_layout.json').read_text(encoding='utf-8'))
data['samples']=[s for s in data['samples'] if s['kind'].startswith('tier')]+samples
data['segments']=[s for s in data['segments'] if s['kind'].startswith('tier')]+segments
for name in ('环廊顶面管线_F3','环廊顶面管线_F3.001'):
    ob=S.objects.get(name)
    if ob:ob.location.z=-.9
(ROOT/'unity_enhanced/checks/v20_layout.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/v20_checks.json').write_text(json.dumps({'samples':data['samples'],'segments':data['segments']},ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
