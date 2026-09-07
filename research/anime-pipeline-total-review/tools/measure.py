"""Read-only measurements of protected comic outputs; writes only review evidence.

Run with PYTHONPATH=../.scratch/python python measure.py from this directory.
Pixel proxies use a 256x256 normalized grayscale thumbnail; never aesthetics scores.
"""
import base64, collections, hashlib, io, json, re, statistics, sys
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from PIL import Image, ImageFilter
import numpy as np

OUT = Path(__file__).resolve().parents[1]
BASE = OUT.parents[2]
TREES = {
 'legacy': BASE/'anime-pipeline',
 'borrowed': BASE/'anime-pipeline-reimagining-20260903',
 'city': BASE/'anime-pipeline-reimagining-clean-webtoon-20260903-213010',
 'ember_volume': BASE/'anime-pipeline-litrpg-manhwa-20260904-001211',
 'premium': BASE/'anime-pipeline-ember-lattice-premium-rd-20260904-150943',
 'editorial': BASE/'anime-pipeline-ember-lattice-editorial-gear-20260904',
}

def sha(data): return hashlib.sha256(data).hexdigest()
def leaf(path, seen=None):
    path=Path(path).resolve(); seen=set() if seen is None else seen
    if path in seen: raise ValueError('SVG image cycle')
    seen.add(path)
    if path.suffix.lower() != '.svg': return path, path.read_bytes()
    root=ET.fromstring(path.read_text())
    for elem in root.iter():
        if elem.tag.split('}')[-1]=='image':
            href=elem.attrib.get('href') or elem.attrib.get('{http://www.w3.org/1999/xlink}href')
            if not href: continue
            if href.startswith('data:'): return str(path)+'#inline',base64.b64decode(href.split(',',1)[1])
            if re.match(r'https?://',href): raise ValueError('Network images forbidden in local measurement')
            return leaf(path.parent/unquote(href),seen)
    raise ValueError('No raster image in SVG')

def image_metrics(data):
    with Image.open(io.BytesIO(data)) as im:
        size=list(im.size)
        gray=im.convert('L').resize((256,256),Image.Resampling.LANCZOS)
        a=np.asarray(gray,dtype=np.float32)
        med=np.asarray(gray.filter(ImageFilter.MedianFilter(3)),dtype=np.float32)
        d=np.asarray(gray.resize((9,8)),dtype=np.int16)
        bits=(d[:,1:]>d[:,:-1]).flatten()
        dh=sum(int(v)<<i for i,v in enumerate(bits))
        edge=np.maximum(np.abs(a[1:,:-1]-a[:-1,:-1]),np.abs(a[:-1,1:]-a[:-1,:-1]))
        return {'dimensions':size,'aspect':round(size[0]/size[1],4),
          'dark_pixel_pct':round(float((a<48).mean()*100),3),
          'midrange_pixel_pct':round(float(((a>=48)&(a<144)).mean()*100),3),
          'p90_p10_value_separation':round(float(np.percentile(a,90)-np.percentile(a,10)),3),
          'luminance_std':round(float(a.std()),3),'edge_over24_pct':round(float((edge>24).mean()*100),3),
          'median_filter_delta':round(float(np.abs(a-med).mean()),3),'dhash64':f'{dh:016x}'}

def summary(rows):
    valid=[r for r in rows if 'sha256' in r]; hashes=[r['sha256'] for r in valid]
    pairs=[]; affected=set()
    for i,a in enumerate(valid):
        for b in valid[i+1:]:
            if a['sha256']==b['sha256']:continue
            dist=(int(a['dhash64'],16)^int(b['dhash64'],16)).bit_count()
            if dist<=6:
                pairs.append({'a':a['id'],'b':b['id'],'distance':dist});affected.update([a['id'],b['id']])
    dimensions=collections.Counter('x'.join(map(str,r['dimensions'])) for r in valid)
    numeric=['dark_pixel_pct','midrange_pixel_pct','p90_p10_value_separation','luminance_std','edge_over24_pct','median_filter_delta']
    return {'positions':len(rows),'readable':len(valid),'missing_or_unresolved':len(rows)-len(valid),
      'unique_source_hashes':len(set(hashes)),'exact_reuse_positions':len(hashes)-len(set(hashes)),
      'exact_reuse_pct':round(100*(len(hashes)-len(set(hashes)))/len(hashes),3) if hashes else None,
      'near_duplicate_pairs_excluding_exact':pairs,'near_duplicate_affected_positions':len(affected),
      'dimensions':dict(dimensions),'source_bytes_with_reuse':sum(r['source_bytes'] for r in valid),
      'dark_frames_over60pct_dark_pixels':sum(r['dark_pixel_pct']>60 for r in valid),
      'proxy_distributions':{k:{'min':min(r[k] for r in valid),'median':statistics.median(r[k] for r in valid),'max':max(r[k] for r in valid)} for k in numeric} if valid else {}}

def run():
    groups={}
    for key,pattern in [('borrowed','experiments/reimaginings/borrowed-down/chapters/ch*/panels/*.png'),('city','experiments/reimaginings/the-city-keeps-oaths/chapters/ch*/panels/*.png'),('ember_volume','docs/reimaginings/ember-lattice/volume/chapters/ch*/panels/*.svg')]:
        groups[key]=[(str(p.relative_to(TREES[key])),p) for p in sorted(TREES[key].glob(pattern))]
    for key,filename,suffix in [('premium','benchmark-manifest.json','benchmark24'),('premium','ch01-manifest.json','unique52'),('editorial','ch01-manifest.json','editorial52')]:
        root=TREES[key];m=json.loads((root/'production/reimaginings/ember-lattice/premium-rd'/filename).read_text());assets={a['asset_id']:a for a in m['assets']}
        for route in ['baseline','raw','hybrid']:
            groups[suffix+'_'+route]=[(p['panel_id'],root/assets[p['variants'][route]]['path']) for p in m['panels']]
    groups['legacy_kitchen4']=[(f'p{i:02}',TREES['legacy']/f'pagecomp3/page03_p{i:02}.png') for i in [6,7,8,10]]
    results={};cache={}
    for group,paths in groups.items():
        rows=[]
        for ident,p in paths:
            row={'id':ident,'artifact':str(p)}
            try:
                source,data=leaf(p);h=sha(data)
                if h not in cache:cache[h]=image_metrics(data)
                row.update({'leaf_source':str(source),'sha256':h,'source_bytes':len(data),**cache[h]})
            except (OSError,ValueError,ET.ParseError) as e:row['error']=str(e)
            rows.append(row)
        results[group]={'summary':summary(rows),'panels':rows};print(group,len(rows),results[group]['summary']['unique_source_hashes'],flush=True)
    output={'schema':'TotalReviewMeasurements/1','source_root':str(BASE),'method':{'exact':'SHA256 of recursively resolved source raster, not SVG wrapper or lettering hash','near':'64-bit dHash <=6 Hamming, exact matches excluded; candidate flags require human confirmation, not identity or pose proof','pixel':'256x256 grayscale thumbnail, thresholds dark<48, mid48..143, edge>24. Resizing changes frequencies; dark/midrange and density are diagnostics, not beauty measures. Same algorithm for all sources.','scope':'All source-panel positions in three longform experiments, premium benchmark/52-panel manifests and four accepted-for-internal-research legacy kitchen panels. Further legacy mechanisms inventoried separately; no inference of complete lifetime output count.'},'groups':results}
    (OUT/'evidence/deterministic-measurements.json').write_text(json.dumps(output,indent=2)+'\n')

if __name__=='__main__':run()
