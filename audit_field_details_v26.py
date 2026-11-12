"""Check stair shoulder clearance and the internal riser in the actual mesh."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
exec(compile((ROOT/'audit_inner_field_v25.py').read_text(encoding='utf8'), 'base_field_audit', 'exec'))
detail_tests = []
for side in [-1,1]:
    for offset in [-1.2,0,1.2]:
        path = [(side*15.5,-22.5+offset,0)] + [
            (side*(14.625-k*.35),-22.5+offset,(k+1)*.1625) for k in range(4)
        ] + [(side*13.1,-22.5+offset,.65)]
        for a,b in zip(path,path[1:]):
            for h in [.5,.95,1.75]:
                detail_tests.append((Vector(a)+Vector((0,0,h)),Vector(b)+Vector((0,0,h))))
for x in [-.9,0,.9]:
    path=[(x,-21,.65)]+[(x,-22.4+(2.5-k)*.34,.65+(k+1)/6) for k in range(3)]+[(x,-22.7,1.15)]
    for a,b in zip(path,path[1:]):
        for h in [.5,.95,1.75]:
            detail_tests.append((Vector(a)+Vector((0,0,h)),Vector(b)+Vector((0,0,h))))
failures=[]
for a,b in detail_tests:
    delta=b-a
    hit=tree.ray_cast(a,delta.normalized(),delta.length)
    if hit[0] is not None:
        failures.append({'start':list(a),'end':list(b),'hit':list(hit[0])})
report_path=ROOT/'unity_enhanced/checks/v26_detail_audit.json'
report=json.loads(report_path.read_text(encoding='utf8'))
report.update(base_route_segments=len(tests),stair_clearance_segments=len(detail_tests),failures=failures)
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V26_DETAIL_CLEARANCE',len(detail_tests),'failures',len(failures))
assert not failures, failures
