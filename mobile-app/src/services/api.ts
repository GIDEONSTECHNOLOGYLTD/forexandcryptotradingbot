import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Backend API URL
// ALWAYS use production backend for testing
const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for Render free tier cold starts
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

// Response interceptor with retry logic and error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Handle 401 errors (token expired)
    if (error.response?.status === 401) {
      await SecureStore.deleteItemAsync('authToken');
      return Promise.reject(error);
    }
    
    // Retry on timeout or network errors (max 3 retries with exponential backoff)
    if (!config || !config.retry) {
      config.retry = 0;
    }
    
    const shouldRetry = 
      error.code === 'ECONNABORTED' || 
      error.message.includes('timeout') || 
      error.message.includes('Network Error') ||
      error.message.includes('ETIMEDOUT') ||
      error.response?.status === 503 || // Service unavailable (cold start)
      error.response?.status === 502;   // Bad gateway
    
    if (config.retry < 3 && shouldRetry) {
      config.retry += 1;
      const delay = Math.min(1000 * Math.pow(2, config.retry - 1), 5000); // Max 5s delay
      console.log(`🔄 Retrying request (attempt ${config.retry}/3) after ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return api(config);
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

export const updateBot = async (botId: string, config: any) => {
  const response = await api.put(`/bots/${botId}`, config);
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

// Notification endpoints
export const savePushToken = async (pushToken: string) => {
  const response = await api.post('/user/push-token', { push_token: pushToken });
  return response.data;
};

export const getNotificationSettings = async () => {
  const response = await api.get('/user/notification-settings');
  return response.data;
};

export const updateNotificationSettings = async (settings: any) => {
  const response = await api.put('/user/notification-settings', settings);
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

export const getOpenPositions = async () => {
  const response = await api.get('/positions/open');
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

export const getUserBalance = async () => {
  const response = await api.get('/user/balance');
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
export const getCryptoNetworks = async () => {
  const response = await api.get('/payments/crypto/networks');
  return response.data;
};

export const initializeCryptoPayment = async (data: {
  plan: string;
  crypto_currency: string;
  network?: string;
  amount: number;
}) => {
  const response = await api.post('/payments/crypto/initialize', data);
  return response.data;
};

export const checkCryptoPaymentStatus = async (paymentId: string) => {
  const response = await api.get(`/payments/crypto/status/${paymentId}`);
  return response.data;
};

// In-App Purchase Verification
export const verifyInAppPurchase = async (data: {
  plan: string;
  receipt_data: string;
  platform: string;
}) => {
  const response = await api.post('/payments/iap/verify', data);
  return response.data;
};

// New Listing Bot
export const getNewListingBotStatus = async () => {
  const response = await api.get('/new-listing/status');
  return response.data;
};

export const startNewListingBot = async (config: {
  buy_amount_usdt: number;
  take_profit_percent: number;
  stop_loss_percent: number;
  max_hold_time: number;
}) => {
  const response = await api.post('/new-listing/start', config);
  return response.data;
};

export const stopNewListingBot = async () => {
  const response = await api.post('/new-listing/stop');
  return response.data;
};

export const updateNewListingBotConfig = async (config: {
  buy_amount_usdt: number;
  take_profit_percent: number;
  stop_loss_percent: number;
  max_hold_time: number;
}) => {
  const response = await api.put('/new-listing/config', config);
  return response.data;
};

// System Settings
export const getSystemSettings = async () => {
  const response = await api.get('/system/settings');
  return response.data;
};

export const updateSystemSettings = async (settings: any) => {
  const response = await api.put('/system/settings', settings);
  return response.data;
};

// Subscription Verification
export const verifySubscriptionPayment = async (paymentData: any) => {
  const response = await api.post('/subscriptions/verify-payment', paymentData);
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
  updateBot,
  deleteBot,
  getTrades,
  getPerformance,
  getPortfolio,
  getUserBalance,
  getTradeHistory,
  getOpenPositions,
  getBotAnalytics,
  getAISuggestions,
  createSubscription,
  getSubscription,
  updateProfile,
  getProfile,
  connectExchange,
  disconnectExchange,
  getExchangeStatus,
  initializePaystackPayment,
  getCryptoNetworks,
  initializeCryptoPayment,
  checkCryptoPaymentStatus,
  verifyInAppPurchase,
  getNewListingBotStatus,
  startNewListingBot,
  stopNewListingBot,
  updateNewListingBotConfig,
  getSystemSettings,
  updateSystemSettings,
  verifySubscriptionPayment,
};
