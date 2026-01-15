import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../api/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const isGuest = user && !user.email;
  const isAuthenticated = user && !!user.email;

  useEffect(() => {
    refreshUser();
  }, []);

  const refreshUser = async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await authService.login(email, password);
    setUser({
      userId: response.user.userId,
      email: response.user.email,
      type: 'registered',
    });
  };

  const register = async (email, password) => {
    const response = await authService.register(email, password);
    setUser({
      userId: response.user.userId,
      email: response.user.email,
      type: 'registered',
    });
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const value = {
    user,
    isGuest,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
