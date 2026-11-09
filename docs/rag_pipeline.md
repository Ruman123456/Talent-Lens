# Genuine Retrieval-Augmented Generation (RAG) Pipeline

TalentLens AI implements a genuine semantic RAG pipeline designed around technical literature citations, avoiding generic web lookups or ungrounded generative hallucinations.

## 1. Document Ingestion Pipeline

```
[ Raw PDF / TXT Literature ]
            │
            ▼  (PyMuPDF / Page & Section Extraction)
[ Page-Aware Text Elements (Text + Page Number) ]
            │
            ▼  (Boundary-Preserving Windowing)
[ Chunks (800-1000 tokens / 120-150 token overlap) ]
            │
            ▼  (all-MiniLM-L6-v2 Embeddings)
[ 384-dimensional Dense Vector Representations ]
            │
            ▼  (Idempotent Insertion with SHA-256 Hashes)
[ ChromaDB Persistent Collections (role_{role_id}) ]
```

### Idempotency & Chunk Metadata
Each chunk stores comprehensive tracing metadata:
```json
{
  "role_id": "ai_ml_engineer",
  "source_name": "Burkov The Hundred Page Machine Learning Book",
  "filename": "Burkov_The_Hundred_Page_Machine_Learning_Book.pdf",
  "page_number": 24,
  "page_range": "24-25",
  "content_hash": "a4f89d...",
  "chunk_id": "ai_ml_engineer_a4f89d_12"
}
```

## 2. Dynamic Query Construction Flow
Rather than querying the vector database with the full raw resume, the `ContextBuilder` synthesizes resume traits and role competencies into independent, high-signal queries:
1. **Foundational Query**: Core mathematical or architectural basis for the role.
2. **Intersection Query**: Technologies explicitly claimed on candidate resume tested against textbook theory.
3. **Applied Scenario Query**: High-concurrency or failure-mode tradeoffs in candidate project spaces.
4. **Competency Gap Query**: Deep concepts required for the role that are absent from the resume.

## 3. Retrieval & Deduplication
1. Multi-query search retrieves Top-K (`k=4`) candidates per query.
2. Similarity threshold (`threshold=0.35`) prunes noise.
3. Chunks are deduplicated by `chunk_id` while aggregating matched query traces.
4. Top grounded passages are passed to the `QuestionGenerator` alongside page and document citations.

## 4. Question & Source Traceability
Every generated question contains explicit citation objects linking each question to the exact textbook page and excerpt from which its concept was derived.

