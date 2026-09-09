const VERSION = '3.6.5-VF1';
const LS = 'bencao:rd1';
const WIKI = name => `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(name).replace(/%2F/g,'/')}`;
const FILE_PAGE = name => `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(name).replace(/%20/g,'_')}`;

const HERBS = [
  {
    id:'bc001', no:'BC.001', name:'陈皮', pinyin:'CHÉN PÍ', latinDrug:'Citri Reticulatae Pericarpium', plant:'Citrus reticulata Blanco', part:'干燥成熟果皮', color:'#A87546', aromaColors:['#D79A55','#B8743E','#81705C'],
    hero:'./images/bc001-hero-vf1.webp', origin:'./images/bc001-02-fresh-peel.jpg', material:'./images/bc001-03-dried-material.jpg', plate:'./images/bc001-study-detail-grid-01.jpg?v=ls2', detail1:'./images/bc001-atlas-outer.jpg', detail2:'./images/bc001-atlas-inner.jpg?v=ls2',
    heroPos:'56% 48%',
    today:['你可能已经见过它很多次。','今天，认真看一次。'],
    identity:{lead:'它来自成熟柑橘的果皮。',sub:'从果实到干燥后的材料，变化发生在时间里。',originTitle:'从果实开始。',originText:'剥开的果皮有清楚的内外两面。此时，它仍保留新鲜果实的颜色与水分。',materialTitle:'时间参与了形成。',materialText:'水分逐渐离开，果皮变干、卷曲、变轻；颜色、纹理与触感也随之改变。',note:'时间不是唯一的质量标准。品种、原料、加工与储存同样重要。'},
    evidence:{mark:'药', title:'Citri Reticulatae Pericarpium', lines:['干燥成熟果皮','温 · 辛、苦 · 肺、脾'], note:'传统 / 药典知识体系'},
    atlas:{lead:'干燥之后，果皮成为一种新的材料。',portrait:'先看整体：卷曲、厚薄、内外表面一起构成它的材料感。',structureTitle:'同一片果皮，有两种表面。',structureNote:'深与浅、紧密与疏松，在同一片材料上并置。',d1:['外表面','紧密 · 起伏 · 点状纹理'],d2:['内表面','浅色 · 疏松 · 多孔'],specimen:['卷曲边缘','断面与碎片','材料整体']},
    aroma:['柑橘皮','辛香','干燥 · 微木质'], sensory:'柑橘皮 · 辛香 · 干燥 · 微木质',
    gate:'真实陈皮', action2:'轻轻折动边缘，再闻一次。',
    look:['纹理','卷曲','颜色','厚薄','白色内层','油室','其他'], touch:['干','韧','脆','粗','薄','厚','说不清'], first:['明亮','沉稳','清','柔','说不清'], assoc:['柑橘','青草','花','辛香','其他','说不清'], compare:['更亮','更辛','更深','更柔','变化不明显','说不清'],
    sources:[{label:'BC.001 影像为本草镜现有原型视觉研究素材。',href:''}]
  },
  {
    id:'bc002', no:'BC.002', name:'薄荷', pinyin:'BÒ HÉ', latinDrug:'Menthae Haplocalycis Herba', plant:'Mentha haplocalyx Briq.', part:'干燥地上部分', color:'#71836B', aromaColors:['#75A06F','#84A876','#C7B55C'],
    hero:'./images/bc002-hero-vf1.webp', origin:'./images/bc002-hero-vf1.webp', material:'./images/bc002-detail-01-vu1.jpg', plate:'./images/bc002-atlas-plate-vu1.jpg?v=ls2', detail1:'./images/bc002-detail-02-vu1.jpg?v=ls2', detail2:'./images/bc002-detail-03-vu1.jpg', atlasImages:[['./images/bc002-detail-01-vu1.jpg','植株全貌','植株挺立 · 叶片对生 · 叶色青绿'],['./images/bc002-detail-02-vu1.jpg?v=ls2','叶片表面','叶面皱缩 · 脉络清晰 · 细小腺点'],['./images/bc002-detail-03-vu1.jpg','叶片背面','叶背较浅 · 脉络凸起 · 细柔毛'],['./images/bc002-detail-04-vu1.jpg','茎与叶节','茎呈四棱 · 具细柔毛 · 叶对生于节上'],['./images/bc002-detail-05-vu1.jpg?v=ls2','花序','轮伞花序顶生 · 花小而密']], heroPos:'50% 45%',
    today:['先不要把它等同于“清凉”。','先看一片叶。'],
    identity:{lead:'它来自一株有四棱茎、对生叶的薄荷。',sub:'被采收、干燥以后，叶、茎与花序一起成为药材的地上部分。',originTitle:'叶与茎先构成它。',originText:'叶片有清楚的脉络和锯齿边缘；茎有明显棱角。新鲜时，绿色与水分让结构显得舒展。',materialTitle:'叶、茎与花序共同构成地上部分。',materialText:'当前 Visual Study 先记录鲜活结构与可见特征；正式公开版再补拍同一摄影体系下的干燥药材整体。',note:'揉动会快速改变薄荷的气息，所以第一次闻之前，先不要揉。'},
    evidence:{mark:'药', title:'Menthae Haplocalycis Herba', lines:['干燥地上部分','辛，凉 · 肺、肝'], note:'传统 / 2025《中国药典》体系'},
    atlas:{lead:'薄荷不是一张“绿叶”图片；它是一组叶、茎、边缘与碎片。',portrait:'先看干燥后的整体：轻、散、叶片卷曲，茎段穿在其中。',structureTitle:'叶脉、锯齿与茎棱，是它最容易被看见的结构。',structureNote:'薄、轻和易碎决定了薄荷材料在手里的节奏。',d1:['叶片','皱缩 · 锯齿 · 脉络'],d2:['干燥状态','轻 · 脆 · 易碎'],specimen:['叶片边缘','茎与叶','干燥整体']},
    aroma:['薄荷叶','青绿 · 清透','辛香 · 高扬'], sensory:'薄荷叶 · 青绿 · 清透 · 辛香',
    gate:'来源明确的真实薄荷', action2:'用指腹轻轻揉一下叶片，再闻一次。',
    look:['叶脉','锯齿','叶背','卷曲','茎棱','颜色','其他'], touch:['薄','干','脆','轻','粗','韧','说不清'], first:['清','透','绿','辛香','说不清'], assoc:['青草','茶','香草','辛香','其他','说不清'], compare:['更清','更辛','更绿','更浓','变化不明显','说不清'],
    sources:[{label:'BC002 Hero + Material Atlas：BENCAO Photographic Direction 01 原型 Visual Study；不是植物学鉴定或药材质量证据。正式公开版需以自有、来源明确且可核验材料重拍。',href:''}]
  },
  {
    id:'bc003', no:'BC.003', name:'枸杞', pinyin:'GǑU QǏ', latinDrug:'Lycii Fructus', plant:'Lycium barbarum L.', part:'干燥成熟果实', color:'#A55343', aromaColors:['#C96D58','#B65B4B','#9C7659'],
    hero:'./images/bc003-hero-vf1.webp', origin:'./images/bc003-hero-vf1.webp', material:'./images/bc003-detail-05-vu1.jpg?v=ls2', plate:'./images/bc003-atlas-plate-vu1.jpg?v=ls2', detail1:'./images/bc003-detail-03-vu1.jpg', detail2:'./images/bc003-detail-04-vu1.jpg', atlasImages:[['./images/bc003-detail-01-vu1.jpg','果枝全貌','枝条纤细 · 叶片互生 · 果实椭圆'],['./images/bc003-detail-02-vu1.jpg?v=ls2','叶片表面','叶片狭长 · 叶脉清晰 · 表面具细密纹理'],['./images/bc003-detail-03-vu1.jpg','果实表面','果实椭圆 · 表皮薄而光滑 · 微具纵纹'],['./images/bc003-detail-04-vu1.jpg','果实剖面','果肉柔软多汁 · 内含多枚扁平种子'],['./images/bc003-detail-05-vu1.jpg?v=ls2','干燥材料','干燥后果实皱缩 · 长椭圆形 · 表面纵皱']], heroPos:'50% 48%',
    today:['它常常以一把红色出现。','今天，只看一颗。'],
    identity:{lead:'它来自宁夏枸杞的成熟果实。',sub:'成熟、采收、干燥之后，一颗多汁果实变成皱缩而柔韧的果干材料。',originTitle:'先是一颗成熟果实。',originText:'鲜果呈红色，轮廓饱满。单独看一颗时，果柄端、果尖与细微色差才会出现。',materialTitle:'干燥把水分收进皱纹里。',materialText:'果皮皱缩，体积减小；表面由光滑转为起伏，内部仍可能保留一定柔润感。',note:'枸杞常被当作食物，但本草镜第一版仍不鼓励品尝来源不明的材料。'},
    evidence:{mark:'药', title:'Lycii Fructus', lines:['宁夏枸杞的干燥成熟果实','甘，平 · 肝、肾'], note:'传统 / 2025《中国药典》体系'},
    atlas:{lead:'把“一把红色”拆成单颗之后，形状、皱纹与柔韧度开始有差别。',portrait:'先看一颗，再看一把。材料的差异不是噪声，也是它的一部分。',structureTitle:'表皮皱缩，果肉与种子藏在内部。',structureNote:'这是一种有厚度、有内外层次的干燥果实，不是一张平面红色。',d1:['单颗表面','皱缩 · 长椭圆 · 色差'],d2:['群体状态','大小 · 形状 · 干燥程度不同'],specimen:['单颗轮廓','皱纹密度','一把材料']},
    aroma:['果干','淡甜香','蜜样 · 轻草本'], sensory:'果干 · 淡甜香 · 蜜样 · 轻草本',
    gate:'来源明确的真实枸杞', action2:'用指腹轻压一颗，再闻一次。',
    look:['皱纹','颜色','形状','果柄痕','大小','个体差异','其他'], touch:['柔','韧','干','皱','轻','略黏','说不清'], first:['淡','柔','甜香','熟','说不清'], assoc:['果干','枣','蜂蜜','青草','其他','说不清'], compare:['更甜香','更果香','更深','更柔','变化不明显','说不清'],
    sources:[{label:'BC003 Hero + Material Atlas：BENCAO Photographic Direction 01 原型 Visual Study；不是植物学鉴定或药材质量证据。正式公开版需以自有、来源明确且可核验材料重拍。',href:''}]
  },
  {
    id:'bc004', no:'BC.004', name:'桂花', pinyin:'GUÌ HUĀ', latinDrug:'Osmanthus fragrans (Thunb.) Lour.', plant:'Osmanthus fragrans (Thunb.) Lour.', part:'花（本草镜体验材料：来源明确的干燥桂花）', color:'#C49A4C', aromaColors:['#D6BA68','#C89E49','#A9845C'],
    hero:'./images/bc004-hero-vf1.webp', origin:'./images/bc004-hero-vf1.webp', material:'./images/bc004-detail-05-vu1.jpg?v=ls2', plate:'./images/bc004-atlas-plate-vu1.jpg?v=ls2', detail1:'./images/bc004-detail-02-vu1.jpg?v=ls2', detail2:'./images/bc004-detail-03-vu1.jpg', atlasImages:[['./images/bc004-detail-01-vu1.jpg','花枝全貌','花簇生于叶腋 · 花叶相映 · 枝条舒展'],['./images/bc004-detail-02-vu1.jpg?v=ls2','花簇','小花密集成簇 · 花瓣肉质 · 淡黄色'],['./images/bc004-detail-03-vu1.jpg','单花结构','花冠四瓣 · 花瓣厚实 · 中央具短花蕊'],['./images/bc004-detail-04-vu1.jpg','叶片与叶脉','叶片革质 · 表面光滑 · 叶脉清晰'],['./images/bc004-detail-05-vu1.jpg?v=ls2','干燥花材','干燥后呈金黄色 · 花形完整或微卷']], heroPos:'50% 52%',
    today:['它很小，香气却常常先于形状被记住。','今天，先看见它。'],
    identity:{lead:'它来自木犀叶腋里成簇开放的小花。',sub:'花朵只有很小的尺度。干燥之后，颜色、卷曲和碎裂让它变成另一种轻盈材料。',originTitle:'先从叶腋里的花簇开始。',originText:'木犀的花聚在叶腋，花冠可呈黄白、淡黄、黄色或橙红。完整花朵本身很小。',materialTitle:'干燥会放大“轻”和“碎”。',materialText:'花冠收缩、颜色加深，花梗与碎瓣混在一起。少量材料就形成很高的表面积。',note:'桂花在本草镜中按植物与感官材料呈现，不把它标成现行《中国药典》标准药材。'},
    evidence:{mark:'', title:'Osmanthus fragrans (Thunb.) Lour.', lines:['木犀科 · 木犀属','花簇生叶腋 · 花极芳香'], note:'植物学身份记录；这里不使用“药”标签'},
    atlas:{lead:'桂花的材料性格来自尺度：一朵很小，一撮很多。',portrait:'先看一撮。再靠近，花冠、花梗和碎瓣才从“金黄色”里分离出来。',structureTitle:'小尺度、薄花瓣与聚集状态，一起决定它的材料感。',structureNote:'这里不把“香”当成视觉答案；先只记录形状、颜色和碎裂。',d1:['干燥花朵','小 · 轻 · 卷曲'],d2:['聚集状态','花冠 · 花梗 · 碎瓣'],specimen:['单朵尺度','花簇关系','干燥整体']},
    aroma:['花香','杏桃样 · 蜜甜','干花 · 柔和'], sensory:'花香 · 杏桃样 · 蜜甜 · 干花',
    gate:'来源明确的真实干燥桂花', action2:'轻轻拨动几朵，再闻一次。',
    look:['花瓣','颜色','花梗','大小','聚集','碎片','其他'], touch:['轻','干','脆','薄','碎','柔','说不清'], first:['明亮','轻','甜香','浓','说不清'], assoc:['花','杏桃','蜂蜜','熟果','其他','说不清'], compare:['更甜香','更果香','更深','更柔','变化不明显','说不清'],
    sources:[{label:'BC004 Hero + Material Atlas：BENCAO Photographic Direction 01 原型 Visual Study；不是植物学鉴定或药材质量证据。正式公开版需以自有、来源明确且可核验材料重拍。',href:''}]
  },
  {
    id:'bc005', no:'BC.005', name:'菊花', pinyin:'JÚ HUĀ', latinDrug:'Chrysanthemi Flos', plant:'Chrysanthemum morifolium Ramat.', part:'干燥头状花序', color:'#9A8B60', aromaColors:['#D3C48E','#B7A66D','#95836B'],
    hero:'./images/bc005-hero-vf1.webp', origin:'./images/bc005-hero-vf1.webp', material:'./images/bc005-detail-05-vu1.jpg?v=ls2', plate:'./images/bc005-atlas-plate-vu1.jpg?v=ls2', detail1:'./images/bc005-detail-02-vu1.jpg?v=ls2', detail2:'./images/bc005-detail-03-vu1.jpg', atlasImages:[['./images/bc005-detail-01-vu1.jpg','花枝全貌','植株挺立 · 花枝分枝 · 花朵簇生'],['./images/bc005-detail-02-vu1.jpg?v=ls2','花序中心','管状花密集 · 球状排列 · 黄色'],['./images/bc005-detail-03-vu1.jpg','舌状花','舌状花呈长条形 · 边缘微卷 · 质地薄柔'],['./images/bc005-detail-04-vu1.jpg','花叶与花蕾','叶片羽状分裂 · 花蕾外层苞片紧密包裹'],['./images/bc005-detail-05-vu1.jpg?v=ls2','干燥花材','干燥后花形完整 · 瓣片皱缩卷曲 · 质地轻脆']], heroPos:'50% 46%',
    today:['“一朵菊花”其实有很多层。','今天，从花心往外看。'],
    identity:{lead:'它来自菊的头状花序。',sub:'盛开时采收，经过不同加工方式后，花序整体成为干燥材料。',originTitle:'它不是单一的一片花瓣。',originText:'外围与中央的花在同一个花序里形成层次；颜色、形态与排列让整朵花有明确中心。',materialTitle:'干燥保留了花序，也改变了支撑。',materialText:'花瓣折缩、花心变得密实或松散，整体变轻、变脆；不同产地和加工方式也会带来外观差异。',note:'菊花药材按产地与加工方法可分多种类型；原型页面不把某一张视觉研究图当作全部菊花。'},
    evidence:{mark:'药', title:'Chrysanthemi Flos', lines:['菊的干燥头状花序','甘、苦，微寒 · 肺、肝'], note:'传统 / 2025《中国药典》体系'},
    atlas:{lead:'先看“整朵”，再把注意力移到花心、花瓣与基部。',portrait:'干燥后的花序仍然有中心和方向，但支撑变轻，花瓣更容易折缩。',structureTitle:'层次比颜色更重要。',structureNote:'花心的密度、外围花瓣的卷曲和基部结构，让一朵干菊花有不同触感区域。',d1:['花序层次','中心 · 外围 · 方向'],d2:['干燥状态','轻 · 松 · 易脆'],specimen:['花心','外围花瓣','整朵花序']},
    aroma:['干花','青草 · 草本','柔和 · 微甘香'], sensory:'干花 · 青草 · 草本 · 柔和',
    gate:'来源明确的真实菊花', action2:'用指尖轻轻拨开花心，再闻一次。',
    look:['花心','花瓣层次','颜色','卷曲','基部','完整度','其他'], touch:['轻','柔','脆','干','松','薄','说不清'], first:['清','淡','柔','草本','说不清'], assoc:['干花','青草','茶','晒过的植物','其他','说不清'], compare:['更草本','更清','更深','更柔','变化不明显','说不清'],
    sources:[{label:'BC005 Hero + Material Atlas：BENCAO Photographic Direction 01 原型 Visual Study；不是植物学鉴定或药材质量证据。正式公开版需以自有、来源明确且可核验材料重拍。',href:''}]
  },
  {
    id:'bc006', no:'BC.006', name:'紫苏', pinyin:'ZǏ SŪ', latinDrug:'Perillae Folium', plant:'Perilla frutescens (L.) Britt.', part:'干燥叶（或带嫩枝）', color:'#74586C', aromaColors:['#8A687C','#745768','#87735C'],
    hero:'./images/bc006-hero-vf1.webp', origin:'./images/bc006-hero-vf1.webp', material:'./images/bc006-detail-05-vu1.jpg?v=ls2', plate:'./images/bc006-atlas-plate-vu1.jpg?v=ls2', detail1:'./images/bc006-detail-02-vu1.jpg?v=ls2', detail2:'./images/bc006-detail-03-vu1.jpg', atlasImages:[['./images/bc006-detail-01-vu1.jpg','叶枝全貌','植株挺立 · 叶片对生 · 叶形宽卵 · 叶缘锯齿'],['./images/bc006-detail-02-vu1.jpg?v=ls2','叶片表面','叶面紫红 · 脉络清晰 · 具细小腺点'],['./images/bc006-detail-03-vu1.jpg','叶片背面','叶背色较浅 · 脉络隆起 · 密被短柔毛'],['./images/bc006-detail-04-vu1.jpg','茎与叶节','茎呈紫绿色 · 具细柔毛 · 叶对生于节上'],['./images/bc006-detail-05-vu1.jpg?v=ls2','干燥叶材','干燥后叶片卷曲 · 质地轻脆 · 色泽紫褐']], heroPos:'50% 45%',
    today:['先别只看它的紫。','沿着叶脉走一次。'],
    identity:{lead:'它来自紫苏的叶，或带嫩枝的叶。',sub:'鲜叶有清楚的锯齿、叶脉和上下表面；干燥后会皱缩卷曲，颜色与脆度一起改变。',originTitle:'一片叶先有方向。',originText:'叶尖、叶基、圆锯齿与中脉共同建立轮廓；不同植株可呈紫色，或上表面偏绿、下表面偏紫。',materialTitle:'干燥把一片展开的叶变成卷曲薄片。',materialText:'叶片失水后容易皱缩、破碎，边缘和叶脉仍是辨认材料状态的重要视觉线索。',note:'当前紫苏 Material Atlas 使用叶片结构视觉研究图作为摄影占位；正式发布前应补拍可核验的干燥紫苏叶材料。'},
    evidence:{mark:'药', title:'Perillae Folium', lines:['干燥叶（或带嫩枝）','辛，温 · 肺、脾'], note:'传统 / 2025《中国药典》体系'},
    atlas:{lead:'紫苏的材料感来自一张薄叶上的很多方向：叶脉、锯齿、毛与卷曲。',portrait:'先看整片叶的轮廓。干燥材料的正式摄影位在发布前补拍，这里只作为叶片结构参照。',structureTitle:'上表面与下表面，不只是颜色不同。',structureNote:'叶脉凹凸、疏毛与边缘锯齿会改变指尖沿着叶片移动时的感觉。',d1:['叶背结构','叶脉 · 疏毛 · 凹凸'],d2:['叶片轮廓','锯齿 · 叶尖 · 颜色'],specimen:['叶脉','锯齿边缘','整片轮廓']},
    aroma:['紫苏叶','青绿 · 辛香','草本 · 微厚'], sensory:'紫苏叶 · 青绿 · 辛香 · 草本',
    gate:'来源明确的真实紫苏叶', action2:'轻轻折动叶缘，再闻一次。',
    look:['叶脉','锯齿','叶背','颜色','卷曲','叶柄','其他'], touch:['薄','脆','粗','干','轻','略绒','说不清'], first:['清','辛香','绿','厚','说不清'], assoc:['青草','香草','辛香','叶片','其他','说不清'], compare:['更辛','更草本','更深','更清','变化不明显','说不清'],
    sources:[{label:'BC006 Hero + Material Atlas：BENCAO Photographic Direction 01 原型 Visual Study；不是植物学鉴定或药材质量证据。正式公开版需以自有、来源明确且可核验材料重拍。',href:''}]
  }
];

const $ = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>[...root.querySelectorAll(s)];
const herbGrid = $('#herbGrid');
const catalogueView = $('#catalogueView');
const detailView = $('#detailView');
const blackout = $('#blackout');
let activeHerb = null;
let encState = null;
let advanceTimer = null;
let encStepStartedAt = null;

function pad2(n){ return String(n).padStart(2,'0'); }
function countKey(id){ return `${LS}:${id}:count`; }
function getCount(id){ return Number(localStorage.getItem(countKey(id)) || 0); }
function setCount(id,n){ localStorage.setItem(countKey(id),String(n)); }
function esc(s=''){ return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function img(src,alt,extra=''){ return `<img src="${src}" alt="${esc(alt)}" loading="lazy" decoding="async" ${extra} onerror="this.classList.add('image-failed')">`; }
function rgbChannels(hex){
  const v=String(hex||'').replace('#','').trim();
  const full=v.length===3?v.split('').map(x=>x+x).join(''):v;
  if(!/^[0-9a-fA-F]{6}$/.test(full)) return [120,120,120];
  return [parseInt(full.slice(0,2),16),parseInt(full.slice(2,4),16),parseInt(full.slice(4,6),16)];
}
function rgba(hex,a){ const [r,g,b]=rgbChannels(hex); return `rgba(${r},${g},${b},${a})`; }
function aromaFieldStyle(colors){
  const [opening,middle,drydown]=colors;
  return [
    'background-color:#e7dfd2',
    `background-image:radial-gradient(ellipse 42% 38% at 23% 37%,${rgba(opening,.72)} 0%,${rgba(opening,.50)} 34%,${rgba(opening,.25)} 58%,${rgba(opening,0)} 79%),radial-gradient(ellipse 39% 35% at 54% 55%,${rgba(middle,.68)} 0%,${rgba(middle,.46)} 35%,${rgba(middle,.23)} 59%,${rgba(middle,0)} 80%),radial-gradient(ellipse 37% 33% at 79% 69%,${rgba(drydown,.64)} 0%,${rgba(drydown,.43)} 36%,${rgba(drydown,.21)} 60%,${rgba(drydown,0)} 81%)`,
    'background-repeat:no-repeat'
  ].join(';');
}

function track(event, herbId=activeHerb?.id, data={}){
  try{
    const key=`${LS}:events`;
    const arr=JSON.parse(localStorage.getItem(key)||'[]');
    arr.push({event,herb:herbId||null,at:new Date().toISOString(),...data});
    localStorage.setItem(key,JSON.stringify(arr.slice(-250)));
  }catch{}
}

function renderCatalogue(){
  herbGrid.innerHTML = HERBS.map(h=>{
    const c=getCount(h.id);
    return `<button class="herb-card" type="button" data-herb="${h.id}" style="--herb-color:${h.color}">
      <div class="herb-card-figure">${img(h.hero,`${h.name}原植物视觉研究图`,`loading="eager" fetchpriority="high" style="object-position:${h.heroPos||'50% 50%'}"`)}</div>
      <div class="herb-card-body">
        <div class="herb-card-title"><span class="herb-card-id">${h.no}</span><h3>${h.name}</h3><span class="herb-card-pinyin">${h.pinyin}</span></div>
        <div class="herb-card-latin">${h.latinDrug}</div>
        <div class="herb-card-link">进入探索 → ${c?`<span class="herb-card-seen">已遇见 ${pad2(c)}</span>`:''}</div>
      </div>
    </button>`;
  }).join('');
  $$('.herb-card',herbGrid).forEach(b=>b.addEventListener('click',()=>openHerb(b.dataset.herb)));
  const met=HERBS.filter(h=>getCount(h.id)>0).length;
  $('#catalogueCount').textContent=`已遇见 ${met} / ${HERBS.length}`;
}

function renderDetail(h){
  const idx=HERBS.findIndex(x=>x.id===h.id);
  const next=HERBS[(idx+1)%HERBS.length];
  detailView.style.setProperty('--herb-color',h.color);
  const aromaColors=h.aromaColors || [h.color,h.color,h.color];
  detailView.innerHTML = `
    <div class="detail-rail"><button type="button" data-go-catalogue>← 本草目录</button><button type="button" data-jump="today">TODAY</button><button type="button" data-jump="identity">IDENTITY</button><button type="button" data-jump="atlas">ATLAS</button><button type="button" data-jump="aroma">AROMA</button></div>
    <section class="plate today" id="today">
      <header class="folio"><span>BENCAO / ${VERSION}</span><span>${h.no} · TODAY</span></header>
      <div class="today-copy"><p class="eyebrow">${h.plant.toUpperCase()} / SPECIMEN ${h.no.slice(-3)}</p><h1>${h.name}</h1><p class="latin">${h.latinDrug}</p>
        <div class="today-statement"><p>${h.today[0]}</p><p>${h.today[1]}</p><button type="button" class="text-cta" data-jump="identity">靠近一点 →</button></div>
      </div>
      <figure class="today-figure">${img(h.hero,`${h.name}原植物视觉研究图`,`loading="eager" fetchpriority="high" style="object-position:${h.heroPos||'50% 50%'}"`)}<figcaption class="image-caption"><span>BOTANICAL IDENTITY / 原植物</span><span>${h.no}</span></figcaption></figure>
    </section>

    <section class="plate identity" id="identity">
      <header class="folio"><span>${h.no} / IDENTITY</span><span>ORIGIN → MATERIAL</span></header>
      <div class="identity-head"><p class="eyebrow">IDENTITY / SPECIMEN READING</p><h2>${h.identity.lead}</h2><p>${h.identity.sub}</p></div>
      <div class="identity-grid">
        <article class="identity-chapter"><div class="chapter-meta">01 / ORIGIN · 来源</div><figure>${img(h.origin,`${h.name}原植物或新鲜状态视觉研究图`)}</figure><h3>${h.identity.originTitle}</h3><p>${h.identity.originText}</p></article>
        <article class="identity-chapter"><div class="chapter-meta">02 / MATERIAL · 材料</div><figure>${img(h.material,`${h.name}材料视觉研究图`)}</figure><h3>${h.identity.materialTitle}</h3><p>${h.identity.materialText}</p></article>
      </div>
      <p class="atlas-disclaimer">${h.identity.note}</p>
      <aside class="evidence-note ${h.evidence.mark?'':'no-mark'}">${h.evidence.mark?`<span class="evidence-mark">${h.evidence.mark}</span>`:''}<div><p><strong>${h.evidence.title}</strong></p>${h.evidence.lines.map(x=>`<p>${x}</p>`).join('')}<small>${h.evidence.note}</small></div></aside>
      <button type="button" class="text-cta" data-jump="atlas">进入材料图谱 →</button>
    </section>

    <section class="plate atlas" id="atlas">
      <header class="folio"><span>${h.no} / MATERIAL ATLAS</span><span>MATERIAL PORTRAIT → STRUCTURE → PLATE</span></header>
      <div class="atlas-head"><p class="eyebrow">VISUAL STUDY / 图像研究</p><h2>${h.name} · 材料图谱</h2><p>${h.atlas.lead}</p></div>
      <div class="atlas-portrait"><figure>${img(h.material,`${h.name}材料整体视觉研究图`)}</figure><div class="atlas-portrait-copy"><p class="eyebrow">01 / MATERIAL PORTRAIT</p><h3>先看整体。</h3><p>${h.atlas.portrait}</p></div></div>
      <div class="atlas-subhead"><div><p class="eyebrow">02 / DEFINING STRUCTURE</p><h3>${h.atlas.structureTitle}</h3></div><p>${h.atlas.structureNote}</p></div>
      ${h.atlasImages ? `<div class="atlas-five-grid">${h.atlasImages.map((item,i)=>`<figure class="atlas-five-cell cell-${i+1}">${img(item[0],`${h.name}${item[1]}视觉研究图`)}<figcaption><strong>${String(i+1).padStart(2,'0')} ${item[1]}</strong><small>${item[2]}</small></figcaption></figure>`).join('')}</div>` : `<div class="atlas-pair"><figure>${img(h.detail1,`${h.name}${h.atlas.d1[0]}视觉研究图`)}<figcaption><strong>01 ${h.atlas.d1[0]}</strong><small>${h.atlas.d1[1]}</small></figcaption></figure><figure>${img(h.detail2,`${h.name}${h.atlas.d2[0]}视觉研究图`)}<figcaption><strong>02 ${h.atlas.d2[0]}</strong><small>${h.atlas.d2[1]}</small></figcaption></figure></div>`}
      <p class="atlas-observation">${h.atlas.structureNote}</p>
      <div class="atlas-subhead"><div><p class="eyebrow">03 / SPECIMEN PLATE</p><h3>${h.name} · 图像档案</h3></div><p>这些图像可以帮助你看见。真实的材料，仍然比图像多。</p></div>
      ${h.plate ? `<figure class="atlas-plate-figure">${img(h.plate,`${h.name} · 标本盘图像档案`)}<figcaption><span>SPECIMEN PLATE / 标本盘</span><strong>${h.no} ${h.name}</strong></figcaption></figure>` : ''}
      ${h.atlasImages ? `<div class="atlas-plate-index">${h.atlasImages.map((item,i)=>`<span>${String.fromCharCode(65+i)} / ${item[1]}</span>`).join('')}</div>` : `<div class="specimen-grid"><figure class="specimen-cell">${img(h.detail1,`${h.name}${h.atlas.specimen[0]}`)}<figcaption>A / ${h.atlas.specimen[0]}</figcaption></figure><figure class="specimen-cell">${img(h.detail2,`${h.name}${h.atlas.specimen[1]}`)}<figcaption>B / ${h.atlas.specimen[1]}</figcaption></figure><figure class="specimen-cell">${img(h.material,`${h.name}${h.atlas.specimen[2]}`)}<figcaption>C / ${h.atlas.specimen[2]}</figcaption></figure></div>`}
      <p class="atlas-disclaimer">原型影像只用于建立观察路径，不作为显微、鉴定或质量证明。正式公开版应使用自有、来源明确且可核验的材料摄影。</p>
      <button type="button" class="text-cta" data-jump="aroma">从材料，到气息 →</button>
    </section>

    <section class="plate aroma" id="aroma">
      <header class="folio"><span>${h.no} / AROMA FIELD</span><span>EDITORIAL SENSORY MAP</span></header>
      <div class="aroma-title"><p class="eyebrow">气发生在空间里</p><h2>纸上留下一次气息。</h2></div>
      <div class="aroma-field" style="${aromaFieldStyle(aromaColors)}"><div class="aroma-label a1"><span>OPENING / 初息</span><strong>${h.aroma[0]}</strong></div><div class="aroma-label a2"><span>MIDDLE / 中息</span><strong>${h.aroma[1]}</strong></div><div class="aroma-label a3"><span>DRYDOWN / 余息</span><strong>${h.aroma[2]}</strong></div><div class="aroma-axis"><span>BRIGHT</span><i></i><span>DEEP</span></div></div>
      <div class="disclaimer"><p>这不是气味本身。</p><p>这是一张感官地图。</p><p class="return">真正的气，要回到真实${h.name}里。</p></div>
      <button type="button" class="text-cta" data-open-gate>开始真实相遇 →</button>
    </section>

    <section class="gate" id="gate" hidden><div class="gate-inner"><p class="eyebrow">SCREEN → MATERIAL</p><h2>屏幕到这里先退后一步。</h2><p>Encounter 只记录你与真实材料发生的感受。第一版不鼓励品尝来源不明的材料；未知来源只做看 / 触 / 闻。</p><div class="gate-actions"><button class="gate-primary" type="button" data-enter-encounter>我手边有${h.gate} →</button><button class="gate-secondary" type="button" data-go-catalogue>暂时没有，回到本草目录</button></div></div></section>

    <section class="encounter" id="encounter" hidden>
      <header class="folio folio-dark"><span>${h.no} / ENCOUNTER</span><span>${h.name}</span></header>
      <div class="encounter-stage-wrap" id="encounterStages"></div>
      <div class="encounter-bottom"><button class="encounter-back" type="button" data-enc-back hidden>← 返回上一步</button><span class="encounter-progress" id="encounterProgress">01 / 08</span></div>
    </section>

    <section class="result" id="result" hidden><div class="result-inner"><p class="eyebrow">你的${h.name}</p><div class="result-id" id="resultId">${h.no} / ENCOUNTER 01</div><blockquote class="raw-note" id="resultNote"></blockquote><div class="user-tags" id="resultTags"></div><div class="editorial"><span class="evidence-mark">编</span><div><h3>本草镜档案</h3><p>${h.sensory}</p></div></div><p class="result-principle">它们不需要完全一样。感官是材料与个人共同发生的。</p></div></section>

    <section class="spectrum-block" id="personalSpectrum" hidden><div class="spectrum-inner"><p class="eyebrow">ARCHIVE / PERSONAL</p><h2>我的本草谱</h2><div class="facts"><div class="fact"><div class="fact-label">SPECIMEN</div><div class="fact-value">${h.no} ${h.name}</div></div><div class="fact"><div class="fact-label">ENCOUNTERS</div><div class="fact-value">已遇见 <span data-local-count>00</span></div></div><div class="fact"><div class="fact-label">REAL AROMA</div><div class="fact-value">真实闻过 <span data-local-smell>00</span></div></div></div><p>同一味本草，在不同时间里，可以留下不同记录。</p><button class="repeat" type="button" data-repeat>再遇一次 →</button><button class="next-herb" type="button" data-next-herb="${next.id}">继续 ${next.no} ${next.name} →</button></div></section>

    <footer class="credit-strip"><strong>VISUAL STUDY SOURCES / 原型影像来源</strong><br>${h.sources.map(s=>s.href?`<a href="${s.href}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join('<br>')}</footer>
  `;

  bindDetail(h);
}

function openHerb(id,{replaceHash=false}={}){
  const h=HERBS.find(x=>x.id===id) || HERBS[0];
  activeHerb=h;
  renderDetail(h);
  catalogueView.hidden=true; detailView.hidden=false;
  document.title=`本草镜 BENCAO｜${h.no} ${h.name}`;
  if(replaceHash) history.replaceState(null,'',`#herb=${h.id}`); else history.pushState(null,'',`#herb=${h.id}`);
  window.scrollTo({top:0,behavior:'auto'});
  track('herb_open',h.id);
}

function showCatalogue({replaceHash=false}={}){
  activeHerb=null; detailView.hidden=true; catalogueView.hidden=false; renderCatalogue();
  document.title='本草镜 BENCAO MIRROR｜六味本草';
  if(replaceHash) history.replaceState(null,'','#catalogue'); else history.pushState(null,'','#catalogue');
  window.scrollTo({top:0,behavior:'auto'}); track('catalogue_view',null);
}

function bindDetail(h){
  $$('[data-go-catalogue]',detailView).forEach(b=>b.addEventListener('click',()=>showCatalogue()));
  $$('[data-jump]',detailView).forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.jump)?.scrollIntoView({behavior:'smooth'})));
  $('[data-open-gate]',detailView)?.addEventListener('click',()=>{ const gate=$('#gate'); gate.hidden=false; gate.scrollIntoView({behavior:'smooth'}); track('encounter_gate_view',h.id); });
  $('[data-enter-encounter]',detailView)?.addEventListener('click',()=>startEncounter(h));
  $('[data-repeat]',detailView)?.addEventListener('click',()=>startEncounter(h,true));
  $('[data-next-herb]',detailView)?.addEventListener('click',e=>openHerb(e.currentTarget.dataset.nextHerb));
}

function encounterSteps(h){
  return [
    {id:'look',label:'01 / LOOK · 看',title:'先不要闻。只看。',prompt:'选一个你最先注意到的地方。',choices:h.look},
    {id:'touch',label:'02 / TOUCH · 触',title:'拿起来。指尖更接近哪一种？',prompt:'只记录现在的触感。',choices:h.touch},
    {id:'smell1confirm',label:'03 / FIRST SMELL · 第一次闻',title:'靠近一点。闻一次。',prompt:'先不要找答案。只留意最先出现的感觉。',confirm:'我已经闻过了'},
    {id:'first',label:'03 / FIRST IMPRESSION · 初感',title:'第一感觉更接近——',prompt:'这里记录的是这一次的感官语言，不是传统药性。',choices:h.first},
    {id:'assoc',label:'03 / ASSOCIATION · 联想',title:'它让你想到什么？',prompt:'不是标准答案，只记这一次联想。',choices:h.assoc},
    {id:'smell2confirm',label:'04 / SECOND SMELL · 第二次闻',title:h.action2,prompt:'让材料发生一点变化，再靠近。',confirm:'我已经闻过第二次了'},
    {id:'compare',label:'04 / COMPARE · 比较',title:'和第一次相比——',prompt:'比较，比判断更重要。',choices:h.compare},
    {id:'note',label:'05 / RAW NOTE · 你的话',title:'最后，留一句自己的话。',prompt:'像什么？让你想到什么？',note:true}
  ];
}

function startEncounter(h,repeat=false){
  clearTimeout(advanceTimer);
  encState={index:0,values:{}};
  encStepStartedAt=performance.now();
  const enc=$('#encounter'); enc.hidden=false; $('#result').hidden=true; $('#personalSpectrum').hidden=true;
  buildEncounter(h);
  const transition=()=>{ enc.scrollIntoView({behavior:'auto',block:'start'}); blackout.classList.remove('on'); };
  if(repeat){ enc.scrollIntoView({behavior:'smooth'}); track('encounter_repeat_start',h.id); return; }
  blackout.classList.add('on'); setTimeout(transition,720); track('encounter_start',h.id);
}

function buildEncounter(h){
  const steps=encounterSteps(h); const holder=$('#encounterStages');
  holder.innerHTML=steps.map((s,i)=>`<div class="encounter-stage ${i===0?'active':''}" data-enc-step="${i}"><div class="encounter-no">${s.label}</div><h2>${s.title}</h2><p>${s.prompt}</p>${s.choices?`<div class="choices">${s.choices.map(c=>`<button class="choice" type="button" data-choice="${esc(c)}">${c}</button>`).join('')}</div>`:''}${s.confirm?`<button class="confirm-action" type="button" data-confirm>${s.confirm}</button>`:''}${s.note?`<textarea class="encounter-note" maxlength="160" placeholder="写下你自己的句子……"></textarea><br><button class="encounter-submit" type="button" data-submit>留下这次相遇 →</button>`:''}</div>`).join('');
  $$('.choice',holder).forEach(btn=>btn.addEventListener('click',()=>{
    const stage=btn.closest('.encounter-stage'); const i=Number(stage.dataset.encStep); const s=steps[i];
    $$('.choice',stage).forEach(x=>x.classList.remove('selected')); btn.classList.add('selected'); encState.values[s.id]=btn.dataset.choice; track(`${s.id}_select`,h.id,{value:btn.dataset.choice});
    advanceTimer=setTimeout(()=>showEncStep(i+1,steps.length),180);
  }));
  $$('[data-confirm]',holder).forEach(btn=>btn.addEventListener('click',()=>{const stage=btn.closest('.encounter-stage');const i=Number(stage.dataset.encStep);const s=steps[i];encState.values[s.id]=true;track(s.id,h.id);showEncStep(i+1,steps.length);}));
  $('[data-submit]',holder)?.addEventListener('click',()=>{const raw=$('.encounter-note',holder).value;encState.values.raw_note=raw;track('raw_note_submit',h.id,{has_note:!!raw.trim(),note_length:raw.length});finishEncounter(h);});
  $('[data-enc-back]',detailView).onclick=()=>showEncStep(Math.max(0,encState.index-1),steps.length);
  updateEncUI(steps.length);
}

function showEncStep(i,total){
  clearTimeout(advanceTimer);
  if(encStepStartedAt!==null && encState){ track('encounter_step_duration',activeHerb?.id,{step:encState.index+1,duration_ms:Math.round(performance.now()-encStepStartedAt)}); }
  encState.index=Math.max(0,Math.min(i,total-1));
  encStepStartedAt=performance.now();
  $$('.encounter-stage',detailView).forEach((s,n)=>s.classList.toggle('active',n===encState.index)); updateEncUI(total);
}
function updateEncUI(total){ $('#encounterProgress').textContent=`${pad2(encState.index+1)} / ${pad2(total)}`; $('[data-enc-back]',detailView).hidden=encState.index===0; }

function finishEncounter(h){
  if(encStepStartedAt!==null && encState){ track('encounter_step_duration',h.id,{step:encState.index+1,duration_ms:Math.round(performance.now()-encStepStartedAt)}); encStepStartedAt=null; }
  const n=getCount(h.id)+1; setCount(h.id,n);
  const vals=encState.values; localStorage.setItem(`${LS}:${h.id}:last`,JSON.stringify(vals));
  $('#resultId').textContent=`${h.no} / ENCOUNTER ${pad2(n)}`;
  const note=$('#resultNote'); note.textContent=vals.raw_note.trim()?vals.raw_note:'这一次，你没有留下文字。'; note.classList.toggle('empty',!vals.raw_note.trim());
  const tags=[vals.first,vals.assoc,vals.compare].filter(Boolean); $('#resultTags').innerHTML=tags.map(t=>`<span class="user-tag">${esc(t)}</span>`).join('');
  $('[data-local-count]').textContent=pad2(n); $('[data-local-smell]').textContent=pad2(n);
  $('#result').hidden=false; $('#personalSpectrum').hidden=false; $('#result').scrollIntoView({behavior:'smooth'}); track('result_view',h.id,{encounter_no:n}); renderSpectrum(); renderCatalogue();
}

function renderSpectrum(){
  $('#spectrumGrid').innerHTML=HERBS.map(h=>{const c=getCount(h.id);return `<div class="spectrum-row"><span class="spectrum-row-id">${h.no}</span><strong>${h.name}</strong><span>${c?`已遇见 ${pad2(c)}`:'尚未相遇'}</span></div>`}).join('');
}

function openDialog(id){ const d=$(id); renderSpectrum(); if(typeof d.showModal==='function') d.showModal(); else d.setAttribute('open',''); }
$$('[data-open-spectrum]').forEach(b=>b.addEventListener('click',()=>openDialog('#spectrumDialog')));
$$('[data-open-about]').forEach(b=>b.addEventListener('click',()=>openDialog('#aboutDialog')));
$$('[data-dialog-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('[data-go-catalogue]',document).forEach(b=>{ if(!detailView.contains(b)) b.addEventListener('click',()=>showCatalogue()); });
window.addEventListener('pagehide',()=>{ track('session_exit',activeHerb?.id,{view:activeHerb?'detail':'catalogue',encounter_step:encState?.index!==undefined?encState.index+1:null}); });
window.addEventListener('popstate',routeFromHash);
function routeFromHash(){ const m=location.hash.match(/^#herb=(bc00[1-6])$/); if(m) openHerb(m[1],{replaceHash:true}); else showCatalogue({replaceHash:true}); }

renderCatalogue(); renderSpectrum();
const initial=location.hash.match(/^#herb=(bc00[1-6])$/); if(initial) openHerb(initial[1],{replaceHash:true}); else history.replaceState(null,'','#catalogue');
