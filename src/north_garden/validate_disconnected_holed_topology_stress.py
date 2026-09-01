"""Panel-neutral disconnected/ring-hole stress for inward boundary mechanics."""
from __future__ import annotations
import argparse, copy, hashlib, io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from validate_ch05_p036_mask_topology import components, inward_alpha

ROOT=Path(__file__).resolve().parents[2]
BOUNDARY=ROOT/"docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
SELECTOR=ROOT/"config/scale-aware-repair-boundary-selector-contract-r1.json"
REPORT=ROOT/"docs/research/evidence/disconnected-holed-mask-topology-stress-r1.json"
OUT=ROOT/"experiments/outputs/disconnected_holed_mask_topology_stress_r1"
WIDTHS=[2,4,6,8,10,12,16,20]

class StressError(RuntimeError): pass
def require(v,m):
    if not v: raise StressError(m)
def sha_bytes(v): return hashlib.sha256(v).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
def png_bytes(a):
    b=io.BytesIO(); Image.fromarray(a).save(b,format="PNG",compress_level=6); return b.getvalue()

def geometry():
    size=(480,640); ring_img=Image.new("L",(size[1],size[0]),0); draw=ImageDraw.Draw(ring_img)
    draw.ellipse((90,130,290,330),fill=255); draw.ellipse((145,185,235,275),fill=0)
    thin_img=Image.new("L",(size[1],size[0]),0); ImageDraw.Draw(thin_img).line((390,165,550,310),fill=255,width=32)
    ring=np.asarray(ring_img)>0; thin=np.asarray(thin_img)>0; support=ring|thin
    yy,xx=np.ogrid[:size[0],:size[1]]; hole=(xx-190)**2+(yy-230)**2 <= 45**2
    return support,ring,thin,hole

def build(write):
    boundary=json.loads(BOUNDARY.read_text(encoding="utf-8")); selector=json.loads(SELECTOR.read_text(encoding="utf-8"))
    require(boundary["decision"]["selected_compositor_policy"]=="cosine-inset-16px","boundary source changed")
    support,ring,thin,hole=geometry(); require(len(components(support))==2,"support not two components"); require(not (support&hole).any(),"hole not protected")
    variants=[]; alphas={}
    for width in WIDTHS:
        alpha,core=inward_alpha(support,width); alphas[width]=alpha
        nonzero=alpha>0
        row={"feather_width_px":width,"support_component_count":len(components(support)),"nonzero_alpha_component_count":len(components(nonzero)),"fully_replaced_core_component_count":len(components(core)),"fully_replaced_core_pixels":int(core.sum()),"fully_replaced_core_fraction":round(float(core.sum()/support.sum()),9),"ring_core_fraction":round(float((core&ring).sum()/ring.sum()),9),"thin_component_core_fraction":round(float((core&thin).sum()/thin.sum()),9),"hole_nonzero_alpha_pixels":int((nonzero&hole).sum()),"exterior_nonzero_alpha_pixels":int((nonzero&~support).sum())}
        row["qualifies"]=row["nonzero_alpha_component_count"]==2 and row["fully_replaced_core_component_count"]==2 and row["ring_core_fraction"]>=.15 and row["thin_component_core_fraction"]>=.15 and row["hole_nonzero_alpha_pixels"]==0 and row["exterior_nonzero_alpha_pixels"]==0
        variants.append(row)
    passing=[x for x in variants if x["qualifies"]]; require(passing,"no passing width"); selected=max(passing,key=lambda x:x["feather_width_px"]); first_fail=next((x for x in variants if x["feather_width_px"]>selected["feather_width_px"] and not x["qualifies"]),None)
    support_bytes=png_bytes((support*255).astype(np.uint8)); alpha_bytes=png_bytes(np.rint(alphas[selected["feather_width_px"]]*255).astype(np.uint8))
    if write:
        OUT.mkdir(parents=True,exist_ok=True)
        for path,data in ((OUT/"disconnected-ring-thin-support-r1.png",support_bytes),(OUT/f"selected-{selected['feather_width_px']:02d}px-inward-alpha-r1.png",alpha_bytes)):
            if path.exists(): require(path.read_bytes()==data,f"existing output differs: {path.name}")
            else: path.write_bytes(data)
    base=np.zeros((*support.shape,3),dtype=np.uint8)+80; layer=base.copy(); layer[support]=[150,110,70]; alpha=alphas[selected["feather_width_px"]]
    comp=np.rint(base*(1-alpha[:,:,None])+layer*alpha[:,:,None]).astype(np.uint8)
    return {"record_type":"DisconnectedHoledMaskTopologyStress","schema_version":"1.0","record_id":"ng-disconnected-holed-mask-topology-stress-r1","state":"LOCAL_PANEL_NEUTRAL_MECHANICS_CONTROL_NOT_PRODUCTION_POLICY","sources":{"boundary":{"path":BOUNDARY.relative_to(ROOT).as_posix(),"sha256":sha(BOUNDARY)},"selector":{"path":SELECTOR.relative_to(ROOT).as_posix(),"sha256":sha(SELECTOR)}},"geometry":{"canvas_width":support.shape[1],"canvas_height":support.shape[0],"fixed_before_width_series":True,"support_components":2,"ring_outer_diameter_px":200,"ring_inner_hole_diameter_px":90,"ring_wall_px":55,"thin_component_width_px":32,"widths_px":WIDTHS,"selection_rule":"widest tested width retaining exactly two nonzero/core components, >=15% core in ring and thin component, exact protected hole and exterior"},"variants":variants,"decision":{"selected_width_px":selected["feather_width_px"],"selected_measurements":selected,"first_larger_failing_width_px":first_fail["feather_width_px"] if first_fail else None,"mechanics_control_pass":True,"panel_profile_created":False,"production_policy_created":False,"provider_route_changed":False},"outputs":{"support":{"path":f"experiments/outputs/disconnected_holed_mask_topology_stress_r1/disconnected-ring-thin-support-r1.png","sha256":sha_bytes(support_bytes)},"selected_alpha":{"path":f"experiments/outputs/disconnected_holed_mask_topology_stress_r1/selected-{selected['feather_width_px']:02d}px-inward-alpha-r1.png","sha256":sha_bytes(alpha_bytes)}},"validation":{"synthetic_composite_changed_pixels_outside_support":int(np.any(comp!=base,axis=2)[~support].sum()),"synthetic_composite_changed_pixels_inside_hole":int(np.any(comp!=base,axis=2)[hole].sum())},"review":{"human_review_status":"not_yet_performed","human_minutes":None,"accepted":False},"activity":{"provider_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"limitations":["Panel-neutral abstract geometry only; no ComicPanelPlan profile, mask, art, or upload authority.","One ring hole and two disconnected components do not establish arbitrary topology coverage.","Topology/core retention does not establish seam quality, causality, identity continuity, or narrative applicability.","The selected width is local to this exact geometry and cannot become a universal default."]}

def mutations(expected):
    vals=[]
    actions=[lambda x:x["geometry"].update(support_components=1),lambda x:x["geometry"].update(fixed_before_width_series=False),lambda x:x["geometry"]["widths_px"].remove(12),lambda x:x["decision"].update(selected_width_px=16),lambda x:x["decision"].update(panel_profile_created=True),lambda x:x["decision"].update(production_policy_created=True),lambda x:x["decision"]["selected_measurements"].update(hole_nonzero_alpha_pixels=1),lambda x:x["decision"]["selected_measurements"].update(fully_replaced_core_component_count=1),lambda x:x["validation"].update(synthetic_composite_changed_pixels_outside_support=1),lambda x:x["review"].update(human_minutes=1),lambda x:x["review"].update(accepted=True),lambda x:x["activity"].update(provider_requests=1)]
    for action in actions: item=copy.deepcopy(expected); action(item); vals.append(item)
    return sum(v!=expected for v in vals),len(vals)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--emit",type=Path); args=parser.parse_args()
    try:
        expected=build(True)
        if args.emit:
            target=args.emit if args.emit.is_absolute() else ROOT/args.emit; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
        else: require(json.loads(REPORT.read_text(encoding="utf-8"))==expected,"tracked stress report differs")
        rejected,total=mutations(expected); require(rejected==total,"mutation rejection incomplete")
    except (StressError,FileNotFoundError,KeyError,json.JSONDecodeError) as error:
        print(f"FAIL: {error}",file=sys.stderr); return 1
    s=expected["decision"]["selected_measurements"]
    print(f"0 failures, 0 warnings (2 disconnected components + protected hole; selected {s['feather_width_px']}px; ring/thin core {s['ring_core_fraction']:.3%}/{s['thin_component_core_fraction']:.3%})")
    print(f"exact hole/exterior; {rejected}/{total} mutations rejected; no profile/policy/review/request/upload/$0")
    return 0
if __name__=="__main__": raise SystemExit(main())
