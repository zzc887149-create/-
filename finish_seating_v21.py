import bpy,bmesh,math,json,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
# Remove residual old lower-tier crowd, without touching the new bowl or inner-field spectators.
for scene in (S,D):
    for o in list(scene.objects):
        if o.type!='MESH' or 'V21' in o.name:continue
        isdetail=(scene==S and (any(c.name.startswith('07_') for c in o.users_collection) or o.name.startswith('NEAR_'))) or (scene==D and o.name.startswith(('Chunk_CROWD_','Chunk_PHONES_')))
        if not isdetail:continue
        bm=bmesh.new();bm.from_mesh(o.data)
        drop=[v for v in bm.verts if ((o.matrix_world@v.co).x/75)**2+((o.matrix_world@v.co).y/106)**2>1]
        bmesh.ops.delete(bm,geom=drop,context='VERTS');bm.to_mesh(o.data);bm.free()
        if scene==D and not len(o.data.polygons):bpy.data.objects.remove(o,do_unlink=True)
for o in list(D.objects):
    if o.name.startswith('LOD_') and not o.children:bpy.data.objects.remove(o,do_unlink=True)
# Vertex palette preview in Blender matches Unity's vertex-color shader.
mat=bpy.data.materials['BNE_006'];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
vc=next((n for n in mat.node_tree.nodes if n.type=='VERTEX_COLOR'),None) or mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
# Restore closed red shells with ONLY the approved new route openings.
COL={c.name[:2]:c for c in S.collection.children}
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
src=ast.parse((ROOT/'refine_exterior_shell_v13.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='shell2_profile'],type_ignores=[]),'profile','exec'))
data=json.loads((ROOT/'unity_enhanced/checks/v21_cutters.json').read_text(encoding='utf-8'))
me=bpy.data.meshes.new('V21_all_routes');me.from_pydata(data['v'],[],data['f']);me.update()
lowercut=bpy.data.objects.new('V21_all_routes',me);S.collection.objects.link(lowercut);bpy.context.view_layer.update()
def applycut(ob,cutter):
    m=ob.modifiers.new('草图C入口','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    dg=bpy.context.evaluated_depsgraph_get();ob.data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear()
for ob in list(S.objects):
    if ob.name.startswith('红色看台背壳_'):bpy.data.objects.remove(ob,do_unlink=True)
src=(ROOT/'rebuild_bowl_envelope_v15.py').read_text(encoding='utf-8')
src=src[src.index('N=768;M=20;'):src.index('for ob in [lowercut,uppercut]')]
src=src.replace('applycut(ob,lowercut);applycut(ob,uppercut)','applycut(ob,lowercut)')
exec(src)
bpy.data.objects.remove(lowercut,do_unlink=True)
# Update close-up views to the approved new entrances.
layout=json.loads((ROOT/'unity_enhanced/checks/v21_layout.json').read_text(encoding='utf-8'))
for idx,tier,band in [(14,1,'rear'),(15,2,'middle'),(16,3,'lower_middle')]:
    p=next(p for p in layout['portals'] if p['tier']==tier and p['band']==band and p['bay']==0)
    e=Vector(p['point']);rad=Vector((e.x,e.y,0)).normalized();tan=Vector((-rad.y,rad.x,0))
    for prefix,loc in [('VIEW_',e-rad*9+tan*7+Vector((0,0,4))),('LOOK_',e+Vector((0,0,1)))]:
        for scene in (S,D):
            for o in scene.objects:
                if o.name.startswith(prefix+str(idx)+'_'):o.location=loc
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Closed shells regenerated; field detail preserved; entrance views updated')
