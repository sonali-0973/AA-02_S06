/** Requests use the same-origin Nginx API proxy. */
export async function request(path, { method = 'GET', body, session } = {}) {
  const headers = {};
  if (session) headers['X-Session-Code'] = session;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const response = await fetch(`/api${path}`, { method, headers, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(`Request failed (${response.status}).`);
    error.code = payload?.error_code || 'REQUEST_FAILED';
    throw error;
  }
  return payload;
}
