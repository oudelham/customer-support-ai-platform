import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <main className="max-w-2xl mx-auto min-h-screen flex flex-col justify-center p-6 text-center space-y-6">
      <h1 className="text-4xl font-extrabold text-slate-900">Lingo2U</h1>
      <p className="text-xl text-slate-600">
        Practice speaking English slowly and safely with Sam, your patient AI tutor for beginners.
      </p>
      <div className="flex gap-4 justify-center">
        <Link to="/register" className="px-8 py-4 rounded-xl bg-blue-600 text-white font-bold text-lg">
          Get Started Free
        </Link>
        <Link to="/login" className="px-8 py-4 rounded-xl border border-slate-300 font-bold text-lg">
          Log In
        </Link>
      </div>
    </main>
  );
}
