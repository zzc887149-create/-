"""Close the missing lower-bowl rear deck between seating and red bowl shell."""
import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');s=bpy.context.scene
assert s.get('upper_tier_v10') and not s.get('rear_deck_v12')
c=bpy.data.collections.new('25_看台后缘空隙封接');s.collection.children.link(c)
vs=[];fs=[];n=1440;z=1.2+22*.54
# Seat tier ends at radii 96.7 / 126.7; shell at this height is 101.485 / 130.983.
# Small overlaps seal both boundaries without reaching the last seat footprint.
for h in [z-.32,z+.006]:
 for rx,ry in [(96.65,126.65),(101.68,131.18)]:
  for i in range(n):
   a=i*math.tau/n;vs.append((rx*math.cos(a),ry*math.sin(a),h))
for i in range(n):
 j=(i+1)%n
 fs.extend([(2*n+i,3*n+i,3*n+j,2*n+j),(i,j,n+j,n+i),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
me=bpy.data.meshes.new('V12_后排连接平台');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['concrete']);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
uv=me.uv_layers.new(name='MetreUV')
for f in me.polygons:
 axes=[0,1] if abs(f.normal.z)>.5 else [0,2] if abs(f.normal.y)>.5 else [1,2]
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
ob=bpy.data.objects.new('V12_下层看台后缘连续连接平台',me);c.objects.link(ob)
tree=BVHTree.FromPolygons([v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);fail=[];count=0
for i in range(720):
 a=(i+.5)*math.tau/720
 for t in [.015,.25,.5,.75,.985]:
  x=(96.7+(101.48-96.7)*t)*math.cos(a);y=(126.7+(130.98-126.7)*t)*math.sin(a)
  hit,_,_,_=tree.ray_cast(Vector((x,y,z+1)),Vector((0,0,-1)),2);count+=1
  if hit is None or abs(hit.z-(z+.006))>.02:fail.append([i,t])
assert not fail,fail[:10]
report={'samples':count,'failures':len(fail),'deck_top':z+.006,'thickness':.326,'inner_radii':[96.65,126.65],'outer_radii':[101.68,131.18],'note':'Model-derived closure, not surveyed stadium dimensions.'}
(ROOT/'unity_enhanced/checks/rear_gap_v12.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for prefix,position in [('VIEW_',(-99.2,0,z+1.7)),('LOOK_',(-95.5,25,z+1.1))]:
 name=prefix+'17_RearDeck';obj=bpy.data.objects.new(name,None);s.collection.children.get('19_全场观察机位',c).objects.link(obj);obj.location=position
 d=bpy.data.scenes['UNITY_ENHANCED_V3'];copy=obj.copy();d.collection.objects.link(copy);copy.parent=d.objects['BirdsNest_Enhanced_360']
s['rear_deck_v12']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'赵雷2026_鸟巢_看台后缘补齐版.blend'))
print(json.dumps(report))
