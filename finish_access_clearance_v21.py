"""Local intersections resolved without cutting roof steel or deleting route tests."""
import bpy,math,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
tree=ast.parse((ROOT/'rebuild_seating_v21.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
def subtract(ob,cut):
    cutter=cut.finish();bpy.context.view_layer.update()
    mod=ob.modifiers.new('入口真实净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;mod.use_self=True
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me
    bpy.data.objects.remove(cutter,do_unlink=True)
cut=Mesh('V21_TEMP_后台梯道',bpy.data.materials['concrete'])
tile(cut,0,8,-.15,3.7,-2.9,2.9,4.5,3.5)
subtract(S.objects['后台通行地台'],cut)
cut=Mesh('V21_TEMP_二层后沿净空',bpy.data.materials['concrete'])
for b in range(N):
    for side in [-1,1]:
        wa,wb=sorted([side*1.4,side*2.9])
        tile(cut,1,b,13.8,16.5,wa,wb,28.0,3.5)
subtract(S.objects['V21_层间前檐_3'],cut)
# Move the six schematic columns beside the passage instead of removing their structure.
for n in [16,18,20,40,42,44]:
    ob=S.objects['环廊混凝土柱.%03d'%n]
    if ob.get('v21_relocated'):continue
    p=ob.matrix_world.translation;tan=Vector((-p.y,p.x,0)).normalized()
    ob.location+=tan*3.1;ob['v21_relocated']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
