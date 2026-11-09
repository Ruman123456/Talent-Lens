import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Download, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  BookOpen,
  FileText,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { apiService } from '../services/api';
import { FinalReport, QuestionEvaluationDetail } from '../types';

export const ResultsDashboardPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [report, setReport] = useState<FinalReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQIndex, setExpandedQIndex] = useState<number | null>(0);
  const [filterMode, setFilterMode] = useState<'all' | 'answered' | 'unanswered'>('all');

  useEffect(() => {
    if (!sessionId) return;
    apiService.getReport(sessionId)
      .then(data => setReport(data))
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load report.'))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3">
        <div className="w-6 h-6 border-2 border-zinc-900 dark:border-zinc-100 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-zinc-500 dark:text-zinc-400">Loading interview breakdown and citations...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-md mx-auto p-8 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs text-center space-y-4 mt-12">
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">Report Unavailable</h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">{error || 'Could not load report.'}</p>
        <Link to="/" className="px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 rounded-md text-xs font-medium inline-block">
          Return Home
        </Link>
      </div>
    );
  }

  const isQuestionAnswered = (q: QuestionEvaluationDetail) => {
    if (!q.candidate_answer) return false;
    const trimmed = q.candidate_answer.trim();
    return (
      trimmed !== '' &&
      trimmed.toLowerCase() !== 'no response recorded.' &&
      q.correctness !== 'unanswered'
    );
  };

  const answeredQuestions = report.question_details.filter(isQuestionAnswered);
  const unansweredQuestions = report.question_details.filter(q => !isQuestionAnswered(q));

  const filteredQuestions = report.question_details.filter(q => {
    if (filterMode === 'answered') return isQuestionAnswered(q);
    if (filterMode === 'unanswered') return !isQuestionAnswered(q);
    return true;
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Top Banner & Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80 dark:border-zinc-800/80">
        <div className="space-y-1.5">
          <p className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
            Candidate Evaluation Summary
          </p>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
            {report.candidate_name}
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Target Track: <span className="text-zinc-800 dark:text-zinc-200 font-medium">{report.role_name}</span> • Completed {new Date(report.generated_at).toLocaleDateString()}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/setup"
            onClick={() => {
              localStorage.removeItem('talentlens_active_session');
              window.dispatchEvent(new Event('talentlens_session_cleared'));
            }}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-md border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 text-xs font-medium transition-all duration-200"
          >
            <span>Start New Interview</span>
          </Link>

          <a
            href={apiService.getReportPdfUrl(sessionId!)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 active:scale-[0.98] shadow-xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </a>
        </div>
      </div>

      {/* Overview Cards: Total, Answered, Unanswered */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
            Total Questions
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
              {report.question_details.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">challenges presented</span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
            Answered
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-semibold tracking-tight text-emerald-600 dark:text-emerald-400">
              {answeredQuestions.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">
              responses recorded
            </span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
            Unanswered
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className={`text-3xl font-semibold tracking-tight ${unansweredQuestions.length > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-zinc-400'}`}>
              {unansweredQuestions.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">
              skipped or blank
            </span>
          </div>
        </div>
      </div>

      {/* Question-Wise Evaluation Breakdown & Citations */}
      <div className="rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-6 sm:p-8 shadow-2xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-100 dark:border-zinc-800/80">
          <div>
            <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              Question-Wise Evaluation Breakdown & Citations
            </h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Detailed review of candidate responses, qualitative feedback, and grounded literature sources.
            </p>
          </div>

          {/* Filter Pills: All / Answered / Unanswered */}
          <div className="flex items-center gap-1.5 p-1 rounded-md border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 self-start sm:self-auto">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                filterMode === 'all'
                  ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
              }`}
            >
              All ({report.question_details.length})
            </button>
            <button
              onClick={() => setFilterMode('answered')}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                filterMode === 'answered'
                  ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
              }`}
            >
              Answered ({answeredQuestions.length})
            </button>
            <button
              onClick={() => setFilterMode('unanswered')}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                filterMode === 'unanswered'
                  ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                  : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
              }`}
            >
              Unanswered ({unansweredQuestions.length})
            </button>
          </div>
        </div>

        {/* Accordion Questions List */}
        <div className="space-y-3">
          {filteredQuestions.map((q) => {
            const originalIndex = report.question_details.findIndex(item => item.question_id === q.question_id);
            const isExpanded = expandedQIndex === originalIndex;
            const answered = isQuestionAnswered(q);

            return (
              <div 
                key={q.question_id}
                className="border border-zinc-200/80 dark:border-zinc-800 rounded-lg overflow-hidden transition-all duration-200"
              >
                {/* Accordion Header */}
                <div 
                  onClick={() => setExpandedQIndex(isExpanded ? null : originalIndex)}
                  className="p-4 bg-zinc-50/60 dark:bg-zinc-900/40 hover:bg-zinc-100/60 dark:hover:bg-zinc-800/50 cursor-pointer flex items-center justify-between gap-4 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="font-mono text-xs text-zinc-400 dark:text-zinc-500 shrink-0">
                      #{q.question_index}
                    </span>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-xs text-zinc-900 dark:text-zinc-100">
                          {q.topic}
                        </span>
                        <span className="text-[11px] text-zinc-400 capitalize">
                          • {q.difficulty}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-500 dark:text-zinc-400 truncate mt-0.5">
                        {q.question_text}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {answered ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wider uppercase bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span>Answered</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wider uppercase bg-zinc-100 text-zinc-600 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                        <span>Unanswered</span>
                      </span>
                    )}

                    {isExpanded ? (
                      <ChevronUp className="w-3.5 h-3.5 text-zinc-400" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />
                    )}
                  </div>
                </div>

                {/* Accordion Expanded Details */}
                {isExpanded && (
                  <div className="p-5 sm:p-6 space-y-5 bg-white dark:bg-zinc-900/60 border-t border-zinc-100 dark:border-zinc-800/80 text-xs">
                    {/* Full Question */}
                    <div className="space-y-1">
                      <span className="font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider text-[10px]">
                        Question
                      </span>
                      <p className="font-medium text-zinc-900 dark:text-zinc-100 leading-relaxed text-sm">
                        {q.question_text}
                      </p>
                    </div>

                    {/* Submitted Response */}
                    <div className="space-y-1.5">
                      <span className="font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider text-[10px]">
                        Candidate Response
                      </span>
                      {answered ? (
                        <div className="p-4 rounded-md bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200/70 dark:border-zinc-800">
                          <p className="text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap leading-relaxed font-sans">
                            {q.candidate_answer}
                          </p>
                        </div>
                      ) : (
                        <div className="p-4 rounded-md bg-zinc-50/50 dark:bg-zinc-900/30 border border-dashed border-zinc-300 dark:border-zinc-800 text-zinc-400 italic">
                          No response recorded for this question.
                        </div>
                      )}
                    </div>

                    {/* Qualitative Evaluation & Feedback */}
                    {answered && (
                      <div className="space-y-3 pt-2 border-t border-zinc-100 dark:border-zinc-800/80">
                        <span className="font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider text-[10px]">
                          Qualitative Evaluation & Feedback
                        </span>

                        {q.evaluation_explanation && (
                          <div className="p-3.5 rounded-md bg-zinc-50/70 dark:bg-zinc-950/40 border border-zinc-200/60 dark:border-zinc-800/80 text-zinc-700 dark:text-zinc-300 leading-relaxed">
                            {/* Strip any legacy raw score mentions like "Score: 3.5/5.0" */}
                            {q.evaluation_explanation.replace(/Score:\s*\d+(\.\d+)?\s*\/\s*5\.0[.\s—-]*/gi, '')}
                          </div>
                        )}

                        {q.strengths && q.strengths.length > 0 && (
                          <div className="space-y-1">
                            <span className="font-medium text-emerald-700 dark:text-emerald-400 text-[11px]">
                              Identified Strengths:
                            </span>
                            <ul className="list-disc list-inside text-zinc-600 dark:text-zinc-400 space-y-0.5 pl-1">
                              {q.strengths.map((str, sIdx) => (
                                <li key={sIdx}>{str}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {q.missing_concepts && q.missing_concepts.length > 0 && q.missing_concepts[0] !== 'Unanswered' && (
                          <div className="space-y-1">
                            <span className="font-medium text-amber-700 dark:text-amber-400 text-[11px]">
                              Missing Concepts / Growth Areas:
                            </span>
                            <ul className="list-disc list-inside text-zinc-600 dark:text-zinc-400 space-y-0.5 pl-1">
                              {q.missing_concepts.map((mc, mIdx) => (
                                <li key={mIdx}>{mc}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Grounded Literature Reference Citations */}
                    {q.source_references && q.source_references.length > 0 && (
                      <div className="p-3.5 rounded-md bg-zinc-50/80 dark:bg-zinc-950/50 border border-zinc-200/70 dark:border-zinc-800/80 space-y-2">
                        <div className="flex items-center gap-1.5 font-medium text-zinc-600 dark:text-zinc-400 text-[11px] uppercase tracking-wider">
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>Grounded Literature Citation</span>
                        </div>
                        {q.source_references.map((r, rIdx) => (
                          <div key={rIdx} className="space-y-1">
                            <div className="font-medium text-zinc-800 dark:text-zinc-200 text-xs">
                              {r.document_name} {r.page_number && <span className="text-zinc-400 font-normal">(Page {r.page_number})</span>}
                            </div>
                            {r.snippet && (
                              <p className="text-[11px] text-zinc-500 dark:text-zinc-400 italic border-l border-zinc-300 dark:border-zinc-700 pl-2.5 my-1 leading-relaxed">
                                "{r.snippet}..."
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};