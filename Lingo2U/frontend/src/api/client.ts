import { useAuthStore } from '../store/authStore';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function apiFetch(path: string, options: RequestInit = {}): Promise<any> {
  const { accessToken, refreshToken, setTokens, logout } = useAuthStore.getState();
  const headers = new Headers(options.headers || {});

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401 && refreshToken && !path.includes('/auth/')) {
    const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (refreshRes.ok) {
      const tokens = await refreshRes.json();
      setTokens(tokens.access_token, tokens.refresh_token);
      headers.set('Authorization', `Bearer ${tokens.access_token}`);
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } else {
      logout();
      window.location.href = '/login';
      throw new Error('Session expired');
    }
  }

  if (!response.ok) {
    const errBody = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(errBody.message || 'Server error');
  }

  if (response.status === 204) return null;
  return response.json();
}
