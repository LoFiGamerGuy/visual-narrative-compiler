"""Build the fixed context mask for a fictional G07a right-token repair control."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png'
OUT=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-right-token-context-mask-v2-comfy-alpha.png'

def main():
    src=Image.open(SOURCE).convert('RGB')
    # ComfyUI LoadImage derives MASK as 1 - alpha. Its inpaint target must be
    # transparent, while the preserved exterior is opaque.
    mask=Image.new('RGBA',src.size,(0,0,0,255))
    ImageDraw.Draw(mask).polygon([(810,270),(1010,270),(1010,720),(810,720)],fill=(255,255,255,0))
    OUT.parent.mkdir(parents=True,exist_ok=True); mask.save(OUT)
    print(OUT)
if __name__=='__main__':main()
