"""Repair reversed upper tunnels and local route obstructions; preserve all audit samples."""
import bpy,math,json,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
M={n:bpy.data.materials[n] for n in ('concrete','栏杆细金属')}
tree=ast.parse((ROOT/'rebuild_seating_v20.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
samples=[];segments=[];cuts=[]
for b in range(N):
    tag='L3_upper_middle_%02d'%b
    for prefix in ('V20_通道_','V20_围护_'):
        ob=S.objects.get(prefix+tag)
        if ob:bpy.data.objects.remove(ob,do_unlink=True)
    z=H(2,15,b);passage(2,b,17.2,10.05,z,z,tag)
data=json.loads((ROOT/'unity_enhanced/checks/v20_layout.json').read_text(encoding='utf-8'))
data['samples']=[s for s in data['samples'] if not s['kind'].startswith('L3_upper_middle_')]+samples
data['segments']=[s for s in data['segments'] if not s['kind'].startswith('L3_upper_middle_')]+segments
audit=json.loads((ROOT/'unity_enhanced/checks/v20_audit_fast.json').read_text(encoding='utf-8'))
# Raised services can retain their complete circular runs above the walking envelope.
for name in ('环廊顶面管线_F3','环廊顶面管线_F3.001'):
    ob=S.objects.get(name)
    if ob and not ob.get('v20_raised'):ob.location.z+=1.1;ob['v20_raised']=True
for name in sorted({f['hit'] for f in audit['all_failures'] if (f['hit'] or '').startswith('环廊混凝土柱')}):
    ob=S.objects.get(name)
    if ob and not ob.get('v20_route_shifted'):
        p=ob.matrix_world.translation;ob.location+=Vector((-p.y,p.x,0)).normalized()*3.2;ob['v20_route_shifted']=True
# Cut only obstruction objects identified by audit, with contiguous walking envelopes.
targets={f['hit'] for f in audit['all_failures'] if f['hit'] and not f['hit'].startswith(('环廊顶面管线','环廊混凝土柱'))}
for name in targets:
    ob=S.objects.get(name)
    if not ob or ob.type!='MESH':continue
    cutter=Mesh('V20_TEMP_local_clearance',M['concrete'])
    failures=[f for f in audit['all_failures'] if f['hit']==name]
    for f in failures:
        if 'sample' in f:
            p=Vector(f['sample']['point'])
        else:
            p=(Vector(f['segment']['a'])+Vector(f['segment']['b']))*.5-Vector((0,0,1.25))
        cutter.box(p+Vector((0,0,1.28)),(1.05,1.05,2.34))
    cut=cutter.finish();bpy.context.view_layer.update()
    mod=ob.modifiers.new('通道局部净空修复','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;mod.use_self=True
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me
    bpy.data.objects.remove(cut,do_unlink=True)
    print('Cleared',name,flush=True)
(ROOT/'unity_enhanced/checks/v20_layout.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/v20_checks.json').write_text(json.dumps({'samples':data['samples'],'segments':data['segments']},ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
