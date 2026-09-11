"""Freeze reviewed scripts, exact copy, budgets and reference roles before generation."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parents[2]
P=R/'production/pilot-chapters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
order=['NG','BP','ST','RC','FL']
style_ids=dict(NG='01',BP='19',ST='18',RC='13',FL='06')

def aspect(beat):
    cam=beat['camera'].lower()
    if 'vertical' in cam or 'extreme-wide' in cam or 'long rear' in cam:return 'portrait',1024,1536
    if len(beat['copy'])>1:return 'square',1024,1024
    if 'close' in cam or 'insert' in cam:return 'square',1024,1024
    return 'landscape',1536,1024

def lettering(beat,w,h,cast):
    copy=beat['copy'];items=[]
    for i,line in enumerate(copy):
        # Text remains editable. Actual-pixel review may reposition these boxes
        # with a candidate-hash-bound override; it may never change frozen copy.
        width=.455 if len(copy)>1 else .72
        x=.025+i*.495 if len(copy)>1 else .04
        height=min(.48, .30*w/h)
        item=dict(id=beat['id']+'-L'+str(i+1),speaker=line['speaker'],text=line['text'],kind=line.get('kind','speech'),x=x,y=.025,w=width,h=height)
        speaker_key=line.get('speaker_id',line['speaker'].split('/')[0].strip()).lower()
        visible=any(speaker_key==k or speaker_key in cast[k]['name'].lower() for k in beat['cast_in_frame'])
        if item['kind']=='speech' and not visible:
            item['offscreen']=True
            item['attribution']=line.get('attribution','Voice, inside' if speaker_key=='bloom' else line['speaker']+' · off panel')
        items.append(item)
    return items

def main():
    assert not (P/'plan.json').exists(),'Frozen plan exists; do not overwrite.'
    refs={x['id']:x for x in json.loads((P/'references.json').read_text())['references']}
    old=json.loads((R/'production/anchor-return/plan.json').read_text())
    controls={x['id']:x for x in json.loads((P/'controls/manifest.json').read_text())['controls']}
    plan={'schema':'PilotChaptersPlan/1','experiment_id':'PC-20260909-01','base_commit':'407750b0e74a93f8a0b0bb4a81ee8b3d0fc192d4','hypothesis':'Artwork-informed worlds and character appeal, then story-led newly drawn panels and editable lettering, can produce five distinct complete compact pilot chapters without losing the original media or quiet surfaces.','budget':json.loads((P/'budget.json').read_text())['budget'],'styles':old['styles'],'chapters':[],'entries':[],'support_entries':[],'policy':{'cast_and_canon':'provisional independent options','owner_preferences':'initially blank; historical choices separate','generation':'built-in only; every new panel newly generated','finishing':'source-only and evidence-based; medium and narrative contacts protected','provider_unknown_fields':None}}
    for cid in order:
        path=R/'research/pilot-chapters/editorial'/f'{cid}.json';s=json.loads(path.read_text());assert len(s['beats'])==16
        cast={c['id']:c for c in s['cast']};sid=style_ids[cid]
        chapter={k:s[k] for k in ['id','title','chapter_title','premise','emotional_engine','future_engine','style_contract','cast','setting','power_rule']}
        chapter.update(subtitle=s['chapter_title'],logline=s['premise'],panel_ids=[b['id'] for b in s['beats']],script_path=str(path.relative_to(R)),script_sha256=sha(path),style_id=sid)
        plan['chapters'].append(chapter)
        plan['support_entries'].append(dict(id=cid+'-SHEET',chapter_id=cid,category=cid,title=s['title']+' · provisional cast',brief='One front view of each principal subject and clear signature equipment; no contradictory turnaround or unlabeled mirror view.',reference_id=sid,cast=s['cast']))
        for j,b in enumerate(s['beats'],1):
            assert b['id']==f'{cid}{j:02}'
            assert len(b['copy'])<=2
            assert all(x['text'].strip() for x in b['copy'])
            assert b.get('cast_in_frame') is not None, b['id']+' lacks explicit visible cast'
            assert all(x in cast for x in b['cast_in_frame'])
            shape,w,h=aspect(b)
            e={**b,'chapter_id':cid,'category':cid,'sequence_order':j,'title':b.get('title',b['action'].split(';')[0][:90]),'brief':b['action'],'aspect':shape,'requested_width':w,'requested_height':h,'lettering':lettering(b,w,h,cast),'gap_after':80 if not b['copy'] else 32,'references':[{'path':refs[sid]['path'],'sha256':refs[sid]['sha256'],'role':'Original drawing and world benchmark only; this is a new single story panel.'}],'subject_reference_id':cid+'-SHEET'}
            if e['id'] in controls:e['control']=controls[e['id']]
            plan['entries'].append(e)
    assert len(plan['entries'])==80 and len(plan['support_entries'])==5
    dump(P/'plan.json',plan);(P/'plan.sha256').write_text(sha(P/'plan.json')+'\n')
    print(json.dumps({'panels':80,'chapters':5,'support_sheets':5,'plan_sha256':sha(P/'plan.json')}))

if __name__=='__main__':main()
