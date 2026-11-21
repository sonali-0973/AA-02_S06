import { createActionQueue } from './action-queue.js';
import * as api from './api.js';

const sessionCode = crypto.randomUUID(); // Mock ownership marker, not authentication.
const enqueue = createActionQueue();
const $ = id => document.getElementById(id);
const state = { exhibits: [], selected: null, planCode: null, plan: null };

const el = (tag, props = {}, ...children) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};
const mins = n => `${n} min`;
const setStatus = text => { $('status').textContent = text; };
const showAlert = text => { $('plan-alert').textContent = text || ''; $('plan-alert').hidden = !text; };
const errorText = e => `${e.message}${e.code && e.code !== 'REQUEST_FAILED' ? ` (${e.code})` : ''}`;

$('session').textContent = sessionCode;
$('mock-badge').hidden = !api.isMock;

api.setLogger(({ time, method, path, session, body, status, response }) => {
  const item = el('li', {}, `${time}  ${method} ${path} → ${status}`);
  const detail = JSON.stringify({ sessionHeader: session ?? null, requestBody: body ?? null, response }, null, 2);
  item.append(el('pre', {}, detail));
  $('log').prepend(item);
});

/* ---------- rendering (only shows what the server returned) ---------- */
function renderExhibits() {
  const inPlan = new Set((state.plan?.items ?? []).map(i => i.code));
  $('cat-empty').hidden = state.exhibits.length > 0;
  $('exhibit-list').replaceChildren(...state.exhibits.map(e => {
    const button = el('button', { type: 'button' },
      el('span', {}, el('strong', {}, e.name), ' ', el('span', { className: 'meta' }, e.code)),
      el('span', { className: 'meta' }, inPlan.has(e.code) ? 'In plan' : e.suggested != null ? `Suggested ${mins(e.suggested)}` : ''));
    button.setAttribute('aria-current', String(state.selected?.code === e.code));
    button.addEventListener('click', () => selectExhibit(e.code));
    return el('li', {}, button);
  }));
}

function renderDetail() {
  const e = state.selected;
  if (!e) return;
  const input = el('input', { type: 'number', id: 'add-minutes', value: e.suggested ?? '', inputMode: 'numeric' });
  const add = el('button', { type: 'button', className: 'act' }, 'Add to plan');
  add.addEventListener('click', () => addStop(e.code, input.value, add));
  $('detail').replaceChildren(
    el('h3', {}, e.name),
    el('dl', {},
      el('dt', {}, 'Code'), el('dd', {}, e.code),
      el('dt', {}, 'Theme'), el('dd', {}, e.theme || 'Not listed'),
      el('dt', {}, 'Suggested time'), el('dd', {}, e.suggested != null ? mins(e.suggested) : 'Not listed')),
    el('div', { className: 'field' }, el('label', { htmlFor: 'add-minutes' }, 'Minutes to allocate'), input, add),
    el('p', { className: 'empty' }, 'The suggested time is a guide only. Your allocation is what gets saved.'));
}

function renderPlan() {
  const plan = state.plan;
  $('plan-code').textContent = state.planCode ?? 'not created yet';
  const items = plan?.items ?? [];
  $('plan-empty').hidden = items.length > 0;
  $('plan-total').textContent = mins(plan?.total ?? 0);
  $('plan-items').replaceChildren(...items.map(i => {
    const input = el('input', { type: 'number', value: i.allocated, id: `alloc-${i.code}`, inputMode: 'numeric' });
    const save = el('button', { type: 'button', className: 'act quiet' }, 'Save minutes');
    const remove = el('button', { type: 'button', className: 'act danger' }, 'Remove');
    save.addEventListener('click', () => changeStop(i.code, input.value, save));
    remove.addEventListener('click', () => removeStop(i.code, remove));
    return el('li', {},
      el('h3', {}, i.exhibit.name),
      el('p', { className: 'sub' }, `${i.code} · ${i.exhibit.theme || 'No theme'} · suggested ${i.exhibit.suggested != null ? mins(i.exhibit.suggested) : 'n/a'}`),
      el('p', { className: 'sub' }, 'Saved allocation: ', el('span', { className: 'saved' }, mins(i.allocated))),
      el('div', { className: 'row' },
        el('label', { htmlFor: input.id }, 'Minutes'), input, save, remove));
  }));
  renderExhibits();
}

/* ---------- actions: queued, awaited, then re-read from the server ---------- */
const toMinutes = raw => (raw.trim() === '' ? raw : Number(raw)); // no client-side range check: the server decides

async function refreshPlan() {
  state.plan = await api.getPlan(state.planCode, sessionCode);
  renderPlan();
}

function mutate(button, label, operation, doneText) {
  showAlert('');
  button.disabled = true;
  setStatus(`${label}…`);
  return enqueue(async () => {
    try {
      await operation();
      await refreshPlan();
      setStatus(doneText);
    } catch (e) {
      showAlert(`${label} failed: ${errorText(e)}`);
      setStatus('Nothing was changed.');
      if (state.planCode) await refreshPlan().catch(() => {}); // show the retained saved state
    } finally { button.disabled = false; }
  });
}

const addStop = (code, raw, btn) => mutate(btn, 'Adding stop',
  () => api.addItem(state.planCode, sessionCode, code, toMinutes(raw)), `${code} added to the plan.`);
const changeStop = (code, raw, btn) => mutate(btn, 'Saving minutes',
  () => api.updateItem(state.planCode, sessionCode, code, toMinutes(raw)), `${code} updated.`);
const removeStop = (code, btn) => mutate(btn, 'Removing stop',
  () => api.removeItem(state.planCode, sessionCode, code), `${code} removed. It is still in the exhibit list.`);

async function selectExhibit(code) {
  setStatus('Loading exhibit…');
  try {
    state.selected = await enqueue(() => api.getExhibit(code));
    renderDetail(); renderExhibits(); setStatus('');
  } catch (e) { setStatus(`Could not load exhibit: ${errorText(e)}`); }
}

/* ---------- start-up ---------- */
(async function init() {
  setStatus('Loading exhibits…');
  try {
    state.exhibits = await api.listExhibits();
    renderExhibits();
    const created = await enqueue(() => api.createPlan(sessionCode));
    state.planCode = created.planCode;
    await enqueue(refreshPlan);
    setStatus('Ready.');
  } catch (e) {
    setStatus(`Could not start: ${errorText(e)}`);
  }
})();
