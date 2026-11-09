export interface ExtractedProfile {
  technical_skills: string[];
  programming_languages: string[];
  frameworks_libraries: string[];
  databases: string[];
  cloud_technologies: string[];
  tools_platforms: string[];
  projects: Array<{
    name: string;
    description: string;
    technologies: string[];
  }>;
  work_experience: Array<{
    role: string;
    company: string;
    highlights: string;
  }>;
  education: Array<{
    degree: string;
    institution: string;
    year: string;
  }>;
  domain_exposure: string[];
  summary: string;
}

export interface ResumeData {
  id: string;
  candidate_id: string;
  original_filename: string;
  extracted_profile: ExtractedProfile;
  created_at: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  configuration: {
    competencies: string[];
    topics: string[];
  };
  has_knowledge_base: boolean;
  total_chunks: number;
  total_documents: number;
  created_at: string;
}

export interface SourceReference {
  document_name: string;
  page_number?: number;
  chunk_id: string;
  snippet?: string;
}

export interface InterviewQuestion {
  id: string;
  question_index: number;
  question_text: string;
  topic: string;
  difficulty: string;
  question_type: string;
  expected_concepts: string[];
  source_references: SourceReference[];
}

export interface InterviewSession {
  id: string;
  candidate_id: string;
  candidate_name: string;
  resume_id: string;
  role_id: string;
  role_name: string;
  status: string;
  total_questions: number;
  answered_questions: number;
  current_question?: InterviewQuestion;
  overall_score?: number;
  started_at: string;
  completed_at?: string;
}

export interface QuestionEvaluationDetail {
  question_id: string;
  question_index: number;
  question_text: string;
  topic: string;
  difficulty: string;
  question_type: string;
  candidate_answer: string;
  score: number;
  correctness: string;
  strengths: string[];
  missing_concepts: string[];
  improvement_suggestions: string[];
  evaluation_explanation: string;
  source_references: SourceReference[];
}

export interface FinalReport {
  session_id: string;
  candidate_name: string;
  role_name: string;
  resume_summary: string;
  summary?: string;
  overall_score: number;
  total_questions: number;
  questions_answered: number;
  topic_performance: Record<string, number>;
  technical_performance: Record<string, number>;
  strengths: string[];
  knowledge_gaps: string[];
  recommendations: string[];
  question_details: QuestionEvaluationDetail[];
  generated_at: string;
}

export interface KnowledgeDocument {
  id: string;
  filename: string;
  source_name: string;
  status: string;
  total_chunks: number;
  created_at: string;
}

export interface KnowledgeStatus {
  role_id: string;
  role_name: string;
  total_documents: number;
  total_chunks: number;
  is_ready: boolean;
  documents: KnowledgeDocument[];
}
