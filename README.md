# 蓝色大肥鱼二创表情包

面向 Meme Manager 整理的「蓝色大肥鱼 / 鲸鱼娘 / DeepSeek 娘」静态 + 动态二创表情包。

当前版本优先收录**来源可追溯、许可说明明确**的二创素材。仓库会把上游 4×4 动作序列图自动转换为聊天用动态 GIF，同时抽取代表性帧生成静态 PNG。网络上作者或授权不明的合集只作为发现线索，不直接混入可分发资源。

## 当前内容

第一批素材来自 `YunYueSama/codex-deepseek-pet` 中作者有权授权的生成素材，包括：

- 挥手、走路、跳跃
- 吃饭、饭团剧情
- 睡觉
- 跳舞、哼歌
- 偷吃 / 搞怪
- token 梗
- 尾巴轻摆
- 待机回复

当前自动生成：

- **15 个动态 GIF**
- **60 张静态 PNG**
- 15 个聊天语义分类
- 完整来源、SHA-256、尺寸、帧号和许可记录

## 目录

- `manifest.json`：包信息、兼容版本与分类说明
- `memes_data.json`：分类兼容说明
- `sources.json`：上游素材 URL、目标分类、输出文件名和许可
- `source_index.json`：自动生成的哈希、尺寸、来源、动态/静态类型映射
- `scripts/build_memes.py`：下载序列图，生成动态 GIF 与静态 PNG
- `memes/<category>/*.gif`：动态表情，保留原有路径以兼容现有使用方式
- `memes/<category>/static/*.png`：静态表情
- `previews/cover.png`：封面
- `previews/overview.png`：动态表情总览
- `previews/static-overview.png`：静态表情总览
- `LICENSES/`：上游许可原文

## 自动构建

仓库中的 GitHub Actions 会在 `sources.json` 或构建脚本变化时：

1. 从公开上游仓库下载原始动作序列图；
2. 按 4×4 网格拆成 16 帧；
3. 去除纯品红背景并缩放为 256×256 聊天表情尺寸；
4. 生成透明动态 GIF；
5. 从每组序列中抽取第 1、6、11、16 帧，生成静态 PNG；
6. 生成动态/静态总览图和 `source_index.json`；
7. 自动提交生成结果。

## 静态表情策略

当前静态表情不是从授权不明的网络图片直接搬运，而是从已经纳入许可记录的动作序列中抽帧生成。

这样有几个好处：

- 每张静态 PNG 都能对应到明确的上游源文件；
- 可以记录具体 `frame_index`；
- 静态图与动态 GIF 风格保持一致；
- 不会把「来源不明」误标成「可自由商用」。

后续如果某个公开静态表情包的原作者和许可能够核实，可以继续加入 `sources.json` 或独立静态来源清单。

## 来源与署名

主要素材来源：

作者：YunYueSama  
仓库：https://github.com/YunYueSama/codex-deepseek-pet

其作者有权授权的图片、设计图、动画、角色设定与文档适用「大肥鱼项目署名许可 1.0」，允许使用、修改、分享及商用，但必须保留作者、仓库地址及完整许可文本。本仓库生成的 GIF 和静态 PNG 都属于经过修改/处理的衍生文件。

本仓库**不收录**上游明确标记为原作者/授权待核实的社区参考图，例如 `assets/你这吃白饭的蓝色大肥鱼.png`，也不把不明来源素材标记为自由授权。

## 其他公开二创索引

整理过程中还发现以下公开项目，可作为后续扩充与来源核对线索：

- `anka-afk/blue-fat-fish-meme-pack`
- `EDMOK/blue-fish-archive`
- `lmy414/ai-girl-stickers`
- `the-beating-light-of-the-nail/deepseek-chan-meme-pack`

这些项目中的素材许可状态并不完全相同，因此不会未经核对就自动复制。

## 权利说明

「蓝色大肥鱼 / 鲸鱼娘 / DeepSeek 娘」属于社区二创语境。本仓库不宣称拥有底层角色、品牌、商标或第三方参考作品的权利，也不表示 DeepSeek 官方授权或背书。

若你是相关权利人，需要补充署名、修正来源或移除内容，可通过仓库 Issue 联系维护者。

## 维护

Meme Manager 适配与整理：wedfkewn
