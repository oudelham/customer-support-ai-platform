import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function RegisterPage() {
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const tokens = await apiFetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, display_name: displayName }),
      });
      setTokens(tokens.access_token, tokens.refresh_token);
      navigate('/onboarding');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="max-w-md mx-auto min-h-screen flex flex-col justify-center p-6">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl border border-slate-200 space-y-4">
        <h1 className="text-2xl font-bold">Create Account</h1>
        {error && <div className="p-3 bg-rose-50 text-rose-700 rounded-lg text-sm">{error}</div>}
        <input
          type="text"
          placeholder="Your Name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="w-full border border-slate-300 rounded-xl p-3"
        />
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-slate-300 rounded-xl p-3"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder="Password (min 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-slate-300 rounded-xl p-3"
        />
        <button type="submit" className="w-full py-3 rounded-xl bg-blue-600 text-white font-bold">
          Sign Up
        </button>
        <p className="text-sm text-center text-slate-600">
          Already have an account? <Link to="/login" className="text-blue-600 font-semibold">Log In</Link>
        </p>
      </form>
    </main>
  );
}
