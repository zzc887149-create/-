import bpy,json
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
assert S.get('screen_audience_v24')
bpy.context.window.scene=D
bpy.ops.export_scene.fbx(filepath=str(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Models/BirdsNest_Enhanced.fbx'),use_selection=False,use_visible=False,object_types={'MESH','EMPTY'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',colors_type='LINEAR',bake_anim=False,path_mode='STRIP',embed_textures=False,add_leaf_bones=False)
bpy.context.window.scene=S
exec(compile((ROOT/'report_export_geometry_v23.py').read_text(encoding='utf8').replace("'version':'v23'","'version':'v24'"),'report','exec'))
