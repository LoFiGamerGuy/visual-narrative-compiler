/* Bounded preference storage shared by the two offline refinement views. */
window.RefinementPreferences = function(data, onChange) {
  'use strict';
  const facets = ['character', 'style', 'readability', 'comfort'];
  const ids = data.entries.map(e => e.id), entries = new Map(data.entries.map(e => [e.id, e]));
  const storageKey = `visual-refinement:${data.mode}:${data.experiment_id}:${data.dataset_sha256}`;
  let choices = Object.fromEntries(ids.map(id => [id, {shortlist: false, responses: Object.fromEntries(facets.map(k => [k, null])), note: ''}]));
  let storageAvailable = true;
  const unavailable = new Set();
  const status = text => { document.getElementById('save-status').textContent = text; };
  function exactKeys(value, keys, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== [...keys].sort().join('|')) throw Error(`Invalid ${label}.`);
  }
  function exportChoices() {
    return {schema: 'VisualRefinementChoices/1', experiment_id: data.experiment_id, mode: data.mode,
      dataset_sha256: data.dataset_sha256, plan_sha256: data.plan_sha256,
      source_bindings: structuredClone(data.source_bindings), exported_at: new Date().toISOString(), choices: structuredClone(choices)};
  }
  function validate(draft) {
    exactKeys(draft, ['schema', 'experiment_id', 'mode', 'dataset_sha256', 'plan_sha256', 'source_bindings', 'exported_at', 'choices'], 'choice file');
    if (draft.schema !== 'VisualRefinementChoices/1' || typeof draft.exported_at !== 'string' || !Number.isFinite(Date.parse(draft.exported_at))) throw Error('Invalid choice-file format.');
    for (const key of ['experiment_id', 'mode', 'dataset_sha256', 'plan_sha256']) if (draft[key] !== data[key]) throw Error('These choices belong to a different or older image set. Nothing was changed.');
    if (!Array.isArray(draft.source_bindings) || draft.source_bindings.length !== data.source_bindings.length) throw Error('The complete image binding list is required.');
    draft.source_bindings.forEach((binding, i) => {
      exactKeys(binding, ['id', 'attempt_id', 'sha256'], 'image binding');
      for (const key of ['id', 'attempt_id', 'sha256']) if (binding[key] !== data.source_bindings[i][key]) throw Error('An image or its source hash has changed. Nothing was imported.');
    });
    exactKeys(draft.choices, ids, 'image choices');
    for (const id of ids) {
      const choice = draft.choices[id];
      exactKeys(choice, ['shortlist', 'responses', 'note'], 'choice'); exactKeys(choice.responses, facets, 'responses');
      if (typeof choice.shortlist !== 'boolean' || typeof choice.note !== 'string' || choice.note.length > 4000 || Object.values(choice.responses).some(v => ![null, 'yes', 'no', 'unsure'].includes(v))) throw Error('Invalid response or note longer than 4,000 characters.');
      if (!entries.get(id).candidate && (choice.shortlist || choice.note || Object.values(choice.responses).some(v => v !== null))) throw Error('A missing image cannot have an owner response.');
    }
    return structuredClone(draft.choices);
  }
  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(exportChoices())); storageAvailable = true; status('Saved in this browser'); }
    catch { storageAvailable = false; status('Storage unavailable · export to keep'); }
  }
  function importChoices(draft) { const next = validate(draft); choices = next; save(); onChange(); return true; }
  function update(id, facet, value) {
    if (!entries.get(id)?.candidate || unavailable.has(id)) return false;
    if (facet === 'shortlist' && typeof value === 'boolean') choices[id].shortlist = value;
    else if (facet === 'note' && typeof value === 'string' && value.length <= 4000) choices[id].note = value;
    else if (facets.includes(facet) && [null, 'yes', 'no', 'unsure'].includes(value)) choices[id].responses[facet] = value;
    else throw Error('Invalid choice change');
    save(); onChange(); return true;
  }
  try { const saved = localStorage.getItem(storageKey); if (saved) { choices = validate(JSON.parse(saved)); status('Your saved choices are restored'); } }
  catch { status('Saved choices could not be restored · import a saved copy'); }
  return Object.freeze({exportChoices, importChoices, validate, update, save,
    markUnavailable: id => { unavailable.add(id); onChange(); }, isUnavailable: id => unavailable.has(id),
    get: id => structuredClone(choices[id]), getAll: () => structuredClone(choices),
    getStorage: () => ({key: storageKey, available: storageAvailable})});
};
