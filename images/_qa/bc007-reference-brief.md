# BC.007 金银花 · 重建参考锚点（2026-09-20）

状态：**仅锁定药材身份和视觉参考，未批准任何新图；Hero 仍待合格实物摄影素材。**

## 真实药材身份

- 药材：金银花 / Lonicerae Japonicae Flos，来源植物：忍冬 *Lonicera japonica* Thunb.。
- 药用部位：干燥花蕾或带初开的花；不把整株活体花枝、叶片、藤蔓和已完全盛开的鲜花用作本草镜干燥药材 Hero/Specimen。
- 干燥花蕾外观核对：棒状，上粗下细、稍弯曲，长约 2–3 cm；上端宽约 3 mm，下端约 1.5 mm；黄白或绿白色，短柔毛密被。参考：
  - 南京中医药大学中药标本馆：https://zybb.njucm.edu.cn/yaocai_info.asp?unid=134
  - 神农 Alpha / 《中国药典（2020 年版）》对应条目：https://shennongalpha.westlake.edu.cn/en-zh/knowledge/nmm-01af
- 参考实物照片：香港理工大学中药资料库的金银花干燥药材标本（含 1 cm 比例尺）：
  https://herbaltcm.sn.polyu.edu.hk/tc/herbal/japanese-honeysuckle-flower
  **许可注意**：该大学版权声明不允许在未经许可情况下复制和发布受版权保护的资料。此图只能作内部形态比对，不得直接下载进 GitHub、裁切重发或将其当作开放授权的照片。
  版权声明：https://herbaltcm.sn.polyu.edu.hk/sc/copyright

## Hero 候选图验收清单

1. 同一画面为干燥忍冬花蕾实物，单张摄影；主体完整，不出现海报/拼版/文字。
2. 每根花蕾的顶部、基部和尺度须与实物摄影及上述文字基准相符；不能是过长的纤维条、剥开的花瓣、花梗堆或细枝。
3. 图像来源需具备公开许可及正确署名，或者为可证明来源的自有摄影；如仅作 AI 示意，必须明显标记 AI，不能据此作药材鉴别。
4. 保留花蕾之间的自然差异、淡色短柔毛和足够锐度；暖米白自然光仅作视觉处理，不可生成实物未见的内部结构。
5. 当前两轮旧 Hero AI 候选未通过形态审核，不复用也不上传候选目录。宁缺勿滥；先获取合法可用的真实干燥药材母图，方启动正式 Hero 制作。

## 审核路径

候选文件：`images/_candidates/bc007/hero-v2.webp`（尚未生成/入库）。
候选来源记录：随候选 ZIP 提交到 `asset-import/candidates/`，经 staging 工作流单独归档，状态只能是未通过。
逐图登记：`data/visual-qa-register.json` 中 `bc007` / `hero`；当前不得设置 `approved: true`。

如果后续取得大学标本图库的书面复用授权或自有实拍图，再记录可用许可并核对基源，不将仅用于审核的第三方图片偷换为可发布正式图。
