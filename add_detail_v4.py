"""Additional editable circulation details, based on the saved exterior staircase photograph."""
import bpy, bmesh, math, ast, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S=bpy.context.scene
assert S.get('enhanced_v3') and not S.get('detail_v4')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_近景完善版.blend'))
tree=ast.parse((ROOT/'build_concert.py').read_text(encoding='utf-8'))
helpers=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cube_v','cube_f'] for t in n.targets))]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'helpers','exec'))
COL={c.name[:2]:c for c in S.collection.children}
c=bpy.data.collections.new('19_近景楼梯与环廊细化');S.collection.children.link(c);COL['19']=c
concrete=bpy.data.materials['concrete'];red=bpy.data.materials['楼梯红色防滑涂层'];metal=bpy.data.materials['栏杆细金属'];black=bpy.data.materials['black']
lum=material('BND_环廊灯罩',(.8,.74,.60),.65,0,.5)
def localbox(name,p,d,mat,a):
    ob=box(name,p,d,mat,'19');ob.rotation_euler.z=a;return ob
for bay in range(12):
    a=bay*math.tau/12+.11;rad=Vector((math.cos(a),math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0));centre=Vector((126.5*math.cos(a),143.5*math.sin(a),0))
    panels=Batch('楼梯平台红色格栅_%02d'%bay,red,'19');rails=Batch('楼梯平台扶手_%02d'%bay,metal,'19');risers=Batch('楼梯红色踏步立面_%02d'%bay,red,'19')
    for flight in range(6):
        direction=1 if flight%2==0 else -1;zbase=flight*3.75;lane=rad*((flight%2)*2.6-1.3)
        for j in range(25):
            p=centre+lane+tan*((j*.28-3.4-.169)*direction);p.z=zbase+(j+1)*.15-.075;risers.box(p,(1.6,.014,.15),a)
        # Continuous slab below the existing treads: local width, length and rising profile.
        verts=[]
        for bottom in [True,False]:
            for x,t in [(-1.1,-3.55),(1.1,-3.55),(1.1,3.6),(-1.1,3.6)]:
                p=centre+lane+rad*x+tan*(t*direction);p.z=zbase+(t+3.4)*(.15/.28)-(.28 if bottom else .08);verts.append(tuple(p))
        mesh('楼梯连续底板_%02d_%d'%(bay,flight),verts,cube_f,concrete,'19')
        landing=centre+tan*(3.9*direction);landing.z=zbase+3.75
        for side in [-1,1]:
            pp=landing+rad*(side*2.65)
            # Light open grille panels at landing edges, rather than solid walls across the stairs.
            for j in range(12):
                p=pp+tan*(-.64+j*.116);p.z=landing.z+.48;panels.box(p,(.035,.025,.9),a)
            for z in [.12,.45,.82]:
                p=pp.copy();p.z=landing.z+z;panels.box(p,(.04,1.35,.035),a)
            p=pp.copy();p.z=landing.z+1.02;rails.box(p,(.07,1.42,.065),a)
    panels.finish();rails.finish();risers.finish()
    # Red floor labels face into the circulation gallery. Bay numbers are intentionally omitted.
    aa=round(a/(math.tau/48))*(math.tau/48);r=Vector((math.cos(aa),math.sin(aa),0))
    for level,z in enumerate([.08,7.5,15,22.5]):
        p=Vector((130*math.cos(aa),147*math.sin(aa),z+2.0))-r*.45
        cv=bpy.data.curves.new('楼层文字','FONT');cv.body='F'+str(level+1);cv.size=.65;cv.align_x='CENTER';cv.extrude=.0015
        ob=link(bpy.data.objects.new('红色楼层标识_F'+str(level+1),cv),'19');ob.location=p;ob.rotation_euler=(math.pi/2,0,aa-math.pi/2);cv.materials.append(red)

# Modest surface-mounted conduits and light housings beneath the existing floor plates.
# These are visual approximations, not a mechanical-services survey.
for level,z in enumerate([6.8,14.3,21.8]):
    for radius in [123.0,123.35]:
        pts=[(radius*math.cos(i*math.tau/240),(radius+17)*math.sin(i*math.tau/240),z) for i in range(240)]
        line('环廊顶面管线_F'+str(level+1),pts,.04,metal,'19',True)
    hangers=Batch('管线支架_F'+str(level+1),metal,'19');cases=Batch('环廊灯具外壳_F'+str(level+1),black,'19');diffusers=Batch('环廊灯罩_F'+str(level+1),lum,'19')
    for i in range(48):
        a=i*math.tau/48
        hangers.box((123.2*math.cos(a),140.2*math.sin(a),z+.16),(.62,.06,.30),a)
        cases.box((125*math.cos(a),142*math.sin(a),z-.05),(.20,1.6,.09),a)
        diffusers.box((125*math.cos(a),142*math.sin(a),z-.10),(.16,1.5,.018),a)
    hangers.finish();cases.finish();diffusers.finish()

# Stage cables and pedal details; keep the existing artist and instruments editable.
for i,x in enumerate([-12,-4,0,8,12]):
    points=[(x,52.1,2.225),(x+.2,54.3,2.225),(x+1.1,55.2,2.225),(x+.5,57.0,2.225)]
    line('舞台音频线_%d'%i,points,.009,black,'19')
for x in [-.55,.3]:
    localbox('主唱踏板',(x,50.0,2.25),(.22,.32,.10),black,0)
    localbox('踏板开关',(x,49.93,2.31),(.04,.04,.025),metal,0)

views=[('10_StageClose',(15,30,8),(0,56,6)),('12_Memorial',(-.8,43.2,1.55),(-2.2,41.7,.65))]
a=.11;rad=Vector((math.cos(a),math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0));centre=Vector((126.5*math.cos(a),143.5*math.sin(a),0))
p=centre-rad*1.3-tan*8;p.z=1.65;t=centre-rad*1.3+tan*2;t.z=3.15
views.append(('11_StairDetail',tuple(p),tuple(t)))
for name,p,t in views:
    for prefix,point in [('VIEW_',p),('LOOK_',t)]:
        ob=link(bpy.data.objects.new(prefix+name,None),'19');ob.location=point

# World metre UVs on the new slabs only.
for ob in c.objects:
    if ob.type!='MESH' or concrete not in list(ob.data.materials):continue
    uv=ob.data.uv_layers.new(name='MetreUV')
    for face in ob.data.polygons:
        axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in face.loop_indices:
            p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/2,p[axes[1]]/2)

S['detail_v4']=True;S['detail_v4_note']='Stair slab, landing grilles and red floor labels informed by exterior_stairs.jpg; service lines approximate.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_近景完善版.blend'))
print('Added detail collection with',len(c.objects),'objects')
