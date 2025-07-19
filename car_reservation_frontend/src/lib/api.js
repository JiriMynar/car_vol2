import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (intranetId) => api.post('/auth/login', { intranet_id: intranetId }),
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

// Vehicles API
export const vehiclesAPI = {
  getAll: (status = 'Active') => api.get('/vehicles', { params: { status } }),
  getById: (id) => api.get(`/vehicles/${id}`),
  create: (data) => api.post('/vehicles', data),
  update: (id, data) => api.put(`/vehicles/${id}`, data),
  delete: (id) => api.delete(`/vehicles/${id}`),
  checkAvailability: (id, startTime, endTime) => 
    api.get(`/vehicles/${id}/availability`, { 
      params: { start_time: startTime, end_time: endTime } 
    }),
};

// Reservations API
export const reservationsAPI = {
  getAll: (params = {}) => api.get('/reservations', { params }),
  getById: (id) => api.get(`/reservations/${id}`),
  create: (data) => api.post('/reservations', data),
  update: (id, data) => api.put(`/reservations/${id}`, data),
  cancel: (id) => api.delete(`/reservations/${id}`),
  getCalendarData: (startDate, endDate, vehicleId = null) => 
    api.get('/calendar', { 
      params: { start_date: startDate, end_date: endDate, vehicle_id: vehicleId } 
    }),
};

// Users API
export const usersAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  updateRole: (id, roleId) => api.put(`/users/${id}/role`, { role_id: roleId }),
  updateStatus: (id, isActive) => api.put(`/users/${id}/status`, { is_active: isActive }),
  getRoles: () => api.get('/roles'),
  createRole: (data) => api.post('/roles', data),
};

// Service Records API
export const serviceRecordsAPI = {
  getAll: (vehicleId = null) => api.get('/service-records', { 
    params: vehicleId ? { vehicle_id: vehicleId } : {} 
  }),
  getById: (id) => api.get(`/service-records/${id}`),
  create: (data) => api.post('/service-records', data),
  update: (id, data) => api.put(`/service-records/${id}`, data),
  delete: (id) => api.delete(`/service-records/${id}`),
  getByVehicle: (vehicleId) => api.get(`/vehicles/${vehicleId}/service-records`),
};

// Damage Records API
export const damageRecordsAPI = {
  getAll: (params = {}) => api.get('/damage-records', { params }),
  getById: (id) => api.get(`/damage-records/${id}`),
  create: (data) => api.post('/damage-records', data),
  update: (id, data) => api.put(`/damage-records/${id}`, data),
  delete: (id) => api.delete(`/damage-records/${id}`),
  getByVehicle: (vehicleId) => api.get(`/vehicles/${vehicleId}/damage-records`),
};

export default api;

