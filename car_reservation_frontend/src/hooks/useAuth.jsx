import { useState, useEffect, createContext, useContext } from 'react';
import { authAPI } from '@/lib/api';
import { getStoredToken, getStoredUser, setAuthData, clearAuthData } from '@/lib/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      const token = getStoredToken();
      const storedUser = getStoredUser();

      if (token && storedUser) {
        try {
          // Verify token is still valid
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          // Token is invalid, clear stored data
          clearAuthData();
          setUser(null);
          setIsAuthenticated(false);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (intranetId) => {
    try {
      const response = await authAPI.login(intranetId);
      const { access_token, user: userData } = response.data;
      
      setAuthData(access_token, userData);
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Přihlášení se nezdařilo' 
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Ignore logout errors
    } finally {
      clearAuthData();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const isAdmin = () => {
    return user && user.role_name === 'Fleet Administrator';
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    isAdmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

