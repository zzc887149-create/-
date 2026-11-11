import bpy,bmesh,math,json
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');PKG=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
S=bpy.context.scene;assert S.get('detail_v4')
previous=bpy.data.scenes.get('UNITY_DETAIL_V4')
if previous:
    for ob in list(previous.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(previous)
C=next(c for c in S.collection.children if c.name.startswith('19_'))
records=json.loads((PKG/'materials.json').read_text(encoding='utf-8'))['materials'];names={r['label']:r['name'] for r in records}
D=bpy.data.scenes.new('UNITY_DETAIL_V4');D.unit_settings.scale_length=1
root=bpy.data.objects.new('BirdsNest_Detail_V4',None);D.collection.objects.link(root)
buckets={};dg=bpy.context.evaluated_depsgraph_get()
for ob in C.objects:
    if ob.type=='EMPTY':
        n=ob.copy();D.collection.objects.link(n);n.parent=root;continue
    data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    coords=[ob.matrix_world@v.co for v in data.vertices];uv=data.uv_layers.active
    for p in data.polygons:
        mat=data.materials[p.material_index];mn=names.get(mat.name,mat.name)
        ctr=sum((coords[i] for i in p.vertices),start=coords[p.vertices[0]]*0)/len(p.vertices)
        sector=int(((math.atan2(ctr.y/150,ctr.x/133)+math.tau)%math.tau)/math.tau*12)
        key=(sector,mn);b=buckets.setdefault(key,{'v':[],'f':[],'uv':[],'mat':mat,'map':{}});face=[];puv=[]
        for li in p.loop_indices:
            vi=data.loops[li].vertex_index;k=(ob.name,vi)
            if k not in b['map']:b['map'][k]=len(b['v']);b['v'].append(tuple(coords[vi]))
            face.append(b['map'][k]);puv.append(tuple(uv.data[li].uv) if uv else (0,0))
        b['f'].append(face);b['uv'].append(puv)
    bpy.data.meshes.remove(data)
tri=0
for (sector,mn),b in buckets.items():
    name='Detail_%02d_%s'%(sector,mn);me=bpy.data.meshes.new(name);me.from_pydata(b['v'],[],b['f']);me.materials.append(bpy.data.materials.get(mn) or b['mat']);me.update();uv=me.uv_layers.new(name='UVMap')
    for p,puv in zip(me.polygons,b['uv']):
        for li,v in zip(p.loop_indices,puv):uv.data[li].uv=v
    ob=bpy.data.objects.new(name,me);D.collection.objects.link(ob);ob.parent=root;tri+=sum(len(p.vertices)-2 for p in me.polygons)
bpy.context.window.scene=D
bpy.ops.export_scene.fbx(filepath=str(PKG/'Models/BirdsNest_Details.fbx'),use_selection=False,object_types={'MESH','EMPTY'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP')
bpy.context.window.scene=S
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
(ROOT/'unity_enhanced/detail_geometry.json').write_text(json.dumps({'added_triangles':tri,'added_chunks':len(buckets),'additional_views':sum(o.name.startswith('VIEW_') for o in D.objects)},indent=2),encoding='utf-8')
print('Detail export:',tri,'triangles;',len(buckets),'chunks')
