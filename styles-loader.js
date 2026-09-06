(async()=>{
  const names=['css-00.txt','css-01.txt','css-02.txt'];
  const parts=await Promise.all(names.map(n=>fetch('./css-parts/'+n+'?v=364af3gh1',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(n);return r.text()})));
  const style=document.createElement('style');style.dataset.bencao='gh1';style.textContent=parts.join('');document.head.appendChild(style);
})().catch(err=>console.error('BENCAO style load failed',err));
