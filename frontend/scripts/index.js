import { request } from './http.js';
import { createActionQueue } from './action-queue.js';
const sessionCode = crypto.randomUUID(); // Mock ownership marker, not authentication.
let collectionCode = null; // TODO: retain the create-or-return response's scenario code.
const enqueue = createActionQueue();
document.querySelector('#session').textContent = `Mock session: ${sessionCode}`;
async function run(button, operation) {
  button.disabled = true;
  try {
    const result = await operation();
    document.querySelector('#output').textContent = JSON.stringify(result, null, 2);
    document.querySelector('#status').textContent = 'Bootstrap request completed.';
  } catch (error) {
    document.querySelector('#status').textContent = `${error.message} ${error.code || ''}`;
  } finally { button.disabled = false; }
}
for (const [id, operation] of [
  ['health', () => request('/health')],
  ['catalogue', () => request('/catalogue')],
  ['collection', () => enqueue(() => request('/collections', { method: 'POST', session: sessionCode }))]
]) {
  const button = document.getElementById(id);
  button.addEventListener('click', () => run(button, operation));
}
// TODO: queue every collection read/write, send the same session header,
// await mutation then GET authoritative saved state; never invent success/totals.
