# BC.007 金银花 Hero · 真实摄影源首轮筛选（2026-09-20）

结论：**两张可追溯摄影源均不批准为 Hero；不上传正式资产，不恢复网页展示。** 这是单图 Hero 参考筛选，不意味着两张均为其他物种。

## 候选 01：干菊花与干金银花同框

- 文件页：https://commons.wikimedia.org/wiki/File:Dried_Chrysanthemum_and_Dried_Honeysuckles.jpg
- 摄影：Peachyeung316；授权：CC BY-SA 4.0（https://creativecommons.org/licenses/by-sa/4.0/）；原图尺寸：5184×3888。
- 通过 GitHub Actions 下载原始照片并在全幅、局部裁切画面中检查。左侧为大量干菊花，右侧为透明包装袋中的金银花，画面有红色零售标签。
- 判定：**不通过 Hero**。混合药材、塑料袋及标签不能在保留足够的自然标本构图与单独花蕾细节的同时干净消除；禁止 AI 生成不存在的袋外药材结构来修补。
- 真实干燥药材的右侧部分可作内部形态参照，不能未经独立验收充当正式图集；保留作者/授权信息。

## 候选 02：单独干金银花密集纹理

- 文件页：https://commons.wikimedia.org/wiki/File:Dried_honeysuckle.jpg
- 由 Commons MediaWiki API 读取原图和元数据：作者 François Nguyen；许可证 CC BY 2.0（https://creativecommons.org/licenses/by/2.0）；2448×2448；文件描述 Dried honeysuckle；Commons 分类 Lonicera japonica。
- 原图为密集干燥花材全幅近景，能见大量浅绿、黄白、弯曲花蕾/花部，但单根完整花蕾的顶部、基部轮廓难以分辨，缺少可靠尺度对照，背景完全被材料填满。
- 判定：**不通过 Hero**：不能清晰呈现完整个体、鉴别性形态与具有留白的主体构图。暂列 Detail 表面纹理的待核来源，不自动批准图像内容；分类和文件描述并不构成凭证式基源鉴定。

## 下一轮筛选门槛

- 优先带可靠基源标识的干燥金银花药材照片，至少有清晰的独立棒状花蕾可辨顶部、下端、略弯曲和短柔毛；整张照片不混入其他药材、包装、人物或大幅文字。
- 取材必须有合法使用权限、作者和来源记录；不可把大学受版权保护的教学标本照擅自搬入公开 GitHub。
- 即使实拍参考来源通过授权检查，仍要检查实际 Hero 裁切画面；材料呈现不清楚时不入候选或正式库。
- 当前 `data/visual-qa-register.json` 中 BC.007/hero 的 `approved` 保持 false；当前网站图集继续暂停展示。
