"""Report the actual exported scene, independently of older version report files."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢');OUT=ROOT/'unity_enhanced';D=bpy.data.scenes['UNITY_ENHANCED_V3']
rows=[]
for ob in D.objects:
    if ob.type!='MESH' or not ob.name.startswith('Chunk_') or not ob.name.endswith('_L0'):continue
    lo=D.objects.get(ob.name[:-3]+'_L1');n=sum(len(p.vertices)-2 for p in ob.data.polygons)
    rows.append({'chunk':ob.name[:-3],'category':ob.name.split('_')[1],'near_triangles':n,'far_triangles':sum(len(p.vertices)-2 for p in lo.data.polygons) if lo else n})
f=OUT/'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Models/BirdsNest_Enhanced.fbx'
report={'version':'v25','chunks':len(rows),'LOD_groups':sum(o.name.startswith('LOD_') for o in D.objects),'near_triangles':sum(r['near_triangles'] for r in rows),'far_triangles':sum(r['far_triangles'] for r in rows),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'details':rows}
(OUT/'optimization_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:v for k,v in report.items() if k!='details'})
