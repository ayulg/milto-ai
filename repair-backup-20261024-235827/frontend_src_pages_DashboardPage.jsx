import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../api/client';
import { ArrowRightIcon, SparklesIcon, ChartBarIcon, AcademicCapIcon } from '@heroicons/react/24/outline';
import NotificationBell from '../components/common/NotificationBell';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, loading: authLoading, logout } = useAuth();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate('/login');
      return;
    }
    loadResults();
  }, [user, authLoading]);

   const loadResults = async () => {
  try {
    // Always load the latest assessment saved for this logged-in account.
    const response = await assessmentAPI.getResults();
    const data = response.data;

    if (data.assessment) {
      // The backend nests saved profile and analysis inside "assessment".
      const savedResults = {
        ...data,
        ...data.assessment,
      };

      setResults(savedResults);
      sessionStorage.setItem(
        'milto_results',
        JSON.stringify(savedResults)
      );
    } else {
      sessionStorage.removeItem('milto_results');
      navigate('/assessment');
    }
  } catch (err) {
    console.error(
      'Could not load saved assessment:',
      err.response?.status,
      err.response?.data || err.message
    );
    setLoadError(err.response?.data?.error || err.message || 'Could not load saved results. Please try again.');
  } finally {
    setLoading(false);
  }
};

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-[#d2a277] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!results && loadError) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="glass-card p-8 max-w-lg w-full">
          <h2 className="text-xl font-bold mb-3">Could not load your saved results</h2>
          <p className="text-red-400 mb-6">{loadError}</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Try again
          </button>
          <button onClick={() => navigate('/assessment')} className="btn ml-3">
            Start a new assessment
          </button>
        </div>
      </div>
    );
  }

  if (!results) return null;

  const { profile, analysis, recommendations, hollandCode, hollandNarrative } = results;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#d2a277] flex items-center justify-center font-bold text-xl text-[#0b1117]">
              M
            </div>
            <span className="font-display font-bold text-xl">Milto AI</span>
          </Link>
          <div className="flex items-center gap-3">
            <NotificationBell />
            <Link to="/coach" className="btn btn-secondary text-sm">AI Coach</Link>
            <button onClick={handleLogout} className="btn btn-secondary text-sm">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* Welcome */}
        <div className="mb-10">
          <p className="text-[#d2a277] text-sm font-medium mb-2">Your Milto Profile</p>
          <h1 className="font-display font-bold text-4xl md:text-5xl mb-3">
            Hello, {user?.username}
          </h1>
          <p className="text-gray-400 max-w-3xl">
            Based on your assessment, here is your personality analysis and top career matches.
          </p>
        </div>

        {/* 10-Level Analysis */}
        {analysis && (
          <section className="mb-10">
            <h2 className="font-display font-bold text-2xl mb-5 flex items-center gap-2">
              <AcademicCapIcon className="w-6 h-6 text-[#d2a277]" />
              10-Level Analysis
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(analysis).map(([key, level]) => (
                <div key={key} className="glass-card p-4 text-center">
                  <div className="text-3xl font-display font-bold text-[#d2a277] mb-1">
                    {level.score}
                  </div>
                  <div className="text-xs text-gray-400">{level.name}</div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Holland Code */}
        <section className="mb-10">
          <div className="glass-card p-8">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div>
                <p className="text-sm text-gray-400 mb-2">Your Holland Code (RIASEC)</p>
                <div className="font-display font-bold text-6xl tracking-wider text-[#d2a277]">
                  {hollandCode}
                </div>
              </div>
              <div className="flex-1">
                <p className="text-gray-300">{hollandNarrative}.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Top 10 Career Matches */}
        <section className="mb-10">
          <h2 className="font-display font-bold text-2xl mb-5 flex items-center gap-2">
            <ChartBarIcon className="w-6 h-6 text-[#d2a277]" />
            Top 10 Career Matches
          </h2>
          <div className="space-y-3">
            {recommendations?.map((rec, idx) => (
              <CareerMatchCard key={rec.career.id} rank={idx + 1} rec={rec} />
            ))}
          </div>
        </section>

        {/* Next Steps */}
        <section>
          <h2 className="font-display font-bold text-2xl mb-5 flex items-center gap-2">
            <SparklesIcon className="w-6 h-6 text-[#d2a277]" />
            Next Steps
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <Link to="/coach" className="glass-card p-6 hover:border-[#d2a277]/30 transition-all">
              <h3 className="font-display font-bold text-xl mb-2">Talk to AI Coach</h3>
              <p className="text-gray-400 text-sm mb-4">
                Get personalized advice about any career path.
              </p>
              <span className="text-[#d2a277] text-sm font-medium inline-flex items-center gap-1">
                Start chatting <ArrowRightIcon className="w-4 h-4" />
              </span>
            </Link>
            <Link to="/career-lab" className="glass-card p-6 hover:border-[#d2a277]/30 transition-all">
              <h3 className="font-display font-bold text-xl mb-2">Explore a Career</h3>
              <p className="text-gray-400 text-sm mb-4">
                Want a career not in your top 10? Analyze any path.
              </p>
              <span className="text-[#d2a277] text-sm font-medium inline-flex items-center gap-1">
                Open Career Lab <ArrowRightIcon className="w-4 h-4" />
              </span>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

function CareerMatchCard({ rank, rec }) {
  const { career, match_percentage, reasons } = rec;
  const pct = match_percentage || Math.round((rec.score || 0) * 100);

  return (
    <div className="glass-card p-5 hover:border-[#d2a277]/30 transition-all">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-[#d2a277]/10 flex items-center justify-center font-display font-bold text-xl text-[#d2a277]">
          {rank}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start gap-4 mb-2">
            <div>
              <h3 className="font-display font-bold text-lg">{career.title}</h3>
              <p className="text-sm text-gray-400">{career.cluster}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-display font-bold text-[#d2a277]">{pct}%</div>
              <div className="text-xs text-gray-500">match</div>
            </div>
          </div>
          <p className="text-sm text-gray-400 mb-3">{career.summary}</p>
          {reasons && reasons.length > 0 && (
            <div className="text-xs text-gray-500">
              <strong className="text-gray-400">Why it fits:</strong> {reasons[0]}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


