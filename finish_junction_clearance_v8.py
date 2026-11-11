import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=(ROOT/'refine_seating_mouths_v8.py').read_text(encoding='utf-8')
exec(src[src.index('tree=ast.parse'):src.index('COL={')]);COL={c.name[:2]:c for c in S.collection.children}
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports'];tiers=[(76,106,1.2,23,.9,.54,12),(99,128,17,16,1.02,.65,9)]
exec(src[src.index('def prism('):src.index('for p in ports:')])
def cut_object(ob,cutter):
 m=ob.modifiers.new('V8_净空收口','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 ob.modifiers.clear();ob.data=me
cut=Batch('V8_TEMP_分流平台净空',None,'23')
for p in ports:
 rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height'];tile(cut,q,r-.51,r+.51,-3.2,3.2,h-.1,h+2.2)
cutter=cut.finish();bpy.context.view_layer.update()
for ob in list(S.objects):
 if ob.type=='MESH' and ob.name.startswith(('V7_入口侧墙_','V7_入口扶手_')):cut_object(ob,cutter)
 if ob.type=='CURVE' and ob.name.startswith('V7_连接扶手_'):
  # Withdraw the head of each handrail to the end of the new turning platform.
  tag=ob.name.split('V7_连接扶手_')[1].split('.')[0];level=int(tag[1]);bay=int(tag.split('_B')[1]);p=next(p for p in ports if p['level']==level and p['bay']==bay)
  for sp in ob.data.splines:
   v=sp.points[0];pos=Vector(v.co[:3]);pos+=Vector(p['rad'])*.85;v.co=(*pos,1)
bpy.data.objects.remove(cutter,do_unlink=True)
cut=Batch('V8_TEMP_内缘楼板净空',None,'23')
for p in ports:
 if p['tier']!=2 or p['row']!=0:continue
 rx,ry,z,n,step,rise,mid,q=params(p)
 for side in [-1,1]:tile(cut,q,4.6,8.4,side*2.4-.86,side*2.4+.86,19.5,24.8)
cutter=cut.finish();bpy.context.view_layer.update()
for ob in list(S.objects):
 if ob.name=='环形集散厅楼板_F4' or ob.name.startswith('环廊径向梁'):cut_object(ob,cutter)
bpy.data.objects.remove(cutter,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Trimmed portal handrails and obstructing concourse inner edges')
