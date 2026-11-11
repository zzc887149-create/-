from pathlib import Path
root=Path(__file__).resolve().parent
summary='最新更新（v19 提词器环境融合）：移除大屏下方重复的假看台、发光窗片及悬空装饰，恢复现有阶梯座席与入口的完整视线；保留后方大屏及原有字幕，补充背面钢框和四处与现有屋架相接的连接件，降低夜间字幕亮度。连接件根据现有模型设计，现场照片未提供可测量的安装节点。'
p=root/'精修版入口.md';s=p.read_text(encoding='utf-8');end=s.index('保留 v15 更新')
s='# 赵雷鸟巢 · 全场精修版\n\n'+summary+'\n\n保留 v18 三层入口环向重排：三层各 28 个位置（复原估计值，共 84 处），下、中层各只有一排入口。\n\n'+s[end:]
s=s.replace('WindowsPreview_v18','WindowsPreview_v19').replace('赵雷2026_鸟巢_入口环向重排版.blend','赵雷2026_鸟巢_提词器环境融合版.blend');p.write_text(s,encoding='utf-8')
p=root/'unity_enhanced/使用说明.md';s=p.read_text(encoding='utf-8');end=s.index('## 最快查看')
s='# 鸟巢全场 · v19 提词器环境融合\n\n'+summary+'\n\n保持自由飞行相机。\n\n'+s[end:]
s=s.replace('WindowsPreview_v18','WindowsPreview_v19').replace('赵雷2026_鸟巢_入口环向重排版.blend','赵雷2026_鸟巢_提词器环境融合版.blend')
s=s.replace('**“舞台提词器 · 少年锦时歌词”** 可直接从主唱视角查看提词器屏幕上的歌词与舞台前缘细节','**“后方大屏 · 背影歌词提词器”** 可直接查看大屏与周围看台')
p.write_text(s,encoding='utf-8')
(root/'references/v19_提词器融合依据.md').write_text('''# v19 提词器环境融合依据

- 演出照片来源：https://www.acmelighting.com/Info/detail/cat_id/29/id/11825 。本地 contact_sheet.jpg、acme_00.jpg、acme_17.jpg 展示场馆内连续的看台和局部夜景照明，不能据此将暗部建成独立黑色假看台。
- 场馆内部空间参照：https://stadiumdb.com/pictures/stadiums/chn/beijing_national_stadium/beijing_national_stadium09.jpg 。这是通用鸟巢照片，并非本次演出现场。
- 现有大屏位置、比例和字幕沿用前版。去掉其下方摄影式布景（假窗、假入口、整片星海坡面），露出原有真实三维座席、阶梯及通道。
- 背面钢框与四处屋架连接是模型空间下的合理重建，不能作为现场实测安装结构。连接端点通过现有屋面钢带网格最近点确定，不连接到膜面；未在看台步行通道设置新柱脚。
''',encoding='utf-8')
