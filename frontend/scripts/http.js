/** Requests use the same-origin Nginx API proxy. */
let hook = () => {};
export const setHttpLog = fn => { hook = fn; };

function messageFrom(payload, status) {
  if (payload?.message) return payload.message;
  if (typeof payload?.detail === 'string') return payload.detail;
  if (Array.isArray(payload?.detail)) return payload.detail.map(d => d.msg).join('; ');
  return `Request failed (${status}).`;
}

export async function request(path, { method = 'GET', body, session } = {}) {
  const headers = {};
  if (session) headers['X-Session-Code'] = session;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const entry = { time: new Date().toLocaleTimeString(), method, path: `/api${path}`, session, body };
  let response;
  try {
    response = await fetch(`/api${path}`, { method, headers, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
  } catch (networkError) {
    hook({ ...entry, status: 'NETWORK ERROR', response: networkError.message });
    throw networkError;
  }
  const payload = await response.json().catch(() => null);
  hook({ ...entry, status: response.status, response: payload });
  if (!response.ok) {
    const error = new Error(messageFrom(payload, response.status));
    error.code = payload?.error_code || 'REQUEST_FAILED';
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}