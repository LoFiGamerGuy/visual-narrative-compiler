import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {connect,pause} from '../nightglass-refinement/reader/cdp.mjs';
const root=process.cwd(),receipt=JSON.parse(readFileSync('research/texture-refinement-kit/package-verification.json','utf8'));
const c=await connect(9391),out=resolve('research/texture-refinement-kit/screenshots');mkdirSync(out,{recursive:true});
const results=[];
try{
 await c.send('Network.enable');
 await c.send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 for(const [name,dir] of [['live',resolve('docs/texture-refinement-kit')],['extracted',receipt.extracted]]){
  await c.send('Page.navigate',{url:pathToFileURL(resolve(dir,'index.html')).href});
  for(let i=0;i<50;i++){if(await c.ev('!!window.textureKitReady'))break;await pause(100)}
  if(!await c.ev('!!window.textureKitReady'))throw Error('Guide not ready');
  await c.ev("document.documentElement.style.scrollBehavior='auto'");
  await c.ev('(async()=>{for(const i of document.images){i.loading="eager";await i.decode()}})()');
  for(const [width,height] of [[390,844],[1024,768],[1440,1000]]){
   await c.viewport(width,height);
   await c.ev('scrollTo(0,0)');await pause(100);
   const checks=await c.ev(`(()=>({overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth===1536&&i.naturalHeight===1024,uncropped:Math.abs(i.getBoundingClientRect().width/i.getBoundingClientRect().height-1.5)<.01})),prompts:document.querySelectorAll('textarea').length,copyButtons:document.querySelectorAll('[data-copy]').length}))()`);
   if(checks.overflow||checks.images.length!==10||checks.images.some(i=>!i.loaded||!i.uncropped)||checks.prompts!==10||checks.copyButtons!==10)throw Error(JSON.stringify(checks));
   if(name==='extracted'&&width===390){
    await c.screenshot(resolve(out,'phone-guide.png'));
    await c.ev("document.getElementById('prompt-01').scrollIntoView()");await c.screenshot(resolve(out,'phone-prompt.png'));
    await c.ev("document.getElementById('example-S05-R1').scrollIntoView()");await c.screenshot(resolve(out,'phone-snow-pair.png'));
   }
   if(name==='extracted'&&width===1440){await c.ev("document.getElementById('example-S05-R1').scrollIntoView()");await c.screenshot(resolve(out,'desktop-snow-pair.png'))}
   results.push({name,width,height,...checks});
  }
  for(let i=1;i<=10;i++){
   const id=String(i).padStart(2,'0'),file=readFileSync(resolve(dir,`prompts/${id}.txt`),'utf8');
   if(await c.ev(`document.getElementById('text-${id}').value`)!==file)throw Error('Copy source differs from TXT');
  }
  // Exercise actual button plus deterministic denied-clipboard fallback.
  await c.ev("document.querySelector('[data-copy]').click()");await pause(200);
  const normal=await c.ev("document.getElementById('copy-status').textContent");
  await c.ev("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw Error('simulated permission denial')}}});document.execCommand=()=>false;document.querySelector('[data-copy]').click()");await pause(100);
  const fallback=await c.ev("({message:document.getElementById('copy-status').textContent,selected:document.activeElement.selectionEnd-document.activeElement.selectionStart,length:document.activeElement.value.length})");
  if(!fallback.message.includes('automatic copying is unavailable')||fallback.selected!==fallback.length)throw Error('Copy fallback failed');
  results.push({name,all_prompt_bytes_match:true,copy_status:normal,denied_clipboard_fallback:fallback});
 }
 if(c.errors.length)throw Error(JSON.stringify(c.errors));
 writeFileSync('research/texture-refinement-kit/browser-verification.json',JSON.stringify({pass:true,offline:true,results,errors:c.errors},null,2)+'\n');
 console.log(JSON.stringify({pass:true,offline:true,viewports:6,images:10,prompts:10,extraction:receipt.extracted}));
}finally{await c.close()}
