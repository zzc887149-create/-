"""Clear seats/crowd at row turns in the actual elliptical aisle coordinates."""
from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'finish_seating_entries_v7.py').read_text(encoding='utf-8')
exec(src[:src.index('def overlaps(')])
tiers=[(76,106,1.2,23,.9,.54),(99,128,17,16,1.02,.65)]
def overlaps(q):
 for tier,(rx,ry,z,n,step,rise) in enumerate(tiers,1):
  if not z-.4<q.z<z+(n-1)*rise+2.5:continue
  low=-.8;high=(n-.2)*step
  def inside(r):return (q.x/(rx+step*.5+r))**2+(q.y/(ry+step*.5+r))**2<1
  if inside(low) or not inside(high):continue
  for _ in range(14):
   r=(low+high)*.5
   if inside(r):high=r
   else:low=r
  r=(low+high)*.5
  if not -.8<r<(n-.2)*step:continue
  angle=math.atan2(q.y/(ry+step*.5+r),q.x/(rx+step*.5+r))
  for p in ports:
   if p['tier']!=tier or p['row']!=0:continue
   delta=(angle-p['angle']+math.pi)%math.tau-math.pi
   w=delta*math.hypot(rx*math.sin(p['angle']),ry*math.cos(p['angle']))
   if 1.0<abs(w)<4.4:return True
 return False
exec(src[src.index('report=[]'):].replace('seating_clearance_cleanup.json','row_turn_cleanup_v9.json'))
