# TalentLens AI — AI-Powered Role-Based Candidate Screening System

TalentLens AI is an intelligent, resume-aware, role-based technical interview and candidate screening platform built using a genuine Retrieval-Augmented Generation (RAG) architecture.

The system dynamically conducts personalized technical interviews based on three inputs:
1. **Candidate Resume** (`.pdf` or `.txt`).
2. **Selected Engineering Role** (`AI/ML Engineer`, `Data Science / Applied ML`, `Backend Engineer`).
3. **Role-Specific Knowledge Base** containing textbooks and technical corpora indexed into ChromaDB.

---

## 1. System Architecture & Flow

```
Resume Upload ──► Resume Parsing ──► Role Selection ──► Context Construction
                                                               │
                                                               ▼
Question Generation ◄── Role-Filtered Search ◄── Semantic Query Generation
        │                     (ChromaDB)
        ▼
Interactive Interview ──► Answer Persistence ──► Multi-Criteria Evaluation ──► PDF Screening Report
```

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy, PyMuPDF, FPDF2.
- **Vector Database**: ChromaDB (persistent on disk with logical collections per role).
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`, 384 dimensions).
- **LLM Abstraction**: Configurable provider abstraction supporting Google Gemini (`gemini-1.5-flash`), OpenAI-compatible endpoints (`gpt-4o-mini`), and an offline Demo/Mock Mode.

---

## 2. Directory Structure

```
PGAGI/
├── backend/
│   ├── app/
│   │   ├── api/             # REST endpoints (health, roles, resumes, knowledge, interviews, reports)
│   │   ├── core/            # Config & environment settings
│   │   ├── db/              # SQLAlchemy session and initial seed data
│   │   ├── models/          # Relational ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── resume_service.py      # PDF/TXT parsing & profile extraction
│   │   │   ├── ingestion_service.py   # Chunking, overlap & ChromaDB indexing
│   │   │   ├── embedding_service.py   # SentenceTransformers embedding engine
│   │   │   ├── vector_store.py        # ChromaDB persistent collection manager
│   │   │   ├── context_builder.py     # Resume-aware semantic query constructor
│   │   │   ├── retrieval_service.py   # Multi-query deduplicated RAG retrieval
│   │   │   ├── question_generator.py  # Grounded dynamic question generator
│   │   │   ├── evaluation_service.py  # Multi-criteria answer scoring
│   │   │   ├── report_service.py      # Assessment synthesis & PDF report export
│   │   │   └── interview_service.py   # Session lifecycle manager
│   │   └── main.py          # FastAPI application entrypoint
│   ├── knowledge_base/      # Role corpora directories
│   ├── scripts/
│   │   └── ingest_corpus.py # CLI utility to ingest textbooks
│   └── tests/
│       └── test_e2e_pipeline.py # End-to-end unit & integration test suite
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, layout components
│   │   ├── pages/           # Landing, Setup, Interview Workspace, Results, Knowledge Base
│   │   ├── services/        # Axios API client
│   │   ├── types/           # TypeScript interfaces
│   │   └── App.tsx          # Router setup
│   └── package.json
├── docs/
│   ├── architecture.md      # Detailed system architecture
│   ├── rag_pipeline.md      # In-depth RAG design documentation
│   └── demo_script.md       # Step-by-step video demonstration guide
├── .env.example             # Environment variable template
└── README.md
```

---

## 3. Quick Start & Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Backend Setup
```bash
# In the root repository directory:
pip install -r requirements.txt
# (or: pip install fastapi uvicorn sqlalchemy chromadb sentence-transformers pymupdf fpdf2 pydantic-settings httpx pytest)

# Copy environment file
cp .env.example .env
```

To configure Google Gemini or OpenAI (optional):
```env
LLM_PROVIDER="gemini"
GEMINI_API_KEY="your-gemini-api-key"
# or
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-openai-api-key"
```
*(By default, `LLM_PROVIDER="demo"` runs in offline mode without requiring external API keys).*

### Step 2: Ingest Knowledge Base Corpora
The repository includes the CLI ingestion tool. To index role corpora into ChromaDB:

```bash
# Ingest AI/ML textbook (e.g. Burkov's The Hundred-Page Machine Learning Book)
python backend/scripts/ingest_corpus.py --role ai_ml_engineer

# Ingest Data Science corpus
python backend/scripts/ingest_corpus.py --role data_science

# Ingest Backend Engineering systems handbook
python backend/scripts/ingest_corpus.py --role backend_engineer
```

### Step 3: Run the Backend Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- API Swagger Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

### Step 4: Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 4. Running Backend Tests
Execute the comprehensive end-to-end integration and unit test suite:

```bash
python backend/tests/test_e2e_pipeline.py
# or
pytest backend/tests/test_e2e_pipeline.py -v
```

Verified test coverage includes:
1. System health check.
2. Configured roles listing.
3. Knowledge base readiness and chunk statistics.
4. Document boundary-preserving chunking with page retention.
5. Resume upload and structured skill profile extraction.
6. Full interview lifecycle: session creation, question generation with source citations, answer evaluation, session completion, and final report synthesis.

---

## 5. Key Design Decisions & Tradeoffs

1. **Sentence Transformers (`all-MiniLM-L6-v2`) over Proprietary API Embeddings**:
   - Ensures zero external embedding network latency and removes runtime API cost during ingestion.
   - Embeddings for both chunk storage and query retrieval run deterministically under the same vector space.

2. **Multi-Query Decomposition instead of Raw Resume Concatenation**:
   - Passing a full raw resume into a vector similarity search produces noisy, unfocused semantic vectors.
   - The `ContextBuilder` decomposes candidate skills into targeted conceptual queries (foundations, tools, architecture tradeoffs, and competency gaps), ensuring diverse, high-relevance chunk retrieval.

3. **Grounding & Traceability**:
   - Every question carries a `source_references` array detailing the document name, page number, chunk ID, and source snippet.
   - Candidates and interviewers can inspect the exact literature citations supporting each question.

4. **Session Persistence**:
   - Every question, answer, and evaluation record is persisted in the database with timestamps and foreign keys, allowing candidates to refresh the page or resume in-progress interviews seamlessly.

---

