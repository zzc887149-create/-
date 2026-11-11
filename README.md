# 赵雷「没有信号」鸟巢场景复原

Blender 源场景与 Unity 可编辑工程。当前版本 v25：鸟巢内外全场、舞台、三层看台和通道、提词器后方空座，以及依据座位图重排的 26 个内场分区和中控台。

![内场布局](unity_enhanced/checks/v25_field_plan.png)

## 获取工程

本仓库使用 Git LFS 保存模型、贴图和大型验证数据。克隆前安装 Git 与 Git LFS：

```shell
git lfs install
git clone https://github.com/zzc887149-create/-.git zhaolei-birds-nest
cd zhaolei-birds-nest
git lfs pull
```

在 Unity Hub 中添加 `unity_enhanced/UnityProject`，使用 **Unity 6000.3.16f1**。工程使用 Built-in 渲染管线；场景为 `Assets/ZhaoLeiBirdsNestEnhanced/Scenes/BirdsNest_Enhanced.unity`。Assets 的 `.meta` 文件均需保留。

Blender 源文件为根目录的 `赵雷2026_鸟巢_座位图内场版.blend`，保存版本为 Blender 5.2.2。请保留相邻的 `textures` 及 Unity 资源目录。

## 观看与构建

仓库主要保存可编辑源文件；Windows 程序、Unity 导入包和缓存不纳入 Git 历史。本机工作目录的 `双击观看_赵雷鸟巢（最新版）.lnk` 是生成的观看入口，不能作为跨电脑启动文件。

在 Unity 工程执行编辑器方法 `ZhaoLeiBirdsNestV3.BuildVenuePlayer.Build` 可构建 Windows 预览。生成目录为 `unity_enhanced/WindowsPreview_v25`；运行时需要将 `BirdsNest.exe`、`BirdsNest_Data`、`UnityPlayer.dll` 等依赖保留在同一目录。按 9 可查看内场分区与中控台。

根目录 Python 脚本保留了建模迭代过程，其中包含原工作机的绝对 `ROOT` 路径；换电脑运行脚本前需修改路径。部分历史脚本依赖没有提交的旧版场景，请优先编辑当前源文件。最新内场流程见 [v25 验证记录](unity_enhanced/checks/v25_交付验证.md)。

## 资料与精度

参考资料及来源说明保存在 `references` 和根目录 Markdown 文件中。内部尺寸、座位数量及舞台细节为照片和用户确认草图基础上的视觉复原，不是实测施工数据。引用图片及贴图的权利归其各自权利人，未额外授予第三方素材许可。

## 提交约定

- 提交 Assets、Packages、ProjectSettings、脚本及最新版 Blender 源文件。
- 不提交 Unity Library/Temp、旧 Blender 备份、重复 Windows 构建或本机快捷方式。
- 模型与贴图由 `.gitattributes` 指定使用 Git LFS；不要移除 `.meta` 或只上传单个 `.unity` 场景。
