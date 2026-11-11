import bpy,bmesh,math,json,ast,bisect,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
src=(ROOT/'finish_seating_v23.py').read_text(encoding='utf-8')
exec(src[:src.index('# Restore closed red shells')])
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
tree=ast.parse((ROOT/'rebuild_seating_v23.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'v23_helpers','exec'))
for o in list(S.objects):
    if o.name.startswith('红色看台背壳_'):bpy.data.objects.remove(o,do_unlink=True)
profiles=[(0,0,0,-1.15)]
for t,(_,_,nn,step) in enumerate(TIERS):
    if t:profiles.append((t,0,0,-.35))
    profiles.extend((t,j,(j+1)*step,-.35) for j in range(nn))
vs=[];fs=[];segments=1120
for t,j,r,dz in profiles:
    rx,ry,_,_=TIERS[t]
    for i in range(segments):
        u=i/segments;a=angle(t,r,u);vs.append(((rx+r)*math.cos(a),(ry+r)*math.sin(a),h(t,j,a)+dz))
for j in range(len(profiles)-1):
    if profiles[j][0]!=profiles[j+1][0]:continue
    for i in range(segments):
        k=(i+1)%segments;fs.append((j*segments+i,j*segments+k,(j+1)*segments+k,(j+1)*segments+i))
me=bpy.data.meshes.new('V23_随阶梯连续碗壁');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['外碗赭红混凝土']);me.update()
ob=bpy.data.objects.new('红色看台背壳_V23_连续底壳',me);next(c for c in S.collection.children if c.name.startswith('13_')).objects.link(ob)
mod=ob.modifiers.new('封闭墙厚','SOLIDIFY');mod.thickness=.18;mod.offset=-1
dg=bpy.context.evaluated_depsgraph_get();ob.data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));ob.modifiers.clear()
data=json.loads((ROOT/'unity_enhanced/checks/v23_cutters.json').read_text(encoding='utf-8'))
me=bpy.data.meshes.new('V23_all_routes');me.from_pydata(data['v'],[],data['f']);me.update()
cut=bpy.data.objects.new('V23_all_routes',me);S.collection.objects.link(cut);bpy.context.view_layer.update()
mod=ob.modifiers.new('真实入口开洞','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;mod.use_self=True
dg=bpy.context.evaluated_depsgraph_get();ob.data=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));ob.modifiers.clear();bpy.data.objects.remove(cut,do_unlink=True)
uv=ob.data.uv_layers.new(name='MetreUV')
for f in ob.data.polygons:
    axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
    for li in f.loop_indices:
        v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
exec(src[src.index('# Update close-up views'):])


