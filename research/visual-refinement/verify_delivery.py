"""Verify delivered native provenance, frozen inputs, selections and call ceilings."""
from pathlib import Path
import argparse, collections, hashlib, json, struct

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'production/visual-refinement'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def verify(require_complete=True, check_originals=True):
    errors=[]; observations=[]
    def check(ok, message):
        if not ok: errors.append(message)
    jobs={}
    for name in ['comparison-jobs.json','comparison-retry-jobs.json','sequence-jobs.json','sequence-retry-jobs.json']:
        path=P/name
        if not path.exists(): continue
        frozen=path.with_suffix(path.suffix+'.sha256')
        check(frozen.exists() and frozen.read_text().split()[0]==sha(path), 'Frozen job manifest changed: '+name)
        for job in read(path)['jobs']:
            aid=job['attempt_id']; check(aid not in jobs,'Duplicate frozen job '+aid); jobs[aid]=job
            check(sha(ROOT/job['prompt_path'])==job['prompt_sha256'],'Frozen prompt changed: '+aid)
            for ref in job['references']:
                check(sha(ROOT/ref['path'])==ref['sha256'],'Frozen reference changed: '+aid+' '+ref['path'])
            if job.get('copy_source'):
                c=job['copy_source']; check(sha(ROOT/c['path'])==c['sha256'],'Frozen dialogue changed: '+aid)
    for rel in ['research/visual-refinement/experiment.md','production/visual-refinement/sequence-plan.json']:
        path=ROOT/rel; check(path.with_suffix(path.suffix+'.sha256').read_text().split()[0]==sha(path),'Frozen plan changed: '+rel)
    calls={}
    for path in sorted((P/'calls').glob('*.json')):
        c=read(path); aid=c['attempt_id']; check(aid not in calls,'Duplicate receipt '+aid); calls[aid]=c
        check(c.get('direct_paid_spend_usd')==0,'Missing or nonzero direct spend receipt: '+aid)
        for field in ['model','snapshot','seed','usage','billing']:
            check(field in c and c[field] is None,'Unexpected backend metadata: '+aid+' '+field)
        check('image_url' not in path.read_text(),'Inline raster data in receipt '+aid)
        check(sha(ROOT/c['prompt_path'])==c['prompt_sha256'],'Receipt prompt mismatch '+aid)
        if aid in jobs:
            j=jobs[aid]
            check(c['prompt_sha256']==j['prompt_sha256'] and c['references']==j['references'],'Receipt differs from frozen job '+aid)
    for asset in read(P/'setup-plan.json')['assets']:
        aid=asset['id']+'-P'
        check(sha(ROOT/asset['path'])==asset['sha256'],'Setup prompt changed '+aid)
        if aid in calls: check(calls[aid]['prompt_sha256']==asset['sha256'],'Setup receipt mismatch '+aid)
    counts=collections.Counter(c['phase'] for c in calls.values())
    retries=[aid for aid in calls if aid.endswith('-R')]
    check(len(calls)<=50 and len(retries)<=10,'Call budget exceeded')
    by_id=collections.Counter(c['id'] for c in calls.values())
    check(all(n<=2 for n in by_id.values()),'More than one repair per asset')
    candidates={}; primary_counts=collections.Counter(); aspect_drift=[]
    for name,phase in [('setup-candidates.json','setup'),('candidates.json','comparison'),('sequence-candidates.json','sequence')]:
        for row in read(P/name)['candidates']:
            aid=row['attempt_id']; candidates[aid]=row; path=ROOT/row['path']; c=calls[aid]
            check(sha(path)==row['sha256'],'Native hash mismatch '+aid)
            check(struct.unpack('>II',path.read_bytes()[16:24])==(row['width'],row['height']),'Native dimensions mismatch '+aid)
            check(row['owner_approval'] is None and row['status']=='reviewable-unaccepted','Invented approval '+aid)
            if check_originals: check(sha(Path(row['source_path']))==row['sha256'],'Original tool PNG differs '+aid)
            if aid.endswith('-P'): primary_counts[phase]+=1
            j=jobs.get(aid,{})
            if j.get('requested_aspect_ratio'):
                a,b=map(int,j['requested_aspect_ratio'].split(':'))
                if abs(row['width']/row['height']-a/b)>.015: aspect_drift.append({'attempt_id':aid,'requested':j['requested_aspect_ratio'],'native':[row['width'],row['height']]})
    check(set(candidates)<=set(calls),'Candidate without receipt')
    if require_complete:
        check(dict(primary_counts)=={'setup':2,'comparison':20,'sequence':18},'Missing planned primary returns')
        check(len(candidates)==len(calls),'Not every call has a retained native return; inspect failures')
    for filename,expected in [('selected.json',20),('sequence-selected.json',18)]:
        selected=read(P/filename)['selected']
        if require_complete: check(len(selected)==expected,'Incomplete selection '+filename)
        for key,aid in selected.items(): check(aid in candidates and candidates[aid]['id']==key,'Invalid selection '+key)
    return {'schema':'RefinementDeliveryVerification/1','pass':not errors,'errors':errors,'call_counts':dict(counts),'total_calls':len(calls),'repair_calls':len(retries),'native_returns':len(candidates),'primary_returns':dict(primary_counts),'native_aspect_drift':aspect_drift,'original_tool_pngs_checked':check_originals,'backend_metadata':'Not returned; null retained.','direct_paid_spend_usd':0,'scope':'Native hashes, original tool bytes when available, frozen prompts/reference/copy hashes, receipt bindings, explicit selections and call budget. This is not an artistic or semantic acceptance test.'}

if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('--progressive',action='store_true'); a.add_argument('--portable',action='store_true'); a.add_argument('--output',default='research/visual-refinement/delivery-verification.json'); args=a.parse_args()
    report=verify(not args.progressive,not args.portable); out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report)); raise SystemExit(0 if report['pass'] else 1)
