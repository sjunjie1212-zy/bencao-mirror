(() => {
  const existingSpecimens = {
    bc002:'./images/bc002-atlas-plate-vu1.jpg',
    bc003:'./images/bc003-atlas-plate-vu1.jpg',
    bc004:'./images/bc004-atlas-plate-vu1.jpg',
    bc005:'./images/bc005-atlas-plate-vu1.jpg',
    bc006:'./images/bc006-atlas-plate-vu1.jpg'
  };
  Object.entries(existingSpecimens).forEach(([id, specimen]) => {
    const h = HERBS.find(x => x.id === id);
    if (!h || !Array.isArray(h.images) || h.images.includes(specimen)) return;
    h.images = [h.images[0], specimen, ...h.images.slice(1)];
  });

  const imported = [
    ['bc007','jinyinhua','Lonicera japonica'],
    ['bc008','shanzha','Crataegus pinnatifida'],
    ['bc009','gancao','Glycyrrhiza uralensis'],
    ['bc010','danggui','Angelica sinensis'],
    ['bc011','huangqi','Astragalus mongholicus'],
    ['bc012','fuling','Wolfiporia cocos'],
    ['bc013','yiyiren','Coix lacryma-jobi var. ma-yuen'],
    ['bc014','lianzi','Nelumbo nucifera'],
    ['bc015','juemingzi','Senna obtusifolia / Senna tora'],
    ['bc016','dazao','Ziziphus jujuba'],
    ['bc017','renshen','Panax ginseng'],
    ['bc018','danshen','Salvia miltiorrhiza'],
    ['bc019','lianqiao','Forsythia suspensa'],
    ['bc020','maidong','Ophiopogon japonicus'],
    ['bc021','wuweizi','Schisandra chinensis'],
    ['bc022','baihe','Lilium brownii / Lilium lancifolium'],
    ['bc023','rougui','Cinnamomum cassia'],
    ['bc024','dingxiang','Syzygium aromaticum'],
    ['bc025','sharen','Wurfbainia villosa / Amomum villosum'],
    ['bc026','houpo','Magnolia officinalis'],
    ['bc027','huanglian','Coptis chinensis'],
    ['bc028','huangqin','Scutellaria baicalensis'],
    ['bc029','zexie','Alisma orientale'],
    ['bc030','banxia','Pinellia ternata'],
    ['bc031','tianma','Gastrodia elata'],
    ['bc032','niuxi','Achyranthes bidentata'],
    ['bc033','duzhong','Eucommia ulmoides'],
    ['bc034','muxiang','Aucklandia costus / Saussurea costus'],
    ['bc035','jixueteng','Spatholobus suberectus'],
    ['bc036','sumu','Biancaea sappan / Caesalpinia sappan'],
    ['bc037','zhizi','Gardenia jasminoides'],
    ['bc038','zhishi','Citrus aurantium'],
    ['bc039','foshou','Citrus medica var. sarcodactylis'],
    ['bc040','wumei','Prunus mume'],
    ['bc046','cheqianzi','Plantago asiatica / Plantago depressa']
  ];
  const roles = ['hero','specimen','detail-01','detail-02','detail-03','detail-04','detail-05'];
  imported.forEach(([id, slug, plant]) => {
    const h = HERBS.find(x => x.id === id);
    if (!h) return;
    h.assetStatus = 'formal';
    h.plant = plant;
    h.hero = `./images/${id}-${slug}-hero-v1.webp`;
    h.images = roles.map(role => `./images/${id}-${slug}-${role}-v1.webp`);
    h.intro = `${h.name}的整体形态、药用部位与局部结构以 7 张高清影像连续呈现，便于从整体到细节进行材料观察。`;
    h.note = '本组高清影像来自 Wikimedia Commons 的开放许可素材，经统一尺寸与格式规范化后用于本草镜视觉观察；原作者、许可与来源链接保存在仓库资产清单中。';
  });
  renderCatalogue();
  if (active) renderDetail(active);
})();
