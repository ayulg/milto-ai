import { API_BASE } from '../config.js';
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeftIcon, ArrowTrendingUpIcon, ClockIcon, ExclamationTriangleIcon, CheckCircleIcon, SparklesIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

export default function CareerChangePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [current, setCurrent] = useState('');
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => { if (!user) navigate('/login'); }, [user, navigate]);

  const handleAnalyze = async () => {
    if (!current.trim() || !target.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/career-change`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current, target }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Analysis failed');
      setResult(data);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const difficultyColor = { low: 'text-green-400', moderate: 'text-[#d2a277]', medium: 'text-orange-400', high: 'text-red-400' };

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6">
          <ArrowLeftIcon className="w-4 h-4" /><span className="text-sm">Back to Dashboard</span>
        </Link>
        <div className="flex items-center gap-3 mb-3">
          <ArrowTrendingUpIcon className="w-8 h-8 text-[#d2a277]" />
          <h1 className="font-display font-bold text-3xl">Career Change Planner</h1>
        </div>
        <p className="text-gray-400 max-w-2xl">Thinking about switching careers? Tell me where you are and where you want to go.</p>
      </div>

      <div className="glass-card p-6 mb-6">
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Current Career</label>
            <input type="text" value={current} onChange={(e) => setCurrent(e.target.value)} placeholder="e.g., Teacher, Accountant" className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Target Career</label>
            <input type="text" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="e.g., Software Engineer" className="input" />
          </div>
        </div>
        <button onClick={handleAnalyze} disabled={!current.trim() || !target.trim() || loading} className="btn btn-primary w-full justify-center disabled:opacity-50">
          {loading ? 'Analyzing...' : 'Analyze My Transition'}
          {!loading && <ArrowRightIcon className="w-4 h-4" />}
        </button>
      </div>

      {error && <div className="glass-card p-4 border border-red-500/30 bg-red-500/5 mb-6"><p className="text-red-400 text-sm">{error}</p></div>}

      {loading && (
        <div className="glass-card p-12 text-center">
          <div className="w-12 h-12 border-4 border-[#d2a277] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Analyzing transition...</p>
        </div>
      )}

      {result && !loading && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="flex items-center gap-4 mb-6 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <p className="text-xs text-gray-400 mb-1">From</p>
                <h3 className="font-display font-bold text-xl">{result.current_career.title}</h3>
              </div>
              <ArrowRightIcon className="w-8 h-8 text-[#d2a277]" />
              <div className="flex-1 min-w-[200px]">
                <p className="text-xs text-gray-400 mb-1">To</p>
                <h3 className="font-display font-bold text-xl text-[#d2a277]">{result.target_career.title}</h3>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <p className="text-xs text-gray-400 mb-1">Overlap</p>
                <p className="font-display font-bold text-2xl text-green-400">{result.overlap_ratio}%</p>
              </div>
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <p className="text-xs text-gray-400 mb-1">Difficulty</p>
                <p className={`font-display font-bold text-2xl capitalize ${difficultyColor[result.difficulty]}`}>{result.difficulty}</p>
              </div>
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <p className="text-xs text-gray-400 mb-1">Timeline</p>
                <p className="font-display font-bold text-2xl">{result.estimated_months}mo</p>
              </div>
            </div>
          </div>

          {result.transferable_skills?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-green-400" />Your Transferable Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.transferable_skills.map((s, i) => (
                  <span key={i} className="px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/30 text-sm text-green-300">
                    {s.skill} · {s.strength}/5
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.skill_gaps?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-orange-400" />Skills to Build
              </h3>
              <div className="space-y-4">
                {result.skill_gaps.map((gap, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300 capitalize">{gap.skill}</span>
                      <span className="text-gray-500">{gap.current}/5 → {gap.needed}/5</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-orange-400 rounded-full" style={{ width: `${(gap.current / gap.needed) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="glass-card p-6">
            <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-[#d2a277]" />Bridge Plan ({result.estimated_months}-month roadmap)
            </h3>
            <div className="space-y-4">
              {result.bridge_plan.map((step, i) => (
                <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <p className="text-xs text-[#d2a277] font-medium mb-1">{step.phase}</p>
                  <h4 className="font-medium mb-2">{step.title}</h4>
                  <p className="text-sm text-gray-400 mb-2">{step.action}</p>
                  <p className="text-xs text-green-400">Target: {step.target}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4">Risks</h3>
              <ul className="space-y-2">
                {result.risks.map((r, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-orange-400">•</span><span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4">Success Factors</h3>
              <ul className="space-y-2">
                {result.success_factors.map((s, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-green-400">•</span><span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="glass-card p-4 border-l-4 border-[#d2a277]">
            <p className="text-xs text-gray-400">{result.disclaimer}</p>
          </div>

          <div className="flex gap-3 flex-wrap">
            <Link to="/coach" className="btn btn-primary">
              <SparklesIcon className="w-4 h-4" />Talk to AI Coach
            </Link>
            <button onClick={() => { setResult(null); setCurrent(''); setTarget(''); }} className="btn btn-secondary">Plan Another</button>
          </div>
        </div>
      )}
    </div>
  );
}
