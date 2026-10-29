import { API_BASE } from '../config.js';
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeftIcon, SparklesIcon, ClockIcon, CheckCircleIcon, LightBulbIcon, BookOpenIcon, BriefcaseIcon, AcademicCapIcon } from '@heroicons/react/24/outline';

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
      const res = await fetch(`${API_BASE}/api/development/plan`, {
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

  const examples = [
    { group: 'Personal strengths', items: ['confidence', 'discipline', 'communication', 'leadership', 'time management'] },
    { group: 'Digital & technical', items: ['programming', 'data analysis', 'AI skills', 'cybersecurity', 'web design'] },
    { group: 'Creative & practical', items: ['writing', 'dancing', 'photography', 'public speaking', 'problem solving'] },
    { group: 'Career-ready', items: ['teamwork', 'project management', 'research', 'customer service', 'entrepreneurship'] },
  ];

  return (
    <div className="min-h-screen w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-5 sm:py-8">
      <div className="mb-8">
        <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6">
          <ArrowLeftIcon className="w-4 h-4" />
          <span className="text-sm">Back to Dashboard</span>
        </Link>
        <div className="flex items-start gap-3 mb-3">
          <div className="w-11 h-11 shrink-0 rounded-2xl bg-[#d2a277]/10 border border-[#d2a277]/20 flex items-center justify-center"><SparklesIcon className="w-6 h-6 text-[#d2a277]" /></div>
          <div className="min-w-0"><p className="text-xs uppercase tracking-[.18em] text-[#d2a277] mb-1">Build your next capability</p><h1 className="font-display font-bold text-2xl sm:text-3xl md:text-4xl">Personal Development</h1></div>
        </div>
        <p className="text-gray-400 max-w-2xl leading-7">Create a practical 12-week plan for almost any skill, career capability, or personal strength. Start small, practice consistently, and track evidence of progress.</p>
      </div>

      <div className="glass-card p-4 sm:p-6 lg:p-7 mb-6">
        <div className="flex items-center gap-2 mb-3"><BriefcaseIcon className="w-5 h-5 text-[#d2a277]" /><label htmlFor="development-goal" className="text-sm font-semibold">What do you want to develop?</label></div>
        <form onSubmit={(e) => { e.preventDefault(); handleCreate(); }} className="flex flex-col sm:flex-row gap-3">
          <input id="development-goal" type="text" value={goal} onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., dancing, nursing skills, Excel, teamwork..." aria-label="Skill or trait to develop"
            className="input min-w-0 flex-1" disabled={loading} maxLength={100} />
          <button type="submit" disabled={!goal.trim() || loading} className="btn btn-primary justify-center disabled:opacity-50 sm:shrink-0">
            {loading ? 'Building plan…' : 'Create 12-week plan'} <SparklesIcon className="w-4 h-4" />
          </button>
        </form>
        <div className="mt-6 space-y-5">
          {examples.map(group => <div key={group.group}><p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{group.group}</p><div className="flex flex-wrap gap-2">{group.items.map(ex => <button type="button" key={ex} disabled={loading} onClick={() => { setGoal(ex); handleCreate(ex); }} className="px-3 py-2 rounded-xl bg-white/[.035] border border-white/10 text-xs sm:text-sm text-gray-300 hover:text-white hover:border-[#d2a277]/60 hover:bg-[#d2a277]/[.07] transition-colors disabled:opacity-50">{ex}</button>)}</div></div>)}
        </div>
        <p className="mt-5 text-xs text-gray-500">You can enter a skill even if it is not listed above. Plans are starting guides—adapt them to your time, access, and experience.</p>
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
        <div className="space-y-5 sm:space-y-6">
          <div className="glass-card p-5 sm:p-7">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${plan.goal_type === 'skill' ? 'bg-blue-500/10 border border-blue-500/30 text-blue-300' : 'bg-purple-500/10 border border-purple-500/30 text-purple-300'}`}>
              {plan.goal_type}
            </span>
            <h2 className="font-display font-bold text-3xl mb-2 mt-3">{plan.goal_name}</h2>
            <p className="text-gray-400">{plan.goal_description}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
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
