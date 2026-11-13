import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [recentSessions, setRecentSessions] = useState<any[]>([]);

  useEffect(() => {
    apiFetch('/scenarios').then(setScenarios);
    apiFetch('/progress').then(setProgress);
    apiFetch('/sessions').then((list) => setRecentSessions(list.slice(0, 3)));
  }, []);

  const startRecommended = async (scenarioId: string) => {
    const res = await apiFetch('/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
    navigate(`/session/${res.session_id}`);
  };

  const recommended = scenarios[0];

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Lingo2U</h1>
        <nav className="flex gap-4 text-base font-medium text-blue-600">
          <Link to="/scenarios">Scenarios</Link>
          <Link to="/history">History</Link>
          <Link to="/progress">Progress</Link>
          <Link to="/settings">Settings</Link>
        </nav>
      </header>

      {recommended && (
        <section className="bg-blue-600 text-white rounded-2xl p-6 space-y-3">
          <span className="text-xs uppercase tracking-wider bg-blue-500 px-3 py-1 rounded-full">
            Recommended Next Scenario
          </span>
          <h2 className="text-2xl font-bold">{recommended.title}</h2>
          <p className="text-blue-100">{recommended.description}</p>
          <button
            onClick={() => startRecommended(recommended.id)}
            className="px-6 py-3 rounded-xl bg-white text-blue-700 font-bold text-lg"
          >
            Start Speaking Now
          </button>
        </section>
      )}

      {progress && (
        <section className="grid grid-cols-2 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200">
            <div className="text-sm text-slate-500">Completed Sessions</div>
            <div className="text-3xl font-bold mt-1">{progress.completed_sessions}</div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200">
            <div className="text-sm text-slate-500">Minutes Practiced</div>
            <div className="text-3xl font-bold mt-1">{progress.total_minutes}</div>
          </div>
        </section>
      )}

      <section className="bg-white p-6 rounded-2xl border border-slate-200 space-y-3">
        <h3 className="text-xl font-bold">Recent Sessions</h3>
        {recentSessions.length === 0 ? (
          <p className="text-slate-600">No sessions yet. Pick a scenario above to begin!</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {recentSessions.map((s) => (
              <li key={s.id} className="py-3 flex justify-between items-center">
                <div>
                  <div className="font-semibold">{s.scenario_title}</div>
                  <div className="text-sm text-slate-500">
                    {new Date(s.started_at).toLocaleDateString()}
                  </div>
                </div>
                <Link to={`/session/${s.id}/report`} className="text-blue-600 font-semibold">
                  View Report
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
