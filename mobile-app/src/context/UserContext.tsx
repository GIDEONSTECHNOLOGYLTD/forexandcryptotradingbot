import React, { createContext, useState, useContext, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import * as api from '../services/api';

interface User {
  email: string;
  full_name: string;
  role: 'admin' | 'user';
  subscription: 'free' | 'pro' | 'enterprise';
  exchange_connected: boolean;
}

interface UserContextType {
  user: User | null;
  isAdmin: boolean;
  loading: boolean;
  refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType>({
  user: null,
  isAdmin: false,
  loading: true,
  refreshUser: async () => {},
});

export const useUser = () => useContext(UserContext);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    try {
      // Check if user has auth token first
      const token = await SecureStore.getItemAsync('authToken');
      if (!token) {
        console.log('⚠️ No auth token found, skipping user fetch');
        setUser(null);
        setLoading(false);
        return;
      }

      console.log('🔄 Fetching user profile...');
      const userData = await api.getProfile();
      console.log('👤 User data loaded:', {
        email: userData.email,
        role: userData.role,
        isAdmin: userData.role === 'admin'
      });
      setUser({
        email: userData.email,
        full_name: userData.full_name || '',
        role: userData.role || 'user',
        subscription: userData.subscription || 'free',
        exchange_connected: userData.exchange_connected || false,
      });
    } catch (error: any) {
      console.error('❌ Failed to fetch user:', error.message || error);
      // If 401, clear token
      if (error.response?.status === 401) {
        await SecureStore.deleteItemAsync('authToken');
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const isAdmin = user?.role === 'admin';

  return (
    <UserContext.Provider value={{ user, isAdmin, loading, refreshUser }}>
      {children}
    </UserContext.Provider>
  );
};
