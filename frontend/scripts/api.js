/**
 * Scenario S06 API wrapper.
 * Response field names are normalised in ONE place (the norm* functions).
 * If the page shows blanks, compare these names with the real JSON from curl.
 */
import { request } from './http.js';

export const isMock = false;
let logger = () => {};
export const setLogger = fn => { logger = fn; };

async function call(path, options = {}) {
  const entry = { method: options.method || 'GET', path: `/api${path}`, body: options.body };
  try {
    const response = await request(path, options);
    logger({ ...entry, status: 'OK', response });
    return response;
  } catch (error) {
    logger({ ...entry, status: error.status ?? 'ERROR', response: error.payload ?? error.message });
    throw error;
  }
}

export const normExhibit = e => ({
  code: e.exhibitCode ?? e.exhibit_code ?? e.code,
  name: e.name ?? e.title ?? e.exhibitCode ?? e.code,
  theme: e.theme ?? '',
  suggested: e.suggestedMinutes ?? e.suggested_minutes ?? e.suggestedVisitMinutes ?? e.suggestedVisitTime ?? null
});

const normPlan = p => ({
  planCode: p.planCode ?? p.plan_code ?? p.code,
  total: p.totalMinutes ?? p.totalVisitMinutes ?? p.total_minutes ?? p.total ?? 0,
  items: (p.items ?? p.stops ?? p.entries ?? []).map(i => ({
    code: i.exhibitCode ?? i.exhibit_code ?? i.code,
    allocated: i.allocatedMinutes ?? i.allocated_minutes,
    exhibit: normExhibit(i.exhibit ?? i)
  }))
});

export async function listExhibits() {
  const r = await call('/exhibits');
  const list = Array.isArray(r) ? r : r.items ?? r.exhibits ?? [];
  return list.map(normExhibit);
}
export const getExhibit = async code => normExhibit(await call(`/exhibits/${encodeURIComponent(code)}`));

export async function createPlan(session) {
  const r = await call('/visit-plans', { method: 'POST', session });
  return { planCode: r.planCode ?? r.plan_code ?? r.code };
}
export const getPlan = async (planCode, session) => normPlan(await call(`/visit-plans/${planCode}`, { session }));
export const addItem = (planCode, session, exhibitCode, allocatedMinutes) =>
  call(`/visit-plans/${planCode}/items`, { method: 'POST', session, body: { exhibitCode, allocatedMinutes } });
export const updateItem = (planCode, session, exhibitCode, allocatedMinutes) =>
  call(`/visit-plans/${planCode}/items/${encodeURIComponent(exhibitCode)}`, { method: 'PUT', session, body: { allocatedMinutes } });
export const removeItem = (planCode, session, exhibitCode) =>
  call(`/visit-plans/${planCode}/items/${encodeURIComponent(exhibitCode)}`, { method: 'DELETE', session });