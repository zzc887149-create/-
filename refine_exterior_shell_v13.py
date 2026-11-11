"""V13: Reconstruct Bird's Nest exterior steel shell, saddle roof lattice, and upper red bowl shell.
Eliminates floating roof steel (2.8m offset bug), perimeter roof spikes, mid-air dead-end facade beams,
and upper-tier grey concrete step ledges poking through the red bowl shell.
"""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S = bpy.context.scene
assert S.get('rear_deck_v12'), "Expected v12 scene as input"

COL = {c.name[:2]: c for c in S.collection.children}
silver = bpy.data.materials['外层浅灰钢带']
membrane = bpy.data.materials['membrane']
facade_red = bpy.data.materials['外碗赭红混凝土']
dark = bpy.data.materials['dark']
steel = bpy.data.materials['steel']

# ---------------------------------------------------------------------------
# 1. Unified Saddle Roof & Facade Envelope Mathematics
# ---------------------------------------------------------------------------
# Outer perimeter at u=0: (rx=148.0, ry=166.8)
# Inner oculus at u=1:    (rx=62.0,  ry=91.0)
# Lowered roof elevation matches correct_roof.py (54.6 - 2.8 = 51.8)
def roofR(u):
    return (148.0 - 86.0 * u, 166.8 - 75.8 * u)

def roofSurfZ(u, a):
    base = 51.8 + 14.6 * math.cos(2.0 * a)
    return base - 2.0 * (u ** 1.35)

def roofPos(u, a, dz=0.0):
    rx, ry = roofR(u)
    return Vector((rx * math.cos(a), ry * math.sin(a), roofSurfZ(u, a) + dz))

def roofNormal(u, a):
    du = 0.002
    da = 0.002
    u0, u1 = max(0.0, u - du), min(1.0, u + du)
    p_u = roofPos(u1, a) - roofPos(u0, a)
    p_a = roofPos(u, a + da) - roofPos(u, a - da)
    # u goes inward (from outer rim to inner ring), a goes counter-clockwise:
    # p_a x p_u points upward (+Z)
    n = p_a.cross(p_u).normalized()
    if n.z < 0:
        n = -n
    return n

# Facade shell envelope: h in [0, 1] from ground (z=0) to roof shoulder (u=0, z=roofSurfZ(0, a))
def facadeR(h):
    bow = math.sin(math.pi * h)
    return (137.0 + 11.0 * h + 1.10 * bow, 155.0 + 11.8 * h + 1.45 * bow)

def facadePos(h, a, dr=0.0):
    rx, ry = facadeR(h)
    rx += dr
    ry += dr
    z = h * roofSurfZ(0.0, a)
    return Vector((rx * math.cos(a), ry * math.sin(a), z))

def facadeNormal(h, a):
    rx, ry = facadeR(h)
    return Vector((math.cos(a) / rx, math.sin(a) / ry, -0.14)).normalized()

def assign_metre_uv(me, scale=2.0):
    uv = me.uv_layers.active or me.uv_layers.new(name='MetreUV')
    for poly in me.polygons:
        n = poly.normal
        axis = max(range(3), key=lambda k: abs(n[k]))
        axes = [k for k in range(3) if k != axis]
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v[axes[0]] / scale, v[axes[1]] / scale)

def add_bevel(ob, width=0.035):
    mod = ob.modifiers.new('近景倒角', 'BEVEL')
    mod.width = width
    mod.segments = 2
    mod.limit_method = 'ANGLE'
    return ob

def make_strip_mesh(name, sec_quads, mat, col_key='01', closed=False, bevel_w=0.035):
    vs = []
    fs = []
    for q in sec_quads:
        vs.extend(tuple(p) for p in q)
    m_cnt = len(sec_quads)
    seg_cnt = m_cnt if closed else m_cnt - 1
    for j in range(seg_cnt):
        jn = (j + 1) % m_cnt
        for k in range(4):
            kn = (k + 1) % 4
            fs.append((4 * j + k, 4 * j + kn, 4 * jn + kn, 4 * jn + k))
    if not closed:
        fs.append((3, 2, 1, 0))
        off = 4 * (m_cnt - 1)
        fs.append((off, off + 1, off + 2, off + 3))
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], fs)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    me.update()
    if mat:
        me.materials.append(mat)
    assign_metre_uv(me)
    ob = bpy.data.objects.new(name, me)
    COL[col_key].objects.link(ob)
    if bevel_w > 0:
        add_bevel(ob, bevel_w)
    return ob

def build_facade_strip(name, ha_pts, width, depth, dr=0.0, mat=None, col_key='01', closed=False):
    """Build a continuous facade ribbon using iso-height circumferential sections at constant h
    (or iso-angle vertical offsets for closed horizontal rings), guaranteeing 100% flush joints at h=0 and h=1."""
    n_pts = len(ha_pts)
    quads = []
    if closed:
        # Closed circumferential ring band: offset vertically along h and radially by depth
        for j, (h, a) in enumerate(ha_pts):
            z_span = max(35.0, roofSurfZ(0.0, a))
            dh = (width * 0.5) / z_span
            q = []
            for s_w, s_d in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                hj = min(0.992, max(0.005, h + s_w * dh))
                v = facadePos(hj, a, dr + s_d * depth * 0.5)
                v.z -= 0.12
                q.append(v)
            quads.append(q)
    else:
        # Full-height column / diagonal ribbon from h=0 to h=1: offset circumferentially at constant h
        pts = [facadePos(h, a, dr) for h, a in ha_pts]
        for j, ((h, a), p) in enumerate(zip(ha_pts, pts)):
            t_vec = (pts[min(j + 1, n_pts - 1)] - pts[max(j - 1, 0)]).normalized()
            rx, ry = facadeR(h)
            e_tan = Vector((-rx * math.sin(a), ry * math.cos(a), 0.0))
            arc_scale = e_tan.length
            # Correct width for diagonal angle so perpendicular ribbon width equals `width`
            sin_pitch = max(0.42, math.sqrt(max(0.0, 1.0 - (t_vec.dot(e_tan.normalized())) ** 2)))
            eff_half_w = (width * 0.5) / sin_pitch
            da = eff_half_w / arc_scale
            q = []
            for s_w, s_d in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                aj = a + s_w * da
                v = facadePos(h, aj, dr + s_d * depth * 0.5)
                if h >= 0.999:
                    # Tuck top end cleanly into the outer roof shoulder ring girder
                    v.z = roofSurfZ(0.0, aj) - (0.04 if s_d > 0 else 0.36)
                elif h <= 0.001:
                    v.z = 0.0
                else:
                    v.z = h * (roofSurfZ(0.0, aj) - 0.12)
                q.append(v)
            quads.append(q)
    return make_strip_mesh(name, quads, mat or silver, col_key, closed=closed)

def build_roof_strip(name, ua_pts, width, depth, dz=0.0, mat=None, col_key='01', closed=False):
    """Build a continuous saddle-roof ribbon aligned with the lowered roof surface and flush at u=0 and u=1."""
    n_pts = len(ua_pts)
    quads = []
    if closed:
        # Closed ring girder at constant u (e.g. u=0 outer rim or u=1 inner oculus): offset radially along u
        for j, (u, a) in enumerate(ua_pts):
            du = (width * 0.5) / 86.0
            q = []
            for s_w, s_d in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                uj = min(1.0, max(0.0, u + (s_w + 1.0) * 0.5 * du * (1.0 if u < 0.5 else -1.0)))
                v = roofPos(uj, a, dz + s_d * depth * 0.5)
                q.append(v)
            quads.append(q)
    else:
        # Radial/diagonal roof truss or woven ribbon from u=0 to u=1: offset circumferentially at constant u
        pts = [roofPos(u, a, dz) for u, a in ua_pts]
        for j, ((u, a), p) in enumerate(zip(ua_pts, pts)):
            t_vec = (pts[min(j + 1, n_pts - 1)] - pts[max(j - 1, 0)]).normalized()
            rx, ry = roofR(u)
            e_tan = Vector((-rx * math.sin(a), ry * math.cos(a), 0.0))
            arc_scale = e_tan.length
            sin_ang = max(0.45, math.sqrt(max(0.0, 1.0 - (t_vec.dot(e_tan.normalized())) ** 2)))
            da = ((width * 0.5) / sin_ang) / arc_scale
            q = []
            for s_w, s_d in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                aj = a + s_w * da
                v = roofPos(u, aj, dz + s_d * depth * 0.5)
                q.append(v)
            quads.append(q)
    return make_strip_mesh(name, quads, mat or silver, col_key, closed=closed)

# ---------------------------------------------------------------------------
# 2. Update PTFE Saddle Roof Membrane & Edge Return
# ---------------------------------------------------------------------------
old_roof = S.objects.get('PTFE马鞍形屋面')
if old_roof:
    bpy.data.objects.remove(old_roof, do_unlink=True)

N_roof = 240
u_steps = [k / 9.0 for k in range(10)]
roof_vs = []
for u in reversed(u_steps):  # from inner (u=1) to outer (u=0)
    rx, ry = roofR(u)
    for i in range(N_roof):
        a = math.tau * i / N_roof
        roof_vs.append((rx * math.cos(a), ry * math.sin(a), roofSurfZ(u, a)))
roof_fs = []
for j in range(len(u_steps) - 1):
    for i in range(N_roof):
        inext = (i + 1) % N_roof
        # Reversed winding to match original flip(o) + solidify(-1)
        roof_fs.append((j * N_roof + i, (j + 1) * N_roof + i, (j + 1) * N_roof + inext, j * N_roof + inext))

roof_me = bpy.data.meshes.new('PTFE马鞍形屋面')
roof_me.from_pydata(roof_vs, [], roof_fs)
roof_me.materials.append(membrane)
roof_me.update()
assign_metre_uv(roof_me, 4.0)
roof_ob = bpy.data.objects.new('PTFE马鞍形屋面', roof_me)
COL['02'].objects.link(roof_ob)
roof_ob['layer_clearance_corrected'] = True
mod = roof_ob.modifiers.new('实体厚度_Unity正反可见', 'SOLIDIFY')
mod.thickness = 0.23
mod.offset = -1.0
mod.use_even_offset = True

# Rebuild 屋面外沿收边 so it tucks cleanly underneath the lowered outer roof edge
old_rim = S.objects.get('屋面外沿收边')
if old_rim:
    bpy.data.objects.remove(old_rim, do_unlink=True)
rim_vs = []
for dz in [-1.75, -0.08]:
    for i in range(N_roof):
        a = math.tau * i / N_roof
        rim_vs.append((147.65 * math.cos(a), 166.45 * math.sin(a), roofSurfZ(0.0, a) + dz))
rim_fs = [(i, (i + 1) % N_roof, N_roof + (i + 1) % N_roof, N_roof + i) for i in range(N_roof)]
rim_me = bpy.data.meshes.new('屋面外沿收边')
rim_me.from_pydata(rim_vs, [], rim_fs)
rim_me.materials.append(membrane)
rim_me.update()
assign_metre_uv(rim_me, 4.0)
rim_ob = bpy.data.objects.new('屋面外沿收边', rim_me)
COL['17'].objects.link(rim_ob)
m_rim = rim_ob.modifiers.new('收边厚度', 'SOLIDIFY')
m_rim.thickness = 0.23

# ---------------------------------------------------------------------------
# 3. Rebuild Collection 01 (Bird's Nest Steel Structure) Without Protrusions
# ---------------------------------------------------------------------------
removed_steel = 0
for ob in list(COL['01'].objects):
    bpy.data.objects.remove(ob, do_unlink=True)
    removed_steel += 1

# 3a. Outer shoulder ring girder (u=0) and Inner oculus ring girder (u=1)
ring_N = 240
build_roof_strip(
    '屋面边环_外环',
    [(0.0, math.tau * i / ring_N) for i in range(ring_N)],
    width=1.55, depth=0.56, dz=-0.18, mat=silver, col_key='01', closed=True
)
build_roof_strip(
    '屋面边环_内环',
    [(1.0, math.tau * i / ring_N) for i in range(ring_N)],
    width=1.35, depth=0.52, dz=-0.16, mat=silver, col_key='01', closed=True
)

# 3b. 24 Primary Portal Trusses: paired columns + curved roof primary girders
for i in range(24):
    a = i * math.tau / 24.0
    for leg_idx, da in enumerate([-0.047, 0.047]):
        ha = [
            (k / 18.0, a + da * (1.0 - k / 18.0))
            for k in range(19)
        ]
        build_facade_strip(
            f'主桁架柱_{i:02d}_{leg_idx}',
            ha, width=1.65, depth=0.82, dr=0.04, mat=silver, col_key='01'
        )
    ua = [
        (k / 18.0, a + 0.06 * (k / 18.0))
        for k in range(19)
    ]
    build_roof_strip(
        f'屋面主梁_{i:02d}',
        ua, width=1.42, depth=0.56, dz=-0.16, mat=silver, col_key='01'
    )

# 3c. 84 Continuous Roof Woven Ribbons (replacing 504 segmented straight boxes)
for family, sgn in enumerate([-1, 1]):
    for i in range(42):
        a = i * math.tau / 42.0
        ua = [
            (k / 20.0, a + sgn * 0.50 * (k / 20.0))
            for k in range(21)
        ]
        build_roof_strip(
            f'屋面交织带_{family}_{i:02d}',
            ua, width=0.82, depth=0.44, dz=-0.14, mat=silver, col_key='01'
        )

# 3d. 104 Full-Height Facade Woven Diagonal Ribbons (mitered flush at ground & roof rim)
random.seed(20261024)
for i in range(104):
    a = i * math.tau / 104.0 + random.uniform(-0.022, 0.022)
    span = random.choice([-1, 1]) * random.uniform(0.22, 0.68)
    ha = []
    for k in range(21):
        t = k / 20.0
        aa = a + span * t + 0.014 * math.sin(t * math.tau + i)
        ha.append((t, aa))
    build_facade_strip(
        f'精修通高编织钢梁_{i:03d}',
        ha,
        width=random.uniform(1.38, 1.95),
        depth=random.uniform(0.62, 0.82),
        dr=0.0,
        mat=silver,
        col_key='01'
    )

# 3e. 54 Secondary Facade Ribbons: 48 full-span flatter diagonals + 6 closed circumferential ring bands
# ZERO mid-air dead ends and tucked slightly inside (-0.06m) primary outer surface
for i in range(48):
    a = (i + 0.5) * math.tau / 48.0
    span = (1 if i % 2 == 0 else -1) * random.uniform(0.48, 0.82)
    ha = [(k / 20.0, a + span * (k / 20.0)) for k in range(21)]
    build_facade_strip(
        f'精修斜横钢梁_{i:03d}',
        ha,
        width=random.uniform(1.18, 1.55),
        depth=0.58,
        dr=-0.06,
        mat=silver,
        col_key='01'
    )

for idx, h_ring in enumerate([0.22, 0.42, 0.62, 0.80, 0.92, 0.985]):
    w_ring = 1.35 if h_ring < 0.95 else 1.50
    ha = [
        (min(0.995, max(0.01, h_ring + 0.025 * math.sin(3.0 * math.tau * k / 180.0 + idx))), math.tau * k / 180.0)
        for k in range(180)
    ]
    build_facade_strip(
        f'精修斜横钢梁_{48 + idx:03d}',
        ha,
        width=w_ring,
        depth=0.60,
        dr=-0.04,
        mat=silver,
        col_key='01',
        closed=True
    )

# ---------------------------------------------------------------------------
# 4. Fix Upper Red Bowl Shell (红色看台背壳) So Concrete Steps Never Poke Through
# ---------------------------------------------------------------------------
def shell2_profile(zf):
    # Starts at (118.0, 144.5) at zf=0 (z_lin=28.0) to match 红色看台背壳_1_* seamlessly,
    # reaches (120.7, 145.7) by zf=0.12 (before 三层看台_层3 starts at z_lin=30.5),
    # and encloses all 19 rows up to (141.05, 166.05) at zf=1.0 (z_lin=45.6).
    ramp = min(1.0, zf / 0.11)
    bow = math.sin(math.pi * zf)
    rx = 118.0 + 2.65 * ramp + (141.05 - 120.65) * zf + 0.75 * bow
    ry = 144.5 + 1.15 * ramp + (166.05 - 145.65) * zf + 0.75 * bow
    z_lin = 28.0 + (45.6 - 28.0) * zf
    return rx, ry, z_lin

# Restore 三层看台_层3 row 18 outer edge to exact (139.9, 164.9) so all v10 floor samples stay exact
tier3 = S.objects['三层看台_层3']
for v in tier3.data.vertices:
    rad = math.hypot(v.co.x / 139.55, v.co.y / 164.55)
    if rad > 0.9995:
        a = math.atan2(v.co.y / 164.55, v.co.x / 139.55)
        v.co.x = 139.9 * math.cos(a)
        v.co.y = 164.9 * math.sin(a)
tier3.data.update()

# Restore 红色看台背壳_1_* top edge to exact (118.0, 144.5) and clear any F4 portal overhang
f4_ports = [
    p for p in json.loads((ROOT / 'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Editor/seating_entries.json').read_text(encoding='utf-8'))['ports']
    if p['level'] == 4
]
for ob in S.objects:
    if ob.type == 'MESH' and ob.name.startswith('红色看台背壳_1_'):
        for v in ob.data.vertices:
            if v.co.z > 24.5 and math.hypot(v.co.x / 118.3, v.co.y / 144.8) > 1.0:
                a = math.atan2(v.co.y / 145.55, v.co.x / 120.55)
                v.co.x = 118.0 * math.cos(a)
                v.co.y = 144.5 * math.sin(a)
        ob.data.update()
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        rem1 = []
        for f in bm.faces:
            pts_f = [ob.matrix_world @ v.co for v in f.verts] + [ob.matrix_world @ f.calc_center_median()]
            if max(pt.z for pt in pts_f) < 22.0:
                continue
            hit1 = False
            for p in f4_ports:
                entry = Vector(p['entry'])
                rad_v = Vector(p['rad'])
                tan_v = Vector(p['tan'])
                for pt in pts_f:
                    d = pt - entry
                    if -1.5 < d.dot(rad_v) < p['length'] + 1.8 and abs(d.dot(tan_v)) < 1.65 and pt.z > p['concourse'] + 0.5:
                        hit1 = True
                        break
                if hit1:
                    break
            if hit1:
                rem1.append(f)
        if rem1:
            bmesh.ops.delete(bm, geom=rem1, context='FACES')
            bm.to_mesh(ob.data)
            ob.data.update()
        bm.free()

# Rebuild 红色看台背壳_2_%02d with 8 vertical subdivisions and an outward profile that cleanly wraps
# all 19 rows of 三层看台_层3, plus a top coping return, then cut the 12 v10 upper portals & stair clearance.
for ob in list(S.objects):
    if ob.name.startswith('红色看台背壳_2_'):
        bpy.data.objects.remove(ob, do_unlink=True)

ports = json.loads((ROOT / 'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))['ports']

for sector in range(48):
    a0 = sector * math.tau / 48.0 + 0.006
    a1 = (sector + 1) * math.tau / 48.0 - 0.006
    rows_a = 16
    z_steps = 10
    vs = []
    for kz in range(z_steps + 1):
        zf = kz / z_steps
        for j in range(rows_a + 1):
            a = a0 + (a1 - a0) * j / rows_a
            rx, ry, z_lin = shell2_profile(zf)
            # Match exact saddle height drop of correct_roof.py on 三层看台_层3
            a_tier = math.atan2((ry * math.sin(a)) / 155.0, (rx * math.cos(a)) / 132.0)
            z = z_lin - 12.5 * (math.sin(a_tier) ** 4) * min(1.0, max(0.0, (z_lin - 24.0) / 22.0))
            vs.append((rx * math.cos(a), ry * math.sin(a), z))
    fs = []
    stride = rows_a + 1
    for kz in range(z_steps):
        for j in range(rows_a):
            v0 = kz * stride + j
            v1 = v0 + 1
            v2 = (kz + 1) * stride + j + 1
            v3 = (kz + 1) * stride + j
            fs.append((v0, v1, v2, v3))
    me = bpy.data.meshes.new(f'红色看台背壳_2_{sector:02d}')
    me.from_pydata(vs, [], fs)
    me.materials.append(facade_red)
    me.update()
    assign_metre_uv(me, 2.0)
    ob = bpy.data.objects.new(f'红色看台背壳_2_{sector:02d}', me)
    COL['13'].objects.link(ob)
    mod = ob.modifiers.new('实体厚度_Unity正反可见', 'SOLIDIFY')
    mod.thickness = 0.25
    mod.offset = -1.0
    mod.use_even_offset = True
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    ob.modifiers.clear()
    ob.data = new_me
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    remove = []
    for f in bm.faces:
        pts_f = [ob.matrix_world @ v.co for v in f.verts] + [ob.matrix_world @ f.calc_center_median()]
        c = pts_f[-1]
        hit_portal = False
        for p in ports:
            entry = Vector(p['entry'])
            rad = Vector((math.cos(p['angle']), math.sin(p['angle']), 0.0))
            tan = Vector((-rad.y, rad.x, 0.0))
            for pt in pts_f:
                d = pt - entry
                if -2.0 < d.dot(rad) < p['length'] + 2.2 and abs(d.dot(tan)) < 2.15 and pt.z < p['height'] + 3.2:
                    hit_portal = True
                    break
            if hit_portal:
                break
        if not hit_portal and min(pt.z for pt in pts_f) < 28.5:
            for p in f4_ports:
                entry = Vector(p['entry'])
                rad = Vector(p['rad'])
                tan = Vector(p['tan'])
                for pt in pts_f:
                    d = pt - entry
                    if -1.8 < d.dot(rad) < p['length'] + 2.2 and abs(d.dot(tan)) < 1.85 and pt.z < p['height'] + 3.2:
                        hit_portal = True
                        break
                if hit_portal:
                    break
        if hit_portal:
            remove.append(f)
    if remove:
        bmesh.ops.delete(bm, geom=remove, context='FACES')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()

# ---------------------------------------------------------------------------
# 5. Lower Excessively Tall Rear Stage Scaffolding Towers (42m -> 36.2m)
# ---------------------------------------------------------------------------
TOP_LIMIT = 36.2
for ob in list(COL['05'].objects):
    if ob.name.startswith('舞台支撑塔') and ob.type == 'MESH':
        # Tower beams are centered at z=21 with length 42 (0..42) -> lower top to TOP_LIMIT
        for v in ob.data.vertices:
            w_co = ob.matrix_world @ v.co
            if w_co.z > TOP_LIMIT:
                w_co.z = TOP_LIMIT
                v.co = ob.matrix_world.inverted() @ w_co
        ob.data.update()
    elif ob.name.startswith(('塔架交叉撑', '塔架横撑')) and ob.type == 'MESH':
        zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
        if max(zs) > TOP_LIMIT + 0.15:
            bpy.data.objects.remove(ob, do_unlink=True)
    elif ob.name.startswith(('后部横向桁架', '桁架斜撑')) and ob.type == 'MESH':
        if ob.location.z > 38.0:
            ob.location.z = 36.0
    elif ob.name.startswith('信封吊索') and ob.type == 'CURVE':
        for sp in ob.data.splines:
            for pt in sp.points:
                if pt.co.z > 39.2:
                    pt.co.z = 39.2

bpy.context.view_layer.update()

# ---------------------------------------------------------------------------
# 6. Automated Audit: Roof Rim Protrusions, Bowl Exposure, and V10/V12 Clearances
# ---------------------------------------------------------------------------
dg = bpy.context.evaluated_depsgraph_get()
steel_protrusions = 0
max_rim_excess = 0.0
for ob in COL['01'].objects:
    if ob.type != 'MESH':
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    for v in me.vertices:
        w = ob.matrix_world @ v.co
        # Check radial distance in roof coordinates
        a = math.atan2(w.y / 166.8, w.x / 148.0)
        z_rim = roofSurfZ(0.0, a)
        # Near outer perimeter (h > 0.85), no vertex should exceed roofSurfZ(0, a) + 0.45m
        r_norm = math.hypot(w.x / 148.0, w.y / 166.8)
        if r_norm > 0.94:
            excess = w.z - (z_rim + 0.42)
            if excess > max_rim_excess:
                max_rim_excess = excess
            if excess > 0.05:
                steel_protrusions += 1
    ev.to_mesh_clear()

# Check that 三层看台_层3 has 0 vertices protruding outside 红色看台背壳_2_*
shell_verts, shell_faces = [], []
for ob in S.objects:
    if ob.type == 'MESH' and ob.name.startswith('红色看台背壳_2_'):
        me = ob.evaluated_get(dg).to_mesh()
        off = len(shell_verts)
        shell_verts.extend(ob.matrix_world @ v.co for v in me.vertices)
        shell_faces.extend([off + i for i in p.vertices] for p in me.polygons)
        ob.evaluated_get(dg).to_mesh_clear()

# Verify V10 upper-tier samples & routes still have 0 headroom/floor failures
arch_verts, arch_faces, arch_names = [], [], []
for ob in S.objects:
    col_prefix = next((c.name[:2] for c in ob.users_collection), None)
    if ob.type != 'MESH' or col_prefix in ['04', '07', '10', '11', '12', '16', '19', '20']:
        continue
    if ob.name.startswith(('看台座椅_', '内场折叠椅_', 'NEAR_')) or ob.name == '灯束薄雾范围':
        continue
    me = ob.evaluated_get(dg).to_mesh()
    off = len(arch_verts)
    arch_verts.extend(ob.matrix_world @ v.co for v in me.vertices)
    for p in me.polygons:
        arch_faces.append([off + i for i in p.vertices])
        arch_names.append(ob.name)
    ob.evaluated_get(dg).to_mesh_clear()

arch_tree = BVHTree.FromPolygons(arch_verts, arch_faces)
v10_data = json.loads((ROOT / 'unity_enhanced/checks/upper_tier_v10.json').read_text(encoding='utf-8'))
v10_failures = []
for s_pt in v10_data['samples']:
    q = Vector(s_pt['point'])
    hit_f, _, idx_f, _ = arch_tree.ray_cast(q + Vector((0, 0, 0.04)), Vector((0, 0, -1)), 0.12)
    if hit_f is None or abs(hit_f.z - q.z) > 0.03:
        v10_failures.append({'type': 'floor', 'sample': s_pt, 'hit': arch_names[idx_f] if hit_f else None})
        continue
    hit_h, _, idx, _ = arch_tree.ray_cast(q + Vector((0, 0, 0.04)), Vector((0, 0, 1)), 2.1)
    if hit_h is not None:
        v10_failures.append({'type': 'headroom', 'sample': s_pt, 'hit': arch_names[idx], 'z': hit_h.z})
for r in v10_data['routes']:
    for a_pt, b_pt in zip(r['points'], r['points'][1:]):
        va, vb = Vector(a_pt), Vector(b_pt)
        d = vb - va
        if d.length > 0.03:
            hit_r, _, idx_r, _ = arch_tree.ray_cast(va, d.normalized(), max(0.0, d.length - 0.02))
            if hit_r is not None:
                v10_failures.append({'type': 'route', 'kind': r['kind'], 'hit': arch_names[idx_r]})

assert steel_protrusions == 0, f"Found {steel_protrusions} steel vertices protruding above roof rim (max excess {max_rim_excess:.3f}m)"
assert len(v10_failures) == 0, f"V10 clearance regressions: {len(v10_failures)} ({v10_failures[:5]})"

S['exterior_shell_v13'] = True
audit_report = {
    'removed_old_steel_objects': removed_steel,
    'new_steel_objects': len(COL['01'].objects),
    'steel_rim_protrusions': steel_protrusions,
    'max_rim_excess_m': round(max_rim_excess, 4),
    'v10_clearance_samples_checked': len(v10_data['samples']),
    'v10_clearance_failures': len(v10_failures),
    'stage_tower_top_m': TOP_LIMIT,
    'roof_membrane_rings': len(u_steps),
    'upper_bowl_sectors_rebuilt': 48,
}
(ROOT / 'unity_enhanced/checks/exterior_shell_v13.json').write_text(
    json.dumps(audit_report, ensure_ascii=False, indent=2), encoding='utf-8'
)

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / '赵雷2026_鸟巢_看台后缘补齐版.blend'))
print("V13_EXTERIOR_SUCCESS:", json.dumps(audit_report, ensure_ascii=False))
