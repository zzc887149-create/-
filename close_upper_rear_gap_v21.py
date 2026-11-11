"""V21: Close the structural and visual gap between the uppermost 3rd-tier rear audience rows
(三层看台_层3, t=2, j=18) and the Bird's Nest stadium building envelope & saddle roof:
1. Build a continuous 360-degree Upper-Tier Rear Concourse Promenade Deck, Rear Seat-Back Parapet,
   and Safety Handrail (V21_最上层看台后缘环廊平台 & V21_最上层看台后缘护栏) bridging from the back of
   row 18 (rx=139.9m, ry=164.9m) radially outward to the Bird's Nest outer building envelope.
2. Rebuild 红色看台背壳_V20_连续底壳 so that instead of terminating at the floor of row 18 (z=32.87..44.73m),
   it continues outward beneath the Upper-Tier Rear Concourse Deck and rises continuously along the
   upper bowl shoulder (between the inner and outer faces of the woven steel columns) all the way up
   to the PTFE马鞍形屋面 saddle roof outer rim (z=37.20..66.40m) with an inward roof-underside collar.
3. Restore the top 3 central aisle terraces (j=16, 17, 18, r=17.6..20.9m) behind the inward-facing
   L3_upper_middle portal hood and enclose the 24 upper switchback stair cores (V21_上层折返核外包壁)
   so zero sky leaks through the 3rd-tier aisles or portals.
"""
import bpy, bmesh, math, json, ast, bisect
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
S = bpy.data.scenes['赵雷2026_没有信号_鸟巢复刻']
D = bpy.data.scenes['UNITY_ENHANCED_V3']
bpy.context.window.scene = S

C27 = next(c for c in S.collection.children if c.name.startswith('27_'))
C = C27
C13 = next(c for c in S.collection.children if c.name.startswith('13_'))
N = 24
PHASE = .03834
HALF = 2.4
tables = {}

M = {n: bpy.data.materials[n] for n in ('concrete', '外碗赭红混凝土', '栏杆细金属')}

# Load exact v20 coordinate helpers
tree = ast.parse((ROOT / 'rebuild_seating_v20.py').read_text(encoding='utf-8'))
defs = [
    n for n in tree.body
    if isinstance(n, (ast.FunctionDef, ast.ClassDef))
    or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('CF', 'CV', 'TIERS') for t in n.targets))
]
exec(compile(ast.Module(body=defs, type_ignores=[]), 'v20_helpers', 'exec'))

# Saddle roof & outer facade envelope functions from refine_exterior_shell_v13.py
def roofR(u):
    return (148.0 - 86.0 * u, 166.8 - 75.8 * u)

def roofSurfZ(u, a):
    base = 51.8 + 14.6 * math.cos(2.0 * a)
    return base - 2.0 * (u ** 1.35)

def facadeR(h):
    bow = math.sin(math.pi * h)
    return (137.0 + 11.0 * h + 1.10 * bow, 155.0 + 11.8 * h + 1.45 * bow)

def facadePos(h, a, dr=0.0, z_override=None):
    rx, ry = facadeR(h)
    rx += dr
    ry += dr
    z = (h * roofSurfZ(0.0, a)) if z_override is None else z_override
    return Vector((rx * math.cos(a), ry * math.sin(a), z))

# Remove any previous V21 objects if re-running
for ob in list(S.objects):
    if ob.name.startswith(('V21_', '红色看台背壳_')):
        bpy.data.objects.remove(ob, do_unlink=True)

# ---------------------------------------------------------------------------
# 1. Build Upper-Tier Rear Concourse Promenade Deck, Seat-Back Parapet & Guardrail
#    + Restore rows j=16,17,18 central terrace behind L3_upper_middle portal hood
#    + Enclose the 24 upper switchback stair cores (V21_上层折返核外包壁)
# ---------------------------------------------------------------------------
rear_deck = Mesh('V21_最上层看台后缘环廊平台', M['concrete'])
rear_parapet = Mesh('V21_最上层看台后排挡墙', M['外碗赭红混凝土'])
rear_rail = Mesh('V21_最上层看台后缘护栏', M['栏杆细金属'])
core_hood = Mesh('V21_上层折返核外包壁', M['外碗赭红混凝土'])
top_aisle_infill = Mesh('V21_三层看台顶段中央阶梯补全', M['concrete'])

rx2, ry2, n2, step2 = TIERS[2]  # (119, 144, 19, 1.1)
r_top_row = n2 * step2          # 19 * 1.1 = 20.9m -> rx=139.9, ry=164.9

# 1a. Continuous 360-degree Upper Rear Concourse Deck & Parapet behind row 18
L_top = table(2, r_top_row)[2]
sub_per_bay = 16
for b in range(N):
    w_bay = L_top / N
    for k in range(sub_per_bay):
        w0 = k * w_bay / sub_per_bay
        w1 = (k + 1) * w_bay / sub_per_bay
        u0 = b / N + PHASE + w0 / L_top
        u1 = b / N + PHASE + w1 / L_top
        a0 = angle(2, r_top_row, u0)
        a1 = angle(2, r_top_row, u1)
        z0 = h(2, 18, a0)
        z1 = h(2, 18, a1)
        # Deck top sits +0.48m above row 18 floor (one comfortable step above the last row)
        zd0 = z0 + 0.48
        zd1 = z1 + 0.48
        zb0 = z0 - 0.35
        zb1 = z1 - 0.35

        # Inner edge overlaps 0.08m into row 18 (r = 20.82m) so there is zero seam
        p_in0 = Vector(((rx2 + 20.82) * math.cos(a0), (ry2 + 20.82) * math.sin(a0), 0.0))
        p_in1 = Vector(((rx2 + 20.82) * math.cos(a1), (ry2 + 20.82) * math.sin(a1), 0.0))

        # Mid edge at r = 21.22m (back of front curb / parapet)
        p_mid0 = Vector(((rx2 + 21.22) * math.cos(a0), (ry2 + 21.22) * math.sin(a0), 0.0))
        p_mid1 = Vector(((rx2 + 21.22) * math.cos(a1), (ry2 + 21.22) * math.sin(a1), 0.0))

        # Outer edge meets the Bird's Nest outer bowl wall at facadePos(h_d, a, dr=-0.12)
        hd0 = min(0.96, max(0.55, zd0 / roofSurfZ(0.0, a0)))
        hd1 = min(0.96, max(0.55, zd1 / roofSurfZ(0.0, a1)))
        p_out0 = facadePos(hd0, a0, dr=-0.12, z_override=0.0)
        p_out1 = facadePos(hd1, a1, dr=-0.12, z_override=0.0)

        # Concourse slab from p_in to p_out
        rear_deck.prism(
            [(p_in0.x, p_in0.y), (p_out0.x, p_out0.y), (p_out1.x, p_out1.y), (p_in1.x, p_in1.y)],
            [zd0, zd0, zd1, zd1],
            [zb0, zb0, zb1, zb1]
        )

        # Behind seating blocks (w0 >= HALF and w1 <= w_bay - HALF), add a solid seat-back parapet
        # rising to z + 1.38m so top-row spectators have an immediate architectural backing behind their seats
        in_aisle = (w0 < HALF - 0.05) or (w1 > w_bay - HALF + 0.05)
        if not in_aisle:
            rear_deck.prism(
                [(p_in0.x, p_in0.y), (p_mid0.x, p_mid0.y), (p_mid1.x, p_mid1.y), (p_in1.x, p_in1.y)],
                [z0 + 1.32, z0 + 1.32, z1 + 1.32, z1 + 1.32],
                [zd0, zd0, zd1, zd1]
            )

        # Outer perimeter spandrel curb where the rear deck meets the upper red bowl wall
        p_wall_in0 = facadePos(hd0, a0, dr=-0.42, z_override=0.0)
        p_wall_in1 = facadePos(hd1, a1, dr=-0.42, z_override=0.0)
        rear_parapet.prism(
            [(p_wall_in0.x, p_wall_in0.y), (p_out0.x, p_out0.y), (p_out1.x, p_out1.y), (p_wall_in1.x, p_wall_in1.y)],
            [zd0 + 1.85, zd0 + 1.85, zd1 + 1.85, zd1 + 1.85],
            [zb0, zb0, zb1, zb1]
        )

    # Continuous handrail along the rear concourse inner edge (r = 21.05m)
    rail_pts = []
    for k in range(sub_per_bay + 1):
        u = b / N + PHASE + (k / sub_per_bay) / N
        a = angle(2, r_top_row, u)
        z = h(2, 18, a) + 0.48
        rail_pts.append(Vector(((rx2 + 21.05) * math.cos(a), (ry2 + 21.05) * math.sin(a), z)))
    track(rear_rail, rail_pts)

    # 1b. Restore central terrace infill on Tier 3 for row j=18 (r = 19.8..20.9m) and any row j>=16
    # that is completely clear of the L3_upper_middle portal (r <= 17.35m).
    for j in (16, 17, 18):
        r0 = max(j * step2, 17.65)
        r1 = (j + 1) * step2
        if r0 < r1 and (j == 18 or H(2, j, b) >= H(2, 15, b) + 2.35):
            tile(top_aisle_infill, 2, b, r0, r1, -1.2, 1.2, lambda w, jj=j, bb=b: H(2, jj, bb, w))

    # 1c. Enclose the back & sides of the 24 upper switchback stair cores (V20_上层折返核_%02d)
    # strictly outside the walking envelope so no sky is visible through the portals or aisles.
    levels = [22.5, H(2, 0, b) - 2.4, H(2, 4, b), H(2, 15, b)]
    short = (levels[3] - levels[2]) < 3.6
    back = 15.35 if short else 14.30
    r_core_back = 17.42  # Behind both the rear landing and the L3_upper_middle tunnel (which ends at r=17.20m)
    z_core_top = levels[3] + 2.68
    z_core_bot = 22.25
    # Back wall behind the entire core & upper_middle portal hood (at r = 17.42..17.66m)
    tile(core_hood, 2, b, r_core_back, r_core_back + 0.24, -1.48, 1.48, z_core_top, z_core_top - z_core_bot)
    # Left side wall (w = -1.48..-1.30, full height from 22.25m to z_core_top)
    tile(core_hood, 2, b, 9.15, r_core_back + 0.24, -1.48, -1.30, z_core_top, z_core_top - z_core_bot)
    # Right side wall above F4 bridge headroom (z = 25.10m to z_core_top, w = +1.30..+1.48)
    tile(core_hood, 2, b, 9.15, r_core_back + 0.24, 1.30, 1.48, z_core_top, z_core_top - 25.10)
    # Roof cap over switchback core (from r = 9.15 to r_core_back + 0.24, w = -1.48 .. +1.48)
    tile(core_hood, 2, b, 9.15, r_core_back + 0.24, -1.48, 1.48, z_core_top + 0.20, 0.22)
    # Bottom soffit under F4 bridge & core (top at 22.34m, thickness 0.16m -> bottom at 22.18m)
    tile(core_hood, 2, b, 2.65, r_core_back + 0.24, -1.48, 3.35, 22.34, 0.16)

rear_deck.finish(C27)
rear_parapet.finish(C13)
rear_rail.finish(C27)
core_hood.finish(C13)
top_aisle_infill.finish(C27)

# ---------------------------------------------------------------------------
# 2. Rebuild 红色看台背壳_V20_连续底壳 so it extends from the ground (z=0.05m)
#    all the way up to the PTFE马鞍形屋面 Saddle Roof Rim (z=37.2..66.4m)
# ---------------------------------------------------------------------------
profiles = [(0, 0, 0, -1.15)]
for t, (_, _, nn, step) in enumerate(TIERS):
    if t:
        profiles.append((t, 0, 0, -0.35))
    profiles.extend((t, j, (j + 1) * step, -0.35) for j in range(nn))

vs = []
fs = []
segments = 1120

# 2a. Stepped seating bowl underside rings (identical to v20b up to row 18 of Tier 3)
for t, j, r, dz in profiles:
    rx, ry, _, _ = TIERS[t]
    for i in range(segments):
        u = i / segments
        a = angle(t, r, u)
        vs.append(((rx + r) * math.cos(a), (ry + r) * math.sin(a), h(t, j, a) + dz))

# 2b. Upper bowl extension rings:
# Ring U0: radially outward under the Upper-Tier Rear Concourse Deck to facadePos(hd, a, dr=-0.06)
# Rings U1..U8: rising along the Bird's Nest upper bowl shoulder (dr=-0.06, inside the outer face of
#               the woven steel columns and behind their inner face) up to the saddle roof rim (u=0)
# Ring U9: inward roof-underside collar at u=0.055 sealing against PTFE马鞍形屋面
upper_steps = 8
for step_idx in range(upper_steps + 2):
    for i in range(segments):
        u = i / segments
        a = angle(2, r_top_row, u)
        z_row18 = h(2, 18, a) - 0.35
        z_roof0 = roofSurfZ(0.0, a) - 0.03
        hd = min(0.95, max(0.55, (z_row18 + 0.83) / roofSurfZ(0.0, a)))
        if step_idx == 0:
            # Outer edge of rear concourse deck soffit
            p = facadePos(hd, a, dr=-0.06, z_override=z_row18)
            vs.append((p.x, p.y, p.z))
        elif step_idx <= upper_steps:
            f = step_idx / upper_steps
            h_cur = hd + (1.0 - hd) * f
            z_cur = z_row18 * (1.0 - f) + z_roof0 * f
            p = facadePos(h_cur, a, dr=-0.06, z_override=z_cur)
            vs.append((p.x, p.y, p.z))
        else:
            # Inward collar under PTFE马鞍形屋面 at u = 0.055
            u_roof = 0.055
            rx_r, ry_r = roofR(u_roof)
            z_r = roofSurfZ(u_roof, a) - 0.10
            vs.append((rx_r * math.cos(a), ry_r * math.sin(a), z_r))

total_rings = len(profiles) + upper_steps + 2
for j in range(total_rings - 1):
    for i in range(segments):
        k = (i + 1) % segments
        fs.append((j * segments + i, j * segments + k, (j + 1) * segments + k, (j + 1) * segments + i))

me = bpy.data.meshes.new('V21_随阶梯与上碗封顶连续碗壁')
me.from_pydata(vs, [], fs)
me.materials.append(M['外碗赭红混凝土'])
me.update()

ob = bpy.data.objects.new('红色看台背壳_V20_连续底壳', me)
C13.objects.link(ob)

mod = ob.modifiers.new('封闭墙厚', 'SOLIDIFY')
mod.thickness = 0.16
mod.offset = -1
dg = bpy.context.evaluated_depsgraph_get()
ob.data = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
ob.modifiers.clear()

# Cut route openings using v20_cutters.json
data = json.loads((ROOT / 'unity_enhanced/checks/v20_cutters.json').read_text(encoding='utf-8'))
cut_me = bpy.data.meshes.new('V21_all_routes')
cut_me.from_pydata(data['v'], [], data['f'])
cut_me.update()
cut_ob = bpy.data.objects.new('V21_all_routes', cut_me)
S.collection.objects.link(cut_ob)
bpy.context.view_layer.update()

mod = ob.modifiers.new('真实入口开洞', 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = cut_ob
mod.use_self = True
dg = bpy.context.evaluated_depsgraph_get()
ob.data = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
ob.modifiers.clear()
bpy.data.objects.remove(cut_ob, do_unlink=True)

uv = ob.data.uv_layers.new(name='MetreUV')
for f in ob.data.polygons:
    axes = [k for k in range(3) if k != max(range(3), key=lambda k: abs(f.normal[k]))]
    for li in f.loop_indices:
        v = ob.data.vertices[ob.data.loops[li].vertex_index].co
        uv.data[li].uv = (v[axes[0]], v[axes[1]])

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('V21 upper rear gap closure complete; bowl max z:', round(max(v.co.z for v in ob.data.vertices), 2))
