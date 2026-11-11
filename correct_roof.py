import bpy,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
s=bpy.context.scene
roof=bpy.data.objects['PTFE马鞍形屋面']
if not roof.get('layer_clearance_corrected'):
    for v in roof.data.vertices:v.co.z-=2.8
    roof['layer_clearance_corrected']=True
    # Bowl height at the two low ends follows the saddle envelope.
    names=['三层看台_层3','看台座椅_红','看台座椅_灰白','观众头部_远景','全场手机星光']
    names += ['观众衣着_'+str(i) for i in range(5)]
    for name in names:
        ob=bpy.data.objects.get(name)
        if ob and ob.type=='MESH':
            for v in ob.data.vertices:
                x,y,z=v.co
                if z>24 and (x/110)**2+(y/135)**2>.90:
                    a=math.atan2(y/155,x/132)
                    v.co.z -= 12.5*math.sin(a)**4*min(1,max(0,(z-24)/22))
            ob.data.update()
    # Warm front parapet of tier 3 also follows the low-end adjustment.
    for ob in s.objects:
        if ob.name.startswith('看台层间前檐_2') and ob.type=='MESH':
            for v in ob.data.vertices:
                x,y,z=v.co;a=math.atan2(y/144,x/119)
                v.co.z-=12.5*math.sin(a)**4*min(1,max(0,(z-24)/22))
cam=bpy.data.objects['CAM_03_鸟巢建筑鸟瞰'];cam.location=(315,-354,290);cam.data.lens=45
cam.rotation_euler=(Vector((0,0,23))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_没有信号_鸟巢.blend'))
def rerender():
    env=bpy.data.objects['夜间环境填光'].data
    for name,fn in [('CAM_01_现场正面全景','01_现场正面.png'),('CAM_02_看台斜向全景','02_看台视角.png'),('CAM_03_鸟巢建筑鸟瞰','03_鸟巢鸟瞰.png')]:
        s.camera=bpy.data.objects[name];s.render.filepath=str(ROOT/'renders'/fn)
        if name.startswith('CAM_03'):env.energy=250000
        bpy.ops.render.render(write_still=True)
        env.energy=14000
    s.camera=bpy.data.objects['CAM_01_现场正面全景'];s.render.filepath=str(ROOT/'renders/01_现场正面.png')
    (ROOT/'renders/roof_correction_done.json').write_text(json.dumps({'roof_clearance_m':2.8,'low_end_seating_adjusted':True}),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_没有信号_鸟巢.blend'))
    return None
bpy.app.timers.register(rerender,first_interval=1)
print('Roof and seating clearance corrected, three renders queued')
