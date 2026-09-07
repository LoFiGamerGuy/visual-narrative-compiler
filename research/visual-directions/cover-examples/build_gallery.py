from pathlib import Path
import json,html,hashlib,argparse
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'production/visual-directions/cover-examples'
D=ROOT/'docs/research/visual-directions/cover-examples'
parser=argparse.ArgumentParser();parser.add_argument('--require-complete',action='store_true');args=parser.parse_args()
data=json.loads((P/'concepts.json').read_text());images=json.loads((P/'images.json').read_text())['images'] if (P/'images.json').exists() else []
known={r['id']:r for r in images}
if args.require_complete:assert len(known)==10
for r in images:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
def esc(s):return html.escape(s,quote=True)
def cover(c):
 cid=c['id'];author_class='author dark-author' if cid=='05' else 'author'
 image=f'<img src="art-{cid}.png" alt="Text-free illustration for {esc(c["title"])}" width="1024" height="1536">' if cid in known else '<div class="pending">Illustration in progress</div>'
 return f'<div class="cover {c["tone"]}" id="cover-{cid}">{image}<div class="lettering"><div class="top"><p class="genre">{esc(c["genre"])}</p><h2>{esc(c["title"])}</h2></div><div class="{author_class}">AUTHOR NAME</div></div></div>'
cards=[]
for c in data['concepts']:
 cid=c['id'];cards.append(f'<article id="example-{cid}">{cover(c)}<div class="card-info"><span class="number">{cid}</span><div><h3>{esc(c["genre"])}</h3><p class="links"><a href="art-{cid}.png" target="_blank">Original art ↗</a> <a href="cover-{cid}.png" download>Cover PNG ↓</a></p></div></div><details><summary>Try a different title</summary><label>Title<input class="title-input" data-id="{cid}" value="{esc(c["title"])}" maxlength="100"></label><label>Title color<select class="tone-input" data-id="{cid}"><option value="pale" {"selected" if c["tone"]=="pale" else ""}>Dark lettering</option><option value="dark" {"selected" if c["tone"]=="dark" else ""}>Light lettering</option></select></label></details></article>')
head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Black Petal · Ten cover possibilities</title><link rel="stylesheet" href="style.css"></head>'
page=head+'<body><header><p class="eyebrow">BLACK PETAL / COVER STUDIES / 01—10</p><h1>Ten cover possibilities.</h1><p class="lede">Ten stories in Black Petal’s visual style.</p><p class="muted">Invented sample titles. Edit the lettering or view the art alone.</p><nav><a href="overview.html">All ten at a glance ↗</a><a href="START_HERE.txt">How to use these</a></nav></header><main><details class="edit-controls"><summary>Try your title &amp; author</summary><section class="controls" aria-label="Cover controls"><label>Author name<input id="author-input" value="AUTHOR NAME" maxlength="70"></label><button id="toggle-art" aria-pressed="false">Hide lettering</button><button id="save-page">Save edited page</button><p id="status" role="status">Edits stay on this page; save a copy to keep them.</p></section></details><div class="grid">'+''.join(cards)+'</div></main><footer>Original illustrations with editable sample lettering. Choose by number; these are examples for discussion.</footer><script src="app.js"></script></body></html>'
(D/'index.html').write_text(page)
overview=head+'<body class="overview"><header><p class="eyebrow">BLACK PETAL / COVER STUDIES</p><h1>Ten possible stories.</h1><p>Sample titles · Open the gallery to inspect the art or edit the lettering.</p><a href="index.html">Open the cover gallery ↗</a></header><main id="overview-sheet"><div class="sheet-grid">'+''.join(f'<a class="overview-item" href="index.html#example-{c["id"]}">{cover(c)}<p>{c["id"]} · {esc(c["genre"])}</p></a>' for c in data['concepts'])+'</div><p class="sheet-note">BLACK PETAL — TEN COVER EXAMPLES · Sample titles and author placeholders</p></main></body></html>'
(D/'overview.html').write_text(overview)
print(json.dumps({'available':len(known),'total':10,'index':str(D/'index.html')}))
