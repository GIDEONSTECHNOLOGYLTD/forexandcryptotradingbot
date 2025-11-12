import React, { createContext, useState, useContext, useEffect } from 'react';
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
      const userData = await api.getProfile();
      setUser({
        email: userData.email,
        full_name: userData.full_name || '',
        role: userData.role || 'user',
        subscription: userData.subscription || 'free',
        exchange_connected: userData.exchange_connected || false,
      });
    } catch (error) {
      console.error('Failed to fetch user:', error);
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
