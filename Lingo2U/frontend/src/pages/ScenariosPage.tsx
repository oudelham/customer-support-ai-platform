import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function ScenariosPage() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<any[]>([]);

  useEffect(() => {
    apiFetch('/scenarios').then(setScenarios);
  }, []);

  const handleStart = async (scenarioId: string) => {
    const res = await apiFetch('/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
    navigate(`/session/${res.session_id}`);
  };

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Practice Scenarios</h1>
        <Link to="/dashboard" className="text-blue-600 font-semibold">Back to Dashboard</Link>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        {scenarios.map((s) => (
          <div key={s.id} className="bg-white p-5 rounded-2xl border border-slate-200 flex flex-col justify-between space-y-4">
            <div>
              <span className="text-xs font-bold px-2 py-1 rounded bg-slate-100 text-slate-700">{s.difficulty}</span>
              <h2 className="text-xl font-bold mt-2">{s.title}</h2>
              <p className="text-slate-600 text-sm mt-1">{s.description}</p>
            </div>
            <button
              onClick={() => handleStart(s.id)}
              className="w-full py-3 rounded-xl bg-blue-600 text-white font-bold hover:bg-blue-700"
            >
              Start Conversation
            </button>
          </div>
        ))}
      </div>
    </main>
  );
}
