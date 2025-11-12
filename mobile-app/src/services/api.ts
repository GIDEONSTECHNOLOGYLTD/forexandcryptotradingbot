import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Backend API URL
// ALWAYS use production backend for testing
const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased to 30 seconds for Render cold starts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, logout user
      await SecureStore.deleteItemAsync('authToken');
      // Navigate to login screen
    }
    return Promise.reject(error);
  }
);

// Authentication
export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  const { access_token } = response.data;
  await SecureStore.setItemAsync('authToken', access_token);
  return response.data;
};

export const signup = async (email: string, password: string, full_name: string) => {
  const response = await api.post('/auth/register', { email, password, full_name });
  return response.data;
};

export const logout = async () => {
  await SecureStore.deleteItemAsync('authToken');
};

// Dashboard
export const getDashboard = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

// Bots
export const getBots = async () => {
  const response = await api.get('/bots/my-bots');
  return response.data;
};

export const createBot = async (config: any) => {
  const response = await api.post('/bots/create', config);
  return response.data;
};

export const startBot = async (botId: string) => {
  const response = await api.post(`/bots/${botId}/start`);
  return response.data;
};

export const stopBot = async (botId: string) => {
  const response = await api.post(`/bots/${botId}/stop`);
  return response.data;
};

export const deleteBot = async (botId: string) => {
  const response = await api.delete(`/bots/${botId}`);
  return response.data;
};

export const getAISuggestions = async () => {
  const response = await api.get('/ai/suggestions');
  return response.data;
};

export const getBotAnalytics = async (botId: string) => {
  const response = await api.get(`/bots/${botId}/analytics`);
  return response.data;
};

export const getTradeHistory = async (botId?: string) => {
  const params = botId ? { bot_id: botId } : {};
  const response = await api.get('/trades/history', { params });
  return response.data;
};

// Trading
export const getTrades = async () => {
  const response = await api.get('/trades');
  return response.data;
};

export const getPerformance = async (botId: string) => {
  const response = await api.get(`/bots/${botId}/performance`);
  return response.data;
};

// Portfolio
export const getPortfolio = async () => {
  const response = await api.get('/portfolio');
  return response.data;
};

// Payments
export const createSubscription = async (plan: string, paymentMethod: string) => {
  const response = await api.post('/subscriptions/create', { plan, payment_method: paymentMethod });
  return response.data;
};

export const getSubscription = async () => {
  const response = await api.get('/subscriptions/my-subscription');
  return response.data;
};

// Settings
export const updateProfile = async (data: any) => {
  const response = await api.put('/users/me', data);
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

// Exchange Connection
export const connectExchange = async (credentials: {
  okx_api_key: string;
  okx_secret_key: string;
  okx_passphrase: string;
  paper_trading: boolean;
}) => {
  const response = await api.post('/user/connect-exchange', credentials);
  return response.data;
};

export const disconnectExchange = async () => {
  const response = await api.delete('/user/disconnect-exchange');
  return response.data;
};

export const getExchangeStatus = async () => {
  const response = await api.get('/user/exchange-status');
  return response.data;
};

// Paystack Payment
export const initializePaystackPayment = async (data: {
  email: string;
  amount: number;
  plan: string;
}) => {
  const response = await api.post('/payments/paystack/initialize', data);
  return response.data;
};

// Crypto Payment
export const initializeCryptoPayment = async (data: {
  plan: string;
  crypto_currency: string;
  amount: number;
}) => {
  const response = await api.post('/payments/crypto/initialize', data);
  return response.data;
};

export const checkCryptoPaymentStatus = async (paymentId: string) => {
  const response = await api.get(`/payments/crypto/status/${paymentId}`);
  return response.data;
};

export default {
  login,
  signup,
  logout,
  getDashboard,
  getBots,
  createBot,
  startBot,
  stopBot,
  getTrades,
  getPerformance,
  getPortfolio,
  createSubscription,
  getSubscription,
  updateProfile,
  getProfile,
  connectExchange,
  disconnectExchange,
  getExchangeStatus,
  initializePaystackPayment,
  initializeCryptoPayment,
  checkCryptoPaymentStatus,
};
