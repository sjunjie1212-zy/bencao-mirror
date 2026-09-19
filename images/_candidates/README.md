# 本草镜候选影像入库与逐张验收

当前状态：所有 46 味 **0/46 套正式七图通过**。现有 38 味的旧图在网页隔离，8 味仅以“未验收 AI 原型预览”展示。

## 仅将候选图放入 GitHub

- 一张候选图先确认实物参考：物种/药材来源、药用部位、参考图 URL、作者、许可、观察特征。
- 创建压缩包，例如 `bc007-hero-rebuild.zip`，包内只允许平铺文件，不得包含子目录：
  - `hero-v2.webp`（也支持 specimen/detail-01…detail-05 和 avif/png/jpg）
  - `evidence.json`（为包内每张图分别列出来源，示例如下）。
- 把 ZIP 上传 GitHub `main/asset-import/candidates/`。**新工作流只会把文件移动到 `images/_candidates/bc007/` 并清除暂存 ZIP；不会把图标记为正式、覆盖 `images/` 根目录或解除网页隔离。**
- 已经同名的候选文件不覆盖，重做时递增版本号如 `hero-v3.webp`。不经过逐张验证的图片不得跳过候选目录。

```json
{
  "herb_id": "bc007",
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

上例中的 URL 是**字段示例而非实际可靠来源**，不得作为 BC.007 的审核依据。

## 严格验收与发布

1. 核对药典基源、原始标本和参考图许可，检查生成后的整张图片以及必要的高清局部，排除虚构结构和错误种仁/果核。
2. 验收人对每个角色独立记录依据，填入 `data/visual-qa-register.json`。一次未通过只能保持待审或拒收，不能“先标记通过以后再核验”。
3. 审核表中的 `source_verified`、`medicinal_part_verified`、`visual_verified`、`independence_verified` 必须全部为 true，并附实际候选文件、参考文件、审核人和非空证据列表；CI 仅验证记录完整性，不替代专业人员的药材鉴定。
4. 一味七张全部逐张验收通过后，人工复核最终资产对应的药材身份、图位与网页映射，提交到正式 `images/` 目录，更新 manifest、索引、网站映射、QA 登记表与 Pages 发布校验。
5. AI 合成或示意图继续显著标记为 AI，不得称为真实实物记录。若没有可验证断面资料，宁可留空，不得凭空生成。

**注意**：`images/_candidates/` 与正式资产都在公开 GitHub 仓库中，候选图不在网页目录展示，但 GitHub 文件 URL 本身是公开的。
