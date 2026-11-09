# End-to-End Demo Script for Walkthrough Video

This script outlines the exact sequence for demonstrating **TalentLens AI** for the mandatory submission video.

---

## Part 1: Architecture & Technology Stack (0:00 - 1:15)
1. **Introduction**:
   - "Welcome to the demonstration of TalentLens AI, an AI-powered role-based technical candidate screening system with a grounded RAG architecture."
2. **Key Architectural Pillars**:
   - Explain the stack: **FastAPI**, **SQLAlchemy**, **ChromaDB**, **Sentence Transformers (`all-MiniLM-L6-v2`)**, **PyMuPDF**, and **React + TypeScript + Tailwind CSS**.
   - Highlight the design rule: "Questions are not hardcoded or generic; they are dynamically generated from candidate resumes intersected with role-specific literature stored in ChromaDB."

---

## Part 2: Knowledge Base Management & Corpus Ingestion (1:15 - 2:30)
1. Navigate to the **Knowledge Base** tab in the UI:
   - Show the configured roles: **AI/ML Engineer**, **Data Science / Applied ML**, and **Backend Engineer**.
   - Highlight the indexed corpus for AI/ML: *The Hundred-Page Machine Learning Book* by Andriy Burkov (118 chunks in `role_ai_ml_engineer`).
   - Highlight the indexed corpus for Backend Engineer: *Backend Systems Engineering Handbook* (in `role_backend_engineer`).
2. Demonstrate Ingestion:
   - Upload a new document or demonstrate idempotent duplicate protection.

---

## Part 3: Candidate Entry & Resume Parsing (2:30 - 3:45)
1. Navigate to **New Screening**:
   - Enter candidate credentials: `Alex Rivera` (`alex.rivera@example.com`).
   - Select role: **AI/ML Engineer**.
   - Drag and drop or upload a sample technical resume (`.pdf` or `.txt`).
2. Click **"Extract Profile & Continue"**:
   - Show the parsed resume preview: Technical skills, programming languages, databases, cloud tools, and project summaries.
   - Note: Qualifications are not fabricated; extraction is structured and validated against the resume content.

---

## Part 4: Dynamic Question Generation & Grounding (3:45 - 5:15)
1. Click **"Launch Interview Workspace"**:
   - Observe the backend orchestrating Context Construction → Dynamic Query Generation → ChromaDB Retrieval → Structured Question Generation.
2. Inspect the first question:
   - Show topic, progressive difficulty tag, and question type (`conceptual`, `practical`, `scenario_based`).
   - **Showcase the Grounded Knowledge Reference drawer**: Point out the textbook citation, page number, and source passage retrieved via RAG.

---

## Part 5: Interactive Interview & Answer Evaluation (5:15 - 6:45)
1. Answer the current question:
   - Provide a technical answer explaining concepts (e.g. gradient descent update formula, learning rate impact on oscillations, and momentum).
   - Click **"Submit Answer"**: observe real-time evaluation against the rubric and reference text.
   - Proceed to the next question.
2. Refresh the browser page to demonstrate session persistence and continuity.

---

## Part 6: Comprehensive Screening Report & PDF Export (6:45 - 8:00)
1. Click **"Finish & View Report"**:
   - Display the overall screening score (e.g. `4.2 / 5.0`).
   - Showcase the **Multi-Criteria Radar Chart** (Technical Correctness, Conceptual Depth, Completeness, Clarity).
   - Showcase the **Topic Performance Bar Chart**.
   - Review the candidate's Demonstrated Strengths, Identified Knowledge Gaps, and Tailored Improvement Recommendations.
   - Expand the Question-Wise accordion to view candidate answers alongside the AI evaluator's feedback and source citations.
2. Click **"Export Official PDF Report"**:
   - Open and display the professionally generated PDF screening report.

