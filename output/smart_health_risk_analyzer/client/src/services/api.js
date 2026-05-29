javascript
import axios from 'axios';

// Base URL for the API
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

// Service for making API calls
const api = {
  // User authentication
  signup: (userData) => {
    return axios.post(`${API_BASE_URL}/auth/signup`, userData);
  },
  
  login: (credentials) => {
    return axios.post(`${API_BASE_URL}/auth/login`, credentials);
  },

  // File upload
  uploadMedicalReport: (formData, token) => {
    return axios.post(`${API_BASE_URL}/reports/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    });
  },

  // Fetch user dashboard data
  getDashboardData: (token) => {
    return axios.get(`${API_BASE_URL}/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  },

  // Fetch user history
  getUserHistory: (token) => {
    return axios.get(`${API_BASE_URL}/history`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }
};

export default api;