// Element-anchored capture: uses Playwright's scrollIntoViewIfNeeded (which
// handles nested scroll containers) then a viewport screenshot showing the
// furniture amid its surrounding prose. Robust to the legacy scroll machinery.
import { chromium } from 'playwright-core';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const MIME={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2','.gif':'image/gif','.avif':'image/avif'};
function serve(root){return new Promise(r=>{const s=http.createServer((q,res)=>{try{let p=decodeURIComponent(q.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';const fp=path.join(root,p);if(!fp.startsWith(root)||!fs.existsSync(fp)||fs.statSync(fp).isDirectory()){res.writeHead(404);res.end();return;}res.writeHead(200,{'Content-Type':MIME[path.extname(fp).toLowerCase()]||'application/octet-stream'});fs.createReadStream(fp).pipe(res);}catch(e){res.writeHead(500);res.end();}});s.listen(0,'127.0.0.1',()=>r(s));});}
const [urlPath,outPrefix,vpArg,csArg]=process.argv.slice(2);
const vp=vpArg==='mobile'?{width:390,height:844}:{width:1440,height:900};
const srv=await serve('/home/user/the-signal');const port=srv.address().port;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
const ctx=await b.newContext({viewport:vp,serviceWorkers:'block',colorScheme:csArg||'light'});
const pg=await ctx.newPage();
await pg.goto(`http://127.0.0.1:${port}${urlPath}`,{waitUntil:'networkidle',timeout:30000}).catch(()=>{});
await pg.waitForTimeout(500);
// warm-up to trigger reveals on surrounding prose
await pg.evaluate(async()=>{const h=document.documentElement.scrollHeight,s=Math.round(innerHeight*0.6);for(let y=0;y<=h;y+=s){scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}});
const targets=[['.mx-numbers',0],['.mx-ledger',0],['.mx-ledger',4],['.mx-quote',1],['.mx-quote',5],['.mx-cheat',0]];
for(const [sel,idx] of targets){
  const loc=pg.locator(sel).nth(idx);
  try{
    await loc.scrollIntoViewIfNeeded({timeout:5000});
    await pg.waitForTimeout(300);
    const name=sel.replace(/[^a-z]/gi,'')+idx;
    await pg.screenshot({path:`${outPrefix}__${name}.png`});
  }catch(e){console.log('MISS',sel,idx,String(e).slice(0,60));}
}
console.log('done');
await b.close();srv.close();
