import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Layers,
  BookOpen
} from 'lucide-react';
import { apiService } from '../services/api';
import { Role, KnowledgeStatus } from '../types';

export const KnowledgeManagementPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>('ai_ml_engineer');
  const [status, setStatus] = useState<KnowledgeStatus | null>(null);
  
  const [sourceName, setSourceName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    apiService.getRoles()
      .then(data => {
        setRoles(data);
        if (data.length > 0 && !selectedRole) {
          setSelectedRole(data[0].id);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const loadStatus = (roleId: string) => {
    apiService.getKnowledgeStatus(roleId)
      .then(data => setStatus(data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    if (selectedRole) {
      loadStatus(selectedRole);
    }
  }, [selectedRole]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !sourceName.trim()) {
      setMessage({ text: 'Please provide both source name and a document file.', type: 'error' });
      return;
    }

    setIngesting(true);
    setMessage(null);

    try {
      const res = await apiService.ingestDocument(selectedRole, sourceName, file);
      setMessage({ text: res.message || 'Ingestion completed successfully!', type: 'success' });
      setFile(null);
      setSourceName('');
      loadStatus(selectedRole);
      apiService.getRoles().then(setRoles);
    } catch (err: any) {
      setMessage({ text: err?.response?.data?.detail || 'Document ingestion failed.', type: 'error' });
    } finally {
      setIngesting(false);
    }
  };

  const currentRoleData = roles.find(r => r.id === selectedRole);

  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-16">
      <div className="space-y-1.5">
        <p className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500">
          Knowledge Infrastructure
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
          Corpus & Literature Ingestion
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Manage textbook literature, engineering guides, and documents indexed in role-specific ChromaDB vector collections.
        </p>
      </div>

      {/* Role Switcher Tabs */}
      <div className="flex flex-wrap gap-1.5 border-b border-zinc-200/80 dark:border-zinc-800/80 pb-3">
        {roles.map(r => (
          <button
            key={r.id}
            onClick={() => setSelectedRole(r.id)}
            className={`px-3.5 py-1.5 rounded-md text-xs font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedRole === r.id
                ? 'bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                : 'bg-white dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-50 dark:hover:bg-zinc-800/60'
            }`}
          >
            <span>{r.name}</span>
            <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
              selectedRole === r.id 
                ? 'bg-zinc-800 text-zinc-200 dark:bg-zinc-200 dark:text-zinc-800' 
                : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-500'
            }`}>
              {r.total_chunks}
            </span>
          </button>
        ))}
      </div>

      {message && (
        <div className={`p-4 rounded-lg text-xs flex items-start gap-3 border ${
          message.type === 'success'
            ? 'bg-zinc-100 dark:bg-zinc-900 border-zinc-300 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200'
            : 'bg-rose-50/70 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300'
        }`}>
          <span className="leading-relaxed">{message.text}</span>
        </div>
      )}

      {/* Upload and Table Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Form */}
        <div className="rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-7 shadow-2xs space-y-6 transition-colors duration-200">
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Index Literature</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Add technical books for <strong className="font-medium text-zinc-800 dark:text-zinc-200">{currentRoleData?.name}</strong>.
            </p>
          </div>

          <form onSubmit={handleIngest} className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                Textbook Title *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Mitchell Machine Learning (Ch. 1-4)"
                value={sourceName}
                onChange={e => setSourceName(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 focus:border-zinc-400 dark:focus:border-zinc-600 focus:bg-white dark:focus:bg-zinc-900 focus:ring-2 focus:ring-zinc-200/60 dark:focus:ring-zinc-800 outline-none text-xs text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 transition-all"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                Corpus File (.PDF or .TXT) *
              </label>
              <label className="flex flex-col items-center justify-center border border-dashed border-zinc-200 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600 bg-zinc-50/40 dark:bg-zinc-950/40 rounded-lg p-6 cursor-pointer transition-all duration-200 group">
                <UploadCloud className="w-6 h-6 text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors mb-2" />
                <span className="text-xs font-medium text-zinc-700 dark:text-zinc-300 text-center">
                  {file ? file.name : 'Select document file'}
                </span>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={e => e.target.files && setFile(e.target.files[0])}
                  className="hidden"
                />
              </label>
            </div>

            <button
              type="submit"
              disabled={ingesting || !file || !sourceName}
              className="w-full py-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 text-xs font-medium transition-all duration-200 disabled:opacity-50 active:scale-[0.98] shadow-xs flex items-center justify-center gap-2"
            >
              {ingesting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
                  <span>Embedding Chunks...</span>
                </>
              ) : (
                <>
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Index into ChromaDB</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Indexed Corpus List */}
        <div className="lg:col-span-2 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-7 shadow-2xs space-y-6 transition-colors duration-200">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800/80">
            <div className="space-y-0.5">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                Corpus Literature — {currentRoleData?.name}
              </h3>
              <p className="font-mono text-[11px] text-zinc-400 dark:text-zinc-500">
                Collection: role_{selectedRole}
              </p>
            </div>

            <div className="text-right">
              <span className="text-[11px] font-mono text-zinc-400 dark:text-zinc-500">Indexed Chunks</span>
              <div className="text-lg font-light text-zinc-900 dark:text-zinc-100">{status?.total_chunks || 0}</div>
            </div>
          </div>

          {status && status.documents.length > 0 ? (
            <div className="divide-y divide-zinc-100 dark:divide-zinc-800/80">
              {status.documents.map((doc) => (
                <div key={doc.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-md bg-zinc-100 dark:bg-zinc-800/80 flex items-center justify-center text-zinc-500 dark:text-zinc-400 border border-zinc-200/50 dark:border-zinc-700/50">
                      <FileText className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <h4 className="font-medium text-xs text-zinc-900 dark:text-zinc-100">{doc.source_name}</h4>
                      <p className="text-[11px] text-zinc-400">{doc.filename} • {new Date(doc.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200/60 dark:border-zinc-700/60">
                    {doc.total_chunks} Chunks
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 space-y-2">
              <Layers className="w-8 h-8 text-zinc-300 dark:text-zinc-700 mx-auto" />
              <h4 className="text-xs font-medium text-zinc-700 dark:text-zinc-300">No Literature Indexed</h4>
              <p className="text-[11px] text-zinc-400 max-w-xs mx-auto">
                Index textbooks to ground the dynamic screening questions for this track.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
