"""Externalize inline PNG references into existing local source files, preserving pixels."""
from pathlib import Path
import json,hashlib,base64,re,os,datetime
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S';cache={}
for p in B.rglob('*.png'):
 if 'runtime' in p.relative_to(B).parts:continue
 cache.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),p)
pattern=re.compile(r'data:image/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=]+')
for panel,source_version,target_version in [('P09','F01-v4','F01-v4-portable'),('P14','F02-v5','F02-v5-portable')]:
 pre=B/panel/source_version;out=B/panel/target_version;out.mkdir();source=pre/(panel+'-'+source_version+'.spec.json');s=json.loads(source.read_text());mapping={};old=s['output_svg'];s['id']+='-portable';s['output_svg']=str((out/(panel+'-'+target_version+'.svg')).relative_to(R))
 def externalize(uri):
  data=base64.b64decode(uri.group().split(',',1)[1]);digest=hashlib.sha256(data).hexdigest();p=cache.get(digest)
  if p is None:raise ValueError('Inline raster has no existing source-bound local PNG: '+digest)
  href=os.path.relpath(p,out).replace(os.sep,'/');mapping[digest]={'source_png':str(p.relative_to(R)),'portable_href':href,'bytes':len(data)};return href
 for layer in s['layers']:
  if 'svg' in layer:layer['svg']=pattern.sub(externalize,layer['svg'])
 if s.get('defs_svg'):s['defs_svg']=pattern.sub(externalize,s['defs_svg'])
 target=out/(panel+'-'+target_version+'.spec.json');target.write_text(json.dumps(s,indent=2)+'\n')
 receipt={'schema':'RasterExternalization/1','panel':panel,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_spec':str(source.relative_to(R)),'source_spec_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_svg':old,'source_svg_sha256':hashlib.sha256((R/old).read_bytes()).hexdigest(),'source_png':str((pre/(panel+'-'+source_version+'.png')).relative_to(R)),'source_png_sha256':hashlib.sha256((pre/(panel+'-'+source_version+'.png')).read_bytes()).hexdigest(),'target_spec':str(target.relative_to(R)),'target_spec_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'external_rasters':mapping,'pixel_verification':'Pending portable render comparison','source_versions_modified':False}
 (out/'externalization-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(str(target.relative_to(R)),len(mapping))
