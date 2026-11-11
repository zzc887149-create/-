"""Single portal belt per tier. 28 positions are a reconstruction estimate, not surveyed counts."""
import bpy,math,json,ast,re,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
DEST=ROOT/'赵雷2026_鸟巢_入口环向重排版.blend'
assert S.get('continuous_bowl_v15') and not S.get('layout_v16')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
backup=ROOT/'unity_enhanced/checks/pre_v16';backup.mkdir(exist_ok=True)
for name in ['seating_entries.json','upper_tier_v10.json','seating_junctions_v9.json']:
 shutil.copy2(ROOT/'unity_enhanced/checks'/name,backup/name)
# Restore pre-portal bowl and seating, retaining the latest stage, exterior and rear deck.
targets={o.name:o for o in S.objects if o.type=='MESH' and (o.name.startswith(('三层看台_','看台座椅_','NEAR_','环形集散厅楼板_','环廊径向梁')) or any(c.name.startswith('07_') for c in o.users_collection))}
D=bpy.data.scenes['UNITY_ENHANCED_V3']
targets.update({o.name:o for o in D.objects if o.type=='MESH' and o.name.startswith(('Chunk_SEATS_','Chunk_CROWD_','Chunk_PHONES_'))})
mats={m.name:m for m in bpy.data.materials}
with bpy.data.libraries.load(str(ROOT/'赵雷2026_鸟巢_楼梯连通版.blend'),link=False) as (a,b):
 names=[n for n in targets if n in a.objects];b.objects=names[:]
for name,ob in zip(names,b.objects):
 data=ob.data.copy()
 for i,m in enumerate(data.materials):
  if m:
   base=re.sub(r'\.\d{3}$','',m.name);data.materials[i]=mats.get(base,mats.get(m.name,m))
 targets[name].data=data;bpy.data.objects.remove(ob,do_unlink=True)
for col in list(S.collection.children):
 if col.name[:2] in ['22','23','24','26']:
  for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(col)
for key in ['seating_entries_v7','seating_mouths_v8','upper_tier_v10','portal_enclosures_v14','continuous_bowl_v15']:
 if key in S:del S[key]
# Script adapters suppress historical save paths and operate on the new layout only.
def run(name,edits=()):
 text=(ROOT/name).read_text(encoding='utf-8')
 text=re.sub(r'bpy\.ops\.wm\.save_as_mainfile\(filepath=[^\n]*?\)', 'None',text) if False else text
 # Calls can occur after semicolons: replace the full save expression, including nested str().
 tree=ast.parse(text)
 class SaveRemover(ast.NodeTransformer):
  def visit_Call(self,n):
   if isinstance(n.func,ast.Attribute) and n.func.attr=='save_as_mainfile':return ast.copy_location(ast.Constant(None),n)
   return self.generic_visit(n)
 for old,new in edits:text=text.replace(old,new)
 tree=SaveRemover().visit(ast.parse(text));ast.fix_missing_locations(tree)
 exec(compile(tree,name,'exec'),{})
 (ROOT/'unity_enhanced/checks/v16_progress.txt').write_text(name,encoding='utf-8')
src=(ROOT/'connect_seating_entries_v7.py').read_text(encoding='utf-8')
# Generate one mid-row entrance per angular position, connected to F2/F4.
run('connect_seating_entries_v7.py',[
 ('specs=[(0,0,.08),(0,12,7.5),(1,0,15),(1,9,22.5)]','specs=[(0,12,7.5),(1,9,22.5)]'),
 ('range(12)','range(28)'),
 ('a=(round((bay*math.tau/12+.11-.0105)/(math.tau/40))+1)*math.tau/40+.0105','a=bay*math.tau/28+.19'),
 ("'level':level+1","'level':2 if tier==0 else 4")])
run('refine_seating_exits_v7.py')
run('refine_seating_mouths_v8.py',[("if p['row']==0:","if True:"),("if p['row']!=0:continue","if False:continue")])
run('refine_row_connections_v9.py',[("if p['row']!=0:continue","if False:continue")])
run('rebuild_portal_wall_ends_v8.py')
run('finish_junction_clearance_v8.py',[("if p['tier']!=2 or p['row']!=0:continue","if p['tier']!=2:continue")])
run('finish_row_clearance_v9.py',[("if p['tier']!=2 or p['row']!=0:continue","if p['tier']!=2:continue")])
ob=S.objects['三层看台_层3']
for v in ob.data.vertices:
 if math.hypot(v.co.x/139.55,v.co.y/164.55)>.9995:
  a=math.atan2(v.co.y/164.55,v.co.x/139.55);v.co.x=139.9*math.cos(a);v.co.y=164.9*math.sin(a)
ob.data.update()
run('connect_upper_tier_v10.py', [('range(12)','range(28)'),('a=bay*math.tau/12+.458','a=bay*math.tau/28+.302')])
run('finish_upper_portals_v10.py')
run('finish_portal_enclosures_v14.py')
run('rebuild_bowl_envelope_v15.py')
run('clear_rear_deck_headroom_v12.py')
# Occupancy cleanup uses the same updated angular positions as the new paths.
run('finish_seating_entries_v7.py')
run('clear_row_turns_v9.py',[("or p['row']!=0",'')])
run('clear_upper_occupancy_v10.py')
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/seating_entries.json').write_text(json.dumps(ports,ensure_ascii=False),encoding='utf-8')
# Existing named viewpoint markers are preserved in the export scene.
for o in S.objects:
 if o.name.startswith(('VIEW_','LOOK_')):
  target=D.objects.get(o.name)
  if target:target.location=o.location
S['layout_v16']=True
S['layout_v16_note']='28 estimated positions per tier; no vertically duplicated lower/middle portals; not a surveyed door count.'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('V16 layout complete: 28 lower + 28 middle + 28 upper')
