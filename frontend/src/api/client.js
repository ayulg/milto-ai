import axios from 'axios';

// Use the SAME domain as the browser URL to avoid cookie issues
// If frontend is on http://localhost:5173, use http://localhost:5000
// If frontend is on http://127.0.0.1:5173, use http://127.0.0.1:5000
const API_HOST = typeof window !== 'undefined' && window.location.hostname === '127.0.0.1' ? '127.0.0.1' : 'localhost';
const API_BASE = `http://${API_HOST}:5000`;

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Debug interceptor
api.interceptors.request.use((config) => {
  console.log(`📤 ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (email, password) => api.post('/api/register', { email, password }),
  login: (email, password) => api.post('/api/login', { email, password }),
  logout: () => api.post('/api/logout'),
  me: () => api.get('/api/me'),
};

export const assessmentAPI = {
  submit: (answers) => api.post('/api/assessment', { answers }),
  getResults: () => api.get('/api/results'),
  getHistory: () => api.get('/api/history'),
};

export const careerAPI = {
  explorePath: (interest) => api.post('/api/explore-path', { interest }),
  submitFeedback: (careerId, rating) => api.post('/api/feedback', { careerId, rating }),
  getMeta: () => api.get('/api/meta'),
};

export const coachAPI = {
  sendMessage: (message) => api.post('/api/coach', { message }),
  getAIStatus: () => api.get('/api/ai-status'),
};

export default api;
export const profileAPI = {
  get: () => api.get('/api/profile'),
  update: (profile) => api.put('/api/profile', profile),
};

export const notificationsAPI = {
  get: () => api.get('/api/notifications'),
  dismiss: (id) => api.post('/api/notifications/dismiss', { id }),
};

export const activityAPI = {
  complete: (activityId, difficulty = 'just-right', note = '') =>
    api.post('/api/activity/complete', { activityId, difficulty, note }),
};

export const reflectionAPI = {
  get: () => api.get('/api/reflections'),
  save: (prompt, response) => api.post('/api/reflections', { prompt, response }),
};

export const dailyAPI = {
  get: () => api.get('/api/daily'),
  toggleTask: (date, taskId, done) => api.post('/api/daily/task', { date, taskId, done }),
};
