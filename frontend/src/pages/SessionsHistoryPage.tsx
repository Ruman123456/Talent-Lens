import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Clock, 
  CheckCircle2, 
  PlayCircle, 
  Trash2, 
  Search, 
  Filter, 
  ArrowRight, 
  FileText, 
  RotateCcw,
  Sparkles,
  TrendingUp,
  User
} from 'lucide-react';
import { apiService } from '../services/api';
import { InterviewSession } from '../types';

export const SessionsHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'in_progress'>('all');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getSessions();
      setSessions(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load past screening sessions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleDeleteSession = async (sessionId: string, candidateName: string) => {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete the screening session for ${candidateName}?`
    );
    if (!confirmed) return;

    setDeletingId(sessionId);
    try {
      await apiService.resetInterview(sessionId);
      // Clear active localStorage session if it was this one
      const active = localStorage.getItem('talentlens_active_session');
      if (active === sessionId) {
        localStorage.removeItem('talentlens_active_session');
        window.dispatchEvent(new Event('talentlens_session_cleared'));
      }
      setSessions(prev => prev.filter(s => s.id !== sessionId));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to delete session.');
    } finally {
      setDeletingId(null);
    }
  };

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = 
      session.candidate_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.role_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || session.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const completedSessions = sessions.filter(s => s.status === 'completed');
  const inProgressSessions = sessions.filter(s => s.status !== 'completed');

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-200/80 dark:border-zinc-800">
        <div>
          <p className="text-[11px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
            Audit & Screenings Archive
          </p>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
            Previous Screening Sessions
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
            Review completed evaluations, download PDF reports, or resume unfinished candidate interviews.
          </p>
        </div>

        <Link
          to="/setup"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 active:scale-[0.98] shadow-xs self-start sm:self-auto"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>New Screening</span>
        </Link>
      </div>

      {/* Aggregate Metrics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Total Sessions
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              {sessions.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">candidates screened</span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Completed Evaluations
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">
              {completedSessions.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">
              of {sessions.length} sessions
            </span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-2xs">
          <p className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            In Progress
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-bold tracking-tight text-amber-600 dark:text-amber-400">
              {inProgressSessions.length}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500">active or unfinished</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search candidate or role..."
            className="w-full pl-9 pr-3 py-2 rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 text-xs text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 focus:ring-1 focus:ring-zinc-400 transition-all"
          />
        </div>

        <div className="flex items-center gap-1.5 p-1 rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 self-start sm:self-auto">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1 rounded text-xs font-medium transition-all ${
              statusFilter === 'all'
                ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            All ({sessions.length})
          </button>
          <button
            onClick={() => setStatusFilter('completed')}
            className={`px-3 py-1 rounded text-xs font-medium transition-all ${
              statusFilter === 'completed'
                ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Completed ({completedSessions.length})
          </button>
          <button
            onClick={() => setStatusFilter('in_progress')}
            className={`px-3 py-1 rounded text-xs font-medium transition-all ${
              statusFilter === 'in_progress'
                ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            In Progress ({sessions.length - completedSessions.length})
          </button>
        </div>
      </div>

      {/* Sessions List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-3">
          <div className="w-6 h-6 border-2 border-zinc-900 dark:border-zinc-100 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-zinc-500 dark:text-zinc-400">Loading screening history...</p>
        </div>
      ) : error ? (
        <div className="p-8 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 text-center space-y-3">
          <p className="text-xs text-rose-500">{error}</p>
          <button
            onClick={fetchSessions}
            className="px-3 py-1.5 rounded-md text-xs font-medium bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            Retry
          </button>
        </div>
      ) : filteredSessions.length === 0 ? (
        <div className="p-12 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 text-center space-y-4">
          <div className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mx-auto text-zinc-400">
            <FileText className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              No sessions found
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-sm mx-auto">
              {searchQuery || statusFilter !== 'all'
                ? 'No interview sessions match your search or filter criteria.'
                : 'No interview screening sessions have been conducted yet.'}
            </p>
          </div>
          <Link
            to="/setup"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-md bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 text-xs font-medium"
          >
            <span>Start First Screening</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSessions.map(session => {
            const isCompleted = session.status === 'completed';
            const startedDate = new Date(session.started_at).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            });
            const startedTime = new Date(session.started_at).toLocaleTimeString(undefined, {
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div
                key={session.id}
                className="group p-5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-200 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                {/* Candidate & Role Info */}
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 tracking-tight">
                      {session.candidate_name}
                    </span>
                    <span className="text-zinc-300 dark:text-zinc-700">•</span>
                    <span className="text-xs font-medium text-zinc-600 dark:text-zinc-300">
                      {session.role_name}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wider uppercase border ${
                        isCompleted
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                          : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          isCompleted ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'
                        }`}
                      />
                      <span>{isCompleted ? 'Completed' : 'In Progress'}</span>
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400 flex-wrap">
                    <span className="flex items-center gap-1 font-mono text-[11px]">
                      <Clock className="w-3 h-3 text-zinc-400" />
                      {startedDate} at {startedTime}
                    </span>
                    <span>•</span>
                    <span>
                      {session.answered_questions} of {session.total_questions} questions answered
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  {isCompleted ? (
                    <Link
                      to={`/report/${session.id}`}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-800 dark:text-zinc-200 text-xs font-medium transition-all duration-200"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>View Report</span>
                    </Link>
                  ) : (
                    <Link
                      to={`/interview/${session.id}`}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 active:scale-[0.98] shadow-xs"
                    >
                      <PlayCircle className="w-3.5 h-3.5" />
                      <span>Resume Session</span>
                    </Link>
                  )}

                  <button
                    onClick={() => handleDeleteSession(session.id, session.candidate_name)}
                    disabled={deletingId === session.id}
                    title="Delete session"
                    className="p-2 rounded-md text-zinc-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50/60 dark:hover:bg-rose-950/40 border border-transparent hover:border-zinc-200 dark:hover:border-zinc-800 transition-all duration-200 disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
