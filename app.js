(async()=>{
  const names=['app-00.txt','app-01.txt','app-02.txt','app-03.txt'];
  const parts=await Promise.all(names.map(n=>fetch('./app-parts/'+n+'?v=364af3gh1',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(n);return r.text()})));
  let source=parts.join('');
  const directLoader=`async function spriteDataUrl(herb){\n  if(spriteCache.has(herb)) return spriteCache.get(herb);\n  const promise=fetch(\`./assets/\${herb}-direct.b64?v=\${VERSION}\`,{cache:'force-cache'}).then(async r=>{\n    if(!r.ok) throw new Error(\`sprite \${herb}\`);\n    return \`data:image/webp;base64,\${(await r.text()).trim()}\`;\n  });\n  spriteCache.set(herb,promise);\n  return promise;\n}\n`;
  source=source.replace(/async function spriteDataUrl\(herb\)\{[\s\S]*?(?=async function hydrateSprites)/,directLoader);
  (0,eval)(source);
})().catch(err=>{console.error('BENCAO app load failed',err);document.body.dataset.appError='1';});
