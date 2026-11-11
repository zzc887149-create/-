import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
code=(ROOT/'connect_seating_entries_v7.py').read_text(encoding='utf-8')
exec(code[code.index('tree=ast.parse'):code.index('COL={')])
COL={c.name[:2]:c for c in S.collection.children};C=COL['22'];concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属']
exec(code[code.index('def point('):code.index('for bay in range(12):')])
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
for ob in list(C.objects):bpy.data.objects.remove(ob,do_unlink=True)
exec(code[code.index('for p in ports:\n tag='):code.index('# Open the front safety rail')])
exec(code[code.index('# World-space concrete UVs'):code.index('# The new inspection viewpoint')])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Finished solid stair bases and side guards at all seating entries')
