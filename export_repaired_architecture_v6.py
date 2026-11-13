"""Rebuild only architecture chunks, preserving all existing crowd/seat LOD meshes."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');OUT=ROOT/'unity_enhanced';PKG=OUT/'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
S=bpy.context.scene;assert S.get('stairs_connected_v6')
D=bpy.data.scenes['UNITY_ENHANCED_V3'];root=D.objects['BirdsNest_Enhanced_360']
records=json.loads((PKG/'materials.json').read_text(encoding='utf-8'))['materials'];mnames={r['label']:r['name'] for r in records}
dg=bpy.context.evaluated_depsgraph_get();buckets={}
for ob in list(S.objects):
 col=next((c.name[:2] for c in ob.users_collection),None)
 if col in ['04','07','10','11','12','16','19','20'] or ob.type not in {'MESH','CURVE','FONT'} or ob.name=='灯束薄雾范围' or ob.name.startswith(('看台座椅_','内场折叠椅_','NEAR_')):continue
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 if not me:continue
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 coords=[ob.matrix_world@v.co for v in me.vertices];uv=me.uv_layers.active
 for poly in me.polygons:
  mat=me.materials[poly.material_index] if len(me.materials) else bpy.data.materials['concrete'];mn=mnames[mat.name]
  p=sum((coords[i] for i in poly.vertices),Vector())/len(poly.vertices);sector=int(((math.atan2(p.y/155,p.x/135)+math.tau)%math.tau)/math.tau*16)
  name='Chunk_ARCH_A_%02d_%s_L0'%(sector,mn);b=buckets.setdefault(name,{'v':[],'f':[],'uv':[],'smooth':[],'map':{},'mat':mn})
  face=[];puv=[]
  for li in poly.loop_indices:
   vi=me.loops[li].vertex_index;key=(ob.name,vi)
   if key not in b['map']:b['map'][key]=len(b['v']);b['v'].append(tuple(coords[vi]))
   face.append(b['map'][key]);puv.append(tuple(uv.data[li].uv) if uv else (0,0))
  b['f'].append(face);b['uv'].append(puv);b['smooth'].append(poly.use_smooth)
 bpy.data.meshes.remove(me)
for ob in list(D.objects):
 if ob.name.startswith('Chunk_ARCH_') and ob.name not in buckets:bpy.data.objects.remove(ob,do_unlink=True)
newreports=[]
for name,b in buckets.items():
 me=bpy.data.meshes.new(name+'_v6');me.from_pydata(b['v'],[],b['f']);me.materials.append(bpy.data.materials[b['mat']]);me.update();uv=me.uv_layers.new(name='UVMap')
 for face,puv,smooth in zip(me.polygons,b['uv'],b['smooth']):
  face.use_smooth=smooth
  for li,p in zip(face.loop_indices,puv):uv.data[li].uv=p
 ob=D.objects.get(name)
 if ob:ob.data=me
 else:ob=bpy.data.objects.new(name,me);D.collection.objects.link(ob);ob.parent=root
 tri=sum(len(p.vertices)-2 for p in me.polygons);newreports.append({'chunk':name[:-3],'category':'ARCH','near_triangles':tri,'far_triangles':tri})
 b.clear()
bpy.context.window.scene=D
f=PKG/'Models/BirdsNest_Enhanced.fbx'
# Export outside Assets, then replace: do not truncate a model still mapped by
# another process, or let Unity import a partially written FBX.
pending=OUT/'BirdsNest_Enhanced_export.fbx'
bpy.ops.export_scene.fbx(filepath=str(pending),use_selection=False,use_visible=False,object_types={'MESH','EMPTY'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',colors_type='LINEAR',bake_anim=False,path_mode='STRIP',embed_textures=False,add_leaf_bones=False)
pending.replace(f)
bpy.context.window.scene=S
p=OUT/'optimization_geometry.json';report=json.loads(p.read_text(encoding='utf-8'));report['details']=[r for r in report['details'] if r['category']!='ARCH']+newreports
report.update(chunks=len(report['details']),near_triangles=sum(r['near_triangles'] for r in report['details']),far_triangles=sum(r['far_triangles'] for r in report['details']),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False))
