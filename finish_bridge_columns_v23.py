import bpy
from mathutils import Vector
S=bpy.context.scene
for n in [1,5,9,13,17,21,25,29,33,37,41,45]:
    ob=S.objects['环廊混凝土柱.%03d'%n]
    if ob.get('v23_bridge_relocated'):continue
    p=ob.matrix_world.translation;ob.location+=Vector((p.x,p.y,0)).normalized()*3.2;ob['v23_bridge_relocated']=True
for n in [1,25,17,41]:
    ob=S.objects['环廊混凝土柱.%03d'%n]
    if ob.get('v23_bridge_adjusted'):continue
    p=ob.matrix_world.translation;r=Vector((p.x,p.y,0)).normalized();t=Vector((-r.y,r.x,0))
    ob.location+=(-r*3.2+t*4.2) if n in [1,25] else t*3.5;ob['v23_bridge_adjusted']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
