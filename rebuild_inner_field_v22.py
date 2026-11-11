"""Rebuild the inner-field (内场) seating blocks, crowd, phones, barriers, and central FOH (中控台)
to match the official Zhao Lei 2026 Bird's Nest Concert seating chart (bdb_aug2.png):
- Front 3 rows of blocks (Row A, Row B, Row C): 6 blocks per row (3 left, central aisle, 3 right)
- Rear 2 rows of blocks (Row D, Row E): 4 blocks per row (2 left, 2 right)
- Central FOH (中控台) in the center of Row D (spanning Col 2 & Col 3), with open center behind it in Row E.
- Preserves 09_纪念座椅 at (-2.2, 41.7) untouched in the front-inner foreground of A3.
"""
import bpy, bmesh, math, random, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
OUT = ROOT / 'unity_enhanced'
PKG = OUT / 'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'

S = bpy.data.scenes['赵雷2026_没有信号_鸟巢复刻']
D = bpy.data.scenes['UNITY_ENHANCED_V3']
root = D.objects['BirdsNest_Enhanced_360']

c06 = bpy.data.collections['06_内场折叠椅']
c07 = bpy.data.collections['07_观众与手机灯']
c18 = next(c for c in S.collection.children if c.name.startswith('18_'))

# 1. Remove old inner-field objects in 06_内场折叠椅
for ob in list(c06.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# Remove old field-only crowd/phone meshes in 07_观众与手机灯 and NEAR_近场圆润头部 in 18_*
for ob in list(c07.objects):
    if ob.name.startswith('观众衣着_') or ob.name in ('观众头部_远景', '全场手机星光'):
        bpy.data.objects.remove(ob, do_unlink=True)
for ob in list(S.objects):
    if ob.name.startswith('NEAR_'):
        bpy.data.objects.remove(ob, do_unlink=True)

# Remove old inner-field chunks in D (UNITY_ENHANCED_V3)
for ob in list(D.objects):
    if any(k in ob.name for k in ('Chunk_CHAIRS_F_', 'Chunk_CROWD_F_', 'Chunk_PHONES_F_')):
        bpy.data.objects.remove(ob, do_unlink=True)

M = {n: bpy.data.materials[n] for n in (
    'steel', 'dark', 'black', 'chair', 'skin', 'phone', 'warm', 'amber',
    '栏杆细金属', '导向标识白漆', '内场橡胶防护板'
)}
cloth_mats = [bpy.data.materials[f'观众织物_{i}'] for i in range(5)]
cloth_colors = [tuple(m.diffuse_color) for m in cloth_mats]
skin_color = tuple(M['skin'].diffuse_color)

CF = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
CV = [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
OF = [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]

class Builder:
    def __init__(self, name, mat):
        self.name = name
        self.mat = mat
        self.v = []
        self.f = []
        self.smooth = []
    def box(self, p, size, rz=0.0, rx=0.0):
        k = len(self.v)
        cz, sz = math.cos(rz), math.sin(rz)
        cx, sx = math.cos(rx), math.sin(rx)
        for vx, vy, vz in CV:
            x, y, z = vx * size[0], vy * size[1], vz * size[2]
            if rx:
                y, z = cx * y - sx * z, sx * y + cx * z
            if rz:
                x, y = cz * x - sz * y, sz * x + cz * y
            self.v.append((p[0] + x, p[1] + y, p[2] + z))
        self.f.extend(tuple(k + i for i in f) for f in CF)
        self.smooth.extend([False] * 6)
    def oct(self, p, r):
        k = len(self.v)
        x, y, z = p
        self.v.extend([(x+r,y,z),(x-r,y,z),(x,y+r,z),(x,y-r,z),(x,y,z+r),(x,y,z-r)])
        self.f.extend(tuple(k + i for i in f) for f in OF)
        self.smooth.extend([False] * 8)
    def round_head(self, p):
        k = len(self.v)
        for zz, rr in [(-0.11, 0.065), (-0.065, 0.11), (0.065, 0.105), (0.125, 0.05)]:
            for idx in range(8):
                a = idx * math.tau / 8
                self.v.append((p[0] + rr * math.cos(a), p[1] + rr * 0.88 * math.sin(a), p[2] + zz))
        for j in range(3):
            for idx in range(8):
                self.f.append(tuple(k + n for n in [j*8+idx, j*8+(idx+1)%8, (j+1)*8+(idx+1)%8, (j+1)*8+idx]))
                self.smooth.append(True)
        self.f.append(tuple(k + idx for idx in range(7, -1, -1)))
        self.smooth.append(True)
        self.f.append(tuple(k + 24 + idx for idx in range(8)))
        self.smooth.append(True)
    def finish(self, col):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.materials.append(self.mat)
        for poly, sm in zip(me.polygons, self.smooth):
            poly.use_smooth = sm
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        col.objects.link(ob)
        return ob

# 2. Define the 6 Columns and 5 Rows (6 + 6 + 6 + 4 + 4 = 26 seating blocks)
COLS = [
    (-55.2, -39.6),  # Col 0 (Outer Left: A1, B1, C1, D1, E1)
    (-36.8, -20.6),  # Col 1 (Mid Left:   A2, B2, C2, D2, E2)
    (-17.8,  -1.8),  # Col 2 (Inner Left: A3, B3, C3)
    (  1.8,  17.8),  # Col 3 (Inner Right: A4, B4, C4)
    ( 20.6,  36.8),  # Col 4 (Mid Right:  A5, B5, C5, D3, E3)
    ( 39.6,  55.2),  # Col 5 (Outer Right: A6, B6, C6, D4, E4)
]

# Each block: (block_name, row_idx, col_idx, x0, x1, y0, y1)
# Placed across y in [-52.0, +40.4] so all 5 rows + FOH are 100% visible in VIEW_04, VIEW_05, VIEW_06, VIEW_09
BLOCKS = [
    # Row A (Front row, 6 blocks: A1..A6)
    ('A1', 0, 0, -55.2, -39.6,  24.0,  40.4),
    ('A2', 0, 1, -36.8, -20.6,  24.0,  40.4),
    ('A3', 0, 2, -17.8,  -1.8,  24.0,  38.6),  # recessed behind central thrust & memorial chair at (-2.2, 41.7)
    ('A4', 0, 3,   1.8,  17.8,  24.0,  38.6),
    ('A5', 0, 4,  20.6,  36.8,  24.0,  40.4),
    ('A6', 0, 5,  39.6,  55.2,  24.0,  40.4),
    # Row B (2nd row, 6 blocks: B1..B6)
    ('B1', 1, 0, -55.2, -39.6,   6.2,  20.8),
    ('B2', 1, 1, -36.8, -20.6,   6.2,  20.8),
    ('B3', 1, 2, -17.8,  -1.8,   6.2,  20.8),
    ('B4', 1, 3,   1.8,  17.8,   6.2,  20.8),
    ('B5', 1, 4,  20.6,  36.8,   6.2,  20.8),
    ('B6', 1, 5,  39.6,  55.2,   6.2,  20.8),
    # Row C (3rd row, 6 blocks: C1..C6; C3 & C4 slightly shorter at rear to frame FOH)
    ('C1', 2, 0, -55.2, -39.6, -11.6,   3.0),
    ('C2', 2, 1, -36.8, -20.6, -11.6,   3.0),
    ('C3', 2, 2, -17.8,  -1.8,  -9.8,   3.0),
    ('C4', 2, 3,   1.8,  17.8,  -9.8,   3.0),
    ('C5', 2, 4,  20.6,  36.8, -11.6,   3.0),
    ('C6', 2, 5,  39.6,  55.2, -11.6,   3.0),
    # Row D (4th row, 4 blocks: D1, D2 | [Central FOH] | D3, D4)
    ('D1', 3, 0, -55.2, -39.6, -31.0, -14.8),
    ('D2', 3, 1, -36.8, -20.6, -31.0, -14.8),
    ('D3', 3, 4,  20.6,  36.8, -31.0, -14.8),
    ('D4', 3, 5,  39.6,  55.2, -31.0, -14.8),
    # Row E (5th row, 4 blocks: E1, E2 | [Open Center behind FOH] | E3, E4)
    ('E1', 4, 0, -55.2, -39.6, -51.5, -34.2),
    ('E2', 4, 1, -36.8, -20.6, -51.5, -34.2),
    ('E3', 4, 4,  20.6,  36.8, -51.5, -34.2),
    ('E4', 4, 5,  39.6,  55.2, -51.5, -34.2),
]

chair_body = Builder('内场折叠椅_座与靠背', M['chair'])
chair_legs = Builder('内场折叠椅_金属椅腿', M['steel'])
crowd_builders = [Builder(f'观众衣着_{i}', cloth_mats[i]) for i in range(5)]
far_heads = Builder('观众头部_远景', M['skin'])
near_heads = Builder('NEAR_近场圆润头部', M['skin'])
phones = Builder('全场手机星光', M['phone'])

# Also accumulate directly into D (UNITY_ENHANCED_V3) spatial buckets so export is fast & exact
bne_chair = bpy.data.materials['BNE_023']
bne_steel = bpy.data.materials['BNE_000']
bne_crowd = bpy.data.materials['BNE_006']
bne_phone = bpy.data.materials['BNE_025']

d_buckets = {}
def get_d_bucket(cat, reg, mat_obj, has_color=False):
    key = (cat, reg, mat_obj.name)
    if key not in d_buckets:
        d_buckets[key] = {'v': [], 'f': [], 'color': [] if has_color else None, 'smooth': [], 'mat': mat_obj, 'cat': cat}
    return d_buckets[key]

def d_add_box(b, p, size, color=None):
    k = len(b['v'])
    for vx, vy, vz in CV:
        b['v'].append((p[0] + vx*size[0], p[1] + vy*size[1], p[2] + vz*size[2]))
    b['f'].extend(tuple(k + i for i in f) for f in CF)
    b['smooth'].extend([False] * 6)
    if b['color'] is not None:
        b['color'].extend([color] * 8)

def d_add_oct(b, p, r, color=None):
    k = len(b['v'])
    x, y, z = p
    b['v'].extend([(x+r,y,z),(x-r,y,z),(x,y+r,z),(x,y-r,z),(x,y,z+r),(x,y,z-r)])
    b['f'].extend(tuple(k + i for i in f) for f in OF)
    b['smooth'].extend([False] * 8)
    if b['color'] is not None:
        b['color'].extend([color] * 6)

def d_add_round_head(b, p, color):
    k = len(b['v'])
    for zz, rr in [(-0.11, 0.065), (-0.065, 0.11), (0.065, 0.105), (0.125, 0.05)]:
        for idx in range(8):
            a = idx * math.tau / 8
            b['v'].append((p[0] + rr * math.cos(a), p[1] + rr * 0.88 * math.sin(a), p[2] + zz))
    for j in range(3):
        for idx in range(8):
            b['f'].append(tuple(k + n for n in [j*8+idx, j*8+(idx+1)%8, (j+1)*8+(idx+1)%8, (j+1)*8+idx]))
            b['smooth'].append(True)
    b['f'].append(tuple(k + idx for idx in range(7, -1, -1)))
    b['smooth'].append(True)
    b['f'].append(tuple(k + 24 + idx for idx in range(8)))
    b['smooth'].append(True)
    if b['color'] is not None:
        b['color'].extend([color] * 32)

def field_region(x, y):
    return 'F_%d_%d' % (math.floor((x + 80.0) / 32.0), math.floor((y + 115.0) / 32.0))

rng = random.Random(20260802)
DX = 0.74
DY = 1.06

total_chairs = 0
total_spectators = 0
total_phones = 0
near_head_count = 0

for bname, r_idx, c_idx, x0, x1, y0, y1 in BLOCKS:
    nx = int((x1 - x0) / DX)
    ny = int((y1 - y0) / DY)
    x_start = x0 + 0.5 * ((x1 - x0) - (nx - 1) * DX)
    y_start = y0 + 0.5 * ((y1 - y0) - (ny - 1) * DY)
    for iy in range(ny):
        y = y_start + iy * DY
        for ix in range(nx):
            x = x_start + ix * DX
            if (x / 69.5) ** 2 + (y / 99.0) ** 2 > 0.94:
                continue
            if abs(x - (-2.2)) < 1.1 and abs(y - 41.7) < 1.1:
                continue
            total_chairs += 1
            reg = field_region(x, y)

            # Chair geometry in S and D (matching build_concert.py heights: seat z=0.46, back z=0.77, legs z=0.25)
            chair_body.box((x, y, 0.46), (0.45, 0.43, 0.07))
            chair_body.box((x, y - 0.22, 0.77), (0.45, 0.06, 0.52))
            for xx in (-0.18, 0.18):
                chair_legs.box((x + xx, y - 0.15, 0.25), (0.026, 0.027, 0.50))
                chair_legs.box((x + xx, y + 0.15, 0.25), (0.026, 0.027, 0.50))

            db_c = get_d_bucket('CHAIRS', reg, bne_chair, False)
            d_add_box(db_c, (x, y, 0.46), (0.45, 0.43, 0.07))
            d_add_box(db_c, (x, y - 0.22, 0.77), (0.45, 0.06, 0.52))
            db_l = get_d_bucket('CHAIRS', reg, bne_steel, False)
            for xx in (-0.18, 0.18):
                d_add_box(db_l, (x + xx, y - 0.15, 0.25), (0.026, 0.027, 0.50))
                d_add_box(db_l, (x + xx, y + 0.15, 0.25), (0.026, 0.027, 0.50))

            # Spectator (~90% occupancy)
            if rng.random() < 0.90:
                total_spectators += 1
                ci = rng.randrange(5)
                crowd_builders[ci].box((x, y, 1.08), (0.39, 0.32, 0.67))
                db_cr = get_d_bucket('CROWD', reg, bne_crowd, True)
                d_add_box(db_cr, (x, y, 1.08), (0.39, 0.32, 0.67), cloth_colors[ci])

                if abs(x) < 33.0 and 8.0 < y < 43.0:
                    near_head_count += 1
                    near_heads.round_head((x, y, 1.62))
                    d_add_round_head(db_cr, (x, y, 1.62), skin_color)
                else:
                    far_heads.oct((x, y, 1.62), 0.13)
                    d_add_oct(db_cr, (x, y, 1.62), 0.13, skin_color)

            # Phone light (~32% of seats)
            if rng.random() < 0.32:
                total_phones += 1
                ph_pos = (x + 0.15, y + 0.12, 1.70 + rng.random() * 0.38)
                phones.oct(ph_pos, 0.045)
                db_ph = get_d_bucket('PHONES', reg, bne_phone, False)
                d_add_oct(db_ph, ph_pos, 0.045)

chair_body.finish(c06)
chair_legs.finish(c06)
for cb in crowd_builders:
    cb.finish(c07)
far_heads.finish(c07)
near_heads.finish(c18)
phones.finish(c07)
S['v3_near_heads'] = near_head_count

# 3. Build Longitudinal & Transverse Aisle Crowd Barriers + Central FOH (中控台) in 06_内场折叠椅
barriers = Builder('内场分区护栏与立柱', M['栏杆细金属'])

def add_barrier_line_y(x, y0, y1):
    length = y1 - y0
    ym = 0.5 * (y0 + y1)
    barriers.box((x, ym, 0.98), (0.045, length, 0.045))
    barriers.box((x, ym, 0.52), (0.035, length, 0.035))
    n_posts = max(2, int(length / 3.2) + 1)
    for i in range(n_posts):
        yp = y0 + i * (length / (n_posts - 1))
        barriers.box((x, yp, 0.52), (0.06, 0.06, 1.02))
        barriers.box((x, yp, 0.025), (0.28, 0.16, 0.04))

def add_barrier_line_x(x0, x1, y):
    length = x1 - x0
    xm = 0.5 * (x0 + x1)
    barriers.box((xm, y, 0.98), (length, 0.045, 0.045))
    barriers.box((xm, y, 0.52), (length, 0.035, 0.035))
    n_posts = max(2, int(length / 3.2) + 1)
    for i in range(n_posts):
        xp = x0 + i * (length / (n_posts - 1))
        barriers.box((xp, y, 0.52), (0.06, 0.06, 1.02))
        barriers.box((xp, y, 0.025), (0.16, 0.28, 0.04))

# Longitudinal aisle barriers along the 5 rows
for x_aisle in (-56.0, -38.2, -19.2, 19.2, 38.2, 56.0):
    add_barrier_line_y(x_aisle, -52.0, 40.6)

# Central longitudinal aisle (x = -1.35 and x = +1.35) along Rows A, B, C (from FOH front y=-10.2 to y=+38.8)
for x_center in (-1.35, 1.35):
    add_barrier_line_y(x_center, -10.2, 21.0)
    add_barrier_line_y(x_center, 23.8, 38.8)

# Transverse aisle barriers between rows (A-B at y=22.4, B-C at y=4.6, C-D at y=-13.2, D-E at y=-32.6)
for y_trans in (22.4, 4.6, -13.2, -32.6):
    for c_idx, (cx0, cx1) in enumerate(COLS):
        if y_trans == -32.6 and c_idx in (2, 3):
            continue  # Open center behind FOH
        add_barrier_line_x(cx0, cx1, y_trans)

# Front stage-facing barrier across Row A (leaving memorial chair area open)
for c_idx, (cx0, cx1) in enumerate(COLS):
    if c_idx in (2, 3):
        continue
    add_barrier_line_x(cx0, cx1, 41.2)

# 4. Central FOH (中控台) Island in the middle of Row D (x in [-15.2, +15.2], y in [-31.5, -13.5], center y = -22.5)
FOH_Y = -22.5
add_barrier_line_x(-15.2, 15.2, FOH_Y + 9.0)
add_barrier_line_x(-15.2, 15.2, FOH_Y - 9.0)
add_barrier_line_y(-15.2, FOH_Y - 9.0, FOH_Y + 9.0)
add_barrier_line_y( 15.2, FOH_Y - 9.0, FOH_Y + 9.0)
barriers.finish(c06)

foh_deck = Builder('调音台控制平台', M['dark'])
foh_steel = Builder('FOH棚柱与桁架', M['steel'])
foh_roof = Builder('FOH棚顶', M['black'])
foh_trim = Builder('FOH平台警示边条', M['导向标识白漆'])
foh_screens = Builder('FOH控台屏幕_冷光', M['phone'])
foh_meters = Builder('FOH控台推子_暖光', M['warm'])

# Lower main deck (z = 0..0.65) and upper director riser (z = 0.65..1.15)
foh_deck.box((0.0, FOH_Y, 0.325), (27.0, 15.0, 0.65))
foh_deck.box((0.0, FOH_Y - 3.5, 0.90), (23.0, 7.2, 0.50))
# Access steps on left & right of FOH deck
for side in (-1, 1):
    foh_deck.box((side * 14.1, FOH_Y, 0.16), (1.2, 3.2, 0.32))
    foh_deck.box((side * 13.7, FOH_Y, 0.32), (0.6, 3.2, 0.64))

# White safety edge strips on FOH platforms
foh_trim.box((0.0, FOH_Y + 7.5, 0.655), (27.0, 0.14, 0.02))
foh_trim.box((0.0, FOH_Y - 7.5, 0.655), (27.0, 0.14, 0.02))
foh_trim.box((-13.5, FOH_Y, 0.655), (0.14, 15.0, 0.02))
foh_trim.box(( 13.5, FOH_Y, 0.655), (0.14, 15.0, 0.02))
foh_trim.box((0.0, FOH_Y + 0.1, 1.155), (23.0, 0.14, 0.02))

# 6 Truss columns + upper truss frame + sloped black weather canopy roof
for px in (-12.8, 0.0, 12.8):
    for py in (FOH_Y - 6.8, FOH_Y + 6.8):
        foh_steel.box((px, py, 2.55), (0.38, 0.38, 3.80))
# Roof perimeter truss beams
foh_steel.box((0.0, FOH_Y + 6.8, 4.35), (26.2, 0.36, 0.36))
foh_steel.box((0.0, FOH_Y - 6.8, 4.15), (26.2, 0.36, 0.36))
for px in (-12.8, -6.4, 0.0, 6.4, 12.8):
    foh_steel.box((px, FOH_Y, 4.25), (0.30, 14.0, 0.30), rx=-0.015)

# Canopy roof
foh_roof.box((0.0, FOH_Y, 4.55), (28.0, 15.6, 0.24), rx=-0.015)
foh_trim.box((0.0, FOH_Y + 7.8, 4.68), (28.0, 0.16, 0.04))
foh_trim.box((0.0, FOH_Y - 7.8, 4.45), (28.0, 0.16, 0.04))

# Front Row Audio Mixing Consoles (PA FOH - 3 large consoles at FOH_Y + 5.0 on lower deck z=0.65)
for cx in (-7.2, 0.0, 7.2):
    foh_roof.box((cx, FOH_Y + 5.0, 1.05), (4.2, 1.35, 0.80))
    foh_steel.box((cx, FOH_Y + 5.0, 1.50), (4.0, 1.20, 0.14), rx=0.18)
    foh_screens.box((cx - 1.0, FOH_Y + 5.45, 1.72), (1.1, 0.08, 0.42), rx=-0.15)
    foh_screens.box((cx + 1.0, FOH_Y + 5.45, 1.72), (1.1, 0.08, 0.42), rx=-0.15)
    foh_meters.box((cx, FOH_Y + 4.75, 1.58), (3.4, 0.45, 0.03), rx=0.18)

# Rear Row Lighting / Laser / Disguise Visual Consoles (4 consoles at FOH_Y - 2.5 on upper riser z=1.15)
for cx in (-8.1, -2.7, 2.7, 8.1):
    foh_roof.box((cx, FOH_Y - 2.5, 1.55), (3.6, 1.25, 0.80))
    foh_steel.box((cx, FOH_Y - 2.5, 1.98), (3.4, 1.10, 0.12), rx=0.16)
    foh_screens.box((cx - 0.75, FOH_Y - 2.05, 2.22), (0.95, 0.08, 0.40), rx=-0.12)
    foh_screens.box((cx + 0.75, FOH_Y - 2.05, 2.22), (0.95, 0.08, 0.40), rx=-0.12)
    foh_meters.box((cx, FOH_Y - 2.72, 2.05), (2.8, 0.40, 0.03), rx=0.16)

# Outboard DSP / Amp Racks at rear corners of FOH
for side in (-1, 1):
    foh_roof.box((side * 11.2, FOH_Y - 5.6, 1.85), (1.8, 1.4, 1.40))
    foh_meters.box((side * 11.2, FOH_Y - 4.89, 2.15), (1.4, 0.04, 0.12))
    foh_screens.box((side * 11.2, FOH_Y - 4.89, 1.85), (1.4, 0.04, 0.12))

# Central cable ramp (过线槽) running along x = 0 down the central aisle from FOH to stage
foh_roof.box((0.0, 17.2, 0.035), (0.75, 61.4, 0.07))
foh_trim.box((-0.28, 17.2, 0.072), (0.08, 61.4, 0.01))
foh_trim.box(( 0.28, 17.2, 0.072), (0.08, 61.4, 0.01))

foh_deck.finish(c06)
foh_steel.finish(c06)
foh_roof.finish(c06)
foh_trim.finish(c06)
foh_screens.finish(c06)
foh_meters.finish(c06)

# 5. Materialize new inner-field chunks in D (UNITY_ENHANCED_V3) with L0/L1 LODs
bpy.context.window.scene = D
dg_d = bpy.context.evaluated_depsgraph_get()
field_reports = []

for (cat, reg, mat_name), b in d_buckets.items():
    name = f'Chunk_{cat}_{reg}_{mat_name}'
    me = bpy.data.meshes.new(name + '_v22')
    me.from_pydata(b['v'], [], b['f'])
    me.materials.append(b['mat'])
    for poly, sm in zip(me.polygons, b['smooth']):
        poly.use_smooth = sm
    me.update()
    me.uv_layers.new(name='UVMap')
    if b['color'] is not None:
        vc = me.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
        for v_attr, col_val in zip(vc.data, b['color']):
            v_attr.color = col_val

    o = bpy.data.objects.new(name + '_L0', me)
    D.collection.objects.link(o)
    o.parent = root
    hi = sum(len(p.vertices) - 2 for p in me.polygons)
    lo = hi

    if cat in ('CROWD', 'CHAIRS') and hi > 300:
        group = bpy.data.objects.new('LOD_' + name, None)
        D.collection.objects.link(group)
        group.parent = root
        o.parent = group
        low = o.copy()
        low.data = me.copy()
        low.name = name + '_L1'
        D.collection.objects.link(low)
        low.parent = group
        mod = low.modifiers.new('Far mesh simplification', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = 0.26
        mod.use_collapse_triangulate = True
        dg_d = bpy.context.evaluated_depsgraph_get()
        lowdata = bpy.data.meshes.new_from_object(low.evaluated_get(dg_d), preserve_all_data_layers=True, depsgraph=dg_d)
        low.modifiers.clear()
        old_me = low.data
        low.data = lowdata
        bpy.data.meshes.remove(old_me)
        lo = sum(len(p.vertices) - 2 for p in lowdata.polygons)

    field_reports.append({'chunk': name, 'category': cat, 'near_triangles': hi, 'far_triangles': lo})
    b.clear()

bpy.context.window.scene = S
S['inner_field_v22'] = True

# 6. Update optimization_geometry.json for non-ARCH field chunks, then run export_repaired_architecture_v6.py
opt_path = OUT / 'optimization_geometry.json'
report_data = json.loads(opt_path.read_text(encoding='utf-8'))
report_data['details'] = [
    r for r in report_data['details']
    if not any(r['chunk'].startswith(prefix) for prefix in ('Chunk_CHAIRS_F_', 'Chunk_CROWD_F_', 'Chunk_PHONES_F_'))
] + field_reports
opt_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding='utf-8')

print(json.dumps({
    'status': 'INNER_FIELD_V22_BUILT',
    'blocks': len(BLOCKS),
    'total_chairs': total_chairs,
    'total_spectators': total_spectators,
    'total_phones': total_phones,
    'near_heads': near_head_count,
    'field_chunks': len(field_reports),
}, ensure_ascii=False))

# Execute architecture chunk rebuild + FBX export + blend save
exec((ROOT / 'export_repaired_architecture_v6.py').read_text(encoding='utf-8'))
