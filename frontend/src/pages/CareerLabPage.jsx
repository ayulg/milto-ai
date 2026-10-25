import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { careerAPI } from '../api/client';
import {
  ArrowLeftIcon, MagnifyingGlassIcon, ChartBarIcon,
  AcademicCapIcon, SparklesIcon, CheckCircleIcon
} from '@heroicons/react/24/outline';

export default function CareerLabPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) navigate('/login');
  }, [user, navigate]);

  const handleExplore = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await careerAPI.explorePath(q);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    'Software Engineer', 'Doctor', 'AI Engineer', 'Nurse',
    'Teacher', 'Data Scientist', 'Product Manager', 'Cybersecurity Analyst',
  ];

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6">
          <ArrowLeftIcon className="w-4 h-4" />
          <span className="text-sm">Back to Dashboard</span>
        </Link>

        <div className="flex items-center gap-3 mb-3">
          <MagnifyingGlassIcon className="w-8 h-8 text-[#d2a277]" />
          <h1 className="font-display font-bold text-3xl">Career Lab</h1>
        </div>
        <p className="text-gray-400 max-w-2xl">
          Explore <strong>any</strong> career path — even if it's not in your top 10 matches.
        </p>
      </div>

      <div className="glass-card p-6 mb-6">
        <label className="block text-sm font-medium mb-3">What career do you want to explore?</label>
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleExplore()}
            placeholder="e.g., Software Engineer, Doctor, AI Engineer..."
            className="input flex-1"
            disabled={loading}
          />
          <button
            onClick={() => handleExplore()}
            disabled={!query.trim() || loading}
            className="btn btn-primary disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        <div className="mt-4">
          <p className="text-xs text-gray-500 mb-2">Or try:</p>
          <div className="flex flex-wrap gap-2">
            {examples.map(ex => (
              <button
                key={ex}
                onClick={() => { setQuery(ex); handleExplore(ex); }}
                className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs hover:border-[#d2a277]/50"
              >
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
          <p className="text-gray-400">Analyzing your fit...</p>
        </div>
      )}

      {result && !loading && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
              <div>
                <p className="text-xs text-[#d2a277] mb-1">Career Path Analysis</p>
                <h2 className="font-display font-bold text-3xl">
                  {result.matchedCareer?.title || result.query}
                </h2>
                <p className="text-sm text-gray-400 mt-1">{result.matchedCareer?.cluster || 'General'}</p>
              </div>
              <div className="text-center">
                <div className={`font-display font-bold text-5xl mb-1 ${
                  result.fit >= 70 ? 'text-green-400' :
                  result.fit >= 50 ? 'text-[#d2a277]' : 'text-orange-400'
                }`}>
                  {result.fit}%
                </div>
                <p className="text-xs text-gray-400 uppercase tracking-wide">{result.status} fit</p>
              </div>
            </div>
            {result.matchedCareer?.summary && (
              <p className="text-gray-300">{result.matchedCareer.summary}</p>
            )}
          </div>

          {result.matchedCareer && (
            <EthiopianContext careerId={result.matchedCareer.id} />
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-green-400" />
                Your Strengths
              </h3>
              {result.strengths?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {result.strengths.map((s, i) => (
                    <span key={i} className="px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/30 text-sm text-green-300">
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No strong signals yet.</p>
              )}
            </div>

            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <ChartBarIcon className="w-5 h-5 text-orange-400" />
                Skills to Develop
              </h3>
              {result.gaps?.length > 0 ? (
                <div className="space-y-3">
                  {result.gaps.slice(0, 4).map((gap, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">{gap.skill}</span>
                        <span className="text-gray-500">{gap.have}/{gap.need}</span>
                      </div>
                      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-orange-400 rounded-full"
                          style={{ width: `${(gap.have / gap.need) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No major gaps!</p>
              )}
            </div>
          </div>

          {result.difficulties?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4">⚠️ What to Expect</h3>
              <ul className="space-y-2">
                {result.difficulties.map((d, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-3">
                    <span className="text-[#d2a277]">•</span>
                    <span>{d}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.steps?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                <AcademicCapIcon className="w-5 h-5 text-[#d2a277]" />
                Your Bridge Plan
              </h3>
              <div className="space-y-4">
                {result.steps.map((step, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#d2a277]/10 border border-[#d2a277]/30 flex items-center justify-center font-display font-bold text-[#d2a277] flex-shrink-0">
                      W{step.week}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium mb-1">{step.title}</h4>
                      <p className="text-sm text-gray-400 mb-1">{step.action}</p>
                      <p className="text-xs text-[#d2a277]">Target: {step.target}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => {
                const careerName = result.matchedCareer?.title || result.query || query;
                const prompt = `Act as my personalized Milto career coach. Help me build skills for ${careerName}.

Career Lab assessment:
- Fit score: ${result.fit ?? "Not assessed"}%
- Status: ${result.status || "Not assessed"}
- Strengths: ${result.strengths?.join(", ") || "Not yet identified"}
- Skill gaps: ${result.gaps?.map(g => `${g.skill} (current ${g.have}, target ${g.need})`).join("; ") || "Not yet assessed"}
- Suggested steps: ${result.steps?.map(s => `Week ${s.week}: ${s.title} ? ${s.action}`).join("; ") || "Not available"}

Create a practical weekly development plan with priorities, exercises, milestones, and ways to measure progress. Treat missing information as unknown, not zero. These results are estimates. Ask focused questions if needed. Be supportive, direct, and specific.`;
                navigate("/coach", { state: { initialPrompt: prompt } });
              }}
              className="btn btn-primary"
            >
              Build My Personal Development Plan ?
            </button>
            <button
              onClick={() => { setResult(null); setQuery(''); }}
              className="btn btn-secondary"
            >
              Explore Another
            </button>
          </div>
        </div>
      )}

      {!result && !loading && !error && (
        <div className="glass-card p-12 text-center">
          <MagnifyingGlassIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="font-display font-bold text-xl mb-2">Ready to explore?</h3>
          <p className="text-gray-400">Enter any career and I'll analyze your fit.</p>
        </div>
      )}
    </div>
  );
}

function EthiopianContext({ careerId }) {
  const [ctx, setCtx] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!careerId) {
      setLoading(false);
      return;
    }
    fetch(`http://localhost:5000/api/ethiopian/career/${careerId}`)
      .then(r => r.json())
      .then(data => setCtx(data.context || null))
      .catch(() => setCtx(null))
      .finally(() => setLoading(false));
  }, [careerId]);

  if (loading || !ctx) return null;

  return (
    <div className="glass-card p-6 border-l-4 border-yellow-500">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🇪🇹</span>
        <h3 className="font-display font-bold text-lg">Ethiopian Job Market</h3>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-400 mb-1">Local Demand</p>
          <p className="font-medium capitalize">{ctx.local_demand}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 mb-1">Salary Range (ETB/month)</p>
          <p className="font-medium">{ctx.salary_range_etb}</p>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-xs text-gray-400 mb-2">Top Employers in Ethiopia</p>
        <div className="flex flex-wrap gap-2">
          {ctx.employers?.map((e, i) => (
            <span key={i} className="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs">
              {e}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <p className="text-xs text-gray-400 mb-2">Relevant University Programs</p>
        <div className="flex flex-wrap gap-2">
          {ctx.top_programs?.map((p, i) => (
            <span key={i} className="px-2 py-1 rounded-lg bg-[#d2a277]/10 border border-[#d2a277]/30 text-xs text-[#d2a277]">
              {p}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}