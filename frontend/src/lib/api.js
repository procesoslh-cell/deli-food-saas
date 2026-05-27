const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export async function api(path, options={}) {
  const res = await fetch(`${API_URL}${path}`, {headers:{'Content-Type':'application/json'}, ...options});
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}
export const get = (p) => api(p);
export const post = (p, body) => api(p, {method:'POST', body:JSON.stringify(body)});
