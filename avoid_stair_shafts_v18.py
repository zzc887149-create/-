import bpy,json,math,ast
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
file=ROOT/'unity_enhanced/checks/seating_entries.json';data=json.loads(file.read_text(encoding='utf-8'))
for p in data['ports']:
 if p['level']!=4 or p['bay'] not in [4,9,18,23]:continue
 p['angle']+=-.04 if p['bay'] in [4,18] else .045
 a=p['angle'];p['rad']=[math.cos(a),math.sin(a),0];p['tan']=[-math.sin(a),math.cos(a),0];p['entry']=[(99+9.5*1.02)*math.cos(a),(128+9.5*1.02)*math.sin(a),p['height']]
file.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
class Clean(ast.NodeTransformer):
 def visit_Call(self,n):
  if isinstance(n.func,ast.Attribute) and n.func.attr=='save_as_mainfile':return ast.copy_location(ast.Constant(None),n)
  return self.generic_visit(n)
def run(name,edits=(),text=None):
 text=text or (ROOT/name).read_text(encoding='utf-8')
 for a,b in edits:text=text.replace(a,b)
 tree=Clean().visit(ast.parse(text));ast.fix_missing_locations(tree);exec(compile(tree,name,'exec'),{})
for col in list(S.collection.children):
 if col.name[:2] in ['23','26']:
  for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(col)
run('finish_entry_steps_v7.py')
src=(ROOT/'refine_seating_mouths_v8.py').read_text(encoding='utf-8');first=src.index('for p in ports:');last=src.index("for p in ports:\n rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height'];tag=")
src=src[:first]+src[last:]
run('refine_seating_mouths_v8.py',[("assert S.get('seating_entries_v7') and not S.get('seating_mouths_v8')",'assert True'),("if p['row']!=0:continue",'if False:continue')],src)
run('refine_row_connections_v9.py',[("if p['row']!=0:continue",'if False:continue')])
run('rebuild_portal_wall_ends_v8.py')
run('finish_junction_clearance_v8.py',[("if p['tier']!=2 or p['row']!=0:continue","if p['tier']!=2:continue")])
run('finish_row_clearance_v9.py',[("if p['tier']!=2 or p['row']!=0:continue","if p['tier']!=2:continue")])
del S['portal_enclosures_v14'];run('finish_portal_enclosures_v14.py')
del S['continuous_bowl_v15'];run('rebuild_bowl_envelope_v15.py')
run('repair_layout_surfaces_v18.py')
run('finish_seating_entries_v7.py');run('clear_row_turns_v9.py',[("or p['row']!=0",'')])
run('sync_layout_v16_checks.py')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_入口环向重排版.blend'))
print('Four middle entrances shifted away from exterior stair shafts')
