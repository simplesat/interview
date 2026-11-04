import axios from 'axios';
import { camelizeKeys, decamelizeKeys } from 'humps';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/',
});

api.interceptors.request.use((config) => {
  if (config.data && typeof config.data === 'object') {
    config.data = decamelizeKeys(config.data);
  }
  return config;
});

api.interceptors.response.use(
  (response) => {
    if (response.data && typeof response.data === 'object') {
      response.data = camelizeKeys(response.data);
    }
    return response;
  },
  (error) => {
    const data = axios.isAxiosError(error) ? error.response?.data : undefined;
    if (data && typeof data === 'object') {
      error.response.data = camelizeKeys(data);
    }
    return Promise.reject(error);
  },
);
