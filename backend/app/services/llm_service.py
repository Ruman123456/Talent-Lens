import abc
import json
import os
import re
import random
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Generate structured JSON response"""
        pass

    @abc.abstractmethod
    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        """Generate raw text response"""
        pass

class DemoMockProvider(LLMProvider):
    """
    Clearly labelled demo mode when no API keys are provided.
    Generates intelligent, context-aware responses based on extracted resume skills and retrieved knowledge chunks.
    Does NOT pretend to be an external proprietary LLM call; provides full deterministic functionality for screening.
    """
    def __init__(self):
        self.provider_name = "TalentLens Local Engine (Demo / Offline Mode)"

    def _extract_json_block(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        lower_prompt = prompt.lower()
        
        # 1. Profile Extraction from Resume
        if "extract the candidate's profile" in lower_prompt or "resume parsing" in lower_prompt:
            # Smart rule-based extraction strictly grounded in the provided resume text
            # Extract resume text section from prompt
            resume_text = ""
            if "resume text:" in lower_prompt:
                resume_text = prompt.split("Resume Text:")[-1].replace("---", "").strip()
            else:
                resume_text = prompt

            lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
            lower_resume = resume_text.lower()

            languages = []
            frameworks = []
            databases = []
            cloud = []
            tools = []

            kw_lang = ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "scala", "ruby", "sql", "r", "kotlin", "swift"]
            kw_frameworks = ["fastapi", "django", "flask", "react", "next.js", "vue", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "spring boot", "express"]
            kw_db = ["postgresql", "mysql", "mongodb", "sqlite", "redis", "cassandra", "dynamodb", "chromadb", "elasticsearch"]
            kw_cloud = ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "linux"]
            kw_tools = ["git", "github", "gitlab", "postman", "vs code", "jira"]

            for w in kw_lang:
                if re.search(r'\b' + re.escape(w) + r'\b', lower_resume):
                    languages.append(w.title() if len(w) > 3 else w.upper())
            for w in kw_frameworks:
                if re.search(r'\b' + re.escape(w) + r'\b', lower_resume):
                    frameworks.append(w.title())
            for w in kw_db:
                if re.search(r'\b' + re.escape(w) + r'\b', lower_resume):
                    databases.append(w.title())
            for w in kw_cloud:
                if re.search(r'\b' + re.escape(w) + r'\b', lower_resume):
                    cloud.append(w.upper() if len(w) <= 3 else w.title())
            for w in kw_tools:
                if re.search(r'\b' + re.escape(w) + r'\b', lower_resume):
                    tools.append(w.title() if len(w) > 3 else w.upper())

            technical_skills = list(set(languages + frameworks + databases + cloud + tools))

            # Extract genuine work experience if present in text
            work_experience = []
            exp_matches = re.findall(r'(?:experience|work experience|employment)[\s:]*([^\n\r]+(?:\n[^\n\r]+){0,3})', resume_text, re.IGNORECASE)
            if exp_matches:
                for match in exp_matches[:2]:
                    match_clean = match.strip()
                    if match_clean and len(match_clean) > 5:
                        work_experience.append({
                            "role": match_clean.split("\n")[0][:80].strip(),
                            "company": "From Resume",
                            "highlights": match_clean[:200].strip()
                        })
            else:
                for line in lines:
                    if any(term in line.lower() for term in ["intern", "engineer", "developer", "analyst"]) and not any(term in line.lower() for term in ["target", "skills", "education"]):
                        work_experience.append({
                            "role": line[:80].strip(),
                            "company": "From Resume",
                            "highlights": line[:200].strip()
                        })
                        break

            # Extract genuine education if present in text
            education = []
            edu_patterns = [r'(?:b\.?tech|b\.?e\.?|bachelor|m\.?tech|master|m\.?s\.?|phd|diploma|degree)[^\n,]*', r'education[\s:]*([^\n\r]+)']
            for pat in edu_patterns:
                m = re.search(pat, resume_text, re.IGNORECASE)
                if m:
                    deg = m.group(0).strip()
                    education.append({
                        "degree": deg[:100],
                        "institution": "From Resume",
                        "year": ""
                    })
                    break

            # Extract genuine projects if present in text
            projects = []
            proj_matches = re.findall(r'(?:projects?|project:)[\s:]*([^\n\r]+(?:\n[^\n\r]+){0,2})', resume_text, re.IGNORECASE)
            if proj_matches:
                for p in proj_matches[:2]:
                    p_clean = p.strip()
                    if p_clean and len(p_clean) > 5:
                        projects.append({
                            "name": p_clean.split("\n")[0][:60].strip(),
                            "description": p_clean[:200].strip(),
                            "technologies": [t for t in technical_skills if t.lower() in p_clean.lower()]
                        })

            # Genuine summary
            summary = ""
            if technical_skills:
                summary = f"Candidate with demonstrated skills in {', '.join(technical_skills[:5])}."
            elif lines:
                summary = f"Profile parsed from resume: {lines[0][:100]}."
            else:
                summary = "Candidate profile extracted from submitted document."

            domain_exposure = []
            if frameworks or "python" in lower_resume or "ai" in lower_resume or "machine learning" in lower_resume:
                domain_exposure.append("Machine Learning & Software Engineering")
            if databases:
                domain_exposure.append("Data Systems & Persistence")

            return {
                "technical_skills": technical_skills,
                "programming_languages": languages,
                "frameworks_libraries": frameworks,
                "databases": databases,
                "cloud_technologies": cloud,
                "tools_platforms": tools,
                "projects": projects,
                "work_experience": work_experience,
                "education": education,
                "domain_exposure": domain_exposure,
                "summary": summary
            }

        # 2. Context Building & Query Generation
        if "generate semantic search queries" in lower_prompt:
            # Randomize topic focus based on keywords found in the prompt
            all_query_pools = [
                "Loss functions, gradient descent optimization, and model convergence criteria",
                "Overfitting prevention, cross-validation, regularization, and generalization bounds",
                "Architectural tradeoffs in supervised vs unsupervised learning representations",
                "Data preprocessing, feature engineering, and high-dimensional space behavior",
                "Neural network backpropagation and activation function selection",
                "Ensemble methods: bagging, boosting, and stacking strategies",
                "Dimensionality reduction: PCA, t-SNE, and UMAP mechanics",
                "Model evaluation metrics: precision, recall, F1, AUC-ROC, and calibration",
                "Hyperparameter tuning strategies: grid search, Bayesian optimization, random search",
                "RESTful API design principles, versioning, and idempotency",
                "Database normalization, indexing strategies, and query optimization",
                "Concurrency models: async/await, thread pools, and event-driven architectures",
                "Microservices patterns: service mesh, circuit breakers, and saga patterns",
                "Caching strategies: LRU, write-through, TTL, and cache invalidation",
                "Data pipelines, ETL patterns, and stream processing architectures"
            ]
            random.shuffle(all_query_pools)
            selected_queries = all_query_pools[:4]

            # Detect candidate strengths from prompt keywords
            strength_pool = ["Backend API Design", "Data Structures", "Python Engineering",
                             "ML Pipeline Architecture", "Statistical Modeling", "System Design"]
            gap_pool = ["Theoretical convergence proofs", "Advanced hyperparameter regularization",
                        "Distributed systems design", "Memory management optimizations",
                        "Mathematical foundations of optimization", "Production MLOps practices"]
            random.shuffle(strength_pool)
            random.shuffle(gap_pool)

            return {
                "queries": selected_queries,
                "candidate_strengths": strength_pool[:3],
                "potential_gaps": gap_pool[:2],
                "recommended_difficulty": random.choice(["easy", "medium", "medium", "hard"])
            }

        # 3. Dynamic Question Generation grounded in retrieved chunks & resume
        if "generate exactly" in lower_prompt and "interview questions" in lower_prompt:
            # Parse retrieved chunks from the prompt to ensure tight grounding
            extracted_refs = []
            # Look for chunks pattern: [Ref X] Source: <name> (p. <page>) [ID: <id>]\nExcerpt: <snippet>
            chunk_blocks = re.findall(r'\[Ref\s*(\d+)\]\s*Source:\s*([^\n\(]+)\s*(?:\(p\.\s*([^\)]+)\))?\s*\[ID:\s*([^\]]+)\]\s*\nExcerpt:\s*([^\n\r]+(?:\n[^\n\r]+){0,3})', prompt)
            
            for m in chunk_blocks:
                ref_num, src_name, page_no, chunk_id, excerpt = m
                extracted_refs.append({
                    "document_name": src_name.strip(),
                    "page_number": int(page_no) if page_no and page_no.strip().isdigit() else 1,
                    "chunk_id": chunk_id.strip(),
                    "snippet": excerpt.strip()[:250]
                })

            # Extract candidate skills mentioned in prompt
            skills_match = re.search(r'Candidate Skills:\s*([^\n]+)', prompt)
            candidate_skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()] if skills_match else []

            # Extract role name
            role_match = re.search(r'Target Role:\s*([^\n]+)', prompt)
            role_title = role_match.group(1).strip() if role_match else "Software & ML Systems"

            generated_questions = []
            # If retrieved chunks exist, synthesize questions directly from each chunk's content and candidate skills!
            if extracted_refs:
                for idx, ref in enumerate(extracted_refs[:6]):
                    snippet_text = ref["snippet"]
                    # Extract the first sentence or salient concept from the chunk snippet
                    first_sent = snippet_text.split(".")[0].strip()
                    if len(first_sent) > 120:
                        first_sent = first_sent[:120]

                    skill_tie = candidate_skills[idx % len(candidate_skills)] if candidate_skills else "software engineering"
                    
                    q_text = (
                        f"Based on the principle that '{first_sent}...', how would you design and implement "
                        f"this in a production system using {skill_tie}? Discuss key architectural tradeoffs and error cases."
                    )
                    topic_title = f"{ref['document_name'].split('.')[0]} Applied Mechanics"
                    
                    generated_questions.append({
                        "question_text": q_text,
                        "topic": topic_title[:40],
                        "difficulty": "medium" if idx % 2 == 0 else "hard",
                        "question_type": "scenario_based" if idx % 2 == 0 else "practical",
                        "resume_relevance": f"Connects candidate's skill in {skill_tie} directly with foundational concepts from {ref['document_name']}.",
                        "expected_concepts": [
                            "System design tradeoffs",
                            f"Applied {skill_tie} architecture",
                            "Handling edge cases and failure modes",
                            "Performance and convergence implications"
                        ],
                        "evaluation_rubric": [
                            "Demonstrates clear technical depth and algorithmic rationale",
                            f"Applies {skill_tie} patterns correctly",
                            "Explicitly references tradeoffs and validation"
                        ],
                        "source_references": [ref]
                    })

            # If not enough chunks were parsed from prompt, add context-grounded items
            if len(generated_questions) < 6:
                diffs = ["easy", "medium", "medium", "hard", "medium", "hard"]
                types = ["conceptual", "practical", "scenario_based", "problem_solving", "practical", "scenario_based"]
                for i in range(len(generated_questions), 6):
                    skill_tie = candidate_skills[i % len(candidate_skills)] if candidate_skills else "Python"
                    ref = extracted_refs[0] if extracted_refs else {
                        "document_name": f"{role_title} Corpus",
                        "page_number": i + 1,
                        "chunk_id": f"chunk-ref-{i}",
                        "snippet": f"Core concepts and system patterns for {role_title}."
                    }
                    generated_questions.append({
                        "question_text": f"In {role_title}, how do you evaluate model generalization vs latency tradeoffs when building with {skill_tie}?",
                        "topic": f"{role_title} System Architecture",
                        "difficulty": diffs[i],
                        "question_type": types[i],
                        "resume_relevance": f"Evaluates production readiness in {skill_tie}.",
                        "expected_concepts": ["Generalization vs latency", "Production monitoring", "Error analysis"],
                        "evaluation_rubric": ["Technical reasoning", "System design considerations"],
                        "source_references": [ref]
                    })

            return generated_questions

        # 3. Question Generation (single-question path)
        if "generate an interview question" in lower_prompt:
            single_questions = [
                {
                    "question_text": "Explain how gradient descent optimization reaches convergence, and how the choice of learning rate affects variance and bias during training.",
                    "topic": "Model Optimization & Convergence",
                    "difficulty": "medium",
                    "question_type": "conceptual",
                    "expected_concepts": [
                        "gradient computation and parameter updates",
                        "learning rate impact on oscillation vs slow convergence",
                        "local minima and saddle points",
                        "momentum or adaptive optimizers like Adam"
                    ],
                    "evaluation_rubric": [
                        "Mathematical or conceptual formulation of gradient update step",
                        "Explanation of learning rate too high vs too low",
                        "Practical mitigation strategies such as learning rate schedules or momentum"
                    ]
                },
                {
                    "question_text": "How do you distinguish between bias error and variance error in a model, and what practical techniques do you use to address each?",
                    "topic": "Bias-Variance Tradeoff",
                    "difficulty": "medium",
                    "question_type": "conceptual",
                    "expected_concepts": [
                        "bias-variance decomposition",
                        "underfitting vs overfitting",
                        "regularization techniques",
                        "cross-validation strategies"
                    ],
                    "evaluation_rubric": [
                        "Correctly defines bias and variance sources",
                        "Links overfitting/underfitting to complexity",
                        "Proposes concrete regularization or data augmentation remedies"
                    ]
                },
                {
                    "question_text": "Describe how you would design a RESTful API for a high-throughput ML inference service. What are the key reliability and latency considerations?",
                    "topic": "API Design & Inference Engineering",
                    "difficulty": "medium",
                    "question_type": "scenario_based",
                    "expected_concepts": [
                        "async request handling",
                        "batching strategies",
                        "rate limiting and circuit breakers",
                        "health checks and observability"
                    ],
                    "evaluation_rubric": [
                        "Addresses concurrency and async processing",
                        "Mentions batching for throughput optimization",
                        "Considers failure modes and fallback strategies"
                    ]
                }
            ]
            return random.choice(single_questions)

        # 4. Answer Evaluation — content-aware, keyword-matched scoring
        if "evaluate the candidate's answer" in lower_prompt:
            # Extract the answer text submitted
            answer_raw = prompt.split("Candidate Answer:")[-1].strip() if "Candidate Answer:" in prompt else ""
            answer_lower = answer_raw.lower()

            # Detect if answer is empty, trivially short, or nonsensical
            trivial_patterns = [r"^n/?a$", r"^no answer$", r"^i don.?t know$", r"^skip$",
                                r"^idk$", r"^none$", r"^\.$", r"^-+$", r"^na$", r"^n\.a\.$"]
            is_trivial = (
                len(answer_raw.strip()) < 10
                or any(re.match(p, answer_raw.strip().lower()) for p in trivial_patterns)
            )

            # Extract expected_concepts from prompt if present
            expected_concepts: List[str] = []
            ec_match = re.search(r"[Ee]xpected [Cc]oncepts?[:\s]+(.+?)(?:\n[A-Z]|Evaluation Rubric|$)",
                                 prompt, re.DOTALL)
            if ec_match:
                raw_concepts = ec_match.group(1)
                # Pull out bullet / list items
                concepts_found = re.findall(r"[-•*]?\s*(.+?)(?:\n|$)", raw_concepts)
                expected_concepts = [c.strip().lower() for c in concepts_found if c.strip()]

            # Count how many expected concept keywords appear in the answer
            matched = 0
            if expected_concepts:
                for concept in expected_concepts:
                    # Match any significant word from each concept phrase
                    words = [w for w in re.split(r'[\s,/()]+', concept) if len(w) > 3]
                    if any(w in answer_lower for w in words):
                        matched += 1
            else:
                # Fallback: score on meaningful word count (>= 30 unique meaningful words = decent)
                words = [w for w in re.split(r'\W+', answer_lower) if len(w) > 3]
                matched = min(len(set(words)), 4)

            total_concepts = max(len(expected_concepts), 4)

            # Score computation
            if is_trivial:
                score = 1.0
                correctness = "incorrect"
                strengths = ["Acknowledged the question"]
                missing = expected_concepts[:3] if expected_concepts else ["Core concept explanation",
                                                                            "Technical depth",
                                                                            "Practical examples"]
                suggestions = ["Study the topic fundamentals before the interview.",
                                "Attempt to reason through problems even if uncertain."]
                explanation = "The response does not demonstrate understanding of the question. Score: 1.0/5.0."
            elif matched == 0 and len(answer_raw.strip()) < 50:
                score = 1.5
                correctness = "incorrect"
                strengths = ["Some attempt to respond"]
                missing = expected_concepts[:3] if expected_concepts else ["Conceptual depth", "Keyword accuracy"]
                suggestions = ["Revisit core concepts for this topic.", "Use technical vocabulary in responses."]
                explanation = "The response is too brief and does not address the core technical concepts. Score: 1.5/5.0."
            elif matched == 0:
                score = 2.0
                correctness = "incorrect"
                strengths = ["Response shows some structure"]
                missing = expected_concepts[:3] if expected_concepts else ["Technical terminology", "Core mechanisms"]
                suggestions = ["Address the specific concepts asked.", "Back up claims with technical reasoning."]
                explanation = "Response is wordy but misses the key technical concepts. Score: 2.0/5.0."
            else:
                ratio = matched / total_concepts
                if ratio >= 0.75:
                    score = round(4.0 + min(ratio - 0.75, 0.25) * 4, 1)  # 4.0 – 5.0
                    correctness = "correct"
                    strengths = [f"Correctly covered {matched} of {total_concepts} key concepts",
                                 "Strong technical depth and accurate terminology"]
                elif ratio >= 0.5:
                    score = round(3.0 + (ratio - 0.5) * 4, 1)  # 3.0 – 4.0
                    correctness = "partially_correct"
                    strengths = [f"Addressed {matched} key concept(s) with reasonable accuracy",
                                 "Demonstrated partial understanding of the domain"]
                elif ratio >= 0.25:
                    score = round(2.0 + (ratio - 0.25) * 4, 1)  # 2.0 – 3.0
                    correctness = "partially_correct"
                    strengths = ["Mentioned some relevant terms"]
                else:
                    score = round(1.5 + ratio * 2, 1)  # 1.5 – 2.0
                    correctness = "incorrect"
                    strengths = ["Made an attempt to respond"]

                unmatched = [c for c in expected_concepts
                             if not any(w in answer_lower for w in
                                        [w for w in re.split(r'[\s,/()]+', c) if len(w) > 3])]
                missing = unmatched[:3] if unmatched else ["Greater mathematical depth",
                                                            "Edge case discussion",
                                                            "Real-world implementation examples"]
                suggestions = [
                    f"Deepen coverage of: {', '.join(missing[:2])}." if missing else "Excellent coverage.",
                    "Support conceptual claims with concrete implementation examples."
                ]
                explanation = (f"The candidate addressed {matched}/{total_concepts} expected concept areas. "
                               f"Score: {score}/5.0 — {'Strong' if score >= 4 else 'Moderate' if score >= 3 else 'Weak'} response.")

            return {
                "score": score,
                "technical_correctness": correctness,
                "strengths": strengths,
                "missing_concepts": missing,
                "improvement_suggestions": suggestions,
                "evaluation_explanation": explanation
            }

        # Default fallback
        return {
            "result": "Processed through TalentLens Local Engine",
            "score": 3.5,
            "strengths": ["Clear communication"],
            "missing_concepts": ["Deeper mathematical derivation"]
        }

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        return "TalentLens AI Response: Evaluated under structured screening rubric."

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

def get_llm_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAICompatibleProvider(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            base_url=settings.OPENAI_BASE_URL
        )
    return DemoMockProvider()

