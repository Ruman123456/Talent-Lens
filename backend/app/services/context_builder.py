from typing import Dict, Any, List
from app.services.llm_service import get_llm_provider

class ContextBuilder:
    @staticmethod
    def build_interview_context(
        extracted_profile: Dict[str, Any],
        role_name: str,
        role_competencies: List[str],
        role_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesizes candidate profile and role requirements into targeted semantic queries.
        Identifies potential gaps, strengths, and appropriate question difficulty.
        """
        provider = get_llm_provider()

        prompt = f"""
You are an expert AI technical interview architect.
We need to screen a candidate for the role: "{role_name}".

Candidate Extracted Profile:
- Technical Skills: {', '.join(extracted_profile.get('technical_skills', [])[:10])}
- Programming Languages: {', '.join(extracted_profile.get('programming_languages', [])[:6])}
- Frameworks & Libraries: {', '.join(extracted_profile.get('frameworks_libraries', [])[:8])}
- Databases: {', '.join(extracted_profile.get('databases', [])[:5])}
- Cloud / Tools: {', '.join(extracted_profile.get('cloud_technologies', [])[:5])}
- Projects: {[p.get('name') for p in extracted_profile.get('projects', [])[:3]]}
- Domain Exposure: {', '.join(extracted_profile.get('domain_exposure', [])[:4])}

Role Expected Competencies:
{', '.join(role_competencies)}

Role Primary Topics:
{', '.join(role_topics)}

Task:
Generate 4 to 6 focused, high-precision semantic queries to retrieve foundational and applied textbook passages.
Ensure the queries explore:
1. Foundational principles of the role.
2. Intersecting technologies demonstrated on the candidate's resume.
3. Applied project architecture concepts.
4. Gaps between resume exposure and core competencies.

Return JSON in this structure:
{{
  "queries": ["string"],
  "candidate_strengths": ["string"],
  "potential_gaps": ["string"],
  "recommended_difficulty": "easy | medium | hard"
}}
"""
        system_instruction = "Output valid JSON representing interview context and semantic retrieval queries."
        result = provider.generate_json(prompt, system_instruction=system_instruction)

        # Fallbacks if needed
        queries = result.get("queries", [])
        if not queries:
            queries = [
                f"{role_name} core architectural principles and algorithms",
                f"{' '.join(role_topics[:2])} fundamental concepts",
                f"{' '.join(extracted_profile.get('programming_languages', ['Python'])[:2])} system optimization and data structures"
            ]

        return {
            "queries": queries,
            "candidate_strengths": result.get("candidate_strengths", []),
            "potential_gaps": result.get("potential_gaps", []),
            "recommended_difficulty": result.get("recommended_difficulty", "medium")
        }

context_builder = ContextBuilder()

