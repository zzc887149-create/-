import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
upper=json.loads((ROOT/'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))['ports']
assert len(ports)==56 and len(upper)==28
for tier in [1,2]:
 ps=[p for p in ports if p['tier']==tier]
 assert len(ps)==28 and len({round(p['angle'],5) for p in ps})==28 and len({p['row'] for p in ps})==1
p=next(p for p in ports if p['bay']==0 and p['tier']==1)
e=Vector(p['entry']);r=Vector(p['rad']);t=Vector(p['tan'])
positions={'VIEW_14_SeatingEntry':e+r*(p['length']+1)+t*0+Vector((0,0,p['concourse']+1.8-p['height'])),
 'LOOK_14_SeatingEntry':e-r*3+Vector((0,0,1.5)),
 'VIEW_15_SeatingJunction':e-r*6+t*5+Vector((0,0,4)),
 'LOOK_15_SeatingJunction':e+r+Vector((0,0,.5))}
p=upper[0];e=Vector(p['entry']);e.z=p['height'];r=Vector((math.cos(p['angle']),math.sin(p['angle']),0));t=Vector((-r.y,r.x,0))
positions.update({'VIEW_16_UpperTier':e-r*6+t*6+Vector((0,0,4)),'LOOK_16_UpperTier':e+r+Vector((0,0,1))})
for name,pos in positions.items():
 S.objects[name].location=pos
 if D.objects.get(name):D.objects[name].location=pos
editor=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor'
(editor/'seating_entries.json').write_text(json.dumps({'ports':ports},ensure_ascii=False),encoding='utf-8')
for source,dest in [('seating_junctions_v9.json','junction_checks.json'),('upper_tier_v10.json','upper_tier_checks.json')]:
 data=json.loads((ROOT/'unity_enhanced/checks'/source).read_text(encoding='utf-8'))
 out={'samples':data['samples'],'segments':[{'kind':r['kind'],'a':a,'b':b} for r in data['routes'] for a,b in zip(r['points'],r['points'][1:])]}
 (editor/dest).write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
(ROOT/'unity_enhanced/checks/layout_v16.json').write_text(json.dumps({'portals_per_tier':[28,28,28],'total':84,'lower_middle_vertical_duplicates':0,'counts_are_reconstruction_estimates':True},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_入口环向重排版.blend'))
print('Layout and check metadata synchronized: 84 portals, no lower/middle duplicate positions')
