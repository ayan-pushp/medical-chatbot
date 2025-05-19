import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const chatAPI = {
  sendMessage: (message, dialogState) => 
    api.post('/chat', { message, dialog_state: dialogState }),
  getHistory: () => api.get('/chat/history'),
};

export const authAPI = {
  login: async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await api.post('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    if (!response.access_token) {
      throw new Error(`Invalid response: ${JSON.stringify(response)}`);
    }

    return response;
  },

  register: async (username, password) => {
    try {
      const response = await api.post('/auth/register', {
        username,
        password
      });
      return response;
    } catch (error) {
      throw error; 
    }
  }
};
