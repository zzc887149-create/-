"""Vacate the rear LED sightline shadow, retaining empty seats and circulation."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');OUT=ROOT/'unity_enhanced';S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
assert not S.get('screen_audience_v24'),'Already applied'
screen=S.objects['后方看台提词器_主箱体']
corners=[screen.matrix_world@Vector(v) for v in screen.bound_box]
xmin=min(v.x for v in corners);xmax=max(v.x for v in corners);sy=max(v.y for v in corners)
zmin=min(v.z for v in corners);zmax=max(v.z for v in corners)
def blocked(p):
    # A stage-centre sightline projected through the actual cabinet footprint.
    # A small lateral margin keeps boundary spectators clear of the cabinet.
    if p.y>=sy-.1 or p.z<21.2 or p.z>37:return False
    scale=(65-p.y)/(65-sy)
    return (xmin-.4)*scale<=p.x<=(xmax+.4)*scale
seen=set();records=[];removed_people=0
for ob in list(S.objects)+list(D.objects):
    if ob.type!='MESH' or not any(k in ob.name for k in ['CROWD_V23_','PHONES_V23_']):continue
    me=ob.data
    if me.as_pointer() in seen:continue
    seen.add(me.as_pointer());phone='PHONES' in ob.name;low=ob.name.endswith('_L1');stride=6 if phone else 8 if low else 14
    assert len(me.vertices)%stride==0,(ob.name,len(me.vertices),stride)
    before=len(me.vertices);drop=[];groups=0
    for i in range(0,before,stride):
        p=sum((ob.matrix_world@me.vertices[j].co for j in range(i,i+stride)),Vector())/stride
        if blocked(p):drop.extend(range(i,i+stride));groups+=1
    if drop:
        bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in drop],context='VERTS');bm.to_mesh(me);bm.free();me.update()
    if not phone and not low:removed_people+=groups
    # Whole primitives must remain; both shared near meshes and far LODs are checked.
    assert len(me.vertices)%stride==0
    remaining=sum(blocked(sum((ob.matrix_world@me.vertices[j].co for j in range(i,i+stride)),Vector())/stride) for i in range(0,len(me.vertices),stride))
    assert remaining==0,(ob.name,remaining)
    if groups:records.append({'mesh':ob.name,'removed_people_or_lights':groups,'remaining_in_shadow':remaining})
S['screen_audience_v24']=True;S['screen_shadow_removed_people']=removed_people
report={'screen_bounds':[xmin,xmax,sy,zmin,zmax],'removed_people':removed_people,'remaining_bowl_audience':62887-removed_people,'empty_seats_preserved':True,'meshes':records}
(OUT/'checks/v24_screen_audience.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
DEST=ROOT/'赵雷2026_鸟巢_提词器后方空座版.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print(json.dumps({k:v for k,v in report.items() if k!='meshes'},ensure_ascii=False))
