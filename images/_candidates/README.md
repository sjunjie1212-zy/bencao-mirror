# 本草镜候选影像入库与验收

当前状态：所有 46 味 **0/46 张母图通过**。现有 38 味的旧图在网页隔离，8 味仅以“未验收 AI 原型预览”展示。

**验收单位是每味一张母图**（`images/_masters/`），七个图位是它的派生视角——详见 `images/_masters/README.md`。

## 仅将候选图放入 GitHub

- 先确认实物参考：物种/药材来源、药用部位、参考图 URL、作者、许可、观察特征。
- 创建压缩包，例如 `bc007-rebuild.zip`，包内只允许平铺文件，不得包含子目录：
  - `master-v1.webp`（**可选**，母图；一旦有母图，七个图位就该是它的派生）
  - `hero-v2.webp`（也支持 specimen/detail-01…detail-05 和 avif/png/jpg）
  - `evidence.json`（母图与图位各自的来源，示例如下）
- 把 ZIP 上传 GitHub `main/asset-import/candidates/`。**新工作流只会把母图移到 `images/_masters/`、把图位移到 `images/_candidates/bc007/`，并清除暂存 ZIP；不会把任何一张标记为正式或通过，不会覆盖 `images/` 根目录，也不会解除网页隔离。**
- 已经同名的文件不覆盖，重做时递增版本号如 `hero-v3.webp`。不经过验证的图片不得跳过候选目录。

```json
{
  "herb_id": "bc007",
  "master": {
    "file": "master-v1.webp",
    "source_kind": "self_shot",
    "source_page": "",
    "source_file": "",
    "photographer": "自拍 / 项目自有",
    "license": "internal-original",
    "license_url": "",
    "taxon_claimed": "Lonicera japonica Thunb.",
    "medicinal_part": "干燥花蕾或带初开的花",
    "observed_feature": "干燥黄白色棒状花蕾，被短柔毛，上粗下细稍弯曲",
    "verified": false
  },
  "assets": [
    {
      "file": "hero-v2.webp",
      "reference_url": "https://example.org/verified-specimen-photo",
      "reference_taxon": "Lonicera japonica Thunb.",
      "reference_part": "dried flower buds or opening flowers",
      "source_author": "source credit / collector",
      "source_license": "documented license or internal-original",
      "observed_feature": "dried yellow-white or green-white tubular buds with fine short hairs",
      "approved": false
    }
  ]
}
```

- `source_kind` 只能是 `self_shot` 或 `open_license`：后者必须同时给全 `photographer`、`license`、`license_url`、`source_page`。
- 仅授权内部比对的第三方图（如香港理工大学中药资料库的教学标本照）标 `third_party_review_only: true`，**会被直接拒绝入库**——它在公开仓库里就是侵权。
- 上例中的 URL 是**字段示例而非实际可靠来源**，不得作为 BC.007 的审核依据。
- 上传只能提交候选。`verified` / `approved` 由上传者写成 `true` 会被拒绝；它们只能由人工在登记表里置位。

## 验收与发布

1. **先验收母图。** 核对药典基源、实物身份、药用部位与许可；检查全分辨率画面，排除虚构结构、错误种仁/果核与拼版。母图不过，该味七个图位一律不许通过。
2. 母图通过后，逐张核验七个派生图位。**同一味的七张来自同一张母图是设计如此**；要查的是它们是否各自承担了封面/远景/中景/细节的观察职责，以及有没有夸大或补出母图里不存在的东西。
3. 验收人把依据填入 `data/visual-qa-register.json`：母图填 `masters[0]` 的 `verified`、`reviewer`、`evidence`；图位填 `derived_from`（指向本味母图）、`output_file`、三个 `*_verified` 与 `approved`。一次未通过只能保持待审或拒收，不能“先标记通过以后再核验”。
4. `source_verified`、`medicinal_part_verified`、`visual_verified` 必须全部为 true，并附实际候选文件、发布文件、审核人和非空证据列表；CI 只验证记录完整性与母图跨味不重复，不替代专业人员的药材鉴定。
5. 一味七张全部通过后，人工复核资产对应的药材身份、图位与网页映射，提交到正式 `images/` 目录，更新 manifest、索引、网站映射、QA 登记表与 Pages 发布校验。
6. AI 合成或示意图继续显著标记为 AI，不得称为真实实物记录。若没有可验证断面资料，宁可留空，不得凭空生成。

**注意**：`images/_candidates/`、`images/_masters/` 与正式资产都在公开 GitHub 仓库中，候选图不在网页目录展示，但 GitHub 文件 URL 本身是公开的。
