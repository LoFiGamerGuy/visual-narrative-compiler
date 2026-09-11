"""Build editable, source-bound SVG composites from explicit local layers.

No generation, segmentation model, or hidden retouching. A spec lists local PNG
layers, optional SVG masks/paths, and explicit transforms in output pixels.
Every version gets a new spec/SVG/receipt; existing outputs are never replaced.
"""
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
import argparse, datetime, hashlib, json, os

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(spec_path):
 spec=json.loads(spec_path.read_text()); out=(ROOT/spec['output_svg']).resolve()
 if not out.is_relative_to(ROOT) or out.exists():raise ValueError('New output inside checkout required')
 width,height=spec['width'],spec['height'];inputs=[]
 body=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',f'<title>{escape(spec["id"])} — editable original scene composite</title>',f'<desc>{escape(spec.get("description","Unaccepted agent-authored conventional composite"))}</desc>',f'<rect width="{width}" height="{height}" fill="{escape(spec.get("matte","#faf7ec"))}"/>']
 if spec.get('defs_svg'):body.append('<defs>'+spec['defs_svg']+'</defs>')
 for layer in spec['layers']:
  body.append('<g id='+quoteattr(layer['id'])+' data-source-kind='+quoteattr(layer.get('kind','editable-layer'))+' transform='+quoteattr(layer.get('transform','translate(0 0)'))+(' clip-path='+quoteattr('url(#'+layer['clip']+')') if layer.get('clip') else '')+'>')
  if 'path' in layer:
   p=(ROOT/layer['path']).resolve()
   if not p.is_relative_to(ROOT) or not p.is_file():raise ValueError('Existing local layer required')
   digest=sha(p)
   if layer.get('sha256') and layer['sha256']!=digest:raise ValueError('Source layer hash changed')
   inputs.append({'id':layer['id'],'path':p.relative_to(ROOT).as_posix(),'sha256':digest,'transform':layer.get('transform'),'clip':layer.get('clip')})
   href=os.path.relpath(p,out.parent).replace(os.sep,'/')
   body.append('<image href='+quoteattr(href)+f' x="{layer.get("x",0)}" y="{layer.get("y",0)}" width="{layer.get("width",width)}" height="{layer.get("height",height)}" preserveAspectRatio="none"/>')
  if 'svg' in layer:body.append(layer['svg'])
  body.append('</g>')
 body.append('</svg>');out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(body)+'\n')
 receipt={'schema':'EditableComposite/1','id':spec['id'],'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'spec_path':spec_path.relative_to(ROOT).as_posix(),'spec_sha256':sha(spec_path),'svg_path':out.relative_to(ROOT).as_posix(),'svg_sha256':sha(out),'inputs':inputs,'generated_calls_for_this_composition':0,'attribution':'Agent-authored conventional compositing; not human artist labor','art_acceptance':None,'semantic_acceptance':None,'commercial_clearance':None,'limits':'Source hashes prove which layers were used; visible contact, occlusion, anatomy and appeal require actual-art review.'}
 out.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'svg':str(out),'inputs':len(inputs)}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('spec');a=ap.parse_args();build((ROOT/a.spec).resolve())
