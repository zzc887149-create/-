"""Close original top-landing seams and open the old grille at the extension."""
import bpy,math,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
tree=ast.parse((ROOT/'rebuild_seating_v23.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
for ob in list(S.objects):
    if ob.name.startswith('V23_原梯平台补缝_'):bpy.data.objects.remove(ob,do_unlink=True)
for b in range(12):
    a=b*math.tau/12+.11;o=Vector((126.5*math.cos(a),143.5*math.sin(a),0));r=Vector((math.cos(a),math.sin(a),0));t=Vector((-math.sin(a),math.cos(a),0))
    def pts(x0,x1,y0,y1):return [o+r*x+t*y for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
    deck=Mesh('V23_原梯平台补缝_%02d'%b,bpy.data.materials['concrete']);deck.prism(pts(-2.6,2.6,-5.25,-4.4),22.5,22.25);deck.finish()
    if b in [3,9]:
        shell=S.objects['红色看台背壳_V23_连续底壳']
        cut=Mesh('V23_TMP_shell_landing',bpy.data.materials['concrete']);cut.prism(pts(-2.65,-1.0,-5.3,-3.3),24.7,22.48);cutter=cut.finish();bpy.context.view_layer.update()
        mod=shell.modifiers.new('旧平台净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;mod.use_self=True
        dg=bpy.context.evaluated_depsgraph_get();shell.data=bpy.data.meshes.new_from_object(shell.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);shell.modifiers.clear();bpy.data.objects.remove(cutter,do_unlink=True)
    for prefix in ['楼梯平台红色格栅_','楼梯平台扶手_']:
        grille=S.objects.get(prefix+'%02d'%b)
        if not grille:continue
        cut=Mesh('V23_TMP_grille',bpy.data.materials['concrete']);cut.prism(pts(2.4,5.5,-4.7,-3.3),25.0,22.45);cutter=cut.finish();bpy.context.view_layer.update()
        mod=grille.modifiers.new('续接出口净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        dg=bpy.context.evaluated_depsgraph_get();grille.data=bpy.data.meshes.new_from_object(grille.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);grille.modifiers.clear();bpy.data.objects.remove(cutter,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
