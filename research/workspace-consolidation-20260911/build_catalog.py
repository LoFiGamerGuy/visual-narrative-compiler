"""Build navigation and portable JSONL preservation mapping from the finished plan."""
import gzip
import html
import json
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENTRIES = [
 ('nightglass-longform','Nightglass — nine chapters','production/nightglass-longform/package/output/Nightglass-NineChapters-v1/START-HERE.html'),
 ('aws-editorial','AWS editorial study','research/aws-editorial-20260910/reader/index.html'),
 ('pilot-chapters','Independent pilot chapters','docs/pilot-chapters/index.html'),
 ('anchor-return','Anchor return','docs/anchor-return/index.html'),
 ('encounter-lab','Encounter lab','docs/encounter-lab/index.html'),
 ('impact-clarity','Impact clarity','docs/impact-clarity/index.html'),
 ('combat-depth','Combat depth','docs/combat-depth/index.html'),
 ('scale-conflict','Scale and conflict','docs/scale-conflict/index.html'),
 ('texture-kit','Texture refinement guide','docs/texture-refinement-kit/index.html'),
 ('nightglass-refinement','Nightglass refinement','docs/nightglass-refinement/index.html'),
 ('world-components','World components','docs/world-components/index.html'),
 ('world-combat','World combat','docs/world-combat/index.html'),
 ('combat-exploration','Combat exploration','docs/combat-exploration/index.html'),
 ('directions','Visual directions','docs/research/visual-directions/index.html'),
 ('refinement','Visual refinement','docs/research/visual-refinement/index.html'),
 ('structural','Structural pilot','docs/research/structural-pilot/index.html'),
 ('sequence-pilot','Sequence pilot','docs/research/sequence-pilot/index.html'),
 ('ember-lattice-editorial','Ember Lattice editorial and gear','docs/reimaginings/ember-lattice/premium-rd/benchmark-suite/index.html'),
 ('ember-lattice-premium','Ember Lattice premium research','docs/reimaginings/ember-lattice/premium-rd/index.html'),
 ('litrpg-manhwa','Ember Lattice volume','docs/reimaginings/ember-lattice/volume/index.html'),
 ('reimagining-clean','The City Keeps Oaths','docs/reimaginings/the-city-keeps-oaths/viewer.html'),
 ('reimagining-20260903','Borrowed Down','experiments/reimaginings/borrowed-down/START-HERE.html'),
 ('total-review','Pipeline review','docs/research/anime-pipeline-total-review/index.html'),
 ('reimagining','Legacy baseline','README_CODEX_BOOTSTRAP.md'),
]

def main():
    db = sqlite3.connect(HERE/'inventory.sqlite3')
    db.row_factory = sqlite3.Row
    workspaces = json.loads((HERE/'workspaces.json').read_text())
    snapshots = []
    for ws in workspaces:
        _,title,path = next(x for x in ENTRIES if x[0] in ws['name'])
        row = db.execute('SELECT destination FROM actions WHERE workspace=? AND path=?',(ws['name'],path)).fetchone()
        if not row:
            raise RuntimeError(f'Missing catalog entry: {ws["name"]}/{path}')
        snapshots.append(dict(name=ws['name'],title=title,path=path,branch=ws['branch'],commit=ws['head'],url='workspaces/'+ws['name']+'/'+path))
    (HERE/'catalog.json').write_text(json.dumps(snapshots,indent=2)+'\n')
    with gzip.open(HERE/'preservation-map.jsonl.gz','wt',encoding='utf-8') as stream:
        for row in db.execute('SELECT a.workspace,a.path,a.destination,a.action,a.sha,a.size,f.link FROM actions a JOIN files f USING(workspace,path) ORDER BY a.workspace,a.path'):
            stream.write(json.dumps(dict(row),separators=(',',':'))+'\n')
    cards=[]
    seen=set()
    for s in snapshots:
        if s['path'] in seen or s['title']=='Legacy baseline':
            continue
        seen.add(s['path'])
        cards.append(f'<a class="card" href="{html.escape(s["path"])}">{html.escape(s["title"])}</a>')
    history='\n'.join(f'<li><a href="{html.escape(s["url"])}">{html.escape(s["name"].removeprefix("anime-pipeline-"))}</a></li>' for s in snapshots)
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anime Pipeline Library</title><style>
body{margin:0;background:#11151c;color:#e6eaf0;font:17px/1.6 system-ui,sans-serif}main{max-width:1050px;margin:auto;padding:48px 24px}h1{font-size:2.5rem;line-height:1.15}h2{margin-top:2.5rem}a{color:#a2ceff}code{background:#242c37;padding:3px 6px;border-radius:4px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}.card{display:block;background:#202833;padding:20px;border:1px solid #354152;border-radius:9px;text-decoration:none}.card:hover{border-color:#a2ceff}li{margin:8px 0}.muted{color:#b5bfcc}
</style></head><body><main><p class="muted">One workspace · preserved production history</p><h1>Anime Pipeline Library</h1><p>Read the current work, explore independent projects, or revisit a preserved workspace.</p><p>For historical views and older cross-project links, launch <code>start-library.cmd</code> on Windows or run <code>python scripts/serve_library.py --open</code>.</p><h2>Readers and galleries</h2><div class="grid">'''+''.join(cards)+'''</div><h2>Preserved workspace views</h2><p class="muted">These views use the original files through the local library server. Shared files are stored once; differing versions remain available.</p><ul>'''+history+'''</ul><h2>Source and preservation</h2><p><a href="WORKSPACE-INDEX.md">Workspace guide</a> · <a href="research/workspace-consolidation-20260911/RESULT.md">Consolidation results</a> · <a href="research/nightglass-longform/FINAL-CHAPTER9-HANDOFF.md">Nightglass final handoff</a></p></main></body></html>'''
    (ROOT/'START-HERE.html').write_text(page,encoding='utf-8')
    rows='\n'.join(f'| {s["name"]} | `{s["branch"]}` | `{s["commit"][:12]}` |' for s in snapshots)
    guide='''# Consolidated anime-pipeline workspace

Open [START-HERE.html](START-HERE.html) for current readers and galleries. On Windows, double-click `start-library.cmd`. On Linux/WSL, run `python scripts/serve_library.py --open`. The local server also exposes exact historical workspace views and remaps old browser links without rewriting historical evidence.

All 26 former sibling workspaces are consolidated here. Their Git branches remain, and their unique local files are preserved. The current source includes Nightglass, both earlier independent stories, AWS editorial work, and both versions of the pipeline review.

| Location | Contents |
| --- | --- |
| `production/` | Current production sources, native art and releases |
| `docs/` | Readers, galleries and guides |
| `research/` | Experiments, prompts, reviews and evidence |
| `reimaginings/`, `src/`, `scripts/` | Story bibles and reusable source |
| `archive/workspace-variants/` | Conflicting historical file contents, stored once by SHA256 |
| `research/workspace-consolidation-20260911/` | Inventory, original branches, path mapping, execution and verification records |

The local `inventory.sqlite3` maps every original file to its retained destination. `preservation-map.jsonl.gz` is an independent, compressed JSONL export of that mapping. Each row includes the former workspace, original path, retained destination and SHA256. The archive and full local inventory remain outside public Git; Git is not a backup of ignored artwork.

For a historical file, query the mapping or open its `/workspaces/<old-folder>/<original-path>` URL through the library server. Historical absolute symlink targets (browser locks and security fixtures) are recorded unchanged and are not active runtime paths. Old execution receipts describe their original locations and are intentionally retained as evidence.

Avoid creating another permanent sibling checkout. Keep routine work in this consolidated tree. If concurrent work needs isolation, create a temporary worktree under `.worktrees/`, preserve its unique local output and retire it when finished. Do not merge independent story canon merely because its source shares a repository.

## Retained branches

| Former workspace | Branch | Original commit |
| --- | --- | --- |
'''+rows+'\n'
    (ROOT/'WORKSPACE-INDEX.md').write_text(guide,encoding='utf-8')
    print(f'Built catalog for {len(snapshots)} historical workspaces and {len(cards)} current entries.')

if __name__=='__main__':
    main()
