/**
 * API Service - Handles all HTTP requests
 */

import axios from 'axios';
import Cookie from 'js-cookie';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use((config) => {
  const token = Cookie.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      Cookie.remove('access_token');
      Cookie.remove('user_role');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (userData) => api.post('/auth/register/customer', userData),
  registerAgent: (userData, agentCode) => 
    api.post('/auth/register/agent', { ...userData, agent_code: agentCode }),
  login: (credentials) => api.post('/auth/login', credentials),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  verifyResetToken: (token) => api.get(`/auth/verify-reset-token/${token}`),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};


export const collectMilk = async (data, token) => {
  return axios.post(
    "/api/v1/milk-collection/",
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
};

// Product APIs
export const productAPI = {
  getAll: (skip = 0, limit = 100) => api.get('/products', { params: { skip, limit } }),
  list: (skip = 0, limit = 10) => api.get('/products', { params: { skip, limit } }),
  search: (query, skip = 0, limit = 10) => 
    api.get('/products/search', { params: { query, skip, limit } }),
  getByType: (type, skip = 0, limit = 10) => 
    api.get(`/products/type/${type}`, { params: { skip, limit } }),
  getDetails: (id) => api.get(`/products/${id}`),
  create: (productData) => api.post('/products', productData),
  update: (id, productData) => api.put(`/products/${id}`, productData),
  delete: (id) => api.delete(`/products/${id}`),
  uploadImage: (productId, file) => {
    const formData = new FormData();
    formData.append("file", file);
    
    return api.post(`/products/${productId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Order APIs
// Order APIs
export const orderAPI = {
  create: (orderData) => api.post('/orders', orderData),
  getMyOrders: (status = null) => api.get('/orders/my-orders', { params: { status } }),
  getDetails: (id) => api.get(`/orders/${id}`),
  confirm: (id) => api.post(`/orders/${id}/confirm`),
  cancel: (id) => api.post(`/orders/${id}/cancel`),
  getAllOrders: (status = null, skip = 0, limit = 50) =>
    api.get('/orders/admin/all', { params: { status, skip, limit } }),
  // alias used by admin pages:
  getAll: (status = null, skip = 0, limit = 50) =>
    api.get('/orders/admin/all', { params: { status, skip, limit } }),
};

// Delivery APIs
// export const deliveryAPI = {
//   assignAgent: (deliveryId, agentId) => 
//     api.post(`/deliveries/${deliveryId}/assign-agent`, { agent_id: agentId }),
//   start: (id) => api.post(`/deliveries/${id}/start`),
//   complete: (id, data) => api.post(`/deliveries/${id}/complete`, data),
//   verifyOTP: (id, otp) => api.post(`/deliveries/${id}/verify-otp`, { otp }),
//   getMyDeliveries: () => api.get('/deliveries/agent/my-deliveries'),
//   getDetails: (id) => api.get(`/deliveries/${id}`),
//   fail: (id, reason) => api.post(`/deliveries/${id}/fail`, { reason }),
// };

// Payment APIs
export const paymentAPI = {
  createUPI: (paymentData) => api.post('/payments/upi', paymentData),
  createCard: (paymentData) => api.post('/payments/card', paymentData),
  createCash: (paymentData) => api.post('/payments/cash', paymentData),
  getMyPayments: (skip = 0, limit = 10) => 
    api.get('/payments/my-payments', { params: { skip, limit } }),
  getDetails: (id) => api.get(`/payments/${id}`),
  refund: (id, reason) => api.post(`/payments/${id}/refund`, { reason }),
  getAllPayments: (status = null, skip = 0, limit = 50) => 
    api.get('/payments/admin/all', { params: { status, skip, limit } }),
};

// Customer APIs
// export const customerAPI = {
//   getProfile: () => api.get('/customers/profile'),
//   updateProfile: (data) => api.put('/customers/profile', data),
//   getActiveSubscriptions: () => api.get('/customers/subscriptions/active'),
//   getCustomer: (id) => api.get(`/customers/${id}`),
//   getAllCustomers: (skip = 0, limit = 50) => 
//     api.get('/customers/admin/all', { params: { skip, limit } }),
//   getCustomersWithPendingBalance: (skip = 0, limit = 50) => 
//     api.get('/customers/admin/pending-balance', { params: { skip, limit } }),
// };

export const customerAPI = {
  getProfile: () => api.get('/customers/profile'),
  updateProfile: (data) => api.put('/customers/profile', data),
  getActiveSubscriptions: () => api.get('/customers/subscriptions/active'),
  getCustomer: (id) => api.get(`/customers/${id}`),
  getAllCustomers: (skip = 0, limit = 50) => 
    api.get('/customers/admin/all', { params: { skip, limit } }),
  getCustomersWithPendingBalance: (skip = 0, limit = 50) => 
    api.get('/customers/admin/pending-balance', { params: { skip, limit } }),
  // Aliases for frontend pages:
  getAll: (skip = 0, limit = 50) => 
    api.get('/customers/admin/all', { params: { skip, limit } }),
  getPendingBalance: (skip = 0, limit = 50) => 
    api.get('/customers/admin/pending-balance', { params: { skip, limit } }),
};

// Agent APIs
// Agent APIs
export const agentAPI = {
  getProfile: () => api.get('/agents/profile'),
  updateProfile: (data) => api.put('/agents/profile', data),
  updateLocation: (data) => api.post('/agents/location', data),
  getAssignedDeliveries: () => api.get('/agents/deliveries/assigned'),
  getAgent: (id) => api.get(`/agents/${id}`),
  getAllAgents: (skip = 0, limit = 50) =>
    api.get('/agents/admin/all', { params: { skip, limit } }),
  getAvailableAgents: (skip = 0, limit = 50) =>
    api.get('/agents/admin/available', { params: { skip, limit } }),
  // aliases used by admin pages:
  getAll: (skip = 0, limit = 50) =>
    api.get('/agents/admin/all', { params: { skip, limit } }),
  getAvailable: (skip = 0, limit = 50) =>
    api.get('/agents/admin/available', { params: { skip, limit } }),
};

// Subscription APIs
// export const subscriptionAPI = {
//   create: (subscriptionData) => api.post('/subscriptions', subscriptionData),
//   getMySubscriptions: (status = null) => 
//     api.get('/subscriptions/my-subscriptions', { params: { status } }),
//   getDetails: (id) => api.get(`/subscriptions/${id}`),
//   update: (id, data) => api.put(`/subscriptions/${id}`, data),
//   pause: (id) => api.post(`/subscriptions/${id}/pause`),
//   resume: (id) => api.post(`/subscriptions/${id}/resume`),
//   cancel: (id) => api.post(`/subscriptions/${id}/cancel`),
// };

// Review APIs
// export const reviewAPI = {
//   create: (reviewData) => api.post('/reviews', reviewData),
//   getProductReviews: (productId, skip = 0, limit = 10) => 
//     api.get(`/reviews/product/${productId}`, { params: { skip, limit } }),
//   getMyReviews: () => api.get('/reviews/my-reviews'),
//   update: (id, data) => api.put(`/reviews/${id}`, data),
//   delete: (id) => api.delete(`/reviews/${id}`),
//   getProductRating: (productId) => api.get(`/reviews/product/${productId}/rating`),
// };

// Admin APIs
export const adminAPI = {
  getDashboardStats: () => api.get('/admin/reports/dashboard-stats'),
  getRevenueReport: (days = 30) => 
    api.get('/admin/reports/revenue-report', { params: { days } }),
  getDeliveryReport: (days = 30) => 
    api.get('/admin/reports/delivery-report', { params: { days } }),
  getProductReport: () => api.get('/admin/reports/product-report'),
  getCustomerReport: () => api.get('/admin/reports/customer-report'),
};
export const deliveryAPI = {
  assignAgent: (deliveryId, agentId) => 
    api.post(`/deliveries/${deliveryId}/assign-agent`, { agent_id: agentId }),
  start: (id) => api.post(`/deliveries/${id}/start`),
  complete: (id, data) => api.post(`/deliveries/${id}/complete`, data),
  verifyOtp: (id, data) => api.post(`/deliveries/${id}/verify-otp`, data),
  getMyDeliveries: () => api.get('/deliveries/agent/my-deliveries'),
  getDetails: (id) => api.get(`/deliveries/${id}`),
  fail: (id, data) => api.post(`/deliveries/${id}/fail`, data),
  getPending: () => api.get('/deliveries/admin/pending'),
  getAll: (status = null) => 
    api.get('/deliveries/admin/all', { params: status ? { status } : {} }),
};

// Review APIs
export const reviewAPI = {
  create: (reviewData) => api.post('/reviews', reviewData),
  getMyReviews: () => api.get('/reviews/my-reviews'),
  getProductReviews: (productId) => api.get(`/reviews/product/${productId}`),
  update: (reviewId, reviewData) => api.put(`/reviews/${reviewId}`, reviewData),
  delete: (reviewId) => api.delete(`/reviews/${reviewId}`),
};

export const subscriptionAPI = {
  create: (subscriptionData) => api.post('/subscriptions', subscriptionData),
  
  getMySubscriptions: (skip = 0, limit = 10, status = null) =>
    api.get('/subscriptions/my-subscriptions', { 
      params: { skip, limit, ...(status && { status }) } 
    }),
  
  getDetails: (id) => api.get(`/subscriptions/${id}`),
  
  update: (id, data) => api.put(`/subscriptions/${id}`, data),
  
  pause: (id, pauseData) => api.post(`/subscriptions/${id}/pause`, pauseData),
  
  resume: (id) => api.post(`/subscriptions/${id}/resume`),
  
  cancel: (id) => api.delete(`/subscriptions/${id}`),
  
  getStats: () => api.get('/subscriptions/stats/summary'),
};


// Location APIs
export const locationAPI = {
  updateLocation: (locationData) => 
    api.post('/locations/update', locationData),
  
  getCurrentLocation: () => 
    api.get('/locations/current'),
  
  getLocationHistory: (hours = 24) => 
    api.get('/locations/history', { params: { hours } }),
  
  getDeliveryRoute: (deliveryId) => 
    api.get(`/locations/delivery/${deliveryId}`),
  
  getAllAgentsMap: () => 
    api.get('/locations/admin/agents-map'),
  
  calculateDistance: (lat1, lon1, lat2, lon2) => 
    api.post('/locations/calculate-distance', null, {
      params: { lat1, lon1, lat2, lon2 }
    }),
  
  cleanupLocations: (days = 30) => 
    api.delete('/locations/cleanup', { params: { days } }),
};

// Map API endpoints
export const mapAPI = {
  // Admin - Get all agents on map
  getAdminAgentsMap: async () => {
    return axios.get(`${API_BASE_URL}/locations/map/admin/agents`);
  },

  // Customer - Get active delivery tracking
  getCustomerDeliveryTracking: async () => {
    return axios.get(`${API_BASE_URL}/locations/map/customer/delivery-tracking`);
  },

  // Get delivery route for map
  getDeliveryRoute: async (deliveryId) => {
    return axios.get(`${API_BASE_URL}/locations/map/delivery/${deliveryId}/route`);
  },

  // Get map statistics
  getMapStats: async () => {
    return axios.get(`${API_BASE_URL}/locations/map/stats`);
  }
};



export default api;
