from pathlib import Path
import re,json,concurrent.futures,urllib.request
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).parent
html=(root/'acme_source.html').read_text(encoding='utf-8')
urls=list(dict.fromkeys(re.findall(r'<img class="raw-image" src="([^"]+)"',html)))
urls=[('https://www.acmelighting.com'+u if u.startswith('/') else u) for u in urls]
def fetch(pair):
    i,u=pair
    try:
        r=urllib.request.urlopen(u,timeout=25)
        p=root/f'acme_{i:02d}{".gif" if ".gif" in u else ".jpg"}'
        p.write_bytes(r.read())
        return {'id':i,'url':u,'path':p.name}
    except Exception as e:return {'id':i,'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: results=list(ex.map(fetch,enumerate(urls)))
(root/'sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1200,((len(results)+2)//3)*260),'#151820');d=ImageDraw.Draw(sheet)
for n,r in enumerate(results):
    if 'path' not in r:continue
    im=Image.open(root/r['path']).convert('RGB');im.thumbnail((392,230))
    x=(n%3)*400;y=(n//3)*260;sheet.paste(im,(x,y+25));d.text((x+5,y+5),r['path'],fill='white')
sheet.save(root/'contact_sheet.jpg')
print(json.dumps(results,ensure_ascii=False))
