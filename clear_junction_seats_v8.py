from pathlib import Path
ROOT=Path(r'C:\Users\Lenovo\Desktop\赵雷鸟巢')
src=(ROOT/'finish_seating_entries_v7.py').read_text(encoding='utf-8')
exec(src[:src.index('def overlaps(')])
def overlaps(q):
 for p in ports:
  if p['row']!=0:continue
  z=p['height'];n=23 if p['tier']==1 else 16;step=p['row_step'];rise=p['row_rise']
  if not z-.4<q.z<z+(n-1)*rise+2.5:continue
  d=q-p['entry'];t=d.dot(p['rad']);w=d.dot(p['tan'])
  if not -.9<t<(n-.3)*step:continue
  if 1.05<abs(w)<4.15:return True
  mid=12 if p['tier']==1 else 9
  if (abs(t)<1 or abs(t-mid*step)<1) and abs(w)<4.15:return True
 return False
exec(src[src.index('report=[]'):].replace('seating_clearance_cleanup.json','junction_seat_cleanup.json'))
