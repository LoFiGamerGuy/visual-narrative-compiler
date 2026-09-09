// Executed in the functions tool JavaScript environment, not Node or an API client.
// Supply a reviewed frozen job array with exact prompt strings. Four workers maximum.
async function run(jobs) {
 const root=load("pcRoot"),q=s=>"'"+s.replace(/'/g,"'\\''")+"'";
 let cursor=0;const outcomes=[];
 async function worker() { while(cursor<jobs.length) {const j=jobs[cursor++];try{
 const {prompt,...meta}=j;const paths=j.references.map(r=>root+"/"+r.path);
 const rec={...meta,started:await tools.clock__curr_time({}),referenced_image_paths:paths,tool:"builtin image_gen",model:null,snapshot:null,seed:null,usage:null,billing:null,direct_paid_spend_usd:0};
 async function save(data,initial=false) {const code="from pathlib import Path;p=Path("+JSON.stringify(root+"/production/pilot-chapters/calls/"+j.attempt_id+".json")+");"+(initial?"assert not p.exists();":"")+"p.write_text("+JSON.stringify(JSON.stringify(data,null,2)+"\n")+")";
 const r=await tools.exec_command({cmd:"python3 -c "+q(code),login:false,max_output_tokens:300});if(r.exit_code!==0)throw Error(r.output);}
 await save(rec,true);
 let result;try{result=await tools.image_gen__imagegen({prompt,referenced_image_paths:paths});}catch(error){await save({...rec,finished:await tools.clock__curr_time({}),status:"failed-no-artwork-returned",returned_artwork:null,error:String(error)});throw error;}generatedImage(result);
 const receipt={...rec,finished:await tools.clock__curr_time({}),output_hint:result.output_hint};store("pcResult:"+j.attempt_id,receipt);await save(receipt);
 outcomes.push({id:j.attempt_id,status:"saved"});text({id:j.attempt_id,status:"saved"});
 }catch(e){outcomes.push({id:j.attempt_id,status:"error",error:String(e)});text(outcomes.at(-1));} }}
 const settled=await Promise.allSettled(Array.from({length:Math.min(4,jobs.length)},()=>worker()));text({workers:settled.map(x=>({status:x.status,reason:String(x.reason||"")})),outcomes});
}
