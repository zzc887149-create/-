"""Use the existing actual-mesh report, marking this detail revision."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
exec(compile((ROOT/'report_export_geometry_v25.py').read_text(encoding='utf8'), 'geometry_report', 'exec'))
p = ROOT/'unity_enhanced/optimization_geometry.json'
report = json.loads(p.read_text(encoding='utf8'))
report['version'] = 'v26'
p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
