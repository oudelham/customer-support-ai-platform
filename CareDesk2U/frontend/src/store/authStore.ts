import { create } from "zustand";
import { AuthResponse, User } from "../types";
import { authService } from "../services/authService";

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setAuthFromResponse: (response: AuthResponse) => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  refreshToken: localStorage.getItem("refresh_token"),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login({ email, password });
      get().setAuthFromResponse(response);
    } catch (error: any) {
      set({ error: error?.message || "Login failed" });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    void authService.logout();
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, token: null, refreshToken: null });
  },

  setAuthFromResponse: (response) => {
    localStorage.setItem("access_token", response.accessToken);
    if (response.refreshToken) {
      localStorage.setItem("refresh_token", response.refreshToken);
    }
    set({
      user: response.user,
      token: response.accessToken,
      refreshToken: response.refreshToken ?? null
    });
  },

  isAuthenticated: () => Boolean(get().token)
}));

export const restoreAuth = () => {
  const token = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");
  if (token) {
    useAuthStore.setState({ token, refreshToken });
  }
};