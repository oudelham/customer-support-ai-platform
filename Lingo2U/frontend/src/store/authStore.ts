import { create } from 'zustand';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem('Lingo2U_access'),
  refreshToken: localStorage.getItem('Lingo2U_refresh'),
  setTokens: (access, refresh) => {
    localStorage.setItem('Lingo2U_access', access);
    localStorage.setItem('Lingo2U_refresh', refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  logout: () => {
    localStorage.removeItem('Lingo2U_access');
    localStorage.removeItem('Lingo2U_refresh');
    set({ accessToken: null, refreshToken: null });
  },
}));
