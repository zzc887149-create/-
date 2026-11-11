"""Deterministic circulation repair with explicit landing-to-flight route checks."""
import bpy,math,json,ast,bisect,textwrap
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
samples=[];segments=[];portals=[];cuts=[];dimensions=[]
lower=src[src.index('    # Lower tier'):src.index('    # A compact rear switchback')]
def pathcheck(points,kind,b):
    for p in points:sample(p,kind,b)
    route(points,kind)
for b in range(N):
    exec(textwrap.dedent(lower))
    levels=[22.5,H(2,0,b)-2.4,H(2,4,b),H(2,15,b)]
    short=levels[3]-levels[2]<3.6
    front=10.25;back=15.35 if short else 14.3
    core=Mesh('V20_上层折返核_%02d'%b,M['concrete']);guard=Mesh('V20_上层折返护栏_%02d'%b,M['栏杆细金属'])
    tile(core,2,b,3,10.2,.8,3.2,22.5)
    tile(core,2,b,2.7,3.3,-.2,3.2,22.5);tile(core,2,b,9.25,10.25,-1.2,3.2,22.5)
    for w in [1.3,2,2.7]:pathcheck([q(2,b,3+i*.24,w,22.5) for i in range(31)],'upper_F4_bridge',b)
    for li,(low,high) in enumerate(zip(levels,levels[1:])):
        nf=(1 if short else 3) if li==2 else max(2,math.ceil((high-low)/5)*2)
        centers=[-1.12,0,1.12] if nf==3 else [-.61 if f%2==0 else .61 for f in range(nf)]
        for f in range(nf):
            zlow=low+(high-low)*f/nf;zhi=low+(high-low)*(f+1)/nf
            outward=f%2==0;wc=centers[f];ns=max(1,math.ceil((zhi-zlow)/.19));going=(back-front)/ns
            dimensions.append({'bay':b,'level':li,'flight':f,'rise':(zhi-zlow)/ns,'going':going,'width':1.02})
            # Each transfer platform covers its two actual flight axes, not an unrelated centerline.
            for end,z,wother in [(False,zlow,centers[f-1] if f else 0),(True,zhi,centers[f+1] if f+1<nf else 0)]:
                rear=outward if end else not outward
                ra,rb=(back,back+.95) if rear else (front-1,front)
                wa,wb=min(wc,wother)-.51,max(wc,wother)+.51
                tile(core,2,b,ra,rb,wa,wb,z)
                pts=[q(2,b,(ra+rb)/2,wc+(wother-wc)*i/8,z) for i in range(9)]
                pathcheck(pts,'upper_core_landing',b)
            steps=[]
            for k in range(ns):
                ra=front+going*k if outward else back-going*k;rb=ra+going if outward else ra-going
                z=zlow+(zhi-zlow)*(k+1)/ns
                tile(core,2,b,min(ra,rb),max(ra,rb),wc-.51,wc+.51,z)
                p=q(2,b,(ra+rb)/2,wc,z);steps.append(p);sample(p,'upper_core_steps',b)
            route(steps,'upper_core_steps')
            rstart=front-.5 if outward else back+.475;rend=back+.475 if outward else front-.5
            route([q(2,b,rstart,wc,zlow),steps[0]],'upper_core_entry_seam')
            route([steps[-1],q(2,b,rend,wc,zhi)],'upper_core_exit_seam')
            for ww in [wc-.55,wc+.55]:track(guard,[q(2,b,front if outward else back,ww,zlow),q(2,b,back if outward else front,ww,zhi)])
    # Front access landings below the upper band's rear landing.
    for z in levels[:-1]:tile(core,2,b,9.25,10.25,-1.2,1.2,z)
    core.finish();guard.finish()
    for band,row,z in [('bottom',0,levels[1]),('lower_middle',4,levels[2]),('upper_middle',15,levels[3])]:
        r0=-.15 if band=='bottom' else (row+.5)*1.1
        end=back+.475 if band=='upper_middle' else 10.05
        passage(2,b,r0+.15,end,z,z,'L3_'+band+'_%02d'%b)
        floor=Mesh('V20_上层洞口平台_'+band+'_%02d'%b,M['concrete']);tile(floor,2,b,r0-.08,r0+.17,-HALF,HALF,z);floor.finish()
data=json.loads((ROOT/'unity_enhanced/checks/v20_layout.json').read_text(encoding='utf-8'))
data['samples']=[s for s in data['samples'] if s['kind'].startswith('tier')]+samples
data['segments']=[s for s in data['segments'] if s['kind'].startswith('tier')]+segments
(ROOT/'unity_enhanced/checks/v20_layout.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/v20_portals.json').write_text(json.dumps({'portals':data['portals']},ensure_ascii=False),encoding='utf-8')
(ROOT/'unity_enhanced/checks/v20_core_dimensions.json').write_text(json.dumps(dimensions),encoding='utf-8')
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/v20_checks.json').write_text(json.dumps({'samples':data['samples'],'segments':data['segments']},ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Access cores regenerated',len(dimensions),'flights')
