from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

from app.models.entities import (
    Candidate, Resume, Role, KnowledgeDocument, 
    InterviewSession, InterviewQuestion, InterviewAnswer, 
    AnswerEvaluation, SessionReport
)
from app.services.context_builder import context_builder
from app.services.retrieval_service import retrieval_service
from app.services.question_generator import question_generator
from app.services.evaluation_service import evaluation_service
from app.services.report_service import report_service
from app.services.vector_store import vector_store

class InterviewService:
    @staticmethod
    def create_interview_session(
        db: Session,
        candidate_name: str,
        resume_id: str,
        role_id: str
    ) -> InterviewSession:
        # Validate resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume ID {resume_id} not found.")

        # Validate role
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role ID {role_id} not found.")

        # Check knowledge base sufficiency
        kb_stats = vector_store.get_role_stats(role_id)
        if kb_stats["total_chunks"] == 0:
            raise ValueError(
                f"Knowledge base for role '{role.name}' has no indexed documents. "
                "Please ingest role-specific textbook/corpus before starting the interview."
            )

        candidate = resume.candidate
        if candidate_name and candidate.name != candidate_name:
            candidate.name = candidate_name
            db.commit()

        # Step 1: Resume-aware Context Construction
        role_config = role.configuration_json or {}
        context_data = context_builder.build_interview_context(
            extracted_profile=resume.extracted_profile_json,
            role_name=role.name,
            role_competencies=role_config.get("competencies", []),
            role_topics=role_config.get("topics", [])
        )

        # Step 2: RAG Retrieval from Role-Filtered Knowledge Base
        retrieved_chunks = retrieval_service.retrieve_context_for_queries(
            role_id=role_id,
            queries=context_data.get("queries", [])
        )

        # Step 3: Dynamic Question Generation
        generated_questions = question_generator.generate_interview_questions(
            candidate_name=candidate.name,
            role_name=role.name,
            extracted_profile=resume.extracted_profile_json,
            context_data=context_data,
            retrieved_chunks=retrieved_chunks,
            num_questions=6
        )

        # Step 4: Persist Session & Questions
        session = InterviewSession(
            candidate_id=candidate.id,
            resume_id=resume.id,
            role_id=role.id,
            status="in_progress",
            generated_context=context_data,
            retrieval_metadata={
                "queries_executed": context_data.get("queries", []),
                "total_chunks_retrieved": len(retrieved_chunks),
                "chunks": [
                    {"chunk_id": c.get("chunk_id"), "similarity": c.get("similarity")}
                    for c in retrieved_chunks[:6]
                ]
            }
        )
        db.add(session)
        db.flush()

        for q_data in generated_questions:
            question = InterviewQuestion(
                session_id=session.id,
                question_index=q_data["question_index"],
                question_text=q_data["question_text"],
                topic=q_data["topic"],
                difficulty=q_data["difficulty"],
                question_type=q_data["question_type"],
                evaluation_rubric=q_data["evaluation_rubric"],
                expected_concepts=q_data["expected_concepts"],
                retrieved_chunk_references=q_data["source_references"],
                generation_metadata=q_data.get("generation_metadata", {})
            )
            db.add(question)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def submit_answer(
        db: Session,
        session_id: str,
        question_id: str,
        answer_text: str
    ) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Interview session not found.")
        if session.status == "completed":
            raise ValueError("This interview session has already been completed.")

        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == session_id
        ).first()
        if not question:
            raise ValueError("Question not found in this interview session.")

        # Check if already answered
        existing_answer = db.query(InterviewAnswer).filter(
            InterviewAnswer.question_id == question_id,
            InterviewAnswer.session_id == session_id
        ).first()

        if existing_answer:
            existing_answer.answer_text = answer_text
            existing_answer.submitted_at = datetime.utcnow()
            answer_record = existing_answer
        else:
            answer_record = InterviewAnswer(
                session_id=session_id,
                question_id=question_id,
                answer_text=answer_text
            )
            db.add(answer_record)
        db.flush()

        # Evaluate Answer
        eval_result = evaluation_service.evaluate_candidate_answer(
            question_text=question.question_text,
            topic=question.topic,
            difficulty=question.difficulty,
            expected_concepts=question.expected_concepts,
            evaluation_rubric=question.evaluation_rubric,
            source_references=question.retrieved_chunk_references,
            answer_text=answer_text
        )

        existing_eval = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == answer_record.id).first()
        if existing_eval:
            existing_eval.score = eval_result["score"]
            existing_eval.correctness = eval_result["correctness"]
            existing_eval.strengths = eval_result["strengths"]
            existing_eval.missing_concepts = eval_result["missing_concepts"]
            existing_eval.improvement_suggestions = eval_result["improvement_suggestions"]
            existing_eval.evaluation_explanation = eval_result["evaluation_explanation"]
        else:
            eval_record = AnswerEvaluation(
                answer_id=answer_record.id,
                score=eval_result["score"],
                correctness=eval_result["correctness"],
                strengths=eval_result["strengths"],
                missing_concepts=eval_result["missing_concepts"],
                improvement_suggestions=eval_result["improvement_suggestions"],
                evaluation_explanation=eval_result["evaluation_explanation"]
            )
            db.add(eval_record)

        db.commit()
        db.refresh(answer_record)

        # Check if all questions answered
        total_questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).count()
        answered_count = db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session_id).count()

        return {
            "answer_id": answer_record.id,
            "session_id": session_id,
            "question_id": question_id,
            "total_questions": total_questions,
            "answered_count": answered_count,
            "is_all_answered": answered_count >= total_questions
        }

    @staticmethod
    def complete_interview(db: Session, session_id: str) -> SessionReport:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found.")

        # Collect all questions and evaluations
        questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.question_index).all()
        evaluated_qa = []

        for q in questions:
            ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
            if ans and ans.evaluation:
                ev = ans.evaluation
                evaluated_qa.append({
                    "question_id": q.id,
                    "question_index": q.question_index,
                    "topic": q.topic,
                    "difficulty": q.difficulty,
                    "score": ev.score,
                    "correctness": ev.correctness,
                    "strengths": ev.strengths,
                    "missing_concepts": ev.missing_concepts,
                    "improvement_suggestions": ev.improvement_suggestions,
                    "evaluation_explanation": ev.evaluation_explanation
                })

        report_summary = report_service.generate_screening_report(
            candidate_name=session.candidate.name,
            role_name=session.role.name,
            resume_summary=session.resume.extracted_profile_json.get("summary", ""),
            evaluated_qa_list=evaluated_qa
        )

        existing_report = db.query(SessionReport).filter(SessionReport.session_id == session_id).first()
        if existing_report:
            existing_report.overall_score = report_summary["overall_score"]
            existing_report.summary = report_summary["summary"]
            existing_report.topic_performance = report_summary["topic_performance"]
            existing_report.strengths = report_summary["strengths"]
            existing_report.knowledge_gaps = report_summary["knowledge_gaps"]
            existing_report.recommendations = report_summary["recommendations"]
            report_entity = existing_report
        else:
            report_entity = SessionReport(
                session_id=session_id,
                overall_score=report_summary["overall_score"],
                summary=report_summary["summary"],
                topic_performance=report_summary["topic_performance"],
                strengths=report_summary["strengths"],
                knowledge_gaps=report_summary["knowledge_gaps"],
                recommendations=report_summary["recommendations"]
            )
            db.add(report_entity)

        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(report_entity)
        return report_entity

interview_service = InterviewService()

