# TalentLens AI — System Architecture Overview

## 1. Architectural Philosophy
TalentLens AI is designed with a service-based architecture ensuring clear separation of concerns, testability, and deterministic traceability:

```
[ Frontend: React + TS + Tailwind + Vite ]
                   │
                   ▼  (RESTful JSON / Multipart HTTP)
[ FastAPI Backend API Layer (app/api/endpoints.py) ]
                   │
      ┌────────────┼──────────────────────────┐
      ▼            ▼                          ▼
[Resume Service] [Context Builder]     [Interview Service]
      │            │                          │
      │            ▼                          ▼
      │    [Retrieval Service] ───► [Question Generator]
      │            │                          │
      │            ▼                          ▼
      │    [Chroma Vector Store]      [Evaluation Service]
      │    (Sentence Transformers)            │
      │                                       ▼
      └──────────────────────────────► [Report Service]
                                              │
                                              ▼
                                    [Relational Database]
                                      (SQLite / Postgres)
```

## 2. Core Service Responsibilities

### `resume_service.py`
- Handles multi-format document ingest (`.pdf` via PyMuPDF and `.txt`).
- Extracts text while removing formatting artifacts.
- Utilizes structured extraction with fallback validation to parse skills, programming languages, databases, tools, projects, and education.

### `context_builder.py`
- Prevents simplistic resume-to-query concatenation.
- Synthesizes candidate strengths and role expectations into 4 to 6 focused semantic search queries exploring foundational algorithms, resume-relevant tools, and candidate competency gaps.

### `retrieval_service.py` & `vector_store.py`
- Embeds queries using `all-MiniLM-L6-v2`.
- Queries role-specific logical ChromaDB collections (`role_{role_id}`).
- Deduplicates matching chunks across multi-query retrieval passes.
- Applies strict similarity thresholds to eliminate noise.

### `question_generator.py`
- Generates 6 progressive, grounded interview challenges across difficulty spectrums (easy, medium, hard).
- Enforces question types: conceptual, practical, scenario-based, problem-solving.
- Embeds source citations (`document_name`, `page_number`, `chunk_id`, `snippet`) directly into each question record.

### `evaluation_service.py`
- Implements multi-criteria evaluation scoring from 1.0 to 5.0.
- Assesses Technical Correctness, Conceptual Depth, Missing Concepts, and Improvement Suggestions against the question's rubric and retrieved reference snippets.

### `report_service.py`
- Aggregates question scores and computes topic-wise and competency radar metrics.
- Synthesizes an executive assessment report.
- Exports a formal, styled PDF report via `fpdf2`.

