# 蓝色大肥鱼二创动态表情包

面向 Meme Manager 整理的「蓝色大肥鱼 / 鲸鱼娘 / DeepSeek 娘」动态表情包。

当前版本优先收录**来源可追溯、许可说明明确**的二创素材，并自动把上游 4×4 动作序列图转换为聊天用动态 GIF。网络上作者或授权不明的合集只作为发现线索，不直接混入可分发资源。

## 当前内容

第一批动态表情来自 `YunYueSama/codex-deepseek-pet` 中作者有权授权的生成素材，包括：

- 挥手、走路、跳跃
- 吃饭、饭团剧情
- 睡觉
- 跳舞、哼歌
- 偷吃 / 搞怪
- token 梗
- 尾巴轻摆

构建后的图片放在 `memes/<category>/`，并按与参考包相同的聊天语义分类维护。

## 目录

- `manifest.json`：包信息、兼容版本与分类说明
- `memes_data.json`：分类兼容说明
- `sources.json`：上游素材 URL、目标分类、输出文件名和许可
- `source_index.json`：自动构建后生成的哈希、尺寸与来源映射
- `scripts/build_memes.py`：下载序列图并生成动态 GIF
- `memes/<category>/`：最终表情
- `previews/`：封面与总览
- `LICENSES/`：上游许可原文

## 自动构建

仓库中的 GitHub Actions 会在 `sources.json` 或构建脚本变化时：

1. 从公开上游仓库下载原始动作序列图；
2. 按 4×4 网格拆成 16 帧；
3. 去除纯品红背景并缩放为聊天表情尺寸；
4. 生成透明动态 GIF；
5. 生成封面、总览图和 `source_index.json`；
6. 自动提交生成结果。

## 来源与署名

主要素材来源：

作者：YunYueSama  
仓库：https://github.com/YunYueSama/codex-deepseek-pet

其作者有权授权的图片、设计图、动画、角色设定与文档适用「大肥鱼项目署名许可 1.0」，允许使用、修改、分享及商用，但必须保留作者、仓库地址及完整许可文本。本仓库生成 GIF 属于经过修改的衍生文件。

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
