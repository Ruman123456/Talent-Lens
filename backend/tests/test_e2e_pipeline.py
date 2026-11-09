import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.models.entities import Role, KnowledgeDocument
from app.services.vector_store import vector_store
from app.services.resume_service import resume_service
from app.services.ingestion_service import ingestion_service
from app.services.retrieval_service import retrieval_service

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_list_roles():
    response = client.get("/api/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 3
    role_ids = [r["id"] for r in roles]
    assert "ai_ml_engineer" in role_ids
    assert "data_science" in role_ids
    assert "backend_engineer" in role_ids

def test_knowledge_base_status():
    response = client.get("/api/knowledge-bases/ai_ml_engineer/status")
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == "ai_ml_engineer"
    assert data["total_chunks"] > 0
    assert data["is_ready"] is True

def test_document_chunking_and_metadata():
    pages = [
        {"page_number": 1, "text": "Paragraph 1 about machine learning.\n\nParagraph 2 discussing gradient descent optimization."},
        {"page_number": 2, "text": "Paragraph 3 about regularizing neural networks.\n\nParagraph 4 on cross validation."}
    ]
    chunks = ingestion_service.chunk_document(pages, chunk_size=200, chunk_overlap=30)
    assert len(chunks) >= 1
    assert "page_number" in chunks[0]
    assert "text" in chunks[0]

def test_resume_upload_and_extraction():
    sample_resume = """
    Jane Doe
    jane.doe@example.com
    Skills: Python, PyTorch, FastAPI, PostgreSQL, Docker, Machine Learning, Scikit-learn
    Experience: Machine Learning Engineer Intern at AI Corp. Built RAG pipelines and optimized latency.
    Projects: Neural Search Engine - Indexed millions of embeddings with ChromaDB and FAISS.
    Education: B.S. in Computer Science
    """
    response = client.post(
        "/api/resumes/upload",
        data={"candidate_name": "Jane Doe", "candidate_email": "jane@example.com"},
        files={"file": ("resume.txt", sample_resume.encode("utf-8"), "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] is not None
    assert "technical_skills" in data["extracted_profile"]
    assert len(data["extracted_profile"]["technical_skills"]) > 0
    return data["id"]

def test_interview_full_lifecycle():
    # 1. Upload resume
    sample_resume = "Alex Rivera\nSkills: Python, FastAPI, Machine Learning, Gradient Descent, PyTorch.\nProjects: Image Classifier."
    res_resp = client.post(
        "/api/resumes/upload",
        data={"candidate_name": "Alex Rivera", "candidate_email": "alex@example.com"},
        files={"file": ("alex_resume.txt", sample_resume.encode("utf-8"), "text/plain")}
    )
    assert res_resp.status_code == 200
    resume_id = res_resp.json()["id"]

    # 2. Start Interview Session
    session_resp = client.post(
        "/api/interviews",
        json={
            "candidate_name": "Alex Rivera",
            "resume_id": resume_id,
            "role_id": "ai_ml_engineer"
        }
    )
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    session_id = session_data["id"]
    assert session_data["total_questions"] >= 6
    assert session_data["current_question"] is not None

    # 3. Retrieve Questions
    q_resp = client.get(f"/api/interviews/{session_id}/questions")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) >= 6

    # Verify source citations exist on questions
    first_q = questions[0]
    assert "source_references" in first_q
    assert len(first_q["source_references"]) > 0

    # 4. Submit Answers
    for q in questions[:2]:
        ans_resp = client.post(
            f"/api/interviews/{session_id}/answers",
            json={
                "question_id": q["id"],
                "answer_text": "Gradient descent computes the loss gradient with respect to model parameters and updates weights in opposite direction using learning rate."
            }
        )
        assert ans_resp.status_code == 200

    # 5. Complete Interview & Generate Report
    comp_resp = client.post(f"/api/interviews/{session_id}/complete")
    assert comp_resp.status_code == 200

    report_resp = client.get(f"/api/interviews/{session_id}/report")
    assert report_resp.status_code == 200
    report = report_resp.json()
    assert "overall_score" in report
    assert "topic_performance" in report
    assert "strengths" in report
if __name__ == "__main__":
    print("Running health check...")
    test_health_check()
    print("OK")
    print("Running list roles...")
    test_list_roles()
    print("OK")
    print("Running knowledge base status...")
    test_knowledge_base_status()
    print("OK")
    print("Running document chunking...")
    test_document_chunking_and_metadata()
    print("OK")
    print("Running resume upload and extraction...")
    test_resume_upload_and_extraction()
    print("OK")
    print("Running interview full lifecycle...")
    test_interview_full_lifecycle()
    print("ALL TESTS PASSED SUCCESSFULLY!")

