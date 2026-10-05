import { apiClient } from "./api";
import { AuthResponse, User } from "../types";

interface LoginRequest {
  email: string;
  password: string;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/login", credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Logout remains local if the server is unavailable.
    }
  },

  async refreshToken(refreshToken: string): Promise<{ accessToken: string }> {
    const response = await apiClient.post<{ accessToken: string }>("/auth/refresh", {
      refreshToken
    });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    // The supplied Java backend does not expose /auth/me.
    throw new Error("The Java backend does not expose /api/v1/auth/me; use the user returned by /api/v1/auth/login.");
  }
};