"""Create synthetic proxy QA controls; never renderer outputs or benchmark cases."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'experiments/outputs/geometry_proxy_tiles_g07_v1/g07a-role-tiles-r1.png'
OUT=ROOT/'experiments/outputs/proxy_tile_qa_injections_v1'
def save(im,name): im.save(OUT/name)
def main():
 OUT.mkdir(parents=True,exist_ok=True); base=Image.open(SOURCE).convert('RGB')
 # Valid reference control.
 save(base,'g07a_valid_reference.png')
 # Swap expected orange/teal roles by copying their fixed marker regions.
 swapped=base.copy(); left=base.crop((300,405,445,565)); right=base.crop((775,405,920,565)); swapped.paste(right,(300,405)); swapped.paste(left,(775,405)); save(swapped,'g07a_inject_role_swap.png')
 # Remove expected right teal marker using the underlying geometry base crop.
 removed=base.copy(); raw=Image.open(ROOT/'experiments/outputs/geometry_proxy_g07_v1/g07a-geometry-base-r3.png').convert('RGB'); removed.paste(raw.crop((760,390,960,620)),(760,390)); save(removed,'g07a_inject_missing_teal.png')
 # Add a disconnected orange marker within left sensor ROI.
 dup=base.copy(); d=ImageDraw.Draw(dup); d.rectangle((445,445,485,500),fill=(230,135,35),outline=(42,42,42),width=4); save(dup,'g07a_inject_duplicate_orange.png')
 print(OUT)
if __name__=='__main__':main()
