"""Photo-grounded, editable Zhao Lei 2026 Bird's Nest reconstruction.
Executed in the live Blender process through MCP. Scale: metres.
Venue envelope follows published dimensions; temporary stage dimensions estimated.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
random.seed(20260912)
S=bpy.data.scenes.new('赵雷2026_没有信号_鸟巢复刻')
bpy.context.window.scene=S
S.unit_settings.system='METRIC'
S.unit_settings.scale_length=1
COL={}
for name in ['01_鸟巢钢结构','02_看台与屋面','03_舞台与信封','04_LED真实现场贴图','05_灯架音响','06_内场折叠椅','07_观众与手机灯','08_人物乐队','09_纪念座椅','10_灯光','11_摄影机','12_参考图']:
    c=bpy.data.collections.new(name);S.collection.children.link(c);COL[name[:2]]=c
def link(o,c): COL[c].objects.link(o);return o
def mesh(name,vs,fs,mat,c='03',uv=None):
    m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();o=link(bpy.data.objects.new(name,m),c)
    if mat:m.materials.append(mat)
    if uv:
        layer=m.uv_layers.new(name='PhotoUV')
        for p in m.polygons:
            for li in p.loop_indices:layer.data[li].uv=uv[m.loops[li].vertex_index]
    return o
def material(name,color,rough=.5,metal=0,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=emit
    return m
def photo(name,fn,emission=1):
    m=material(name,(.5,.5,.5),.85,0,emission);b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/fn),check_existing=True);t.image.pack()
    m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],b.inputs['Emission Color']);return m
M={}
for key,col,rough,metal,emit in [
('steel',(.29,.33,.38),.4,.7,0),('dark',(.012,.017,.026),.6,.3,0),('floor',(.03,.035,.046),.7,.2,0),('concrete',(.19,.20,.22),.85,0,0),('membrane',(.42,.45,.48),.85,0,0),('red',(.24,.018,.027),.65,0,0),('white',(.55,.52,.49),.7,0,0),('chair',(.18,.20,.22),.55,.3,0),('amber',(1,.28,.055),.3,0,9),('warm',(1,.72,.36),.3,0,7),('cyan',(.22,.62,1),.3,0,6),('phone',(.69,.85,1),.4,0,4),('skin',(.53,.30,.18),.7,0,0),('blue',(.018,.12,.42),.8,0,0),('wood',(.49,.24,.065),.4,0,0),('black',(.009,.011,.015),.6,0,0),('green',(.035,.18,.06),.8,0,0),('petal',(.96,.90,.68),.7,0,0)]:M[key]=material(key,col,rough,metal,emit)
LED=[photo('现场LED_左侧_ACME17','led_left.jpg',1.4),photo('现场LED_中央_ACME17','led_center.jpg',1.4),photo('现场LED_右侧_ACME17','led_right.jpg',1.4)]
WALL=photo('现场旧墙_照片衍生','wall_photo.jpg',.06)
ENV=photo('悬挂信封_现场贴图','envelope.jpg',.8)
cube_v=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
cube_f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,loc,dim,mat,c='03'):
    o=mesh(name,[(v[0]*dim[0],v[1]*dim[1],v[2]*dim[2]) for v in cube_v],cube_f,mat,c);o.location=loc;return o
def line(name,points,r,mat,c='05',closed=False):
    cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=1;cv.bevel_depth=r;cv.bevel_resolution=0
    sp=cv.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    sp.use_cyclic_u=closed;o=link(bpy.data.objects.new(name,cv),c);cv.materials.append(mat);return o
def beam(name,a,b,w,d,mat,c='01'):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(b-a).length),mat,c);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
class Batch:
    def __init__(self,name,mat,c):self.name=name;self.mat=mat;self.c=c;self.v=[];self.f=[]
    def box(self,p,d,angle=0):
        off=len(self.v);ca,sa=math.cos(angle),math.sin(angle)
        for x,y,z in cube_v:
            x*=d[0];y*=d[1];self.v.append((p[0]+ca*x-sa*y,p[1]+sa*x+ca*y,p[2]+z*d[2]))
        self.f.extend(tuple(off+i for i in f) for f in cube_f)
    def oct(self,p,r):
        n=len(self.v);x,y,z=p;self.v.extend([(x+r,y,z),(x-r,y,z),(x,y+r,z),(x,y-r,z),(x,y,z+r),(x,y,z-r)])
        self.f.extend(tuple(n+j for j in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)])
    def finish(self):return mesh(self.name,self.v,self.f,self.mat,self.c)
def oval(name,rx,ry,z,r,mat,c='02'):
    return line(name,[(rx*math.cos(i*math.tau/240),ry*math.sin(i*math.tau/240),z) for i in range(240)],r,mat,c,True)
def ribbon(name,rows,mat,c='02',N=240):
    vs=[]
    for rx,ry,z in rows:
        for i in range(N):
            a=math.tau*i/N;zz=z(a) if callable(z) else z;vs.append((rx*math.cos(a),ry*math.sin(a),zz))
    fs=[]
    for j in range(len(rows)-1):
        for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
    return mesh(name,vs,fs,mat,c)
# Venue: short axis X, long axis Y. Fixed seat counts intentionally approximate.
box('广场基座',(0,0,-1.1),(365,395,2),M['concrete'],'02')
mesh('内场保护地板',[(75*math.cos(i*math.tau/180),106*math.sin(i*math.tau/180),0) for i in range(180)],[tuple(range(180))],M['floor'],'02')
tiers=[(76,106,1.2,23,.9,.54),(99,128,17,16,1.02,.65),(119,144,30.5,19,1.1,.81)]
seatB=[Batch('看台座椅_红',M['red'],'02'),Batch('看台座椅_灰白',M['white'],'02')]
crowdB=[Batch('观众衣着_'+str(i),material('观众织物_'+str(i),col), '07') for i,col in enumerate([(.012,.02,.034),(.07,.09,.12),(.17,.18,.2),(.3,.29,.27),(.08,.12,.19)])]
heads=Batch('观众头部_远景',M['skin'],'07');phones=Batch('全场手机星光',M['phone'],'07')
seatcount=0
for tier,(rx,ry,z,n,step,rise) in enumerate(tiers):
    rows=[]
    for j in range(n):
        rows.extend([(rx+j*step,ry+j*step,z+j*rise),(rx+(j+1)*step,ry+(j+1)*step,z+j*rise)])
    ribbon('三层看台_层'+str(tier+1),rows,M['concrete'])
    oval('看台栏杆_'+str(tier),rx,ry,z+1.15,.075,M['steel'])
    for j in range(n):
        ax,ay=rx+(j+.5)*step,ry+(j+.5)*step;zz=z+j*rise
        count=int(math.tau*((ax+ay)/2)/.65)
        for k in range(count):
            a=math.tau*k/count
            if (a%(math.tau/40)) < .021:continue
            x,y=ax*math.cos(a),ay*math.sin(a)
            angle=a+math.pi/2
            b=seatB[1 if random.random()<.15 else 0];b.box((x,y,zz+.43),(.46,.42,.12),angle);b.box((x+.2*math.cos(a),y+.2*math.sin(a),zz+.72),(.46,.09,.48),angle)
            seatcount+=1
            if y<53 or abs(x)>63:
                if random.random()<.68:
                    crowdB[random.randrange(5)].box((x,y,zz+.93),(.39,.3,.60),angle);heads.oct((x,y,zz+1.39),.12)
                if random.random()<.18:phones.oct((x,y,zz+1.6+random.random()*.4),random.uniform(.035,.065))
    oval('层间包厢灯带_'+str(tier),rx-1,ry-1,z-.8,.09,M['warm'])
    ribbon('看台层间前檐_'+str(tier),[(rx-.2,ry-.2,z-1.3),(rx-.2,ry-.2,z-.2)],M['dark'])
for b in seatB:b.finish()
# Roof / woven rectangular steel ribbons; an approximation of the real saddle shell.
def roofZ(a):return 54.6+14.6*math.cos(2*a)
ribbon('PTFE马鞍形屋面',[(62,91,lambda a:roofZ(a)-2),(91,116,lambda a:roofZ(a)),(148,166.5,roofZ)],M['membrane'])
for rx,ry in [(62,91),(148,166.5)]:
    line('屋面边环',[(rx*math.cos(a),ry*math.sin(a),roofZ(a)) for a in [i*math.tau/240 for i in range(240)]],.55,M['steel'],'01',True)
for i in range(24):
    a=i*math.tau/24
    top=(146*math.cos(a),164*math.sin(a),roofZ(a))
    for da in [-.047,.047]:
        beam('主桁架柱_%02d'%i,(137*math.cos(a+da),155*math.sin(a+da),0),top,1.45,1.2,M['steel'])
    inside=(62*math.cos(a+.06),91*math.sin(a+.06),roofZ(a+.06)-2)
    beam('屋面主梁_%02d'%i,top,inside,1.2,1.3,M['steel'])
for family,sgn in enumerate([-1,1]):
    for i in range(64):
        a=i*math.tau/64;pts=[]
        for j in range(7):
            t=j/6;aa=a+sgn*.38*t+.035*math.sin(t*math.pi*2+i)
            pts.append(((137+11*t)*math.cos(aa),(155+11.5*t)*math.sin(aa),roofZ(aa)*t))
        for j in range(6):beam('交织钢带_%d_%02d_%d'%(family,i,j),pts[j],pts[j+1],.67,.48,M['steel'])
    for i in range(42):
        a=i*math.tau/42;pts=[]
        for j in range(7):
            t=j/6;aa=a+sgn*.50*t
            pts.append(((148-86*t)*math.cos(aa),(166.5-75.5*t)*math.sin(aa),roofZ(aa)+(1-t)*.5-2*t))
        for j in range(6):beam('屋面交织带_%d_%02d_%d'%(family,i,j),pts[j],pts[j+1],.52,.45,M['steel'])
# Stage footprint and the shallow centre thrust visible in reference 18.
outline=[(-58,68),(-58,54),(-20,54),(-14,48),(14,48),(20,54),(58,54),(58,68)]
vs=[(x,y,z) for z in [.15,2.2] for x,y in outline];N=len(outline)
fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('主舞台_浅前凸地台',vs,fs,M['dark'])
line('连续暖白舞台边沿',[(x,y,2.26) for x,y in outline[1:7]],.09,M['warm'])
for j in range(4):box('乐队阶梯_'+str(j),(0,60+j*1.35,2.5+j*.45),(41,1.4,.45),M['dark'])
for side in [-1,1]:
    for j in range(5):box('侧台楼梯',(side*58,54+j*.45,.23+j*.44),(2,.48,.44),M['dark'])
def screen(name,x0,x1,y0,z0,z1,mat,curve=0,c='04'):
    vs=[];uv=[];N=40
    for i in range(N+1):
        u=i/N;x=x0+(x1-x0)*u;y=y0+curve*(1-(2*u-1)**2)
        vs.extend([(x,y,z0),(x,y,z1)]);uv.extend([(u,0),(u,1)])
    fs=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(N)]
    o=mesh(name,vs,fs,mat,c,uv);o['source']='ACME 2026-09-15, image 17';o['estimated_dimensions_m']=[x1-x0,z1-z0];return o
screen('LED_中央弧形_可替换贴图',-25,25,67,9,30,LED[1],3.4)
screen('LED_左翼',-58,-25.5,64.5,9,30,LED[0],.8)
screen('LED_右翼',25.5,58,64.5,9,30,LED[2],.8)
for x0,x1 in [(-58,-23),(23,58)]:screen('旧墙侧翼',x0,x1,64.1,2.2,9,WALL,0,'03')
screen('旧墙中央背景',-23,23,68,4,9,WALL,0,'03')
# Suspended irregular envelope / kite, traced from photograph. No generic rectangle.
ep=[(-10.2,64,31.5),(-8.2,68,39),(10.3,67,38),(8.8,63,32.2)]
mesh('悬挂信封_真实轮廓',ep,[(0,1,2,3)],ENV,'03',[(0,0),(0,1),(1,1),(1,0)])
line('信封厚框',ep,.26,M['steel'],'03',True)
centre=(.1,63.1,35.2)
for i in range(4):line('信封折线_'+str(i),[ep[i],centre],.13,M['white'],'03')
for x in [-8,8]:line('信封吊索',[(x,67,38.5),(x,69,43)],.035,M['dark'])
# Scaffolding, three splayed lighting ladders each side, line-array stacks.
for x in [-59,-25,25,59]:
    for yy in [68,71]:
        for dx in [-.65,.65]:beam('舞台支撑塔',(x+dx,yy,0),(x+dx,yy,42),.18,.18,M['dark'],'05')
    for z in range(1,42,2):
        beam('塔架交叉撑',(x-.65,68,z),(x+.65,68,z+2),.09,.09,M['steel'],'05')
        beam('塔架横撑',(x-.65,68,z),(x+.65,68,z),.08,.08,M['steel'],'05')
for z in [31.7,41.5]:
    for y in [68,71]:beam('后部横向桁架',(-60,y,z),(60,y,z),.22,.22,M['dark'],'05')
    for x in range(-60,60,3):beam('桁架斜撑',(x,68,z),(x+3,71,z),.11,.11,M['dark'],'05')
for x in [-54,-25,25,54]:
    for k in range(12):
        o=box('吊挂线阵音箱',(x,61.7-.018*k*k,30.8-.63*k),(1.65,1.25,.59),M['black'],'05');o.rotation_euler.x=-.018*k
        box('音箱格栅',(x,61.03-.018*k*k,30.8-.63*k),(1.47,.04,.43),M['chair'],'05')
fixtures=Batch('上方三排矩阵灯',M['amber'],'05')
for side in [-1,1]:
    for row in range(3):
        pts=[]
        for i in range(31):
            x=side*(13+i*1.47);z=32+row*2.35+(.9-row*.35)*(i/30)
            pts.append((x,64,z));fixtures.box((x,63.6,z),(.43,.18,.35))
        line('斜向灯具吊杆',pts,.14,M['dark'])
fixtures.finish()
for i in range(100):
    x=-57+i*114/99;y=53.5 if abs(x)>20 else (47.6 if abs(x)<14 else 47.6+(abs(x)-14))
    box('前沿线性脚光',(x,y,2.48),(.77,.22,.18),M['amber'],'05')
for x in range(-48,49,4):
    box('摇头灯底座',(x,53.8,2.5),(.65,.6,.28),M['black'],'05')
    box('摇头灯灯体',(x,53.8,2.94),(.42,.48,.50),M['dark'],'05')
    box('脚灯发光面',(x,53.5,3),(.29,.05,.29),M['warm'],'05')
# Stained-colour NO SIGNAL lettering on the scenic wall, like reference 17.
for i,ch in enumerate('NO SIGNAL'):
    cv=bpy.data.curves.new('景片字_'+ch,'FONT');cv.body=ch;cv.size=4.6;cv.extrude=.035
    o=link(bpy.data.objects.new('NO SIGNAL_'+str(i),cv),'03');o.location=(-18+i*4.1,67.6,4.2);o.rotation_euler=(math.pi/2,0,0)
    cv.materials.append(material('彩色玻璃字_'+str(i),[(.9,.15,.04),(.03,.43,.7),(.8,.61,.06),(.03,.5,.27)][i%4],.4,0,.3))
# Match visible edge gaps rather than origins: I is much narrower than G/N/A.
bpy.context.view_layer.update()
signal_letters=[bpy.data.objects['NO SIGNAL_'+str(i)] for i in range(3,9)]
signal_edges=[(min((o.matrix_world@Vector(v)).x for v in o.bound_box),max((o.matrix_world@Vector(v)).x for v in o.bound_box)) for o in signal_letters]
signal_gap=(signal_edges[-1][1]-signal_edges[0][0]-sum(b-a for a,b in signal_edges))/5
signal_cursor=signal_edges[0][0]
for o,(a,b) in zip(signal_letters,signal_edges):
    o.location.x+=signal_cursor-a
    signal_cursor+=b-a+signal_gap
bpy.context.view_layer.update()
# Field seating, 15 rectangular blocks with longitudinal and transverse aisles.
chseat=Batch('内场折叠椅_座与靠背',M['chair'],'06');chlegs=Batch('内场折叠椅_金属椅腿',M['steel'],'06')
fieldcount=0
for blocky in range(3):
    for blockx in range(5):
        for row in range(29):
            y=38-blocky*40-row*1.12
            for k in range(26):
                x=-55+blockx*23+k*.71
                if (x/71)**2+(y/104)**2>.94:continue
                chseat.box((x,y,.46),(.45,.43,.07));chseat.box((x,y-.22,.77),(.45,.06,.52))
                for xx in [-.18,.18]:
                    chlegs.box((x+xx,y-.15,.25),(.026,.027,.5));chlegs.box((x+xx,y+.15,.25),(.026,.027,.5))
                fieldcount+=1
                if random.random()<.87:
                    crowdB[random.randrange(5)].box((x,y,1.08),(.39,.32,.67));heads.oct((x,y,1.62),.13)
                if random.random()<.35:phones.oct((x+.15,y+.12,1.7+random.random()*.38),.045)
chseat.finish();chlegs.finish()
for b in crowdB:b.finish()
heads.finish();phones.finish()
# Field barriers and FOH island, all independent of stadium seating bowl.
for x in [-35,-12,11,34]:
    line('内场纵向护栏',[(x,39,.95),(x,-80,.95)],.045,M['steel'],'06')
    for y in range(-80,40,4):line('护栏立柱',[(x,y,.05),(x,y,.95)],.04,M['steel'],'06')
for y in [-.4,-40.4]:
    line('横向通道护栏',[(-59,y,.95),(59,y,.95)],.045,M['steel'],'06')
box('调音台控制平台',(0,-46,.45),(8,6,.9),M['dark'],'06')
box('FOH棚顶',(0,-46,3.1),(8,6,.2),M['black'],'06')
for x in [-3.7,3.7]:
    for y in [-48.7,-43.3]:line('FOH棚柱',[(x,y,.5),(x,y,3.1)],.065,M['steel'],'06')
# Editable low-poly performance props and scale figure; no facial likeness claim.
def ellipsoid(name,p,scale,mat,c='08',seg=14,rings=8):
    vs=[]
    for j in range(rings+1):
        phi=math.pi*j/rings
        for i in range(seg):
            a=math.tau*i/seg;vs.append((p[0]+scale[0]*math.sin(phi)*math.cos(a),p[1]+scale[1]*math.sin(phi)*math.sin(a),p[2]+scale[2]*math.cos(phi)))
    fs=[(j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i) for j in range(rings) for i in range(seg)]
    o=mesh(name,vs,fs,mat,c)
    for f in o.data.polygons:f.use_smooth=True
    return o
def person(name,x,y,z,blue=False):
    cloth=M['blue'] if blue else M['black']
    ellipsoid(name+'_上衣',(x,y,z+1.20),(.26,.17,.34),cloth)
    ellipsoid(name+'_头',(x,y,z+1.70),(.125,.13,.16),M['skin'])
    for side in [-1,1]:
        box(name+'_黑短裤',(x+side*.12,y,z+.79),(.19,.25,.35),M['black'],'08')
        beam(name+'_腿',(x+side*.12,y,z+.66),(x+side*.15,y-.025,z+.12),.095,.11,M['skin'],'08')
        box(name+'_鞋',(x+side*.15,y-.06,z+.07),(.17,.32,.14),M['white'],'08')
        beam(name+'_手臂',(x+side*.26,y,z+1.40),(x+side*.37,y-.22,z+1.01),.13,.13,cloth,'08')
    ellipsoid(name+'_帽子',(x,y,z+1.84),(.15,.15,.08),M['black'])
    box(name+'_帽檐',(x,y-.16,z+1.81),(.29,.17,.035),M['black'],'08')
person('赵雷_蓝卫衣黑短裤',0,50.4,2.2,True)
ellipsoid('木吉他_下琴身',(-.11,50.12,3.23),(.23,.075,.27),M['wood'])
ellipsoid('木吉他_上琴身',(.05,50.12,3.48),(.17,.07,.19),M['wood'])
ellipsoid('吉他音孔',(-.03,50.038,3.38),(.075,.008,.075),M['black'])
beam('吉他琴颈',(.12,50.1,3.53),(.66,50.12,3.96),.07,.035,M['wood'],'08')
for i in range(6):line('吉他弦',[(-.1+i*.007,50.025,3.16),(.65+i*.007,50.08,3.95)],.0013,M['steel'],'08')
line('话筒立杆',[(0,49.8,2.2),(0,49.8,3.7),(.05,50.13,3.83)],.015,M['steel'],'08')
for a in [0,2.094,4.188]:line('话筒三脚',[(0,49.8,2.25),(.3*math.cos(a),49.8+.3*math.sin(a),2.21)],.015,M['black'],'08')
for x,y in [(-13,58),(-8,60),(8,60),(14,58),(-18,63),(18,63),(-4,64),(4,64)]:person('乐手',x,y,2.7+(y-58)*.22)
for x,y in [(-12,58),(12,58)]:
    box('键盘',(x,y,3.65),(2.2,.6,.19),M['black'],'08')
    for i in range(35):box('琴键',(x-1+i*.058,y-.2,3.77),(.052,.2,.04),M['white'],'08')
    for side in [-1,1]:beam('键盘X架',(x+side*.8,y,2.3),(x-side*.8,y,3.6),.04,.04,M['steel'],'08')
for x,y,z,r in [(-1,62,3.3,.65),(-2,62,3.9,.32),(0,62,3.9,.34),(1,62,3.5,.42)]:
    ellipsoid('鼓组',(x,y,z),(r,.35,r),M['dark']);ellipsoid('鼓皮',(x,y-.35,z),(r*.92,.02,r*.92),M['white'])
for x,y in [(-2.5,61),(1.8,61.8),(-.5,63)]:
    line('镲片支架',[(x,y,2.5),(x,y,4.5)],.025,M['steel'],'08');ellipsoid('金属镲',(x,y,4.5),(.5,.5,.035),M['wood'])
for x in [-16,-8,8,16]:
    o=box('楔形返听音箱',(x,53.5,2.5),(1.1,.7,.48),M['black'],'08');o.rotation_euler.x=.3
# Memorial chair: requested by source brief, exact location/flowers remain unverified.
mx,my=-2.2,41.7
box('纪念空座_座面',(mx,my,.47),(.48,.48,.08),M['chair'],'09');box('纪念空座_椅背',(mx,my-.22,.80),(.48,.07,.55),M['chair'],'09')
for dx in [-.19,.19]:
    for dy in [-.18,.18]:beam('纪念空座_椅腿',(mx+dx,my+dy,.03),(mx+dx,my+dy,.47),.025,.025,M['steel'],'09')
for j in range(11):
    a=j*2.4;x=mx+.15*math.cos(a);y=my+.13*math.sin(a)
    line('花束花茎',[(mx,my,.52),(x,y,.78+random.random()*.12)],.008,M['green'],'09')
    for k in range(5):ellipsoid('花束花瓣',(x+.043*math.cos(k*math.tau/5),y+.043*math.sin(k*math.tau/5),.87),(.04,.025,.018),M['petal'],'09',8,4)
# Lighting.
world=bpy.data.worlds.new('鸟巢夜空');S.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.055,.075,.13,1);bg.inputs['Strength'].default_value=.22
def light(name,kind,p,target,color,power,size=1):
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
    if kind=='AREA':d.shape='DISK';d.size=size
    if kind=='SPOT':d.spot_size=math.radians(size);d.spot_blend=.45;d.shadow_soft_size=.12
    o=link(bpy.data.objects.new(name,d),'10');o.location=p;o.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler();return o
light('夜间环境填光','AREA',(0,-20,115),(0,10,0),(.32,.47,.75),14000,140)
light('舞台暖色面光','AREA',(0,35,27),(0,61,4),(1,.60,.28),16000,45)
for x in [-40,0,40]:light('LED反射补光','AREA',(x,62,20),(x,0,4),(.32,.55,1),4800,24)
for x in [-48,-32,-16,0,16,32,48]:
    light('旧墙洗墙灯','AREA',(x,61,3.4),(x,66,8),(1,.32,.065),3500,7)
for i in range(24):
    a=i*math.tau/24;p=(132*math.cos(a),151*math.sin(a),46)
    light('鸟巢环廊暖光','AREA',p,(p[0]*1.04,p[1]*1.04,60),(1,.36,.09),2600,12)
for side in [-1,1]:
    for i in range(10):
        x=side*(15+i*4.4);p=(x,62,34+(i%3)*2.1);target=(x*.55-22*side,-8+i*4,3)
        light('舞台交叉追光','SPOT',p,target,(.55,.72,1),85000,8)
for x in [-8,8]:light('艺人面光','SPOT',(x,44,20),(0,50.5,3),(1,.78,.48),7000,16)
# Thin atmospheric volume for actual spot beams.
fog=bpy.data.materials.new('舞台薄雾');fog.use_nodes=True;fog.node_tree.nodes.clear()
out=fog.node_tree.nodes.new('ShaderNodeOutputMaterial');vol=fog.node_tree.nodes.new('ShaderNodeVolumePrincipled')
vol.inputs['Density'].default_value=.0014;vol.inputs['Color'].default_value=(.50,.58,.70,1);vol.inputs['Anisotropy'].default_value=.35
fog.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume']);box('灯束薄雾范围',(0,20,21),(130,135,43),fog,'10')
# Four purposeful cameras.
def camera(name,p,target,lens):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_end=1500;o=link(bpy.data.objects.new(name,d),'11');o.location=p;o.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler();return o
cam=camera('CAM_01_现场正面全景',(0,-93,27),(0,61,19),38)
camera('CAM_02_看台斜向全景',(91,-92,50),(0,40,19),40)
camera('CAM_03_鸟巢建筑鸟瞰',(258,-290,238),(0,0,23),48)
camera('CAM_04_舞台近景',(28,6,12),(0,61,17),32)
camera('CAM_05_纪念空座',(-.55,38.6,1.7),(mx,my,.7),52)
S.camera=cam;S.render.engine='BLENDER_EEVEE';S.render.resolution_x=1500;S.render.resolution_y=950;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(ROOT/'renders'/'01_stage.png');S.render.film_transparent=False
S.view_settings.exposure=0
S.eevee.use_volume_custom_range=True;S.eevee.volumetric_start=.1;S.eevee.volumetric_end=400
S.eevee.taa_render_samples=64;S.eevee.volumetric_samples=64
# Reference images remain packed, available in the image editor without affecting renders.
for fn in ['acme_00.jpg','acme_16.jpg','acme_17.jpg','acme_18.jpg','contact_sheet.jpg']:
    im=bpy.data.images.load(str(ROOT/'references'/fn),check_existing=True);im.pack()
S['建模依据']='本地MD + ACME现场照片00/16/17/18；场馆官方尺寸333×296×69.21m'
S['准确性说明']='场馆总体尺寸有来源；舞台米数、座椅数、桁架工程细部为照片估算；人物为比例示意；纪念空座按MD要求设置，位置未核验。'
S['seating_approximation_count']=seatcount;S['field_chair_count']=fieldcount
S['photo_source']='https://www.acmelighting.com/Info/detail/cat_id/29/id/11825'
for screenarea in bpy.context.screen.areas:
    if screenarea.type=='VIEW_3D':
        screenarea.spaces.active.clip_end=2000
        screenarea.spaces.active.region_3d.view_perspective='CAMERA'
        screenarea.spaces.active.overlay.show_overlays=False
ROOT.joinpath('renders').mkdir(exist_ok=True)
notes=bpy.data.texts.new('README_建模依据与使用说明');notes.write('赵雷2026 没有信号 鸟巢复刻\n真实照片参考：ACME案例，2026-09-15。\n主屏、侧屏、信封贴图来自公开现场照片，已打包。照片版权属于原权利人。\n切换CAM_01~05查看现场、斜向、建筑、舞台与空座。\n舞台尺寸与观众数量为视觉复原估算，不是施工或座位图。人物不含写实面部。\n默认原场景保留，新场景分12个集合。\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_没有信号_鸟巢.blend'))
print(json.dumps({'objects':len(S.objects),'stadium_seats':seatcount,'field_chairs':fieldcount,'blend':str(ROOT/'赵雷2026_没有信号_鸟巢.blend')},ensure_ascii=False))
