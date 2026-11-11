"""Acceptance checks specific to the approved one-floor/one-flat-passage relationship."""
import json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent;C=ROOT/'unity_enhanced/checks'
layout=json.loads((C/'v21_layout.json').read_text(encoding='utf-8'))
meta=json.loads((C/'v21_level_routes.json').read_text(encoding='utf-8'))
groups=collections.defaultdict(list)
for sample in layout['samples']:
    if sample['kind'].startswith(('L1_','L2_','L3_')):groups[sample['kind']].append(sample['point'][2])
errors=[]
if len(groups)!=120:errors.append('Expected 120 independently sampled passages')
for r in meta['routes']:
    zs=groups[r['kind']]
    if not zs or max(abs(z-r['floor']) for z in zs)>.001:errors.append('Non-level passage '+r['kind'])
    if r['steps_in_passage']!=0:errors.append('Stairs inside passage '+r['kind'])
for s in layout['segments']:
    if s['kind'].startswith(('L1_','L2_','L3_')) and abs(s['a'][2]-s['b'][2])>.001:errors.append('Vertical transition '+s['kind'])
for s in meta['stairs']:
    if s['riser']>.18001 or s['going']<.28:errors.append('Bad public stair proportions '+str(s))
out={'passages':len(groups),'floor_levels':meta['floors'],'public_stair_flights':len(meta['stairs']),'max_passage_elevation_difference':max(max(z)-min(z) for z in groups.values()),'failures':errors}
(C/'v21_flat_access_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
assert not errors
