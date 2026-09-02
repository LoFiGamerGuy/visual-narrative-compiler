"""Build deterministic local P010-P013 review images after all four candidates exist."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BLUEPRINT=ROOT/"production/comic/review/ch05-p010-p013-prerender-packet-blueprint-r1.json"
def ignored(path): return subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT).returncode==0
def main():
    p=argparse.ArgumentParser(); p.add_argument("--dry-run",action="store_true"); a=p.parse_args()
    try: spec=json.loads(BLUEPRINT.read_text(encoding="utf-8")); from PIL import Image,ImageDraw,ImageFilter
    except (FileNotFoundError,json.JSONDecodeError,ImportError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    sources=[ROOT/x["expected_output_path"] for x in spec["candidate_slots"]]; outputs=[ROOT/x["path"] for x in spec["artifacts"]]; missing=[x for x in sources if not x.is_file()]
    if not all(ignored(x) for x in [*sources,*outputs]): print("FAIL: candidate/output path is not ignored",file=sys.stderr); return 1
    if a.dry_run:
        print(f"P010-P013 packet preflight PASS: {len(sources)} slots/{len(missing)} candidates missing; {len(outputs)} ignored outputs remain NOT_BUILT; no files written")
        return 0
    if missing:
        print(f"FAIL: {len(missing)}/4 candidates missing; packet not built",file=sys.stderr); return 1
    loaded=[Image.open(x).convert("RGB") for x in sources]; outroot=outputs[0].parent; outroot.mkdir(parents=True,exist_ok=True)
    def fit(im,w): return im.resize((w,int(im.height*w/im.width+0.5)),Image.Resampling.LANCZOS)
    def label(im,text):
        canvas=Image.new("RGB",(im.width,im.height+34),"white"); canvas.paste(im,(0,34)); ImageDraw.Draw(canvas).text((10,10),text,fill="black"); return canvas
    def stack(items,gap=18,bg="white"):
        w=max(x.width for x in items); h=sum(x.height for x in items)+gap*(len(items)-1); c=Image.new("RGB",(w,h),bg); y=0
        for x in items: c.paste(x,((w-x.width)//2,y)); y+=x.height+gap
        return c
    full=stack([label(fit(im,600),spec["candidate_slots"][i]["candidate_slot"]) for i,im in enumerate(loaded)]); full.save(outputs[0],optimize=False,compress_level=9)
    phone=stack([label(fit(im,390),spec["candidate_slots"][i]["candidate_slot"]+" phone") for i,im in enumerate(loaded)],12); phone.save(outputs[1],optimize=False,compress_level=9)
    seq=stack([fit(im,spec["candidate_slots"][i]["cadence_width_px"]) for i,im in enumerate(loaded)],24,"#ece8df"); seq.save(outputs[2],optimize=False,compress_level=9)
    overlays=[]
    for i,im in enumerate(loaded):
        view=fit(im,600).convert("RGBA"); zone=spec["candidate_slots"][i]["lettering_safe_zone_normalized"]; x0=round(zone[0]*view.width); y0=round(zone[1]*view.height); x1=round((zone[0]+zone[2])*view.width); y1=round((zone[1]+zone[3])*view.height); layer=Image.new("RGBA",view.size,(0,0,0,0)); draw=ImageDraw.Draw(layer); draw.rectangle((x0,y0,x1,y1),fill=(55,190,110,70),outline=(15,120,60,230),width=4); view=Image.alpha_composite(view,layer).convert("RGB"); overlays.append(label(view,spec["candidate_slots"][i]["candidate_slot"]+" proposed quiet zone"))
    stack(overlays).save(outputs[3],optimize=False,compress_level=9)
    density=[]
    for i,im in enumerate(loaded):
        g=fit(im,390).convert("L").filter(ImageFilter.FIND_EDGES); hist=g.histogram(); occupied=sum(v for level,v in enumerate(hist) if level>=32)/sum(hist); density.append(label(fit(im,390),f"{spec['candidate_slots'][i]['candidate_slot']} edge occupancy {occupied:.6f}"))
    stack(density).save(outputs[4],optimize=False,compress_level=9)
    print("P010-P013 packet built: 5 ignored local outputs; source pixels unchanged; no provider activity")
    return 0
if __name__=="__main__": raise SystemExit(main())
