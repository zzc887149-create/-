from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=ROOT/'unity_enhanced/使用说明.md';s=p.read_text(encoding='utf-8')
for a,b in [('看台接通版 · v7','看台衔接精修版 · v8'),('WindowsPreview_v7','WindowsPreview_v8'),('共 14 个直达视角','共 15 个直达视角'),('3,907,916','3,887,524'),('1,610,248','1,691,860'),('14 个观察点','15 个观察点'),('checks/v7_smoke/','checks/v8_smoke/'),('赵雷2026_鸟巢_看台接通版.blend','赵雷2026_鸟巢_看台衔接精修版.blend')]:s=s.replace(a,b)
s=s.replace('和“看台入口 · 环廊连接通道”','、“看台入口 · 环廊连接通道”和“看台内侧 · 出口与梯道衔接”')
s=s.replace('## 本轮具体改动\n','''## 本轮具体改动

- v8 在看台内侧新增 48 个出口分流平台与 48 条两侧细分梯道，补上前缘护栏、洞口阶梯栏板、踏边和实体底座，让通道出口接入看台梯道。
- 调整伸入分流平台的旧墙端与扶手，清理梯道内座椅、人物及其远景替代网格；修复切割影响到的相邻座席面。
- Blender 新平台/梯道 10,008 个地面和净空采样点、3,432 段路线检查通过；另有 1,872 个相邻座席平台位置检查通过。Unity 导入后执行独立复查，记录见 `checks/junction_unity_validation.txt`。
- 新增“看台内侧 · 出口与梯道衔接”机位。修复前后截图为 `checks/Mouth_before_F2.png` 和 `checks/Mouth_F2.png`。
- 仅覆盖现有下层、中层看台的这些出口，第三层看台及其他未覆盖过道仍待完善。新增构造是模型修复估算，并非现场施工图复刻，详见上一级 `references/v8_看台衔接精修依据.md`。

保留的 v7 通道修复：
''')
start=s.index('- 28 个日夜固定视角中，');end=s.index('\n',start)
s=s[:start]+'- v7 的入口夜景曾有轻微遮挡开关亮度差异。v8 的 30 个日夜固定视角重新检查结果见 `checks/runtime_validation.csv` 与 `checks/v8_检查说明.md`；桌面实际点击尚未完成。'+s[end:]
p.write_text(s,encoding='utf-8')
