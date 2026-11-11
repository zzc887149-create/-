"""Approved sketch C: unified seating modules, portal bands and access cores.
All dimensions/counts are reconstruction choices, not surveyed stadium data.
Run in the source Blender scene. The v19 file is retained for rollback.
"""
import bpy, math, json, bisect, random, ast, bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene; D=bpy.data.scenes['UNITY_ENHANCED_V3']
DEST=ROOT/'赵雷2026_鸟巢_上层扩席连通版.blend'
CHECK=ROOT/'unity_enhanced/checks'; PKG=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
N=24; PHASE=.03834; HALF=2.4
def progress(s):
    (CHECK/'v23_progress.txt').write_text(s,encoding='utf-8');print(s)
assert S.get('teleprompter_v19') and not S.get('seating_v23')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
# Remove obsolete routes as a unit; preserve stage, facade, exterior stairs and field chairs.
for c in list(S.collection.children):
    if c.name[:2] in ('22','23','24','26'):
        for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(S.objects):
    if o.name.startswith(('看台座椅_','看台栏杆_','看台层间前檐_','层间包厢灯带_')):
        bpy.data.objects.remove(o,do_unlink=True)
# Retain only the field components of old mixed crowd/phone meshes.
for o in list(S.objects):
    if o.type!='MESH' or not (any(c.name.startswith('07_') for c in o.users_collection) or o.name.startswith('NEAR_')):continue
    bm=bmesh.new();bm.from_mesh(o.data)
    drop=[v for v in bm.verts if (o.matrix_world@v.co).z>4 or ((o.matrix_world@v.co).x/75)**2+((o.matrix_world@v.co).y/106)**2>1]
    bmesh.ops.delete(bm,geom=drop,context='VERTS');bm.to_mesh(o.data);bm.free()
# Discard old exported seating and bowl-only detail; field detail is preserved and trimmed.
for o in list(D.objects):
    if o.name.startswith(('Chunk_SEATS_','LOD_Chunk_SEATS_')):
        bpy.data.objects.remove(o,do_unlink=True);continue
    if o.type=='MESH' and o.name.startswith(('Chunk_CROWD_','Chunk_PHONES_')):
        bm=bmesh.new();bm.from_mesh(o.data);drop=[v for v in bm.verts if (o.matrix_world@v.co).z>4 or ((o.matrix_world@v.co).x/75)**2+((o.matrix_world@v.co).y/106)**2>1]
        bmesh.ops.delete(bm,geom=drop,context='VERTS');bm.to_mesh(o.data);bm.free()

C=bpy.data.collections.new('27_草图C统一看台');S.collection.children.link(C)
M={n:bpy.data.materials[n] for n in ('concrete','red','white','skin','phone','栏杆细金属','楼梯红色防滑涂层')}
CF=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
CV=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
class Mesh:
    def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.f=[];self.colors=[]
    def prism(self,pts,top,bottom):
        ts=top if isinstance(top,list) else [top]*4;bs=bottom if isinstance(bottom,list) else [bottom]*4
        k=len(self.v);self.v.extend([(p[0],p[1],z) for p,z in zip(pts,bs)]+[(p[0],p[1],z) for p,z in zip(pts,ts)])
        self.f.extend(tuple(k+i for i in f) for f in CF)
    def box(self,p,size,a=0,color=None):
        k=len(self.v);ca,sa=math.cos(a),math.sin(a)
        for x,y,z in CV:
            x*=size[0];y*=size[1];self.v.append((p[0]+ca*x-sa*y,p[1]+sa*x+ca*y,p[2]+z*size[2]))
        self.f.extend(tuple(k+i for i in f) for f in CF)
        if color:self.colors.extend([color]*8)
    def oct(self,p,r,color=None):
        k=len(self.v);x,y,z=p;self.v.extend([(x+r,y,z),(x-r,y,z),(x,y+r,z),(x,y-r,z),(x,y,z+r),(x,y,z-r)])
        self.f.extend(tuple(k+i for i in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)])
        if color:self.colors.extend([color]*6)
    def finish(self,collection=C):
        if not self.f:return None
        me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.materials.append(self.mat);me.update()
        if self.colors:
            col=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
            for d,c in zip(col.data,self.colors):d.color=c
        else:
            uv=me.uv_layers.new(name='MetreUV')
            for f in me.polygons:
                axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
                for li in f.loop_indices:
                    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
        o=bpy.data.objects.new(self.name,me);collection.objects.link(o);return o
TIERS=[(76,106,23,.9),(99,128,16,1.02),(109.5,134.5,32,.72)]
tables={}
def table(t,r):
    key=(t,round(r,5))
    if key not in tables:
        rx,ry,_,_=TIERS[t];rx+=r;ry+=r;angles=[i*math.tau/2048 for i in range(2049)];ss=[0]
        for a,b in zip(angles,angles[1:]):ss.append(ss[-1]+math.hypot(rx*(math.cos(b)-math.cos(a)),ry*(math.sin(b)-math.sin(a))))
        tables[key]=(ss,angles,ss[-1])
    return tables[key]
def angle(t,r,u):
    ss,aa,L=table(t,r);d=(u%1)*L;i=min(bisect.bisect_right(ss,d)-1,len(ss)-2)
    return aa[i]+(aa[i+1]-aa[i])*(d-ss[i])/(ss[i+1]-ss[i])
def q(t,b,r,w=0,z=0):
    rx,ry,_,_=TIERS[t];a=angle(t,r,b/N+PHASE+w/table(t,r)[2]);return Vector(((rx+r)*math.cos(a),(ry+r)*math.sin(a),z))
def hraw(t,j,a):
    f=math.sin(a)**4
    if t==0:return 1.2+j*((15.0-1.2)/22)
    if t==1:return 17.8+min(j,9)*((22.5-17.8)/9)+max(0,j-9)*.12
    return 26.2+j*.26
def h(t,j,a):
    # Flat transfer landings at aisle axes; interpolate the seat terraces between them.
    if t==0:return hraw(t,j,a)
    r=(j+.5)*TIERS[t][3];ss,aa,L=table(t,r);a%=math.tau
    i=min(bisect.bisect_right(aa,a)-1,len(aa)-2);u=(ss[i]+(ss[i+1]-ss[i])*(a-aa[i])/(aa[i+1]-aa[i]))/L
    x=((u-PHASE)%1)*N;b=math.floor(x);f=x-b;f=max(0,min(1,(f-.13)/.74))
    a0=angle(t,r,b/N+PHASE);a1=angle(t,r,(b+1)/N+PHASE)
    return hraw(t,j,a0)*(1-f)+hraw(t,j,a1)*f
def H(t,j,b,w=0):
    r=(j+.5)*TIERS[t][3];a=angle(t,r,b/N+PHASE+w/table(t,r)[2]);return h(t,j,a)
def tile(mesh,t,b,r0,r1,w0,w1,top,thick=.22):
    pts=[q(t,b,r0,w0),q(t,b,r1,w0),q(t,b,r1,w1),q(t,b,r0,w1)]
    tops=[top(w0),top(w0),top(w1),top(w1)] if callable(top) else [top]*4
    mesh.prism(pts,tops,[z-thick for z in tops])
samples=[];segments=[];portals=[];cuts=[];counts=[]
def sample(p,kind,bay):samples.append({'kind':kind,'bay':bay,'point':list(p)})
def route(points,kind):
    for a,b in zip(points,points[1:]):segments.append({'kind':kind,'a':list(a+Vector((0,0,1.25))),'b':list(b+Vector((0,0,1.25)))})
def beam(mesh,a,b,width=.045):
    a,b=Vector(a),Vector(b);d=b-a;u=d.normalized();v=u.cross(Vector((0,0,1)))
    if v.length<.01:v=Vector((1,0,0))
    v.normalize();w=u.cross(v);k=len(mesh.v)
    for p in (a,b):
        for x,y in ((-1,-1),(1,-1),(1,1),(-1,1)):mesh.v.append(tuple(p+v*x*width/2+w*y*width/2))
    mesh.f.extend(tuple(k+i for i in f) for f in CF)
def track(mesh,points):
    for a,b in zip(points,points[1:]):beam(mesh,a+Vector((0,0,1.05)),b+Vector((0,0,1.05)))
    for p in points[::3]:beam(mesh,p,p+Vector((0,0,1.05)))
def passage(t,b,r0,r1,z0,z1,tag):
    """A straight-height or stepped tunnel with explicit enclosed sides and roof."""
    if r1<r0:r0,r1,z0,z1=r1,r0,z1,z0
    floor=Mesh('V23_通道_'+tag,M['concrete']);walls=Mesh('V23_围护_'+tag,M['concrete'])
    head=2.36 if t==2 else 2.5
    length=r1-r0;n=max(1,math.ceil(abs(z1-z0)/.16));run=n*.28 if n>1 else 0
    start=r1-run;path=[]
    def floorh(r):return z0 if r<start else z0+(z1-z0)*min(n,max(1,math.floor((r-start)/.28)+1))/n
    if start>r0:tile(floor,t,b,r0,start,-1.2,1.2,z0)
    for k in range(n if run else 0):tile(floor,t,b,start+k*.28,start+(k+1)*.28,-1.2,1.2,z0+(z1-z0)*(k+1)/n)
    # Single connected cutter per tunnel; only old architecture is cut by these volumes.
    cut=Mesh('V23_CUT_'+tag,M['concrete']);cut.prism([q(t,b,r0-.12,-1.23),q(t,b,r1+.15,-1.23),q(t,b,r1+.15,1.23),q(t,b,r0-.12,1.23)],max(z0,z1)+head,min(z0,z1)-.04);cuts.append(cut)
    for k in range(max(1,math.ceil(length/.4))):
        a=r0+k*length/math.ceil(length/.4);bb=r0+(k+1)*length/math.ceil(length/.4)
        zh=max(floorh(a+.001),floorh(bb-.001));low=min(floorh(a+.001),floorh(bb-.001))-.22
        for w in [-1.32,1.32]:
            wallend=23.1 if t==2 else r1
            seat_j=min(TIERS[t][2]-1,max(0,math.floor(a/TIERS[t][3])))
            embedded_top=min(zh+head,H(t,seat_j,b)) if a<TIERS[t][2]*TIERS[t][3] else zh+head
            if a<wallend and embedded_top>low:tile(walls,t,b,a,min(bb,wallend),w-.12,w+.12,embedded_top,embedded_top-low)
        seat_j=min(TIERS[t][2]-1,max(0,math.floor(a/TIERS[t][3])))
        if a>=TIERS[t][2]*TIERS[t][3] or H(t,seat_j,b)>=zh+head:
            tile(walls,t,b,a,bb,-1.44,1.44,zh+head,.18)
    ts=[r0+.04]
    if start>r0:ts.extend(r0+(start-r0)*i/max(1,math.ceil((start-r0)/.24)) for i in range(1,max(1,math.ceil((start-r0)/.24))))
    if run:ts.extend(start+(k+.5)*.28 for k in range(n))
    else:ts.extend(r0+length*i/max(1,math.ceil(length/.24)) for i in range(1,max(1,math.ceil(length/.24))))
    ts.append(r1-.02)
    for w in [-.7,0,.7]:
        path=[q(t,b,r,w,floorh(r)) for r in ts]
        for p in path:sample(p,tag,b)
        route(path,tag)
    floor.finish();walls.finish();return floorh

progress('Rebuilding three equal-arc seating tiers')
for t,(rx,ry,n,step) in enumerate(TIERS):
    solid=Mesh('V23_座席基座_'+str(t+1),M['concrete']);stairs=Mesh('V23_连续梯道_'+str(t+1),M['concrete']);rails=Mesh('V23_梯道扶手_'+str(t+1),M['栏杆细金属'])
    for j in range(n):
        r0=j*step;r1=(j+1)*step;L=table(t,(j+.5)*step)[2];width=L/N-2*HALF
        counts.append({'tier':t+1,'row':j,'module_width':L/N,'seat_width':width,'seats_per_block':int((width-.3)/.56)})
        for b in range(N):
            margin=HALF
            # Every block has identical arc length at this row, including end curves.
            for k in range(12):
                u0=(b+(margin/(L/N))+(1-2*margin/(L/N))*k/12)/N+PHASE
                u1=(b+(margin/(L/N))+(1-2*margin/(L/N))*(k+1)/12)/N+PHASE
                pts=[];tops=[]
                for r,u in ((r0,u0),(r1,u0),(r1,u1),(r0,u1)):
                    a=angle(t,r,u);pts.append(((rx+r)*math.cos(a),(ry+r)*math.sin(a)));tops.append(h(t,j,a))
                solid.prism(pts,tops,[z-.23 for z in tops])
            # Central aisle infill only where it is not the portal's open headroom.
            openhole=False
            if t==1 and j>=9 and H(t,j,b)<H(t,9,b)+2.7:openhole=True
            if t==2:
                if any(lo<=j<=hi for lo,hi in [(2,7),(11,16),(21,26)]):openhole=True
            if not openhole:tile(stairs,t,b,r0,r1,-1.2,1.2,lambda w:H(t,j,b,w))
    div=5
    for b in range(N):
        for side in [-1,1]:
            path=[]
            for k in range((n-1)*div+1):
                j=min(k//div,n-2);f=(k-j*div)/div;r=(.5+k/div)*step
                lo=0 if k==0 else r-step/div/2;hi=n*step if k==(n-1)*div else r+step/div/2
                def top(w):return H(t,j,b,w)*(1-f)+H(t,j+1,b,w)*f
                w0,w1=sorted((side*1.44,side*HALF));tile(stairs,t,b,lo,hi,w0,w1,top)
                for w in [side*1.72,side*2.12]:sample(q(t,b,r,w,top(w)),'tier%d_aisle'%(t+1),b)
                path.append(q(t,b,r,side*1.9,top(side*1.9)))
            route(path,'tier%d_aisle'%(t+1))
            guardpoints=[q(t,b,p_r,side*1.39,H(t,j,b,side*1.39)) for j,p_r in enumerate((j+.5)*step for j in range(n))]
            if t==2:
                for jj in range(len(guardpoints)-1):
                    if jj not in [1,2,10,11,20,21]:track(rails,guardpoints[jj:jj+2])
            else:track(rails,guardpoints)
            for j in range(n):
                r=(j+.5)*step
                # Flat side transfer pads at each row, meeting both stair and seat slab.
                a,bb=sorted((side*1.44,side*2.8))
                tile(stairs,t,b,r-.07,r+.07,a,bb,lambda w:H(t,j,b,w))
                pts=[q(t,b,r,side*w,H(t,j,b,side*w)) for w in (1.8,2.2,2.4,2.6)]
                for p in pts:sample(p,'tier%d_row_turn'%(t+1),b)
                route(pts,'tier%d_row_turn'%(t+1))
    old=S.objects.get('三层看台_层'+str(t+1));temp=solid.finish()
    if old:old.data=temp.data;bpy.data.objects.remove(temp,do_unlink=True)
    stairs.finish();rails.finish()

exec(compile((ROOT/'v23_access_geometry.py').read_text(encoding='utf-8'),'v23_access_geometry.py','exec'))

# Fascias are closed except for the approved upper bottom entrances.
for t,(rx,ry,n,step) in enumerate(TIERS):
    fascia=Mesh('V23_层间前檐_'+str(t+1),M['concrete']);rail=Mesh('V23_看台前护栏_'+str(t+1),M['栏杆细金属'])
    for b in range(N):
        L=table(t,0)[2]
        for k in range(20):
            w0=k*L/N/20;w1=(k+1)*L/N/20
            if t==2 and (w0<1.5 or w1>L/N-1.5):continue
            top=lambda w:H(t,0,b,w)-.04
            tile(fascia,t,b,-.22,0,w0,w1,top,.3 if t else 1.1)
        pts=[q(t,b,0,w,H(t,0,b,w)) for w in [HALF+(L/N-2*HALF)*i/16 for i in range(17)]]
        track(rail,pts)
    fascia.finish();rail.finish()

# Build occupancy and true lightweight detail LODs directly, sharing existing vertex palette.
progress('Populating equal-width blocks at 97 percent occupancy')
palette=bpy.data.materials['BNE_006'];record=json.loads((PKG/'materials.json').read_text(encoding='utf-8'))['materials']
phone_mat=bpy.data.materials[next(r['name'] for r in record if r['label']=='phone')]
root=D.objects['BirdsNest_Enhanced_360'];rng=random.Random(20261030);seat_total=0;people_total=0;newreports=[]
skin=[(.53,.30,.18,1),(.65,.42,.28,1),(.42,.26,.17,1)]
clothes=[(.012,.02,.034,1),(.07,.09,.12,1),(.17,.18,.2,1),(.3,.29,.27,1),(.08,.12,.19,1),(.45,.40,.34,1)]
for t,(rx,ry,n,step) in enumerate(TIERS):
    for b in range(N):
        builders={k:Mesh('Chunk_'+k+'_V23_%d_%02d'%(t,b),phone_mat if k=='PHONES' else palette) for k in ['SEATS','CROWD','PHONES']}
        lows={k:Mesh('low',palette) for k in ['SEATS','CROWD']}
        for j in range(n):
            r=(j+.5)*step;L=table(t,r)[2];margin=HALF+.2
            width=L/N-2*margin;num=int(width/.56)
            for k in range(num):
                w=margin+(k+.5)*width/num;u=b/N+PHASE+w/L;a=angle(t,r,u);z=h(t,j,a);p=q(t,b,r,w,z);x,y=p.x,p.y;rot=a+math.pi/2
                color=(.24,.018,.027,1) if rng.random()>.12 else (.55,.52,.49,1)
                builders['SEATS'].box((x,y,z+.43),(.46,.42,.12),rot,color)
                builders['SEATS'].box((x+.19*math.cos(a),y+.19*math.sin(a),z+.72),(.46,.09,.48),rot,color)
                lows['SEATS'].box((x+.19*math.cos(a),y+.19*math.sin(a),z+.68),(.46,.12,.5),rot,color);seat_total+=1
                # Backstage sightline blocks keep seats, but do not seat audience behind the stage.
                if (y<53 or abs(x)>63) and rng.random()<.97:
                    c=rng.choice(clothes);sk=rng.choice(skin)
                    builders['CROWD'].box((x,y,z+.94),(.38,.29,.60),rot,c);builders['CROWD'].oct((x,y,z+1.38),.12,sk)
                    lows['CROWD'].box((x,y,z+1.02),(.38,.29,.83),rot,c);people_total+=1
                    if rng.random()<.13:builders['PHONES'].oct((x,y,z+1.52+rng.random()*.3),rng.uniform(.032,.048))
        for cat,batch in builders.items():
            name=batch.name;batch.name='看台座椅_V23_'+name if cat=='SEATS' else 'V23_DETAIL_'+name
            ob=batch.finish()
            if ob is None:continue
            # Keep source detail outside architecture export.
            if cat!='SEATS':
                C.objects.unlink(ob);next(c for c in S.collection.children if c.name.startswith('07_')).objects.link(ob)
            hi=bpy.data.objects.new(name+'_L0',ob.data);D.collection.objects.link(hi);hi.parent=root
            ht=sum(len(p.vertices)-2 for p in hi.data.polygons);lt=ht
            if cat in lows:
                group=bpy.data.objects.new('LOD_'+name,None);D.collection.objects.link(group);group.parent=root;hi.parent=group
                lows[cat].name=name+'_L1';lo=lows[cat].finish(D.collection);lo.parent=group;lt=sum(len(p.vertices)-2 for p in lo.data.polygons)
            newreports.append({'chunk':name,'category':cat,'near_triangles':ht,'far_triangles':lt})

# New route cutters applied only to pre-existing structure, preserving the newly built path floors.
progress('Cutting legacy walls and concourse obstructions around new routes')
cutmesh=Mesh('V23_TEMP_route_cutters',M['concrete'])
for c in cuts:
    off=len(cutmesh.v);cutmesh.v.extend(c.v);cutmesh.f.extend(tuple(off+i for i in f) for f in c.f)
cutter=cutmesh.finish();bpy.context.view_layer.update()
cut_bounds=[([min(v[k] for v in c.v) for k in range(3)],[max(v[k] for v in c.v) for k in range(3)]) for c in cuts]
for o in list(S.objects):
    if o.type not in ('MESH','CURVE') or o.name.startswith(('V23_','看台座椅_','三层看台_')):continue
    if not (o.name.startswith(('环形集散厅楼板','环廊径向梁','环廊周圈护栏','环廊护栏立杆','V12_'))):continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
    nearby=[c for c,(cl,ch) in zip(cuts,cut_bounds) if all(cl[k]<=hi[k]+.01 and ch[k]>=lo[k]-.01 for k in range(3))]
    if not nearby:continue
    local=Mesh('V23_TEMP_local',M['concrete'])
    for c in nearby:
        off=len(local.v);local.v.extend(c.v);local.f.extend(tuple(off+i for i in f) for f in c.f)
    localcut=local.finish();bpy.context.view_layer.update()
    if o.type=='CURVE':
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));new=bpy.data.objects.new(o.name+'_V23',me)
        for col in o.users_collection:col.objects.link(new)
        bpy.data.objects.remove(o,do_unlink=True);o=new
    mod=o.modifiers.new('草图C通道净空','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=localcut
    mod.use_self=True
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);o.modifiers.clear();o.data=me
    bpy.data.objects.remove(localcut,do_unlink=True)
    progress('Cleared '+o.name)
bpy.data.objects.remove(cutter,do_unlink=True)
# Old wall holes must not remain: regenerated shell will be cut from the same route volumes separately.
# Keep cutter data for this next deterministic step and for audit.
(CHECK/'v23_cutters.json').write_text(json.dumps({'v':cutmesh.v,'f':cutmesh.f}),encoding='utf-8')
(PKG/'Editor/v23_portals.json').write_text(json.dumps({'portals':portals},ensure_ascii=False),encoding='utf-8')
S['seating_v23']=True;S['seating_v23_seats']=seat_total;S['seating_v23_people']=people_total
data={'modules_per_tier':N,'occupancy_target':.97,'seat_count':seat_total,'audience_count':people_total,'portals':portals,'rows':counts,'samples':samples,'segments':segments}
(CHECK/'v23_layout.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
(PKG/'Editor/v23_checks.json').write_text(json.dumps({'samples':samples,'segments':segments},ensure_ascii=False),encoding='utf-8')
report=json.loads((ROOT/'unity_enhanced/optimization_geometry.json').read_text(encoding='utf-8'))
report['details']=[r for r in report['details'] if r['category']!='SEATS' and not (r['category'] in ['CROWD','PHONES'] and '_B_' in r['chunk'])]+newreports
(ROOT/'unity_enhanced/optimization_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
progress('Geometry generated: %d seats, %d audience, %d entrance positions'%(seat_total,people_total,len(portals)))


