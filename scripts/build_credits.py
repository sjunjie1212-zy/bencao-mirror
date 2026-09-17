#!/usr/bin/env python3
"""生成 credits.html —— 影像来源与署名页。

站点是公开的 GitHub Pages，很多影像是 Wikimedia Commons 的 CC BY / CC BY-SA
素材。这些许可要求我们对使用者署名、标许可、给出链接；把来源只留在
images/_manifests/ 里不算履行。

数据全部来自已有清单，不手工维护：
  images/_manifests/manifest-bc007-bc040-bc046.json   Commons 那批，含 author/license
  images/_manifests/manifest-bc041-bc045.csv          只有文件信息，缺来源字段
  app46.js                                            BC.001–BC.006 的编号与名称

BC.001–BC.006 是生成式流程产出的影像（见 app46.js 的 AI_ASSET_IDS），
没有外部权利人可署名，单独列一节并明确标注 AI 生成。

用法：python3 scripts/build_credits.py    （在仓库根目录执行）
"""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = ROOT / "images" / "_manifests"
COMMONS = MANIFEST_DIR / "manifest-bc007-bc040-bc046.json"
PENDING = MANIFEST_DIR / "manifest-bc041-bc045.csv"
APP = ROOT / "app46.js"
OUT = ROOT / "credits.html"

ROLE_ZH = {
    "hero": "主图",
    "specimen": "标本",
    "detail-01": "细节 01",
    "detail-02": "细节 02",
    "detail-03": "细节 03",
    "detail-04": "细节 04",
    "detail-05": "细节 05",
}
ROLE_ORDER = {k: i for i, k in enumerate(ROLE_ZH)}


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def code_num(code: str) -> int:
    digits = re.sub(r"\D", "", code)
    return int(digits) if digits else 0


def read_commons() -> list[dict]:
    rows = json.loads(COMMONS.read_text(encoding="utf-8"))
    return sorted(rows, key=lambda r: (code_num(r["code"]), ROLE_ORDER.get(r["role"], 99)))


def read_pending() -> list[dict]:
    with PENDING.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return sorted(rows, key=lambda r: (code_num(r["code"]), ROLE_ORDER.get(r["role"], 99)))


def read_ai_herbs() -> list[tuple[str, str]]:
    """从 app46.js 取 BC.001–BC.006 的编号与名称，避免在这里再抄一份。"""
    src = APP.read_text(encoding="utf-8")
    found = re.findall(r"id:'(bc00[1-6])',no:'(BC\.\d{3})',name:'([^']+)'", src)
    return sorted(((no, name) for _, no, name in found), key=lambda x: code_num(x[0]))


def group_by_code(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row["code"], []).append(row)
    return out


def render_commons(groups: dict[str, list[dict]]) -> str:
    parts = []
    for code in sorted(groups, key=code_num):
        rows = groups[code]
        name = rows[0].get("chinese_name") or ""
        body = []
        for row in rows:
            author = row.get("author") or "（未记录）"
            license_name = row.get("license") or "（未记录）"
            url = row.get("license_url") or ""
            license_cell = (
                f'<a href="{esc(url)}" rel="license noopener" target="_blank">{esc(license_name)}</a>'
                if url
                else esc(license_name)
            )
            source = row.get("source_page") or ""
            source_cell = (
                f'<a href="{esc(source)}" rel="noopener" target="_blank">{esc(row.get("source_title") or source)}</a>'
                if source
                else "—"
            )
            body.append(
                "<tr>"
                f'<td data-label="角色">{esc(ROLE_ZH.get(row["role"], row["role"]))}</td>'
                f'<td data-label="文件"><code>{esc(row["filename"])}</code></td>'
                f'<td data-label="作者">{esc(author)}</td>'
                f'<td data-label="许可">{license_cell}</td>'
                f'<td data-label="来源">{source_cell}</td>'
                "</tr>"
            )
        parts.append(
            f'<section class="credit-herb"><h3><span>{esc(code)}</span>{esc(name)}'
            f'<small>{len(rows)} 张</small></h3><div class="credit-table-wrap"><table>'
            "<thead><tr><th>角色</th><th>文件</th><th>作者</th><th>许可</th><th>来源</th></tr></thead>"
            f'<tbody>{"".join(body)}</tbody></table></div></section>'
        )
    return "".join(parts)


def render_pending(groups: dict[str, list[dict]]) -> str:
    parts = []
    for code in sorted(groups, key=code_num):
        rows = groups[code]
        name = rows[0].get("chinese_name") or ""
        files = "、".join(f'<code>{esc(r["filename"])}</code>' for r in rows)
        parts.append(
            f'<li><b>{esc(code)} {esc(name)}</b><span>{len(rows)} 张</span><p>{files}</p></li>'
        )
    return "".join(parts)


def render_ai(herbs: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<li><b>{esc(no)} {esc(name)}</b><span>7 张</span></li>' for no, name in herbs
    )
    return f'<ul class="credit-ai">{items}</ul>'


def build() -> str:
    commons = read_commons()
    pending = read_pending()
    ai_herbs = read_ai_herbs()
    ai_count = len(ai_herbs) * 7
    commons_groups = group_by_code(commons)
    pending_groups = group_by_code(pending)
    attribution_required = sum(
        1 for r in commons if (r.get("license") or "").startswith("CC BY")
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="#ECE9E1" />
<title>影像来源与署名｜本草镜 BENCAO MIRROR</title>
<meta name="description" content="本草镜公开测试版所用影像的来源、作者与许可。" />
<link rel="stylesheet" href="./styles.css?v=365vf3" />
<link rel="stylesheet" href="./beta.css?v=400b1" />
<style>
.credits-page{{max-width:1180px;margin:0 auto;padding:64px clamp(18px,4vw,48px) 120px}}
.credits-page h1{{font-size:clamp(38px,5vw,64px);font-weight:400;margin:18px 0 22px;letter-spacing:.02em}}
.credits-lede{{max-width:760px;color:var(--graphite);line-height:1.9;font-size:15px}}
.credits-rule{{height:1px;background:var(--fiber,rgba(24,23,19,.14));margin:56px 0}}
.credits-section{{margin-top:64px}}
.credits-section>h2{{font-size:clamp(24px,3vw,34px);font-weight:400;margin:10px 0 14px}}
.credits-section>p{{max-width:780px;color:var(--graphite);line-height:1.9;font-size:14px}}
.credit-herb{{margin-top:40px}}
.credit-herb h3{{font-weight:400;font-size:20px;margin:0 0 14px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.credit-herb h3 span{{font:10px/1 var(--sans,inherit);letter-spacing:.14em;color:var(--graphite)}}
.credit-herb h3 small{{font:10px/1 var(--sans,inherit);letter-spacing:.08em;color:var(--graphite);margin-left:auto}}
.credit-table-wrap{{overflow-x:auto;border-top:1px solid rgba(24,23,19,.14)}}
.credit-table-wrap table{{width:100%;border-collapse:collapse;font-size:12.5px}}
.credit-table-wrap th{{text-align:left;font:9px/1 var(--sans,inherit);letter-spacing:.14em;color:var(--graphite);padding:12px 14px 10px 0;text-transform:uppercase;white-space:nowrap}}
.credit-table-wrap td{{padding:10px 14px 10px 0;border-top:1px solid rgba(24,23,19,.08);vertical-align:top;line-height:1.7}}
.credit-table-wrap td code{{font-size:11.5px;word-break:break-all}}
.credit-table-wrap a{{color:var(--cinnabar,#8C3A2B);text-decoration:none;border-bottom:1px solid rgba(140,58,43,.3)}}
.credit-ai{{list-style:none;padding:0;margin:22px 0 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:2px 24px}}
.credit-ai li{{display:flex;gap:10px;align-items:baseline;padding:12px 0;border-top:1px solid rgba(24,23,19,.08)}}
.credit-ai li b{{font-weight:400}}
.credit-ai li span{{margin-left:auto;font:10px/1 var(--sans,inherit);color:var(--graphite)}}
.credits-pending{{list-style:none;padding:0;margin:22px 0 0}}
.credits-pending li{{padding:14px 0;border-top:1px solid rgba(24,23,19,.08);display:flex;gap:12px;flex-wrap:wrap;align-items:baseline}}
.credits-pending li b{{font-weight:400}}
.credits-pending li span{{font:10px/1 var(--sans,inherit);color:var(--graphite)}}
.credits-pending li p{{margin:0;flex-basis:100%;font-size:12px;color:var(--graphite);line-height:1.9;word-break:break-all}}
.credits-back{{display:inline-block;margin-top:70px;color:var(--cinnabar,#8C3A2B);text-decoration:none;border-bottom:1px solid rgba(140,58,43,.35);padding-bottom:3px}}
@media(max-width:640px){{.credit-table-wrap thead{{display:none}}.credit-table-wrap tr{{display:block;padding:12px 0;border-top:1px solid rgba(24,23,19,.1)}}.credit-table-wrap td{{display:block;border:0;padding:2px 0}}.credit-table-wrap td::before{{content:attr(data-label)"：";color:var(--graphite);font-size:11px}}}}
</style>
</head>
<body>
<main class="credits-page">
  <p class="eyebrow">CREDITS / 影像来源</p>
  <h1>影像来源与署名</h1>
  <p class="credits-lede">本草镜公开测试版目前使用三类影像：AI 生成图像、Wikimedia Commons 的公开许可素材、以及来源尚待补齐的资产。这一页把每一张的去向写清楚。本草镜不对影像做植物学鉴定或药材质量证明；影像用于材料观察与产品体验。</p>
  <p class="credits-lede">署名与许可是使用条件，不是礼节。Commons 那批里有 {attribution_required} 张属于 CC BY 或 CC BY-SA，要求署名、标明许可并给出链接；CC BY-SA 还要求以相同方式共享。CC0 与公有领域的素材我们也一并列出，方便核对。</p>
  <div class="credits-rule"></div>

  <section class="credits-section">
    <p class="eyebrow">TYPE 01 / GENERATED</p>
    <h2>AI 生成影像（{ai_count} 张）</h2>
    <p>以下条目的影像来自生成式流程，不是真实药材的摄影记录。页面在卡片与条目页对这些影像显示「AI 生成影像」标记。它们用于建立观察路径与页面节奏，不能作为植物学鉴定、药材真伪或质量依据。</p>
    {render_ai(ai_herbs)}
  </section>

  <section class="credits-section">
    <p class="eyebrow">TYPE 02 / LICENSED</p>
    <h2>公开许可素材（{len(commons)} 张 · {len(commons_groups)} 味）</h2>
    <p>来自 Wikimedia Commons。作者与许可按条目逐张列出，许可名称可点开查看条款原文，来源列指向 Commons 上的文件页。</p>
    {render_commons(commons_groups)}
  </section>

  <section class="credits-section">
    <p class="eyebrow">TYPE 03 / PROVENANCE PENDING</p>
    <h2>来源待补（{len(pending)} 张 · {len(pending_groups)} 味）</h2>
    <p>这些资产已经上线，但对应清单里没有作者、许可与来源字段，因此无法在此署名。在补齐来源之前，不要把它们当作可核查的素材对外使用；补齐后这一节会并入上一节。</p>
    <ul class="credits-pending">{render_pending(pending_groups)}</ul>
  </section>

  <a class="credits-back" href="./">← 回到本草目录</a>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
