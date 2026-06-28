import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT_MS } from '../constants/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    'Accept': 'application/json',
  },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'Network error';
    return Promise.reject(new Error(message));
  },
);

export default client;
