import axios from 'axios';

const API_BASE_URL = 'http://10.10.50.1:8000';

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

export default api;

export const labAPI = {
  list: () => api.get('/api/labs'),
  create: (data) => api.post('/api/labs', data),
  get: (name) => api.get(`/api/labs/${name}`),
  delete: (name) => api.delete(`/api/labs/${name}`),
  routers: (name) => api.get(`/api/labs/${name}/routers`),
  start: (name) => api.post(`/api/labs/${name}/start`),
  stop: (name) => api.post(`/api/labs/${name}/stop`),
};
