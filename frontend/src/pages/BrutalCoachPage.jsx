import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function BrutalCoachPage() {
  const [message, setMessage] = useState('');
  const [intensity, setIntensity] = useState('direct');
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!message) return;
    const userMsg = { role: 'user', text: message };
    setChat(prev => [...prev, userMsg]);
    setMessage('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/coach/brutal', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, intensity })
      });
      const data = await res.json();
      setChat(prev => [...prev, { role: 'ai', text: data.reply }]);
    } catch (e) {
      setChat(prev => [...prev, { role: 'ai', text: 'Error connecting to coach.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen max-w-3xl mx-auto px-6 py-8 flex flex-col">
      <Link to="/dashboard" className="text-gray-400 hover:text-white mb-6 block">← Back to Dashboard</Link>

      <div className="flex justify-between items-center mb-6">
        <h1 className="font-display font-bold text-3xl">AI Career Coach</h1>
        <select 
          value={intensity} 
          onChange={e => setIntensity(e.target.value)}
          className="bg-[#18242e] border border-white/10 rounded-lg px-3 py-2 text-sm"
        >
          <option value="gentle">Gentle Mode</option>
          <option value="direct">Direct Mode</option>
          <option value="brutal">Brutal Honesty</option>
        </select>
      </div>

      <div className="flex-1 glass-card p-6 mb-6 overflow-y-auto space-y-4 min-h-[400px]">
        {chat.length === 0 && <p className="text-gray-500 text-center mt-10">Ask me anything. I will tell you the truth.</p>}
        {chat.map((c, i) => (
          <div key={i} className={`flex ${c.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-xl ${c.role === 'user' ? 'bg-[#d2a277] text-[#0b1117]' : 'bg-[#18242e]'}`}>
              {c.text}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-500">Coach is typing...</div>}
      </div>

      <div className="flex gap-2">
        <input 
          type="text" 
          value={message} 
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask for advice..." 
          className="input flex-1" 
        />
        <button onClick={send} className="btn btn-primary">Send</button>
      </div>
    </div>
  );
}