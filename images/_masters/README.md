# 母图库（master photographs）

本草镜的验收单位是**每味一张母图**。图集里的七个图位——`hero`（封面）、`specimen`（整体远景）、
`detail-01`…`detail-05`（中景与局部放大）——都是这一张母图的不同尺度视角，按设计共用它。
所以「同一味的七张来自同一张母图」不是缺陷；**缺陷是母图本身不合格，或者两个药材共用同一张母图。**

本目录存放通过验收的母图，登记在 `data/visual-qa-register.json` 的 `herbs[].masters`，
由 `scripts/validate_visual_qa.py` 在 Pages 发布前强制校验。

## 硬规则：母图必须自有或开放许可

本目录在**公开仓库**里，GitHub 文件 URL 本身是公开的。因此：

- ✅ **自有拍摄**（`source_kind: "self_shot"`）：无许可风险，来源可证，首选。
- ✅ **开放许可**（`source_kind: "open_license"`）：CC BY / CC BY-SA / CC0，且必须记全
  `license`、`license_url`、`photographer`、`source_page` 四项。CC BY-SA 的相同方式共享
  义务随演绎图一起延续。
- ❌ **仅授权「内部比对」的第三方图不得入库。** 例：香港理工大学中药资料库的教学标本照，
  其版权声明不允许未经许可复制和发布（见 `images/_qa/bc007-reference-brief.md`）。
  这类图只能在本地做形态比对，**不要下载进仓库、不要裁切重发**。
- ❌ 来源不明、只有文件名、或无法回溯到具体文件页的图，一律不收。

## 命名与格式

- 文件名：`bcNNN-master-vN.<ext>`，扩展名限 `jpg` / `jpeg` / `png` / `webp` / `avif`。
- 分辨率：七个图位的发布规格是 **1122×1402（4:5 竖幅）**。母图必须明显大于它——
  `hero` 与 `specimen` 的裁切窗一旦缩到发布尺寸就会糊的母图，直接退回，不要靠放大凑数。
  经验下限 **2400 px 短边**。
- 体积：20 KB – 12 MB（与候选图位同一套校验）。
- `sha256` 必须是文件真实哈希，登记表里的值与文件对不上，门禁会直接失败。

## 母图如何进入仓库

经 `asset-import/candidates/` 的候选 ZIP 通道，由 `scripts/stage_visual_candidates.py` 落盘：

- ZIP 内平铺，含 `evidence.json` + 1–7 张图位，**可额外含一张 `master-vN.<ext>`**。
- 母图落到本目录，图位落到 `images/_candidates/bcNNN/`。
- 两者都**不会**被自动标记 approved，也**不会**写入 `images/` 根目录。
  母图的 `verified` 与图位的 `approved` 只能由人工在登记表里置位。

图位本身（`images/` 根目录的发布文件）不在本目录，见 `images/_candidates/README.md` 的验收流程。
