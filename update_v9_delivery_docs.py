from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
p=ROOT/'unity_enhanced/使用说明.md';s=p.read_text(encoding='utf-8')
s=s.replace('看台衔接精修版 · v8 · 2026-10-27','逐排衔接修复版 · v9 · 2026-10-28').replace('WindowsPreview_v8','WindowsPreview_v9').replace('赵雷2026_鸟巢_看台衔接精修版.blend','赵雷2026_鸟巢_逐排衔接修复版.blend')
s=s.replace('## 本轮具体改动\n','''## 本轮具体改动

- v9 将下层、中层 48 条侧向梯道按每排座席标高重新对齐，936 个逐排连接不再使用旧版最高约 5.9 厘米的错位踏面；48 个出口平台两翼同步收口。
- 扩大中层梯道及转弯区域与 F4 楼板、径向梁的避让开口；清理椭圆看台边缘伸入通路的座椅和观众，并同步远景模型。
- Blender 的 32,112 个地面/净空点与 7,152 段路线通过；同一批点另行检查座椅、观众占用也通过。Unity 导入后的复查包含建筑、座椅与观众，结果见 checks/junction_unity_validation.txt。
- 仍为自由飞行浏览，没有添加第一人称；第三层看台通路待后续完善。参考与精度说明见 ../references/v9_逐排衔接修复依据.md。
- 本机独立工程 Library 缓存通过目录连接放在 D:/赵雷鸟巢_Unity缓存/Library；打包工程不含此缓存，其他电脑打开会正常重新生成。

保留的 v8 修复：
''')
p.write_text(s,encoding='utf-8')
p=ROOT/'精修版入口.md';s=p.read_text(encoding='utf-8');start=s.index('最新修正');end=s.index('\n\n',start)
s=s[:start]+'最新修正（v9）：重新对齐 48 条侧向梯道与 936 个座席排连接，调整 48 个出口平台两翼，修复 F4 楼板与径向梁对转弯通路的遮挡，并清理伸入通路的座椅与观众。点击“看台内侧 · 出口与梯道衔接”查看，按 N 切换白天。'+s[end:]
s=s.replace('赵雷2026_鸟巢_看台衔接精修版.blend','赵雷2026_鸟巢_逐排衔接修复版.blend');p.write_text(s,encoding='utf-8')
p=ROOT/'unity_enhanced/optimization_geometry.json';d=json.loads(p.read_text(encoding='utf-8'));d['sha256']=hashlib.sha256((ROOT/'unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Models/BirdsNest_Enhanced.fbx').read_bytes()).hexdigest();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
