"""Spatially partition and merge evaluated geometry, then create real reduced LOD meshes."""
import bpy,bmesh,math,json,shutil,time,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
OUT=ROOT/'unity_enhanced';PKG=OUT/'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
for name in ['Models','Textures','Scripts','Editor','Shaders']:(PKG/name).mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;assert S.get('enhanced_v3')
assert not bpy.data.scenes.get('UNITY_ENHANCED_V3'),'Export scene already exists'
D=bpy.data.scenes.new('UNITY_ENHANCED_V3');D.unit_settings.system='METRIC';D.unit_settings.scale_length=1
root=bpy.data.objects.new('BirdsNest_Enhanced_360',None);D.collection.objects.link(root)
dg=bpy.context.evaluated_depsgraph_get();materials={};manifest=[];buckets={};counts={};started=time.time()
def register(m,vertex=False):
 key='VERTEX_PALETTE' if vertex else m.name
 if key in materials:return materials[key]
 name='BNE_%03d'%len(materials)
 n=m.copy();n.name=name;materials[key]=n
 bs=next((x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 entry={'name':name,'label':key,'baseColor':list(bs.inputs['Base Color'].default_value) if bs else list(m.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value) if bs else .7,'metallic':float(bs.inputs['Metallic'].default_value) if bs else 0,'emission':list(bs.inputs['Emission Color'].default_value) if bs else [0,0,0,1],'strength':float(bs.inputs['Emission Strength'].default_value) if bs else 0,'texture':'','normal':'','vertexColor':vertex}
 if vertex:entry.update(baseColor=[1,1,1,1],roughness=.8,metallic=0,emission=[0,0,0,1],strength=0)
 elif bs:
  for socket,field in [('Base Color','texture'),('Normal','normal')]:
   links=bs.inputs[socket].links
   node=links[0].from_node if links else None
   if node and node.type=='NORMAL_MAP':node=node.inputs['Color'].links[0].from_node
   if node and node.type=='TEX_IMAGE' and node.image:
    img=node.image;src=Path(bpy.path.abspath(img.filepath));fn=name+'_'+field+src.suffix
    if src.is_file():shutil.copy2(src,PKG/'Textures'/fn)
    else:fn=name+'_'+field+'.png';img.save_render(str(PKG/'Textures'/fn),scene=S)
    entry[field]=fn
    if field=='texture':entry['baseColor']=[1,1,1,1]
  if entry['texture'] and entry['strength']>0:entry['emission']=[1,1,1,1]
 manifest.append(entry);return n
def region(p,detail=False):
 x,y,z=p
 if detail:
  if (x/75)**2+(y/106)**2<1.04 and z<6:return 'F_%d_%d'%(math.floor((x+80)/32),math.floor((y+115)/32))
  a=(math.atan2(y/155,x/135)+math.tau)%math.tau
  return 'B_%02d_%d'%(int(a/math.tau*20)%20,int(z/18))
 a=(math.atan2(y/155,x/135)+math.tau)%math.tau
 return 'A_%02d'%int(a/math.tau*16)
def bucket(key,mat,cat):
 if key not in buckets:buckets[key]={'v':[],'f':[],'uv':[],'color':[],'smooth':[],'mat':mat,'cat':cat,'map':{}}
 return buckets[key]
for oi,o in enumerate(list(S.objects)):
 if o.type=='EMPTY' and o.name.startswith(('VIEW_','LOOK_')):
  n=o.copy();n.name=o.name+'_V3';D.collection.objects.link(n);n.parent=root;n.matrix_world=o.matrix_world.copy();continue
 col=next((c.name[:2] for c in o.users_collection if c.name[:2] not in ['10','11','12','16']),None)
 if not col or o.type not in ['MESH','CURVE','FONT'] or o.name=='灯束薄雾范围':continue
 ev=o.evaluated_get(dg);data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
 if not data or not len(data.polygons):continue
 # Recalculate on complete solids before partitioning, preserving inward/outward consistency.
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 mw=o.matrix_world;coords=[tuple(mw@v.co) for v in data.vertices];uv=data.uv_layers.active
 isseat=o.name.startswith('看台座椅_')
 iscrowd=col=='07' and o.name!='全场手机星光'
 isfield=o.name.startswith('内场折叠椅_')
 isnear=o.name.startswith('NEAR_')
 cat='CROWD' if iscrowd or isnear else 'SEATS' if isseat else 'CHAIRS' if isfield else 'ARCH'
 detail=cat!='ARCH';vertex=iscrowd or isseat or isnear
 stride=32 if isnear else 6 if o.name=='观众头部_远景' else 8 if detail else 0
 if o.name=='全场手机星光':cat='PHONES'
 comp_regions={}
 mats=list(data.materials)
 for p in data.polygons:
  oldmat=mats[p.material_index] if p.material_index<len(mats) else mats[0] if mats else bpy.data.materials['concrete']
  mat=register(oldmat,vertex)
  if stride:
   comp=p.vertices[0]//stride
   if comp not in comp_regions:
    pts=coords[comp*stride:comp*stride+stride];centre=tuple(sum(v[k] for v in pts)/len(pts) for k in range(3));comp_regions[comp]=region(centre,True)
   reg=comp_regions[comp]
  else:
   centre=tuple(sum(coords[v][k] for v in p.vertices)/len(p.vertices) for k in range(3));reg=region(centre,cat=='PHONES')
  # Keep photographed LED panels separate so materials stay individually addressable.
  group='LED' if col=='04' else cat
  key=(group,reg,mat.name)
  b=bucket(key,mat,group);face=[];puv=[]
  color=tuple(oldmat.diffuse_color) if vertex else (1,1,1,1)
  for li in p.loop_indices:
   vi=data.loops[li].vertex_index;vkey=(oi,vi)
   if vkey not in b['map']:
    b['map'][vkey]=len(b['v']);b['v'].append(coords[vi]);b['color'].append(color)
   face.append(b['map'][vkey]);puv.append(tuple(uv.data[li].uv) if uv else (0,0))
  b['f'].append(face);b['uv'].append(puv);b['smooth'].append(p.use_smooth)
 bpy.data.meshes.remove(data)
 if oi%300==0:(OUT/'export_progress.txt').write_text('Partitioned source object '+str(oi),encoding='utf-8')
report=[]
bpy.context.window.scene=D
for index,(key,b) in enumerate(buckets.items()):
 name='Chunk_%s_%s_%s'%(key[0],key[1],key[2]);me=bpy.data.meshes.new(name);me.from_pydata(b['v'],[],b['f']);me.materials.append(b['mat']);me.update()
 uv=me.uv_layers.new(name='UVMap')
 for p,puv,sm in zip(me.polygons,b['uv'],b['smooth']):
  p.use_smooth=sm
  for li,t in zip(p.loop_indices,puv):uv.data[li].uv=t
 if key[2]==materials.get('VERTEX_PALETTE',object()).name if 'VERTEX_PALETTE' in materials else False:
  vc=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
  for v,c in zip(vc.data,b['color']):v.color=c
 o=bpy.data.objects.new(name+'_L0',me);D.collection.objects.link(o);o.parent=root
 hi=sum(len(p.vertices)-2 for p in me.polygons);lo=hi
 if b['cat'] in ['CROWD','SEATS','CHAIRS'] and hi>300:
  group=bpy.data.objects.new('LOD_'+name,None);D.collection.objects.link(group);group.parent=root;o.parent=group
  low=o.copy();low.data=me.copy();low.name=name+'_L1';D.collection.objects.link(low);low.parent=group
  mod=low.modifiers.new('Far mesh simplification','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=.26;mod.use_collapse_triangulate=True
  dg2=bpy.context.evaluated_depsgraph_get();lowdata=bpy.data.meshes.new_from_object(low.evaluated_get(dg2),preserve_all_data_layers=True,depsgraph=dg2)
  low.modifiers.clear();old=low.data;low.data=lowdata;bpy.data.meshes.remove(old)
  lo=sum(len(p.vertices)-2 for p in lowdata.polygons)
 report.append({'chunk':name,'category':b['cat'],'near_triangles':hi,'far_triangles':lo})
 if index%20==0:(OUT/'export_progress.txt').write_text('Created LOD chunk %d / %d'%(index,len(buckets)),encoding='utf-8')
 # Free Python construction buffers progressively.
 b.clear()
f=PKG/'Models/BirdsNest_Enhanced.fbx'
bpy.ops.export_scene.fbx(filepath=str(f),use_selection=False,use_visible=False,object_types={'MESH','EMPTY'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',colors_type='LINEAR',bake_anim=False,path_mode='STRIP',embed_textures=False,add_leaf_bones=False)
(PKG/'materials.json').write_text(json.dumps({'materials':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
summary={'chunks':len(report),'LOD_groups':sum(x['far_triangles']!=x['near_triangles'] for x in report),'near_triangles':sum(x['near_triangles'] for x in report),'far_triangles':sum(x['far_triangles'] for x in report),'export_seconds':round(time.time()-started,1),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'details':report}
(OUT/'optimization_geometry.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.context.window.scene=S
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_精修日夜版.blend'))
(OUT/'export_progress.txt').write_text('COMPLETE',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='details'},ensure_ascii=False))
