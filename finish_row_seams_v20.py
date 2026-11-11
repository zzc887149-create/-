"""Broaden row transfer pads to survive imported collider edge tolerances."""
import bpy,math,ast,bisect
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
C=next(c for c in S.collection.children if c.name.startswith('27_'))
N=24;PHASE=.03834;HALF=2.4;tables={}
tree=ast.parse((ROOT/'rebuild_seating_v20.py').read_text(encoding='utf-8'))
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CF','CV','TIERS') for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
old=S.objects.get('V20_逐排接缝加强平台')
if old:bpy.data.objects.remove(old,do_unlink=True)
pads=Mesh('V20_逐排接缝加强平台',bpy.data.materials['concrete'])
for t,(_,_,nn,step) in enumerate(TIERS):
    for b in range(N):
        for j in range(nn):
            r=(j+.5)*step
            for side in [-1,1]:
                a,bb=sorted((side*1.44,side*2.85))
                tile(pads,t,b,r-.115,r+.115,a,bb,lambda w:H(t,j,b,w)-.002,.24)
pads.finish();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
