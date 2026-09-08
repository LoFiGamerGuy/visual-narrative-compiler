"""Build a self-contained guide; copy original images without transforming them."""
from pathlib import Path
import hashlib, html, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / 'docs/texture-refinement-kit'
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/c/AgentWorkspaces/anime-pipeline-nightglass-refinement-20260908-1015')
BASE = SOURCE / 'production/nightglass-refinement'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')

MASTER = '''Edit the attached source image. Use it as the sole visual reference and preserve its own drawing or painting treatment, aspect ratio, framing, subject identity, expression, pose, silhouettes, object construction, spatial relationships, palette and lighting mood.

Redraw the surface finish so the image feels calmer and more deliberate. Replace distracting repeated tiny marks with broad intentional light and shadow shapes inside the existing forms. Preserve depth, character appeal and differences between materials. Keep selective crisp accents on faces, important contours, meaningful seams and functional contacts. Keep purposeful environmental detail that explains the place and its scale.

Simplify excess scratches, chips, crack networks, tiny facets, equal-weight hair strands, speckles and scattered glitter wherever they compete with the focal subject. Preserve intentional brushwork and stylistic texture that give this particular artwork its character. Do not add ornament or new detail to compensate. This is a drawn or painted surface redraw, not blur, denoise, low resolution, airbrushing, glossy 3D rendering, flat vector art or empty minimalism.

Especially preserve: [name the features you love and must keep].
Focus the simplification on: [name the specific surfaces or effects that feel too busy].

Return one edited artwork, not a before/after composite. Do not add subjects, objects, text, labels or watermarks. Do not redesign the image.'''
ADAPTERS = [
('01', 'Standard pass', 'Start here; replace the two bracketed lines.', ''),
('02', 'Gentle pass', 'For a picture that is already close.', 'Use a gentle degree of simplification. Remove the most repetitive, distracting microtexture while retaining the existing modeling, stylistic brushwork and selected small details. Protect the richness of the image; avoid flattening areas that are already calm.'),
('03', 'Strong pass', 'For dense texture across many surfaces.', 'Make a substantial reduction in distracting small marks. Give most large forms calm interiors, expressed through connected light and shadow masses. Preserve meaningful contour changes, material boundaries, perspective and focal detail. Do not simply lower contrast, wash out colors, erase architecture or remove design features. More grouping must not mean less character.'),
('04', 'Faces, hair and clothing', 'Protect identity while simplifying strands and folds.', 'Keep the exact facial structure, age, expression, eye shape, hairline and hairstyle. Group hair into designed locks with selective strand accents. Keep clothing construction, tailoring and major tension folds; reduce repetitive little creases and all-over fabric noise. Preserve any emblem or purposeful pattern. Keep eyes and lips precisely drawn; no beauty filter, younger replacement face or plastic skin.'),
('05', 'Places and architecture', 'Keep an inhabited world with calmer surfaces.', 'Keep the camera, major buildings, paths, landmarks, vegetation masses and foreground-to-background depth. Group windows and reflected light into deliberate clusters separated by quiet areas. Describe stone with large planes and meaningful joints, foliage with coherent masses, and water with broad reflection bands. Retain enough specific detail to explain location, scale and weather. Do not erase the world or make every material smooth in the same way.'),
('06', 'Creatures', 'For wildlife, companions and monsters.', 'Keep the exact species design, anatomy, limb count, joints, grounded contacts, head and jaw construction, silhouette, pose and temperament. Group fur into directional masses or scales into broader material areas while retaining the boundaries that explain anatomy. Reduce repetitive cracks, facets and sparkle inside existing shapes. Preserve organic weight and distinctive features; do not turn the creature into a plastic toy or decorative mascot.'),
('07', 'Weapons and armor', 'For equipment whose design already works.', 'Preserve complete construction, length, thickness, scale, attachments, joints, grip and the relationship to the hand or body. Keep blade edges and functional seams crisp. Describe metal with a few broad reflections; simplify decorative scratches and etched noise that hide its shape. Keep meaningful wear, insignia and material differences. Do not change the mechanism, add ornament or invent new parts. This pass changes surfaces, not equipment design.'),
('08', 'Magic and weather', 'For readable action without particle storms.', 'Preserve the source, direction, target and consequence of the effect, and any protected or untouched area. Group dense particles, spray, snow or sparks into a coherent directional gesture with broad light and shadow shapes and selective edge accents. Keep the existing action and environmental depth legible. Do not let effects cover faces or contacts; do not replace a specific ability with a generic glowing aura. Preserve the source medium, avoiding graphic ribbons if they would conflict with its style.'),
('09', 'Book-cover artwork', 'Use on the art layer; keep typography in your layout.', 'Treat this as the illustration for an existing book cover. Preserve the current aspect ratio, crop, main subject placement, dramatic focal point, palette and existing quiet space for title and author lettering. Simplify distracting texture in that existing quiet space without adding new objects or redesigning the composition. Keep the source genre and drawing treatment; do not impose anime or any unrelated style. The supplied source is the artwork layer without cover lettering. Do not generate title, author name, logos or a new layout.'),
('10', 'Recover from over-smoothing', 'Reattach the ORIGINAL, not the over-smoothed result.', 'The previous attempt removed too much character. Restart from this attached ORIGINAL image and use a narrower surface edit. Preserve its distinctive brushwork, expressive contours, large folds, selected wear and separation between materials. Simplify only the explicitly named distracting repetitions. Keep sharp facial and functional details; retain the original contrast and depth. Do not polish everything, replace the face or turn cloth, stone and skin into one smooth material.')
]
prompts=[]
for num, title, use, adapter in ADAPTERS:
    body = MASTER + ('\n\nSpecific priority for this pass: ' + adapter if adapter else '') + '\n'
    filename=f'prompts/{num}.txt'
    write(KIT/filename, body)
    prompts.append(dict(id=num,title=title,use=use,path=filename,text=body))
write(KIT/'PROMPTS.txt', 'TEXTURE REFINEMENT — COPY ONE PROMPT PER REQUEST\nThese are reusable adaptations, not verbatim tested prompts. Replace brackets.\n\n' + '\n\n'.join(f'{p["id"]} — {p["title"]}\n{p["use"]}\n\n{p["text"]}' for p in prompts))
write(KIT/'skill/texture-refinement/references/master-prompt.txt', MASTER+'\n')

specs=[
('T01-P','City traversal','previous-world/images/S01.png','Broader paving reflections and calmer façades preserve the city’s depth.'),
('T02-P','Giant encounter','previous-world/images/S06.png','Reduced crack mosaics inside armor leave the enormous encounter readable.'),
('T03-P','Character','previous-world/images/C01.png','Grouped hair, cloth and background marks preserve the face and stance.'),
('T04-P','Creature','previous-world/images/M01.png','Broader dark plates reduce glitter. Some texture remains at the jaw and ground.'),
('S05-R1','Snow shelter','candidates/S05-P.png','A substantial reduction in snow flecks; the flowing weather becomes more stylized.')]
examples=[]
for attempt, title, before, observation in specs:
    call=json.loads((BASE/f'calls/{attempt}.json').read_text())
    assert len(call['references']) == 1
    assert call['references'][0]['sha256'] == sha(BASE/before)
    assert call['prompt_sha256'] == sha(BASE/f'prompts/{attempt}.txt')
    e=dict(attempt=attempt,title=title,observation=observation,files={})
    for role, src, dest in [
        ('before',BASE/before,f'examples/{attempt}-before.png'),
        ('after',BASE/f'candidates/{attempt}.png',f'examples/{attempt}-after.png'),
        ('prompt',BASE/f'prompts/{attempt}.txt',f'exact-tested-prompts/{attempt}.txt'),
        ('call',BASE/f'calls/{attempt}.json',f'provenance/{attempt}.json')]:
        (KIT/dest).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,KIT/dest)
        assert sha(src)==sha(KIT/dest)
        e['files'][role]=dict(path=dest,sha256=sha(src),source=str(src))
    examples.append(e)
write(KIT/'provenance/examples.json',json.dumps(dict(source_commit='83b06de9812176c8614fc6d09a058f5ff12a912b',experiment='NR-20260908-01',images_transformed=False,new_generations=0,examples=examples),indent=2)+'\n')
feedback={'date':'2026-09-08','scope':'Global texture-process preference; no individual ratings or canon assignments', 'quote':"yes yes yes absolutely yes, this is going so in the right direction. the texture change is a HUGE HUEG improvement, make suer we absolutely save and codify this process so tha twe can use it a tall tmies going forward. My wife would also like to replicate it with her work, can you put together a guide and list of prompts she could use to accomplish the same? She has source images she would like to run through that process."}
write(KIT/'provenance/owner-feedback.json',json.dumps(feedback,indent=2)+'\n')
evidence='''# Tested origin and limits

Source delivery: NR-20260908-01, commit 83b06de9812176c8614fc6d09a058f5ff12a912b. Built-in image generation, source-only edits. Model snapshot and seed were not exposed. Four controlled texture edits T01–T04 improved surface hierarchy; S05-R1 substantially simplified snow but made weather more stylized. These results support a preferred method, not guaranteed identity preservation or deterministic reproduction.

The owner explicitly endorsed the overall texture change on 2026-09-08 and asked for ongoing reuse. No per-image preference export was supplied with that endorsement. A04-R1 is a counterexample: surface relief did not fix incorrect shield mechanics. New-composition prompts alone continued to reintroduce texture.

Archived exact prompt hashes and source/return hashes:
'''
for e in examples:
    evidence+=f'\n## {e["attempt"]} — {e["title"]}\n'+''.join(f'- {role}: `{f["sha256"]}`\n' for role,f in e['files'].items() if role!='call')
    write(KIT/f'skill/texture-refinement/references/{e["attempt"]}.txt',(KIT/e['files']['prompt']['path']).read_text())
evidence+='\nExact tested prompts are included beside this file: T01-P.txt, T02-P.txt, T03-P.txt, T04-P.txt, S05-R1.txt. They contain historical subject and output-size constraints, not defaults for new source images. The portable guide includes the actual before/after images and unmodified call records. The master prompt is a newly written adaptation of those tested instructions.\n'
write(KIT/'skill/texture-refinement/references/evidence.md',evidence)

# Small Markdown subset sufficient for this authored guide; no network dependencies.
def inline(s): return __import__('re').sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',html.escape(s))
def guide_html(text):
    parts=[]
    for block in text.strip().split('\n\n'):
        if block.startswith('#'):
            line=block.splitlines()[0]; n=len(line)-len(line.lstrip('#')); parts.append(f'<h{n}>{inline(line[n:].strip())}</h{n}>')
        elif block.startswith('|'):
            rows=[r for r in block.splitlines() if not r.startswith('| ---')]
            parts.append('<div class="table-wrap"><table>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}>{inline(c.strip())}</{"th" if i==0 else "td"}>' for c in row.strip('|').split('|'))+'</tr>' for i,row in enumerate(rows))+'</table></div>')
        elif block.startswith('- '): parts.append('<ul>'+''.join('<li>'+inline(l[2:])+'</li>' for l in block.splitlines())+'</ul>')
        elif block.startswith('1. '): parts.append('<ol>'+''.join('<li>'+inline(l.split('. ',1)[1])+'</li>' for l in block.splitlines())+'</ol>')
        else: parts.append('<p>'+inline(block)+'</p>')
    return '\n'.join(parts)

cards=''
for p in prompts:
    cards+=f'<article id="prompt-{p["id"]}"><h3>{p["id"]} — {html.escape(p["title"])}</h3><p>{html.escape(p["use"])}</p><label for="text-{p["id"]}">Copy this prompt and replace the bracketed instructions</label><textarea id="text-{p["id"]}" spellcheck="false">{html.escape(p["text"])}</textarea><div class="actions"><button data-copy="text-{p["id"]}">Copy prompt {p["id"]}</button><a href="{p["path"]}" download>Download .txt</a></div></article>'
pairs=''
for e in examples:
    pairs+=f'<article id="example-{e["attempt"]}"><h3>{e["title"]}</h3><p>{e["observation"]}</p><div class="pair">'+''.join(f'<figure><a href="{e["files"][role]["path"]}" target="_blank" rel="noopener"><img loading="lazy" src="{e["files"][role]["path"]}" width="1536" height="1024" alt="{e["title"]}: {role} texture redraw"></a><figcaption>{role.title()} · open native image</figcaption></figure>' for role in ['before','after'])+f'</div><a href="{e["files"]["prompt"]["path"]}">Exact tested prompt: {e["attempt"]}</a></article>'
write(KIT/'index.html','''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Keep the image. Calm the texture.</title><link rel="stylesheet" href="style.css"></head><body><header><p class="eyebrow">A practical illustration finishing kit</p><p class="headline">Keep the image.<br>Calm the texture.</p><p>Preserve the character, atmosphere and story you love. Give the eye more room to enjoy them.</p><nav aria-label="Guide sections"><a href="#guide">Quick guide</a><a href="#prompts">10 prompts</a><a href="#examples">Before &amp; after</a><a href="PROMPTS.txt" download>All prompts .txt</a><a href="GUIDE.md" download>Guide .md</a></nav></header><main><section id="guide">'''+guide_html((KIT/'GUIDE.md').read_text())+'''</section><section id="prompts"><h2>Copy a prompt</h2><p>Attach your own original to your image editor. Choose one prompt. Replace the bracketed instructions; use the book-cover prompt on art without lettering. These are new reusable adaptations of the tested method.</p><p id="copy-status" role="status" aria-live="polite"></p>'''+cards+'''</section><section id="examples"><h2>Five real before-and-after examples</h2><p>Original native files, copied unchanged from the completed experiment. Each pair uses the before image as its sole edit reference. Open either image to inspect it at full size.</p>'''+pairs+'''</section><footer><p>Texture refinement kit · September 8, 2026 · No new artwork generated for this guide.</p><p><a href="provenance/examples.json">Source and prompt hashes</a> · <a href="skill/texture-refinement/SKILL.md">Reusable workflow skill</a> · <a href="provenance/owner-feedback.json">Process approval</a></p></footer></main><script src="app.js"></script></body></html>''')
write(KIT/'style.css','''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f1e9;color:#242c35;font:17px/1.65 system-ui,sans-serif}header{background:#152d3c;color:#f7f5ed;padding:52px max(24px,calc((100% - 1120px)/2))}header p{max-width:720px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;color:#a4d8d1}.headline{font:clamp(36px,6vw,64px)/1.1 Georgia,serif;margin:16px 0 24px}nav,.actions{display:flex;flex-wrap:wrap;gap:12px 22px}header a{color:#d0eee6}main{max-width:1168px;margin:auto;padding:28px 24px}section{scroll-margin-top:20px;margin-bottom:56px}#guide{max-width:850px}h1,h2,h3{font-family:Georgia,serif;line-height:1.2}h1{font-size:32px}h2{font-size:29px;margin-top:40px}h3{font-size:24px;margin:0 0 14px}a{color:#155b66;text-underline-offset:3px}a,button{touch-action:manipulation}nav a{padding:8px 0}p{margin:14px 0}li{padding-left:5px;margin:12px 0}article{background:#fffdf7;border:1px solid #d8dedb;border-radius:12px;padding:24px;margin:22px 0}textarea{width:100%;height:270px;display:block;border:1px solid #bac8c6;background:#f7f8f4;border-radius:6px;padding:15px;font:15px/1.6 ui-monospace,monospace;resize:vertical;color:#26323a;margin:10px 0 16px}label{font-size:14px}button{background:#155b66;color:white;border:0;border-radius:6px;padding:12px 18px;font:inherit;cursor:pointer}button:focus-visible,a:focus-visible,textarea:focus-visible{outline:3px solid #ce7b2e;outline-offset:4px}.actions{align-items:center}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:18px 0}figure{margin:0;min-width:0}img{display:block;width:100%;height:auto;border-radius:5px}figcaption{font-size:14px;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:15px}td,th{text-align:left;border-bottom:1px solid #ced7d2;padding:10px}.table-wrap{overflow-x:auto}footer{border-top:1px solid #ced7d2;font-size:14px;padding:20px 0}#copy-status{min-height:1.5em;color:#155b66}@media(max-width:650px){header{padding:32px 20px}main{padding:20px 16px}article{padding:16px}.pair{grid-template-columns:1fr;gap:10px}h1{font-size:28px}textarea{height:320px}}@media print{body{background:white;font-size:11pt}header{background:white;color:black;padding:0}header a{color:black}main{padding:0}nav,button,textarea,.actions,#copy-status{display:none}#prompts{display:none}.pair{grid-template-columns:1fr 1fr}article{break-inside:avoid;border:0}a{color:black}section{margin-bottom:20px}}''')
write(KIT/'app.js','''document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const field=document.getElementById(button.dataset.copy);field.focus();field.select();let copied=false;try{if(navigator.clipboard){await navigator.clipboard.writeText(field.value);copied=true}}catch{}if(!copied){try{copied=document.execCommand('copy')}catch{}}const message=copied?'Prompt copied. Replace the bracketed instructions before submitting.':'Text selected. Use your device’s Copy command; automatic copying is unavailable here.';document.getElementById('copy-status').textContent=message;button.textContent=copied?'Copied':'Selected — copy manually';button.setAttribute('aria-label',message)}));window.textureKitReady=true;''')
write(KIT/'OPEN_GUIDE.cmd','@echo off\nstart "" "%~dp0index.html"\n')
write(KIT/'START_HERE.txt','''TEXTURE REFINEMENT KIT

Extract the entire ZIP first. Open index.html in your browser, or double-click OPEN_GUIDE.cmd on Windows. The guide and examples work offline. This kit does not upload or edit your source images.

For the shortest route: read GUIDE.md, attach your own original artwork in an image editor that supports image-based edits, and copy Prompt 01 from PROMPTS.txt. Replace its bracketed lines. All ten prompts also have individual .txt files.

examples/ contains five actual before/after pairs at original native size.
exact-tested-prompts/ contains the five unmodified prompts that made those results.
provenance/ preserves source bindings, exact call records and the owner's process approval.
skill/texture-refinement/ contains the reusable agent workflow and supporting prompts.

The ten general-purpose prompts are newly adapted for your own source images; they have not all been separately image-tested. The method cannot guarantee identical output or exact identity preservation. Compare before accepting each result.
''')
write(ROOT/'research/texture-refinement-kit/source-baseline.json',json.dumps([f for e in examples for f in e['files'].values()],indent=2)+'\n')
print(json.dumps({'prompts':len(prompts),'example_pairs':len(examples),'native_images':len(examples)*2,'new_generations':0,'kit':str(KIT)}))
