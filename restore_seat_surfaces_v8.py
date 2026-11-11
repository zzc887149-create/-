import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=(ROOT/'refine_seating_mouths_v8.py').read_text(encoding='utf-8')
exec(src[src.index('tree=ast.parse'):src.index('COL={')]);COL={c.name[:2]:c for c in S.collection.children}
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports'];tiers=[(76,106,1.2,23,.9,.54,12),(99,128,17,16,1.02,.65,9)]
exec(src[src.index('def prism('):src.index('for p in ports:')])
names=['三层看台_层1','三层看台_层2']
with bpy.data.libraries.load(str(ROOT/'赵雷2026_鸟巢_看台接通版.blend'),link=False) as (source,target):target.objects=names[:]
for name,loaded in zip(names,target.objects):
 S.objects[name].data=loaded.data.copy();S.objects[name].data.materials.clear();S.objects[name].data.materials.append(bpy.data.materials['concrete']);bpy.data.objects.remove(loaded,do_unlink=True)
for group in ['aisles','landings']:
 cut=Batch('V8_TEMP_'+group,None,'23')
 for p in ports:
  rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height']
  if group=='landings':tile(cut,q,r-.51,r+.51,-3.2,3.2,h-.35,h+2.75)
  elif p['row']==0:
   for side in [-1,1]:tile(cut,q,-.51,(n-1)*step+.51,side*2.4-.78,side*2.4+.78,z-.6,z+n*rise+3)
 cutter=cut.finish();bpy.context.view_layer.update()
 for name in names:
  ob=S.objects[name];m=ob.modifiers.new('V8_分离开槽','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;m.use_self=True
  dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=me
 bpy.data.objects.remove(cutter,do_unlink=True)
# Solid supporting blocks remove the unsupported stair slab appearance.
for p in ports:
 if p['row']!=0:continue
 for side in [-1,1]:
  ob=S.objects['V8_看台细分梯道_F%d_B%02d_%s'%(p['level'],p['bay'],side)]
  # Each authored box has four lower vertices followed by four upper vertices.
  for base in range(0,len(ob.data.vertices),8):
   for i in range(4):ob.data.vertices[base+i].co.z=p['height']-.45
  ob.data.update()
for ob in list(S.objects):
 if ob.type!='MESH' or not (ob.name in names or ob.name.startswith(('V7_入口侧墙_','V8_看台细分梯道_'))):continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Restored seating surfaces and cut non-overlapping aisle and landing groups separately')
