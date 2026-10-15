import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { coachAPI } from '../api/client';
import { ArrowLeftIcon, PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/outline';

export default function CoachPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    loadStatus();
    // Welcome message
    setMessages([{
      role: 'assistant',
      content: "Hi! I'm your Milto AI Coach. I can help you:\n\n• Explore any career path\n• Understand your skill gaps\n• Build a bridge plan for a new career\n• Find learning resources\n\nWhat would you like to explore today?"
    }]);
  }, [user]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadStatus = async () => {
    try {
      const r = await coachAPI.getAIStatus();
      setAiStatus(r.data);
    } catch {}
  };

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await coachAPI.sendMessage(text);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.reply,
        source: response.data.source
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I hit an error: ${err.response?.data?.error || err.message}. Try again?`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "I want to be a software engineer",
    "What career fits my personality?",
    "What should I practice this week?",
    "I want to change my career",
  ];

  return (
    <div className="min-h-screen flex flex-col max-w-4xl mx-auto">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4 flex justify-between items-center sticky top-0 bg-[#0b1117]/95 backdrop-blur z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="text-gray-400 hover:text-white">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-[#d2a277] flex items-center justify-center text-[#0b1117] font-bold">
              M
            </div>
            <div>
              <h1 className="font-display font-bold">AI Coach</h1>
              <p className="text-xs text-gray-400">
                {aiStatus?.externalLLM ? `Ready (${aiStatus.model})` : 'Local mode'}
              </p>
            </div>
          </div>
        </div>
        <Link to="/career-lab" className="text-sm text-gray-400 hover:text-white">
          Career Lab →
        </Link>
      </header>

      {/* Chat messages */}
      <div className="flex-1 px-6 py-6 space-y-4 overflow-y-auto">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-[#d2a277] text-[#0b1117] rounded-br-sm'
                  : 'bg-[#18242e] text-gray-100 rounded-bl-sm'
              }`}
            >
              {msg.content}
              {msg.source === 'generative-ai' && (
                <div className="mt-2 pt-2 border-t border-white/10 text-xs text-gray-400 flex items-center gap-1">
                  <SparklesIcon className="w-3 h-3" />
                  AI-generated
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#18242e] rounded-2xl px-4 py-3 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#d2a277] animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-[#d2a277] animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-[#d2a277] animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="px-6 pb-3">
          <p className="text-xs text-gray-400 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => sendMessage(s)}
                className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm hover:border-[#d2a277]/50 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-white/10 px-6 py-4">
        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex gap-2 items-end"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(input);
              }
            }}
            placeholder="Ask about careers, skills, or next steps..."
            className="input flex-1 resize-none"
            rows="1"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn btn-primary p-3 disabled:opacity-50"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          AI uses a minimized profile context. Never enter passwords or sensitive data.
        </p>
      </div>
    </div>
  );
}
