import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const getTransactions = (limit = 50, offset = 0) =>
  api.get(`/transactions?limit=${limit}&offset=${offset}`);

export const getAnomalies = (status = 'flagged', limit = 50, offset = 0) =>
  api.get(`/anomalies?status=${status}&limit=${limit}&offset=${offset}`);

export const getStats = () => api.get('/stats');

export const triggerDetect = () => api.post('/detect');

export default api;
