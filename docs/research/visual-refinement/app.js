(() => {
  'use strict';
  const mode = document.body.dataset.mode, sequence = mode === 'sequence';
  const data = sequence ? window.VR_SEQUENCE_DATA : window.VR_COMPARISON_DATA;
  const $ = id => document.getElementById(id);
  const entries = new Map(data.entries.map(e => [e.id, e]));
  const styles = new Map((data.styles || []).map(s => [s.id, s]));
  const characters = new Map((data.characters || []).map(c => [c.id, c]));
  let activeCharacter = 'A', activeGroup = 'controlled', shortlistOnly = false, compareIDs = [];
  let activeStyle = data.styles?.[0]?.id, sequenceCompare = false, sequenceReview = false, store, zoomID, referenceID = null, repairID = null;
  const facetLabels = {character: ['Character appeal', 'Like', 'Pass'], style: ['Drawing treatment', 'Like', 'Pass'], readability: ['Easy to read', 'Clear', 'Hard to read'], comfort: ['Visual comfort', 'Comfortable', 'Straining']};
  function node(tag, className, text) { const e = document.createElement(tag); if (className) e.className = className; if (text !== undefined) e.textContent = text; return e; }
  function message(text, error = false) { $('message').hidden = !text; $('message').textContent = text; $('message').classList.toggle('error', error); }
  function sourceURL(path) { return '../../../' + path; }
  function title(entry) {
    if (entry.kind === 'sequence') return `${entry.panel_id} · ${styles.get(entry.style_id)?.title || entry.style_id}`;
    if (entry.kind === 'exploratory') return entry.title;
    return `${entry.style_id} · ${styles.get(entry.style_id)?.title || entry.title}`;
  }
  function shortName(entry) { return entry.kind === 'controlled' ? `${entry.style_id} / ${entry.character_id}` : entry.id; }
  function sync() {
    if (!store) return;
    document.querySelectorAll('[data-entry]').forEach(card => {
      if (store.isUnavailable(card.dataset.entry)) card.querySelectorAll('[data-shortlist],[data-response],[data-note],[data-compare]').forEach(control => { control.disabled = true; });
    });
    document.querySelectorAll('[data-shortlist]').forEach(b => {
      const id = b.dataset.shortlist, active = store.get(id).shortlist;
      b.setAttribute('aria-pressed', String(active)); b.textContent = active ? '✓' : '+';
      b.setAttribute('aria-label', `${active ? 'Remove' : 'Add'} new image ${id} ${active ? 'from' : 'to'} your shortlist`);
    });
    document.querySelectorAll('[data-response]').forEach(b => { const selected = store.get(b.dataset.id).responses[b.dataset.response]; b.setAttribute('aria-pressed', String(selected === b.dataset.value)); });
    document.querySelectorAll('[data-response-count]').forEach(e => {
      const c = store.get(e.dataset.responseCount), count = Object.values(c.responses).filter(v => v !== null).length;
      e.textContent = count ? `${count} of 4 responses recorded${c.note ? ' · Note saved' : ''}` : c.note ? 'Note saved · Responses still open' : 'New image · Not reviewed';
    });
    if ($('shortlist-count')) $('shortlist-count').textContent = Object.values(store.getAll()).filter(c => c.shortlist).length;
    if ($('compare-tray')) {
      $('compare-tray').hidden = compareIDs.length === 0;
      $('tray-label').textContent = compareIDs.length < 2 ? `${compareIDs[0]} selected · choose one more` : compareIDs.map(id => shortName(entries.get(id))).join(' · ');
      $('open-compare').disabled = compareIDs.length < 2;
      document.body.classList.toggle('has-compare', compareIDs.length > 0);
      document.querySelectorAll('[data-compare]').forEach(e => { e.checked = compareIDs.includes(e.dataset.compare); });
    }
  }
  function art(entry, targetHeight) {
    if (!entry.candidate) {
      const box = node('div', 'pending'); box.dataset.missing = entry.id;
      if (targetHeight) box.style.aspectRatio = `392/${targetHeight}`;
      box.append(node('strong', '', entry.id), node('span', '', 'Image not available yet'), node('span', '', 'No owner response assumed')); return box;
    }
    const b = node('button', 'image-button'); b.setAttribute('aria-label', `Open ${title(entry)} at full detail`);
    const img = node('img'); img.src = entry.candidate.src; img.width = entry.candidate.width; img.height = entry.candidate.height; img.loading = 'lazy'; img.decoding = 'async'; img.alt = `${title(entry)}${entry.character_id ? ', shared character ' + entry.character_id : ''}`;
    img.addEventListener('error', () => {
      const failure = node('div', 'image-failure'); failure.append(node('span', '', `${entry.id}: the selected image file is missing or unreadable. Restore this study's art bundle to view it.`));
      b.replaceWith(failure); store?.markUnavailable(entry.id); message(`Image ${entry.id} could not load. Your saved choices were not changed.`, true);
    });
    b.append(img); b.addEventListener('click', () => openZoom(entry.id)); return b;
  }
  function shortlistButton(entry) { const b = node('button', 'shortlist'); b.dataset.shortlist = entry.id; b.disabled = !entry.candidate; b.title = 'New image shortlist'; b.addEventListener('click', () => { store.update(entry.id, 'shortlist', !store.get(entry.id).shortlist); if (shortlistOnly) render(); }); return b; }
  function responseEditor(entry) {
    const editor = node('div', 'response-editor'); editor.hidden = true;
    for (const [key, [label, yes, no]] of Object.entries(facetLabels)) {
      const field = node('fieldset'); field.append(node('legend', '', label)); const options = node('div', 'response-options');
      for (const [value, text] of [['yes', yes], ['no', no], ['unsure', 'Unsure']]) {
        const b = node('button', '', text); b.dataset.id = entry.id; b.dataset.response = key; b.dataset.value = value; b.disabled = !entry.candidate;
        b.addEventListener('click', () => store.update(entry.id, key, store.get(entry.id).responses[key] === value ? null : value)); options.append(b);
      }
      field.append(options); editor.append(field);
    }
    const label = node('label', '', 'Keep this part, change that part…'), note = node('textarea'); note.maxLength = 4000; note.value = store.get(entry.id).note; note.disabled = !entry.candidate; note.dataset.note = entry.id; note.placeholder = 'Your own reaction or a short reason';
    note.addEventListener('input', () => store.update(entry.id, 'note', note.value)); label.append(note); editor.append(label); return editor;
  }
  function appendResponse(content, entry, allowCompare) {
    const tools = node('div', 'card-tools'), toggle = node('button', 'response-toggle', 'Your response'); toggle.setAttribute('aria-expanded', 'false');
    const editor = responseEditor(entry);
    toggle.addEventListener('click', () => { editor.hidden = !editor.hidden; toggle.setAttribute('aria-expanded', String(!editor.hidden)); });
    if (allowCompare) {
      const label = node('label', 'compare-check'), checkbox = node('input'); checkbox.type = 'checkbox'; checkbox.dataset.compare = entry.id; checkbox.disabled = !entry.candidate;
      checkbox.addEventListener('change', () => selectCompare(entry.id, checkbox.checked)); label.append(checkbox, document.createTextNode('Compare')); tools.append(label);
    } else tools.append(node('span', 'quiet', 'Response to this image'));
    tools.append(toggle); const count = node('p', 'response-count'); count.dataset.responseCount = entry.id;
    content.append(tools, count, editor);
  }
  function referenceDetails(entry) {
    const detail = node('details', 'source-details'); detail.append(node('summary', '', 'Brief & references'));
    if (entry.caption) detail.append(node('p', '', entry.caption));
    if (entry.character_id) detail.append(node('p', '', characters.get(entry.character_id)?.description || ''));
    const style = styles.get(entry.style_id);
    if (style?.reference?.path) { const link = node('a', '', `Original style reference ${style.id}`); link.href = sourceURL(style.reference.path); link.target = '_blank'; link.rel = 'noopener'; detail.append(link); }
    if (entry.candidate) { const link = node('a', '', 'Open this original image'); link.href = entry.candidate.src; link.target = '_blank'; link.rel = 'noopener'; detail.append(link); }
    if (style?.reference?.path && entry.candidate) {
      const button = node('button', 'reference-compare', 'Compare with original reference');
      button.addEventListener('click', () => openReference(entry.id)); detail.append(button);
    }
    if (entry.repair) { const button = node('button', 'reference-compare', 'View repair comparison'); button.addEventListener('click', () => openRepair(entry.id)); detail.append(button); }
    return detail;
  }
  function aiNotes(observations, label = 'AI visual observations') {
    const notes = node('details', 'ai-observations'); notes.append(node('summary', '', label));
    notes.append(node('p', 'quiet', 'AI observations, separate from your own response.'));
    const list = node('ul'); observations.forEach(text => list.append(node('li', '', text))); notes.append(list); return notes;
  }
  function card(entry, inCompare = false) {
    const box = node('article', 'card'); box.dataset.entry = entry.id; if (!inCompare) box.id = `image-${entry.id}`;
    box.append(art(entry)); const body = node('div', 'card-body'), head = node('div', 'card-head'), heading = node('div');
    heading.append(node('p', 'reference-label' + (entry.kind === 'exploratory' ? ' exploratory' : ''), entry.kind === 'controlled' ? `★ Previously starred reference ${entry.style_id}` : 'Exploratory mix · Separate from the controlled set'));
    heading.append(node(inCompare ? 'h3' : 'h2', '', title(entry)));
    heading.append(node('p', 'style-caption', entry.kind === 'controlled' ? `${characters.get(entry.character_id)?.title.split(' / ').at(-1)} · Reference: ${styles.get(entry.style_id)?.display_style || 'Drawing treatment'}` : entry.caption));
    head.append(heading, shortlistButton(entry)); body.append(head); appendResponse(body, entry, !inCompare); body.append(referenceDetails(entry));
    if (entry.ai_observations?.length) body.append(aiNotes(entry.ai_observations));
    box.append(body); return box;
  }
  function renderComparison() {
    if (repairID) return renderRepair();
    if (referenceID) return renderReference();
    $('compare-dialog').querySelector('.dialog-hint').textContent = 'Complete boards, matched viewing size. On a phone, comparisons stack vertically.';
    $('compare-stage').style.setProperty('--count', compareIDs.length);
    $('compare-stage').replaceChildren(...compareIDs.map(id => card(entries.get(id), true)));
    $('compare-title').textContent = activeGroup === 'controlled' ? `Character ${activeCharacter} · Same brief, different drawing` : 'Exploratory mixes'; sync();
  }
  function openComparison() { if (compareIDs.length < 2) return; referenceID = null; repairID = null; renderComparison(); $('compare-dialog').showModal(); $('compare-dialog').scrollTop = 0; }
  function renderReference() {
    const entry = entries.get(referenceID), style = styles.get(entry.style_id), original = node('article', 'card reference-card');
    const a = node('a', 'image-button'), img = node('img'); a.href = style.reference.src || sourceURL(style.reference.path); a.target = '_blank'; a.rel = 'noopener'; a.setAttribute('aria-label', `Open original starred reference ${style.id}`);
    img.src = a.href; img.width = style.reference.width; img.height = style.reference.height; img.alt = `Original starred ${style.id} ${style.title}; different character and world`; a.append(img); original.append(a);
    const body = node('div', 'card-body'); body.append(node('p', 'reference-label', `★ Previously starred reference ${style.id}`), node('h3', '', style.title), node('p', 'style-caption', 'Original cast and world. This is a drawing reference, not a controlled character pair.')); original.append(body);
    $('compare-title').textContent = 'Original reference and new result';
    $('compare-dialog').querySelector('.dialog-hint').textContent = 'The original has a different cast and world. Compare drawing choices here; use the controlled view to compare the shared character briefs.';
    $('compare-stage').style.setProperty('--count', 2); $('compare-stage').replaceChildren(original, card(entry, true)); sync();
  }
  function openReference(id) {
    const entry = entries.get(id); if (!entry?.candidate || !styles.get(entry.style_id)?.reference) return;
    referenceID = id; repairID = null; renderReference(); if (!$('compare-dialog').open) $('compare-dialog').showModal(); $('compare-dialog').scrollTop = 0;
  }
  function renderRepair() {
    const entry = entries.get(repairID), repair = entry.repair;
    $('compare-title').textContent = `Repair comparison · ${entry.id}`;
    $('compare-dialog').querySelector('.dialog-hint').textContent = `Hard failure targeted: ${repair.reason} ${repair.conditioning_notice}`;
    $('compare-stage').style.setProperty('--count', 2);
    $('compare-stage').replaceChildren(...[['before', 'Retained primary'], ['after', 'Selected retry']].map(([key, label]) => {
      const candidate = repair[key], box = node('article', 'card repair-card'); box.dataset.repairSide = key;
      const link = node('a', 'image-button'), img = node('img'); link.href = candidate.src; link.target = '_blank'; link.rel = 'noopener'; link.setAttribute('aria-label', `Open ${candidate.attempt_id} at native resolution`);
      img.src = candidate.src; img.width = candidate.width; img.height = candidate.height; img.alt = `${entry.id} ${label}, attempt ${candidate.attempt_id}`; link.append(img); box.append(link);
      const body = node('div', 'card-body'); body.append(node('h3', '', label), node('p', 'style-caption', candidate.attempt_id), node('p', 'repair-trace', `SHA-256 ${candidate.sha256}`));
      const native = node('a', 'repair-native', 'Open native image ↗'); native.href = candidate.src; native.target = '_blank'; native.rel = 'noopener'; body.append(native);
      if (key === 'after') { const record = node('a', 'repair-native', 'Repair source record'); record.href = sourceURL(repair.record_path); record.target = '_blank'; record.rel = 'noopener'; body.append(record, node('p', 'repair-trace', `Record SHA-256 ${repair.record_sha256}`)); }
      box.append(body); return box;
    }));
  }
  function openRepair(id) { if (!entries.get(id)?.repair) return; repairID = id; referenceID = null; renderRepair(); if (!$('compare-dialog').open) $('compare-dialog').showModal(); $('compare-dialog').scrollTop = 0; }
  function selectCompare(id, selected = true) {
    const entry = entries.get(id); if (!entry?.candidate || entry.kind !== activeGroup || entry.kind === 'controlled' && entry.character_id !== activeCharacter) return false;
    if (selected && !compareIDs.includes(id) && compareIDs.length >= 3) { message('Compare two or three images at once. Uncheck one to add another.'); sync(); return false; }
    compareIDs = selected ? [...new Set([...compareIDs, id])] : compareIDs.filter(x => x !== id); message(''); sync(); return true;
  }
  function setCharacter(id) {
    if (!characters.has(id)) throw Error('Unknown shared character');
    activeCharacter = id;
    compareIDs = compareIDs.map(old => `${entries.get(old).style_id}-${id}`).filter(next => entries.get(next)?.candidate);
    render();
  }
  function setGroup(group) { if (!['controlled', 'exploratory'].includes(group)) throw Error('Unknown comparison group'); activeGroup = group; compareIDs = []; render(); }
  function panelCard(entry, panel, comparative) {
    const box = node('article', 'card sequence-card'); box.dataset.entry = entry.id; box.id = `image-${entry.id}`;
    const header = node('div', 'card-body'); header.append(node('p', 'panel-marker', `${panel.id}${comparative ? ' · ' + styles.get(entry.style_id).title : ''}`)); box.append(header, art(entry, panel.target_height_at392));
    if (panel.copy?.length) {
      const strip = node('div', 'dialogue-strip');
      for (const copy of panel.copy) { const line = node('p', 'dialogue-line' + (copy.kind === 'sfx' ? ' sfx' : '')); line.dataset.copyId = copy.id; if (copy.speaker) line.append(node('span', '', copy.speaker)); line.append(document.createTextNode(copy.text)); strip.append(line); }
      box.append(strip);
    }
    const body = node('div', 'card-body review-tools'); body.hidden = !sequenceReview; appendResponse(body, entry, false);
    if (entry.ai_observations?.length) body.append(aiNotes(entry.ai_observations));
    if (entry.repair) { const button = node('button', 'reference-compare', 'View repair comparison'); button.addEventListener('click', () => openRepair(entry.id)); body.append(button); }
    box.append(body); return box;
  }
  function renderSequence() {
    const routeNotes = (data.route_observations || []).filter(r => sequenceCompare || r.style_id === activeStyle);
    $('route-observations').hidden = !routeNotes.length; $('route-observations').replaceChildren(...routeNotes.map(r => aiNotes(r.observations, `AI route observations · ${styles.get(r.style_id).title}`)));
    $('read-story').setAttribute('aria-pressed', String(!sequenceReview)); $('review-panels').setAttribute('aria-pressed', String(sequenceReview));
    $('sequence-switch').replaceChildren(...data.styles.map(s => { const b = node('button', '', s.title); b.setAttribute('aria-pressed', String(s.id === activeStyle)); b.addEventListener('click', () => { activeStyle = s.id; sequenceCompare = false; render(); }); return b; }));
    $('sequence-compare').setAttribute('aria-pressed', String(sequenceCompare));
    $('sequence-compare').disabled = data.styles.length !== 3;
    if (!data.styles.length) {
      const box = node('section', 'plan-placeholder'); box.append(node('h2', '', 'The story tests are being prepared.'), node('p', '', 'Three provisional drawing styles will receive the same six-panel story. No sequence art is available yet.'));
      if (data.panels?.length) { const detail = node('details'); detail.append(node('summary', '', 'Read the frozen dialogue')); for (const panel of data.panels) detail.append(node('p', '', `${panel.id} · ${(panel.copy || []).map(c => (c.speaker ? c.speaker + ': ' : '') + c.text).join(' / ') || 'Silent'}`)); box.append(detail); }
      $('stage').replaceChildren(box); return;
    }
    $('view-description').textContent = sequenceCompare ? 'The same panel in all three provisional treatments. Copy remains identical.' : `Provisional treatment: ${styles.get(activeStyle).title}. Read the same six-panel story, then record your own reactions.`;
    $('stage').classList.toggle('compare-sequence', sequenceCompare);
    if (sequenceCompare) {
      $('stage').replaceChildren(...data.panels.map(panel => {
        const group = node('section', 'sequence-group'); group.append(node('h2', '', panel.id)); const pair = node('div', 'sequence-pair'); pair.append(...data.styles.map(s => panelCard(entries.get(`${s.id}-${panel.id}`), panel, true))); group.append(pair); return group;
      }));
    } else $('stage').replaceChildren(...data.panels.map(p => panelCard(entries.get(`${activeStyle}-${p.id}`), p, false)));
    sync();
  }
  function render() {
    if (sequence) return renderSequence();
    $('controlled-tab').setAttribute('aria-pressed', String(activeGroup === 'controlled')); $('exploratory-tab').setAttribute('aria-pressed', String(activeGroup === 'exploratory'));
    $('cast-switch').hidden = activeGroup !== 'controlled';
    $('cast-switch').replaceChildren(...data.characters.map(c => { const b = node('button', '', `${c.id} · ${c.title.split(' / ').at(-1)}`); b.append(node('small', '', `Character retained from ${c.source_direction}`)); b.setAttribute('aria-pressed', String(c.id === activeCharacter)); b.addEventListener('click', () => setCharacter(c.id)); return b; }));
    $('shortlist-filter').setAttribute('aria-pressed', String(shortlistOnly));
    $('view-description').textContent = activeGroup === 'controlled' ? 'Same brief; framing, body and creature may drift. Compare with the original reference to inspect the drawing transfer.' : 'These two combinations explore retained character ideas. They are outside the controlled style comparison.';
    const visible = data.entries.filter(e => e.kind === activeGroup && (e.kind !== 'controlled' || e.character_id === activeCharacter) && (!shortlistOnly || store.get(e.id).shortlist));
    $('stage').replaceChildren(...visible.map(e => card(e))); $('empty').hidden = visible.length > 0; sync();
  }
  function openZoom(id) {
    const entry = entries.get(id); if (!entry?.candidate) return;
    zoomID = id; $('zoom-title').textContent = title(entry);
    const img = node('img'); img.src = entry.candidate.src; img.width = entry.candidate.width; img.height = entry.candidate.height; img.alt = `${title(entry)}, complete original art`;
    $('zoom-stage').replaceChildren(img); $('zoom-stage').classList.remove('native'); $('zoom-stage').scrollTo(0, 0); $('native-link').href = entry.candidate.src; $('zoom-toggle').textContent = 'Native pixels'; $('zoom-toggle').setAttribute('aria-pressed', 'false');
    if (!$('zoom-dialog').open) $('zoom-dialog').showModal();
  }
  $('zoom-toggle').addEventListener('click', () => { const native = $('zoom-stage').classList.toggle('native'); $('zoom-toggle').setAttribute('aria-pressed', String(native)); $('zoom-toggle').textContent = native ? 'Fit full image' : 'Native pixels'; $('zoom-stage').scrollTo(0, 0); });
  document.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => $(b.dataset.close).close()));
  document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; const top = $('zoom-dialog').open ? $('zoom-dialog') : $('compare-dialog')?.open ? $('compare-dialog') : null; if (top) { e.preventDefault(); top.close(); } });
  if (data.plan_pending) {
    $('export').disabled = true; $('import').disabled = true; $('sequence-compare').disabled = true;
    renderSequence(); $('availability').textContent = 'Sequence plan and art pending';
    window.RefinementApp = Object.freeze({ready: true, getState: () => ({mode, plan_pending: true})}); return;
  }
  store = window.RefinementPreferences(data, sync);
  $('study-link').hidden = !data.study_details_available;
  $('results-link').hidden = !data.results_available;
  if (data.results_available) $('results-link').href = '../../../research/visual-refinement/RESULTS.md';
  if (data.study_details_available) $('study-link').href = '../../../research/visual-refinement/START_HERE.md';
  $('availability').textContent = `${data.available_count}/${data.total_count || 18} ${sequence ? 'sequence panels' : 'comparison images'} available`;
  if (sequence) {
    $('sequence-compare').addEventListener('click', () => { sequenceCompare = !sequenceCompare; render(); });
    $('read-story').addEventListener('click', () => { sequenceReview = false; render(); });
    $('review-panels').addEventListener('click', () => { sequenceReview = true; render(); });
  }
  else {
    $('controlled-tab').addEventListener('click', () => setGroup('controlled')); $('exploratory-tab').addEventListener('click', () => setGroup('exploratory'));
    $('shortlist-filter').addEventListener('click', () => { shortlistOnly = !shortlistOnly; render(); }); $('clear-compare').addEventListener('click', () => { compareIDs = []; sync(); }); $('open-compare').addEventListener('click', openComparison);
  }
  $('export').addEventListener('click', () => {
    store.save(); const blob = new Blob([JSON.stringify(store.exportChoices(), null, 2) + '\n'], {type: 'application/json'}), url = URL.createObjectURL(blob), a = node('a');
    a.href = url; a.download = `refinement-${mode}-${data.dataset_sha256.slice(0, 10)}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); message('Your choices are exported. Keep this file to restore or share them.');
  });
  $('import').addEventListener('click', () => $('import-file').click());
  $('import-file').addEventListener('change', async e => { const file = e.target.files[0]; if (!file) return; try { if (file.size > 250000) throw Error('Choice file exceeds 250 KB.'); store.importChoices(JSON.parse(await file.text())); render(); if ($('compare-dialog')?.open) renderComparison(); message('Your choices are restored for these exact images.'); } catch (error) { message(error.message, true); } e.target.value = ''; });
  window.addEventListener('pagehide', () => store.save());
  render();
  window.RefinementApp = Object.freeze({ready: true, exportChoices: store.exportChoices,
    importChoices: draft => { store.importChoices(draft); render(); if ($('compare-dialog')?.open) renderComparison(); return true; }, validateChoices: store.validate, updateChoice: store.update,
    setCharacter, setGroup, selectCompare, openComparison, openReference, openRepair, openZoom,
    setSequenceStyle: id => { if (!styles.has(id)) throw Error('Unknown provisional style'); activeStyle = id; sequenceCompare = false; render(); },
    setSequenceReview: value => { sequenceReview = !!value; render(); },
    setSequenceCompare: value => { sequenceCompare = !!value; render(); },
    getState: () => ({mode, active_character: activeCharacter, active_group: activeGroup, active_style: activeStyle, sequence_compare: sequenceCompare, sequence_review: sequenceReview, compare_ids: [...compareIDs], dataset_sha256: data.dataset_sha256, choices: store.getAll(), storage: store.getStorage(), zoom_id: zoomID})});
})();
