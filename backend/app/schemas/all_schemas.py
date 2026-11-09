from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Candidate & Resume ---
class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None

class CandidateOut(BaseModel):
    id: str
    name: str
    email: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class ExtractedProfile(BaseModel):
    technical_skills: List[str] = []
    programming_languages: List[str] = []
    frameworks_libraries: List[str] = []
    databases: List[str] = []
    cloud_technologies: List[str] = []
    tools_platforms: List[str] = []
    projects: List[Dict[str, Any]] = []
    work_experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    domain_exposure: List[str] = []
    summary: Optional[str] = ""

class ResumeOut(BaseModel):
    id: str
    candidate_id: str
    original_filename: str
    extracted_profile: ExtractedProfile
    created_at: datetime
    class Config:
        from_attributes = True

# --- Roles ---
class RoleOut(BaseModel):
    id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    has_knowledge_base: bool = False
    total_chunks: int = 0
    total_documents: int = 0
    created_at: datetime
    class Config:
        from_attributes = True

# --- Knowledge Ingestion ---
class IngestResponse(BaseModel):
    document_id: str
    role_id: str
    filename: str
    source_name: str
    total_chunks: int
    message: str

class KnowledgeStatus(BaseModel):
    role_id: str
    role_name: str
    total_documents: int
    total_chunks: int
    is_ready: bool
    documents: List[Dict[str, Any]] = []

# --- Questions & Retrieval ---
class SourceReference(BaseModel):
    document_name: str
    page_number: Optional[int] = None
    chunk_id: str
    snippet: Optional[str] = None

class QuestionOut(BaseModel):
    id: str
    question_index: int
    question_text: str
    topic: str
    difficulty: str
    question_type: str
    expected_concepts: List[str] = []
    source_references: List[SourceReference] = []
    class Config:
        from_attributes = True

# --- Interactive Interview Session ---
class SessionCreate(BaseModel):
    candidate_name: str
    resume_id: str
    role_id: str

class SessionOut(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    resume_id: str
    role_id: str
    role_name: str
    status: str
    total_questions: int
    answered_questions: int
    current_question: Optional[QuestionOut] = None
    overall_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: str
    answer_text: str = Field(..., min_length=1)

class AnswerEvaluationOut(BaseModel):
    id: str
    answer_id: str
    score: float
    correctness: str
    strengths: List[str]
    missing_concepts: List[str]
    improvement_suggestions: List[str]
    evaluation_explanation: str
    class Config:
        from_attributes = True

class AnswerOut(BaseModel):
    id: str
    question_id: str
    question_text: str
    topic: str
    difficulty: str
    answer_text: str
    submitted_at: datetime
    evaluation: Optional[AnswerEvaluationOut] = None
    class Config:
        from_attributes = True

# --- Final Screening Report ---
class QuestionEvaluationDetail(BaseModel):
    question_id: str
    question_index: int
    question_text: str
    topic: str
    difficulty: str
    question_type: str
    candidate_answer: str
    score: float
    correctness: str
    strengths: List[str]
    missing_concepts: List[str]
    improvement_suggestions: List[str]
    evaluation_explanation: str
    source_references: List[SourceReference]

class FinalReportOut(BaseModel):
    session_id: str
    candidate_name: str
    role_name: str
    resume_summary: str
    overall_score: float
    total_questions: int
    questions_answered: int
    topic_performance: Dict[str, float]
    technical_performance: Dict[str, float]
    strengths: List[str]
    knowledge_gaps: List[str]
    recommendations: List[str]
    question_details: List[QuestionEvaluationDetail]
    generated_at: datetime
    class Config:
        from_attributes = True

