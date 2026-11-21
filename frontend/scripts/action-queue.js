/** Serialise collection reads and writes; failure does not block the next action. */
export function createActionQueue() {
  let pending = Promise.resolve();
  return operation => {
    const result = pending.then(operation);
    pending = result.catch(() => {});
    return result;
  };
}
