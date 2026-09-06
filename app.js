(async()=>{
  const names=['app-00.txt','app-01.txt','app-02.txt','app-03.txt'];
  const parts=await Promise.all(names.map(n=>fetch('./app-parts/'+n+'?v=364af3gh1',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(n);return r.text()})));
  (0,eval)(parts.join(''));
})().catch(err=>{console.error('BENCAO app load failed',err);document.body.dataset.appError='1';});
