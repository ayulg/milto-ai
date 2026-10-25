import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { careerAPI, assessmentAPI } from '../api/client';
import { ArrowLeftIcon, ArrowRightIcon, CheckIcon } from '@heroicons/react/24/outline';

const SECTIONS = [
  { id: 'about', label: 'About You' },
  { id: 'personality', label: 'Personality' },
  { id: 'interests', label: 'Interests' },
  { id: 'skills', label: 'Skills' },
  { id: 'values', label: 'Values' },
];

export default function AssessmentPage() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [meta, setMeta] = useState(null);
  const [answers, setAnswers] = useState({});
  const [stepIndex, setStepIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [hasSavedResults, setHasSavedResults] = useState(false);
  const [checkingSavedResults, setCheckingSavedResults] = useState(true);

  useEffect(() => {
    loadMeta();
    let active = true;
    assessmentAPI.getResults()
      .then((response) => { if (active) setHasSavedResults(Boolean(response.data?.assessment)); })
      .catch(() => { if (active) setHasSavedResults(false); })
      .finally(() => { if (active) setCheckingSavedResults(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  const loadMeta = async () => {
    try {
      const response = await careerAPI.getMeta();
      setMeta(response.data);
    } catch (err) {
      setError('Failed to load questions. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const currentSection = SECTIONS[stepIndex];
  const sectionQuestions = meta?.questions?.filter(q => q.section === currentSection.id) || [];

  const handleAnswer = (questionId, value) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleNext = () => {
    if (stepIndex === 0 && !answers.stage) {
      setError('Please select where you are right now.');
      return;
    }
    setError('');
    if (stepIndex < SECTIONS.length - 1) {
      setStepIndex(stepIndex + 1);
      window.scrollTo(0, 0);
    } else {
      submitAssessment();
    }
  };

  const handleBack = () => {
    if (stepIndex > 0) {
      setStepIndex(stepIndex - 1);
      window.scrollTo(0, 0);
    }
  };

  const submitAssessment = async () => {
    setSubmitting(true);
    setError('');
    try {
      const response = await assessmentAPI.submit(answers);
      // Save results in sessionStorage for the dashboard
      sessionStorage.setItem('milto_results', JSON.stringify(response.data));
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#d2a277] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (!meta) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass-card p-8 max-w-md text-center">
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  const progress = ((stepIndex + 1) / SECTIONS.length) * 100;

  return (
    <div className="min-h-screen max-w-3xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <button onClick={() => navigate('/dashboard')} className="inline-flex items-center gap-2 text-gray-400 hover:text-white">
            <ArrowLeftIcon className="w-4 h-4" /><span className="text-sm">Back to dashboard</span>
          </button>
          {hasSavedResults && !checkingSavedResults && <button onClick={() => navigate('/dashboard')} className="btn btn-secondary text-sm">View previous results</button>}
        </div>

        <div className="flex justify-between items-end mb-4">
          <div>
            <p className="text-sm text-gray-400 mb-1">
              Step {stepIndex + 1} of {SECTIONS.length}
            </p>
            <h1 className="font-display font-bold text-3xl">{currentSection.label}</h1>
          </div>
          <span className="text-sm text-gray-400">{Math.round(progress)}%</span>
        </div>

        {/* Progress bar */}
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#d2a277] transition-all duration-500"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Questions */}
      <div className="glass-card p-6 mb-6">
        {sectionQuestions.map((q, idx) => (
          <QuestionItem
            key={q.id}
            question={q}
            value={answers[q.id]}
            onChange={(v) => handleAnswer(q.id, v)}
            stages={meta.stages}
            isLast={idx === sectionQuestions.length - 1}
          />
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between gap-3">
        <button
          onClick={handleBack}
          disabled={stepIndex === 0}
          className="btn btn-secondary"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={submitting}
          className="btn btn-primary"
        >
          {submitting ? 'Analyzing...' : (stepIndex === SECTIONS.length - 1 ? 'Get Results' : 'Continue')}
          {!submitting && stepIndex < SECTIONS.length - 1 && <ArrowRightIcon className="w-4 h-4" />}
          {!submitting && stepIndex === SECTIONS.length - 1 && <CheckIcon className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}

function QuestionItem({ question, value, onChange, stages, isLast }) {
  return (
    <div className={`py-5 ${!isLast ? 'border-b border-white/5' : ''}`}>
      <div className="mb-3">
        <p className="font-medium text-base">{question.prompt}</p>
        {question.help && <p className="text-sm text-gray-400 mt-1">{question.help}</p>}
      </div>

      {question.kind === 'stage' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {stages.map(stage => (
            <button
              key={stage.id}
              onClick={() => onChange(stage.id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                value === stage.id
                  ? 'border-[#d2a277] bg-[#d2a277]/10'
                  : 'border-white/10 hover:border-white/20'
              }`}
            >
              <div className="font-medium text-sm">{stage.label}</div>
              <div className="text-xs text-gray-400 mt-1">{stage.blurb}</div>
            </button>
          ))}
        </div>
      )}

      {question.kind === 'text' && (
        <textarea
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className="input"
          rows="3"
          placeholder="Write a few words..."
        />
      )}

      {question.kind === 'likert' && (
        <div>
          <div className="grid grid-cols-5 gap-2 mb-2">
            {[1, 2, 3, 4, 5].map(v => (
              <button
                key={v}
                onClick={() => onChange(v)}
                className={`h-12 rounded-xl border font-bold transition-all ${
                  value === v
                    ? 'border-[#d2a277] bg-[#d2a277] text-[#0b1117]'
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                {v}
              </button>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>{question.section === 'skills' || question.section === 'values' ? 'Not really' : 'Disagree'}</span>
            <span>{question.section === 'skills' || question.section === 'values' ? 'Very much' : 'Agree'}</span>
          </div>
        </div>
      )}
    </div>
  );
}

