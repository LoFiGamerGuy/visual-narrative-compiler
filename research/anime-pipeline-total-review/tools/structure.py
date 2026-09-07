"""Read-only copy, geometry, source mapping and browser-scale measurements."""
import collections,json,re,statistics,xml.etree.ElementTree as ET
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];BASE=OUT.parents[2]
def dist(values):
    return {'n':len(values),'min':min(values),'median':statistics.median(values),'max':max(values)} if values else {'n':0,'min':None,'median':None,'max':None}
def words(text):return re.findall(r"[\w]+(?:['’][\w]+)?",text)
def svg(path,width):
    root=ET.fromstring(path.read_text());view=[float(x) for x in root.attrib['viewBox'].split()];texts=[e for e in root.iter() if e.tag.split('}')[-1]=='text'];sizes=[];copy=[]
    for t in texts:
        copy.append(' '.join(t.itertext()));fs=t.attrib.get('font-size')
        if fs:sizes.append(float(fs)*width/view[2])
    return {'text_elements':len(texts),'words':sum(len(words(t)) for t in copy),'copy':copy,'displayed_type_px':sizes,'min_type_px':min(sizes) if sizes else None}
def run():
    records={}
    for key,tree in [('premium','anime-pipeline-ember-lattice-premium-rd-20260904-150943'),('editorial','anime-pipeline-ember-lattice-editorial-gear-20260904')]:
        root=BASE/tree;m=json.loads((root/'production/reimaginings/ember-lattice/premium-rd/ch01-manifest.json').read_text());rows=[]
        for p in m['panels']:
            ident=p['panel_id'];path=root/'docs/reimaginings/ember-lattice/premium-rd/panels/hybrid'/f'{ident}.svg';units=p['lettering_units'];boxes=[u['box'] for u in units if 'box'in u]
            rows.append({'panel_id':ident,'order':p['order'],'action_declared':p['action'],'density_declared':p['density'],'scenarios_declared':p['scenarios'],'unit_count':len(units),'balloons':sum(u['kind']not in ['ui','open','sfx'] for u in units),'ui_units':sum(u['kind']=='ui' for u in units),'sfx_units':sum(u['kind']=='sfx' for u in units),'authored_rectangle_area_pct_sum':round(100*sum((b[2]-b[0])*(b[3]-b[1]) for b in boxes),3),'nominal390':svg(path,390),'at362':svg(path,362),'at347_stress':svg(path,347)})
        records[key]={'panels':rows,'summary':{'panels':len(rows),'action_declared':sum(r['action_declared']for r in rows),'silent_panels':sum(r['unit_count']==0 for r in rows),'total_units':sum(r['unit_count']for r in rows),'total_words':sum(r['nominal390']['words']for r in rows),'words_per_panel':dist([r['nominal390']['words']for r in rows]),'balloons_per_panel':dist([r['balloons']for r in rows]),'authored_area_pct':dist([r['authored_rectangle_area_pct_sum']for r in rows]),'actual_svg_type_at362px':dist([s for r in rows for s in r['at362']['displayed_type_px']]),'planned_density':dict(collections.Counter(r['density_declared']for r in rows))}}
    vroot=BASE/'anime-pipeline-litrpg-manhwa-20260904-001211';chapters=[]
    for c in range(1,11):
        plans=json.loads((vroot/f'production/reimaginings/ember-lattice/volume/chapters/ch{c:02}/comic-panel-plans.json').read_text())['panels'];copies=json.loads((vroot/f'production/reimaginings/ember-lattice/volume/chapters/ch{c:02}/lettering-copy.json').read_text())['panel_units'];panels=[]
        for p in plans:
            units=copies.get(p['panel_id'],[]);panels.append({'panel_id':p['panel_id'],'camera_declared':p['camera'],'beat':p['beat'],'density_declared':p['density'],'action_declared':p['action'],'units':len(units),'dialogue_words_authored':sum(len(words(u.get('text','')))for u in units if u.get('kind')=='dialogue'),'all_authored_words':sum(len(words(u.get('text','')+' '+' '.join(u.get('lines',[]))))for u in units),'svg_at390':svg(vroot/f'docs/reimaginings/ember-lattice/volume/chapters/ch{c:02}/panels/p{p["order"]:03}.svg',390)})
        chapters.append({'chapter':c,'panels':panels})
    records['volume']={'chapters':chapters,'warning':'Camera tags are authored declarations, not visual shot classification; first establishing beat is labelled expressive mature close-up. No inferred actual shot histogram.'}
    browser=json.loads((OUT/'evidence/reader-browser-mobile-qa.json').read_text());replacement=OUT/'evidence/reader-browser-mobile-editorial-recheck.json'
    b=browser['results'];
    if replacement.exists():
        new=json.loads(replacement.read_text())['results'];b=[r for r in b if r['id']not in {n['id']for n in new}]+new
    browser_summary=[]
    for r in b:
        o=r['observed'];fig=o['figures'];images=o['images'];existing={Path(i['src'].replace('file://',''))for i in images if i['src'].startswith('file://')};size=sum(p.stat().st_size for p in existing if p.exists());tops=[f['top'] for f in fig];pitch=[y-x for x,y in zip(tops,tops[1:])];gutters=[fig[i+1]['top']-f['top']-f['height']for i,f in enumerate(fig[:-1])]
        browser_summary.append({'id':r['id'],'viewport':r['viewport'],'content_width':o['documentWidth'],'scroll_height':o['scrollHeight'],'viewports_to_scroll':round(o['scrollHeight']/r['viewport']['height'],2),'panel_pitch_csspx':dist(pitch),'inter_figure_gap_csspx':dist(gutters),'image_widths':sorted(set(i['width']for i in images)),'image_heights':dist([i['height']for i in images]),'unique_addressed_image_bytes':size,'unique_addressed_images':len(existing),'decoded_image_count':sum(i['complete']and i['naturalWidth']>0 for i in images),'pending_image_count':sum(not i['complete']for i in images),'failed_image_count':sum(i['complete']and not i['naturalWidth']for i in images),'note':'Local filesystem bytes of directly addressed images; not measured network transfer or decode memory. SVG nested external art may not render despite a naturalWidth. Raster strip wrappers do not expose panel DOM gaps.'})
    report={'schema':'StructureReview/1','method':'SVG text content and numeric font-size from actual shipped overlays, scaled by displayed panel width. Areas are SUM of authored bounding rectangles (can double-count overlap); not occupied glyph/balloon pixel area. Action/density/camera labels are declarations only. Browser dimensions from corrected true mobile sessions.','records':records,'browser':browser_summary,'not_measured':{'actual_pose_repetition':'dHash is not a pose detector; visual observations bounded to samples','actual_shot_frequency':'Metadata camera/scenario declarations conflict with visible shots; no full corpus manual coding performed','true_text_area_pixels':'Vector balloon/glyph pixel segmentation not performed; authored area and visible clipping reported separately','reader_network_latency':'Local cached files only; no throttled device/network benchmark','human_correction_time':'No attributable human timers for this audit or sufficient historical successful-sequence data','provider_generation_cost':'Unknown usage/backend metadata retained null; this audit incurred no paid calls','all_visual_continuity_error_rate':'No representative random sample or complete panel annotation; confirmed cases only','OCR_generated_text_contamination':'No corpus OCR; visible contamination/blank masks sampled and source failure records preserved'}}
    (OUT/'evidence/structural-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v['summary']for k,v in records.items()if 'summary'in v},indent=2))
if __name__=='__main__':run()
