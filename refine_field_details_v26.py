"""Repair existing v25 meshes without reseeding or moving the audience.

Run in the source scene, then export_repaired_architecture_v6.py.
Uses existing materials. Dimensions are model refinements, not as-built data.
"""
import ast, json, math
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
S = bpy.context.scene
D = bpy.data.scenes['UNITY_ENHANCED_V3']
assert S.get('inner_field_v25') and S.get('screen_audience_v24')

def components(ob):
    mesh = ob.data
    neighbors = [[] for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        neighbors[a].append(b); neighbors[b].append(a)
    seen = set()
    for v in mesh.vertices:
        if v.index in seen:
            continue
        ids = []; stack = [v.index]; seen.add(v.index)
        while stack:
            i = stack.pop(); ids.append(i)
            for j in neighbors[i]:
                if j not in seen:
                    seen.add(j); stack.append(j)
        p = sum((ob.matrix_world @ mesh.vertices[i].co for i in ids), Vector()) / len(ids)
        yield ids, p

def seat_key(x, y):
    return round(x, 3), round(y, 3)

occupied = set()
for ob in S.objects:
    if ob.name.startswith('观众衣着_'):
        for ids, p in components(ob):
            assert len(ids) == 8
            occupied.add(seat_key(p.x, p.y))
assert len(occupied) == S['field_audience_count'] == 6866

def repair_phones(ob):
    remove = []; retained = []; before = 0
    for ids, p in components(ob):
        assert len(ids) == 6
        before += 1
        if seat_key(p.x - .15, p.y - .12) not in occupied:
            remove.extend(ids)
        else:
            retained.append(tuple(round(c, 4) for c in p))
    if remove:
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in remove], context='VERTS')
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return before, len(remove)//6, retained

before, removed, source_positions = repair_phones(S.objects['全场手机星光'])
export_positions = []; export_removed = 0
for ob in D.objects:
    if ob.name.startswith('Chunk_PHONES_F_'):
        _, n, positions = repair_phones(ob)
        export_removed += n; export_positions.extend(positions)
assert removed == export_removed
assert sorted(source_positions) == sorted(export_positions)

# Reuse the established mesh builder, without executing the original rebuild.
tree = ast.parse((ROOT/'rebuild_inner_field_v25.py').read_text(encoding='utf8'))
defs = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Builder'
        or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ['CF','CV','OF'] for t in n.targets)]
exec(compile(ast.Module(body=defs, type_ignores=[]), 'field_helpers', 'exec'))
col = bpy.data.collections['06_内场折叠椅']
for name in ['FOH侧梯连续扶手_V26', 'FOH踏步防滑边条_V26']:
    if S.objects.get(name):
        bpy.data.objects.remove(S.objects[name], do_unlink=True)
rails = Builder('FOH侧梯连续扶手_V26', bpy.data.materials['栏杆细金属'])
trim = Builder('FOH踏步防滑边条_V26', bpy.data.materials['导向标识白漆'])

def beam(a, b, width=.045):
    a, b = Vector(a), Vector(b)
    direction = b-a
    q = Vector((0,0,1)).rotation_difference(direction.normalized())
    center = (a+b)/2; offset = len(rails.v)
    rails.v.extend(tuple(center + q @ Vector((x*width,y*width,z*direction.length))) for x,y,z in CV)
    rails.f.extend(tuple(offset+i for i in face) for face in CF)
    rails.smooth.extend([False]*6)

for side in [-1,1]:
    for y in [-24.03,-20.97]:
        beam((side*14.625,y,.1625),(side*14.625,y,1.2625),.055)
        beam((side*13.575,y,.65),(side*13.575,y,1.75),.055)
        beam((side*14.80,y,1.18125),(side*13.575,y,1.75))
        beam((side*13.575,y,1.75),(side*13.15,y,1.75))
    for k in range(4):
        trim.box((side*(14.625-k*.35+.13),-22.5,(k+1)*.1625+.004),(.055,2.95,.008))
for k in range(3):
    trim.box((0,-22.4+(2.5-k)*.34+.13,.65+(k+1)/6+.004),(2.3,.055,.008))
rails.finish(col); trim.finish(col)
S['field_detail_v26'] = True
layout_path = ROOT/'unity_enhanced/checks/v25_field_layout.json'
layout = json.loads(layout_path.read_text(encoding='utf8'))
layout['phones'] = len(source_positions)
layout_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding='utf8')
report = {'version':'v26','audience':len(occupied),'phones_before':before,
          'orphan_phones_removed':removed,'phones_after':len(source_positions),
          'source_export_phone_positions_match':True,'side_stair_clear_width':3.005,
          'marked_treads':11,'new_meshes':2}
(ROOT/'unity_enhanced/checks/v26_detail_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(report)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
