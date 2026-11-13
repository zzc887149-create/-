"""Separate FOH displays from phone lights; model readable generic controls.

These are visual details, not a reconstruction of a particular console brand.
"""
import ast,json,math
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
S=bpy.context.scene
assert S.get('field_detail_v26')
tree=ast.parse((ROOT/'rebuild_inner_field_v25.py').read_text(encoding='utf8'))
defs=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Builder'
      or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['CF','CV','OF'] for t in n.targets)]
exec(compile(ast.Module(body=defs,type_ignores=[]),'field_helpers','exec'))
col=bpy.data.collections['06_内场折叠椅']
mp=ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/materials.json'
records=json.loads(mp.read_text(encoding='utf8'))

def material(label,name,base,emission,strength):
    mat=bpy.data.materials.get(label)
    if mat is None:mat=bpy.data.materials['phone'].copy();mat.name=label
    p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*base,1)
    p.inputs['Emission Color'].default_value=(*emission,1)
    p.inputs['Emission Strength'].default_value=strength
    p.inputs['Roughness'].default_value=.6
    p.inputs['Metallic'].default_value=0
    mat.diffuse_color=(*base,1)
    export=bpy.data.materials.get(name)
    if export is None:export=mat.copy();export.name=name
    export.diffuse_color=mat.diffuse_color
    record=dict(name=name,label=label,baseColor=[*base,1],emission=[*emission,1],
                strength=strength,roughness=.6,metallic=0,texture='',normal='',vertexColor=False)
    records['materials']=[r for r in records['materials'] if r['name']!=name]+[record]
    return mat

display=material('FOH显示面板低亮','BNE_FOH_DISPLAY',(.015,.035,.05),(.08,.19,.28),.55)
meter=material('FOH仪表柔光','BNE_FOH_METER',(.04,.2,.12),(.14,.55,.33),.65)
edge=material('FOH踏步柔光','BNE_FOH_EDGE',(.62,.66,.52),(.36,.42,.26),.35)
mp.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')

names=['FOH控台屏幕_冷光','FOH控台推子_暖光','FOH屏幕外框_V27','FOH控制件_V27','FOH仪表指示_V27']
for name in names:
    if S.objects.get(name):bpy.data.objects.remove(S.objects[name],do_unlink=True)
frames=Builder('FOH屏幕外框_V27',bpy.data.materials['black'])
screens=Builder('FOH控台屏幕_冷光',display)
details=Builder('FOH控制件_V27',bpy.data.materials['steel'])
indicators=Builder('FOH仪表指示_V27',meter)

def local_box(builder,center,offset,size,rx):
    p=Vector(center)+Matrix.Rotation(rx,3,'X')@Vector(offset)
    builder.box(tuple(p),size,rx=rx)

def monitor(x,y,z,width,height,rx,board_y,board_z,board_rx,board_half):
    center=(x,y,z)
    frames.box(center,(width,.08,height),rx=rx)
    board_top=board_z+(y-board_y)*math.tan(board_rx)+board_half/math.cos(board_rx)
    bottom=z-height*.5*math.cos(rx)-.04*abs(math.sin(rx))
    assert bottom>board_top
    details.box((x,y,(board_top+bottom)/2),(.09,.07,bottom-board_top+.015))
    local_box(details,(x,y,board_top),(0,0,.008),(.28,.20,.016),board_rx)
    # Operator-facing side is -Y; dark backing and bezel stay opaque.
    local_box(screens,center,(0,-.044,0),(width-.07,.012,height-.065),rx)
    for i in range(10):
        h=(height-.14)*(.35+.6*((i*7)%11)/10)
        local_box(indicators,center,(-width*.4+i*width*.08,-.053,-height*.32+h/2),
                  (width*.028,.006,h),rx)
    local_box(indicators,center,(0,-.053,height*.34),(width*.78,.006,.012),rx)

def faders(cx,cy,z,width,rx,board_half,offset_y):
    # Small individual controls replace the solid warm luminous rectangle.
    center=Vector((cx,cy,z))+Matrix.Rotation(rx,3,'X')@Vector((0,offset_y,board_half+.0175))
    frames.box(center,(width,.45,.035),rx=rx)
    for i in range(16):
        x=-width*.45+i*width*.9/15
        local_box(details,center,(x,0,.025),(.012,.34,.012),rx)
        local_box(details,center,(x,-.10+(i%5)*.045,.04),(.065,.055,.025),rx)
        local_box(indicators,center,(x,.18,.029),(.035,.025,.012),rx)

fy=-22.5
for cx in [-7.2,0,7.2]:
    for dx in [-1,1]:monitor(cx+dx,fy+5.45,1.95,1.1,.42,-.15,fy+5,1.5,.18,.07)
    faders(cx,fy+5,1.5,3.4,.18,.07,-.25)
for cx in [-8.1,-2.7,2.7,8.1]:
    for dx in [-.75,.75]:monitor(cx+dx,fy-2.05,2.44,.95,.40,-.12,fy-2.5,1.98,.16,.06)
    faders(cx,fy-2.5,1.98,2.8,.16,.06,-.22)
for side in [-1,1]:
    # Rack displays face +Y, unlike the console monitors.
    screens.box((side*11.2,fy-4.89,1.85),(1.4,.04,.12))
    for i in range(8):
        indicators.box((side*11.2-.56+i*.16,fy-4.86,2.15),(.04,.02,.04))
for b in [frames,screens,details,indicators]:b.finish(col)
ob=S.objects['FOH踏步防滑边条_V26'];ob.data.materials.clear();ob.data.materials.append(edge)
S['foh_controls_v27']=True
assert all(m.name!='phone' for o in [screens,indicators] for m in S.objects[o.name].data.materials)
report={'version':'v27','monitors':14,'monitor_stands':14,'rack_displays':2,'fader_banks':7,'faders':112,
        'phone_material_unchanged':True,'new_materials':3,'marked_treads':11,
        'display_night_emission':[.08*.55,.19*.55,.28*.55],
        'meter_night_emission':[.14*.65,.55*.65,.33*.65]}
(ROOT/'unity_enhanced/checks/v27_controls.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(report)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
