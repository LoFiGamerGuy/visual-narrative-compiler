"""Narrow validator for the first linked North Garden production records."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FILES=[ROOT/'production/canon/story-state/ch01-sc01-v1.json',ROOT/'production/assets/asset-registry-ch01-v1.json',ROOT/'production/scene-beats/ch01-sc01-argument-v1.json',ROOT/'production/comic/ch01-sc01-panel-plans-v1.json',ROOT/'production/editions/north-garden-research-edition-001.json',ROOT/'production/stages/kitchen-table-spatial-contract-v1.json']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=[json.loads(p.read_text()) for p in FILES]; story,assets,beat,plans,edition,stage=d
 assert story['record_id']==beat['story_state_id']==plans['story_state_id']
 assert plans['medium']=='comic' and plans['animation_shot_plan'] is None
 ids={a['asset_id'] for a in assets['assets']}
 assert all(set(p['asset_ids'])<=ids and p['spatial_mode'] in {'grounded','cheated','2d_only'} for p in plans['plans'])
 assert all(p.get('spatial_stage_contract_id')=='ng-stage-kitchen-table-contract-r1' and p.get('spatial_assignments') for p in plans['plans'] if p['spatial_mode']=='grounded')
 by_id={p['panel_id'] for p in plans['plans']}
 assert {x['panel_id'] for x in edition['selected_revisions']}==by_id
 for item in edition['selected_revisions']: assert sha(ROOT/item['accepted_asset'])==item['sha256']
 plans_v2=json.loads((ROOT/'production/comic/ch01-sc01-panel-plans-v2.json').read_text())
 revisions=json.loads((ROOT/'production/comic/panel-revisions/ch01-sc01-initial-import-r1.json').read_text())
 edition_v2=json.loads((ROOT/'production/editions/north-garden-research-edition-002.json').read_text())
 assert plans_v2['record_type']=='ComicPanelPlanCollection' and plans_v2['schema_version']=='2.0'
 assert plans_v2['supersedes']==plans['record_id'] and plans_v2['animation_shot_plan'] is None
 stable_panel_ids={plan['panel_id'] for plan in plans_v2['plans']}
 assert all('-r' not in panel_id for panel_id in stable_panel_ids)
 assert len(stable_panel_ids)==len(plans_v2['plans'])
 assert all(plan['plan_revision_id'].endswith('-plan-r2') for plan in plans_v2['plans'])
 assert all(plan['spatial_mode'] in {'grounded','cheated','2d_only'} and plan['spatial_assignments'] for plan in plans_v2['plans'])
 assert revisions['record_type']=='PanelRevisionCollection' and revisions['comic_plan_collection']=='production/comic/ch01-sc01-panel-plans-v2.json'
 revisions_by_id={revision['panel_revision_id']:revision for revision in revisions['revisions']}
 assert {revision['panel_id'] for revision in revisions['revisions']}==stable_panel_ids
 assert all(sha(ROOT/revision['asset_path'])==revision['sha256'] for revision in revisions['revisions'])
 assert all(revision['render_record'] is None and revision['revision_kind']=='historical_import' for revision in revisions['revisions'])
 assert edition_v2['supersedes_edition_id']==edition['edition_id']
 assert edition_v2['comic_plan_collection']==revisions['comic_plan_collection']
 assert set(edition_v2['selected_panel_revision_ids'])==set(revisions_by_id)
 assert stage['authority_state']=='CALIBRATED_2D_LEGACY_REFERENCE_NOT_CANONICAL_3D'
 assert stage['intent_boundary'].startswith('Reusable spatial constraints')
 assert stage['camera_profiles'][0]['not_animation_camera'].startswith('Animation camera')
 assert all(len(o['polygon_normalized']) >= 3 for o in stage['occluders'])
 canonical=json.loads((ROOT/'production/stages/kitchen-table-canonical-geometry-bootstrap-v1.json').read_text())
 assert canonical['shared_asset_boundary'].startswith('Shared canon/set asset')
 assert canonical['adapter_uses']['animation'].startswith('May supply set geometry only')
 canonical_v2=json.loads((ROOT/'production/stages/kitchen-table-canonical-geometry-bootstrap-v2.json').read_text())
 assert canonical_v2['shared_asset_boundary'].startswith('Shared canon/set asset')
 assert 'neutral world-coordinate anchors' in canonical_v2['shared_asset_boundary']
 projection=json.loads((ROOT/'production/stages/kitchen-table-world-to-comic-panel-projection-v1.json').read_text())
 assert projection['stage_id']==canonical_v2['record_id'] and projection['boundary'].startswith('This map permits comic-plan')
 resolved=json.loads((ROOT/'production/stages/resolved/ch01-sc01-kitchen-spatial-inputs-v1.json').read_text())
 assert resolved['state']=='INTENT_DERIVED_NOT_RENDER_PROVENANCE' and resolved['animation_shot_plan'] is None
 assert resolved['plans_source_sha256']==sha(ROOT/'production/comic/ch01-sc01-panel-plans-v1.json')
 manifest_path=ROOT/'production/comic/hard-assertion-manifests/g07-fictional-proxy-v1.json'
 manifest=json.loads(manifest_path.read_text())
 assert manifest['record_type']=='HardAssertionManifest' and manifest['medium']=='comic' and manifest['animation_shot_plan'] is None
 assert manifest['intent_scope']['semantic_source_sha256']=='f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae'
 assert manifest['state']=='ADAPTER_NEUTRAL_INTENT_NOT_FROZEN_BENCHMARK_BUNDLE'
 review=json.loads((ROOT/'experiments/reviews/g07-fictional-proxy-xinsir-replication-review-v1.json').read_text())
 assert review['manifest']['record_id']==manifest['record_id'] and review['decision']['accepted'] is False
 assert review['review']['human_minutes'] is None and review['intent_reference']['proxy_only'] is True
 for record in review['execution_records']:
  assert sha(ROOT/record['path'])==record['sha256']
 bundle=json.loads((ROOT/'experiments/benchmark-case-bundles/benchmark-case-bundle-v1.json').read_text())
 assert bundle['record_type']=='BenchmarkCaseBundle' and bundle['state']=='DRAFT_ADAPTER_SPECIFIC_G07_CONTROLS_NOT_FROZEN'
 assert bundle['semantic_source']['sha256']=='f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae'
 assert bundle['semantic_source']['mutation']=='none' and bundle['scope']['case_ids']==['G07a','G07b']
 assert bundle['intent_manifest']['sha256']==sha(manifest_path)
 assert 'No frozen executable harness.' in bundle['prohibited_claims']
 lint=json.loads((ROOT/'experiments/results/chapter_lint_ch01_research_edition_001.json').read_text())
 assert lint['record_type']=='ChapterLintRecord' and lint['edition_id']==edition['edition_id']
 assert lint['summary']['fail']==0 and lint['summary']['not_assessable']==1 and lint['summary']['advisory']==1
 assert lint['summary']['gating'] is False
 ch02_story=json.loads((ROOT/'production/canon/story-state/ch02-sc01-v1.json').read_text())
 ch02_assets=json.loads((ROOT/'production/assets/asset-registry-ch02-v1.json').read_text())
 ch02_beat=json.loads((ROOT/'production/scene-beats/ch02-sc01-treeline-return-v1.json').read_text())
 ch02_plans=json.loads((ROOT/'production/comic/ch02-sc01-panel-plans-v1.json').read_text())
 ch02_assertions=json.loads((ROOT/'production/comic/hard-assertion-manifests/ch02-treeline-return-archival-review-v1.json').read_text())
 ch02_revisions=json.loads((ROOT/'production/comic/panel-revisions/ch02-sc01-historical-import-r1.json').read_text())
 ch02_edition=json.loads((ROOT/'production/editions/north-garden-ch02-research-edition-001.json').read_text())
 ch02_records=json.loads((ROOT/'experiments/records/historical_legacy_duo2/ch02-treeline-return-r1.json').read_text())
 ch02_review=json.loads((ROOT/'experiments/reviews/ch02-treeline-return-archival-review-v1.json').read_text())
 assert ch02_story['record_id']==ch02_assets['story_state_id']==ch02_beat['story_state_id']==ch02_plans['story_state_id']
 assert ch02_plans['medium']=='comic' and ch02_plans['animation_shot_plan'] is None
 assert {plan['spatial_mode'] for plan in ch02_plans['plans']}=={'2d_only'}
 ch02_asset_ids={asset['asset_id'] for asset in ch02_assets['assets']}
 assert all(set(plan['asset_ids'])<=ch02_asset_ids and plan['spatial_stage_contract_id'] is None for plan in ch02_plans['plans'])
 assert ch02_assertions['state']=='ARCHIVAL_REVIEW_INTENT_RECONSTRUCTED_NOT_PRERENDER'
 assert ch02_assertions['animation_shot_plan'] is None and 'No Stage-A/Stage-B benchmark claim.' in ch02_assertions['prohibited_inferences']
 ch02_panel_ids={plan['panel_id'] for plan in ch02_plans['plans']}
 assert {revision['panel_id'] for revision in ch02_revisions['revisions']}==ch02_panel_ids
 assert all(sha(ROOT/revision['asset_path'])==revision['sha256'] for revision in ch02_revisions['revisions'])
 records_by_id={record['record_id']:record for record in ch02_records}
 assert all(record['provenance_state']=='HISTORICAL_EMBEDDED_WORKFLOW_AVAILABLE' for record in records_by_id.values())
 for revision in ch02_revisions['revisions']:
  reference=revision['render_record'].split('#',1)
  assert reference[0]=='experiments/records/historical_legacy_duo2/ch02-treeline-return-r1.json'
  assert records_by_id[reference[1]]['candidate']['sha256']==revision['sha256']
 assert ch02_edition['comic_plan_collection']==ch02_revisions['comic_plan_collection']
 assert set(ch02_edition['selected_panel_revision_ids'])=={revision['panel_revision_id'] for revision in ch02_revisions['revisions']}
 assert sha(ROOT/ch02_review['manifest']['path'])==ch02_review['manifest']['sha256']
 assert sha(ROOT/ch02_review['execution_records'][0]['path'])==ch02_review['execution_records'][0]['sha256']
 assert ch02_review['review']['human_review_status']=='not_yet_performed' and ch02_review['review']['human_minutes'] is None
 assert all(panel['decision']=='INTERNAL_RESEARCH_SELECT' and all(value=='pass' for value in panel['assertions'].values()) for panel in ch02_review['selected_panels'])
 assert sha(ROOT/ch02_review['rejected_candidate']['path'])==ch02_review['rejected_candidate']['sha256']
 assert 'subject_misclassification' in ch02_review['rejected_candidate']['failure_tags']
 print('0 failures, 0 warnings')
if __name__=='__main__': main()
