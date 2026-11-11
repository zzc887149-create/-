"""Keep field cross aisles open and provide usable FOH side gates/steps."""
import bpy,ast,math,json
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;C=bpy.data.collections['06_内场折叠椅']
tree=ast.parse((ROOT/'rebuild_inner_field_v25.py').read_text(encoding='utf8'))
defs=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Builder' or isinstance(n,ast.FunctionDef) and n.name.startswith('add_barrier_line') or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['CF','CV','OF'] for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'helpers','exec'))
for name in ['内场分区护栏与立柱','调音台控制平台']:
    if S.objects.get(name):bpy.data.objects.remove(S.objects[name],do_unlink=True)
barriers=Builder('内场分区护栏与立柱',bpy.data.materials['栏杆细金属'])
# Outer boundary and centre lane only; all four cross aisles stay open.
for x in [-56,56,-1.35,1.35]:
    spans=[(-52,-34.4),(-30.8,-15),(-11.4,2.8),(6.4,20.6),(24.2,38.8)] if abs(x)>50 else [(-10.2,2.8),(6.4,20.6),(24.2,38.8)]
    for ya,yb in spans:add_barrier_line_y(x,ya,yb)
for x0,x1 in [(-55.2,-39.6),(-36.8,-20.6),(20.6,36.8),(39.6,55.2)]:add_barrier_line_x(x0,x1,41.2)
for y in [-31.5,-13.5]:add_barrier_line_x(-15.2,15.2,y)
for x in [-15.2,15.2]:
    add_barrier_line_y(x,-31.5,-24.4);add_barrier_line_y(x,-20.6,-13.5)
barriers.finish(C)
deck=Builder('调音台控制平台',bpy.data.materials['dark']);fy=-22.5
deck.box((0,fy,.325),(27,15,.65));deck.box((0,fy-3.5,.9),(23,7.2,.5))
for side in [-1,1]:
    for k in range(4):
        top=(k+1)*.1625;deck.box((side*(14.625-k*.35),fy,top/2),(.35,3.2,top))
for k in range(3):
    top=.65+(k+1)/6;deck.box((0,fy+.1+(2.5-k)*.34,(.65+top)/2),(2.4,.34,top-.65))
deck.finish(C)
S['inner_field_v25']=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
