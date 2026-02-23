import axios from 'axios';
import { auth } from '../config/firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API endpoints
export const monitorService = {
  getAll: () => api.get('/api/monitors/'),
  getById: (id) => api.get(`/api/monitors/${id}`),
  create: (data) => api.post('/api/monitors/', data),
  update: (id, data) => api.put(`/api/monitors/${id}`, data),
  delete: (id) => api.delete(`/api/monitors/${id}`),
  getHealthChecks: (id, hours = 24) => 
    api.get(`/api/monitors/${id}/health-checks?hours=${hours}`),
  getDashboardStats: () => api.get('/api/monitors/dashboard/stats'),
};

export const metricsService = {
  getMonitorMetrics: (id, hours = 24) => 
    api.get(`/api/metrics/${id}?hours=${hours}`),
  getDailyMetrics: (id, days = 7) => 
    api.get(`/api/metrics/${id}/daily?days=${days}`),
};

export const alertService = {
  getMonitorAlerts: (id, limit = 50) => 
    api.get(`/api/alerts/${id}?limit=${limit}`),
  getUserAlerts: (limit = 100) => 
    api.get(`/api/alerts/?limit=${limit}`),
};

export const authService = {
  getCurrentUser: () => api.get('/api/auth/me'),
  verifyToken: () => api.get('/api/auth/verify'),
};

export default api;
