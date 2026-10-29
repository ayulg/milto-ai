import { API_BASE } from '../config.js';
import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function LimitationPage() {
  const [career, setCareer] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!career) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/limitations`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ career })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error);
      setData(json);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-6 py-8">
      <Link to="/dashboard" className="text-gray-400 hover:text-white mb-6 block">← Back to Dashboard</Link>
      
      <h1 className="font-display font-bold text-3xl mb-4">Limitation Analysis</h1>
      <p className="text-gray-400 mb-6">Enter your dream career. We will ruthlessly analyze what is holding you back.</p>

      <div className="glass-card p-6 mb-6">
        <div className="flex gap-3">
          <input 
            type="text" 
            value={career} 
            onChange={e => setCareer(e.target.value)} 
            placeholder="e.g. Software Engineer, Doctor, Pilot"
            className="input flex-1"
          />
          <button onClick={handleCheck} disabled={loading} className="btn btn-primary">
            {loading ? 'Analyzing...' : 'Analyze My Gaps'}
          </button>
        </div>
      </div>

      {data && (
        <div className="space-y-6">
          <div className="glass-card p-6 border-l-4 border-red-500">
            <h2 className="text-xl font-bold mb-2">{data.target_career} Readiness: {data.readiness_score}%</h2>
            <p className="text-gray-400">{data.message}</p>
          </div>

          {data.limitations.map((lim, i) => (
            <div key={i} className="glass-card p-4 flex justify-between items-center border border-red-500/20">
              <div>
                <span className={`text-xs font-bold uppercase tracking-wide ${lim.severity === 'high' ? 'text-red-400' : 'text-yellow-400'}`}>
                  {lim.severity} Priority
                </span>
                <p className="font-medium text-lg mt-1">{lim.message}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{lim.current}/5</div>
                <div className="text-xs text-gray-500">Current</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}