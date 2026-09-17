#!/usr/bin/env python3
from pathlib import Path
import json,re

plan=json.loads(Path('data/commons-asset-plan.json').read_text(encoding='utf-8'))
slugs={h['id']:h['slug'] for h in plan['herbs']}

app_path=Path('app46.js')
app=app_path.read_text(encoding='utf-8')
app=app.replace("const VERSION='4.0.0-beta.2';","const VERSION='4.0.0';")

for n in range(2,7):
    sid=f'bc{n:03d}'
    hero=f"'./images/{sid}-hero-vf1.webp',"
    plate=f"'./images/{sid}-atlas-plate-vu1.jpg',"
    if hero in app and plate not in app:
        app=app.replace(hero,hero+plate,1)

marker='const T=['
live_map={k:v for k,v in slugs.items() if 'bc007'<=k<='bc040'}
snippet="\nconst LIVE_ASSET_SLUGS="+json.dumps(live_map,ensure_ascii=False,separators=(',',':'))+";\n"+"P.forEach(h=>{const s=LIVE_ASSET_SLUGS[h.id];if(!s)return;h.assetStatus='formal_hd_asset';h.hero=`./images/${h.id}-${s}-hero-v1.webp`;h.images=[`./images/${h.id}-${s}-hero-v1.webp`,`./images/${h.id}-${s}-specimen-v1.webp`,...Array.from({length:5},(_,i)=>`./images/${h.id}-${s}-detail-0${i+1}-v1.webp`)];h.intro='本条目已接入 7 张高清材料观察图，从整体、标本视角到局部纹理连续浏览。';h.note='高清影像用于本草材料观察与产品体验，不替代植物学鉴定、药材质量鉴别或医疗建议。';});\n"
if 'const LIVE_ASSET_SLUGS=' not in app:
    app=app.replace(marker,snippet+marker,1)

start=app.find("herb({assetStatus:'staged',id:'bc046'")
if start!=-1:
    end=app.find('})',start)
    if end!=-1:
        seg=app[start:end+2]
        seg=seg.replace("assetStatus:'staged',","assetStatus:'formal_hd_asset',")
        seg=seg.replace("hero:null,images:[]","hero:'./images/bc046-cheqianzi-hero-v1.webp',images:['./images/bc046-cheqianzi-hero-v1.webp','./images/bc046-cheqianzi-specimen-v1.webp','./images/bc046-cheqianzi-detail-01-v1.webp','./images/bc046-cheqianzi-detail-02-v1.webp','./images/bc046-cheqianzi-detail-03-v1.webp','./images/bc046-cheqianzi-detail-04-v1.webp','./images/bc046-cheqianzi-detail-05-v1.webp']")
        seg=re.sub(r"intro:'[^']*'","intro:'车前子已接入 7 张高清图，展示整体、标本视角与局部细节。'",seg)
        seg=re.sub(r"note:'[^']*'","note:'高清影像用于本草材料观察与产品体验，不替代药材质量鉴别或医疗建议。'",seg)
        app=app[:start]+seg+app[end+2:]
app_path.write_text(app,encoding='utf-8')

index_path=Path('index.html')
index=index_path.read_text(encoding='utf-8')
repls={
'公开测试版。':'高清公开版。',
'本草镜 BENCAO MIRROR｜公开测试版':'本草镜 BENCAO MIRROR｜高清版',
'PUBLIC BETA · 4.0':'HD RELEASE · 4.0',
'PUBLIC TEST / VISUAL ARCHIVE':'HD RELEASE / VISUAL ARCHIVE',
'BC.001–046 已全部开放浏览。<br>正式影像未入库的条目会明确标注“影像待补”。':'BC.001–046 已全部开放浏览。<br>46 味均已接入高清图集。',
'测试重点</span><b>46 味的目录是否清楚、已有图片是否可信、你会不会愿意继续看下一味？</b>':'高清版</span><b>46 味本草已全部接入图集，可连续浏览整体、标本与细节。</b>',
'这是本草镜的朋友测试版。':'这是本草镜的 46 味高清公开版。',
'这一版开放 BC.001–046 全部条目，优先验证信息架构、视觉体验与浏览路径。已有正式资产的条目展示图集；尚未入库的条目明确显示待补状态。':'这一版开放 BC.001–046 全部条目，并接入高清图集，用于连续观察本草材料的整体、标本与细节。',
'./app46.js?v=400b2':'./app46.js?v=400hd1'
}
for a,b in repls.items(): index=index.replace(a,b)
index_path.write_text(index,encoding='utf-8')
Path('bencao-version.txt').write_text('4.0.0\n',encoding='utf-8')

asset_path=Path('images/ASSET_INDEX.md')
asset=asset_path.read_text(encoding='utf-8')
asset=re.sub(r'\| BC\.007–BC\.034 \|[^\n]*','| BC.007–BC.034 | 高清补齐区间 | ✅ 正式完成 7/7；WEBP 1122×1402 | ✅ 已上线 |',asset)
for n,name in [(35,'鸡血藤'),(36,'苏木'),(37,'栀子'),(38,'枳实'),(39,'佛手'),(40,'乌梅')]:
    asset=re.sub(rf'\| BC\.{n:03d} \| {name} \|[^\n]*',f'| BC.{n:03d} | {name} | ✅ 正式完成 7/7；WEBP 1122×1402 | ✅ 已上线 |',asset)
asset=re.sub(r'\| BC\.046 \| 车前子 \|[^\n]*','| BC.046 | 车前子 | ✅ 正式完成 7/7；WEBP 1122×1402 | ✅ 已上线 |',asset)
asset=asset.replace('`4.0.0-beta.2`','`4.0.0`')
asset=re.sub(r'- 正式影像已在 GitHub 可读取:[^\n]*','- 正式影像已在 GitHub 可读取：BC.001–046（46/46）',asset)
asset=re.sub(r'- BC\.007–040:[^\n]*','- BC.007–040：✅ 高清图集已正式入库并公开',asset)
asset=re.sub(r'- BC\.046:[^\n]*','- BC.046：✅ 高清图集已正式入库并公开',asset)
asset_path.write_text(asset,encoding='utf-8')

roles=['hero','specimen','detail-01','detail-02','detail-03','detail-04','detail-05']
missing=[]
for h in plan['herbs']:
    for role in roles:
        p=Path('images')/f"{h['id']}-{h['slug']}-{role}-v1.webp"
        if not p.is_file() or p.stat().st_size<20000: missing.append(str(p))
if missing: raise SystemExit('Missing HD files: '+', '.join(missing[:20]))
for n,slug in [(41,'mugua'),(42,'luohanguo'),(43,'sangshen'),(44,'suanzaoren'),(45,'taoren')]:
    for role in roles:
        p=Path('images')/f'bc{n:03d}-{slug}-{role}-v1.avif'
        if not p.is_file() or p.stat().st_size<20000: raise SystemExit(f'Missing {p}')
assert "const VERSION='4.0.0';" in app_path.read_text(encoding='utf-8')
print('HD release transformation and asset validation passed')
