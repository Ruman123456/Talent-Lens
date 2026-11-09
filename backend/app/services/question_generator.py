from typing import List, Dict, Any, Optional
import random
from app.services.llm_service import get_llm_provider

class QuestionGenerator:
    @staticmethod
    def generate_interview_questions(
        candidate_name: str,
        role_name: str,
        extracted_profile: Dict[str, Any],
        context_data: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        num_questions: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Dynamically generates structured technical interview questions grounded in retrieved textbook passages.
        Every question is tied directly to source citations, difficulty, and rubric.
        """
        provider = get_llm_provider()

        # Format retrieved chunks for the prompt with source metadata
        chunks_formatted = []
        for i, c in enumerate(retrieved_chunks[:8]):
            meta = c.get("metadata", {})
            src = meta.get("source_name", meta.get("filename", "Textbook Reference"))
            page = meta.get("page_number", "N/A")
            cid = c.get("chunk_id", f"chunk_{i}")
            snippet = c.get("text", "")[:700].replace("\n", " ")
            chunks_formatted.append(f"[Ref {i+1}] Source: {src} (p. {page}) [ID: {cid}]\nExcerpt: {snippet}")

        context_text = "\n\n".join(chunks_formatted) if chunks_formatted else "No specific textbook excerpts available."

        prompt = f"""
You are the Lead Technical Interviewer at TalentLens AI conducting a structured screening session.
Candidate Name: {candidate_name}
Target Role: {role_name}

Candidate Skills: {', '.join(extracted_profile.get('technical_skills', [])[:8])}
Candidate Projects: {[p.get('name') for p in extracted_profile.get('projects', [])[:2]]}
Recommended Difficulty: {context_data.get('recommended_difficulty', 'medium')}

Retrieved Textbook & Technical Knowledge Passages:
---
{context_text}
---

Generate exactly {num_questions} structured, personalized interview questions.
Requirements:
1. Ground each question in the retrieved concepts above and connect it meaningfully to the candidate's skills/projects.
2. Ensure progressive difficulty across questions: start foundational, advance through practical, system design, and edge cases.
3. Diverse question types: conceptual, practical, scenario_based, problem_solving.
4. DO NOT generate generic trivia. Focus on deep engineering understanding, tradeoffs, and failure modes.
5. Provide a rigorous scoring rubric and key expected concepts for each question.
6. Reference the exact source reference (Source Name, Page, Chunk ID) from the retrieved excerpts above for each question.

Strictly output a JSON array of question objects matching this schema:
[
  {{
    "question_text": "...",
    "topic": "...",
    "difficulty": "easy | medium | hard",
    "question_type": "conceptual | practical | scenario_based | problem_solving",
    "resume_relevance": "How this connects to candidate's resume/skills",
    "expected_concepts": ["concept 1", "concept 2", "concept 3"],
    "evaluation_rubric": ["Criterion 1", "Criterion 2"],
    "source_references": [
      {{
        "document_name": "...",
        "page_number": 12,
        "chunk_id": "...",
        "snippet": "..."
      }}
    ]
  }}
]
"""
        system_instruction = "You are a senior technical screener. Output only a valid JSON array of questions."
        
        # In demo mode, or when LLM returns, format safely
        raw_output = provider.generate_json(prompt, system_instruction=system_instruction)

        # Normalization if wrapper dict returned
        questions_list = []
        if isinstance(raw_output, list):
            questions_list = raw_output
        elif isinstance(raw_output, dict):
            for k in ["questions", "items", "data"]:
                if k in raw_output and isinstance(raw_output[k], list):
                    questions_list = raw_output[k]
                    break
            if not questions_list and "question_text" in raw_output:
                questions_list = [raw_output]

        # If fallback is needed (e.g. empty or few questions generated)
        if not questions_list:
            questions_list = QuestionGenerator._get_fallback_grounded_questions(
                role_name, extracted_profile, retrieved_chunks, num_questions
            )

        # Enforce question index and references
        formatted = []
        for idx, q in enumerate(questions_list[:num_questions]):
            # Ensure source references exist
            refs = q.get("source_references", [])
            if not refs and retrieved_chunks:
                top_chunk = retrieved_chunks[min(idx, len(retrieved_chunks)-1)]
                meta = top_chunk.get("metadata", {})
                refs = [{
                    "document_name": meta.get("source_name", "Textbook Reference"),
                    "page_number": meta.get("page_number", 1),
                    "chunk_id": top_chunk.get("chunk_id", "ref-chunk"),
                    "snippet": top_chunk.get("text", "")[:200]
                }]

            formatted.append({
                "question_index": idx + 1,
                "question_text": q.get("question_text", f"Explain core engineering principles in {role_name}."),
                "topic": q.get("topic", "Foundational Principles"),
                "difficulty": q.get("difficulty", "medium"),
                "question_type": q.get("question_type", "conceptual"),
                "resume_relevance": q.get("resume_relevance", "Evaluates fundamental competency for the role."),
                "expected_concepts": q.get("expected_concepts", ["Core algorithm intuition", "Tradeoffs", "Implementation constraints"]),
                "evaluation_rubric": q.get("evaluation_rubric", ["Technical clarity", "Depth of response"]),
                "source_references": refs,
                "generation_metadata": {"grounded": True, "num_sources": len(refs)}
            })

        return formatted

    @staticmethod
    def _get_fallback_grounded_questions(
        role_name: str,
        extracted_profile: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Large, diverse question pool — randomly sampled each time so every session
        gets a different set and ordering.  Pool contains 18 questions across
        ML/AI, Data Science, Backend, and cross-domain topics.
        """
        primary_lang = (extracted_profile.get("programming_languages") or ["Python"])[0]
        frameworks = extracted_profile.get("frameworks_libraries") or ["PyTorch"]
        primary_fw = frameworks[0] if frameworks else "PyTorch"

        # Build chunk refs from the RETRIEVED chunks so references vary per session
        def _refs_for(idx: int) -> List[Dict]:
            if not retrieved_chunks:
                return []
            chunk = retrieved_chunks[min(idx, len(retrieved_chunks) - 1)]
            meta = chunk.get("metadata", {})
            return [{
                "document_name": meta.get("source_name", "Curated Role Corpus"),
                "page_number": meta.get("page_number", idx + 1),
                "chunk_id": chunk.get("chunk_id", f"c{idx}"),
                "snippet": chunk.get("text", "")[:250]
            }]

        all_templates = [
            # --- OPTIMIZATION & TRAINING ---
            {
                "question_text": (
                    f"Explain the optimization dynamics of Gradient Descent vs Stochastic Gradient Descent. "
                    f"Under what loss surface conditions can momentum or adaptive learning rate algorithms "
                    f"(e.g., Adam) overcome plateaus and saddle points?"
                ),
                "topic": "Optimization & Gradient Dynamics",
                "difficulty": "medium",
                "question_type": "practical",
                "expected_concepts": [
                    "gradient calculation over batches",
                    "saddle points vs local minima",
                    "first and second order moments in Adam",
                    "learning rate scheduling"
                ],
                "evaluation_rubric": [
                    "Differentiates batch vs stochastic updates",
                    "Explains momentum physics analog",
                    "Discusses Adam hyperparameter tuning"
                ],
                "source_references": _refs_for(0)
            },
            # --- BIAS-VARIANCE ---
            {
                "question_text": (
                    f"In machine learning systems, how do you mathematically distinguish between inductive bias "
                    f"and variance? Given your experience with {primary_lang}, how do you evaluate model "
                    f"generalization beyond the training distribution?"
                ),
                "topic": "Generalization & Inductive Bias",
                "difficulty": "medium",
                "question_type": "conceptual",
                "expected_concepts": [
                    "bias-variance decomposition",
                    "overfitting prevention",
                    "k-fold cross validation",
                    "regularization penalties"
                ],
                "evaluation_rubric": [
                    "Explicitly defines bias vs variance",
                    "Relates inductive bias to model hypothesis space",
                    "Proposes practical cross-validation strategy"
                ],
                "source_references": _refs_for(1)
            },
            # --- ENSEMBLE METHODS ---
            {
                "question_text": (
                    "Describe the mathematical objective of Decision Tree splitting (e.g. Information Gain, "
                    "Entropy, or Gini Impurity). How do ensemble methods like Random Forests and Gradient "
                    "Boosted Trees reduce variance and bias respectively?"
                ),
                "topic": "Tree-based Models & Ensembling",
                "difficulty": "hard",
                "question_type": "conceptual",
                "expected_concepts": [
                    "entropy and Shannon information gain",
                    "bootstrap aggregation bagging",
                    "sequential residual boosting",
                    "hyperplane splitting"
                ],
                "evaluation_rubric": [
                    "Formulates entropy or Gini equation",
                    "Explains why bagging reduces variance while boosting reduces bias",
                    "Discusses tree depth pruning"
                ],
                "source_references": _refs_for(2)
            },
            # --- PRODUCTION ML DRIFT ---
            {
                "question_text": (
                    "In production ML workflows, how do you detect and mitigate Data Drift (Covariate Shift) "
                    "and Concept Drift? What statistical tests (e.g. KS-test, Population Stability Index) "
                    "would you automate into a monitoring pipeline?"
                ),
                "topic": "Production ML & Drift Detection",
                "difficulty": "hard",
                "question_type": "scenario_based",
                "expected_concepts": [
                    "covariate shift vs concept drift",
                    "Kolmogorov-Smirnov test",
                    "PSI thresholds",
                    "continuous retraining pipelines"
                ],
                "evaluation_rubric": [
                    "Identifies difference between feature and target distribution shifts",
                    "Selects suitable statistical divergence metrics",
                    "Outlines automated alert/fallback architecture"
                ],
                "source_references": _refs_for(3)
            },
            # --- INFERENCE ENGINEERING ---
            {
                "question_text": (
                    f"When building high-throughput inference endpoints using {primary_lang}, how do you "
                    f"manage memory allocation, GPU/CPU batching, and async request concurrency to meet "
                    f"sub-100 ms latency SLAs?"
                ),
                "topic": "Inference Engineering & Latency",
                "difficulty": "medium",
                "question_type": "problem_solving",
                "expected_concepts": [
                    "dynamic batching",
                    "async concurrency models",
                    "worker pooling",
                    "quantization FP16 INT8"
                ],
                "evaluation_rubric": [
                    "Details async vs worker process models",
                    "Addresses batching latency vs throughput tradeoff",
                    "Mentions model quantization benefits"
                ],
                "source_references": _refs_for(4)
            },
            # --- DIMENSIONALITY REDUCTION ---
            {
                "question_text": (
                    "Explain the curse of dimensionality in high-dimensional feature spaces. How do techniques "
                    "like PCA or t-SNE mathematically transform the covariance matrix to preserve variance, "
                    "and when would you choose one over the other?"
                ),
                "topic": "Dimensionality Reduction",
                "difficulty": "medium",
                "question_type": "conceptual",
                "expected_concepts": [
                    "geometric distance distortion in high dimensions",
                    "eigenvalue decomposition of covariance matrix",
                    "orthogonal projection",
                    "explained variance ratio"
                ],
                "evaluation_rubric": [
                    "Explains distance sparsity in high dimensions",
                    "Outlines PCA eigenvector steps",
                    "Contrasts linear PCA with non-linear t-SNE"
                ],
                "source_references": _refs_for(5)
            },
            # --- NEURAL NETWORK ARCHITECTURE ---
            {
                "question_text": (
                    f"Given your experience with {primary_fw}, walk through the forward and backward pass "
                    f"of a deep neural network. How do vanishing and exploding gradients manifest, and what "
                    f"architectural choices (BatchNorm, residual connections, weight initialization) address them?"
                ),
                "topic": "Deep Learning Fundamentals",
                "difficulty": "hard",
                "question_type": "practical",
                "expected_concepts": [
                    "forward pass activation chain",
                    "backpropagation chain rule",
                    "vanishing gradient problem",
                    "batch normalization and residual connections"
                ],
                "evaluation_rubric": [
                    "Correctly traces gradient flow through layers",
                    "Identifies specific layers prone to gradient issues",
                    "Proposes concrete architectural remedies"
                ],
                "source_references": _refs_for(6)
            },
            # --- LOSS FUNCTIONS ---
            {
                "question_text": (
                    "Compare cross-entropy loss vs mean-squared error for classification tasks. When is "
                    "focal loss preferable, and how does label smoothing affect model calibration in "
                    "multi-class problems?"
                ),
                "topic": "Loss Functions & Model Calibration",
                "difficulty": "medium",
                "question_type": "conceptual",
                "expected_concepts": [
                    "cross-entropy log-likelihood interpretation",
                    "MSE vs CE gradient properties",
                    "focal loss class imbalance handling",
                    "label smoothing calibration effect"
                ],
                "evaluation_rubric": [
                    "Correctly derives why CE is preferred over MSE for classification",
                    "Explains focal loss down-weighting mechanism",
                    "Discusses confidence calibration impact of label smoothing"
                ],
                "source_references": _refs_for(7)
            },
            # --- ATTENTION & TRANSFORMERS ---
            {
                "question_text": (
                    "Describe the scaled dot-product attention mechanism in Transformers. Why is the "
                    "scaling factor √d_k necessary, and how does multi-head attention enable the model to "
                    "capture diverse semantic relationships simultaneously?"
                ),
                "topic": "Attention Mechanisms & Transformers",
                "difficulty": "hard",
                "question_type": "conceptual",
                "expected_concepts": [
                    "query key value attention computation",
                    "scaling factor preventing softmax saturation",
                    "multi-head parallel attention",
                    "positional encoding"
                ],
                "evaluation_rubric": [
                    "Correctly formulates attention(Q,K,V) = softmax(QK^T/√d_k)V",
                    "Explains why scaling prevents gradient vanishing in softmax",
                    "Articulates role of multiple attention heads"
                ],
                "source_references": _refs_for(8)
            },
            # --- API DESIGN ---
            {
                "question_text": (
                    f"Design a RESTful API for a real-time candidate scoring service. Walk through "
                    f"your choices for idempotency, versioning strategy, authentication, and how you'd "
                    f"handle partial failures in a distributed deployment using {primary_lang}."
                ),
                "topic": "RESTful API Design",
                "difficulty": "medium",
                "question_type": "scenario_based",
                "expected_concepts": [
                    "idempotency via HTTP verbs",
                    "API versioning strategies",
                    "JWT or OAuth2 authentication",
                    "circuit breaker and retry policies"
                ],
                "evaluation_rubric": [
                    "Correctly applies HTTP verb semantics",
                    "Explains versioning via URL path or Accept header",
                    "Addresses partial failure resilience patterns"
                ],
                "source_references": _refs_for(9)
            },
            # --- DATABASE DESIGN ---
            {
                "question_text": (
                    "Compare SQL and NoSQL storage strategies for storing candidate interview sessions "
                    "and evaluation results. When would you use a document store vs a relational schema, "
                    "and how would you design indexes for read-heavy reporting queries?"
                ),
                "topic": "Database Design & Query Optimization",
                "difficulty": "medium",
                "question_type": "practical",
                "expected_concepts": [
                    "normalization vs denormalization tradeoffs",
                    "B-tree and composite index design",
                    "ACID vs BASE consistency",
                    "query plan analysis"
                ],
                "evaluation_rubric": [
                    "Identifies when relational vs document model is appropriate",
                    "Designs indexes relevant to access patterns",
                    "Discusses CAP theorem implications"
                ],
                "source_references": _refs_for(10)
            },
            # --- CONCURRENCY ---
            {
                "question_text": (
                    f"Explain the difference between threading, multiprocessing, and async I/O in "
                    f"{primary_lang}. For a CPU-bound ML preprocessing pipeline vs an I/O-bound API "
                    f"gateway, which concurrency model would you choose and why?"
                ),
                "topic": "Concurrency & Parallelism",
                "difficulty": "medium",
                "question_type": "problem_solving",
                "expected_concepts": [
                    "GIL and thread limitations",
                    "multiprocessing for CPU bound tasks",
                    "async await event loop for I/O",
                    "worker pool sizing"
                ],
                "evaluation_rubric": [
                    "Correctly identifies GIL impact on threading",
                    "Selects appropriate model per workload type",
                    "Estimates appropriate worker/process counts"
                ],
                "source_references": _refs_for(11)
            },
            # --- CACHING ---
            {
                "question_text": (
                    "Design a caching strategy for a knowledge-retrieval system that serves vector "
                    "similarity search results. How would you handle cache invalidation when the "
                    "underlying knowledge base is updated, and what eviction policy fits this workload?"
                ),
                "topic": "Caching & Cache Invalidation",
                "difficulty": "hard",
                "question_type": "scenario_based",
                "expected_concepts": [
                    "LRU vs LFU eviction",
                    "TTL-based vs event-driven invalidation",
                    "write-through vs write-back cache",
                    "consistent hashing for distributed caches"
                ],
                "evaluation_rubric": [
                    "Proposes a coherent invalidation strategy",
                    "Justifies eviction policy for the access pattern",
                    "Considers distributed cache coherency"
                ],
                "source_references": _refs_for(12)
            },
            # --- RAG ARCHITECTURE ---
            {
                "question_text": (
                    "Explain the Retrieval-Augmented Generation (RAG) pipeline end-to-end: document "
                    "chunking, embedding, vector similarity retrieval, and prompt grounding. What are "
                    "the key failure modes and how would you evaluate retrieval quality?"
                ),
                "topic": "RAG Architecture & Evaluation",
                "difficulty": "hard",
                "question_type": "practical",
                "expected_concepts": [
                    "text chunking with overlap",
                    "dense embedding similarity search",
                    "prompt context window grounding",
                    "faithfulness and relevance metrics"
                ],
                "evaluation_rubric": [
                    "Traces full document-to-answer pipeline",
                    "Identifies hallucination as a retrieval failure mode",
                    "Proposes recall@k or NDCG evaluation"
                ],
                "source_references": _refs_for(13)
            },
            # --- SYSTEM DESIGN ---
            {
                "question_text": (
                    "Design a horizontally scalable ML feature store for real-time serving. How would "
                    "you ensure consistency between offline training features and online serving features, "
                    "and what SLAs would you define for feature freshness?"
                ),
                "topic": "Feature Store & MLOps System Design",
                "difficulty": "hard",
                "question_type": "scenario_based",
                "expected_concepts": [
                    "online vs offline feature store split",
                    "feature consistency and point-in-time correctness",
                    "feature freshness SLA definitions",
                    "serving latency vs batch processing tradeoffs"
                ],
                "evaluation_rubric": [
                    "Proposes online/offline separation architecture",
                    "Addresses training-serving skew problem",
                    "Defines concrete SLA metrics"
                ],
                "source_references": _refs_for(14)
            },
            # --- STATISTICAL TESTING ---
            {
                "question_text": (
                    "Walk through designing an A/B test to evaluate two ML model versions in production. "
                    "How do you calculate the required sample size, choose the significance threshold, "
                    "and avoid common pitfalls like peeking and multiple comparisons?"
                ),
                "topic": "A/B Testing & Statistical Significance",
                "difficulty": "medium",
                "question_type": "problem_solving",
                "expected_concepts": [
                    "null and alternative hypothesis formulation",
                    "power analysis and sample size",
                    "p-value and significance threshold",
                    "Bonferroni correction for multiple tests"
                ],
                "evaluation_rubric": [
                    "Correctly formulates hypotheses",
                    "Applies power analysis formula",
                    "Addresses sequential testing pitfalls"
                ],
                "source_references": _refs_for(15)
            },
            # --- MICROSERVICES ---
            {
                "question_text": (
                    "Compare monolithic vs microservices architecture for an AI screening platform. "
                    "What service decomposition strategy would you apply, and how would you manage "
                    "inter-service communication, service discovery, and distributed tracing?"
                ),
                "topic": "Microservices & Distributed Architecture",
                "difficulty": "hard",
                "question_type": "scenario_based",
                "expected_concepts": [
                    "domain-driven decomposition",
                    "synchronous REST vs async message queues",
                    "service registry and discovery",
                    "distributed tracing with correlation IDs"
                ],
                "evaluation_rubric": [
                    "Proposes a coherent service boundary strategy",
                    "Weighs synchronous vs async communication",
                    "Addresses observability in distributed systems"
                ],
                "source_references": _refs_for(16)
            },
            # --- EVALUATION METRICS ---
            {
                "question_text": (
                    "For an imbalanced binary classification problem (e.g., fraud detection where only "
                    "0.1% of samples are positive), why are accuracy and F1-score misleading? Walk through "
                    "precision-recall curves, AUC-PR vs AUC-ROC, and threshold selection strategies."
                ),
                "topic": "Evaluation Metrics for Imbalanced Data",
                "difficulty": "medium",
                "question_type": "conceptual",
                "expected_concepts": [
                    "accuracy paradox with class imbalance",
                    "precision recall tradeoff",
                    "AUC-PR vs AUC-ROC under imbalance",
                    "threshold optimization for business metrics"
                ],
                "evaluation_rubric": [
                    "Correctly identifies why accuracy fails",
                    "Explains the precision-recall tradeoff",
                    "Recommends AUC-PR over AUC-ROC for imbalance scenarios"
                ],
                "source_references": _refs_for(17)
            },
        ]

        # Shuffle the full pool, then sample num_questions
        random.shuffle(all_templates)
        return all_templates[:num_questions]

question_generator = QuestionGenerator()

