const API = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API Error');
  }
  return res.json();
}

export const auth = {
  register: (username, password) => request('/auth/register', { method: 'POST', body: JSON.stringify({ username, password }) }),
  login: (username, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
};

export const characters = {
  create: (username, name, class_name, race = 'Mensch') =>
    request('/characters/create', { method: 'POST', body: JSON.stringify({ username, name, class_name, race }) }),
  list: (username) => request(`/characters/list/${username}`),
  all: () => request('/characters/all'),
  get: (id) => request(`/characters/${id}`),
};

export const adventure = {
  start: (username, character_id) =>
    request('/adventure/start', { method: 'POST', body: JSON.stringify({ username, character_id }) }),
  startMulti: (character_ids) =>
    request('/adventure/start_multi', { method: 'POST', body: JSON.stringify({ character_ids }) }),
  action: (session_id, action_text, character_name) =>
    request('/adventure/action', { method: 'POST', body: JSON.stringify({ session_id, action_text, character_name }) }),
  state: (session_id) => request(`/adventure/state/${session_id}`),
};
