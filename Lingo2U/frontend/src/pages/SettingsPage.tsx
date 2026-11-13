import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api/client';
import { useAuthStore } from '../store/authStore';

export default function SettingsPage() {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const [profile, setProfile] = useState<any>(null);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    apiFetch('/users/me').then(setProfile);
  }, []);

  const handleToggleNative = async (checked: boolean) => {
    const updated = await apiFetch('/users/me', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ explain_in_native: checked }),
    });
    setProfile(updated);
    setStatusMsg('Settings saved.');
  };

  const handleDeleteTranscripts = async () => {
    if (!window.confirm('Delete all transcripts, reports, and progress history?')) return;
    await apiFetch('/users/me/transcripts', { method: 'DELETE' });
    setStatusMsg('All transcripts and reports have been deleted.');
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Permanently delete your account and all data?')) return;
    await apiFetch('/users/me', { method: 'DELETE' });
    logout();
    navigate('/');
  };

  if (!profile) return <div className="p-6">Loading settings...</div>;

  return (
    <main className="max-w-xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Settings & Privacy</h1>
        <Link to="/dashboard" className="text-blue-600 font-semibold">Back to Dashboard</Link>
      </header>

      {statusMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-xl">
          {statusMsg}
        </div>
      )}

      <section className="bg-white p-6 rounded-2xl border border-slate-200 space-y-4">
        <h2 className="text-xl font-bold">Learning Preferences</h2>
        <label className="flex items-center justify-between gap-4">
          <span>Explain grammar corrections in {profile.native_language}</span>
          <input
            type="checkbox"
            checked={profile.explain_in_native}
            onChange={(e) => handleToggleNative(e.target.checked)}
            className="w-5 h-5"
          />
        </label>
      </section>

      <section className="bg-white p-6 rounded-2xl border border-slate-200 space-y-3">
        <h2 className="text-xl font-bold">Privacy & Data Control</h2>
        <p className="text-sm text-slate-600">
          Lingo2U processes your voice recordings in memory to create transcripts and never stores raw audio files by default. Transcripts and session reports are stored until you delete them.
        </p>
        <div className="pt-2 flex flex-col gap-3">
          <button
            onClick={handleDeleteTranscripts}
            className="w-full py-3 rounded-xl border border-rose-300 text-rose-700 font-semibold hover:bg-rose-50"
          >
            Delete All Transcripts & Reports
          </button>
          <button
            onClick={handleDeleteAccount}
            className="w-full py-3 rounded-xl bg-rose-600 text-white font-semibold hover:bg-rose-700"
          >
            Delete Account & All Data
          </button>
        </div>
      </section>
    </main>
  );
}
