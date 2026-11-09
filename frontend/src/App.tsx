import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { CandidateSetupPage } from './pages/CandidateSetupPage';
import { InterviewWorkspacePage } from './pages/InterviewWorkspacePage';
import { ResultsDashboardPage } from './pages/ResultsDashboardPage';
import { KnowledgeManagementPage } from './pages/KnowledgeManagementPage';
import { SessionsHistoryPage } from './pages/SessionsHistoryPage';
import { ThemeProvider } from './context/ThemeContext';

export function App() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('talentlens_active_session');
    if (saved) {
      setActiveSessionId(saved);
    }

    // Listen for session cleared events dispatched by InterviewWorkspacePage
    const handleSessionCleared = () => setActiveSessionId(null);
    window.addEventListener('talentlens_session_cleared', handleSessionCleared);
    return () => window.removeEventListener('talentlens_session_cleared', handleSessionCleared);
  }, []);

  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 font-sans selection:bg-indigo-500/15 selection:text-indigo-900 dark:selection:text-indigo-200 transition-colors duration-200">
          <Navbar currentSessionId={activeSessionId} />
          
          <main className="flex-1 max-w-6xl w-full mx-auto px-6 sm:px-8 pt-10 sm:pt-14 pb-16">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/setup" element={<CandidateSetupPage />} />
              <Route path="/interview/:sessionId" element={<InterviewWorkspacePage />} />
              <Route path="/report/:sessionId" element={<ResultsDashboardPage />} />
              <Route path="/knowledge" element={<KnowledgeManagementPage />} />
              <Route path="/sessions" element={<SessionsHistoryPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <footer className="border-t border-zinc-200/80 dark:border-zinc-800/80 bg-zinc-50 dark:bg-zinc-950 py-8 mt-auto transition-colors duration-200">
            <div className="max-w-6xl mx-auto px-6 sm:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 dark:text-zinc-500 gap-4">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span className="font-medium text-zinc-700 dark:text-zinc-400">TalentLens Screening Architecture</span>
                <span className="text-zinc-400 dark:text-zinc-600">/</span>
                <span>Production Evaluation Engine</span>
              </div>
              <p className="font-mono text-[11px] text-zinc-400 dark:text-zinc-600 tracking-tight">
                Role-Filtered Literature Citations • Persistent ChromaDB Vector Store
              </p>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
