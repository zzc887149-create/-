"""Complete exposed landing edges and the bridge balustrades behind the bowl."""
import bpy,math,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
tree=ast.parse((ROOT/'rebuild_seating_v21.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
for ob in list(S.objects):
    if ob.name.startswith('V21_公共平台完整护栏_'):bpy.data.objects.remove(ob,do_unlink=True)
for b in range(N):
    g=Mesh('V21_公共平台完整护栏_%02d'%b,bpy.data.materials['栏杆细金属'])
    def rail(ra,rb,wa,wb,z):
        track(g,[q(2,b,ra+(rb-ra)*i/9,wa+(wb-wa)*i/9,z) for i in range(10)])
    for z in [22.5,25.6,29.6,34.0]:
        rail(15.6,18.1,8.8,8.8,z)
        rail(18.1,18.1,8.8,10,z)
    for lo,hi in zip([22.5,25.6,29.6],[25.6,29.6,34]):
        z=(lo+hi)/2
        rail(15.9,18.1,15.4,15.4,z)
        rail(15.9,15.9,14.2,15.4,z)
        rail(18.1,18.1,14.2,15.4,z)
    for w in [8.8,10.0]:rail(3.0,14.35,w,w,22.5)
    g.finish()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
