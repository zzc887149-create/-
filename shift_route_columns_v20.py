"""Relocate a few generic concourse columns that land on approved Sketch-C routes."""
import bpy,json,collections
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
audit=ROOT/'unity_enhanced/checks/v20_audit_fast.json'
if audit.exists():
    data=json.loads(audit.read_text(encoding='utf-8'))
    names=sorted({f.get('hit') for f in data['all_failures'] if (f.get('hit') or '').startswith('环廊混凝土柱')})
else:names=[]
for name in names:
    o=S.objects.get(name)
    if not o:continue
    p=o.matrix_world.translation;tan=Vector((-p.y,p.x,0)).normalized();o.location+=tan*3.2
S['v20_shifted_route_columns']=names
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Shifted route columns:',names)
