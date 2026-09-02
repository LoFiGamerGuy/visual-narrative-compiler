"""Build an offline, read-only-source CH05 owner decision worksheet with local draft export."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
INDEX_PACKET = ROOT / "experiments/review-packets/ch05-owner-review-index-r1/owner-review-index-packet.json"
OUT = ROOT / "experiments/review-packets/ch05-owner-decision-worksheet-r1"
INDEX = OUT / "index.html"
PACKET = OUT / "decision-worksheet-packet.json"

SUPPORT = {
    "sequence_departure_and_clue": "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-departure_and_clue.png",
    "sequence_bridge_to_mill": "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-bridge_to_mill.png",
    "sequence_signal_and_return": "experiments/review-packets/ch05-variable-cadence-assembly-r1/sequence-selected-signal_and_return.png",
    "variable_panel_cadence": "experiments/review-packets/ch05-variable-cadence-assembly-r1/ch05-variable-cadence-phone-scroll-390px-r1.png",
    "role_aware_cel_clear_line_route": "experiments/review-packets/ch05-continuity-style-density-r1/style-engineering-results-r1.png",
    "c005_dense_transition": "experiments/review-packets/ch05-continuity-style-density-r1/selected-phone-density-montage-r1.png",
    "c014_to_c015_action_punctuation": "experiments/review-packets/ch05-continuity-style-density-r1/sequence-appearance-jumps-r1.png",
    "translucent_88_balloon_arm": "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png",
    "light_outside_art_caption_band": "experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png",
    "dark_direct_gutter_text": "experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png",
}


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def href(path: Path) -> str: return Path(os.path.relpath(path, OUT)).as_posix()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")); index = json.loads(INDEX_PACKET.read_text(encoding="utf-8"))
    candidate_index = {item["candidate_id"]: item for item in index["candidates"]}
    subjects = []
    for subject in contract["subjects"]:
        item = dict(subject)
        candidate = candidate_index.get(subject["subject_id"])
        if candidate:
            item["thumbnail_href"] = href(ROOT / candidate["thumbnail_path"])
            item["support_href"] = href(ROOT / candidate["source_path"])
        else:
            support = ROOT / SUPPORT[subject["subject_id"]]
            if not support.is_file(): raise SystemExit(f"missing support artifact: {support}")
            item["thumbnail_href"] = None; item["support_href"] = href(support)
        subjects.append(item)
    embedded = json.dumps({"contract_id": contract["record_id"], "contract_sha256": sha(CONTRACT), "subjects": subjects}, separators=(",", ":")).replace("</", "<\\/")
    css = """body{margin:0;background:#10141a;color:#e8eaed;font:15px/1.45 system-ui,sans-serif}header,main{max-width:1500px;margin:auto;padding:24px}header{background:#171d25;border-bottom:1px solid #303844;position:sticky;top:0;z-index:3}h1,h2,h3{line-height:1.15}.boundary{color:#ffcf73}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center}input,select,textarea,button{font:inherit}input,select,textarea{background:#10161d;color:#edf0f3;border:1px solid #46515f;border-radius:7px;padding:8px}input{min-width:260px}button{background:#2b71ba;color:white;border:0;border-radius:8px;padding:10px 16px;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}.card{background:#19212b;border:1px solid #303a47;border-radius:12px;overflow:hidden}.card img{width:100%;height:280px;object-fit:contain;background:#11161d}.body{padding:14px}.meta{color:#aeb6c1}.allowed{font-size:12px;color:#8fa0b3}select,textarea{box-sizing:border-box;width:100%;margin-top:8px}textarea{min-height:72px}.done{border-color:#3c9a73}.summary{font-weight:700}.group{margin-top:42px}a{color:#89c8ff}code{font-size:12px}details{margin-top:12px}#status{color:#9fd8b8}footer{text-align:center;padding:45px;color:#8c96a2}"""
    script = """const model=JSON.parse(document.getElementById('model').textContent);const groups={};for(const s of model.subjects)(groups[s.subject_type]??=[]).push(s);const root=document.getElementById('root');const esc=x=>String(x).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));let decisions={};function refresh(){let n=Object.values(decisions).filter(x=>x.decision).length;document.getElementById('summary').textContent=`${n} / ${model.subjects.length} draft decisions selected`;document.getElementById('status').textContent=n?'Draft only — export does not change project evidence.':'No draft decisions selected.'}for(const [type,items] of Object.entries(groups)){const section=document.createElement('section');section.className='group';section.innerHTML=`<h2>${esc(type.replaceAll('_',' '))} <span class=meta>(${items.length})</span></h2><div class=grid></div>`;const grid=section.querySelector('.grid');for(const s of items){const card=document.createElement('article');card.className='card';const image=s.thumbnail_href?`<a href="${esc(s.support_href)}"><img src="${esc(s.thumbnail_href)}" alt="${esc(s.subject_id)}"></a>`:'';card.innerHTML=image+`<div class=body><h3>${esc(s.subject_id)}</h3><p><a href="${esc(s.support_href)}">open supporting artifact</a></p><p class=allowed>${esc(s.allowed_decisions.join(' · '))}</p><select><option value="">— pending —</option>${s.allowed_decisions.map(x=>`<option>${esc(x)}</option>`).join('')}</select><textarea placeholder="Optional review notes"></textarea></div>`;const select=card.querySelector('select'),notes=card.querySelector('textarea');const update=()=>{decisions[s.subject_id]={subject_id:s.subject_id,subject_type:s.subject_type,decision:select.value||null,notes:notes.value||null};card.classList.toggle('done',!!select.value);refresh()};select.onchange=update;notes.oninput=update;grid.appendChild(card)}root.appendChild(section)}document.getElementById('export').onclick=()=>{const reviewer=document.getElementById('reviewer').value.trim()||null;const chosen=Object.values(decisions).filter(x=>x.decision||x.notes);const draft={record_type:'ComicOwnerDecisionDraft',schema_version:'1.0',state:'LOCAL_UNINGESTED_DRAFT',contract_id:model.contract_id,contract_sha256:model.contract_sha256,reviewer,decisions:chosen,boundary:'Draft export only; not a hash-chained event, acceptance, plan revision, or project state.'};const blob=new Blob([JSON.stringify(draft,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='ch05-owner-decision-draft.json';a.click();URL.revokeObjectURL(a.href)};document.getElementById('clear').onclick=()=>{for(const el of document.querySelectorAll('select'))el.value='';for(const el of document.querySelectorAll('textarea'))el.value='';decisions={};for(const c of document.querySelectorAll('.card'))c.classList.remove('done');refresh()};refresh();"""
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner decision worksheet r1</title><style>{css}</style></head><body><header><h1>North Garden CH05 · owner decision worksheet r1</h1><p class="boundary"><strong>Offline draft tool:</strong> selections stay in this browser until you export JSON. Nothing is uploaded or written back to the repository.</p><div class="toolbar"><label>Reviewer <input id="reviewer" placeholder="name or handle (optional)"></label><button id="export">Export decision draft JSON</button><button id="clear">Clear draft</button><span id="summary"></span></div><p id="status"></p><details><summary>Contract boundary</summary><p>Contract <code>{html.escape(contract['record_id'])}</code> · <code>{sha(CONTRACT)}</code>. Exported JSON is an uningested draft, not a timed hash-chained review event, acceptance, commercial clearance, plan revision, or generation authority.</p></details></header><main id="root"></main><footer>39 exact pending subjects · local supporting artifacts only · no network code</footer><script id="model" type="application/json">{embedded}</script><script>{script}</script></body></html>'''
    OUT.mkdir(parents=True, exist_ok=True)
    with INDEX.open("w", encoding="utf-8", newline="\n") as handle: handle.write(page)
    packet = {"record_type":"CH05OwnerDecisionWorksheetPacket","schema_version":"1.0","record_id":"ng-ch05-owner-decision-worksheet-packet-r1","state":"OFFLINE_DRAFT_TOOL_READY_CONTRACT_UNCHANGED",
              "contract":{"path":CONTRACT.relative_to(ROOT).as_posix(),"sha256":sha(CONTRACT)},"review_index_packet":{"path":INDEX_PACKET.relative_to(ROOT).as_posix(),"sha256":sha(INDEX_PACKET)},
              "index":{"path":INDEX.relative_to(ROOT).as_posix(),"sha256":sha(INDEX),"bytes":INDEX.stat().st_size},"subject_count":len(subjects),"linked_candidate_count":29,"linked_higher_order_count":10,
              "network_calls":0,"uploads":0,"repository_writes_from_html":0,"decisions_recorded":0,"human_review_minutes":None,
              "boundary":"The worksheet exports an uningested local draft only; it cannot mutate the contract or project state."}
    with PACKET.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(packet,indent=2)+"\n")
    print(f"built offline owner decision worksheet: 39 subjects / 29 candidate links / 10 higher-order links; index {sha(INDEX)} packet {sha(PACKET)}")
    return 0


if __name__=="__main__":raise SystemExit(main())
