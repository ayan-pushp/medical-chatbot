import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      localStorage.setItem('token', response.access_token);
      setUser({ token: response.access_token });
      return true;
    } catch (error) {
      console.error('Login failed:', error.message);
      throw new Error(error.response?.data?.detail || error.message);
    }
  };

  const register = async (username, password) => {
    try {
      const response = await authAPI.register(username, password);
      return response;
    } catch (error) {
      console.error('Registration failed:', error.message);
      throw new Error(error.response?.data?.detail || error.message);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
