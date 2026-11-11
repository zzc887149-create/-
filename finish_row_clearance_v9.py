import bpy,bmesh
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'finish_junction_clearance_v8.py').read_text(encoding='utf-8')
exec(src[:src.index("cut=Batch('V8_TEMP_分流平台净空'")])
cut=Batch('V9_TEMP_逐排衔接净空',None,'23')
for p in ports:
 if p['tier']!=2 or p['row']!=0:continue
 rx,ry,z,n,step,rise,mid,q=params(p)
 for side in [-1,1]:
  tile(cut,q,4.3,9.0,min(side*1.5,side*4.15),max(side*1.5,side*4.15),19.4,25.0)
cutter=cut.finish();bpy.context.view_layer.update()
for ob in list(S.objects):
 if ob.name=='环形集散厅楼板_F4' or ob.name.startswith('环廊径向梁'):cut_object(ob,cutter)
bpy.data.objects.remove(cutter,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Expanded existing concourse-edge clearances to include row turning connections')
