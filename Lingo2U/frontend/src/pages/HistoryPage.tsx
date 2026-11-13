import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function HistoryPage() {
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    apiFetch('/sessions').then(setSessions);
  }, []);

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Session History</h1>
        <Link to="/dashboard" className="text-blue-600 font-semibold">Back to Dashboard</Link>
      </header>
      <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
        {sessions.map((s) => (
          <div key={s.id} className="p-4 flex justify-between items-center">
            <div>
              <div className="font-bold text-lg">{s.scenario_title}</div>
              <div className="text-sm text-slate-500">
                {new Date(s.started_at).toLocaleString()} • {s.status}
              </div>
            </div>
            <Link to={`/session/${s.id}/report`} className="px-4 py-2 rounded-lg bg-blue-50 text-blue-700 font-semibold">
              Report
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}
