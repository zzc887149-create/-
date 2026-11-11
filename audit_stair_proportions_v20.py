"""Check actual consecutive stair samples, independently of collision tests."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'unity_enhanced/checks/v20_layout.json').read_text(encoding='utf-8'))
bad=[];runs=[]
for s in data['segments']:
    if s['kind']!='upper_core_steps':continue
    a,b=s['a'],s['b'];rise=abs(b[2]-a[2]);going=math.hypot(b[0]-a[0],b[1]-a[1])
    if rise<.001:continue
    runs.append(going)
    if going<.25 or rise>.19:bad.append({'a':a,'b':b,'rise':rise,'going':going})
out={'checked':len(runs),'minimum_going':min(runs),'failed_segments':len(bad),'failures':bad}
(ROOT/'unity_enhanced/checks/v20_stair_proportions.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
print({k:v for k,v in out.items() if k!='failures'})
