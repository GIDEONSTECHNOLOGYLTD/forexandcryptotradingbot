import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Change this to your backend URL
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api'  // Local development
  : 'https://your-production-domain.com/api';  // Production

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
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
};
