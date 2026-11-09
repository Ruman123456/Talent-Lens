import axios from 'axios';
import { 
  Role, ResumeData, InterviewSession, 
  InterviewQuestion, FinalReport, KnowledgeStatus 
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const apiService = {
  // Roles
  getRoles: async (): Promise<Role[]> => {
    const res = await api.get<Role[]>('/roles');
    return res.data;
  },

  // Knowledge Base
  getKnowledgeStatus: async (roleId: string): Promise<KnowledgeStatus> => {
    const res = await api.get<KnowledgeStatus>(`/knowledge-bases/${roleId}/status`);
    return res.data;
  },

  ingestDocument: async (roleId: string, sourceName: string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('role_id', roleId);
    formData.append('source_name', sourceName);
    formData.append('file', file);
    const res = await api.post('/knowledge-bases/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // Resume Upload
  uploadResume: async (file: File, name: string, email?: string): Promise<ResumeData> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('candidate_name', name);
    if (email) formData.append('candidate_email', email);
    
    const res = await api.post<ResumeData>('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // Interview Sessions
  getSessions: async (): Promise<InterviewSession[]> => {
    const res = await api.get<InterviewSession[]>('/interviews');
    return res.data;
  },

  startInterview: async (candidateName: string, resumeId: string, roleId: string): Promise<InterviewSession> => {
    const res = await api.post<InterviewSession>('/interviews', {
      candidate_name: candidateName,
      resume_id: resumeId,
      role_id: roleId
    });
    return res.data;
  },

  getSession: async (sessionId: string): Promise<InterviewSession> => {
    const res = await api.get<InterviewSession>(`/interviews/${sessionId}`);
    return res.data;
  },

  getSessionQuestions: async (sessionId: string): Promise<InterviewQuestion[]> => {
    const res = await api.get<InterviewQuestion[]>(`/interviews/${sessionId}/questions`);
    return res.data;
  },

  submitAnswer: async (sessionId: string, questionId: string, answerText: string): Promise<any> => {
    const res = await api.post(`/interviews/${sessionId}/answers`, {
      question_id: questionId,
      answer_text: answerText
    });
    return res.data;
  },

  completeInterview: async (sessionId: string): Promise<any> => {
    const res = await api.post(`/interviews/${sessionId}/complete`);
    return res.data;
  },

  resetInterview: async (sessionId: string): Promise<any> => {
    const res = await api.delete(`/interviews/${sessionId}`);
    return res.data;
  },

  // Report
  getReport: async (sessionId: string): Promise<FinalReport> => {
    const res = await api.get<FinalReport>(`/interviews/${sessionId}/report`);
    return res.data;
  },

  getReportPdfUrl: (sessionId: string): string => {
    return `${API_BASE_URL}/interviews/${sessionId}/report/export`;
  }
};

