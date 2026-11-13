from pathlib import Path
import zipfile,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'unity_enhanced'
subprocess.run(['powershell.exe','-NoProfile','-File',str(ROOT/'sync_preview_entry.ps1')],check=True)
latest=ROOT/'最新_赵雷鸟巢.unitypackage'
shutil.copy2(OUT/'BirdsNest_Enhanced.unitypackage',latest)
assert hashlib.sha256(latest.read_bytes()).digest()==hashlib.sha256((OUT/'BirdsNest_Enhanced.unitypackage').read_bytes()).digest(), 'Root package hash mismatch'
source_assets=OUT/'UnityProject/Assets/ZhaoLeiBirdsNestEnhanced'
legacy_assets=ROOT/'unity_delivery/Assets/ZhaoLeiBirdsNestEnhanced'
shutil.copytree(source_assets,legacy_assets,dirs_exist_ok=True)
copied=[]
for p in sorted(source_assets.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(source_assets);q=legacy_assets/rel
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert q.is_file() and hashlib.sha256(q.read_bytes()).hexdigest()==digest, str(rel)
    copied.append({'file':str(rel),'sha256':digest})
(OUT/'checks/legacy_assets_sync.json').write_text(json.dumps({'verified_files':len(copied),'files':copied},ensure_ascii=False,indent=2),encoding='utf-8')
print('Legacy Unity assets verified:',len(copied),'files')
def archive(source,name,parts=None):
    with zipfile.ZipFile(OUT/name,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(source.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(source)
            if parts and rel.parts[0] not in parts:continue
            z.write(p,str(Path(source.name)/rel))
        z.write(OUT/'使用说明.md','使用说明.md')
    print(name,round((OUT/name).stat().st_size/1048576,1),'MB')
archive(OUT/'UnityProject','BirdsNest_Unity6_Enhanced_Project.zip',{'Assets','Packages','ProjectSettings'})
archive(OUT/'WindowsPreview_v27','BirdsNest_WindowsPreview.zip')
files=[latest,OUT/'BirdsNest_Unity6_Enhanced_Project.zip',OUT/'BirdsNest_WindowsPreview.zip',OUT/'BirdsNest_Enhanced.unitypackage',ROOT/'赵雷2026_鸟巢_座位图内场版.blend']
(OUT/'delivery_manifest.json').write_text(json.dumps([{'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],indent=2,ensure_ascii=False),encoding='utf-8')
