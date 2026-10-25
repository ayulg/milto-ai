import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { reflectionAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';

const PROMPT = 'What did you learn this week, what challenged you, and what is one small step you want to take next?';
export default function ReflectionsPage() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [response, setResponse] = useState('');
  const [reflections, setReflections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  useEffect(() => {
    if (authLoading) return;
    if (!user) { navigate('/login'); return; }
    reflectionAPI.get().then(res => setReflections(res.data.reflections || []))
      .catch(err => setError(err.response?.data?.error || 'Could not load reflections.'))
      .finally(() => setLoading(false));
  }, [user, authLoading, navigate]);
  const save = async (event) => {
    event.preventDefault(); if (!response.trim()) return;
    setSaving(true); setError(''); setNotice('');
    try {
      const res = await reflectionAPI.save(PROMPT, response.trim());
      setReflections(res.data.reflections || []); setResponse(''); setNotice('Reflection saved.');
    } catch (err) { setError(err.response?.data?.error || 'Could not save your reflection.'); }
    finally { setSaving(false); }
  };
  if (loading || authLoading) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading reflections…</div>;
  return <main className="min-h-screen max-w-3xl mx-auto px-6 py-8"><Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8"><ArrowLeftIcon className="w-4 h-4" /> Back to dashboard</Link><h1 className="font-display font-bold text-3xl mb-2">Weekly Reflection</h1><p className="text-gray-400 mb-6">Reflect on progress without judging yourself. Small steps count.</p><form onSubmit={save} className="glass-card p-6 mb-6"><p className="font-medium mb-4">{PROMPT}</p><textarea value={response} onChange={e => setResponse(e.target.value)} rows={5} maxLength={2000} className="input w-full mb-4" placeholder="Write your reflection…" required /><div className="flex items-center justify-between"><span className="text-xs text-gray-500">{response.length}/2000</span><button className="btn btn-primary" disabled={saving || !response.trim()}>{saving ? 'Saving…' : 'Save reflection'}</button></div>{error && <p role="alert" className="text-sm text-red-400 mt-3">{error}</p>}{notice && <p role="status" className="text-sm text-green-400 mt-3">{notice}</p>}</form><section className="glass-card p-6"><h2 className="font-display font-bold text-xl mb-4">Past reflections</h2>{reflections.length === 0 ? <p className="text-sm text-gray-400">Your saved reflections will appear here.</p> : <div className="space-y-4">{reflections.map(item => <article key={item.id} className="p-4 rounded-xl bg-white/5"><p className="text-xs text-gray-500 mb-2">{item.created_at ? new Date(item.created_at).toLocaleString() : item.day_key}</p><p className="text-sm text-gray-300 whitespace-pre-wrap">{item.response}</p></article>)}</div>}</section></main>;
}
