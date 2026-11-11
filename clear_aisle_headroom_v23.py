"""Trim legacy concourse overhangs to the actual new stair routes."""
import bpy,math,ast,bisect,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
tree=ast.parse((ROOT/'rebuild_seating_v23.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
targets=[o for o in S.objects if o.type=='MESH' and o.name.startswith(('环形集散厅楼板_F4','环廊径向梁'))]
for b in range(N):
    cut=Mesh('V23_TEMP_梯道净空',bpy.data.materials['concrete'])
    for side in [-1,1]:
        for j in range(1):
            r0=.5*1.02-.105;r1=15.5*1.02+.105
            z0=H(1,0,b)-.2;z1=H(1,15,b)-.2
            wa,wb=sorted((side*1.42,side*2.84))
            pts=[q(1,b,r0,wa),q(1,b,r1,wa),q(1,b,r1,wb),q(1,b,r0,wb)]
            cut.prism(pts,[z0+2.35,z1+2.35,z1+2.35,z0+2.35],[z0,z1,z1,z0])
    cutter=cut.finish();bpy.context.view_layer.update()
    lo=[min(v[k] for v in cut.v) for k in range(3)];hi=[max(v[k] for v in cut.v) for k in range(3)]
    for ob in targets:
        pts=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        if not all(min(p[k] for p in pts)<=hi[k] and max(p[k] for p in pts)>=lo[k] for k in range(3)):continue
        mod=ob.modifiers.new('新梯道头顶净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;mod.use_self=True
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me
    bpy.data.objects.remove(cutter,do_unlink=True)
    (ROOT/'unity_enhanced/checks/v23_clearance_progress.txt').write_text(str(b+1)+'/24',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('24 middle-tier paired aisles cleared against legacy concourse slabs')


