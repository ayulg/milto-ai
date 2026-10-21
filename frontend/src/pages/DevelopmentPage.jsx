import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeftIcon, SparklesIcon, ClockIcon, CheckCircleIcon, LightBulbIcon, BookOpenIcon } from '@heroicons/react/24/outline';

export default function DevelopmentPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => { if (!user) navigate('/login'); }, [user, navigate]);

  const handleCreate = async (query = null) => {
    const q = query || goal;
    if (!q.trim()) return;
    setLoading(true); setError(''); setPlan(null);
    try {
      const res = await fetch('http://localhost:5000/api/development/plan', {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: q }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setPlan(data);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const examples = ['extraversion', 'discipline', 'confidence', 'programming', 'writing', 'leadership'];

  return (
    <div className="min-h-screen max-w-5xl mx-auto px-6 py-8">
      <div className="mb-8">
        <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6">
          <ArrowLeftIcon className="w-4 h-4" />
          <span className="text-sm">Back to Dashboard</span>
        </Link>
        <div className="flex items-center gap-3 mb-3">
          <SparklesIcon className="w-8 h-8 text-[#d2a277]" />
          <h1 className="font-display font-bold text-3xl">Personal Development</h1>
        </div>
        <p className="text-gray-400 max-w-2xl">Want to change a personality trait or build a skill? Get a 12-week plan.</p>
      </div>

      <div className="glass-card p-6 mb-6">
        <label className="block text-sm font-medium mb-3">What do you want to develop?</label>
        <div className="flex gap-3">
          <input type="text" value={goal} onChange={(e) => setGoal(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            placeholder="e.g., extraversion, discipline, programming..."
            className="input flex-1" disabled={loading} />
          <button onClick={() => handleCreate()} disabled={!goal.trim() || loading}
            className="btn btn-primary disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Plan'}
          </button>
        </div>
        <div className="mt-4">
          <p className="text-xs text-gray-500 mb-2">Or try:</p>
          <div className="flex flex-wrap gap-2">
            {examples.map(ex => (
              <button key={ex} onClick={() => { setGoal(ex); handleCreate(ex); }}
                className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs hover:border-[#d2a277]/50 capitalize">
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="glass-card p-4 border border-red-500/30 bg-red-500/5 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {loading && (
        <div className="glass-card p-12 text-center">
          <div className="w-12 h-12 border-4 border-[#d2a277] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Building your plan...</p>
        </div>
      )}

      {plan && !loading && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${plan.goal_type === 'skill' ? 'bg-blue-500/10 border border-blue-500/30 text-blue-300' : 'bg-purple-500/10 border border-purple-500/30 text-purple-300'}`}>
              {plan.goal_type}
            </span>
            <h2 className="font-display font-bold text-3xl mb-2 mt-3">{plan.goal_name}</h2>
            <p className="text-gray-400">{plan.goal_description}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-green-400" />Daily Habits
              </h3>
              <ul className="space-y-2">
                {plan.daily_habits.map((h, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-green-400">•</span><span>{h}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <BookOpenIcon className="w-5 h-5 text-[#d2a277]" />Resources
              </h3>
              <ul className="space-y-2">
                {plan.resources.map((r, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-[#d2a277]">•</span><span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-[#d2a277]" />Week-by-Week Plan
            </h3>
            <div className="grid md:grid-cols-2 gap-3">
              {plan.weekly_activities.map((w) => (
                <div key={w.week} className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-display font-bold text-lg text-[#d2a277]">Week {w.week}</span>
                    <span className="text-xs text-gray-400">{w.theme}</span>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{w.activity}</p>
                  <p className="text-xs text-gray-500 italic">Focus: {w.focus}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
              <LightBulbIcon className="w-5 h-5 text-yellow-400" />Milestones
            </h3>
            <div className="space-y-3">
              {plan.milestones.map((m, i) => (
                <div key={i} className="flex gap-4 p-3 rounded-xl bg-white/5">
                  <div className="w-12 h-12 rounded-xl bg-[#d2a277]/10 border border-[#d2a277]/30 flex items-center justify-center font-display font-bold text-[#d2a277] flex-shrink-0">
                    W{m.week}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">{m.milestone}</p>
                    <p className="text-xs text-gray-400">Evidence: {m.evidence}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 flex-wrap">
            <Link to="/coach" className="btn btn-primary">
              <SparklesIcon className="w-4 h-4" />Talk to AI Coach
            </Link>
            <button onClick={() => { setPlan(null); setGoal(''); }} className="btn btn-secondary">
              Plan Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
