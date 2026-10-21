import axios from 'axios';

// Use the SAME domain as the browser URL to avoid cookie issues
// If frontend is on http://localhost:5173, use http://localhost:5000
// If frontend is on http://127.0.0.1:5173, use http://127.0.0.1:5000
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

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
  register: (username, password) => api.post('/api/register', { username, password }),
  login: (username, password) => api.post('/api/login', { username, password }),
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