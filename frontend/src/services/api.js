import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL + '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Products
export const getProducts = (params = {}) => api.get('/products', { params });
export const getProduct = (id) => api.get(`/products/${id}`);
export const getCategories = () => api.get('/products/categories');

// Sales
export const getSales = (params = {}) => api.get('/sales', { params });
export const getSalesSummary = (params = {}) => api.get('/sales/summary', { params });

// Elasticity
export const calculateElasticity = (data) => api.post('/elasticity/calculate', data);
export const getProductElasticity = (productId, latest = true) => 
  api.get(`/elasticity/products/${productId}`, { params: { latest } });
export const getElasticityCurve = (productId) => api.get(`/elasticity/curve/${productId}`);
export const bulkCalculateElasticity = (data) => api.post('/elasticity/bulk-calculate', data);

// Scenarios
export const simulateScenario = (data) => api.post('/scenarios/simulate', data);
export const getScenarios = (params = {}) => api.get('/scenarios', { params });
export const getScenario = (id) => api.get(`/scenarios/${id}`);
export const compareScenarios = (scenarioIds) => 
  api.post('/scenarios/compare', { scenario_ids: scenarioIds });
export const bulkSimulateScenarios = (data) => api.post('/scenarios/bulk-simulate', data);

// Recommendations
export const getRecommendations = (params = {}) => api.get('/recommendations', { params });
export const getProductRecommendation = (productId) => api.get(`/recommendations/${productId}`);

// Analytics
export const getDashboardAnalytics = (days = 30) => 
  api.get('/analytics/dashboard', { params: { days } });

// Export
export const exportToExcel = (params = {}) => {
  return api.get('/export/excel', {
    params,
    responseType: 'blob',
  });
};

// Health
export const healthCheck = () => api.get('/health');

export default api;
