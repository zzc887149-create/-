"""Photo-informed architectural refinement. Run in live Blender via MCP."""
import bpy,bmesh,math,random,ast,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene
assert S.get('full_venue_v2') and not S.get('enhanced_v3')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_精修日夜版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
helpers=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'geometry_helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
for name in ['17_精修建筑细节','18_近景补充']:
 c=bpy.data.collections.new(name);S.collection.children.link(c);COL[name[:2]]=c
M={k:bpy.data.materials[k] for k in ['steel','dark','floor','concrete','membrane','red','white','amber','black','skin','phone']}
silver=bpy.data.materials['外层浅灰钢带'];bs=next(n for n in silver.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.57,.565,.54,1);bs.inputs['Metallic'].default_value=.16;bs.inputs['Roughness'].default_value=.56
silver.diffuse_color=(.57,.565,.54,1)
redpaint=material('楼梯红色防滑涂层',(.42,.027,.018),.78)
signwhite=material('导向标识白漆',(.8,.83,.8),.6,0,.05)
joint=material('地坪伸缩缝',(.075,.08,.085),.94)
grille=material('栏杆细金属',(.24,.27,.28),.42,.5)
floorpaint=material('内场橡胶防护板',(.07,.075,.082),.87)

# Use a real CC0 material for concrete. UVs below use world metre scale.
texdir=ROOT/'textures/Concrete034'
concrete=M['concrete'];b=next(n for n in concrete.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for suffix,socket in [('Color','Base Color'),('Roughness','Roughness')]:
 n=concrete.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(texdir/('Concrete034_1K-JPG_'+suffix+'.jpg')),check_existing=True);n.image.pack()
 if suffix!='Color':n.image.colorspace_settings.name='Non-Color'
 concrete.node_tree.links.new(n.outputs['Color'],b.inputs[socket])
nm=concrete.node_tree.nodes.new('ShaderNodeTexImage');nm.image=bpy.data.images.load(str(texdir/'Concrete034_1K-JPG_NormalGL.jpg'),check_existing=True);nm.image.colorspace_settings.name='Non-Color';nm.image.pack()
normal=concrete.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
concrete.node_tree.links.new(nm.outputs['Color'],normal.inputs['Color']);concrete.node_tree.links.new(normal.outputs['Normal'],b.inputs['Normal'])
concrete['pbr_asset']='Concrete034';concrete['world_uv_metres']=2

def bevel(o,width=.04):
 mod=o.modifiers.new('近景倒角','BEVEL');mod.width=width;mod.segments=2;mod.limit_method='ANGLE'
 return o
def strip(name,pts,width,depth,c='01',mat=None):
 """Continuous rectangular ribbon; broad face follows the shell instead of random beam roll."""
 pts=[Vector(p) for p in pts];vs=[];fs=[]
 for j,p in enumerate(pts):
  tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
  normal=Vector((p.x/148**2,p.y/166.5**2,0)).normalized()
  across=tangent.cross(normal).normalized();normal=across.cross(tangent).normalized()
  for a,b0 in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append(tuple(p+across*(a*width/2)+normal*(b0*depth/2)))
 for j in range(len(pts)-1):
  for k in range(4):fs.append((4*j+k,4*j+(k+1)%4,4*(j+1)+(k+1)%4,4*(j+1)+k))
 fs.extend([(3,2,1,0),tuple(4*(len(pts)-1)+k for k in range(4))])
 return bevel(mesh(name,vs,fs,mat or silver,c),.035)

# Replace only the procedural secondary facade authored in v1/v2. Retain the 24 primary trusses.
replaced=[]
for o in list(S.objects):
 if o.name.startswith(('交织钢带_','不规则横斜编织带_')):
  replaced.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for o in COL['01'].objects:
 if o.name.startswith('主桁架柱_'):
  for v in o.data.vertices:v.co.x*=1.42;v.co.y*=1.2
  bevel(o,.055)
 elif o.name.startswith(('屋面主梁_','屋面交织带_')):
  for v in o.data.vertices:v.co.x*=1.55;v.co.y*=1.3
  bevel(o,.025)
random.seed(20261024)
for i in range(104):
 a=i*math.tau/104+random.uniform(-.026,.026)
 span=random.choice([-1,1])*random.uniform(.18,.72)
 pts=[]
 for j in range(19):
  t=j/18;aa=a+span*t+.018*math.sin(t*math.pi*2+i);z=roofZ(aa)*t
  rx=136.7+11.3*t+.65*math.sin(math.pi*t);ry=154.7+11.8*t+.65*math.sin(math.pi*t)
  pts.append((rx*math.cos(aa),ry*math.sin(aa),z))
 strip('精修通高编织钢梁_%03d'%i,pts,random.uniform(1.45,2.15),random.uniform(.65,.95))
for i in range(66):
 a=i*math.tau/66;span=random.uniform(.32,.90);mid=random.uniform(.2,.8);delta=random.choice([-1,1])*random.uniform(.15,.5);pts=[]
 for j in range(15):
  t=j/14;aa=a+span*t;h=max(.035,min(.97,mid+delta*(t-.5)))
  pts.append(((137.5+11*h)*math.cos(aa),(155.5+11.5*h)*math.sin(aa),roofZ(aa)*h))
 strip('精修斜横钢梁_%03d'%i,pts,random.uniform(1.25,1.85),.68)
# Welded end plates at the primary columns, limited small details with real bevels.
for i in range(24):
 a=i*math.tau/24
 o=box('主柱基脚钢板',(137*math.cos(a),155*math.sin(a),.18),(4.1,3.6,.36),silver,'17');o.rotation_euler.z=a;bevel(o,.04)

# Roof edge return closes the visual gap between the roof membrane and steel perimeter.
o=ribbon('屋面外沿收边',[(147.7,166.2,lambda a:roofZ(a)-3.0),(147.7,166.2,lambda a:roofZ(a)-.7)],M['membrane'],'17')
m=o.modifiers.new('收边厚度','SOLIDIFY');m.thickness=.23

# Exterior staircase: real photo shows red tread centres, concrete side walls and silver handrails.
for bay in range(12):
 a=bay*math.tau/12+.11;centre=Vector((126.5*math.cos(a),143.5*math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0));rad=Vector((math.cos(a),math.sin(a),0))
 steps=Batch('楼梯红色踏步_%02d'%bay,redpaint,'17');noses=Batch('楼梯踏步防滑边_%02d'%bay,grille,'17')
 for flight in range(6):
  direction=1 if flight%2==0 else -1;zbase=flight*3.75;lane=rad*((flight%2)*2.6-1.3)
  for j in range(25):
   p=centre+lane+tan*((j*.28-3.4)*direction);p.z=zbase+(j+1)*.15+.007
   steps.box(tuple(p),(1.6,.27,.015),a)
   p+=tan*(.12*direction);p.z+=.007;noses.box(tuple(p),(2.05,.025,.025),a)
  for side in [-1,1]:
   p0=centre+lane+rad*(side*1.18)+tan*(-3.5*direction);p0.z=zbase-.05
   p1=centre+lane+rad*(side*1.18)+tan*(3.5*direction);p1.z=zbase+3.7
   v=[tuple(p0),tuple(p1),tuple(p1+Vector((0,0,.95))),tuple(p0+Vector((0,0,.95)))]
   o=mesh('楼梯实体侧墙',v,[(0,1,2,3)],concrete,'17');m=o.modifiers.new('侧墙厚度','SOLIDIFY');m.thickness=.14
  for j in range(0,25,5):
   p=centre+lane+tan*((j*.28-3.4)*direction);p.z=zbase+(j+1)*.15
   line('楼梯中央护栏立杆',[tuple(p),tuple(p+Vector((0,0,1.0)))],.035,grille,'17')
  p0=centre+lane+tan*(-3.4*direction);p0.z=zbase+1.1
  p1=centre+lane+tan*(3.5*direction);p1.z=zbase+4.85
  line('楼梯中央扶手',[tuple(p0),tuple(p1)],.04,grille,'17')
 steps.finish();noses.finish()

# Concourse balusters and simple directional signs at every entrance; positions are illustrative.
for level,z in enumerate([.08,7.5,15,22.5]):
 rails=Batch('环廊竖向护栏填充_%d'%level,grille,'17')
 for i in range(1200):
  a=i*math.tau/1200;rails.box((132.4*math.cos(a),149.4*math.sin(a),z+.55),(.025,.025,1.0))
 rails.finish()
for i in range(12):
 a=i*math.tau/12;pos=Vector((132*math.cos(a),149*math.sin(a),4.5))
 o=box('入口红色导向牌',pos,(5.0,.14,1.2),redpaint,'17');o.rotation_euler.z=a+math.pi/2
 cv=bpy.data.curves.new('入口导向字','FONT');cv.body='GATE '+chr(65+i);cv.size=.57;cv.align_x='CENTER';cv.extrude=.002
 o=link(bpy.data.objects.new('入口导向_'+chr(65+i),cv),'17');o.location=pos+Vector((.12*math.cos(a),.12*math.sin(a),-.2));o.rotation_euler=(math.pi/2,0,a+math.pi/2);cv.materials.append(signwhite)

# Real material floor tiling with expansion joints; no giant untextured grey slab.
seams=Batch('广场石材分格缝',joint,'17')
for x in range(-220,221,4):seams.box((x,0,-.091),(.018,480,.008))
for y in range(-240,241,4):seams.box((0,y,-.091),(440,.018,.008))
seams.finish()
field=S.objects['内场保护地板'];field.data.materials.clear();field.data.materials.append(floorpaint)
# Stage metal access details, cable covers and ramp edge markers.
for side in [-1,1]:
 for i in range(10):
  o=box('后台线缆保护槽',(side*45,73+i*.45,2.25),(7,.18,.09),M['black'],'18');bevel(o,.035)
 for j in range(5):
  box('侧台防滑踏步边',(side*58,54+j*.45-.2,.45+j*.44),(1.9,.04,.025),signwhite,'18')
for x in range(-48,49,4):
 o=box('前沿楔形返听箱',(x,51.8,2.55),(.95,.65,.55),M['black'],'18');o.rotation_euler.x=.16;bevel(o,.055)
 box('返听箱前网',(x,51.45,2.58),(.82,.025,.33),grille,'18')

# Round the nearest audience heads; distant low-poly audience is retained for LOD.
head=S.objects['观众头部_远景'];data=head.data
vs=[];fs=[];newv=[];newf=[];near_count=0
for i in range(0,len(data.vertices),6):
 pts=[data.vertices[i+j].co.copy() for j in range(6)];p=sum(pts,Vector())/6
 if abs(p.x)<33 and 8<p.y<43 and p.z<4:
  near_count+=1;start=len(newv);r=(pts[0]-p).length
  for zz,rr in [(-.11,.065),(-.065,.11),(.065,.105),(.125,.05)]:
   for k in range(8):
    a=k*math.tau/8;newv.append((p.x+rr*math.cos(a),p.y+rr*.88*math.sin(a),p.z+zz))
  for j in range(3):
   for k in range(8):newf.append(tuple(start+n for n in [j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k]))
  newf.extend([tuple(start+k for k in range(7,-1,-1)),tuple(start+24+k for k in range(8))])
 else:
  off=len(vs);vs.extend(tuple(p0) for p0 in pts)
  fs.extend(tuple(off+j for j in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)])
old=head.data;new=bpy.data.meshes.new('远景头部保留');new.from_pydata(vs,[],fs);new.materials.append(M['skin']);head.data=new
near=mesh('NEAR_近场圆润头部',newv,newf,M['skin'],'18')
for p in near.data.polygons:p.use_smooth=True

# Assign metre-scale UVs to generic architecture only. Preserve photo and screen UVs.
for o in S.objects:
 if o.type!='MESH' or not any(m==concrete for m in o.data.materials):continue
 if o.data.uv_layers:continue
 uv=o.data.uv_layers.new(name='MetreUV');mw=o.matrix_world
 for p in o.data.polygons:
  n=mw.to_3x3()@p.normal;axis=max(range(3),key=lambda k:abs(n[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   v=mw@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
# LED brightness will be driven separately in Unity. Keep Blender screen highlights restrained too.
for m in bpy.data.materials:
 if m.name.startswith('现场LED_'):
  b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Emission Strength'].default_value=.7
S['enhanced_v3']=True;S['v3_near_heads']=near_count
S['v3_note']='Photographic architectural refinement, not surveyed fabrication geometry; generic CC0 concrete; 170 continuous facade ribbons.'
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.overlay.show_overlays=False
  area.spaces.active.region_3d.view_rotation=S.objects['CHECK_01_Exterior_NE'].rotation_euler.to_quaternion()
  area.spaces.active.region_3d.view_location=(0,0,24);area.spaces.active.region_3d.view_distance=410
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_精修日夜版.blend'))
print(json.dumps({'objects':len(S.objects),'replaced_segment_objects':len(replaced),'continuous_facade_ribbons':170,'near_round_heads':near_count},ensure_ascii=False))
