"""Validate portable kitchen stage bootstrap invariants and draft control boundaries."""
import hashlib, json
from pathlib import Path
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path): return json.loads((ROOT/path).read_text())
def main():
 s1=read('production/stages/kitchen-table-canonical-geometry-bootstrap-v1.json'); p1=ROOT/s1['asset']['path']; n1={x[2:] for x in p1.read_text().splitlines() if x.startswith('o ')}
 assert s1['state']=='GEOMETRY_BOOTSTRAP_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART'
 assert {'Floor','BackWall','TableTop','TableLegs','Anchor_SOREN_LEFT_SEATED','Anchor_SIGRID_RIGHT_SEATED','Camera_Table_Seated_Reference'} <= n1
 assert s1['asset']['sha256']==sha(p1) and sha(ROOT/s1['blender_import']['blend_path'])==s1['blender_import']['blend_sha256']
 s2=read('production/stages/kitchen-table-canonical-geometry-bootstrap-v2.json'); p2=ROOT/s2['asset']['path']; n2={x[2:] for x in p2.read_text().splitlines() if x.startswith('o ')}
 assert s2['state']=='GEOMETRY_BOOTSTRAP_NEUTRAL_ANCHORS_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART'
 assert {'Floor','BackWall','TableTop','TableLegs','Anchor_Seated_World_X_NEG','Anchor_Seated_World_X_POS','Camera_Table_Seated_Reference'} <= n2
 assert s2['asset']['sha256']==sha(p2) and sha(ROOT/s2['blender_import']['blend_path'])==s2['blender_import']['blend_sha256']
 projection=read('production/stages/kitchen-table-world-to-comic-panel-projection-v1.json')
 assert projection['stage_id']==s2['record_id'] and projection['verified_projection']['screen_left']=='Anchor_Seated_World_X_POS'
 bundle=read('production/stages/controls/kitchen-table-blender-control-bundle-v2.json')
 assert bundle['state']=='DRAFT_STAGE_A_SEMANTIC_MAPPING_NOT_FROZEN' and bundle['source_authority']['stage_manifest'].endswith('bootstrap-v2.json')
 a=Image.open(ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png').convert('RGBA'); b=Image.open(ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-no-change-r1.png').convert('RGBA')
 assert ImageChops.difference(a,b).getbbox() is None
 print('0 failures, 0 warnings')
if __name__=='__main__': main()
