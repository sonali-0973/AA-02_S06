/**
 * Scenario S06 API wrapper. Field names are normalised in ONE place (the norm* functions)
 * so they can be changed once the group agrees the response shapes.
 * Open the page with ?mock=1 to use in-browser demo data instead of the real backend.
 */
import { request as realRequest } from './http.js';
import { mockRequest } from './mock-api.js';

export const isMock = new URLSearchParams(location.search).has('mock');
let logger = () => {};
export const setLogger = fn => { logger = fn; };

async function call(path, options = {}) {
  const transport = isMock ? mockRequest : realRequest;
  const entry = { method: options.method || 'GET', path: `/api${path}`, body: options.body };
  try {
    const response = await transport(path, options);
    logger({ ...entry, status: 'OK', response });
    return response;
  } catch (error) {
    logger({ ...entry, status: error.status ?? 'ERROR', response: error.payload ?? error.message });
    throw error;
  }
}

export const normExhibit = e => ({
  code: e.exhibitCode,
  name: e.name ?? e.title ?? e.exhibitCode,
  theme: e.theme ?? '',
  suggested: e.suggestedMinutes ?? e.suggestedVisitMinutes ?? e.suggestedVisitTime ?? null
});

const normPlan = p => ({
  planCode: p.planCode,
  total: p.totalMinutes ?? p.totalVisitMinutes ?? 0,
  items: (p.items ?? []).map(i => ({
    code: i.exhibitCode,
    allocated: i.allocatedMinutes,
    exhibit: normExhibit(i.exhibit ?? i)
  }))
});

export async function listExhibits() {
  const r = await call('/exhibits');
  return (Array.isArray(r) ? r : r.exhibits ?? []).map(normExhibit);
}
export const getExhibit = async code => normExhibit(await call(`/exhibits/${encodeURIComponent(code)}`));

export const createPlan = session => call('/visit-plans', { method: 'POST', session });
export const getPlan = async (planCode, session) => normPlan(await call(`/visit-plans/${planCode}`, { session }));
export const addItem = (planCode, session, exhibitCode, allocatedMinutes) =>
  call(`/visit-plans/${planCode}/items`, { method: 'POST', session, body: { exhibitCode, allocatedMinutes } });
export const updateItem = (planCode, session, exhibitCode, allocatedMinutes) =>
  call(`/visit-plans/${planCode}/items/${encodeURIComponent(exhibitCode)}`, { method: 'PUT', session, body: { allocatedMinutes } });
export const removeItem = (planCode, session, exhibitCode) =>
  call(`/visit-plans/${planCode}/items/${encodeURIComponent(exhibitCode)}`, { method: 'DELETE', session });
