import os
import re
import json
import hashlib
from typing import Dict, Any, Tuple
import pymupdf  # PyMuPDF
from app.services.llm_service import get_llm_provider
from app.schemas.all_schemas import ExtractedProfile

class ResumeService:
    @staticmethod
    def extract_text(file_path: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        elif ext == ".pdf":
            text_parts = []
            doc = pymupdf.open(file_path)
            for page in doc:
                text_parts.append(page.get_text())
            full_text = "\n".join(text_parts).strip()
            if not full_text:
                raise ValueError("PDF is empty or contains non-extractable scanned images.")
            return full_text
        else:
            raise ValueError(f"Unsupported resume file format '{ext}'. Only .pdf and .txt are supported.")

    @staticmethod
    def parse_profile(extracted_text: str) -> ExtractedProfile:
        provider = get_llm_provider()
        prompt = f"""
Please extract the candidate's profile from this resume text:
Analyze the following candidate resume text and extract the structured profile.
Strictly return a JSON object with this exact structure:
{{
  "technical_skills": ["string"],
  "programming_languages": ["string"],
  "frameworks_libraries": ["string"],
  "databases": ["string"],
  "cloud_technologies": ["string"],
  "tools_platforms": ["string"],
  "projects": [
    {{"name": "...", "description": "...", "technologies": ["..."]}}
  ],
  "work_experience": [
    {{"role": "...", "company": "...", "highlights": "..."}}
  ],
  "education": [
    {{"degree": "...", "institution": "...", "year": "..."}}
  ],
  "domain_exposure": ["string"],
  "summary": "Concise 2-sentence technical summary"
}}

Rules:
1. Do not invent qualifications or skills not present in the text.
2. Ensure technical terms are clean and categorized correctly.

Resume Text:
---
{extracted_text[:6000]}
---
"""
        system_instruction = "You are a precise technical resume parsing system. Output valid JSON only."
        data = provider.generate_json(prompt, system_instruction=system_instruction)
        
        # Fallback validation to ensure model conforms
        return ExtractedProfile(
            technical_skills=data.get("technical_skills", []),
            programming_languages=data.get("programming_languages", []),
            frameworks_libraries=data.get("frameworks_libraries", []),
            databases=data.get("databases", []),
            cloud_technologies=data.get("cloud_technologies", []),
            tools_platforms=data.get("tools_platforms", []),
            projects=data.get("projects", []),
            work_experience=data.get("work_experience", []),
            education=data.get("education", []),
            domain_exposure=data.get("domain_exposure", []),
            summary=data.get("summary", "")
        )

resume_service = ResumeService()

