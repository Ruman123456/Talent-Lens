import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { 
  UploadCloud, 
  AlertCircle, 
  ArrowRight,
  User,
  Mail,
  Check,
  FileCheck2,
  Clock
} from 'lucide-react';
import { apiService } from '../services/api';
import { Role, ResumeData } from '../types';

export const CandidateSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedRole = searchParams.get('role');

  const [roles, setRoles] = useState<Role[]>([]);
  const [candidateName, setCandidateName] = useState('');
  const [candidateEmail, setCandidateEmail] = useState('');
  const [selectedRoleId, setSelectedRoleId] = useState(preselectedRole || 'ai_ml_engineer');
  const [file, setFile] = useState<File | null>(null);
  
  const [uploading, setUploading] = useState(false);
  const [parsedResume, setParsedResume] = useState<ResumeData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiService.getRoles()
      .then(data => {
        setRoles(data);
        if (!preselectedRole && data.length > 0) {
          const readyRole = data.find(r => r.has_knowledge_base) || data[0];
          setSelectedRoleId(readyRole.id);
        }
      })
      .catch(err => console.error(err));
  }, [preselectedRole]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const ext = selected.name.split('.').pop()?.toLowerCase();
      if (ext !== 'pdf' && ext !== 'txt') {
        setError('Only .pdf and .txt files are supported.');
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleUploadAndAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateName.trim()) {
      setError('Please provide candidate name.');
      return;
    }
    if (!file) {
      setError('Please attach a resume file (.pdf or .txt).');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const resumeData = await apiService.uploadResume(file, candidateName, candidateEmail);
      setParsedResume(resumeData);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to parse resume document.');
    } finally {
      setUploading(false);
    }
  };

  const handleStartInterview = async () => {
    if (!parsedResume) return;

    setUploading(true);
    setError(null);

    try {
      const session = await apiService.startInterview(
        candidateName,
        parsedResume.id,
        selectedRoleId
      );
      localStorage.setItem('talentlens_active_session', session.id);
      navigate(`/interview/${session.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to initialize session.');
      setUploading(false);
    }
  };

  const currentRole = roles.find(r => r.id === selectedRoleId);

  return (
    <div className="max-w-4xl mx-auto space-y-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div className="space-y-1.5">
          <p className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
            Session Configuration
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
            Candidate & Track Setup
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Upload candidate credentials to extract competencies, then select the target evaluation track.
          </p>
        </div>

        <Link
          to="/sessions"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-md border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 text-xs font-medium transition-all self-start sm:self-auto"
        >
          <Clock className="w-3.5 h-3.5 text-zinc-400" />
          <span>View Past Sessions</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-50/70 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 text-xs flex items-start gap-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
          <div className="leading-relaxed">{error}</div>
        </div>
      )}

      {!parsedResume ? (
        <form onSubmit={handleUploadAndAnalyze} className="rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-8 sm:p-10 shadow-2xs space-y-8 transition-colors duration-200">
          {/* Candidate Identification Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                Candidate Name <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Alex Rivera"
                  value={candidateName}
                  onChange={e => setCandidateName(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 rounded-md border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 focus:border-zinc-400 dark:focus:border-zinc-600 focus:bg-white dark:focus:bg-zinc-900 focus:ring-2 focus:ring-zinc-200/60 dark:focus:ring-zinc-800 outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                Email Address <span className="text-zinc-400 text-[11px]">(Optional)</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
                <input
                  type="email"
                  placeholder="alex.rivera@example.com"
                  value={candidateEmail}
                  onChange={e => setCandidateEmail(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 rounded-md border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 focus:border-zinc-400 dark:focus:border-zinc-600 focus:bg-white dark:focus:bg-zinc-900 focus:ring-2 focus:ring-zinc-200/60 dark:focus:ring-zinc-800 outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 transition-all"
                />
              </div>
            </div>
          </div>

          {/* Target Track Selection */}
          <div className="space-y-3">
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Target Evaluation Track <span className="text-rose-500">*</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {roles.map(r => (
                <div
                  key={r.id}
                  onClick={() => setSelectedRoleId(r.id)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                    selectedRoleId === r.id
                      ? 'border-zinc-900 dark:border-zinc-100 bg-zinc-50/80 dark:bg-zinc-800/60 shadow-xs'
                      : 'border-zinc-200/80 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 bg-white dark:bg-zinc-900/40'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-medium text-xs text-zinc-900 dark:text-zinc-100">{r.name}</span>
                      {selectedRoleId === r.id ? (
                        <div className="w-4 h-4 rounded-full bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 flex items-center justify-center">
                          <Check className="w-2.5 h-2.5 stroke-[3]" />
                        </div>
                      ) : (
                        <span className={`w-1.5 h-1.5 rounded-full ${r.has_knowledge_base ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed">
                      {r.description}
                    </p>
                  </div>

                  <div className="mt-3 text-[10px] font-mono text-zinc-400 dark:text-zinc-500">
                    {r.has_knowledge_base ? `${r.total_chunks} chunks indexed` : 'No corpus indexed'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Resume Upload Area */}
          <div className="space-y-3">
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Resume Document (.PDF or .TXT) <span className="text-rose-500">*</span>
            </label>
            <label className="flex flex-col items-center justify-center border border-dashed border-zinc-200 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600 bg-zinc-50/40 dark:bg-zinc-950/40 rounded-xl p-8 cursor-pointer transition-all duration-200 group">
              <div className="w-10 h-10 rounded-lg bg-zinc-100 dark:bg-zinc-800/80 flex items-center justify-center text-zinc-500 dark:text-zinc-400 group-hover:text-zinc-800 dark:group-hover:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60 mb-3 transition-colors">
                <UploadCloud className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-zinc-800 dark:text-zinc-200">
                {file ? file.name : 'Select or drag candidate resume'}
              </span>
              <span className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-1">Plain TXT or PDF up to 10MB</span>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          <div className="flex justify-end pt-4 border-t border-zinc-100 dark:border-zinc-800/80">
            <button
              type="submit"
              disabled={uploading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 disabled:opacity-50 active:scale-[0.98] shadow-xs"
            >
              {uploading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
                  <span>Parsing Profile...</span>
                </>
              ) : (
                <>
                  <span>Extract Profile & Continue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>
      ) : (
        /* Parsed Profile Review */
        <div className="rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-8 sm:p-10 shadow-2xs space-y-8 transition-colors duration-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-zinc-100 dark:border-zinc-800/80 gap-3">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                <FileCheck2 className="w-3.5 h-3.5" />
                <span>Extracted & Validated</span>
              </div>
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                {candidateName}
              </h2>
            </div>
            <button
              onClick={() => setParsedResume(null)}
              className="text-xs text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200 transition-colors"
            >
              Upload Different File
            </button>
          </div>

          {parsedResume.extracted_profile.summary && (
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200/60 dark:border-zinc-800 text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">Profile Summary: </span> 
              {parsedResume.extracted_profile.summary}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <p className="text-[11px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
                Technical Skills & Frameworks
              </p>
              <div className="flex flex-wrap gap-1.5">
                {parsedResume.extracted_profile.technical_skills?.map((s, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-zinc-100/70 dark:bg-zinc-800/70 text-zinc-800 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60 font-medium">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
                Programming Languages
              </p>
              <div className="flex flex-wrap gap-1.5">
                {parsedResume.extracted_profile.programming_languages?.map((lang, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-zinc-100/70 dark:bg-zinc-800/70 text-zinc-800 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60 font-medium">
                    {lang}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
                Databases & Infrastructure
              </p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  ...(parsedResume.extracted_profile.databases || []),
                  ...(parsedResume.extracted_profile.cloud_technologies || [])
                ].map((item, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-zinc-100/70 dark:bg-zinc-800/70 text-zinc-700 dark:text-zinc-300 border border-zinc-200/60 dark:border-zinc-700/60">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
                Selected Evaluation Track
              </p>
              <div className="p-3.5 rounded-lg border border-zinc-200/80 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/40">
                <div className="font-medium text-xs text-zinc-900 dark:text-zinc-100">{currentRole?.name}</div>
                <div className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
                  {currentRole?.has_knowledge_base 
                    ? `Ready: ${currentRole.total_chunks} textbook chunks indexed.` 
                    : 'Corpus not indexed yet.'}
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-6 border-t border-zinc-100 dark:border-zinc-800/80 gap-4">
            <span className="text-xs text-zinc-400 dark:text-zinc-500">
              Questions will be retrieved from the role's verified corpus based on candidate skills.
            </span>

            <button
              onClick={handleStartInterview}
              disabled={uploading || !currentRole?.has_knowledge_base}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 disabled:opacity-50 active:scale-[0.98] shadow-xs"
            >
              {uploading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
                  <span>Retrieving RAG Context...</span>
                </>
              ) : (
                <>
                  <span>Launch Interview Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
