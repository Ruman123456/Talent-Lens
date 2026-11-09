import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="candidate", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    extracted_text = Column(Text, nullable=False)
    extracted_profile_json = Column(JSON, nullable=False)  # Structured profile (skills, projects, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="resumes")
    sessions = relationship("InterviewSession", back_populates="resume")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(64), primary_key=True)  # e.g., 'ai_ml_engineer', 'data_science', 'backend_engineer'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    configuration_json = Column(JSON, nullable=False)  # Expected competencies, topics, defaults
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_documents = relationship("KnowledgeDocument", back_populates="role", cascade="all, delete-orphan")
    sessions = relationship("InterviewSession", back_populates="role")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(String(64), ForeignKey("roles.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    source_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    ingestion_status = Column(String(32), default="pending")  # pending, indexed, failed
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="knowledge_documents")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    role_id = Column(String(64), ForeignKey("roles.id"), nullable=False)
    status = Column(String(32), default="in_progress")  # in_progress, completed, abandoned
    generated_context = Column(JSON, nullable=True)  # Focus areas, candidate strengths/gaps
    retrieval_metadata = Column(JSON, nullable=True)  # Query log and chunk ids used
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", back_populates="interview_sessions")
    resume = relationship("Resume", back_populates="sessions")
    role = relationship("Role", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    answers = relationship("InterviewAnswer", back_populates="session", cascade="all, delete-orphan")
    report = relationship("SessionReport", back_populates="session", uselist=False, cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    question_index = Column(Integer, default=1)
    question_text = Column(Text, nullable=False)
    topic = Column(String(128), nullable=False)
    difficulty = Column(String(32), default="medium")  # easy, medium, hard
    question_type = Column(String(64), default="conceptual")  # conceptual, practical, scenario_based, problem_solving
    evaluation_rubric = Column(JSON, nullable=False)
    expected_concepts = Column(JSON, nullable=False)
    retrieved_chunk_references = Column(JSON, nullable=False)  # [{document_name, page_number, chunk_id, snippet}]
    generation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False)

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("interview_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")

class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    answer_id = Column(String(36), ForeignKey("interview_answers.id"), nullable=False)
    score = Column(Float, nullable=False)  # 1.0 to 5.0
    correctness = Column(String(64), nullable=False)  # correct, partially_correct, incorrect, vague
    strengths = Column(JSON, nullable=False)
    missing_concepts = Column(JSON, nullable=False)
    improvement_suggestions = Column(JSON, nullable=False)
    evaluation_explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    answer = relationship("InterviewAnswer", back_populates="evaluation")

class SessionReport(Base):
    __tablename__ = "session_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    topic_performance = Column(JSON, nullable=False)
    strengths = Column(JSON, nullable=False)
    knowledge_gaps = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="report")

