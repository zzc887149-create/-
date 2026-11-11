from pathlib import Path
import urllib.request, zipfile, json
R=Path(__file__).resolve().parent
out=R/'textures'/'Concrete034';out.mkdir(parents=True,exist_ok=True)
url='https://ambientcg.com/get?file=Concrete034_1K-JPG.zip'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
archive=out/'Concrete034_1K-JPG.zip'
if not archive.exists(): archive.write_bytes(urllib.request.urlopen(req,timeout=45).read())
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        if Path(name).suffix.lower() in ['.jpg','.png']:
            (out/Path(name).name).write_bytes(z.read(name))
ref=R/'references'/'exterior_closeup_tom_nguyen.jpg'
if not ref.exists():
    req=urllib.request.Request('https://upload.wikimedia.org/wikipedia/commons/2/28/Beijing_Birds_Nest_Closeup.jpg',headers={'User-Agent':'BirdsNestReference/1.0'})
    try:ref.write_bytes(urllib.request.urlopen(req,timeout=30).read())
    except Exception as e:print('Additional closeup unavailable:',e)
(out/'source.json').write_text(json.dumps({'asset':'Concrete034','source':'https://ambientcg.com/a/Concrete034','download':url,'license':'CC0 1.0','use':'generic concrete surface detail, not a scan of the stadium'},indent=2),encoding='utf-8')
print([p.name for p in out.iterdir()])
