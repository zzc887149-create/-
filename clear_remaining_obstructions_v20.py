import bpy,math,json,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={};M={'concrete':bpy.data.materials['concrete']}
tree=ast.parse((ROOT/'rebuild_seating_v20.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
audit=json.loads((ROOT/'unity_enhanced/checks/v20_audit_fast.json').read_text(encoding='utf-8'))
allowed=('环廊周圈护栏','环廊顶面管线','V20_上层洞口平台_bottom_','V20_层间前檐_')
for name in sorted({f['hit'] for f in audit['all_failures'] if (f['hit'] or '').startswith(allowed)}):
    ob=S.objects.get(name)
    if not ob:continue
    if ob.type=='CURVE':
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));new=bpy.data.objects.new(name+'_cut',me);new.matrix_world=ob.matrix_world.copy()
        for c in ob.users_collection:c.objects.link(new)
        bpy.data.objects.remove(ob,do_unlink=True);new.name=name;ob=new
    cutter=Mesh('V20_TEMP_clearance',M['concrete'])
    for f in audit['all_failures']:
        if f['hit']!=name:continue
        p=Vector(f['sample']['point']) if 'sample' in f else (Vector(f['segment']['a'])+Vector(f['segment']['b']))*.5-Vector((0,0,1.25))
        cutter.box(p+Vector((0,0,1.28)),(1.15,1.15,2.34))
    cut=cutter.finish();bpy.context.view_layer.update()
    mod=ob.modifiers.new('入口净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;mod.use_self=True
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me;bpy.data.objects.remove(cut,do_unlink=True)
    print(name,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
