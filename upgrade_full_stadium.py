"""Full-volume venue upgrade, executed through live Blender MCP."""
import bpy,bmesh,math,random,ast,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene
if S.get('full_venue_v2'):raise RuntimeError('Full venue upgrade already applied')
# Reuse authored geometry utilities, never the scene-building top-level code.
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
helpers=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'geometry_helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
for name in ['13_完整外碗与环廊','14_楼梯入口与外立面','15_舞台背部设备','16_全场观察点']:
 c=bpy.data.collections.new(name);S.collection.children.link(c);COL[name[:2]]=c
M={k:bpy.data.materials[k] for k in ['steel','dark','floor','concrete','membrane','red','white','amber','black']}
M['facade']=material('外碗赭红混凝土',(.37,.035,.025),.85)
M['silver']=material('外层浅灰钢带',(.48,.51,.55),.52,.38)
M['glass']=material('环廊深色玻璃',(.045,.085,.105),.27,.25)
def thicken(o,t,back=None):
 if back is not None:o.data.materials.append(back)
 mod=o.modifiers.new('实体厚度_Unity正反可见','SOLIDIFY');mod.thickness=t;mod.offset=-1;mod.use_even_offset=True
 if back is not None:mod.material_offset=len(o.data.materials)-1;mod.material_offset_rim=len(o.data.materials)-1
def flip(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
surfaces=[]
for o in list(S.objects):
 if o.type!='MESH':continue
 if o.name.startswith('三层看台_') or o.name=='PTFE马鞍形屋面':
  flip(o);thicken(o,.32 if '看台' in o.name else .23);surfaces.append(o.name)
 elif o.name=='内场保护地板':thicken(o,.16);surfaces.append(o.name)
 elif o.name.startswith(('旧墙','LED_')):
  thicken(o,.35 if o.name.startswith('旧墙') else .28,M['black']);surfaces.append(o.name)
 elif o.name=='悬挂信封_真实轮廓':thicken(o,.16,M['dark']);surfaces.append(o.name)
 elif o.name.startswith('看台层间前檐_'):thicken(o,.18);surfaces.append(o.name)
for o in COL['01'].objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(M['silver'])
# Closed slab ring with top, underside, outer and inner return walls.
def slab(name,rx0,ry0,rx1,ry1,z,t,mat,c='13'):
 vs=[];N=192
 for zz,rx,ry in [(z-t,rx0,ry0),(z-t,rx1,ry1),(z,rx0,ry0),(z,rx1,ry1)]:
  vs.extend((rx*math.cos(i*math.tau/N),ry*math.sin(i*math.tau/N),zz) for i in range(N))
 fs=[]
 for i in range(N):
  j=(i+1)%N
  fs.extend([(2*N+i,3*N+i,3*N+j,2*N+j),(i,j,N+j,N+i),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)])
 return mesh(name,vs,fs,mat,c)
# Annular floor plates below the rising seating bowl.
for level,z in enumerate([.08,7.5,15,22.5]):
 slab('环形集散厅楼板_F'+str(level+1),84+1.42*z,110+1.10*z,133,150,z,.45,M['concrete'])
 for height in [z+.5,z+1.1]:oval('环廊周圈护栏',132.4,149.4,height,.055,M['red'],'13')
 posts=Batch('环廊护栏立杆_F'+str(level),M['steel'],'13')
 for i in range(240):
  a=i*math.tau/240;posts.box((132.4*math.cos(a),149.4*math.sin(a),z+.6),(.06,.06,1.2))
 posts.finish()
# Red structural bowl back. Panel breaks create visible entrance openings at grade.
profiles=[(92,120,.15),(101.5,131,13.1),(118,144.5,28),(139.5,164.4,45.5)]
for band in range(3):
 x0,y0,z0=profiles[band];x1,y1,z1=profiles[band+1]
 for sector in range(48):
  a0=sector*math.tau/48+.012;a1=(sector+1)*math.tau/48-.012
  rows=8;vs=[]
  for zf in [0,1]:
   for j in range(rows+1):
    a=a0+(a1-a0)*j/rows;rx=x0+(x1-x0)*zf;ry=y0+(y1-y0)*zf;z=z0+(z1-z0)*zf
    if z>24:z-=12.5*math.sin(a)**4*min(1,(z-24)/22)
    if band==0 and sector%4==0 and not zf:z=5.3
    vs.append((rx*math.cos(a),ry*math.sin(a),z))
  fs=[(j,j+1,rows+2+j,rows+1+j) for j in range(rows)]
  o=mesh('红色看台背壳_%d_%02d'%(band,sector),vs,fs,M['facade'],'13');thicken(o,.25)
# Perimeter columns, outer gallery apertures and radial support girders.
for i in range(48):
 a=i*math.tau/48;ca,sa=math.cos(a),math.sin(a)
 beam('环廊混凝土柱',(130*ca,147*sa,0),(130*ca,147*sa,28),.85,.85,M['concrete'],'13')
 for z in [7.5,15,22.5]:
  beam('环廊径向梁',((84+1.42*z)*ca,(110+1.1*z)*sa,z-.55),(133*ca,150*sa,z-.55),.6,.7,M['concrete'],'13')
# Twelve repeated exposed switchback stair bays, based on exterior circulation photos.
for bay in range(12):
 a=bay*math.tau/12+.11;centre=Vector((126.5*math.cos(a),143.5*math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0));rad=Vector((math.cos(a),math.sin(a),0))
 steps=Batch('外廊楼梯_%02d'%bay,M['concrete'],'14')
 for flight in range(6):
  direction=1 if flight%2==0 else -1;zbase=flight*3.75;lane=rad*((flight%2)*2.6-1.3)
  for j in range(25):
   p=centre+lane+tan*((j*.28-3.4)*direction);p.z=zbase+(j+1)*.15-.10
   steps.box(tuple(p),(2.2,.32,.20),a)
  for side in [-1,1]:
   p0=centre+lane+rad*(side*1.1)+tan*(-3.4*direction);p0.z=zbase+1
   p1=centre+lane+rad*(side*1.1)+tan*(3.5*direction);p1.z=zbase+4.75
   line('楼梯连续扶手',[tuple(p0),tuple(p1)],.05,M['red'],'14')
  land=centre+tan*(3.9*direction);land.z=zbase+3.65
  steps.box(tuple(land),(5.4,1.4,.2),a)
 steps.finish()
# Woven facade secondary ribbons are deliberately irregular rather than a uniform cage.
random.seed(24024)
for i in range(76):
 a=i*math.tau/76;span=random.uniform(.28,.72);z0=random.uniform(5,35);dz=random.choice([-1,1])*random.uniform(6,21)
 pts=[]
 for j in range(6):
  t=j/5;aa=a+span*t;z=max(3,min(roofZ(aa)-2,z0+dz*t+2*math.sin(t*math.pi)));k=z/roofZ(aa)
  pts.append(((137+11*k)*math.cos(aa),(155+11.5*k)*math.sin(aa),z))
 for j in range(5):beam('不规则横斜编织带_%02d_%d'%(i,j),pts[j],pts[j+1],.8,.5,M['silver'],'14')
# Entrance portals at each quarter and intermediate sectors; location indicative.
font=None
if Path(r'C:\Windows\Fonts\msyh.ttc').exists():font=bpy.data.fonts.load(r'C:\Windows\Fonts\msyh.ttc')
for i in range(12):
 a=i*math.tau/12;ca,sa=math.cos(a),math.sin(a)
 for offset in [-3.1,3.1]:
  x=136*ca-offset*sa;y=154*sa+offset*ca
  beam('外场入口门柱',(x,y,0),(x,y,5.1),.35,.35,M['dark'],'14')
 p=(136*ca,154*sa,5.2);o=box('入口雨棚',p,(7,3,.25),M['dark'],'14');o.rotation_euler.z=a+math.pi/2
 cv=bpy.data.curves.new('门区标记','FONT');cv.body=chr(65+i);cv.size=2.8;cv.extrude=.08
 ob=link(bpy.data.objects.new('入口标识_'+chr(65+i),cv),'14');ob.location=(139*ca,157*sa,5.1);ob.rotation_euler=(math.pi/2,0,a+math.pi/2);cv.materials.append(M['facade'])
# Back of concert: LED modules, stiffeners, service racks and horizontal access deck.
for side,(x0,x1,y0,curv) in enumerate([(-58,-25.5,64.5,.8),(-25,25,67,3.4),(25.5,58,64.5,.8)]):
 modules=Batch('LED背部模块_%d'%side,M['black'],'15');frames=Batch('LED背部接缝_%d'%side,M['steel'],'15')
 cols=round((x1-x0)/1.25)
 for i in range(cols):
  u=(i+.5)/cols;x=x0+(x1-x0)*u;y=y0+curv*(1-(2*u-1)**2)+.43
  for j in range(14):modules.box((x,y,9.75+j*1.5),((x1-x0)/cols-.035,.35,1.45))
  frames.box((x,y+.22,19.5),(.05,.09,21))
 modules.finish();frames.finish()
for x in range(-54,55,6):
 beam('大屏背面斜撑',(x,72,30),(x,80,2.3),.18,.18,M['steel'],'15')
box('后台通行地台',(0,74,1.1),(116,8,2.2),M['dark'],'15')
for x in [-42,-30,30,42]:
 box('后台设备机柜',(x,77,3.2),(2.5,1.4,2),M['black'],'15')
 for j in range(5):box('机柜散热格栅',(x,77.72,2.5+j*.3),(2.2,.02,.08),M['steel'],'15')
bpy.data.objects['广场基座'].dimensions=(440,480,2)
# Exportable viewpoint empties; Unity derives coordinates from these after FBX conversion.
views=[('01_Exterior_NE',(260,-285,110),(0,0,23)),('02_Exterior_SW',(-260,285,90),(0,0,23)),('03_Exterior_Ground',(220,-195,7),(0,0,31)),('04_Inside_Stage',(0,-82,20),(0,62,17)),('05_Inside_Reverse',(0,48,7),(0,-90,26)),('06_Inside_Side',(-90,0,20),(38,15,22)),('07_Concourse',(130,-23,10),(116,34,10)),('08_Backstage',(0,95,16),(0,68,17)),('09_Aerial',(0,-35,390),(0,0,0))]
for name,p,t in views:
 for prefix,pos in [('VIEW_',p),('LOOK_',t)]:
  ob=link(bpy.data.objects.new(prefix+name,None),'16');ob.location=pos
 camera('CHECK_'+name,p,t,34 if 'Ground' not in name else 25)
S['full_venue_v2']=True;S['full_venue_scope']='360-degree closed surfaces; approximate exterior bowl, concourses, 12 stairs, backstage. Not surveyed room-by-room architecture.'
S['unity_export_exclusions']='Volume fog box, Blender lights/cameras, reference images; game lighting rebuilt in Unity.'
S.camera=bpy.data.objects['CHECK_01_Exterior_NE']
# Clear inspection lighting for all-angle geometric checks.
bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Strength'].default_value=.65
env=bpy.data.objects['夜间环境填光'].data;env.energy=450000;env.color=(.8,.87,1)
light('全场检查阳光','SUN',(180,-200,220),(0,0,0),(1,.89,.76),2.1)
bpy.data.objects['灯束薄雾范围'].hide_render=True
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.shading.type='SOLID';a.spaces.active.overlay.show_overlays=True
  a.spaces.active.region_3d.view_perspective='PERSP';a.spaces.active.region_3d.view_distance=430;a.spaces.active.region_3d.view_location=(0,0,20)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_全场_Unity.blend'))
ROOT.joinpath('unity_delivery').mkdir(exist_ok=True)
(ROOT/'unity_delivery/geometry_changes.json').write_text(json.dumps({'thickened_surfaces':surfaces,'objects':len(S.objects),'viewpoints':9,'circulation_note':'Visually estimated from real photos; not construction drawings.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'objects':len(S.objects),'thickened':len(surfaces),'full_venue_saved':True},ensure_ascii=False))
