import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
s=bpy.context.scene
fog=bpy.data.objects['灯束薄雾范围'];fog.display_type='WIRE'
v=next(n for n in bpy.data.materials['舞台薄雾'].node_tree.nodes if n.type=='PRINCIPLED_VOLUME')
v.inputs['Density Attribute'].default_value='';v.inputs['Density'].default_value=.0025
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('舞台交叉'):
        o.data.volume_factor=8;o.data.energy=190000;o.data.spot_size=math.radians(3);o.data.spot_blend=.6;o.data.use_shadow=False
        target=Vector((o.location.x-32,8+(abs(o.location.x)-15)*.6,1))
        o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['CAM_02_看台斜向全景'].data.lens=35
s.eevee.taa_render_samples=64;s.eevee.volumetric_samples=96
s.render.resolution_percentage=100
s.render.resolution_x=1500;s.render.resolution_y=950
s.camera=bpy.data.objects['CAM_01_现场正面全景']
s.render.filepath=str(ROOT/'renders/01_现场正面.png')
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA'
        a.spaces.active.region_3d.view_camera_zoom=0
        a.spaces.active.clip_end=2000
s['渲染说明']='薄雾中的舞台光束为可编辑追光；为露天远景稳定显示，追光体积权重经艺术调整。'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_没有信号_鸟巢.blend'))
def render_deliverables():
    jobs=[('CAM_01_现场正面全景','01_现场正面.png'),('CAM_02_看台斜向全景','02_看台视角.png'),('CAM_03_鸟巢建筑鸟瞰','03_鸟巢鸟瞰.png')]
    status=[]
    for name,fn in jobs:
        s.camera=bpy.data.objects[name];s.render.filepath=str(ROOT/'renders'/fn)
        # Higher exterior fill is an architectural inspection preset only.
        env=bpy.data.objects['夜间环境填光'].data
        old=env.energy
        if name.startswith('CAM_03'):env.energy=250000
        bpy.ops.render.render(write_still=True)
        env.energy=old
        status.append({'camera':name,'file':fn})
        (ROOT/'renders/render_status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    s.camera=bpy.data.objects['CAM_01_现场正面全景'];s.render.filepath=str(ROOT/'renders/01_现场正面.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_没有信号_鸟巢.blend'))
    return None
bpy.app.timers.register(render_deliverables,first_interval=1)
print('Three final renders queued; blend saved.')
