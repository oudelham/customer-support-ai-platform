import axios, { AxiosError, AxiosInstance } from "axios";
import { useAuthStore } from "../store/authStore";

const API_BASE_URL =
  import.meta.env.REACT_APP_API_URL || "http://localhost:8080/api/v1";

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: { "Content-Type": "application/json" }
    });

    this.client.interceptors.request.use((config) => {
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  get<T>(url: string, config = {}) {
    return this.client.get<T>(url, config);
  }

  post<T>(url: string, data?: unknown, config = {}) {
    return this.client.post<T>(url, data, config);
  }

  put<T>(url: string, data?: unknown, config = {}) {
    return this.client.put<T>(url, data, config);
  }
}

export const apiClient = new APIClient();