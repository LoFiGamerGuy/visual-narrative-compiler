import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const group=process.argv[2]||'maps';
const attempt=process.argv[3]||'2';
const chrome='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const lib='/mnt/c/AgentWorkspaces/anime-pipeline-total-review-20260907-014149/research/anime-pipeline-total-review/.scratch/browser-comparables/lib/usr/lib/x86_64-linux-gnu';
const manifest=JSON.parse(await fs.readFile(path.join(here,'v1/manifest.json'),'utf8'));
const rows=manifest.records.filter(x=>group==='maps'?x.id.startsWith('map-'):!x.id.startsWith('map-'));
const sha=buf=>crypto.createHash('sha256').update(buf).digest('hex');
const rendered=[];
for(const row of rows){
 const svg=path.join(here,row.svg),png=svg.replace(/\.svg$/,'.png');
 try{await fs.access(png);throw Error('Preserve existing render: '+png)}catch(e){if(e.code!=='ENOENT')throw e}
 const local=path.join(here,'local','render-'+row.id+'-try'+attempt);
 await fs.mkdir(local,{recursive:true});
 for(const d of ['cache','config','tmp'])await fs.mkdir(path.join(local,d),{recursive:true});
 if(sha(await fs.readFile(svg))!==row.svg_sha256)throw Error('SVG source hash mismatch');
 const args=['--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check','--hide-scrollbars','--force-device-scale-factor=1','--run-all-compositor-stages-before-draw','--timeout=10000','--window-size=1200,800','--user-data-dir='+path.join(local,'profile'),'--screenshot='+png,pathToFileURL(svg).href];
 const start=new Date().toISOString();let log='';
 await new Promise((resolve,reject)=>{
  const child=spawn(chrome,args,{env:{...process.env,LD_LIBRARY_PATH:lib,XDG_CACHE_HOME:path.join(local,'cache'),XDG_CONFIG_HOME:path.join(local,'config'),TMPDIR:path.join(local,'tmp')},stdio:['ignore','pipe','pipe']});
  child.stdout.on('data',x=>log+=x);child.stderr.on('data',x=>log+=x);
  child.on('error',reject);child.on('close',async(code,signal)=>{await fs.writeFile(path.join(local,'process.log'),log,{flag:'wx'});code===0?resolve():reject(Error('Chrome exit '+code+' signal '+signal+' '+log.slice(-2500)))});
 });
 await fs.writeFile(path.join(local,'renderer.log'),log,{flag:'wx'});
 const raw=await fs.readFile(png);if(raw.readUInt32BE(16)!==1200||raw.readUInt32BE(20)!==800)throw Error('Unexpected render size');
 rendered.push({id:row.id,svg:row.svg,svg_sha256:row.svg_sha256,png:path.relative(here,png),png_sha256:sha(raw),width:1200,height:800,started_utc:start,finished_utc:new Date().toISOString()});
 console.log(row.id+' rendered '+sha(raw));
}
await fs.writeFile(path.join(here,'v1','render-receipt-'+group+'.json'),JSON.stringify({schema:'CombatDepthSvgRender/1',renderer:'Chromium static SVG screenshot; no raster editing',code_sha256:sha(await fs.readFile(fileURLToPath(import.meta.url))),group,rendered},null,2)+'\n',{flag:'wx'});
