/* Local, source-bound preference workspace. No votes, ranking or acceptance state. */
(() => {
  'use strict';
  const data = window.VISUAL_DIRECTIONS_DATA;
  const facets = {character: 'Character', drawing_style: 'Drawing style', world: 'World', monster: 'Monster'};
  const $ = id => document.getElementById(id);
  const storageKey = `visual-directions:${data.experiment_id}:${data.dataset_sha256}`;
  const cardMap = new Map(data.cards.map(card => [card.id, card]));
  const blankPreferences = () => Object.fromEntries(data.cards.map(c => [c.id, {favorite: false, likes: Object.fromEntries(Object.keys(facets).map(k => [k, false])), notes: ''}]));
  let preferences = blankPreferences();
  let compareIDs = [];
  let shortlistOnly = false;
  let saveTimer;
  let zoomID;
  let storageAvailable = true;

  function element(tag, className, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function message(text, error = false) {
    $('message').hidden = !text;
    $('message').textContent = text;
    $('message').classList.toggle('error', error);
  }
  function exactKeys(object, keys, label) {
    if (!object || typeof object !== 'object' || Array.isArray(object) || Object.keys(object).sort().join('|') !== [...keys].sort().join('|')) throw Error(`Invalid ${label}.`);
  }
  function exportSelection() {
    return {schema: 'VisualDirectionSelection/1', experiment_id: data.experiment_id,
      dataset_sha256: data.dataset_sha256, concepts_sha256: data.concepts_sha256,
      experiment_sha256: data.experiment_sha256, exported_at: new Date().toISOString(),
      source_bindings: structuredClone(data.source_bindings), preferences: structuredClone(preferences)};
  }
  function validateSelection(draft) {
    exactKeys(draft, ['schema', 'experiment_id', 'dataset_sha256', 'concepts_sha256', 'experiment_sha256', 'exported_at', 'source_bindings', 'preferences'], 'selection envelope');
    for (const key of ['experiment_id', 'dataset_sha256', 'concepts_sha256', 'experiment_sha256']) if (draft[key] !== data[key]) throw Error('This selection belongs to a different or older image dataset. No preferences were changed.');
    if (draft.schema !== 'VisualDirectionSelection/1' || typeof draft.exported_at !== 'string' || !Number.isFinite(Date.parse(draft.exported_at))) throw Error('Invalid selection format.');
    if (!Array.isArray(draft.source_bindings) || draft.source_bindings.length !== 20) throw Error('All 20 source bindings are required.');
    draft.source_bindings.forEach((binding, i) => {
      exactKeys(binding, ['id', 'attempt_id', 'sha256'], 'source binding');
      for (const key of ['id', 'attempt_id', 'sha256']) if (binding[key] !== data.source_bindings[i][key]) throw Error('An image ID or source hash does not match this gallery.');
    });
    exactKeys(draft.preferences, data.cards.map(c => c.id), 'direction preferences');
    for (const [id, pref] of Object.entries(draft.preferences)) {
      exactKeys(pref, ['favorite', 'likes', 'notes'], 'preference');
      exactKeys(pref.likes, Object.keys(facets), 'component likes');
      if (typeof pref.favorite !== 'boolean' || Object.values(pref.likes).some(v => typeof v !== 'boolean') || typeof pref.notes !== 'string' || pref.notes.length > 4000) throw Error('Invalid preference value or note longer than 4,000 characters.');
      if (!cardMap.get(id).candidate && (pref.favorite || Object.values(pref.likes).some(Boolean) || pref.notes)) throw Error('Preferences cannot be assigned to a pending image.');
    }
    return structuredClone(draft.preferences);
  }
  function persist() {
    clearTimeout(saveTimer);
    try {
      localStorage.setItem(storageKey, JSON.stringify(exportSelection()));
      storageAvailable = true;
      $('save-status').textContent = 'Saved in this browser';
    } catch {
      storageAvailable = false;
      $('save-status').textContent = 'Browser storage unavailable · export to keep';
    }
  }
  function importSelection(draft) {
    const next = validateSelection(draft);
    preferences = next;
    persist();
    render();
    if ($('compare-dialog').open) renderComparison();
    message('Selections loaded for these exact images. Import replaces the previous selection in this browser.');
    return true;
  }
  function syncPreferences() {
    document.querySelectorAll('[data-favorite]').forEach(b => {
      const id = b.dataset.favorite, active = preferences[id].favorite;
      b.setAttribute('aria-pressed', String(active));
      b.textContent = active ? '★' : '☆';
      b.setAttribute('aria-label', `${active ? 'Remove' : 'Add'} ${id} ${cardMap.get(id).title} ${active ? 'from' : 'to'} shortlist`);
    });
    document.querySelectorAll('[data-facet]').forEach(b => b.setAttribute('aria-pressed', String(preferences[b.dataset.id].likes[b.dataset.facet])));
    $('favorite-count').textContent = Object.values(preferences).filter(p => p.favorite).length;
    $('mix-list').replaceChildren();
    for (const [key, title] of Object.entries(facets)) {
      const row = element('div', 'mix-row'), links = element('div');
      row.append(element('strong', '', title), links);
      const liked = data.cards.filter(c => preferences[c.id].likes[key]);
      if (!liked.length) links.append(element('span', 'none', 'Still open'));
      liked.forEach(c => { const a = element('a', '', `${c.id} ${c.title}`); a.href = `#direction-${c.id}`; a.addEventListener('click', () => { $('family').value = ''; shortlistOnly = false; render(); }); links.append(a); });
      $('mix-list').append(row);
    }
  }
  function toggleFavorite(id) {
    if (!cardMap.get(id)?.candidate) return;
    preferences[id].favorite = !preferences[id].favorite;
    persist();
    if (shortlistOnly) render(); else syncPreferences();
  }
  function toggleFacet(id, facet) {
    if (!cardMap.get(id)?.candidate || !Object.hasOwn(facets, facet)) return;
    preferences[id].likes[facet] = !preferences[id].likes[facet];
    persist(); syncPreferences();
  }
  function favoriteButton(card) {
    const b = element('button', 'favorite'); b.dataset.favorite = card.id;
    b.disabled = !card.candidate;
    b.addEventListener('click', () => toggleFavorite(card.id));
    return b;
  }
  function componentButtons(card) {
    const box = element('div', 'components'); box.setAttribute('role', 'group'); box.setAttribute('aria-label', `Components you like in direction ${card.id}`);
    for (const [key, label] of Object.entries(facets)) {
      const b = element('button', '', label); b.dataset.facet = key; b.dataset.id = card.id; b.disabled = !card.candidate;
      b.addEventListener('click', () => toggleFacet(card.id, key)); box.append(b);
    }
    return box;
  }
  function art(card) {
    if (!card.candidate) {
      const box = element('div', 'pending-art'); box.append(element('span', 'pending-number', card.id), element('p', '', 'Image pending'), element('p', '', 'No candidate selected yet')); return box;
    }
    const b = element('button', 'art-button'); b.setAttribute('aria-label', `Enlarge ${card.id} ${card.title}`);
    const img = element('img'); img.src = card.candidate.src; img.width = card.candidate.width; img.height = card.candidate.height; img.loading = 'lazy'; img.decoding = 'async'; img.alt = `${card.id} ${card.title}: adult character portrait and full-body concept, world and creature. ${card.style}.`;
    img.addEventListener('error', () => { b.classList.add('image-error'); message(`Image ${card.id} could not load. Restore its source file and rebuild the gallery.`, true); });
    b.append(img, element('span', 'zoom-label', 'View detail ↗')); b.addEventListener('click', () => openZoom(card.id)); return b;
  }
  function heading(card, comparison) {
    const head = element('div', 'card-head'), title = element('div'), line = element('div', 'title-line');
    line.append(element('span', 'number', card.id), element(comparison ? 'h3' : 'h2', '', card.title));
    title.append(line, element('p', 'style-name', card.style)); head.append(title, favoriteButton(card)); return head;
  }
  function renderCard(card, comparison = false) {
    const container = element(comparison ? 'div' : 'article', comparison ? 'compare-card' : 'card');
    if (!comparison) container.id = `direction-${card.id}`;
    container.dataset.direction = card.id;
    container.append(art(card));
    const content = element('div', 'card-content'); content.append(heading(card, comparison), element('p', 'component-label', 'What do you like?'), componentButtons(card));
    if (comparison) {
      if (preferences[card.id].notes) content.append(element('p', 'compare-note', preferences[card.id].notes));
    } else {
      const bottom = element('div', 'card-bottom');
      const label = element('label', 'compare-check'), input = element('input'); input.type = 'checkbox'; input.checked = compareIDs.includes(card.id); input.disabled = !card.candidate; input.dataset.compare = card.id;
      input.addEventListener('change', () => selectCompare(card.id, input.checked)); label.append(input, document.createTextNode('Compare'));
      const notesToggle = element('button', '', 'Notes & concept'); notesToggle.setAttribute('aria-expanded', 'false'); notesToggle.setAttribute('aria-controls', `notes-${card.id}`);
      bottom.append(label, notesToggle); content.append(bottom);
      const details = element('div', 'notes-wrap'); details.id = `notes-${card.id}`; details.hidden = true;
      notesToggle.addEventListener('click', () => { details.hidden = !details.hidden; notesToggle.setAttribute('aria-expanded', String(!details.hidden)); });
      const noteLabel = element('label', '', 'Your notes'), textarea = element('textarea'); textarea.value = preferences[card.id].notes; textarea.maxLength = 4000; textarea.disabled = !card.candidate; textarea.placeholder = 'What would you keep, change, or combine?'; textarea.dataset.notes = card.id;
      textarea.addEventListener('input', () => { preferences[card.id].notes = textarea.value; $('save-status').textContent = 'Saving…'; clearTimeout(saveTimer); saveTimer = setTimeout(persist, 250); });
      noteLabel.append(textarea); details.append(noteLabel);
      const concept = element('details', 'concept-copy'); concept.append(element('summary', '', 'Concept brief & source'));
      for (const [key, labelText] of [['character', 'Character'], ['costume', 'Costume'], ['rendering', 'Drawing'], ['environment', 'World'], ['monster', 'Monster'], ['palette', 'Palette']]) { const p = element('p'); p.append(element('strong', '', `${labelText}. `), document.createTextNode(card[key])); concept.append(p); }
      if (card.candidate) { const source = element('p', 'source-info'), a = element('a', '', 'Open original image'); a.href = card.candidate.src; a.target = '_blank'; a.rel = 'noopener'; source.append(a, document.createElement('br'), document.createTextNode(`${card.candidate.attempt_id} · ${card.candidate.width} × ${card.candidate.height} · SHA-256 ${card.candidate.sha256}`)); concept.append(source); }
      details.append(concept); content.append(details);
    }
    container.append(content); return container;
  }
  function selectCompare(id, selected = true) {
    if (!cardMap.get(id)?.candidate) return false;
    if (selected && !compareIDs.includes(id) && compareIDs.length === 4) {
      message('Compare up to four directions at a time. Uncheck one before adding another.'); syncCompare(); return false;
    }
    compareIDs = selected ? [...new Set([...compareIDs, id])] : compareIDs.filter(x => x !== id);
    message(''); syncCompare(); return true;
  }
  function syncCompare() {
    $('compare-count').textContent = compareIDs.length;
    $('open-compare').disabled = compareIDs.length < 2;
    $('compare-tray').hidden = compareIDs.length === 0;
    $('compare-tray-label').textContent = compareIDs.length < 2 ? `${compareIDs[0]} selected · choose one more` : `Compare ${compareIDs.join(' · ')}`;
    $('tray-open-compare').disabled = compareIDs.length < 2;
    document.body.classList.toggle('has-comparison', compareIDs.length > 0);
    document.querySelectorAll('[data-compare]').forEach(input => { input.checked = compareIDs.includes(input.dataset.compare); });
  }
  function render() {
    const family = $('family').value;
    const visible = data.cards.filter(c => (!family || c.family === family) && (!shortlistOnly || preferences[c.id].favorite));
    $('gallery').replaceChildren(...visible.map(c => renderCard(c)));
    $('empty').hidden = visible.length > 0;
    $('visible-count').textContent = `${visible.length} of 20 directions`;
    $('shortlist-filter').setAttribute('aria-pressed', String(shortlistOnly));
    syncCompare(); syncPreferences();
  }
  function renderComparison() { $('compare-stage').replaceChildren(...compareIDs.map(id => renderCard(cardMap.get(id), true))); syncPreferences(); }
  function openComparison() { if (compareIDs.length < 2) return; renderComparison(); $('compare-dialog').showModal(); }
  function openZoom(id) {
    const card = cardMap.get(id); if (!card?.candidate) return;
    zoomID = id;
    $('zoom-title').textContent = `${id} · ${card.title}`;
    const img = element('img'); img.src = card.candidate.src; img.alt = `${id} ${card.title}, complete original concept board`; img.width = card.candidate.width; img.height = card.candidate.height;
    $('zoom-stage').replaceChildren(img); $('zoom-stage').classList.remove('native'); $('zoom-stage').scrollTo(0, 0);
    $('native-link').href = card.candidate.src;
    $('zoom-toggle').setAttribute('aria-pressed', 'false'); $('zoom-toggle').textContent = 'Native pixels';
    if (!$('zoom-dialog').open) $('zoom-dialog').showModal();
  }
  for (const family of [...new Set(data.cards.map(c => c.family))]) { const option = element('option', '', family); option.value = family; $('family').append(option); }
  $('family').addEventListener('change', render);
  $('shortlist-filter').addEventListener('click', () => { shortlistOnly = !shortlistOnly; render(); });
  $('open-compare').addEventListener('click', openComparison);
  $('tray-open-compare').addEventListener('click', openComparison);
  $('clear-compare').addEventListener('click', () => { compareIDs = []; syncCompare(); });
  $('zoom-toggle').addEventListener('click', () => { const native = $('zoom-stage').classList.toggle('native'); $('zoom-toggle').setAttribute('aria-pressed', String(native)); $('zoom-toggle').textContent = native ? 'Fit complete board' : 'Native pixels'; $('zoom-stage').scrollTo(0, 0); });
  document.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => $(b.dataset.close).close()));
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const top = $('zoom-dialog').open ? $('zoom-dialog') : $('compare-dialog').open ? $('compare-dialog') : null;
    if (top) { event.preventDefault(); top.close(); }
  });
  $('export').addEventListener('click', () => {
    persist();
    const blob = new Blob([JSON.stringify(exportSelection(), null, 2) + '\n'], {type: 'application/json'}), url = URL.createObjectURL(blob), link = element('a');
    link.href = url; link.download = `visual-directions-selection-${data.dataset_sha256.slice(0, 10)}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    message('Your choices are exported. Keep this file to restore or share them.');
  });
  $('import').addEventListener('click', () => $('import-file').click());
  $('import-file').addEventListener('change', async e => {
    const file = e.target.files[0]; if (!file) return;
    try { if (file.size > 250000) throw Error('Selection file exceeds 250 KB.'); importSelection(JSON.parse(await file.text())); } catch (error) { message(error.message, true); }
    e.target.value = '';
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) persist(); });
  window.addEventListener('pagehide', persist);
  try { const saved = localStorage.getItem(storageKey); if (saved) { preferences = validateSelection(JSON.parse(saved)); $('save-status').textContent = 'Saved selection restored'; } } catch (error) { message(`Saved selection could not be loaded: ${error.message}`, true); }
  $('availability').textContent = `${data.available_count}/20 images available${data.available_count < 20 ? ' · generation in progress' : ''}`;
  render();
  window.VisualDirections = Object.freeze({ready: true, exportSelection, importSelection, validateSelection, toggleFavorite, toggleFacet, selectCompare, openComparison, openZoom,
    getState: () => ({preferences: structuredClone(preferences), compare_ids: [...compareIDs], dataset_sha256: data.dataset_sha256, storage_key: storageKey, storage_available: storageAvailable, zoom_id: zoomID})});
})();
