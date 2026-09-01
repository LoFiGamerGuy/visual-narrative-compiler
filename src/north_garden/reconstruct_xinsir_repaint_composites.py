"""Reconstruct uniquely named composites after an early filename-collision incident."""
from pathlib import Path
from PIL import Image
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png'
MASK=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-right-token-context-mask-v2-comfy-alpha.png'
RAW=ROOT/'ComfyUI/output/illustrious_xl_v2_xinsir_repaint_proxy_edit_v1'
OUT=ROOT/'experiments/outputs/illustrious_xl_v2_xinsir_repaint_proxy_edit_v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=Image.open(SRC).convert('RGB'); mask=Image.open(MASK).convert('L'); OUT.mkdir(parents=True,exist_ok=True); result={}
    for tag,raw_name in {'r3_edit':'g07a_seed7704_raw_00003_.png','r4_nochange':'g07a_seed7704_raw_00004_.png'}.items():
        raw=RAW/raw_name; out=OUT/f'{tag}-reconstructed-composite.png'; Image.composite(Image.open(raw).convert('RGB'),source,mask).save(out); result[tag]={'raw':raw.relative_to(ROOT).as_posix(),'raw_sha256':sha(raw),'composite':out.relative_to(ROOT).as_posix(),'composite_sha256':sha(out)}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
