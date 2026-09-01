"""Validate CH04 built-in frontier-art draft provenance without judging quality."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PLANS=ROOT/'production/comic/ch04-sc01-panel-plans-v1.json'
REVISIONS=ROOT/'production/comic/panel-revisions/ch04-sc01-imagegen-r1.json'
REVIEW=ROOT/'experiments/reviews/ch04-dawn-trail-imagegen-review-r1.json'
EDITION=ROOT/'production/editions/north-garden-ch04-imagegen-draft-edition-001.json'
def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
    plans=json.loads(PLANS.read_text()); revisions=json.loads(REVISIONS.read_text()); review=json.loads(REVIEW.read_text()); edition=json.loads(EDITION.read_text())
    assert plans['medium']=='comic' and plans['animation_shot_plan'] is None
    assert [x['panel_id'] for x in plans['plans']]==['ng-ch04-sc01-p001','ng-ch04-sc01-p002','ng-ch04-sc01-p003']
    assert all(x['spatial_mode']=='2d_only' for x in plans['plans'])
    for revision in revisions['revisions']:
        raster=ROOT/revision['asset_path']; record=json.loads((ROOT/revision['render_record']).read_text())
        assert raster.exists() and sha(raster)==revision['sha256']==record['output']['sha256']
        assert record['accepted'] is False and record['human_minutes'] is None
        assert record['prompt_safety']=={'fictional_adults_only':True,'child_data':False,'adult_likeness_input':False,'external_personal_data_upload':False,'age_wording_hygiene':'pass'}
    assert review['state']=='PENDING_AUTHORIZED_HUMAN_REVIEW' and review['summary']['research_accepted']==0
    assert edition['publication_state']=='DRAFT_REVIEW_PENDING_NOT_PUBLISHED'
    assert edition['selected_panel_revision_ids']==[x['panel_revision_id'] for x in revisions['revisions']]
    print('0 failures, 0 warnings (CH04 built-in frontier-art sequence provenance validated)')
if __name__=='__main__': main()
