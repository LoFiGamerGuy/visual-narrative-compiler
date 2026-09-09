"""Compile immutable built-in jobs from the frozen pilot plan; never call paid APIs."""
from pathlib import Path
import argparse,hashlib,json,re
R=Path(__file__).resolve().parents[2];P=R/'production/pilot-chapters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['support','panels']);ap.add_argument('--chapter');a=ap.parse_args()
    plan=json.loads((P/'plan.json').read_text());refs={x['id']:x for x in json.loads((P/'references.json').read_text())['references']};chapters={c['id']:c for c in plan['chapters']}
    candidates={c['attempt_id']:c for c in json.loads((P/'candidates.json').read_text())['candidates']} if (P/'candidates.json').exists() else {}
    selected=json.loads((P/'selected.json').read_text())['selected'] if (P/'selected.json').exists() else {}
    qualifications=json.loads((P/'reference-qualifications.json').read_text())['entries']
    jobs=[]
    entries=plan['support_entries'] if a.mode=='support' else plan['entries']
    for e in entries:
        if a.chapter and e['chapter_id']!=a.chapter:continue
        aid=e['id']+'-P';jp=P/'jobs'/f'{aid}.json';assert not jp.exists(),aid+' already frozen'
        ch=chapters[e['chapter_id']];ref=refs[ch['style_id']]
        rr=[dict(path=ref['path'],sha256=ref['sha256'],role='Original drawing/world benchmark. Preserve its particular drawing treatment, not its board layout.')]
        medium=ch['style_contract']['medium']
        if a.mode=='support':
            people='\n'.join(f"{c['name']}: {c['visual']} Equipment: {c.get('equipment','none')}" for c in ch['cast'])
            prompt=f'''Use case: illustration-story. Create one original provisional cast reference sheet for a new webcomic called {ch['title']}. Landscape 1536x1024. Reference image 1 supplies the drawing medium and world appeal, not a layout to copy.
Style: {medium} Preserve: {ch['style_contract']['retain']}
Show the following principal subjects, each only ONCE in a clear three-quarter/front complete view, separated on a quiet neutral field; a large creature may be shown at smaller diagram scale beside the people. No repeated alternate faces, turnarounds or isolated mirrored equipment. Adults remain clearly adult.
{people}
All garments and equipment intact at this reference stage. Hands actually grip their equipment. If RIGHT hand is specified, trace the anatomical right shoulder/elbow/wrist; on a front-facing figure it is on the viewer's left. Do not invent extra weapons or alternate versions. Keep silhouettes, faces and gear construction clean and memorable. Broad material shapes, selective expressive detail. No busy flooring, particles, scratches, repeated hair facets or glossy generic fantasy. Preserve this original medium's intentional ink or paint character.
Return one polished reference artwork with no writing, labels, lettering, logos, watermarks or decorative border. This sheet is a provisional option, not selected canon.'''
        else:
            sc=candidates[selected[e['subject_reference_id']]]
            rr.append(dict(path=sc['path'],sha256=sc['sha256'],role='New inspected cast identity and equipment reference only. Its neutral layout is not this panel composition.'))
            control=''
            if e.get('control'):
                c=e['control'];rr.append(dict(path=c['path'],sha256=c['sha256'],role=c['role']))
                control='Reference 3 is ONLY an editable geometry/contact schematic. Preserve its useful force/contact relationships but draw the specified camera, realistic anatomy, faces and medium from references 1–2. Never render its labels, stick figures, colored debug shapes or diagram background. '+c['role']
            cast={c['id']:c for c in ch['cast']}
            visible='\n'.join(f"{cast[k]['name']}: {cast[k]['visual']} Equipment: {re.sub(r'No initial[^.]*[.]?', '', cast[k].get('equipment','none'), flags=re.I).strip()}" for k in e['cast_in_frame'])
            qualification=qualifications.get(e['chapter_id'],{})
            for before,after in qualification.get('visual_replacements',{}).items():visible=visible.replace(before,after)
            qualification_note=qualification.get('prompt_note','Current story state overrides reference pose or charge state.')
            if e['chapter_id']=='NG':
                qualification_note=' '.join((['Pell wears only his mustard jacket and body harness; omit the tall external rig beside him in the sheet.'] if 'pell' in e['cast_in_frame'] else [])+(['Sera keeps the long burgundy coat variant shown in the inspected sheet.'] if 'sera' in e['cast_in_frame'] else []))
            if e['chapter_id']=='FL':
                qualification_note=''
                if 'corin' in e['cast_in_frame']:qualification_note+='Corin currently wears plain black gloves on BOTH hands.' if e['sequence_order']<4 else 'Corin currently has a BARE LEFT hand and a plain black glove on his RIGHT hand.'
                if 'lio' in e['cast_in_frame']:qualification_note+=' Lio’s municipal key has a simple TRIANGULAR brass head, not the round bow in the sheet.'
            visibility='; '.join(k+': '+v for k,v in e.get('cast_visibility',{}).items())
            special='; '.join(e.get('special_visual_elements',[]))
            for k,c in cast.items():
                if k not in e['cast_in_frame'] and c['name'].split()[0] in special:
                    special+=' Appearance for this explicitly nonphysical depiction ONLY: '+c['visual']
            h=max((x['y']+x['h'] for x in e['lettering']),default=0)
            lettering=f"Reserve the upper {round(h*100)+3}% of the image as calm, broad in-world background for later speech balloons. Keep ALL faces, hands, important contact and clue details BELOW that zone. Do not draw balloons or text; the blank space will receive editable lettering." if h else 'This is a silent story beat. Use the whole image deliberately; no arbitrary text band.'
            prompt=f'''Use case: illustration-story. Draw ONE NEW finished webcomic panel, not a poster, collage, split board or multiple panels. {e['aspect'].upper()} image, requested {e['requested_width']}x{e['requested_height']}.
Reference 1 is the original drawing/world benchmark. Reference 2 supplies only our newly inspected cast identities, clothing and equipment. Compose the completely new moment described below. Do not reproduce either reference's framing or add its absent characters.
{control}
Drawing treatment: {medium} Preserve {ch['style_contract']['retain']} Avoid {ch['style_contract']['avoid']}
World context: {ch['setting']}
VISIBLE subjects in this panel ONLY:
{visible or 'No principal person visible; show the specific object/environment described below.'}
Inspected reference qualification for visible subjects only: {qualification_note or 'none'}
Visibility/cropping constraints: {visibility or 'Only the subjects above, framed as specified below.'}
ONE current moment: {e['action']}
Current physical state (authoritative): {e['current_state']}
Special visual element, only if specified: {special or 'none'}
Camera and framing: {e['camera']} Respect actual subject-to-frame size, especially extreme wides. Do not enlarge a distant person into a medium shot.
{lettering}
Draw acting with a specific expression and body intention. For contact, show the physical source/contact/target and its immediate reaction. For a clasp or weapon, make shoulder-elbow-wrist-hand-object ownership legible. Keep supports, scale and visible limb anatomy sound. Do not add later injuries, additional duplicates, alternate weapons, generic glows or undescribed consequences.
Surface design: matte quiet ground, broad deliberate light and shadow shapes, selective purposeful architecture. Group foliage, hair and material marks. Keep medium-defining directional ink/brushwork; avoid pervasive microtexture, repeated tiny facets, flooring crack networks, mirror floors and reflection glitter. Preserve richness through faces, composition and world depth.
No text of any kind, no speech balloons, no glyphs, no captions, no SFX lettering, no UI, no signatures, no watermark, no frame. Exact dialogue will be added separately. Return only the new artwork.'''
        pp=P/'prompts'/f'{aid}.txt';assert not pp.exists();pp.write_text(prompt.rstrip()+'\n')
        j=dict(id=e['id'],attempt_id=aid,phase='primary',category=e['chapter_id'],retry_of=None,retry_reason=None,prompt=pp.read_text(),prompt_path=str(pp.relative_to(R)),prompt_sha256=sha(pp),plan_sha256=sha(P/'plan.json'),references=rr)
        if a.mode=='panels':j.update(qualifications_path='production/pilot-chapters/reference-qualifications.json',qualifications_sha256=sha(P/'reference-qualifications.json'))
        dump(jp,j);jobs.append(j)
    out=P/f"jobs-{a.mode}{'-'+a.chapter if a.chapter else ''}.json";assert not out.exists();dump(out,jobs)
    print(json.dumps({'jobs':len(jobs),'path':str(out.relative_to(R))}))

if __name__=='__main__':main()
