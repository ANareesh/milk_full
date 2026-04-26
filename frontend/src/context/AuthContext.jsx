/**
 * Authentication Context - Manages user auth state
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookie from 'js-cookie';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = Cookie.get('access_token');
    const userRole = Cookie.get('user_role');
    if (token && userRole) {
      setUser(JSON.parse(localStorage.getItem('user') || '{}'));
      setRole(userRole);
    }
    setLoading(false);
  }, []);

  const register = async (userData, isAgent = false, agentCode = null) => {
    try {
      const response = isAgent
        ? await authAPI.registerAgent(userData, agentCode)
        : await authAPI.register(userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login({ username, password });
      const { access_token, refresh_token } = response.data;
      
      // Store tokens
      Cookie.set('access_token', access_token, { expires: 1 });
      Cookie.set('refresh_token', refresh_token, { expires: 7 });
      
      // Decode and store user role
      const decoded = JSON.parse(atob(access_token.split('.')[1]));
      const roleValue = decoded.role?.value || decoded.role || String(decoded.role);
      Cookie.set('user_role', roleValue, { expires: 1 });
      setRole(roleValue);
      setUser(decoded);
      localStorage.setItem('user', JSON.stringify(decoded));
      
      return decoded;
    } catch (error) {
      throw error.response?.data || error;
    }
  };

  const logout = () => {
    Cookie.remove('access_token');
    Cookie.remove('refresh_token');
    Cookie.remove('user_role');
    localStorage.removeItem('user');
    setUser(null);
    setRole(null);
  };

  const value = {
    user,
    role,
    loading,
    register,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
