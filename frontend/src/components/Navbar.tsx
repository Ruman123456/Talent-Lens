import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ChevronRight,
  Sun,
  Moon,
  Terminal
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface NavbarProps {
  currentSessionId?: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({ currentSessionId }) => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const navItems = [
    { label: 'Overview', path: '/' },
    { label: 'Screening', path: '/setup' },
    { label: 'Sessions', path: '/sessions' },
    { label: 'Knowledge Base', path: '/knowledge' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-200/80 dark:border-zinc-800/80 bg-zinc-50/80 dark:bg-zinc-950/80 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-6xl mx-auto px-6 sm:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Brand Logo & Identifier */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center text-zinc-50 dark:text-zinc-900 shadow-sm transition-transform duration-200 group-hover:scale-[1.03]">
              <Terminal className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-2.5">
              <span className="font-semibold text-base tracking-tight text-zinc-900 dark:text-zinc-100">
                TalentLens
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border border-zinc-200 dark:border-zinc-800 bg-zinc-100/60 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400">
                RAG Engine
              </span>
            </div>
          </Link>

          {/* Nav Items & Utilities */}
          <div className="flex items-center gap-2 sm:gap-3">
            <nav className="flex items-center gap-1 sm:gap-1.5">
              {navItems.map((item) => {
                const active = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                      active
                        ? 'bg-zinc-200/70 dark:bg-zinc-800/80 text-zinc-900 dark:text-zinc-100 font-semibold shadow-xs'
                        : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200 hover:bg-zinc-100/80 dark:hover:bg-zinc-900'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}

              {currentSessionId && (
                <Link
                  to={`/interview/${currentSessionId}`}
                  className="ml-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium border border-zinc-300 dark:border-zinc-700 bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-all duration-200 active:scale-[0.98]"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Resume Interview</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              )}
            </nav>

            <div className="h-4 w-px bg-zinc-200 dark:bg-zinc-800 mx-1" />

            {/* Subtle Theme Switcher */}
            <button
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="p-2 rounded-md text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-900 border border-transparent hover:border-zinc-200 dark:hover:border-zinc-800 transition-all duration-200"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-zinc-400 hover:text-zinc-200" />
              ) : (
                <Moon className="w-4 h-4 text-zinc-600 hover:text-zinc-900" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
