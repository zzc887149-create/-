"""Remove spectators and phone lights (preserving all stadium seats) in the sightline-obstructed
zone behind the South Stand Teleprompter (后方看台提词器, x in [-15.8, +15.8], y = -127.3, z in [21.9, 35.9]).
Updates both S (赵雷2026_没有信号_鸟巢复刻) and D (UNITY_ENHANCED_V3), then exports BirdsNest_Enhanced.fbx.
"""
import bpy, bmesh, math, json, hashlib
from pathlib import Path

ROOT = Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
OUT = ROOT / 'unity_enhanced'
PKG = OUT / 'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'

S = bpy.data.scenes['赵雷2026_没有信号_鸟巢复刻']
D = bpy.data.scenes['UNITY_ENHANCED_V3']

def is_teleprompter_blocked(x, y, z):
    # Only South Stand Tier 2 (t=1) and Tier 3 (t=2) behind the teleprompter (y < -125.0, z > 16.0)
    if y > -125.0 or z < 16.0:
        return False
    # Sightline shadow cone behind the [-15.8, +15.8] teleprompter at y = -127.3m
    x_limit = 16.0 + 0.262 * max(0.0, -127.3 - y)
    return abs(x) <= x_limit

def filter_chunk_mesh(me, stride):
    if not me or len(me.vertices) == 0:
        return 0
    n_verts = len(me.vertices)
    assert n_verts % stride == 0, f"{me.name}: {n_verts} not divisible by {stride}"
    n_items = n_verts // stride

    drop_indices = set()
    removed = 0
    for i in range(n_items):
        base = i * stride
        cx = sum(me.vertices[base + k].co.x for k in range(stride)) / stride
        cy = sum(me.vertices[base + k].co.y for k in range(stride)) / stride
        cz = sum(me.vertices[base + k].co.z for k in range(stride)) / stride
        if is_teleprompter_blocked(cx, cy, cz):
            removed += 1
            for k in range(stride):
                drop_indices.add(base + k)

    if not drop_indices:
        return 0

    # Rebuild mesh preserving material and float vertex color attribute ('Color')
    has_color = 'Color' in me.color_attributes
    old_colors = [tuple(me.color_attributes['Color'].data[v_idx].color) for v_idx in range(n_verts)] if has_color else None

    old_to_new = {}
    new_v = []
    new_c = []
    for v_idx, v in enumerate(me.vertices):
        if v_idx not in drop_indices:
            old_to_new[v_idx] = len(new_v)
            new_v.append((v.co.x, v.co.y, v.co.z))
            if has_color:
                new_c.append(old_colors[v_idx])

    new_f = []
    for poly in me.polygons:
        if all(vi in old_to_new for vi in poly.vertices):
            new_f.append(tuple(old_to_new[vi] for vi in poly.vertices))

    mats = [m for m in me.materials]
    me.clear_geometry()
    me.from_pydata(new_v, [], new_f)
    for m in mats:
        if m.name not in [existing.name for existing in me.materials]:
            me.materials.append(m)
    me.update()
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    if has_color:
        if 'Color' in me.color_attributes:
            me.color_attributes.remove(me.color_attributes['Color'])
        vc = me.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
        for dst_v, col_val in zip(vc.data, new_c):
            dst_v.color = col_val
    return removed

removed_l0_people = 0
removed_l1_people = 0
removed_phones = 0

for t in (1, 2):
    for b in (15, 16, 17, 18):
        # L0 Crowd mesh (shared between S: V20_DETAIL_Chunk_CROWD_V20_t_b and D: Chunk_CROWD_V20_t_b_L0)
        ob_l0 = D.objects.get(f'Chunk_CROWD_V20_{t}_{b:02d}_L0')
        if ob_l0 and ob_l0.data:
            removed_l0_people += filter_chunk_mesh(ob_l0.data, 14)

        # L1 Crowd mesh (D: Chunk_CROWD_V20_t_b_L1)
        ob_l1 = D.objects.get(f'Chunk_CROWD_V20_{t}_{b:02d}_L1')
        if ob_l1 and ob_l1.data:
            removed_l1_people += filter_chunk_mesh(ob_l1.data, 8)

        # Phones mesh (shared between S: V20_DETAIL_Chunk_PHONES_V20_t_b and D: Chunk_PHONES_V20_t_b_L0)
        ob_ph = D.objects.get(f'Chunk_PHONES_V20_{t}_{b:02d}_L0')
        if ob_ph and ob_ph.data:
            removed_phones += filter_chunk_mesh(ob_ph.data, 6)

# Export updated FBX from D
bpy.context.window.scene = D
f = PKG / 'Models/BirdsNest_Enhanced.fbx'
bpy.ops.export_scene.fbx(
    filepath=str(f),
    use_selection=False,
    use_visible=False,
    object_types={'MESH', 'EMPTY'},
    global_scale=1,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Z',
    axis_up='Y',
    bake_space_transform=False,
    use_mesh_modifiers=True,
    mesh_smooth_type='OFF',
    colors_type='LINEAR',
    bake_anim=False,
    path_mode='STRIP',
    embed_textures=False,
    add_leaf_bones=False,
)
bpy.context.window.scene = S
S['teleprompter_sightline_cleared_v23'] = True

# Update optimization_geometry.json triangle counts and hash
opt_path = OUT / 'optimization_geometry.json'
report = json.loads(opt_path.read_text(encoding='utf-8'))
for entry in report['details']:
    cname = entry['chunk']
    if cname.startswith(('Chunk_CROWD_V20_1_', 'Chunk_CROWD_V20_2_', 'Chunk_PHONES_V20_1_', 'Chunk_PHONES_V20_2_')):
        o0 = D.objects.get(cname + '_L0')
        o1 = D.objects.get(cname + '_L1')
        if o0 and o0.data:
            entry['near_triangles'] = sum(len(p.vertices) - 2 for p in o0.data.polygons)
        if o1 and o1.data:
            entry['far_triangles'] = sum(len(p.vertices) - 2 for p in o1.data.polygons)
        elif o0 and o0.data:
            entry['far_triangles'] = entry['near_triangles']

report['near_triangles'] = sum(r['near_triangles'] for r in report['details'])
report['far_triangles'] = sum(r['far_triangles'] for r in report['details'])
report['sha256'] = hashlib.sha256(f.read_bytes()).hexdigest()
opt_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({
    'status': 'TELEPROMPTER_SIGHTLINE_CLEARED_V23',
    'removed_l0_people': removed_l0_people,
    'removed_l1_people': removed_l1_people,
    'removed_phones': removed_phones,
    'sha256': report['sha256'],
}, ensure_ascii=False))

