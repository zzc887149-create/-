import bpy,bmesh,math
from pathlib import Path
s=bpy.context.scene;assert s.get('rear_deck_v12')
n=360;vs=[];fs=[]
for h in [13.12,15.4]:
 for rx,ry in [(96.5,126.5),(101.85,131.35)]:
  for i in range(n):
   a=i*math.tau/n;vs.append((rx*math.cos(a),ry*math.sin(a),h))
for i in range(n):
 j=(i+1)%n;fs.extend([(2*n+i,3*n+i,3*n+j,2*n+j),(i,j,n+j,n+i),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
me=bpy.data.meshes.new('V12_temporary_clearance');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
cut=bpy.data.objects.new('V12_temporary_clearance',me);s.collection.objects.link(cut);bpy.context.view_layer.update()
count=0
for ob in list(s.objects):
 if not (ob.name.startswith('环形集散厅楼板_F3') or ob.name.startswith('环廊径向梁')):continue
 mod=ob.modifiers.new('后排平台净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
 dg=bpy.context.evaluated_depsgraph_get();new=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);ob.modifiers.clear();ob.data=new;count+=1
bpy.data.objects.remove(cut,do_unlink=True);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Rear deck overhead floor/beam cut:',count)
