import bpy,bmesh,json,shutil,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
PACKAGE=ROOT/'unity_delivery/Assets/ZhaoLeiBirdsNest'
(PACKAGE/'Models').mkdir(parents=True,exist_ok=True);(PACKAGE/'Textures').mkdir(exist_ok=True)
source=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
dest=bpy.data.scenes.new('UNITY_EXPORT_FULL_GEOMETRY');dest.unit_settings.system='METRIC';dest.unit_settings.scale_length=1
root=bpy.data.objects.new('BirdsNest_Full_360',None);dest.collection.objects.link(root)
groups={};matmap={};manifest=[];report=[]
for coll in source.collection.children:
 if coll.name.startswith(('10_','11_','12_')):continue
 group=bpy.data.objects.new('G'+coll.name,None);dest.collection.objects.link(group);group.parent=root;groups[coll.name]=group
def exportmat(m):
 if m.name in matmap:return matmap[m.name]
 name='BN_%03d'%len(matmap);new=m.copy();new.name=name
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 base=list(bs.inputs['Base Color'].default_value) if bs else list(m.diffuse_color)
 entry={'name':name,'label':m.name,'baseColor':base,'metallic':float(bs.inputs['Metallic'].default_value) if bs else 0,'roughness':float(bs.inputs['Roughness'].default_value) if bs else .6,'emission':list(bs.inputs['Emission Color'].default_value) if bs else [0,0,0,1],'strength':float(bs.inputs['Emission Strength'].default_value) if bs else 0,'texture':''}
 if m.use_nodes:
  node=next((n for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None)
  if node:
   image=node.image;filename=name+'.png';entry['texture']=filename
   # Save from packed image pixels, no absolute texture dependency in delivery.
   image.save_render(str(PACKAGE/'Textures'/filename),scene=source)
   entry['baseColor']=[1,1,1,1];entry['emission']=[1,1,1,1]
 matmap[m.name]=new;manifest.append(entry);return new
boundaries={};verts=faces=0
for o in list(source.objects):
 if o.name=='灯束薄雾范围':continue
 if o.type=='EMPTY' and o.name.startswith(('VIEW_','LOOK_')):
  n=o.copy();dest.collection.objects.link(n);n.parent=groups['16_全场观察点'];n.matrix_world=o.matrix_world.copy();continue
 if o.type not in {'MESH','CURVE','FONT'}:continue
 col=next((c for c in o.users_collection if c.name in groups),None)
 if not col:continue
 evaluated=o.evaluated_get(dg)
 data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
 bm=bmesh.new();bm.from_mesh(data)
 # Correct each disconnected solid too; recalculation is local to each component.
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 boundary=sum(e.is_boundary for e in bm.edges)
 if boundary:boundaries[o.name]=boundary
 bm.to_mesh(data);bm.free()
 originals=list(data.materials);data.materials.clear()
 for m in originals:
  if m:data.materials.append(exportmat(m))
 n=bpy.data.objects.new(o.name,data);dest.collection.objects.link(n);n.parent=groups[col.name];n.matrix_world=o.matrix_world.copy()
 verts+=len(data.vertices);faces+=len(data.polygons)
 report.append({'name':o.name,'vertices':len(data.vertices),'polygons':len(data.polygons),'boundary_edges':boundary})
source_name=source.name
bpy.context.window.scene=dest
for o in dest.objects:o.select_set(True)
fbx=PACKAGE/'Models/BirdsNest_Full.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=False,use_visible=False,object_types={'MESH','EMPTY'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP',embed_textures=False,add_leaf_bones=False)
(PACKAGE/'materials.json').write_text(json.dumps({'materials':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
required=['PTFE马鞍形屋面','三层看台_层1','三层看台_层2','三层看台_层3','LED_中央弧形_可替换贴图','内场保护地板']
audit={'source_scene':source_name,'mesh_objects':len(report),'vertices':verts,'polygons':faces,'boundary_edges_on_required_surfaces':{n:boundaries.get(n,0) for n in required},'excluded':['volume fog cube','Blender cameras and lights','reference images'],'fbx_bytes':fbx.stat().st_size,'sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'all_meshes':report}
(ROOT/'unity_delivery/export_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_全场_Unity.blend'))
bpy.context.window.scene=source
# Both editable source and game-export scene are preserved in the new blend.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_全场_Unity.blend'))
print(json.dumps({k:v for k,v in audit.items() if k!='all_meshes'},ensure_ascii=False))
