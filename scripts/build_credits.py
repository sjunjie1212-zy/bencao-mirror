#!/usr/bin/env python3
"""生成 credits.html —— 影像来源与署名页。

本草镜公开测试版展示的 322 张影像（46 味 × 7 张）**全部**来自生成式流程，
不是实拍药材记录。其中大部分以 Wikimedia Commons 的公开许可照片为参考源。

这件事必须在页面上说清楚，原因有两个：
  1. 项目红线：AI 生成影像必须对使用者可见标注，不能只写在仓库文档里。
  2. 许可义务：以 CC BY / CC BY-SA 素材为参考源产生的演绎影像，仍受署名与
     相同方式共享约束。把来源只留在 images/_manifests/ 里不算履行。

数据全部来自已有清单，不手工维护：
  images/_manifests/manifest-bc007-bc040-bc046.json   参考源，含 author/license
  images/_manifests/manifest-bc041-bc045.csv          只有文件信息，参考源未记录
  app46.js                                            BC.001–BC.006 的编号与名称

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
UNRECORDED = MANIFEST_DIR / "manifest-bc041-bc045.csv"
APP = ROOT / "app46.js"
OUT = ROOT / "credits.html"

IMAGES_PER_HERB = 7

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
    digits = re.sub(r"\D", "", code or "")
    return int(digits) if digits else 0


def norm_code(code: str) -> str:
    """清单里编号写法不一（BC.007 / BC041），统一成 BC.0NN 再展示。"""
    return f"BC.{code_num(code):03d}"


def read_commons() -> list[dict]:
    rows = json.loads(COMMONS.read_text(encoding="utf-8"))
    return sorted(rows, key=lambda r: (code_num(r["code"]), ROLE_ORDER.get(r["role"], 99)))


def read_unrecorded() -> list[dict]:
    with UNRECORDED.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return sorted(rows, key=lambda r: (code_num(r["code"]), ROLE_ORDER.get(r["role"], 99)))


def read_early_herbs() -> list[tuple[str, str]]:
    """BC.001–BC.006 的编号与名称，从 app46.js 取，避免在这里再抄一份。"""
    src = APP.read_text(encoding="utf-8")
    found = re.findall(r"id:'(bc00[1-6])',no:'(BC\.\d{3})',name:'([^']+)'", src)
    return sorted(((no, name) for _, no, name in found), key=lambda x: code_num(x[0]))


def read_early_images() -> dict[str, list[str]]:
    """BC.001–BC.006 实际展示的 7 个文件名。

    这六味有影像但没有参考源清单，同样属于「来源未记录」，所以要和
    BC.041–BC.045 一起列在 TYPE 03 里，而不是不声不响地跳过。
    """
    src = APP.read_text(encoding="utf-8")
    out: dict[str, list[str]] = {}
    for m in re.finditer(
        r"id:'(bc00[1-6])',no:'(BC\.\d{3})',name:'[^']+'.*?images:\[(.*?)\]", src, re.S
    ):
        files = re.findall(r"\./images/([^']+)", m.group(3))
        out[m.group(2)] = files
    return out


def group_by_code(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row["code"], []).append(row)
    return out


def herb_name(groups: dict[str, list[dict]], code: str) -> str:
    rows = groups.get(code) or []
    return (rows[0].get("chinese_name") if rows else "") or ""


def render_all_herbs(early: list[tuple[str, str]], commons: dict, unrecorded: dict) -> str:
    """46 味全列，每味 7 张。名称取自清单，BC.001–BC.006 取自 app46.js。"""
    codes: list[tuple[int, str, str]] = []
    for no, name in early:
        codes.append((code_num(no), norm_code(no), name))
    for code in commons:
        codes.append((code_num(code), norm_code(code), herb_name(commons, code)))
    for code in unrecorded:
        codes.append((code_num(code), norm_code(code), herb_name(unrecorded, code)))
    seen = set()
    items = []
    for num, code, name in sorted(codes):
        if code in seen:
            continue
        seen.add(code)
        items.append(f'<li><b>{esc(code)} {esc(name)}</b><span>{IMAGES_PER_HERB} 张</span></li>')
    return f'<ul class="credit-ai">{"".join(items)}</ul>'


def render_sources(groups: dict[str, list[dict]]) -> str:
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
                f'<a href="{esc(source)}" rel="noopener" target="_blank">'
                f'{esc(row.get("source_title") or source)}</a>'
                if source
                else "—"
            )
            body.append(
                "<tr>"
                f'<td data-label="参考影像">{esc(ROLE_ZH.get(row["role"], row["role"]))}</td>'
                f'<td data-label="生成的展示文件"><code>{esc(row["filename"])}</code></td>'
                f'<td data-label="原作者">{esc(author)}</td>'
                f'<td data-label="许可">{license_cell}</td>'
                f'<td data-label="来源">{source_cell}</td>'
                "</tr>"
            )
        parts.append(
            f'<section class="credit-herb"><h3><span>{esc(norm_code(code))}</span>{esc(name)}'
            f'<small>{len(rows)} 张</small></h3><div class="credit-table-wrap"><table>'
            "<thead><tr><th>参考影像</th><th>生成的展示文件</th><th>原作者</th><th>许可</th><th>来源</th></tr></thead>"
            f'<tbody>{"".join(body)}</tbody></table></div></section>'
        )
    return "".join(parts)


def render_unrecorded(
    groups: dict[str, list[dict]],
    early_images: dict[str, list[str]],
    early_names: dict[int, str],
) -> str:
    """列出来源未记录的条目：清单里没有署名信息的那几味，加上 BC.001–BC.006。"""
    entries: list[tuple[int, str, str, list[str]]] = []
    for code in sorted(groups, key=code_num):
        rows = groups[code]
        entries.append(
            (
                code_num(code),
                norm_code(code),
                rows[0].get("chinese_name") or "",
                [r["filename"] for r in rows],
            )
        )
    for code, files in early_images.items():
        entries.append((code_num(code), norm_code(code), early_names.get(code_num(code), ""), files))
    parts = []
    for _, code, name, files in sorted(entries):
        listed = "、".join(f"<code>{esc(f)}</code>" for f in files)
        parts.append(
            f'<li><b>{esc(code)} {esc(name)}</b><span>{len(files)} 张</span><p>{listed}</p></li>'
        )
    return "".join(parts)


def build() -> str:
    commons_rows = read_commons()
    unrecorded_rows = read_unrecorded()
    early = read_early_herbs()
    early_images = read_early_images()
    early_names = {code_num(no): name for no, name in early}
    commons = group_by_code(commons_rows)
    unrecorded = group_by_code(unrecorded_rows)

    herb_count = len(early) + len(commons) + len(unrecorded)
    total_images = herb_count * IMAGES_PER_HERB
    unrecorded_herbs = len(unrecorded) + len(early_images)
    unrecorded_images = len(unrecorded_rows) + sum(len(f) for f in early_images.values())
    attribution_required = sum(
        1 for r in commons_rows if (r.get("license") or "").startswith("CC BY")
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="#ECE9E1" />
<title>影像来源与署名｜本草镜 BENCAO MIRROR</title>
<meta name="description" content="本草镜公开测试版影像的来源、生成方式、原作者与许可。" />
<link rel="stylesheet" href="./styles.css?v=365vf3" />
<link rel="stylesheet" href="./beta.css?v=400b1" />
<style>
.credits-page{{max-width:1180px;margin:0 auto;padding:64px clamp(18px,4vw,48px) 120px}}
.credits-page h1{{font-size:clamp(38px,5vw,64px);font-weight:400;margin:18px 0 22px;letter-spacing:.02em}}
.credits-lede{{max-width:760px;color:var(--graphite);line-height:1.9;font-size:15px}}
.credits-lede strong{{color:var(--ink);font-weight:400}}
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
  <p class="credits-lede"><strong>本草镜公开测试版展示的全部 {total_images} 张影像（{herb_count} 味 × {IMAGES_PER_HERB} 张）都是 AI 生成图像</strong>，不是实拍药材记录。其中大部分以 Wikimedia Commons 的公开许可照片为参考源。页面在每张卡片和每个条目上都标了「AI 生成影像」。</p>
  <p class="credits-lede">这件事有两层后果，都写在这一页里。第一，影像是为了建立观察路径与页面节奏，<strong>不能作为植物学鉴定、药材真伪或质量依据</strong>。第二，以 CC BY / CC BY-SA 素材为参考源产生的演绎影像，仍然带着署名与相同方式共享的义务：下面列出了 {len(commons_rows)} 条参考源的作者与许可，其中 {attribution_required} 条属于 CC BY 或 CC BY-SA。</p>
  <div class="credits-rule"></div>

  <section class="credits-section">
    <p class="eyebrow">TYPE 01 / GENERATED</p>
    <h2>AI 生成影像（{total_images} 张 · {herb_count} 味）</h2>
    <p>每一味 7 张：主图、标本、细节 01–05。全部来自生成式流程，没有一张是实拍记录。</p>
    {render_all_herbs(early, commons, unrecorded)}
  </section>

  <section class="credits-section">
    <p class="eyebrow">TYPE 02 / SOURCE MATERIAL</p>
    <h2>参考源与署名（{len(commons_rows)} 条 · {len(commons)} 味）</h2>
    <p>生成这些影像时使用的公开许可参考素材。作者与许可逐条列出，许可名称可点开查看条款原文，「来源」指向 Commons 上的文件页。请注意：左侧是<strong>参考影像</strong>，右侧才是本草镜实际展示的<strong>生成文件</strong>——两者不是同一个文件。CC BY-SA 要求以相同方式共享，这项义务随演绎影像一起延续。</p>
    {render_sources(commons)}
  </section>

  <section class="credits-section">
    <p class="eyebrow">TYPE 03 / SOURCE UNRECORDED</p>
    <h2>参考源未记录（{unrecorded_images} 张 · {unrecorded_herbs} 味）</h2>
    <p>这些影像同样是生成的，但对应清单里没有作者、许可与来源字段（BC.001–BC.006 则完全没有清单），因此无法在此署名。在补齐来源之前，不要把它们当作可核查的素材对外使用；补齐后这一节会并入上一节。</p>
    <ul class="credits-pending">{render_unrecorded(unrecorded, early_images, early_names)}</ul>
  </section>

  <a class="credits-back" href="./">← 回到本草目录</a>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
