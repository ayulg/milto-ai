export const API_BASE = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' &&
   ['localhost', '127.0.0.1'].includes(window.location.hostname)
    ? `http://${window.location.hostname}:5000`
    : '')
).replace(/\/+$/, '');
