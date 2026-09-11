"""Summarize recorded experiment work without converting observations into approval."""
from pathlib import Path
from datetime import datetime
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'production/structural-pilot'
def read(path): return json.loads(path.read_text())
def seconds(a, b): return (datetime.fromisoformat(b)-datetime.fromisoformat(a)).total_seconds()
events = [json.loads(x) for x in (P/'events.jsonl').read_text().splitlines()]
attempts = [e['data'] for e in events if e['type']=='reserved']
failures = [e['data'] for e in events if e['type']=='failed']
assert len(attempts)==13 and len({a['id'] for a in attempts})==13
work = [json.loads(x) for x in (P/'worklog.jsonl').read_text().splitlines()]
effort = {}
for panel in ('P09','P11'):
    primary = correction = 0
    start = cstart = None
    for row in work:
        if row.get('panel')!=panel: continue
        event = row['event']; at = row['at_utc']
        if event in ('primary-authoring-start','primary-authoring-resume'): start=at
        elif event in ('primary-authoring-pause','primary-authoring-end'):
            primary += seconds(start,at); start=None
        elif event=='correction-authoring-start': cstart=at
        elif event=='correction-authoring-end': correction += seconds(cstart,at); cstart=None
    assert start is None and cstart is None
    effort[panel]={'primary_seconds':primary,'correction_seconds':correction}
p13=read(P/'finishing/CF/P13/effort-and-pixel-evidence.json')
effort['P13']={'primary_seconds':p13['primary_agent_wall_seconds'],'correction_seconds':p13['correction_agent_wall_seconds']}
for row in effort.values():
    assert row['primary_seconds']<=2400 and row['correction_seconds']<=1200
    row['total_seconds']=row['primary_seconds']+row['correction_seconds']
S=read(P/'finishing/S/finishing-summary.json')
control=read(P/'control/control-author-record.json')
result={
 'schema':'StructuralExperimentResults/1',
 'experiments':['SC-20260907-01','CF-20260907-02'],
 'source_commit':'0c1a8fb337d82f0c9c2a45ed94661d1bdaa1f424',
 'panel_generation':{'total':len(attempts),'primary':sum(a['retry_of'] is None for a in attempts),'targeted_retry':sum(a['retry_of'] is not None for a in attempts),'by_route':dict(Counter(a['route'] for a in attempts)),
   'documented_hard_failure_attempt_count':len({f['attempt_id'] for f in failures}),'failures':failures,'actual_observations':sum(e['type']=='observed' for e in events),
   'failure_interpretation':'Raw instruction-contract failures, including all six S alpha failures; not a production success-rate estimate.'},
 'cast_reference_calls':len(read(P/'asset-attempts.json')['attempts']),
 'new_in_product_image_calls_total':14,
 'old_baseline_budgets':{'primary':14,'correction':9,'reference':3,'status':'closed-preserved'},
 'agent_effort':{'control_seconds':control['elapsed_agent_authoring_seconds'],'S_primary_seconds':S['primary_seconds'],'S_correction_seconds':S['correction_seconds'],'S_packaging_seconds':S['packaging_seconds'],'CF_panels':effort,'CF_total_minutes':sum(v['total_seconds'] for v in effort.values())/60,'meaning':'Recorded agent wall authoring intervals, not human labor or total project elapsed time. Parallel work must not be added to claim elapsed time.'},
 'costs':{'direct_paid_usd':0,'in_product_billing_allocation':None,'usage':None,'human_labor_hours':None},
 'raster_metadata':{'provider':None,'model_snapshot':None,'seed':None,'reasoning_model_is_not_image_model':True},
 'decision':{'platform':'Retain Ember provisionally; no identified-provider comparison was run.','active_experimental_workflow':'Editable control, bounded illustrated draft, explicit local correction, editable lettering, actual continuous review.','S_finished_screen':'failed-artistic-coherence','G_screen':'failed-contact-and-motion-contract','CF_result':'Narrow visible corrections; whole sequence remains incoherent.','new_10_to_14_panel_expansion':'not-earned-not-run','production_accepted':False},
 'implemented':['Seven-panel editable original Blender scene and separate passes','Four S and four G screened panels with bounded targeted retries','Three zero-generation local correction proofs; unchanged G14 reference','Fourteen-panel context readers and compact before/after','Source-bound persisted browser lettering drafts with immutable history'],
 'failed':['Requested native transparent character layers returned opaque checkerboards','Fixed machinery and patched anatomy retain diagram-like finish','Full-frame retries lost exact contact, motion or aftermath state','First CF09 contact and CF11 repair versions showed material/seam artifacts; preserved and corrected within one declared round'],
 'unrun':['NovelAI: no authorized connected access available','Local ComfyUI renderer: checked endpoints unavailable','Skilled human artist correction','New coherent 10–14-panel expansion','Independent human comprehension','Owner-preference approval','Commercial-clearance review'],
 'acceptance':{'file_integrity':'See verification receipts','actual_semantics':'AI observations and independent AI reviews; limitations retained','lettering_mobile':'See actual browser QA','artistic_appeal':'Below requested sequential-art bar','independent_human_comprehension':None,'owner_preference':None,'commercial_clearance':None},
 'errata':['CF P13 F02 spec timestamp typo is preserved; corrected observed 25-second interval is in effort-and-pixel-evidence.json.','Reference order in generic ledger is not ordered tool input: exact calls/Axxxxx.json records the actual guide-first, cast-second tool arguments.']
}
out=ROOT/'research/structural-pilot/implementation-results.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'new_image_calls':14,'hard_failure_attempts':result['panel_generation']['documented_hard_failure_attempt_count'],'CF_minutes':result['agent_effort']['CF_total_minutes']}))
