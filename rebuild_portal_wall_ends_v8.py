import bpy,math,ast,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
src=(ROOT/'connect_seating_entries_v7.py').read_text(encoding='utf-8');exec(src[src.index('tree=ast.parse'):src.index('COL={')]);COL={c.name[:2]:c for c in S.collection.children}
exec(src[src.index('def point('):src.index('for bay in range(12):')])
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports'];concrete=bpy.data.materials['concrete'];metal=bpy.data.materials['栏杆细金属']
for p in ports:
 tag='F%d_B%02d'%(p['level'],p['bay']);L=p['length'];run=p['step_run'];h=p['height'];zfloor=p['concourse'];count=p['step_count'];a=p['angle']
 for prefix in ['V7_入口侧墙_','V7_入口扶手_']:
  old=S.objects.get(prefix+tag)
  if old:bpy.data.objects.remove(old,do_unlink=True)
 walls=Batch('V7_入口侧墙_'+tag,concrete,'22');posts=Batch('V7_入口扶手_'+tag,metal,'22')
 for side in [-1,1]:
  walls.box(point(p,(L-run+.9)/2,side*1.125,h+.42),(L-run-.9,.15,1.12),a)
  for j in range(count):
   top=zfloor+(j+1)*(h-zfloor)/count;t=L-(j+.5)*.28
   walls.box(point(p,t,side*1.125,top+.335),(.28,.15,.95),a)
  for j in range(int((L-run-.9)/1.5)+1):posts.box(point(p,.9+j*1.5,side*1.125,h+.98),(.045,.045,.24),a)
 walls.finish();posts.finish()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
