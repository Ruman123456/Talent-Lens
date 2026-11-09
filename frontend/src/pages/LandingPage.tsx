import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  Database, 
  BookOpen,
  ArrowUpRight,
  Clock
} from 'lucide-react';
import { apiService } from '../services/api';
import { Role } from '../types';

export const LandingPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);

  useEffect(() => {
    apiService.getRoles()
      .then(data => setRoles(data))
      .catch(err => console.error(err));
  }, []);

  const totalChunks = roles.reduce((acc, r) => acc + r.total_chunks, 0);
  const totalDocs = roles.reduce((acc, r) => acc + r.total_documents, 0);

  return (
    <div className="space-y-16 sm:space-y-24">
      {/* Hero Section */}
      <section className="relative pt-4 sm:pt-8 space-y-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-200/80 dark:border-zinc-800 bg-white/60 dark:bg-zinc-900/60 backdrop-blur-xs text-xs font-medium text-zinc-600 dark:text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Grounded RAG Screening Architecture</span>
        </div>

        <div className="max-w-3xl space-y-5">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 leading-[1.08]">
            Objective technical interviews grounded in verified literature.
          </h1>

          <p className="text-base sm:text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed max-w-2xl">
            TalentLens parses candidate resumes and dynamically constructs semantic queries against role-specific textbooks and technical corpora, eliminating hallucinated questions and generic trivia.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-4 pt-2">
          <Link
            to="/setup"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-sm font-medium transition-all duration-200 active:scale-[0.98] shadow-xs"
          >
            <span>Start Candidate Screening</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            to="/sessions"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:bg-zinc-50 dark:hover:bg-zinc-800/60 text-zinc-700 dark:text-zinc-300 text-sm font-medium transition-all duration-200"
          >
            <Clock className="w-4 h-4 text-zinc-400" />
            <span>Past Sessions</span>
          </Link>

          <Link
            to="/knowledge"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:bg-zinc-50 dark:hover:bg-zinc-800/60 text-zinc-700 dark:text-zinc-300 text-sm font-medium transition-all duration-200"
          >
            <Database className="w-4 h-4 text-zinc-400" />
            <span>Inspect Knowledge Corpus</span>
          </Link>
        </div>

        {/* Feature Pillars: Minimalist Linear Style */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-12 border-t border-zinc-200/80 dark:border-zinc-800/80">
          <div className="space-y-2.5 p-1">
            <div className="w-8 h-8 rounded-md bg-zinc-100 dark:bg-zinc-800/80 flex items-center justify-center text-zinc-800 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60">
              <Cpu className="w-4 h-4" />
            </div>
            <h3 className="font-medium text-sm text-zinc-900 dark:text-zinc-100">
              Resume-Aware Decomposition
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
              Extracts programming languages, system tradeoffs, and project exposure to guide multi-query vector retrieval.
            </p>
          </div>

          <div className="space-y-2.5 p-1">
            <div className="w-8 h-8 rounded-md bg-zinc-100 dark:bg-zinc-800/80 flex items-center justify-center text-zinc-800 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60">
              <BookOpen className="w-4 h-4" />
            </div>
            <h3 className="font-medium text-sm text-zinc-900 dark:text-zinc-100">
              Curated Textbook Grounding
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
              Every question retains explicit chunk metadata, textbook citations, and page references from the role corpus.
            </p>
          </div>

          <div className="space-y-2.5 p-1">
            <div className="w-8 h-8 rounded-md bg-zinc-100 dark:bg-zinc-800/80 flex items-center justify-center text-zinc-800 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h3 className="font-medium text-sm text-zinc-900 dark:text-zinc-100">
              Multi-Criteria Scoring
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
              Evaluates technical correctness, missing theoretical concepts, and depth against transparent rubrics.
            </p>
          </div>
        </div>
      </section>

      {/* Configured Roles & Corpus Status */}
      <section className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="space-y-1">
            <p className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
              Corpus Readiness
            </p>
            <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
              Supported Technical Tracks
            </h2>
          </div>

          <div className="flex items-center gap-3 text-xs text-zinc-500 dark:text-zinc-400 bg-white dark:bg-zinc-900 px-3.5 py-1.5 rounded-md border border-zinc-200 dark:border-zinc-800 font-mono">
            <span>Documents: <strong className="text-zinc-900 dark:text-zinc-200">{totalDocs}</strong></span>
            <span className="text-zinc-300 dark:text-zinc-700">|</span>
            <span>Vector Chunks: <strong className="text-zinc-900 dark:text-zinc-200">{totalChunks}</strong></span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div 
              key={role.id} 
              className="group relative rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-7 flex flex-col justify-between hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-200 shadow-2xs hover:shadow-xs"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
                    {role.id}
                  </span>
                  {role.has_knowledge_base ? (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      <span>{role.total_chunks} Chunks</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-900">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                      <span>Needs Corpus</span>
                    </span>
                  )}
                </div>

                <div className="space-y-1.5">
                  <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-zinc-700 dark:group-hover:text-zinc-300 transition-colors">
                    {role.name}
                  </h3>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-3 leading-relaxed">
                    {role.description}
                  </p>
                </div>

                <div className="pt-2">
                  <p className="text-[11px] font-medium text-zinc-400 dark:text-zinc-500 uppercase tracking-wider mb-2">
                    Evaluated Competencies
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {role.configuration.competencies?.slice(0, 3).map((comp, idx) => (
                      <span 
                        key={idx} 
                        className="text-[11px] px-2 py-0.5 rounded-md bg-zinc-100/70 dark:bg-zinc-800/70 text-zinc-600 dark:text-zinc-400 border border-zinc-200/50 dark:border-zinc-800"
                      >
                        {comp}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-6 border-t border-zinc-100 dark:border-zinc-800/80 mt-6 flex items-center justify-between">
                <Link
                  to={`/setup?role=${role.id}`}
                  className={`text-xs font-medium inline-flex items-center gap-1 transition-colors ${
                    role.has_knowledge_base 
                      ? 'text-zinc-900 dark:text-zinc-100 hover:text-indigo-600 dark:hover:text-indigo-400' 
                      : 'text-zinc-400 dark:text-zinc-600 pointer-events-none'
                  }`}
                >
                  <span>Select Track</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <Link
                  to="/knowledge"
                  className="text-xs text-zinc-400 dark:text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 inline-flex items-center gap-0.5"
                >
                  <span>Corpus</span>
                  <ArrowUpRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
