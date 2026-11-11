import bpy,bmesh,math,json
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');PKG=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
S=bpy.context.scene;assert S.get('band_v5')
previous=bpy.data.scenes.get('UNITY_BAND_V5')
if previous:
    for ob in list(previous.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(previous)
C=next(c for c in S.collection.children if c.name.startswith('20_'))
records=json.loads((PKG/'materials.json').read_text(encoding='utf-8'))['materials'];names={r['label']:r['name'] for r in records}
D=bpy.data.scenes.new('UNITY_BAND_V5');D.unit_settings.scale_length=1
root=bpy.data.objects.new('BirdsNest_Band_V5',None);D.collection.objects.link(root)
buckets={};newmats={};dg=bpy.context.evaluated_depsgraph_get()
for ob in C.objects:
    if ob.type=='EMPTY':
        n=ob.copy();D.collection.objects.link(n);n.parent=root;continue
    data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    if not ob.name.endswith(('_液晶屏','_观众侧背板','_星海荧光棒群','_看台暗场坡面')):
        bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    coords=[ob.matrix_world@v.co for v in data.vertices];uv=data.uv_layers.active
    for p in data.polygons:
        mat=data.materials[p.material_index];mn=names.get(mat.name,mat.name)
        if mn.startswith('BN5_') and mn not in newmats:
            bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            newmats[mn]={'name':mn,'baseColor':list(bs.inputs['Base Color'].default_value),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value)}
        zone=math.floor(ob.location.x/8) if ob.location.length>0 else math.floor(sum(coords[i].x for i in p.vertices)/len(p.vertices)/8)
        key=(zone,mn);b=buckets.setdefault(key,{'v':[],'f':[],'uv':[],'smooth':[],'mat':mat,'map':{}});face=[];puv=[]
        for li in p.loop_indices:
            vi=data.loops[li].vertex_index;k=(ob.name,vi)
            if k not in b['map']:b['map'][k]=len(b['v']);b['v'].append(tuple(coords[vi]))
            face.append(b['map'][k]);puv.append(tuple(uv.data[li].uv) if uv else (0,0))
        b['f'].append(face);b['uv'].append(puv);b['smooth'].append(p.use_smooth)
    bpy.data.meshes.remove(data)
tri=0
for (zone,mn),b in buckets.items():
    name='Band_%02d_%s'%(zone,mn);me=bpy.data.meshes.new(name);me.from_pydata(b['v'],[],b['f']);me.materials.append(bpy.data.materials.get(mn) or b['mat']);me.update();uv=me.uv_layers.new(name='UVMap')
    for p,puv,sm in zip(me.polygons,b['uv'],b['smooth']):
        p.use_smooth=sm
        for li,v in zip(p.loop_indices,puv):uv.data[li].uv=v
    ob=bpy.data.objects.new(name,me);D.collection.objects.link(ob);ob.parent=root;tri+=sum(len(p.vertices)-2 for p in me.polygons)
bpy.context.window.scene=D
bpy.ops.export_scene.fbx(filepath=str(PKG/'Models/BirdsNest_Band.fbx'),use_selection=False,object_types={'MESH','EMPTY'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP')
bpy.context.window.scene=S
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend'))
(PKG/'band_materials.json').write_text(json.dumps({'materials':list(newmats.values())},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'unity_enhanced/band_geometry.json').write_text(json.dumps({'added_triangles':tri,'added_chunks':len(buckets),'additional_views':1,'source_objects':len(C.objects)},indent=2),encoding='utf-8')
print('Band export:',tri,'triangles;',len(buckets),'chunks')
