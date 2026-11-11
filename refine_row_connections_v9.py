"""Align flanking stairs to every seating row, preserving central entry landings."""
import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('seating_mouths_v8')
src=(ROOT/'refine_seating_mouths_v8.py').read_text(encoding='utf-8')
exec(src[src.index('tree=ast.parse'):src.index('COL={')])
COL={c.name[:2]:c for c in S.collection.children}
ports=json.loads((ROOT/'unity_enhanced/checks/seating_entries.json').read_text(encoding='utf-8'))['ports']
tiers=[(76,106,1.2,23,.9,.54,12),(99,128,17,16,1.02,.65,9)]
exec(src[src.index('def prism('):src.index('for p in ports:')])
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层']
samples=[];routes=[];links=[];changed=[]
def replace(batch):
 old=S.objects.get(batch.name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 ob=batch.finish();changed.append(ob);return ob
for p in ports:
 rx,ry,z,n,step,rise,mid,q=params(p);r=p['row']*step;h=p['height'];tag='F%d_B%02d'%(p['level'],p['bay'])
 deck=Batch('V8_出口分流平台_'+tag,concrete,'23')
 # Keep the centre of the landing full depth; the wings meet the row-height tread.
 tile(deck,q,r-.5,r+.5,-1.6,1.6,h-.28,h+.008)
 for side in [-1,1]:
  tile(deck,q,r-(.5 if p['row']==0 else .12),r+.12,min(side*1.6,side*3.2),max(side*1.6,side*3.2),h-.28,h+.008)
 replace(deck)
 for t in [-.3,0,.3]:
  for w in [-1.2,0,1.2]:samples.append({'kind':'landing','bay':p['bay'],'point':list(q(r+t,w,h+.008))})
 for side in [-1,1]:
  points=[list(q(r,w*side,h+1.3)) for w in [0,.6,1.2,1.8,2.4]]
  routes.append({'kind':'landing_turn','points':points})
 if p['row']!=0:continue
 div=math.ceil(rise/.18-1e-6);run=step/div
 for side in [-1,1]:
  stairs=Batch('V8_看台细分梯道_'+tag+'_'+str(side),concrete,'23')
  noses=Batch('V8_梯道踏边_'+tag+'_'+str(side),red,'23');path=[]
  for k in range((n-1)*div+1):
   centre=k*run;lo=centre-run/2 if k else -.5
   hi=centre+run/2 if k<(n-1)*div else (n-1)*step+.5
   top=z+k*rise/div
   tile(stairs,q,lo,hi,side*2.4-.8,side*2.4+.8,z-.45,top+.008)
   # Leave the row-height tread unpainted across its lateral seating connection.
   if k%div:tile(noses,q,lo,lo+.025,side*2.4-.76,side*2.4+.76,top+.008,top+.014)
   for w in [side*2.4-.5,side*2.4,side*2.4+.5]:samples.append({'kind':'aisle','bay':p['bay'],'point':list(q(centre,w,top+.008))})
   path.append(list(q(centre,side*2.4,top+1.3)))
  for j in range(n):
   rj=j*step;target=z+j*rise
   # Continuous broad connection within the native row footprint.
   half=run*.48
   tile(stairs,q,rj-half,rj+half,min(side*3.02,side*3.65),max(side*3.02,side*3.65),z-.45,target+.008)
   for dr in [-half*.8,0,half*.8]:
    for w in [3.05,3.18,3.21,3.35,3.55,3.64,3.70,3.85]:
     samples.append({'kind':'row_transition','bay':p['bay'],'point':list(q(rj+dr,side*w,target+(.008 if w<3.65 else 0)))})
   routes.append({'kind':'row_turn','points':[list(q(rj,side*w,target+1.3)) for w in [2.4,2.8,3.2,3.6,3.85]]})
   links.append({'bay':p['bay'],'tier':p['tier'],'row':j,'side':side,'height_difference':0})
  replace(stairs);replace(noses);routes.append({'kind':'aisle','points':path})
for ob in changed:
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='MetreUV')
 for f in ob.data.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
data={'landings':48,'flanking_aisles':48,'samples':samples,'routes':routes,'row_links':links}
(ROOT/'unity_enhanced/checks/seating_junctions_v9.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
checks={'samples':samples,'segments':[{'kind':r['kind'],'a':a,'b':b} for r in routes for a,b in zip(r['points'],r['points'][1:])]}
(ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/junction_checks.json').write_text(json.dumps(checks,ensure_ascii=False),encoding='utf-8')
S['row_connections_v9']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_逐排衔接修复版.blend'))
print('V9 row connections',len(links),'samples',len(samples))
