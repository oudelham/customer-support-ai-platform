import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [nativeLanguage, setNativeLanguage] = useState('Spanish');
  const [goal, setGoal] = useState('daily_life');
  const [level, setLevel] = useState<'A1' | 'A2'>('A1');
  const [explainInNative, setExplainInNative] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch('/users/me', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        native_language: nativeLanguage,
        goal,
        level,
        explain_in_native: explainInNative,
        onboarding_completed: true,
      }),
    });
    navigate('/dashboard');
  };

  return (
    <main className="max-w-lg mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Welcome to Lingo2U</h1>
      <p className="text-slate-600 text-lg">Let us personalize Sam, your English speaking tutor.</p>

      <form onSubmit={handleSubmit} className="space-y-5 bg-white p-6 rounded-2xl border border-slate-200">
        <div>
          <label className="block font-semibold mb-2">Your Native Language</label>
          <select
            value={nativeLanguage}
            onChange={(e) => setNativeLanguage(e.target.value)}
            className="w-full border border-slate-300 rounded-xl p-3 text-lg"
          >
            <option value="Spanish">Spanish</option>
            <option value="Portuguese">Portuguese</option>
            <option value="Arabic">Arabic</option>
            <option value="French">French</option>
            <option value="Mandarin">Mandarin</option>
            <option value="Japanese">Japanese</option>
            <option value="Malay">Malay</option>
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-2">Your Main Goal</label>
          <select
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="w-full border border-slate-300 rounded-xl p-3 text-lg"
          >
            <option value="daily_life">Daily Life Conversations</option>
            <option value="travel">Travel & Vacations</option>
            <option value="work">Workplace & Career</option>
            <option value="study">Study & School</option>
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-2">Your English Level</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setLevel('A1')}
              className={`p-4 rounded-xl border text-left ${
                level === 'A1' ? 'border-blue-600 bg-blue-50 font-bold' : 'border-slate-300'
              }`}
            >
              <div>Absolute Beginner (A1)</div>
              <div className="text-xs text-slate-600 font-normal mt-1">I know basic words only</div>
            </button>
            <button
              type="button"
              onClick={() => setLevel('A2')}
              className={`p-4 rounded-xl border text-left ${
                level === 'A2' ? 'border-blue-600 bg-blue-50 font-bold' : 'border-slate-300'
              }`}
            >
              <div>Beginner (A2)</div>
              <div className="text-xs text-slate-600 font-normal mt-1">I can make simple sentences</div>
            </button>
          </div>
        </div>

        <label className="flex items-center gap-3 pt-2">
          <input
            type="checkbox"
            checked={explainInNative}
            onChange={(e) => setExplainInNative(e.target.checked)}
            className="w-5 h-5"
          />
          <span className="text-base">Translate grammar correction tips into my native language</span>
        </label>

        <button
          type="submit"
          className="w-full py-4 rounded-xl bg-blue-600 text-white font-bold text-lg hover:bg-blue-700"
        >
          Start Practicing
        </button>
      </form>
    </main>
  );
}
