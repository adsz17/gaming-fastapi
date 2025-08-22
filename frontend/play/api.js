function headers(token) {
  const h = { 'Content-Type': 'application/json' };
  if (token) h['Authorization'] = 'Bearer ' + token;
  return h;
}

async function request(path, opts = {}, token) {
  const res = await fetch(path, {
    ...opts,
    headers: { ...headers(token), ...(opts.headers || {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export function getState(token) {
  return request('/crash/state', {}, token);
}

export function placeBet(amount, cashout, token) {
  return request('/crash/round', {
    method: 'POST',
    body: JSON.stringify({ bet: amount, cashout }),
  }, token);
}

export function getHistory(token) {
  return request('/history', {}, token);
}
