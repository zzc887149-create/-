import bpy
if 'blender_mcp' not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module='blender_mcp')
def connect():
    if not hasattr(bpy.types,'blendermcp_server') or not bpy.types.blendermcp_server:
        bpy.ops.blendermcp.start_server()
    return None
bpy.app.timers.register(connect,first_interval=2)
