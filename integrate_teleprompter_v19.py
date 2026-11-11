"""Remove photographic stand proxies; mount the LED cabinet to existing roof steel."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('20_'))
prefix='后方看台提词器_'
keep={prefix+'主箱体',prefix+'主液晶屏'}
removed=[]
for o in list(C.objects):
    if o.name.startswith(prefix) and o.name not in keep:
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Reuse only geometry helpers, never the old destructive stage setup.
src=(ROOT/'add_teleprompter_v17.py').read_text(encoding='utf-8')
import ast, math
from mathutils import Matrix
tree=ast.parse(src)
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('add_mesh','add_box_xform'):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
mat=bpy.data.materials['BN5_提词器背板']
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.025,.028,.032,1)
bs.inputs['Roughness'].default_value=.82
bs.inputs['Metallic'].default_value=.35
mat.diffuse_color=(.025,.028,.032,1)
def beam(name,a,b,width=.12):
    a,b=Vector(a),Vector(b);d=b-a
    return add_box_xform(prefix+name,(a+b)/2,(d.length,width,width),mat,
        rot_y=-math.atan2(d.z,math.hypot(d.x,d.y)),rot_z=math.atan2(d.y,d.x))
# Back rails sit entirely above circulation; no invented wall under the display.
for z in (22.1,28.9,35.7):
    beam('背横梁_'+str(z),(-15.4,-127.65,z),(15.4,-127.65,z),.18)
for x in (-15.4,-10,-5,0,5,10,15.4):
    beam('背竖梁_'+str(x),(x,-127.65,22.1),(x,-127.65,35.7),.14)
for i in range(6):
    x=-15+i*5
    beam('背斜撑_'+str(i),(x,-127.68,22.1),(x+5,-127.68,35.7),.075)
# Surface-matched attachment points on actual structural roof beams, not membrane.
verts=[];faces=[]
for o in S.objects:
    if o.type!='MESH' or not o.name.startswith(('屋面主梁','主桁架','屋面次梁','屋面边环','屋面交织带')):continue
    offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
assert verts,'Roof steel unavailable'
bvh=BVHTree.FromPolygons(verts,faces)
anchors=[]
for i,x in enumerate((-12.0,-4.0,4.0,12.0)):
    p=Vector((x,-127.65,35.7));q,n,idx,dist=bvh.find_nearest(p)
    assert q is not None and dist<8,(x,dist)
    beam('屋架连接_'+str(i),p,q,.16)
    add_box_xform(prefix+'连接板_'+str(i),q,(.36,.36,.18),mat)
    anchors.append({'from':list(p),'to':list(q),'length':dist})
# Keep existing lyric texture; soften excessive white emission.
screen=bpy.data.materials['BN5_提词器屏幕']
next(n for n in screen.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Emission Strength'].default_value=1.05
target=ROOT/'赵雷2026_鸟巢_提词器环境融合版.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
exec((ROOT/'export_band_v5.py').read_text(encoding='utf-8').replace("str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend')","bpy.data.filepath"))
path=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/band_materials.json'
data=json.loads(path.read_text(encoding='utf-8'))
for m in data['materials']:
    if m['name']=='BN5_提词器屏幕':m.update(texture='BN5_提词器屏幕_texture.png',emission=1.05)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
S['teleprompter_v19']=True
(ROOT/'unity_enhanced/checks/v19_teleprompter.json').write_text(json.dumps({'removed':removed,'roof_anchors':anchors,'note':'Roof attachment reconstructed, not measured from photos.'},ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print('Integrated screen; removed',len(removed),'stand proxies; anchors',anchors)
