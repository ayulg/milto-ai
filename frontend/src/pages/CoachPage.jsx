
import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { coachAPI } from '../api/client';
import {
  ArrowLeftIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  UserIcon,
} from '@heroicons/react/24/outline';

export default function CoachPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const promptStarted = useRef(false);
  const { user } = useAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [intensity, setIntensity] = useState('direct');

  // Preserve the selected career for the entire conversation.
  const selectedCareer = location.state?.selectedCareer || null;

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    setMessages([
      {
        role: 'assistant',
        content:
          "Hi! I'm your Milto AI Coach. I'll help you build practical skills and make measurable progress.",
      },
    ]);

    const prompt = location.state?.initialPrompt;

    if (prompt && !promptStarted.current) {
      promptStarted.current = true;
      sendMessage(prompt, selectedCareer);
    }
  }, [user, navigate]);

  const sendMessage = async (text, career = selectedCareer) => {
    if (!text.trim() || loading) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);

    try {
      const res = await coachAPI.sendMessage(text, career);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            res.data.reply ||
            'I could not generate a response. Please try again.',
        },
      ]);
    } catch (err) {
      const message =
        err.response?.data?.error ||
        'Could not connect to the coach. Please check that the backend is running and try again.';

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: message },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col max-w-4xl mx-auto px-6 py-8">
      <header className="flex justify-between items-center mb-6">
        <Link
          to="/dashboard"
          className="text-gray-400 hover:text-white flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back
        </Link>

        <div className="flex items-center gap-2">
          <SparklesIcon className="w-5 h-5 text-[#d2a277]" />
          <h1 className="font-display font-bold text-xl">Milto AI Coach</h1>
        </div>
      </header>

      <div
        className="flex-1 glass-card p-6 mb-4 overflow-y-auto space-y-4"
        style={{ minHeight: '400px' }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-[#d2a277] flex items-center justify-center text-[#0b1117] font-bold text-sm flex-shrink-0">
                M
              </div>
            )}

            <div
              className={`max-w-[80%] p-4 rounded-2xl whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-[#18242e] rounded-tr-sm'
                  : 'bg-white/5 rounded-tl-sm'
              }`}
            >
              {msg.content}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0">
                <UserIcon className="w-4 h-4 text-gray-400" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="text-gray-500 text-sm">Coach is typing...</div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
          placeholder="Ask a question about studying, skills, or careers..."
          className="input flex-1"
        />

        <button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="btn btn-primary px-6"
        >
          <PaperAirplaneIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
