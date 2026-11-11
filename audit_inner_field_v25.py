import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');S=bpy.context.scene;D=bpy.data.scenes['UNITY_ENHANCED_V3']
layout=json.loads((ROOT/'unity_enhanced/checks/v25_field_layout.json').read_text(encoding='utf8'))
errors=[];verts=[];faces=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
    if ob.type not in ['MESH','CURVE']:continue
    if not any(c.name.startswith(('06_','07_','18_')) for c in ob.users_collection):continue
    if 'V23' in ob.name:continue
    me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));off=len(verts);verts.extend(ob.matrix_world@v.co for v in me.vertices);faces.extend(tuple(off+i for i in p.vertices) for p in me.polygons);bpy.data.meshes.remove(me)
tree=BVHTree.FromPolygons(verts,faces);tests=[]
for y in [22.4,4.6,-13.2,-32.6]:tests.append(((-54,y,1.25),(54,y,1.25)))
for x in [-38.2,-19.2,19.2,38.2]:tests.append(((x,-52,1.25),(x,40,1.25)))
tests.extend([((0,-55,1.25),(0,-33,1.25)),((0,-10.1,1.25),(0,38.7,1.25))])
for side in [-1,1]:tests.append(((side*19,-22.5,1.25),(side*14.9,-22.5,1.25)))
tests=[((a[0],a[1],height),(b[0],b[1],height)) for a,b in tests for height in [.5,.95,1.25]]
# On stairs the body follows the rising treads, rather than a horizontal ray through them.
for side in [-1,1]:
    steps=[(side*14.9,-22.5,0)]+[(side*(14.625-k*.35),-22.5,(k+1)*.1625) for k in range(4)]+[(side*13.1,-22.5,.65)]
    for p in steps[1:]:
        hit=tree.ray_cast(Vector(p)+Vector((0,0,.04)),Vector((0,0,-1)),.1)
        if hit[0] is None or abs(hit[0].z-p[2])>.005:errors.append({'stair_support':p})
    for a,b in zip(steps,steps[1:]):
        for height in [.5,.95,1.25]:tests.append(((a[0],a[1],a[2]+height),(b[0],b[1],b[2]+height)))
for a,b in tests:
    a,b=Vector(a),Vector(b);d=b-a;hit=tree.ray_cast(a,d.normalized(),d.length)
    if hit[0] is not None:errors.append({'route':[list(a),list(b)],'hit':list(hit[0])})
for x,y,name in layout['seat_positions']:
    if -19.2<x<19.2 and -52<y<-13.2:errors.append({'seat_in_control_or_rear':name})
assert S.get('screen_audience_v24'),'Screen shadow cleanup lost'
out={'blocks':len(layout['blocks']),'chairs':layout['chairs'],'audience':layout['audience'],'clear_routes':len(tests),'failures':errors}
(ROOT/'unity_enhanced/checks/v25_field_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out)
assert not errors
