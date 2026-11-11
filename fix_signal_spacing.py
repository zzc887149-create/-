"""Equal visible edge gaps for SIGNAL; update the existing Unity export meshes."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
OUT=ROOT/'unity_enhanced'
PKG=OUT/'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
S=bpy.context.scene
letters=[bpy.data.objects['NO SIGNAL_'+str(i)] for i in range(3,9)]
assert ''.join(o.data.body for o in letters)=='SIGNAL'
def span(o):
    points=[o.matrix_world@Vector(v) for v in o.bound_box]
    return min(p.x for p in points),max(p.x for p in points)
before=[span(o) for o in letters]
widths=[b-a for a,b in before]
gap=(before[-1][1]-before[0][0]-sum(widths))/5
records=json.loads((PKG/'materials.json').read_text(encoding='utf-8'))['materials']
matids={r['label']:r['name'] for r in records}
D=bpy.data.scenes['UNITY_ENHANCED_V3']
cursor=before[0][0]
changes=[]
for o,(left,right),width in zip(letters,before,widths):
    desired=cursor
    o.location.x+=desired-left
    mid=matids[o.data.materials[0].name]
    chunks=[c for c in D.objects if c.type=='MESH' and any(m.name==mid for m in c.data.materials)]
    assert len(chunks)==1,(o.name,len(chunks))
    c=chunks[0]
    oldleft=min((c.matrix_world@v.co).x for v in c.data.vertices)
    local_delta=c.matrix_world.inverted().to_3x3()@Vector((desired-oldleft,0,0))
    for v in c.data.vertices:v.co+=local_delta
    c.data.update()
    changes.append({'letter':o.data.body,'object':o.name,'shift':desired-left,'left':desired,'right':desired+width})
    cursor+=width+gap
bpy.context.view_layer.update()
after=[span(o) for o in letters]
gaps=[after[i+1][0]-after[i][1] for i in range(5)]
assert max(gaps)-min(gaps)<1e-5,gaps
S['signal_equal_edge_gap']=gap
report={'before_gaps':[before[i+1][0]-before[i][1] for i in range(5)],'after_gaps':gaps,'letters':changes,'rule':'Equal visible horizontal edge gaps; preserve word left and right bounds, letter sizes and colors.'}
(OUT/'checks/signal_spacing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.context.window.scene=D
f=PKG/'Models/BirdsNest_Enhanced.fbx'
bpy.ops.export_scene.fbx(filepath=str(f),use_selection=False,use_visible=False,object_types={'MESH','EMPTY'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',colors_type='LINEAR',bake_anim=False,path_mode='STRIP',embed_textures=False,add_leaf_bones=False)
bpy.context.window.scene=S
p=OUT/'optimization_geometry.json'
data=json.loads(p.read_text(encoding='utf-8'));data['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend'))
print(json.dumps(report,ensure_ascii=False))
