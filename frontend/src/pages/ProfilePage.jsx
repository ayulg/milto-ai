import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { profileAPI, assessmentAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, loading: authLoading, checkAuth } = useAuth();
  const [profile, setProfile] = useState({ display_name: '', study_stage: '', goals: '', interests: '' });
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    if (authLoading) return;
    if (!user) { navigate('/login'); return; }
    let active = true;
    Promise.all([profileAPI.get(), assessmentAPI.getHistory()])
      .then(([profileResponse, historyResponse]) => {
        if (!active) return;
        setProfile({
          display_name: profileResponse.data.profile?.display_name || '',
          study_stage: profileResponse.data.profile?.study_stage || '',
          goals: profileResponse.data.profile?.goals || '',
          interests: profileResponse.data.profile?.interests || '',
        });
        setHistory(historyResponse.data.history || []);
      })
      .catch(err => { if (active) setError(err.response?.data?.error || 'Could not load your profile.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [user, authLoading, navigate]);

  const updateField = (event) => setProfile(current => ({ ...current, [event.target.name]: event.target.value }));
  const saveProfile = async (event) => {
    event.preventDefault(); setSaving(true); setError(''); setNotice('');
    try {
      const response = await profileAPI.update(profile);
      setProfile(response.data.profile);
      await checkAuth();
      setNotice('Profile saved successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Could not save your profile.');
    } finally { setSaving(false); }
  };

  if (loading || authLoading) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading profile…</div>;

  return (
    <main className="min-h-screen max-w-4xl mx-auto px-6 py-8">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8"><ArrowLeftIcon className="w-4 h-4" /> Back to dashboard</Link>
      <div className="flex items-center gap-3 mb-6"><UserCircleIcon className="w-10 h-10 text-[#d2a277]" /><div><h1 className="font-display font-bold text-3xl">Your Profile</h1><p className="text-sm text-gray-400">Your saved details and assessment history</p></div></div>
      <section className="glass-card p-6 mb-6">
        <p className="text-sm text-gray-400 mb-1">Account email</p><p className="font-medium mb-6">{user?.email}</p>
        <form onSubmit={saveProfile} className="space-y-4">
          <div><label className="block text-sm mb-2" htmlFor="display_name">Name to display</label><input id="display_name" name="display_name" value={profile.display_name} onChange={updateField} maxLength={80} className="input w-full" placeholder="Your name" /></div>
          <div><label className="block text-sm mb-2" htmlFor="study_stage">Current study or career stage</label><input id="study_stage" name="study_stage" value={profile.study_stage} onChange={updateField} maxLength={80} className="input w-full" placeholder="e.g. university student, graduate" /></div>
          <div><label className="block text-sm mb-2" htmlFor="goals">Goals</label><textarea id="goals" name="goals" value={profile.goals} onChange={updateField} maxLength={1000} rows={3} className="input w-full" placeholder="What would you like to work toward?" /></div>
          <div><label className="block text-sm mb-2" htmlFor="interests">Interests and skills</label><textarea id="interests" name="interests" value={profile.interests} onChange={updateField} maxLength={1000} rows={3} className="input w-full" placeholder="What do you enjoy learning or doing?" /></div>
          {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
          {notice && <p role="status" className="text-sm text-green-400">{notice}</p>}
          <button type="submit" disabled={saving} className="btn btn-primary">{saving ? 'Saving…' : 'Save profile'}</button>
        </form>
      </section>
      <section className="glass-card p-6">
        <div className="flex items-center justify-between gap-4 mb-4"><div><h2 className="font-display font-bold text-xl">Assessment history</h2><p className="text-sm text-gray-400">Previous results stay saved when you retake the assessment.</p></div><button onClick={() => navigate('/assessment')} className="btn btn-primary text-sm">Retake assessment</button></div>
        {history.length === 0 ? <p className="text-sm text-gray-400">No assessment completed yet. Your first result will appear here.</p> : <div className="space-y-3">{[...history].reverse().map((item, index) => <div key={item.id} className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-white/5"><div><p className="font-medium">Assessment #{history.length - index}</p><p className="text-xs text-gray-400">{item.created_at ? new Date(item.created_at).toLocaleString() : 'Date unavailable'}</p></div><div className="text-sm text-gray-300">{item.hollandCode || 'Profile saved'}{item.topCareer ? ` · ${item.topCareer}` : ''}</div></div>)}</div>}
      </section>
    </main>
  );
}
