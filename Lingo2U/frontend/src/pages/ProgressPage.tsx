import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function ProgressPage() {
  const [progress, setProgress] = useState<any>(null);

  useEffect(() => {
    apiFetch('/progress').then(setProgress);
  }, []);

  if (!progress) return <div className="p-6">Loading progress...</div>;

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Your Learning Progress</h1>
        <Link to="/dashboard" className="text-blue-600 font-semibold">Back to Dashboard</Link>
      </header>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-6 rounded-2xl border border-slate-200">
          <div className="text-slate-500">Sessions Completed</div>
          <div className="text-4xl font-bold mt-2">{progress.completed_sessions}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200">
          <div className="text-slate-500">Minutes Practiced</div>
          <div className="text-4xl font-bold mt-2">{progress.total_minutes}</div>
        </div>
      </div>

      <section className="bg-white p-6 rounded-2xl border border-slate-200 space-y-3">
        <h2 className="text-xl font-bold">Most Common Mistake Areas</h2>
        {progress.mistake_trends?.length === 0 ? (
          <p className="text-slate-600">No mistakes recorded yet. Keep practicing!</p>
        ) : (
          <ul className="space-y-2">
            {progress.mistake_trends.map((m: any) => (
              <li key={m.error_type} className="flex justify-between p-3 bg-slate-50 rounded-xl">
                <span className="capitalize font-medium">{m.error_type.replace('_', ' ')}</span>
                <span className="font-bold text-slate-700">{m.count}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
