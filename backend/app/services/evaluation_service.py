from typing import Dict, Any, List
from app.services.llm_service import get_llm_provider

class EvaluationService:
    @staticmethod
    def evaluate_candidate_answer(
        question_text: str,
        topic: str,
        difficulty: str,
        expected_concepts: List[str],
        evaluation_rubric: List[str],
        source_references: List[Dict[str, Any]],
        answer_text: str
    ) -> Dict[str, Any]:
        """
        Evaluates candidate answer against expected concepts, evaluation rubric,
        and retrieved source citations using structured multi-criteria scoring.
        """
        provider = get_llm_provider()

        ref_snippets = "\n".join([
            f"- {r.get('document_name', 'Doc')} (p. {r.get('page_number', 'N/A')}): {r.get('snippet', '')}"
            for r in source_references
        ])

        prompt = f"""
You are a Lead AI Technical Interviewer evaluating a candidate's response.

Question: {question_text}
Topic: {topic}
Difficulty: {difficulty}

Target Concepts Expected:
{', '.join(expected_concepts)}

Scoring Rubric:
{', '.join(evaluation_rubric)}

Retrieved Reference Material:
{ref_snippets}

Candidate's Submitted Answer:
\"\"\"{answer_text}\"\"\"

Evaluation Criteria:
1. Technical Correctness (Are principles and formulations mathematically/conceptually sound?)
2. Conceptual Depth (Does candidate explain WHY mechanisms work or just state buzzwords?)
3. Missing Concepts (Identify specific critical concepts from the rubric that were omitted)
4. Score between 1.0 (Completely incorrect / irrelevant) to 5.0 (Flawless, comprehensive, deep answer)
5. Assign correctness category: 'correct', 'partially_correct', 'incorrect', 'vague'

Strictly return a JSON object:
{{
  "score": 4.5,
  "correctness": "correct",
  "strengths": ["...", "..."],
  "missing_concepts": ["..."],
  "improvement_suggestions": ["..."],
  "evaluation_explanation": "Thorough justification of the score grounded in the rubric and reference text."
}}
"""
        system_instruction = "You are an objective technical interviewer. Score accurately based on technical correctness and depth. Output valid JSON only."
        data = provider.generate_json(prompt, system_instruction=system_instruction)

        score = float(data.get("score", 3.0))
        # Ensure score bounds
        score = max(1.0, min(5.0, score))

        return {
            "score": round(score, 1),
            "correctness": data.get("correctness", "partially_correct"),
            "strengths": data.get("strengths", ["Answer addressed the fundamental premise of the question."]),
            "missing_concepts": data.get("missing_concepts", ["Could include more specific mathematical formulation."]),
            "improvement_suggestions": data.get("improvement_suggestions", ["Provide concrete production architecture examples."]),
            "evaluation_explanation": data.get("evaluation_explanation", "The response was evaluated against the question rubric and reference concepts.")
        }

evaluation_service = EvaluationService()

