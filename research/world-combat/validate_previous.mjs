import {readFileSync,writeFileSync,copyFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..'),p=resolve(root,'production/world-combat/previous');
const read=n=>JSON.parse(readFileSync(resolve(p,n),'utf8')),hash=f=>createHash('sha256').update(readFileSync(f)).digest('hex');
const choice=read('selection.json'),data=read('data.json'),manifest=read('manifest.json');
const ctx={window:{},structuredClone,document:{getElementById:()=>({textContent:''})},localStorage:{getItem:()=>null,setItem:()=>{}}};
vm.runInNewContext(readFileSync(resolve(p,'preferences.js'),'utf8'),ctx);
const validated=ctx.window.CombatExplorationPreferences(data,()=>{}).validate(choice);
if(JSON.stringify(validated)!==JSON.stringify(choice.choices))throw Error('Previous validator changed values');
for(const item of manifest.sources){const source=data.source_bindings.find(b=>b.id===item.id);if(!source||source.attempt_id!==item.attempt_id||source.sha256!==item.sha256||hash(resolve(root,item.path))!==item.sha256)throw Error('Previous native binding mismatch')}
const plan=resolve(p,'plan.json');if(hash(plan)!==choice.plan_sha256)throw Error('Previous plan mismatch');
const counts={};for(const k of ['character','style','weapon','power','comfort','shortlist']){counts[k]={};for(const c of Object.values(choice.choices)){const v=String(c[k]);counts[k][v]=(counts[k][v]||0)+1}}
const report={schema:'WorldCombatPreviousValidation/1',pass:true,validation:'Exact original preference validator plus native image hashes and exact previous plan hash',export_sha256:hash(resolve(p,'selection.json')),data_sha256:hash(resolve(p,'data.json')),plan_sha256:hash(plan),dataset_sha256:choice.dataset_sha256,bindings_verified:manifest.sources.length,counts,blank_notes:Object.values(choice.choices).every(c=>c.note===''),source:'User-pasted JSON; values and ordering preserved, whitespace normalized only. No prior browser state was read or changed.',owner_approval:null};
writeFileSync(resolve(root,'research/world-combat/previous-validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
