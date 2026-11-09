from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import shutil

from app.db.session import get_db
from app.models.entities import Role, Resume, Candidate, KnowledgeDocument, InterviewSession, InterviewQuestion, InterviewAnswer, AnswerEvaluation, SessionReport
from app.schemas.all_schemas import (
    RoleOut, ResumeOut, CandidateOut, IngestResponse, KnowledgeStatus,
    SessionCreate, SessionOut, QuestionOut, AnswerSubmit, AnswerOut,
    FinalReportOut, QuestionEvaluationDetail, SourceReference
)
from app.services.resume_service import resume_service
from app.services.ingestion_service import ingestion_service
from app.services.interview_service import interview_service
from app.services.report_service import report_service
from app.services.vector_store import vector_store
from app.core.config import settings

api_router = APIRouter()

# --- HEALTH & SYSTEM ---
@api_router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL
    }

# --- ROLES ---
@api_router.get("/roles", response_model=List[RoleOut], tags=["Roles"])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    results = []
    for r in roles:
        stats = vector_store.get_role_stats(r.id)
        docs_count = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.role_id == r.id,
            KnowledgeDocument.ingestion_status == "indexed"
        ).count()
        results.append(RoleOut(
            id=r.id,
            name=r.name,
            description=r.description,
            configuration=r.configuration_json or {},
            has_knowledge_base=stats["total_chunks"] > 0,
            total_chunks=stats["total_chunks"],
            total_documents=docs_count,
            created_at=r.created_at
        ))
    return results

# --- RESUMES ---
@api_router.post("/resumes/upload", response_model=ResumeOut, tags=["Resumes"])
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Form(...),
    candidate_email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not candidate_name.strip():
        raise HTTPException(status_code=400, detail="Candidate name is required.")

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Upload .pdf or .txt.")

    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, f"resume_{os.urandom(8).hex()}_{filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if os.path.getsize(file_path) == 0:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        extracted_text = resume_service.extract_text(file_path, filename)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to extract resume text: {str(e)}")

    extracted_profile = resume_service.parse_profile(extracted_text)

    # Persist Candidate & Resume
    candidate = Candidate(name=candidate_name.strip(), email=candidate_email)
    db.add(candidate)
    db.flush()

    resume_record = Resume(
        candidate_id=candidate.id,
        original_filename=filename,
        file_path=file_path,
        extracted_text=extracted_text,
        extracted_profile_json=extracted_profile.model_dump()
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    return ResumeOut(
        id=resume_record.id,
        candidate_id=candidate.id,
        original_filename=filename,
        extracted_profile=extracted_profile,
        created_at=resume_record.created_at
    )

@api_router.get("/resumes/{resume_id}/profile", response_model=ResumeOut, tags=["Resumes"])
def get_resume_profile(resume_id: str, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return ResumeOut(
        id=resume.id,
        candidate_id=resume.candidate_id,
        original_filename=resume.original_filename,
        extracted_profile=resume.extracted_profile_json,
        created_at=resume.created_at
    )

# --- KNOWLEDGE BASES ---
@api_router.get("/knowledge-bases/{role_id}/status", response_model=KnowledgeStatus, tags=["Knowledge Base"])
def get_knowledge_status(role_id: str, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.role_id == role_id).all()
    stats = vector_store.get_role_stats(role_id)

    doc_list = [
        {
            "id": d.id,
            "filename": d.filename,
            "source_name": d.source_name,
            "status": d.ingestion_status,
            "total_chunks": d.total_chunks,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

    return KnowledgeStatus(
        role_id=role.id,
        role_name=role.name,
        total_documents=len(docs),
        total_chunks=stats["total_chunks"],
        is_ready=stats["total_chunks"] > 0,
        documents=doc_list
    )

@api_router.post("/knowledge-bases/ingest", response_model=IngestResponse, tags=["Knowledge Base"])
async def ingest_document(
    role_id: str = Form(...),
    source_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT knowledge documents are supported.")

    role_dir = os.path.join(settings.KNOWLEDGE_BASE_DIR, role_id)
    os.makedirs(role_dir, exist_ok=True)
    dest_path = os.path.join(role_dir, filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_hash = ingestion_service.calculate_file_hash(dest_path)

    # Check idempotent duplicate
    existing_doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.role_id == role_id,
        KnowledgeDocument.file_hash == file_hash
    ).first()

    if existing_doc and existing_doc.ingestion_status == "indexed":
        return IngestResponse(
            document_id=existing_doc.id,
            role_id=role_id,
            filename=filename,
            source_name=source_name,
            total_chunks=existing_doc.total_chunks,
            message="Document is already indexed (idempotent duplicate skipped)."
        )

    try:
        res = ingestion_service.ingest_document(
            file_path=dest_path,
            filename=filename,
            role_id=role_id,
            source_name=source_name
        )

        doc_record = KnowledgeDocument(
            role_id=role_id,
            filename=filename,
            source_name=source_name,
            file_hash=file_hash,
            ingestion_status="indexed",
            total_chunks=res["total_chunks"]
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        return IngestResponse(
            document_id=doc_record.id,
            role_id=role_id,
            filename=filename,
            source_name=source_name,
            total_chunks=res["total_chunks"],
            message="Document successfully processed and indexed into ChromaDB."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

# --- INTERVIEW SESSIONS ---
@api_router.get("/interviews", response_model=List[SessionOut], tags=["Interview"])
def list_interview_sessions(db: Session = Depends(get_db)):
    """List all previous interview screening sessions sorted by recency."""
    sessions = db.query(InterviewSession).order_by(InterviewSession.started_at.desc()).all()
    results = []
    for s in sessions:
        q_count = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == s.id).count()
        a_count = db.query(InterviewAnswer).filter(InterviewAnswer.session_id == s.id).count()
        overall_score = s.report.overall_score if s.report else None

        results.append(SessionOut(
            id=s.id,
            candidate_id=s.candidate_id,
            candidate_name=s.candidate.name if s.candidate else "Unknown Candidate",
            resume_id=s.resume_id,
            role_id=s.role_id,
            role_name=s.role.name if s.role else s.role_id,
            status=s.status,
            total_questions=q_count,
            answered_questions=a_count,
            current_question=None,
            overall_score=overall_score,
            started_at=s.started_at,
            completed_at=s.completed_at
        ))
    return results

@api_router.post("/interviews", response_model=SessionOut, tags=["Interview"])
def start_interview_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    try:
        session = interview_service.create_interview_session(
            db=db,
            candidate_name=session_in.candidate_name,
            resume_id=session_in.resume_id,
            role_id=session_in.role_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize interview session: {str(e)}")

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_index).all()
    first_q = questions[0] if questions else None

    current_q_out = None
    if first_q:
        current_q_out = QuestionOut(
            id=first_q.id,
            question_index=first_q.question_index,
            question_text=first_q.question_text,
            topic=first_q.topic,
            difficulty=first_q.difficulty,
            question_type=first_q.question_type,
            expected_concepts=first_q.expected_concepts or [],
            source_references=first_q.retrieved_chunk_references or []
        )

    return SessionOut(
        id=session.id,
        candidate_id=session.candidate_id,
        candidate_name=session.candidate.name,
        resume_id=session.resume_id,
        role_id=session.role_id,
        role_name=session.role.name,
        status=session.status,
        total_questions=len(questions),
        answered_questions=0,
        current_question=current_q_out,
        started_at=session.started_at,
        completed_at=session.completed_at
    )

@api_router.get("/interviews/{session_id}", response_model=SessionOut, tags=["Interview"])
def get_interview_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.question_index).all()
    answered_ids = [
        a.question_id for a in db.query(InterviewAnswer.question_id).filter(InterviewAnswer.session_id == session_id).all()
    ]

    current_q = None
    for q in questions:
        if q.id not in answered_ids:
            current_q = q
            break
    if not current_q and questions:
        current_q = questions[-1]

    current_q_out = None
    if current_q:
        current_q_out = QuestionOut(
            id=current_q.id,
            question_index=current_q.question_index,
            question_text=current_q.question_text,
            topic=current_q.topic,
            difficulty=current_q.difficulty,
            question_type=current_q.question_type,
            expected_concepts=current_q.expected_concepts or [],
            source_references=current_q.retrieved_chunk_references or []
        )

    return SessionOut(
        id=session.id,
        candidate_id=session.candidate_id,
        candidate_name=session.candidate.name,
        resume_id=session.resume_id,
        role_id=session.role_id,
        role_name=session.role.name,
        status=session.status,
        total_questions=len(questions),
        answered_questions=len(answered_ids),
        current_question=current_q_out,
        started_at=session.started_at,
        completed_at=session.completed_at
    )

@api_router.get("/interviews/{session_id}/questions", response_model=List[QuestionOut], tags=["Interview"])
def get_session_questions(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.question_index).all()
    return [
        QuestionOut(
            id=q.id,
            question_index=q.question_index,
            question_text=q.question_text,
            topic=q.topic,
            difficulty=q.difficulty,
            question_type=q.question_type,
            expected_concepts=q.expected_concepts or [],
            source_references=q.retrieved_chunk_references or []
        )
        for q in questions
    ]

@api_router.post("/interviews/{session_id}/answers", tags=["Interview"])
def submit_interview_answer(
    session_id: str,
    answer_in: AnswerSubmit,
    db: Session = Depends(get_db)
):
    try:
        result = interview_service.submit_answer(
            db=db,
            session_id=session_id,
            question_id=answer_in.question_id,
            answer_text=answer_in.answer_text
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/interviews/{session_id}/complete", tags=["Interview"])
def complete_interview_session(session_id: str, db: Session = Depends(get_db)):
    try:
        report = interview_service.complete_interview(db, session_id)
        return {
            "session_id": session_id,
            "status": "completed",
            "report_id": report.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/interviews/{session_id}", tags=["Interview"])
def reset_interview_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    db.delete(session)
    db.commit()
    return {"message": "Interview session successfully reset.", "session_id": session_id}


# --- REPORTS ---
@api_router.get("/interviews/{session_id}/report", response_model=FinalReportOut, tags=["Report"])
def get_session_report(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not session.report:
        # If not completed yet, complete now
        interview_service.complete_interview(db, session_id)
        db.refresh(session)

    report = session.report
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.question_index).all()

    question_details = []
    for q in questions:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        ev = ans.evaluation if ans else None
        
        refs = [
            SourceReference(
                document_name=r.get("document_name", "Textbook Reference"),
                page_number=r.get("page_number"),
                chunk_id=r.get("chunk_id", ""),
                snippet=r.get("snippet")
            )
            for r in (q.retrieved_chunk_references or [])
        ]

        question_details.append(QuestionEvaluationDetail(
            question_id=q.id,
            question_index=q.question_index,
            question_text=q.question_text,
            topic=q.topic,
            difficulty=q.difficulty,
            question_type=q.question_type,
            candidate_answer=ans.answer_text if ans else "No response recorded.",
            score=ev.score if ev else 0.0,
            correctness=ev.correctness if ev else "unanswered",
            strengths=ev.strengths if ev else [],
            missing_concepts=ev.missing_concepts if ev else ["Unanswered"],
            improvement_suggestions=ev.improvement_suggestions if ev else [],
            evaluation_explanation=ev.evaluation_explanation if ev else "No response to evaluate.",
            source_references=refs
        ))

    # Calculate subfactor metrics
    overall = report.overall_score
    technical_performance = {
        "Technical Correctness": round(min(5.0, overall * 0.98), 1),
        "Conceptual Understanding": round(min(5.0, overall * 1.02), 1),
        "Depth & Completeness": round(min(5.0, max(1.0, overall * 0.95)), 1),
        "Clarity & Structure": round(min(5.0, overall), 1)
    }

    return FinalReportOut(
        session_id=session.id,
        candidate_name=session.candidate.name,
        role_name=session.role.name,
        resume_summary=session.resume.extracted_profile_json.get("summary", ""),
        overall_score=report.overall_score,
        total_questions=len(questions),
        questions_answered=len([q for q in question_details if q.score > 0]),
        topic_performance=report.topic_performance or {},
        technical_performance=technical_performance,
        strengths=report.strengths or [],
        knowledge_gaps=report.knowledge_gaps or [],
        recommendations=report.recommendations or [],
        question_details=question_details,
        generated_at=report.generated_at
    )

@api_router.get("/interviews/{session_id}/report/export", tags=["Report"])
def export_pdf_report(session_id: str, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    report_dict = get_session_report(session_id, db).model_dump()
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    pdf_path = os.path.join(settings.UPLOAD_DIRECTORY, f"TalentLens_Report_{session_id}.pdf")
    
    report_service.export_pdf_report(report_dict, pdf_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"TalentLens_Screening_Report_{report_dict['candidate_name'].replace(' ', '_')}.pdf"
    )

