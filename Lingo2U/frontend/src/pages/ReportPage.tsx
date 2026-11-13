import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api/client';

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    apiFetch(`/sessions/${id}`).then((data) => {
      if (data.report) {
        setReport(data.report);
      } else {
        apiFetch(`/sessions/${id}/end`, { method: 'POST' }).then(setReport);
      }
    });
  }, [id]);

  if (!report) {
    return <div className="p-8 text-center text-xl">Generating your session report...</div>;
  }

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Session Report</h1>

      <section className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 space-y-2">
        <h2 className="text-lg font-bold text-emerald-900">Great Effort!</h2>
        <p className="text-emerald-800 text-base">{report.summary}</p>
        <p className="text-sm text-emerald-700 font-medium">Strengths: {report.strengths}</p>
      </section>

      {report.top_mistakes?.length > 0 && (
        <section className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4">
          <h2 className="text-xl font-bold">Sentences to Practice (Top {report.top_mistakes.length})</h2>
          {report.top_mistakes.map((m: any, i: number) => (
            <div key={i} className="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-1">
              <div className="text-sm text-rose-700 line-through">{m.wrong}</div>
              <div className="text-base font-bold text-emerald-800">{m.right}</div>
              <div className="text-sm text-slate-700">{m.why}</div>
            </div>
          ))}
        </section>
      )}

      {report.new_words?.length > 0 && (
        <section className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3">
          <h2 className="text-xl font-bold">Key Vocabulary</h2>
          <ul className="space-y-2">
            {report.new_words.map((w: any, i: number) => (
              <li key={i} className="p-3 bg-slate-50 rounded-xl">
                <span className="font-bold">{w.word}</span>: {w.meaning}
                <div className="text-sm text-slate-600 italic mt-1">"{w.example}"</div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="bg-blue-50 border border-blue-200 rounded-2xl p-5">
        <h2 className="font-bold text-blue-900">Next Step Tip</h2>
        <p className="text-blue-800 mt-1">{report.next_tip}</p>
      </section>

      <div className="flex gap-4">
        <Link to="/scenarios" className="flex-1 py-4 text-center rounded-xl bg-blue-600 text-white font-bold text-lg">
          Practice Another Scenario
        </Link>
        <Link to="/dashboard" className="flex-1 py-4 text-center rounded-xl bg-slate-200 text-slate-800 font-bold text-lg">
          Back to Dashboard
        </Link>
      </div>
    </main>
  );
}
