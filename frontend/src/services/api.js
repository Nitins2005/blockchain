import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  refresh: (data) => api.post('/auth/refresh', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  me: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
}

export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getFraudTrend: () => api.get('/admin/fraud-trend'),
  getVolumeTrend: () => api.get('/admin/volume-trend'),
  getBlockchainDistribution: () => api.get('/admin/blockchain-distribution'),
  getCategoryDistribution: () => api.get('/admin/category-distribution'),
  getSystemHealth: () => api.get('/admin/system-health'),
}

export const transactionsAPI = {
  getAll: (params) => api.get('/transactions', { params }),
  getById: (hash) => api.get(`/transactions/${hash}`),
  upload: (formData) => api.post('/transactions/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  export: (params) => api.get('/transactions/export', { params, responseType: 'blob' }),
}

export const walletsAPI = {
  getAll: (params) => api.get('/wallets', { params }),
  getByAddress: (address) => api.get(`/wallets/${address}`),
  create: (data) => api.post('/wallets', data),
  delete: (id) => api.delete(`/wallets/${id}`),
  getTransactions: (address) => api.get(`/wallets/${address}/transactions`),
}

export const graphAPI = {
  getStats: () => api.get('/graph/stats'),
  getWalletGraph: (address) => api.get(`/graph/wallet/${address}`),
  query: (data) => api.post('/graph/query', data),
  getCentralWallets: () => api.get('/graph/central-wallets'),
}

export const featuresAPI = {
  getWalletFeatures: (address) => api.get(`/features/wallet/${address}`),
  computeFeatures: (address) => api.post(`/features/compute/${address}`),
  computeAll: () => api.post('/features/compute-all'),
}

export const fraudAPI = {
  predict: (data) => api.post('/fraud/predict', data),
  getHistory: (address) => api.get(`/fraud/history/${address}`),
  getHighRisk: (params) => api.get('/fraud/high-risk', { params }),
  getStats: () => api.get('/fraud/stats'),
}

export const attributionAPI = {
  predict: (data) => api.post('/attribution/predict', data),
  getHistory: (address) => api.get(`/attribution/history/${address}`),
  getDistribution: () => api.get('/attribution/distribution'),
}

export const explainabilityAPI = {
  explain: (data) => api.post('/explainability/explain', data),
  getReport: (address) => api.get(`/explainability/report/${address}`),
}

export const aiAPI = {
  trainModel: () => api.post('/ai/train-model'),
  predictWallet: (data) => api.post('/ai/predict-wallet', data),
  walletAttribution: (data) => api.post('/ai/wallet-attribution', data),
  explainWallet: (data) => api.post('/ai/explain-wallet', data),
  getModelStatus: () => api.get('/ai/model-status'),
  getTrainingProgress: () => api.get('/ai/training-progress'),
}

export const blacklistAPI = {
  getAll: (params) => api.get('/blacklist', { params }),
  getById: (id) => api.get(`/blacklist/${id}`),
  create: (data) => api.post('/blacklist', data),
  update: (id, data) => api.put(`/blacklist/${id}`, data),
  delete: (id) => api.delete(`/blacklist/${id}`),
  check: (address) => api.get(`/blacklist/check/${address}`),
  importCSV: (formData) => api.post('/blacklist/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  exportCSV: () => api.get('/blacklist/export', { responseType: 'blob' }),
}

export const investigationsAPI = {
  getAll: (params) => api.get('/investigations', { params }),
  getById: (id) => api.get(`/investigations/${id}`),
  create: (data) => api.post('/investigations', data),
  update: (id, data) => api.put(`/investigations/${id}`, data),
  delete: (id) => api.delete(`/investigations/${id}`),
  attachWallet: (id, data) => api.post(`/investigations/${id}/wallets`, data),
  getWallets: (id) => api.get(`/investigations/${id}/wallets`),
  addNote: (id, data) => api.post(`/investigations/${id}/notes`, data),
  getNotes: (id) => api.get(`/investigations/${id}/notes`),
  generateReport: (id) => api.post(`/investigations/${id}/generate-report`),
}

export const reportsAPI = {
  getAll: () => api.get('/reports'),
  generate: (data) => api.post('/reports/generate', data),
  download: (id) => api.get(`/reports/${id}/download`, { responseType: 'blob' }),
}

export const notificationsAPI = {
  getAll: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/mark-all-read'),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  delete: (id) => api.delete(`/notifications/${id}`),
}

export const blockchainAPI = {
  getConfigs: () => api.get('/blockchain/configs'),
  updateConfig: (chain, data) => api.put(`/blockchain/configs/${chain}`, data),
  sync: (chain) => api.post(`/blockchain/sync/${chain}`),
  getStatus: () => api.get('/blockchain/status'),
}

export const usersAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
}

export default api
