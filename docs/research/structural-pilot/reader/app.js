/* Offline, draft-only panel review. No network services, scores or approval writes. */
"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const NS = "http://www.w3.org/2000/svg";
  const WIDTH = 390;
  const KIND = new Set(["dialogue", "ui", "sfx"]);
  const FLAGS = new Set(["note", "wrong_event", "cast_identity", "geography", "contact_force", "continuity_state", "lettering", "delivery", "positive_evidence"]);
  const state = { data: null, selected: 0, letter: null, region: null, view: "review", stress: 0, full: false, showRegions: true, drawing: false, dirty: false, geometry: [] };
  let geometryFrame = 0;
  const experiment = window.STRUCTURAL_ROUTES;
  const routeDrafts = new Map();
  const dirtyRoutes = new Set();
  let routeID = experiment?.default_route || experiment?.routes[0]?.id;
  let neutral = experiment?.neutral_labels !== false;
  const routeLabel = id => { const r = experiment.routes.find(v => v.id === id); return neutral ? `Version ${r.label_neutral}` : r.label_provenance; };
  const measureContext = document.createElement("canvas").getContext("2d");
  const text = (value, max = 4000) => typeof value === "string" ? value.slice(0, max) : "";
  const display = value => typeof value === "string" ? value : value == null ? "Not specified" : JSON.stringify(value, null, 2);
  const finite = (v, fallback) => Number.isFinite(Number(v)) ? Number(v) : fallback;
  const clamp = (v, low, high) => Math.min(high, Math.max(low, v));
  const current = () => state.data?.panels[state.selected];
  const currentLetter = () => current()?.lettering.find(l => l.id === state.letter);
  const currentRegion = () => current()?.protected_regions.find(r => r.id === state.region);
  const unique = prefix => `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  const el = (tag, content, className) => { const n = document.createElement(tag); if (content != null) n.textContent = String(content); if (className) n.className = className; return n; };
  const svgEl = (tag, attrs = {}, content) => { const n = document.createElementNS(NS, tag); Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, String(v))); if (content != null) n.textContent = String(content); return n; };
  function notify(message, error = false) { $("notice").textContent = message; $("notice").classList.toggle("error", error); }
  function dirty() { dirtyRoutes.add(routeID); state.dirty = true; notify("Draft changed. Export review JSON to keep your work; this page does not save automatically."); }
  function localImageSource(src) {
    if (typeof src !== "string" || !src || src.length > 12000000) return "";
    if (/^data:image\/(png|jpe?g|webp);base64,[a-z0-9+/=\s]+$/i.test(src)) return src;
    if (/^file:\/\//i.test(src)) { try { return new URL(src).hostname === "" ? src : ""; } catch { return ""; } }
    if (/^[a-z][a-z0-9+.-]*:/i.test(src) || src.startsWith("//") || src.includes("\\")) return "";
    return src;
  }
  function rect(raw) {
    const w = clamp(finite(raw.w, .35), .02, 1), h = clamp(finite(raw.h, .12), .02, 1);
    return { x: clamp(finite(raw.x, .05), 0, 1 - w), y: clamp(finite(raw.y, .05), 0, 1 - h), w, h };
  }
  function lettering(raw, index = 0) {
    if (!raw || typeof raw !== "object") throw new Error("Lettering must be an object.");
    return { id: text(raw.id, 120) || `letter-${index + 1}`, text: text(raw.text), kind: KIND.has(raw.kind) ? raw.kind : "dialogue", speaker: text(raw.speaker, 100), shape: raw.shape === "ellipse" ? "ellipse" : "rounded", ...rect(raw), font_size: clamp(finite(raw.font_size, raw.kind === "ui" ? 12 : 16), 6, 96), tail: raw.tail && typeof raw.tail === "object" ? { x: clamp(finite(raw.tail.x, .5), 0, 1), y: clamp(finite(raw.tail.y, .5), 0, 1) } : null };
  }
  function region(raw, index = 0) { if (!raw || typeof raw !== "object") throw new Error("Region must be an object."); return { id: text(raw.id, 120) || `region-${index + 1}`, label: text(raw.label, 160) || "Observed region", ...rect(raw) }; }
  function boundedList(value, max, name) { if (value == null) return []; if (!Array.isArray(value) || value.length > max) throw new Error(`${name} must be an array with at most ${max} entries.`); return value; }
  function checkUnique(items, name) { if (new Set(items.map(v => v.id)).size !== items.length) throw new Error(`Duplicate ${name} IDs.`); }
  function sanitizeObservation(raw) {
    if (!raw || typeof raw !== "object") throw new Error("Observation must be an object.");
    // Source reviews may carry structured backend checks; preserve those as visible text,
    // never interpret them as approval or inject their contents into the document.
    if (raw.checks) return { flag: "note", text: text(display(raw.checks), 12000), reviewer: text(display(raw.reviewer), 300), reviewer_kind: "unspecified", created_at: text(raw.created_at, 100), candidate_id: text(raw.candidate_id, 120), image_sha256: text(raw.image_sha256, 64), plan_sha256: text(raw.plan_sha256, 64), source_checks: true };
    return { id: text(raw.id, 120), flag: FLAGS.has(raw.flag) ? raw.flag : "note", text: text(raw.text, 12000), reviewer: text(raw.reviewer ?? raw.claimed_reviewer, 300), reviewer_kind: ["human", "agent"].includes(raw.reviewer_kind) ? raw.reviewer_kind : "unspecified", created_at: text(raw.created_at, 100), candidate_id: text(raw.candidate_id, 120), image_sha256: text(raw.image_sha256 ?? raw.evidence_sha256, 64), plan_sha256: text(raw.plan_sha256, 64), source_checks: raw.source_checks === true };
  }
  function sanitizeData(raw) {
    if (!raw || raw.schema !== "SequenceReview/1" || !/^[a-f0-9]{64}$/i.test(raw.plan_sha256 || "")) throw new Error("Expected SequenceReview/1 with a valid plan SHA-256.");
    const panels = boundedList(raw.panels, 200, "Panels").map((p, i) => {
      if (!p || typeof p !== "object" || !/^[A-Za-z0-9_-]{1,80}$/.test(p.id || "")) throw new Error("Every panel needs a safe, unique ID.");
      const candidate = p.candidate ? { id: text(p.candidate.id, 120), sha256: text(p.candidate.sha256, 64), src: localImageSource(p.candidate.src), width: Math.max(1, finite(p.candidate.width, 390)), height: Math.max(1, finite(p.candidate.height, p.target_css_height_at390 || 500)), status: text(p.candidate.status, 120) || "draft-unaccepted" } : null;
      if (candidate && !/^[a-f0-9]{64}$/i.test(candidate.sha256)) throw new Error(`${p.id}: candidate SHA-256 is missing or invalid.`);
      const letters = boundedList(p.lettering, 100, "Lettering").map(lettering);
      const regions = boundedList(p.protected_regions, 100, "Protected regions").map(region);
      checkUnique(letters, "lettering"); checkUnique(regions, "region");
      return { id: p.id, panel: finite(p.panel, i + 1), function: text(p.function, 300), beat: text(display(p.beat), 12000), camera: text(display(p.camera), 3000), continuity_contract: text(display(p.continuity_contract), 12000), target_css_height_at390: clamp(finite(p.target_css_height_at390, 500), 60, 5000), copy: boundedList(p.copy, 100, "Copy").map(v => text(v)), candidate, observations: boundedList(p.observations, 500, "Observations").map(sanitizeObservation), lettering: letters, protected_regions: regions };
    });
    if (!panels.length) throw new Error("The sequence contains no panels.");
    checkUnique(panels, "panel");
    return { schema: raw.schema, title: text(raw.title, 300) || "Sequence pilot", plan_sha256: raw.plan_sha256, panels, status: { production_eligible: false, blockers: boundedList(raw.status?.blockers, 500, "Blockers").map(v => text(display(v), 2000)) } };
  }
  function artHeight(panel) { return panel.target_css_height_at390; }
  function stressText(original) {
    if (!state.stress || !original.trim()) return original;
    // Repeat only existing words; synthetic length growth is deliberately not a translation.
    const target = Math.ceil(original.length * state.stress / 100), words = original.split(/\s+/);
    let suffix = "", i = 0;
    while (suffix.length < target && i < 1000) { suffix += `${suffix ? " " : ""}${words[i % words.length]}`; i++; }
    return `${original} ${suffix}`;
  }
  function linesFor(value, width, fontSize, bold = false) {
    measureContext.font = `${bold ? "700" : "500"} ${fontSize}px Arial, sans-serif`;
    const result = [];
    for (const paragraph of value.split("\n")) {
      if (!paragraph) { result.push(""); continue; }
      let line = "";
      for (const word of paragraph.split(/\s+/)) {
        const proposed = line ? `${line} ${word}` : word;
        if (line && measureContext.measureText(proposed).width > width) { result.push(line); line = word; }
        else line = proposed;
      }
      result.push(line);
    }
    return result;
  }
  function letterGroup(letter, height, interactive = false) {
    const x = letter.x * WIDTH, y = letter.y * height, w = letter.w * WIDTH, h = letter.h * height;
    const isUI = letter.kind === "ui", isSFX = letter.kind === "sfx";
    const g = svgEl("g", { "data-letter-id": letter.id, class: interactive ? "letter-group" : "" });
    if (letter.tail && !isSFX) {
      const tx = letter.tail.x * WIDTH, ty = letter.tail.y * height;
      g.append(svgEl("path", { d: `M ${x + w * .4} ${y + h * .65} L ${tx} ${ty} L ${x + w * .6} ${y + h * .65} Z`, fill: isUI ? "#193b44" : "#fffdf7", stroke: "#242821", "stroke-width": 1.2 }));
    }
    if (!isSFX) {
      const attrs = { fill: isUI ? "#193b44" : "#fffdf7", stroke: isUI ? "#84bdc1" : "#242821", "stroke-width": 1.2, "data-balloon-shape": letter.shape };
      g.append(letter.shape === "ellipse" ? svgEl("ellipse", { ...attrs, cx: x + w / 2, cy: y + h / 2, rx: w / 2, ry: h / 2 }) : svgEl("rect", { ...attrs, x, y, width: w, height: h, rx: Math.min(18, w / 2, h / 2) }));
    }
    const font = letter.font_size, lines = linesFor(stressText(letter.text), Math.max(10, w - 20), font, isSFX || isUI), lineHeight = font * 1.22;
    const start = y + h / 2 - (lines.length - 1) * lineHeight / 2 + font * .34;
    const t = svgEl("text", { "font-family": "Arial, sans-serif", "font-size": font, "font-weight": isUI || isSFX ? 700 : 500, "text-anchor": "middle", fill: isUI ? "#f7fbec" : "#20261f", "data-glyph-text": letter.id, "aria-label": stressText(letter.text) });
    if (isSFX) { t.setAttribute("stroke", "#fff7df"); t.setAttribute("stroke-width", "1.8"); t.setAttribute("paint-order", "stroke"); t.setAttribute("stroke-linejoin", "round"); }
    lines.forEach((line, i) => t.append(svgEl("tspan", { x: x + w / 2, y: start + i * lineHeight }, line || " ")));
    g.append(t);
    if (interactive && letter.id === state.letter) {
      g.append(svgEl("rect", { x, y, width: w, height: h, fill: "none", stroke: "#256383", "stroke-width": 1.4, "stroke-dasharray": "4 3", "pointer-events": "none", "data-editor-decoration": "true" }));
      g.append(svgEl("rect", { x: x + w - 7, y: y + h - 7, width: 14, height: 14, rx: 2, fill: "#256383", stroke: "white", "stroke-width": 1.5, class: "resize-handle", "data-resize-letter": letter.id, "data-editor-decoration": "true" }));
    }
    return g;
  }
  function protectedGroup(item, height, interactive = false) {
    const x = item.x * WIDTH, y = item.y * height, w = item.w * WIDTH, h = item.h * height;
    const group = svgEl("g", { "data-region-id": item.id, "data-editor-decoration": "true" });
    group.append(svgEl("rect", { x, y, width: w, height: h, fill: "#db9d4f22", stroke: item.id === state.region ? "#994513" : "#b67726", "stroke-width": 1.4, "stroke-dasharray": "5 3", class: interactive ? "region-hit" : "protected-box" }));
    group.append(svgEl("text", { x: x + 3, y: y + 13, "font-size": 10, "font-family": "Arial, sans-serif", fill: "#733c16", stroke: "#fff9e6", "stroke-width": 3, "paint-order": "stroke", "pointer-events": "none" }, item.label));
    return group;
  }
  function overlay(panel, interactive = false, annotations = true) {
    const height = artHeight(panel);
    const svg = svgEl("svg", { xmlns: NS, viewBox: `0 0 ${WIDTH} ${height}`, width: WIDTH, height, role: "img", "aria-label": `${panel.id} lettering${annotations ? " and review annotations" : ""}`, "data-panel-overlay": panel.id });
    panel.lettering.forEach(letter => svg.append(letterGroup(letter, height, interactive)));
    if (annotations && state.showRegions) panel.protected_regions.forEach(item => svg.append(protectedGroup(item, height, interactive)));
    if (interactive) svg.addEventListener("pointerdown", startPointer);
    return svg;
  }
  function canvas(panel, interactive = false) {
    const mount = el("div", null, "art-mount"); mount.classList.toggle("full", state.full);
    const frame = el("div", null, "art-canvas"); frame.style.aspectRatio = `${WIDTH} / ${artHeight(panel)}`; frame.dataset.panelId = panel.id;
    if (interactive) frame.classList.toggle("drawing", state.drawing);
    if (panel.candidate?.src) {
      const img = el("img"); img.src = panel.candidate.src; img.style.objectFit = "contain"; img.alt = neutral ? `${panel.id} artwork. Full image, uncropped. Draft unaccepted.` : `${panel.id} candidate ${panel.candidate.id}. Full image, uncropped. Draft unaccepted.`;
      img.draggable = false; img.addEventListener("error", () => { img.remove(); frame.prepend(emptyArt("Candidate could not be loaded", "Check the local image path. Lettering and geometry remain draft annotations.")); if (interactive) scheduleGeometry(); });
      frame.append(img);
    } else frame.append(emptyArt("No artwork candidate", "The beat is planned. Add and bind a source image before reviewing what the art depicts."));
    frame.append(overlay(panel, interactive, interactive)); mount.append(frame); return mount;
  }
  function emptyArt(title, message) { const box = el("div", null, "empty-art"); box.append(el("span", "+", "empty-symbol"), el("strong", title), el("p", message)); return box; }
  function renderNavigation() {
    const list = $("panel-list"); list.replaceChildren();
    state.data.panels.forEach((panel, i) => { const b = el("button"); b.type = "button"; b.dataset.panelId = panel.id; b.setAttribute("aria-current", String(i === state.selected)); b.append(el("strong", panel.id), el("span", panel.function || "Story beat")); b.addEventListener("click", () => selectPanel(i)); list.append(b); });
    $("panel-count").textContent = `${state.data.panels.length} beats`;
  }
  function selectPanel(index) {
    state.selected = clamp(index, 0, state.data.panels.length - 1); state.letter = current().lettering[0]?.id || null; state.region = current().protected_regions[0]?.id || null; state.drawing = false;
    renderNavigation(); renderCurrent();
    if (state.view === "compare") document.getElementById(`compare-${current().id}`)?.scrollIntoView({ behavior: "auto", block: "start" });
    if (state.view === "reader") document.getElementById(`reader-${current().id}`)?.scrollIntoView({ behavior: "auto", block: "start" });
  }
  function renderCurrent() {
    const panel = current(); if (!panel) return;
    $("stage-title").textContent = state.view === "compare" ? "Matched screen panels" : state.view === "reader" ? `${routeLabel(routeID)} · complete sequence` : `${panel.id} · ${panel.function || "Story beat"}`;
    $("stage-kicker").textContent = state.view === "compare" ? "SAME BEAT / SAME DISPLAY SCALE" : state.view === "reader" ? "DRAFT READER" : "PANEL REVIEW";
    $("previous").disabled = state.selected === 0; $("next").disabled = state.selected === state.data.panels.length - 1;
    renderArt();
    $("source-caption").textContent = panel.candidate ? `Candidate ${panel.candidate.id} · ${panel.candidate.width} × ${panel.candidate.height} · full image contained in planned 390 × ${artHeight(panel)} canvas · ${panel.candidate.status} · SHA-256 ${panel.candidate.sha256.slice(0, 12)}…` : "No candidate is bound to this beat. Empty space is not accepted artwork.";
    $("beat-function").textContent = panel.function; $("beat-text").textContent = panel.beat; $("camera").textContent = panel.camera; $("continuity").textContent = panel.continuity_contract;
    const sources = $("editable-sources"); sources.replaceChildren();
    for (const item of experiment.routes.find(r => r.id === routeID).source_links[panel.id] || []) { const a = el("a", item.label); a.href = item.href; a.title = `Source SHA-256 ${item.sha256}`; sources.append(a, el("span", ` · SHA-256 ${item.sha256}`, "mono")); }
    syncLetterForm(); syncRegionForm(); renderObservations(); scheduleGeometry();
  }
  function renderArt() { const mount = $("art-mount"), rendered = canvas(current(), true); mount.className = rendered.className; mount.replaceChildren(...rendered.childNodes); }
  function renderReader() {
    const target = $("reader-stage"); target.replaceChildren(); target.classList.toggle("full", state.full);
    for (const panel of state.data.panels) { const f = el("figure", null, "reader-panel"); f.id = `reader-${panel.id}`; f.tabIndex = -1; f.append(canvas(panel)); if (!panel.candidate) f.append(el("figcaption", `${panel.id} · ${panel.function}. Artwork pending.`)); if (experiment.reference_only_panels?.includes(panel.id)) f.append(el("figcaption", `${panel.id} · unchanged generated reference; no conventional correction claimed.`)); target.append(f); }
  }
  function renderTranscript() {
    const body = $("transcript-body"); body.replaceChildren();
    for (const panel of state.data.panels) { const a = el("article"); a.append(el("h3", `${panel.id} · ${panel.function}`), el("p", panel.beat)); const list = el("ul"); const copy = panel.lettering.length ? panel.lettering.map(v => `${v.speaker ? `${v.speaker}: ` : ""}${v.text}`) : panel.copy; copy.forEach(line => list.append(el("li", line))); if (copy.length) a.append(list); body.append(a); }
  }
  function options(select, entries, selected, empty) { select.replaceChildren(); if (!entries.length) { const o = el("option", empty); o.value = ""; select.append(o); } else for (const entry of entries) { const o = el("option", entry.label); o.value = entry.id; select.append(o); } select.value = selected || ""; }
  function syncLetterForm() {
    const p = current(); if (!p.lettering.some(v => v.id === state.letter)) state.letter = p.lettering[0]?.id || null;
    options($("lettering-select"), p.lettering.map(v => ({ id: v.id, label: `${v.kind} · ${v.text.slice(0, 34) || "Empty copy"}` })), state.letter, "No lettering yet");
    const l = currentLetter(); $("lettering-form").querySelectorAll("input,select,textarea").forEach(n => n.disabled = !l); $("delete-balloon").disabled = !l;
    $("letter-text").value = l?.text || ""; $("letter-speaker").value = l?.speaker || ""; $("letter-kind").value = l?.kind || "dialogue"; $("letter-shape").value = l?.shape || "rounded"; $("letter-font").value = l?.font_size || 16;
    for (const key of ["x", "y", "w", "h"]) $("letter-" + key).value = l ? (l[key] * 100).toFixed(1) : "";
    $("letter-tail").checked = !!l?.tail; $("tail-x").value = l?.tail ? (l.tail.x * 100).toFixed(1) : "50"; $("tail-y").value = l?.tail ? (l.tail.y * 100).toFixed(1) : "50"; $("tail-x").disabled = $("tail-y").disabled = !l?.tail;
  }
  function syncRegionForm() {
    const p = current(); if (!p.protected_regions.some(v => v.id === state.region)) state.region = p.protected_regions[0]?.id || null;
    options($("region-select"), p.protected_regions.map(v => ({ id: v.id, label: v.label })), state.region, "No observed regions");
    const r = currentRegion(); $("region-form").querySelectorAll("input").forEach(n => n.disabled = !r); $("delete-region").disabled = !r; $("region-label").value = r?.label || "";
    for (const key of ["x", "y", "w", "h"]) $("region-" + key).value = r ? (r[key] * 100).toFixed(1) : "";
    $("draw-region").setAttribute("aria-pressed", String(state.drawing)); $("draw-region").textContent = state.drawing ? "Cancel region drawing" : "Draw a region";
  }
  function updateLetterFromForm(event) {
    event.preventDefault(); const l = currentLetter(); if (!l) return;
    const values = { ...l, text: $("letter-text").value, speaker: $("letter-speaker").value, kind: $("letter-kind").value, shape: $("letter-shape").value, font_size: finite($("letter-font").value, l.font_size), tail: $("letter-tail").checked ? { x: finite($("tail-x").value, 50) / 100, y: finite($("tail-y").value, 50) / 100 } : null };
    for (const key of ["x", "y", "w", "h"]) values[key] = finite($("letter-" + key).value, l[key] * 100) / 100;
    Object.assign(l, lettering(values)); $("tail-x").disabled = $("tail-y").disabled = !l.tail;
    dirty(); renderArt(); renderTranscript(); scheduleGeometry();
  }
  function updateRegionFromForm(event) {
    event.preventDefault(); const r = currentRegion(); if (!r) return; const values = { ...r, label: $("region-label").value };
    for (const key of ["x", "y", "w", "h"]) values[key] = finite($("region-" + key).value, r[key] * 100) / 100;
    Object.assign(r, region(values)); dirty(); renderArt(); scheduleGeometry();
  }
  function renderObservations() {
    const target = $("observations"); target.replaceChildren();
    for (const item of current().observations) { const li = el("li"); li.append(el("strong", item.flag.replaceAll("_", " ")), el("p", item.text), el("span", `${item.reviewer || "Unnamed"} · self-reported ${item.reviewer_kind} · ${item.created_at || "date unspecified"}${item.source_checks ? " · imported structured checks" : ""}`, "small")); target.append(li); }
  }
  function pointInBalloon(px, py, l, height) {
    const x = l.x * WIDTH, y = l.y * height, w = l.w * WIDTH, h = l.h * height, margin = 2;
    if (px < x + margin || px > x + w - margin || py < y + margin || py > y + h - margin) return false;
    if (l.shape === "ellipse") return ((px - x - w / 2) / (w / 2 - margin)) ** 2 + ((py - y - h / 2) / (h / 2 - margin)) ** 2 <= 1;
    const radius = Math.max(0, Math.min(18, w / 2, h / 2) - margin), nx = clamp(px, x + margin + radius, x + w - margin - radius), ny = clamp(py, y + margin + radius, y + h - margin - radius);
    return (px - nx) ** 2 + (py - ny) ** 2 <= radius ** 2 + .01;
  }
  const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  function geometryReport() {
    const p = current(); if (!p) return [];
    const results = [], height = artHeight(p), svg = $("art-mount").querySelector("svg");
    const renderedWidth = svg?.getBoundingClientRect().width || WIDTH;
    if (!p.candidate) results.push({ level: "info", code: "no_art", message: "No artwork: image semantics and protected-region placement are unreviewed." });
    else { const img = $("art-mount").querySelector("img"); if (!img || !img.complete || !img.naturalWidth) results.push({ level: "info", code: "image_pending", message: "Candidate is loading or unavailable. Image-dependent review remains pending." });
      if (Math.abs(p.candidate.height / p.candidate.width * WIDTH - height) > 1) results.push({ level: "info", code: "aspect_ratio_mismatch", message: "Source aspect ratio differs from the planned panel. The full image is contained with visible letterboxing; layout needs review." });
    }
    for (const l of p.lettering) {
      const group = Array.from(svg?.querySelectorAll("[data-letter-id]") || []).find(g => g.dataset.letterId === l.id);
      const lines = group?.querySelectorAll("tspan") || [];
      let clipped = false;
      for (const line of lines) { const b = line.getBBox(); if (!line.textContent.trim()) continue; const corners = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]; if (l.kind !== "sfx" && corners.some(([x, y]) => !pointInBalloon(x, y, l, height))) clipped = true; if (corners.some(([x, y]) => x < 0 || y < 0 || x > WIDTH || y > height)) results.push({ level: "fail", code: "glyph_outside_art", letter_id: l.id, message: `${l.id}: a rendered text box extends beyond the art.` }); }
      if (clipped) results.push({ level: "fail", code: "glyph_outside_balloon", letter_id: l.id, message: `${l.id}: rendered text bounds cross the ${l.shape} balloon contour.` });
      const actualFont = l.font_size * renderedWidth / WIDTH, floor = l.kind === "ui" ? 12 : l.kind === "dialogue" ? 14 : null;
      if (floor && actualFont + .01 < floor) results.push({ level: "fail", code: "font_floor", letter_id: l.id, actual_css_px: actualFont, message: `${l.id}: ${actualFont.toFixed(1)} CSS px at this width; project ${l.kind} floor is ${floor} px.` });
      const occupied = l.tail && l.kind !== "sfx" ? { x: Math.min(l.x, l.tail.x), y: Math.min(l.y, l.tail.y), w: Math.max(l.x + l.w, l.tail.x) - Math.min(l.x, l.tail.x), h: Math.max(l.y + l.h, l.tail.y) - Math.min(l.y, l.tail.y) } : l;
      for (const r of p.protected_regions) if (overlap(occupied, r)) results.push({ level: "fail", code: "protected_collision", letter_id: l.id, region_id: r.id, message: `${l.id}: balloon/tail or SFX bounds overlap marked region “${r.label}” (conservative rectangle test).` });
    }
    for (let i = 0; i < p.lettering.length; i++) for (let j = i + 1; j < p.lettering.length; j++) if (overlap(p.lettering[i], p.lettering[j])) results.push({ level: "fail", code: "letter_overlap", message: `${p.lettering[i].id} and ${p.lettering[j].id}: lettering bounds overlap.` });
    if (!p.lettering.length) results.push({ level: "info", code: "no_lettering", message: p.copy.length ? "Authored copy exists but no lettering is placed. Add balloons deliberately; none are auto-approved." : "No lettering placed. Confirm this is intentionally silent." });
    if (!p.protected_regions.length) results.push({ level: "info", code: "regions_unreviewed", message: "No image regions marked. Absence of collisions does not establish safe placement." });
    if (!results.some(v => v.level === "fail")) results.push({ level: "info", code: "no_geometry_flags", message: "No measured geometry flags in this view. Reader and semantic review remain required." });
    return results;
  }
  function scheduleGeometry() { cancelAnimationFrame(geometryFrame); geometryFrame = requestAnimationFrame(() => { state.geometry = geometryReport(); const target = $("geometry-results"); target.replaceChildren(); state.geometry.forEach(item => target.append(el("li", item.message, item.level))); const count = state.geometry.filter(v => v.level === "fail").length; $("geometry-title").textContent = count ? `${count} geometry flag${count === 1 ? "" : "s"}` : "Geometry measured · review pending"; }); }
  function startPointer(event) {
    if (event.button !== 0) return;
    const svg = event.currentTarget, panel = current(), height = artHeight(panel), b = svg.getBoundingClientRect();
    const point = e => ({ x: clamp((e.clientX - b.left) / b.width, 0, 1), y: clamp((e.clientY - b.top) / b.height, 0, 1) });
    const start = point(event); let item, mode;
    if (state.drawing) { item = region({ id: unique("region"), label: "Observed region · add a label", x: start.x, y: start.y, w: .02, h: .02 }); panel.protected_regions.push(item); state.region = item.id; mode = "draw"; }
    else {
      const hitRegion = event.target.closest("[data-region-id]"); const hitLetter = event.target.closest("[data-letter-id]");
      if (hitRegion) { item = panel.protected_regions.find(v => v.id === hitRegion.dataset.regionId); state.region = item.id; mode = "move"; }
      else if (hitLetter) { item = panel.lettering.find(v => v.id === hitLetter.dataset.letterId); state.letter = item.id; mode = event.target.closest("[data-resize-letter]") ? "resize" : "move"; }
      else return;
    }
    event.preventDefault(); const original = { ...item }; svg.setPointerCapture(event.pointerId); svg.style.touchAction = "none";
    const paint = () => { svg.replaceChildren(); panel.lettering.forEach(l => svg.append(letterGroup(l, height, true))); if (state.showRegions) panel.protected_regions.forEach(r => svg.append(protectedGroup(r, height, true))); syncLetterForm(); syncRegionForm(); scheduleGeometry(); };
    paint();
    const move = e => { const now = point(e), dx = now.x - start.x, dy = now.y - start.y; if (mode === "draw") Object.assign(item, rect({ x: Math.min(start.x, now.x), y: Math.min(start.y, now.y), w: Math.max(.02, Math.abs(dx)), h: Math.max(.02, Math.abs(dy)) })); else if (mode === "resize") { item.w = clamp(original.w + dx, .02, 1 - item.x); item.h = clamp(original.h + dy, .02, 1 - item.y); } else { item.x = clamp(original.x + dx, 0, 1 - item.w); item.y = clamp(original.y + dy, 0, 1 - item.h); } paint(); };
    const end = () => { svg.removeEventListener("pointermove", move); svg.removeEventListener("pointerup", end); svg.removeEventListener("pointercancel", end); state.drawing = false; dirty(); renderArt(); syncRegionForm(); scheduleGeometry(); };
    svg.addEventListener("pointermove", move); svg.addEventListener("pointerup", end); svg.addEventListener("pointercancel", end);
  }
  function exportDraft() {
    if (!state.data) throw new Error("No review is loaded.");
    return { schema: "SequenceReviewDraft/1", title: state.data.title, plan_sha256: state.data.plan_sha256, exported_at: new Date().toISOString(), status: "draft-unaccepted", experiment_id: experiment.experiment_id, route_id: routeID, reader_input_sha256: experiment.input_sha256, reviewer_labels_verified: false, panels: state.data.panels.map(p => ({ id: p.id, candidate_id: p.candidate?.id || null, candidate_sha256: p.candidate?.sha256 || null, lettering: structuredClone(p.lettering), protected_regions: structuredClone(p.protected_regions), observations: structuredClone(p.observations) })) };
  }
  function importDraft(raw) {
    if (!state.data) throw new Error("Load the original exported review bundle before importing a draft.");
    if (!raw || raw.schema !== "SequenceReviewDraft/1") throw new Error("Expected a SequenceReviewDraft/1 export. A draft cannot replace the underlying plan.");
    if (raw.route_id && raw.route_id !== routeID) throw new Error("Switch to the matching route before importing this draft.");
    if (raw.plan_sha256 !== state.data.plan_sha256) throw new Error("Stale or different plan hash. No changes imported.");
    const drafts = boundedList(raw.panels, 200, "Draft panels");
    if (drafts.length !== state.data.panels.length || new Set(drafts.map(p => p?.id)).size !== drafts.length) throw new Error("Draft panel set does not match this sequence.");
    const changes = state.data.panels.map(p => {
      const d = drafts.find(v => v?.id === p.id); if (!d || d.candidate_sha256 !== (p.candidate?.sha256 || null) || d.candidate_id !== (p.candidate?.id || null)) throw new Error(`${p.id}: stale or mismatched candidate binding. No changes imported.`);
      const letters = boundedList(d.lettering, 100, "Lettering").map(lettering), regions = boundedList(d.protected_regions, 100, "Protected regions").map(region), observations = boundedList(d.observations, 500, "Observations").map(sanitizeObservation);
      checkUnique(letters, "lettering"); checkUnique(regions, "region");
      return { panel: p, lettering: letters, protected_regions: regions, observations };
    });
    // Apply only after every panel and hash has passed; source/status fields are ignored.
    changes.forEach(c => { c.panel.lettering = c.lettering; c.panel.protected_regions = c.protected_regions; c.panel.observations = c.observations; });
    dirty(); selectPanel(state.selected); renderReader(); renderTranscript(); notify("Draft imported against matching plan and candidate hashes. Production remains unaccepted."); return true;
  }
  function download(filename, content, type) { const blob = new Blob([content], { type }), url = URL.createObjectURL(blob), a = el("a"); a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
  function exportSVG() {
    const p = current(); if (!p) return;
    const savedStress = state.stress; state.stress = 0; const svg = overlay(p, false, false); state.stress = savedStress;
    const metadata = svgEl("metadata", {}, JSON.stringify({ schema: "SequenceLettering/1", plan_sha256: state.data.plan_sha256, panel_id: p.id, candidate_id: p.candidate?.id || null, candidate_sha256: p.candidate?.sha256 || null, status: "draft-unaccepted", coordinates: "390px wide planned canvas; full candidate contained without cropping", canvas_height: artHeight(p), font_family: "Arial, sans-serif; supply appropriately licensed fonts in production", lettering: p.lettering })); svg.prepend(metadata);
    download(`${p.id}-lettering-draft.svg`, new XMLSerializer().serializeToString(svg), "image/svg+xml"); notify(`${p.id} lettering exported with original copy and hash bindings. Artwork is not embedded.`);
  }
  function renderComparison() {
    const target = $("comparison-stage"); target.replaceChildren();
    target.append(el("p", "Read each version in sequence first. These selected panels then share one canvas size, exact story beat and original copy. Replacement lettering remains a separate editable layer.", "small"));
    for (const id of experiment.selected_panels) {
      const group = el("section", null, "comparison-group"); group.id = `compare-${id}`;
      const planned = state.data.panels.find(p => p.id === id);
      group.append(el("h3", `${id} · ${planned.function}${experiment.reference_only_panels?.includes(id) ? " · unchanged generated reference" : ""}`));
      const requirements = el("details", null, "comparison-requirements"); requirements.append(el("summary", "Frozen event and continuity requirements"), el("p", planned.beat), el("p", planned.continuity_contract)); group.append(requirements);
      const row = el("div", null, "comparison-row");
      for (const route of experiment.routes) {
        const data = route.id === routeID ? state.data : routeDrafts.get(route.id) || sanitizeData(experiment.datasets[route.id]);
        const panel = data.panels.find(p => p.id === id);
        const figure = el("figure", null, "comparison-cell"); figure.dataset.route = route.id;
        const title = el("h4", routeLabel(route.id)); figure.append(title, canvas(panel));
        if (!panel.candidate) figure.append(el("p", "Test candidate not yet supplied.", "small"));
        else { const caption = el("figcaption", `${panel.candidate.id} · SHA-256 ${panel.candidate.sha256}`, "mono provenance-only"); figure.append(caption); }
        const button = el("button", `Read ${routeLabel(route.id)} in context`); button.type = "button"; button.addEventListener("click", () => { switchRoute(route.id); setView("reader"); selectPanel(state.data.panels.findIndex(p => p.id === id)); }); figure.append(button);
        row.append(figure);
      }
      group.append(row); target.append(group);
    }
  }
  function setView(view) {
    state.view = ["reader", "compare"].includes(view) ? view : "review";
    document.body.classList.toggle("reading", state.view === "reader");
    document.body.classList.toggle("comparing", state.view === "compare");
    $("review-stage").hidden = state.view !== "review"; $("reader-stage").hidden = state.view !== "reader"; $("comparison-stage").hidden = state.view !== "compare";
    for (const [id, value] of [["review-view", "review"], ["reader-view", "reader"], ["compare-view", "compare"]]) $(id).setAttribute("aria-pressed", String(state.view === value));
    if (state.data) { if (state.view === "reader") renderReader(); if (state.view === "compare") renderComparison(); renderCurrent(); }
    const query = new URLSearchParams(location.search); query.set("view", state.view); query.set("version", experiment.routes.find(r => r.id === routeID).label_neutral); history.replaceState(null, "", `${location.pathname}?${query}${location.hash}`);
  }
  function renderRouteControls() {
    options($("route-select"), experiment.routes.map(r => ({id: r.id, label: routeLabel(r.id)})), routeID, "No routes");
    const missing = state.data.panels.filter(p => !p.candidate).length;
    $("route-state").textContent = missing ? `${missing} test panels missing · draft unaccepted` : "14 panels available · draft unaccepted";
  }
  function switchRoute(id) {
    if (!experiment.datasets[id]) return;
    if (state.data) routeDrafts.set(routeID, state.data);
    const index = state.selected;
    routeID = id;
    initialize(routeDrafts.get(id) || experiment.datasets[id]);
    selectPanel(index); renderRouteControls(); setView(state.view);
    notify("Version loaded. Edits are retained per version in this tab; export each changed version to keep them.");
  }
  function setNeutral(value) {
    neutral = experiment.neutral_labels === false ? false : !!value; document.body.classList.toggle("neutral-review", neutral); $("neutral-mode").checked = neutral;
    renderRouteControls(); renderCurrent(); renderReader(); if (state.view === "compare") renderComparison();
  }
  function initialize(raw) {
    state.data = sanitizeData(raw); $("title").textContent = state.data.title; document.title = `${state.data.title} · Draft panel review`; $("subtitle").textContent = `${state.data.panels.length} beats · one continuous scene · review the sequence, then the image`;
    $("blockers").replaceChildren(); const blockers = state.data.status.blockers.length ? state.data.status.blockers : ["No verified production acceptance is recorded in this workspace."]; blockers.forEach(b => $("blockers").append(el("li", b)));
    $("gate-summary").textContent = `Draft only · ${blockers.length} production blocker${blockers.length === 1 ? "" : "s"}`; $("binding").textContent = `Plan SHA-256: ${state.data.plan_sha256}`;
    selectPanel(0); renderReader(); renderTranscript(); notify("Review loaded. Edits stay in this browser until you export them.");
  }
  function bindEvents() {
    $("route-select").addEventListener("change", e => switchRoute(e.target.value));
    $("neutral-mode").addEventListener("change", e => setNeutral(e.target.checked));
    $("compare-view").addEventListener("click", () => setView("compare"));
    $("review-view").addEventListener("click", () => setView("review")); $("reader-view").addEventListener("click", () => setView("reader"));
    $("previous").addEventListener("click", () => state.data && selectPanel(state.selected - 1)); $("next").addEventListener("click", () => state.data && selectPanel(state.selected + 1));
    $("preview-mode").addEventListener("change", e => { state.full = e.target.value === "full"; if (state.data) { renderArt(); renderReader(); scheduleGeometry(); } });
    $("stress").addEventListener("change", e => { state.stress = Number(e.target.value); $("stress-note").hidden = !state.stress; if (state.data) { renderArt(); renderReader(); scheduleGeometry(); } });
    $("show-regions").addEventListener("change", e => { state.showRegions = e.target.checked; if (state.data) renderArt(); });
    $("transcript-toggle").addEventListener("click", () => { const open = $("transcript").hidden; $("transcript").hidden = !open; $("transcript-toggle").setAttribute("aria-expanded", String(open)); $("transcript-toggle").textContent = open ? "Close transcript" : "Open transcript"; if (open) $("transcript").scrollIntoView({ block: "start" }); });
    $("lettering-select").addEventListener("change", e => { state.letter = e.target.value; syncLetterForm(); renderArt(); scheduleGeometry(); });
    $("region-select").addEventListener("change", e => { state.region = e.target.value; syncRegionForm(); renderArt(); });
    $("lettering-form").addEventListener("input", updateLetterFromForm); $("lettering-form").addEventListener("submit", e => e.preventDefault());
    $("region-form").addEventListener("input", updateRegionFromForm); $("region-form").addEventListener("submit", e => e.preventDefault());
    $("add-balloon").addEventListener("click", () => { const p = current(); if (!p) return; const l = lettering({ id: unique("letter"), text: p.copy[p.lettering.length] || "", x: .06, y: .04 + Math.min(p.lettering.length, 5) * .13, w: .65, h: Math.max(.08, 66 / artHeight(p)), font_size: 16, kind: "dialogue" }); p.lettering.push(l); state.letter = l.id; dirty(); renderCurrent(); renderTranscript(); $("letter-text").focus(); });
    $("delete-balloon").addEventListener("click", () => { const p = current(); if (!p) return; p.lettering = p.lettering.filter(l => l.id !== state.letter); dirty(); renderCurrent(); renderTranscript(); });
    $("add-region").addEventListener("click", () => { const p = current(); if (!p) return; const r = region({ id: unique("region"), label: "Observed region · add a label", x: .2, y: .3, w: .25, h: .2 }); p.protected_regions.push(r); state.region = r.id; state.showRegions = true; $("show-regions").checked = true; dirty(); renderCurrent(); $("region-label").focus(); });
    $("draw-region").addEventListener("click", () => { if (!current()) return; state.drawing = !state.drawing; state.showRegions = true; $("show-regions").checked = true; syncRegionForm(); renderArt(); notify(state.drawing ? "Drag over the image to mark a region; or use “Region by form” with the keyboard." : "Region drawing cancelled."); });
    $("delete-region").addEventListener("click", () => { const p = current(); if (!p) return; p.protected_regions = p.protected_regions.filter(r => r.id !== state.region); dirty(); renderCurrent(); });
    $("observation-form").addEventListener("submit", e => { e.preventDefault(); const p = current(); if (!p || !$("observation-text").value.trim()) return; p.observations.push(sanitizeObservation({ id: unique("observation"), text: $("observation-text").value, flag: $("observation-flag").value, reviewer: $("reviewer-name").value, reviewer_kind: $("reviewer-kind").value, created_at: new Date().toISOString(), candidate_id: p.candidate?.id || "", image_sha256: p.candidate?.sha256 || "", plan_sha256: state.data.plan_sha256 })); $("observation-text").value = ""; dirty(); renderObservations(); });
    $("export-button").addEventListener("click", () => { try { download(`sequence-review-${routeID}-draft.json`, JSON.stringify(exportDraft(), null, 2) + "\n", "application/json"); dirtyRoutes.delete(routeID); state.dirty = dirtyRoutes.size > 0; notify("Draft JSON downloaded. Reviewer claims and observations do not confer acceptance."); } catch (e) { notify(e.message, true); } });
    $("svg-button").addEventListener("click", exportSVG); $("import-button").addEventListener("click", () => $("import-file").click());
    $("import-file").addEventListener("change", async e => { const file = e.target.files?.[0]; if (!file) return; try { if (file.size > 12000000) throw new Error("Import exceeds the 12 MB review limit."); const data = JSON.parse(await file.text()); importDraft(data); } catch (error) { notify(error.message, true); } finally { e.target.value = ""; } });
    window.addEventListener("resize", () => state.data && scheduleGeometry());
    window.addEventListener("beforeunload", e => { if (state.dirty) { e.preventDefault(); e.returnValue = ""; } });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && state.drawing) { state.drawing = false; syncRegionForm(); renderArt(); } });
  }
  // Read-only snapshots and validated actions for reproducible browser QA.
  window.SequenceReviewApp = Object.freeze({ getState: () => ({ route_id: routeID, neutral, data: structuredClone(state.data), selected: state.selected, view: state.view, stress: state.stress, dirty: state.dirty }), exportDraft, importDraft, geometryReport, switchRoute, setNeutral, selectPanel: index => state.data && selectPanel(index), setView, get ready() { return !!state.data; } });
  bindEvents();
  (async () => {
    try { const raw = window.SEQUENCE_REVIEW_DATA || await fetch("review-data.json").then(r => { if (!r.ok) throw new Error(`Review data could not be loaded (${r.status}).`); return r.json(); }); initialize(raw);
      const query = new URLSearchParams(location.search);
      const requested = experiment.routes.find(r => r.label_neutral === query.get("version"));
      if (requested) switchRoute(requested.id);
      if (experiment.neutral_labels === false) { $("neutral-mode").closest("label").hidden = true; setNeutral(false); }
      renderRouteControls(); setView(query.get("view") || "reader"); }
    catch (error) { $("stage-title").textContent = "The review bundle is unavailable"; notify(`${error.message} Open the complete exported bundle with review-data.js, or serve it locally.`, true); }
  })();
})();
