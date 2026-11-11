"""Editable backline study from ACME concert photos 07 and 20; dimensions/layout estimated."""
import bpy, math, ast, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene
assert S.get('detail_v4') and not S.get('band_v5')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
helpers=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children};C=bpy.data.collections.new('20_实拍乐队与打击乐细化');S.collection.children.link(C);COL['20']=C
black=bpy.data.materials['black'];steel=bpy.data.materials['steel'];skin=bpy.data.materials['skin'];white=bpy.data.materials['white']
bronze=material('BN5_青铜锣',(.47,.28,.09),.48,.72)
resonator=material('BN5_共鸣管',(.30,.19,.09),.45,.45)
wood=material('BN5_深棕琴条',(.14,.055,.025),.53,0)
cloth=material('BN5_演奏服',(.016,.021,.029),.9,0)
hair=material('BN5_深色头发',(.024,.018,.014),.9,0)
paper=material('BN5_谱纸',(.62,.60,.52),.85,0)
def b(name,p,d,mat=black,bev=0):
    o=box(name,p,d,mat,'20')
    if bev:
        mod=o.modifiers.new('边缘倒角','BEVEL');mod.width=bev;mod.segments=2;mod.limit_method='ANGLE'
    return o
def tube(name,p,q,r,mat=steel,segments=12):
    p,q=Vector(p),Vector(q);axis=(q-p).normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.01:u=Vector((1,0,0))
    u.normalize();v=axis.cross(u);vs=[]
    for ctr in [p,q]:
        for k in range(segments):vs.append(tuple(ctr+r*(u*math.cos(k*math.tau/segments)+v*math.sin(k*math.tau/segments))))
    fs=[(k,(k+1)%segments,(k+1)%segments+segments,k+segments) for k in range(segments)]
    fs += [tuple(range(segments-1,-1,-1)),tuple(range(segments,2*segments))]
    o=mesh(name,vs,fs,mat,'20')
    for f in o.data.polygons[:segments]:f.use_smooth=True
    return o
def sphere(name,p,s,mat,seg=12,rings=6):return ellipsoid(name,p,s,mat,'20',seg,rings)
def stand(name,x,y,z,holes=False):
    tube(name+'_立柱',(x,y,z+.04),(x,y,z+1.10),.018,black)
    for a in [0,math.tau/3,math.tau*2/3]:tube(name+'_三脚',(x,y,z+.18),(x+.27*math.cos(a),y+.27*math.sin(a),z+.025),.013,black,8)
    # A tilted plate with true perforations; the music light and lip remain separate editable pieces.
    origin=Vector((x,y,z+1.18));tilt=math.radians(-17)
    def at(xx,zz,depth=0):return tuple(origin+Vector((xx,depth*math.cos(tilt)-zz*math.sin(tilt),depth*math.sin(tilt)+zz*math.cos(tilt))))
    if holes:
        vs=[];fs=[];nx,nz=9,5;cell=.059
        for j in range(nz):
            for i in range(nx):
                cx=(i-(nx-1)/2)*cell;cz=(j-(nz-1)/2)*cell
                start=len(vs)
                for dep in [-.004,.004]:
                    for ring in [False,True]:
                        for k in range(8):
                            a=k*math.tau/8;rr=.012 if ring else cell*.5/max(abs(math.cos(a)),abs(math.sin(a)))
                            vs.append(at(cx+rr*math.cos(a),cz+rr*math.sin(a),dep))
                for k in range(8):
                    n=(k+1)%8
                    for f in [(k,n,8+n,8+k),(16+k,24+k,24+n,16+n),(8+k,8+n,24+n,24+k)]:fs.append(tuple(start+t for t in f))
        mesh(name+'_打孔谱盘',vs,fs,black,'20')
    else:
        plate=b(name+'_谱盘',origin,(.54,.012,.34),black,.007);plate.rotation_euler.x=tilt
        for side in [-1,1]:
            page=b(name+'_谱纸',at(side*.12,0,-.01),(.225,.002,.28),paper);page.rotation_euler.x=tilt
            for staff in range(4):
                for k in range(5):
                    pos=at(side*.12,.10-staff*.062-k*.008,-.012)
                    ink=b(name+'_谱线',pos,(.19,.001,.0015),black);ink.rotation_euler.x=tilt
    lip=b(name+'_托边',at(0,-.16,-.025),(.56,.045,.018),black,.004);lip.rotation_euler.x=tilt
    tube(name+'_灯臂',(x+.18,y+.04,z+1.30),(x+.18,y-.04,z+1.43),.006,black,8)
    b(name+'_谱灯',(x+.10,y-.04,z+1.43),(.17,.035,.025),black,.005)

# Rear riser joins the existing top step (top elevation 4.075 m).
base=4.075
b('后排乐队延伸台',(0,65.65,base-.225),(40,2.8,.45),black)
for x in [-19.5,-10,0,10,19.5]:b('后排地台侧向支撑',(x,65.6,3.1),(.08,2.5,1.5),black)

# Marimba-like keyboard percussion, recognised by the resonator bank in the close photograph.
mx,my=-5.3,65.4
for x in [mx-1.25,mx+1.25]:
    tube('键盘打击乐支腿',(x,my-.32,base+.1),(x,my-.32,base+.9),.035,black)
    tube('键盘打击乐支腿',(x,my+.32,base+.1),(x,my+.32,base+.9),.035,black)
    tube('键盘打击乐脚架',(x,my-.48,base+.1),(x,my+.48,base+.1),.035,black)
    for y in [my-.4,my+.4]:sphere('脚轮',(x,y,base+.055),(.065,.035,.055),black)
for y in [my-.36,my+.36]:b('木琴主框',(mx,y,base+.91),(2.9,.075,.12),wood,.015)
for i in range(30):
    x=mx-1.36+i*.094;length=.7-i*.008
    b('自然音琴条_%02d'%i,(x,my-.08,base+1.01),(.086,length,.045),wood,.008)
    tube('共鸣管_%02d'%i,(x,my-.08,base+.96),(x,my-.08,base+.15+i*.017),.035,resonator,12)
    if i%7 not in [2,6]:
        b('变化音琴条_%02d'%i,(x+.044,my+.29,base+1.065),(.081,length*.70,.045),wood,.008)
        tube('短共鸣管_%02d'%i,(x+.044,my+.29,base+1.0),(x+.044,my+.29,base+.30+i*.013),.03,resonator,10)
for dx in [-.15,.12]:
    tube('琴槌',(mx+dx,my,base+1.06),(mx+dx+.20,my-.23,base+1.08),.008,wood,8)
    sphere('琴槌头',(mx+dx+.20,my-.23,base+1.08),(.035,.035,.035),white)

# Suspended gong: shallow concentric profile and dark rim, not a flat billboard.
gx,gy,gz=-3.25,66.25,base+1.52
for side in [-1,1]:
    tube('大锣架立柱',(gx+side*.83,gy,base+.08),(gx+side*.83,gy,base+2.38),.031,black)
    tube('大锣架脚',(gx+side*.83,gy-.42,base+.065),(gx+side*.83,gy+.42,base+.065),.031,black)
tube('大锣架横梁',(gx-.83,gy,base+2.38),(gx+.83,gy,base+2.38),.035,black)
profile=[(.015,-.12),(.12,-.12),(.22,-.06),(.45,-.025),(.64,.005),(.69,.035),(.70,.07)]
vs=[];fs=[];segments=80
for r,depth in profile:
    for k in range(segments):
        a=k*math.tau/segments;ripple=.0015*math.sin(k*7+r*39)
        vs.append((gx+r*math.cos(a),gy+depth+ripple,gz+r*math.sin(a)))
for j in range(len(profile)-1):
    for k in range(segments):fs.append((j*segments+k,j*segments+(k+1)%segments,(j+1)*segments+(k+1)%segments,(j+1)*segments+k))
fs.append(tuple(range(segments-1,-1,-1)))
gong=mesh('青铜大锣_同心曲面',vs,fs,bronze,'20');solid=gong.modifiers.new('锣体厚度','SOLIDIFY');solid.thickness=.008
for f in gong.data.polygons:f.use_smooth=True
line('大锣深色外缘',[(gx+.70*math.cos(k*math.tau/80),gy+.072,gz+.70*math.sin(k*math.tau/80)) for k in range(80)],.018,black,'20',True)
for dx in [-.25,.25]:line('大锣悬绳',[(gx+dx,gy,gz+.65),(gx+dx,gy,base+2.35)],.007,black,'20')
stand('打击乐谱架左',mx-.7,64.83,base,True);stand('打击乐谱架右',mx+.7,64.83,base,True)

# Seated ensemble silhouettes use rounded shoulders and bent limbs. Counts and positions are estimates.
for idx,x in enumerate([-17,-14,-11,7,10,13,16]):
    y=65.6
    b('乐手椅座',(x,y,base+.46),(.45,.43,.07),black,.025)
    back=b('乐手椅背',(x,y+.22,base+.78),(.46,.055,.43),black,.035);back.rotation_euler.x=-.10
    for dx in [-.18,.18]:
        for dy in [-.17,.17]:tube('折叠椅管架',(x+dx,y+dy,base+.03),(x+dx,y-dy,base+.48),.015,steel,8)
    sphere('后排乐手上衣',(x,y,base+.96),(.23,.16,.34),cloth)
    sphere('后排乐手头部',(x,y-.015,base+1.43),(.115,.12,.15),skin)
    sphere('后排乐手发型',(x,y+.012,base+1.51),(.123,.123,.10),hair)
    for side in [-1,1]:
        tube('演奏裤腿上段',(x+side*.11,y,base+.59),(x+side*.14,y-.34,base+.50),.085,cloth,10)
        tube('演奏裤腿下段',(x+side*.14,y-.34,base+.50),(x+side*.15,y-.39,base+.10),.067,cloth,10)
        sphere('演奏皮鞋',(x+side*.15,y-.46,base+.07),(.08,.15,.065),black)
    # Violin/cello silhouettes; not portraits of any particular orchestra member.
    cello=idx in [0,6]
    if cello:
        sphere('大提琴下琴身',(x,y-.38,base+.53),(.23,.10,.30),wood)
        sphere('大提琴上琴身',(x,y-.38,base+.86),(.17,.095,.19),wood)
        tube('大提琴琴颈',(x,y-.38,base+.99),(x+.06,y-.37,base+1.50),.026,black,8)
        tube('大提琴尾柱',(x,y-.38,base+.04),(x,y-.38,base+.29),.009,steel,8)
    else:
        sphere('小提琴琴身',(x-.10,y-.26,base+1.18),(.18,.07,.10),wood)
        tube('小提琴琴颈',(x-.20,y-.26,base+1.19),(x-.47,y-.25,base+1.23),.023,black,8)
    for side in [-1,1]:
        elbow=(x+side*.29,y-.10,base+.94);hand=(x+side*.22,y-.29,base+1.16)
        tube('演奏上臂',(x+side*.20,y,base+1.15),elbow,.065,cloth,10)
        tube('演奏前臂',elbow,hand,.052,cloth,10);sphere('演奏手',hand,(.045,.048,.05),skin)
    tube('弓杆',(x-.35,y-.34,base+1.02),(x+.32,y-.31,base+1.32),.006,wood,8)
    stand('后排谱架_%02d'%idx,x,64.75,base)

# Boom microphones and laid cables at the percussion station.
for x,y in [(mx-1.5,65.0),(mx+1.3,65.0)]:
    tube('打击乐话筒柱',(x,y,base+.05),(x,y,base+1.65),.016,black)
    tube('打击乐话筒悬臂',(x,y,base+1.60),(x+.30,y+.22,base+1.5),.012,steel)
    tube('打击乐话筒',(x+.25,y+.18,base+1.5),(x+.43,y+.30,base+1.48),.022,black)
    for a in [0,2.094,4.188]:tube('话筒三脚',(x,y,base+.16),(x+.3*math.cos(a),y+.3*math.sin(a),base+.025),.012,black,8)
    line('打击乐音频线',[(x+.4,y+.3,base+1.48),(x,y,base+1.4),(x,y,base+.025),(x+.4,66.7,base+.025)],.006,black,'20')
def add_percussionist():
    x,y,z=-5.3,66.05,4.075
    sphere('打击乐手上衣',(x,y,z+1.15),(.25,.18,.36),cloth)
    sphere('打击乐手头部',(x,y-.03,z+1.67),(.12,.125,.155),skin)
    sphere('打击乐手帽沿',(x,y-.02,z+1.79),(.25,.22,.025),black,20,4)
    tube('打击乐手帽冠',(x,y,z+1.79),(x,y,z+1.94),.145,black,20)
    for side in [-1,1]:
        tube('打击乐手裤腿',(x+side*.12,y,z+.83),(x+side*.16,y,z+.12),.085,cloth,10)
        sphere('打击乐手鞋',(x+side*.16,y-.05,z+.07),(.08,.15,.065),black)
        elbow=(x+side*.34,y-.2,z+1.13);hand=(x+side*.32,y-.48,z+1.15)
        tube('打击乐手上臂',(x+side*.23,y,z+1.38),elbow,.065,cloth,10)
        tube('打击乐手前臂',elbow,hand,.054,cloth,10);sphere('打击乐手手',hand,(.045,.048,.05),skin)
        tip=(x+side*.22,y-.77,z+1.15)
        tube('手持琴槌',hand,tip,.007,wood,8);sphere('手持槌头',tip,(.03,.03,.03),white)
add_percussionist()
for prefix,p in [('VIEW_',(-8.6,61.1,6.4)),('LOOK_',(-5.3,65.2,5.2))]:
    o=link(bpy.data.objects.new(prefix+'13_BandDetail',None),'20');o.location=p
S['band_v5']=True;S['band_v5_note']='ACME photos 07/20: gong, keyboard percussion, perforated music stands and seated ensemble. Layout/dimensions are estimates; no individual likeness.'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        p=Vector((-8.6,61.1,6.4));t=Vector((-5.3,65.2,5.2));r=area.spaces.active.region_3d;r.view_location=t;r.view_distance=(t-p).length;r.view_rotation=(t-p).to_track_quat('-Z','Y');area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend'))
print('Band detail objects:',len(C.objects))
