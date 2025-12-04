import axios from 'axios';

// Dynamic API URL - uses localhost:8000 when tunneling, or detects from window location
const getApiBaseUrl = () => {
  // If accessing via localhost (SSH tunnel), use localhost:8000
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // Otherwise use the same hostname with port 8000
  return `${window.location.protocol}//${window.location.hostname}:8000`;
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const routerAPI = {
  list: () => api.get('/api/routers'),
  create: (data) => api.post('/api/routers', data),
  delete: (name) => api.delete(`/api/routers/${name}`),
  get: (name) => api.get(`/api/routers/${name}`),
  start: (name) => api.post(`/api/routers/${name}/start`),
  stop: (name) => api.post(`/api/routers/${name}/stop`),
  restart: (name) => api.post(`/api/routers/${name}/restart`),
};

export const statsAPI = {
  system: () => api.get('/api/stats/system'),
  router: (name) => api.get(`/api/stats/routers/${name}`),
};

export const topologyAPI = {
  list: () => api.get('/api/topologies'),
  save: (data) => api.post('/api/topologies', data),
  load: (name) => api.get(`/api/topologies/${name}`),
  delete: (name) => api.delete(`/api/topologies/${name}`),
};

export const labAPI = {
  list: () => api.get('/api/labs'),
  create: (data) => api.post('/api/labs', data),
  get: (name) => api.get(`/api/labs/${name}`),
  delete: (name) => api.delete(`/api/labs/${name}`),
  routers: (name) => api.get(`/api/labs/${name}/routers`),
  start: (name) => api.post(`/api/labs/${name}/start`),
  stop: (name) => api.post(`/api/labs/${name}/stop`),
};

export const consoleAPI = {
  createSession: (name) => api.post(`/api/routers/${name}/console/session`),
  getSession: (token) => api.get(`/api/console/${token}`),
  closeSession: (token) => api.delete(`/api/console/${token}`),
};

export default api;
