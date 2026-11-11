"""Build the giant South Stand rear teleprompter LED screen opposite the stage, matching the user's reference photo."""
import bpy, bmesh, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
PKG = ROOT / 'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'


def generate_screen_texture():
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        if (ROOT / 'textures/teleprompter_screen.png').is_file() and (PKG / 'Textures/BN5_提词器屏幕_texture.png').is_file():
            return
        raise

    W, H = 2048, 920
    base = Image.new('RGBA', (W, H), (3, 3, 5, 255))
    glow_wide = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glow_tight = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    draw_wide = ImageDraw.Draw(glow_wide)
    draw_tight = ImageDraw.Draw(glow_tight)
    draw_fg = ImageDraw.Draw(fg)

    font_bold = r'C:\Windows\Fonts\msyhbd.ttc'
    f_lyric = ImageFont.truetype(font_bold, 118)

    lines = [
        '昨日是庆幸着',
        '为何今日要感伤',
        '让烦恼都随雨流进下水道',
    ]
    y_positions = [205, 385, 565]

    for text, y in zip(lines, y_positions):
        bbox = draw_fg.textbbox((0, 0), text, font=f_lyric)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw_wide.text((x, y), text, font=f_lyric, fill=(255, 190, 165, 150))
        draw_tight.text((x, y), text, font=f_lyric, fill=(255, 228, 212, 220))
        draw_fg.text((x, y), text, font=f_lyric, fill=(255, 250, 246, 255))

    # Tiny blue signal dot in upper-right quadrant (visible in user's reference photo)
    dot_x, dot_y = int(W * 0.775), int(H * 0.145)
    draw_wide.ellipse([dot_x - 10, dot_y - 10, dot_x + 10, dot_y + 10], fill=(70, 130, 255, 180))
    draw_fg.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=(135, 185, 255, 255))

    glow_wide = glow_wide.filter(ImageFilter.GaussianBlur(radius=18))
    glow_tight = glow_tight.filter(ImageFilter.GaussianBlur(radius=5))

    comp = Image.alpha_composite(base, glow_wide)
    comp = Image.alpha_composite(comp, glow_tight)
    comp = Image.alpha_composite(comp, fg).convert('RGB')

    out1 = ROOT / 'textures/teleprompter_screen.png'
    out2 = PKG / 'Textures/BN5_提词器屏幕_texture.png'
    comp.save(out1)
    comp.save(out2)


generate_screen_texture()

S = bpy.context.scene
C = next(c for c in S.collection.children if c.name.startswith('20_'))

# Clean up all previous small stage/FOH teleprompters, water bottles, and any prior rear teleprompter objects
for ob in list(C.objects):
    if ob.name.startswith(('舞台提词器_', '控台提词器_', '舞台水瓶_', '后方看台提词器_', 'VIEW_18_', 'LOOK_18_')):
        bpy.data.objects.remove(ob, do_unlink=True)


def ensure_mat(name, color, rough=0.5, metal=0.0, emit=0.0, tex_path=None):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = (*color, 1.0)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in bs.inputs:
        bs.inputs['Specular IOR Level'].default_value = 0.0 if rough >= 0.95 else 0.5
    bs.inputs['Emission Color'].default_value = (*(color if not tex_path else (1.0, 1.0, 1.0)), 1.0)
    bs.inputs['Emission Strength'].default_value = emit
    for link in list(m.node_tree.links):
        if link.to_node == bs and link.to_socket.name in ('Base Color', 'Emission Color'):
            m.node_tree.links.remove(link)
    if tex_path:
        tex_node = next((n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE'), None)
        if not tex_node:
            tex_node = m.node_tree.nodes.new('ShaderNodeTexImage')
        img = bpy.data.images.get(Path(tex_path).name)
        if img:
            bpy.data.images.remove(img)
        img = bpy.data.images.load(str(tex_path), check_existing=False)
        img.pack()
        tex_node.image = img
        m.node_tree.links.new(tex_node.outputs['Color'], bs.inputs['Base Color'])
        m.node_tree.links.new(tex_node.outputs['Color'], bs.inputs['Emission Color'])
    return m


black = bpy.data.materials['black']
steel = bpy.data.materials['steel']
screen_mat = ensure_mat(
    'BN5_提词器屏幕',
    (0.02, 0.02, 0.02),
    rough=1.0,
    metal=0.0,
    emit=1.55,
    tex_path=PKG / 'Textures/BN5_提词器屏幕_texture.png',
)
dark_surround_mat = ensure_mat('BN5_提词器背板', (0.012, 0.012, 0.016), rough=0.98, metal=0.05, emit=0.0)
warm_window_mat = ensure_mat('BN5_看台包厢暖光', (1.0, 0.80, 0.42), rough=0.25, metal=0.0, emit=1.65)
star_blue_mat = ensure_mat('BN5_看台荧光星海', (0.58, 0.86, 1.0), rough=0.15, metal=0.0, emit=2.4)


def add_mesh(name, verts, faces, mat, uvs=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if uvs:
        uv_layer = me.uv_layers.new(name='UVMap')
        for p, puv in zip(me.polygons, uvs):
            p.use_smooth = smooth
            for li, uv in zip(p.loop_indices, puv):
                uv_layer.data[li].uv = uv
    else:
        for p in me.polygons:
            p.use_smooth = smooth
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    C.objects.link(ob)
    return ob


def add_box_xform(name, center, size, mat, rot_x=0.0, rot_y=0.0, rot_z=0.0):
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    local_v = [
        Vector((-sx, -sy, -sz)), Vector((sx, -sy, -sz)), Vector((sx, sy, -sz)), Vector((-sx, sy, -sz)),
        Vector((-sx, -sy, sz)), Vector((sx, -sy, sz)), Vector((sx, sy, sz)), Vector((-sx, sy, sz)),
    ]
    rot = (
        Matrix.Rotation(rot_z, 4, 'Z')
        @ Matrix.Rotation(rot_y, 4, 'Y')
        @ Matrix.Rotation(rot_x, 4, 'X')
    )
    c = Vector(center)
    verts = [tuple(c + (rot @ v)) for v in local_v]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
    return add_mesh(name, verts, faces, mat)


# Clean up the 4 stray Z=30.4 seam-box vertices on 三层看台_层2 at X in [-2.1, -0.2], Y in [-144.3, -128.0]
tier2_ob = S.objects.get('三层看台_层2')
if tier2_ob and tier2_ob.type == 'MESH':
    for v in tier2_ob.data.vertices:
        co = tier2_ob.matrix_world @ v.co
        if -2.5 < co.x < 0.2 and -145.0 < co.y < -127.5 and co.z > 29.5:
            v.co.z = 16.4
    tier2_ob.data.update()

# 1. Giant South Stand Rear Teleprompter LED Screen (facing +Y toward the North Stage)
# Positioned at X in [-15.2, 15.2], Y = -126.8 (cleanly in front of Y=-128.0), Z in [22.2, 35.6]
W_SCR = 30.4
H_SCR = 13.4
Y_SCR = -126.8
Z_BOT = 22.2
Z_TOP = Z_BOT + H_SCR
hw = W_SCR / 2.0

# Matte-black cabinet behind the LED screen + horizontal VIP skybox concourse fascia below it
add_box_xform('后方看台提词器_主箱体', (0.0, Y_SCR - 0.32, (Z_BOT + Z_TOP) / 2.0), (W_SCR + 1.2, 0.52, H_SCR + 0.6), dark_surround_mat)
add_box_xform('后方看台提词器_暗场背幕', (0.0, Y_SCR - 0.45, 20.8), (62.0, 0.45, 3.6), dark_surround_mat)

# Double-sided UV-mapped LED screen quad facing +Y (when looking from +Y toward -Y, +X is screen-left, -X is screen-right)
scr_verts = [
    (hw, Y_SCR, Z_BOT),    # 0: bottom-left (in camera view looking South) -> u=0, v=0
    (-hw, Y_SCR, Z_BOT),   # 1: bottom-right -> u=1, v=0
    (-hw, Y_SCR, Z_TOP),   # 2: top-right -> u=1, v=1
    (hw, Y_SCR, Z_TOP),    # 3: top-left -> u=0, v=1
]
scr_faces = [(0, 1, 2, 3), (0, 3, 2, 1)]
scr_uvs = [
    [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
    [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)],
]
add_mesh('后方看台提词器_主液晶屏', scr_verts, scr_faces, screen_mat, uvs=scr_uvs)

# 2. Warm-lit VIP Skybox / Concourse vertical windows right below the giant screen (matching reference photo)
Z_WIN_MID = 20.45
win_positions = [16.5, 12.4, 10.1, 8.8, 4.2, -0.5, -5.2, -10.4, -15.8]
for idx, wx in enumerate(win_positions):
    w_width = 0.72 if idx not in (2, 3) else 0.52
    add_box_xform(f'后方看台提词器_包厢暖光窗_{idx}', (wx, Y_SCR - 0.15, Z_WIN_MID), (w_width, 0.22, 1.45), warm_window_mat)

# 3. Sloped dark night seating bank beneath the skybox windows + dense blue-white starry glowsticks
bank_verts = [
    (31.0, -118.2, 13.8), (-31.0, -118.2, 13.8),
    (-31.0, Y_SCR - 0.25, 19.3), (31.0, Y_SCR - 0.25, 19.3),
]
add_mesh('后方看台提词器_看台暗场坡面', bank_verts, [(0, 1, 2, 3), (0, 3, 2, 1)], dark_surround_mat)

rng = random.Random(202605)
star_verts = []
star_faces = []
for _ in range(1650):
    t = rng.random()
    sy = -118.3 - t * 8.1
    sz = 14.0 + t * 5.1 + rng.uniform(-0.14, 0.14)
    sx = rng.uniform(-29.0, 29.0)
    r = rng.uniform(0.048, 0.085)
    base_idx = len(star_verts)
    star_verts.extend([
        (sx - r, sy + 0.12, sz),
        (sx + r, sy + 0.12, sz),
        (sx, sy + 0.12, sz + r * 1.3),
        (sx, sy + 0.12, sz - r * 1.3),
    ])
    star_faces.extend([
        (base_idx, base_idx + 1, base_idx + 2),
        (base_idx, base_idx + 2, base_idx + 1),
        (base_idx, base_idx + 1, base_idx + 3),
        (base_idx, base_idx + 3, base_idx + 1),
    ])
add_mesh('后方看台提词器_星海荧光棒群', star_verts, star_faces, star_blue_mat)

# 4. Lower concourse overhang shadow band & warm vomitory exits at the bottom of the frame
add_box_xform('后方看台提词器_看台前檐暗带', (0.0, -118.0, 13.35), (62.0, 0.9, 0.95), dark_surround_mat)
add_box_xform('后方看台提词器_下层通道暗墙', (0.0, -118.6, 11.9), (62.0, 0.5, 2.2), dark_surround_mat)
for idx, (vx, vw) in enumerate([(-14.0, 1.6), (-7.2, 1.2), (-0.8, 2.2), (6.5, 1.4), (13.5, 1.5)]):
    add_box_xform(f'后方看台提词器_下层通道暖光_{idx}', (vx, -118.25, 12.05), (vw, 0.25, 1.35), warm_window_mat)
    for g in (-0.35, 0.0, 0.35):
        add_box_xform(f'后方看台提词器_通道格栅_{idx}_{g:+.2f}', (vx + g * vw, -118.08, 12.05), (0.08, 0.25, 1.40), dark_surround_mat)

# 5. Hanging Line-Array Speaker Cluster & Roof Cross-Cables above the screen (matching upper part of reference photo)
SPK_X, SPK_Y = -7.6, -113.5
add_box_xform('后方看台提词器_吊挂音箱横担', (SPK_X, SPK_Y, 34.45), (2.3, 0.45, 0.42), dark_surround_mat)
add_box_xform('后方看台提词器_吊挂音箱吊臂_L', (SPK_X - 0.58, SPK_Y, 34.95), (0.14, 0.14, 0.95), dark_surround_mat)
add_box_xform('后方看台提词器_吊挂音箱吊臂_R', (SPK_X + 0.58, SPK_Y, 34.95), (0.14, 0.14, 0.95), dark_surround_mat)
add_box_xform('后方看台提词器_吊挂线阵列音箱', (SPK_X, SPK_Y, 32.85), (0.82, 0.68, 2.65), dark_surround_mat)

cables = [
    (Vector((12.5, -106.5, 34.2)), Vector((-4.5, -125.8, 35.8))),
    (Vector((-2.0, -106.5, 34.2)), Vector((11.5, -125.8, 35.8))),
]
for idx, (p0, p1) in enumerate(cables):
    diff = p1 - p0
    mid = (p0 + p1) * 0.5
    yaw = math.atan2(diff.y, diff.x)
    pitch = -math.atan2(diff.z, math.hypot(diff.x, diff.y))
    add_box_xform(f'后方看台提词器_顶棚拉索_{idx}', mid, (diff.length, 0.07, 0.07), dark_surround_mat, rot_y=pitch, rot_z=yaw)

# 6. Dedicated Viewpoint 18 framing the South Stand Giant Teleprompter exactly like the user's photo
for prefix, loc in [('VIEW_18_Teleprompter', (0.0, -91.5, 18.8)), ('LOOK_18_Teleprompter', (0.0, -126.8, 25.8))]:
    existing = S.objects.get(prefix)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
    empty = bpy.data.objects.new(prefix, None)
    empty.location = loc
    C.objects.link(empty)

S['teleprompter_v17'] = True
S['teleprompter_lyric'] = '昨日是庆幸着 / 为何今日要感伤 / 让烦恼都随雨流进下水道'

# Re-run export_band_v5.py logic so BirdsNest_Band.fbx and band_materials.json include the rear teleprompter & viewpoint 18
exec((ROOT / 'export_band_v5.py').read_text(encoding='utf-8').replace(
    "str(ROOT/'赵雷2026_鸟巢_乐队细化版.blend')", "bpy.data.filepath"
))

# Update band_materials.json with texture & emission metadata
bm_path = PKG / 'band_materials.json'
bm_data = json.loads(bm_path.read_text(encoding='utf-8'))
emit_map = {
    'BN5_提词器屏幕': ('BN5_提词器屏幕_texture.png', 1.45),
    'BN5_看台包厢暖光': (None, 1.65),
    'BN5_看台荧光星海': (None, 2.20),
}
for m in bm_data['materials']:
    if m['name'] in emit_map:
        tex, em = emit_map[m['name']]
        if tex:
            m['texture'] = tex
        m['emission'] = em
bm_path.write_text(json.dumps(bm_data, ensure_ascii=False, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('South Stand Giant Teleprompter built and exported to BirdsNest_Band.fbx')
