import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  ArrowRight, 
  Send, 
  ShieldAlert,
  RotateCcw,
  History
} from 'lucide-react';
import { apiService } from '../services/api';
import { InterviewSession, InterviewQuestion } from '../types';

export const InterviewWorkspacePage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerText, setAnswerText] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    Promise.all([
      apiService.getSession(sessionId),
      apiService.getSessionQuestions(sessionId)
    ])
      .then(([sessionData, questionsData]) => {
        setSession(sessionData);
        setQuestions(questionsData);
        const unansweredIdx = Math.min(sessionData.answered_questions, Math.max(0, questionsData.length - 1));
        setCurrentIndex(unansweredIdx);
      })
      .catch((err: any) => {
        setError(err?.response?.data?.detail || 'Failed to load session.');
      })
      .finally(() => setLoading(false));
  }, [sessionId]);

  const currentQuestion = questions[currentIndex];

  const handleSubmitAnswer = async () => {
    if (!sessionId || !currentQuestion || !answerText.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      await apiService.submitAnswer(sessionId, currentQuestion.id, answerText);
      setAnswerText('');

      const updatedSession = await apiService.getSession(sessionId);
      setSession(updatedSession);

      if (currentIndex + 1 < questions.length) {
        setCurrentIndex(currentIndex + 1);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to submit response.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinishInterview = async () => {
    if (!sessionId) return;
    setCompleting(true);
    try {
      await apiService.completeInterview(sessionId);
      localStorage.removeItem('talentlens_active_session');
      window.dispatchEvent(new Event('talentlens_session_cleared'));
      navigate(`/report/${sessionId}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to complete session.');
      setCompleting(false);
    }
  };

  const handleResetInterview = async () => {
    if (!sessionId) return;
    const confirmed = window.confirm(
      "Are you sure you want to reset this interview? All answers and progress for this session will be permanently deleted."
    );
    if (!confirmed) return;

    setResetting(true);
    try {
      await apiService.resetInterview(sessionId);
      localStorage.removeItem('talentlens_active_session');
      window.dispatchEvent(new Event('talentlens_session_cleared'));
      navigate('/setup');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to reset interview session.');
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3">
        <div className="w-6 h-6 border-2 border-zinc-900 dark:border-zinc-100 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-zinc-500 dark:text-zinc-400">Loading interview workspace...</p>
      </div>
    );
  }

  if (error || !session || !currentQuestion) {
    return (
      <div className="max-w-md mx-auto p-8 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs text-center space-y-4 mt-12">
        <ShieldAlert className="w-8 h-8 text-rose-500 mx-auto" />
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">Unable to load session</h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">{error || 'Session not found.'}</p>
        <button
          onClick={() => navigate('/setup')}
          className="px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 rounded-md text-xs font-medium"
        >
          Return to Setup
        </button>
      </div>
    );
  }

  const answeredCount = session.answered_questions;
  const progressPercent = Math.round((answeredCount / questions.length) * 100);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Session Progress Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 transition-colors duration-200">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">{session.candidate_name}</span>
            <span className="text-zinc-300 dark:text-zinc-700">/</span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">{session.role_name}</span>
          </div>
          <p className="font-mono text-[11px] text-zinc-400 dark:text-zinc-500">Session ID: {session.id.slice(0, 8)}</p>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/sessions')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-zinc-200/80 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300 text-xs font-medium transition-all"
            title="View Past Sessions"
          >
            <History className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sessions</span>
          </button>

          <div className="text-right">
            <span className="text-xs font-medium text-zinc-700 dark:text-zinc-300">
              {currentIndex + 1} of {questions.length} Questions
            </span>
            <div className="w-32 h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden mt-1">
              <div 
                className="h-full bg-zinc-900 dark:bg-zinc-100 transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          <div className="text-xs font-mono px-2.5 py-1 rounded-md bg-zinc-100/80 dark:bg-zinc-800/80 text-zinc-700 dark:text-zinc-300 border border-zinc-200/60 dark:border-zinc-700/60">
            {answeredCount} Done
          </div>
        </div>
      </div>

      {/* Main Question Card */}
      <div className="rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-8 sm:p-10 shadow-2xs space-y-8 transition-colors duration-200">
        {/* Topic & Metadata */}
        <div className="flex flex-wrap items-center justify-between gap-2 pb-5 border-b border-zinc-100 dark:border-zinc-800/80">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-md text-[11px] font-semibold tracking-wider uppercase bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200/50 dark:border-zinc-700/50">
              {currentQuestion.topic}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500 capitalize">
              • {currentQuestion.difficulty}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500 capitalize">
              • {currentQuestion.question_type.replace('_', ' ')}
            </span>
          </div>

          <span className="text-[11px] font-mono text-zinc-400 dark:text-zinc-500">
            {currentQuestion.source_references?.length || 0} Retrieved Citations
          </span>
        </div>

        {/* Question Text */}
        <div className="space-y-3">
          <h2 className="text-xl sm:text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100 leading-snug">
            {currentQuestion.question_text}
          </h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Detail the core engineering mechanics, architectural tradeoffs, or algorithmic principles.
          </p>
        </div>

        {/* Literature Citation Drawer */}
        {currentQuestion.source_references && currentQuestion.source_references.length > 0 && (
          <div className="p-4 rounded-lg bg-zinc-50/70 dark:bg-zinc-950/40 border border-zinc-200/70 dark:border-zinc-800/80 space-y-2">
            <div className="flex items-center gap-2 text-[11px] font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Grounded Literature Reference</span>
            </div>
            {currentQuestion.source_references.map((ref, idx) => (
              <div key={idx} className="text-xs text-zinc-600 dark:text-zinc-400 space-y-1">
                <div className="font-medium text-zinc-800 dark:text-zinc-200">
                  {ref.document_name} {ref.page_number && <span className="text-zinc-400 dark:text-zinc-500 font-normal">(Page {ref.page_number})</span>}
                </div>
                {ref.snippet && (
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 italic border-l border-zinc-300 dark:border-zinc-700 pl-2.5 my-1 leading-relaxed">
                    "{ref.snippet}..."
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Answer Editor */}
        <div className="space-y-2.5">
          <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
            Candidate Response
          </label>
          <textarea
            rows={7}
            value={answerText}
            onChange={e => setAnswerText(e.target.value)}
            placeholder="Structure your answer with theoretical principles, implementation details, and failure modes..."
            className="w-full p-4 rounded-md border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 focus:border-zinc-400 dark:focus:border-zinc-600 focus:bg-white dark:focus:bg-zinc-900 focus:ring-2 focus:ring-zinc-200/60 dark:focus:ring-zinc-800 outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 transition-all leading-relaxed font-sans"
          />
        </div>

        {/* Question Pagination & Submission Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-5 border-t border-zinc-100 dark:border-zinc-800/80">
          <div className="flex items-center gap-1.5">
            {questions.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentIndex(idx)}
                className={`w-7 h-7 rounded-md text-xs font-mono transition-all duration-200 ${
                  currentIndex === idx
                    ? 'bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 font-bold shadow-xs'
                    : idx < answeredCount
                    ? 'bg-zinc-100 dark:bg-zinc-800 text-emerald-600 dark:text-emerald-400 font-medium'
                    : 'bg-zinc-50 dark:bg-zinc-900 text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleResetInterview}
              disabled={resetting}
              title="Reset and discard this session"
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md text-zinc-500 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50/60 dark:hover:bg-rose-950/40 text-xs font-medium transition-all duration-200"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Reset Interview</span>
            </button>

            <button
              onClick={handleSubmitAnswer}
              disabled={submitting || !answerText.trim()}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 disabled:opacity-50 active:scale-[0.98] shadow-xs"
            >
              {submitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Submit Answer</span>
                </>
              )}
            </button>

            {answeredCount >= 1 && (
              <button
                onClick={handleFinishInterview}
                disabled={completing}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-md border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 text-xs font-medium transition-all duration-200"
              >
                {completing ? (
                  <span>Generating Report...</span>
                ) : (
                  <>
                    <span>Finish Session</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
